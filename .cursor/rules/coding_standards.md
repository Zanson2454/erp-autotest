---
alwaysApply: true
---
# ERP自动化测试用例生成规范

## 角色定义
你是资深测试开发专家，精通Python、pytest、ERP业务测试，基于curl命令快速生成高质量测试用例。

## 核心原则
- **一次到位**：生成完美代码，无需返工
- **标准化调用**：95%场景使用 `standard_api_call`
- **数据复用**：从缓存获取，禁止硬编码
- **Mock优先**：使用 `self.mock_util` 生成测试数据
- **规范清理**：`teardown_class` 中逐表删除测试数据

## 标准测试用例模板

```python
import allure
import pytest
from testcases.{module} import {Module}BaseTest
from utils.report_util import a, case_decorator

@allure.epic("业务领域")
@allure.feature("功能模块")
class Test{Feature}Management({Module}BaseTest):
    """功能管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.{object}_id = None
        cls.logger.info("测试类初始化完成")
        
        # 从缓存安全获取基础数据（如需要）
        if cls.init_data:
            cls.curr_id = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        
        # 从缓存安全获取主数据（如需要）
        if cls.md_cache_data:
            cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])
            cls.cust_id = cust_info[0].get("id") if cust_info else None
    
    @classmethod
    def teardown_class(cls):
        """数据清理：逐表删除，禁止循环"""
        try:
            cls.db.delete(table="{table1}", where="code like %s", params=["AT_%"])
            cls.db.delete(table="{table2}", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"数据清理失败: {str(e)}")
    
    @case_decorator(
        story="业务场景",
        title="测试{功能}",
        description="验证{具体功能}",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["{模块}", "{功能}"]
    )
    def test_save_{object}(self):
        """测试创建{对象}"""
        try:
            # 1. 准备测试数据（使用mock_util）
            {object}_code = self.mock_util.generate_unique_code(tag="{TAG}")
            {object}_name = f"测试{对象}_{self.mock_util.get_timestamp()}"
            
            # 2. 标准化API调用（推荐95%场景）
            set_dict = {
                "code": {object}_code,
                "name": {object}_name,
                "status": "ENABLED"
            }
            response, extracted_id = self.standard_api_call(
                api_key="{API服务名称}",
                set_dict=set_dict,
                store_id_as="{object}"  # 自动存储为 self.{object}_id
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 记录关键数据
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="业务场景",
        title="测试查询{功能}",
        severity="normal",
        file_level_order=2,
        tags=["{模块}", "查询"]
    )
    def test_query_{object}_page(self):
        """测试分页查询{对象}"""
        try:
            # 1. 确保有数据
            if not self.{object}_id:
                self.test_save_{object}()
            
            # 2. 分页查询
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [{"name": "code", "type": "TEXT"}]
            }
            response, _ = self.standard_api_call(
                api_key="{API服务名称}-查询分页服务",
                set_dict=set_dict
            )
            
            # 3. 断言
            self.assert_util.assert_response_data(response)
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

## Mock数据生成规范

**禁止硬编码，统一使用 `self.mock_util`**：

```python
# ✅ 推荐：使用mock_util生成
code = self.mock_util.generate_unique_code(tag="PARTNER")
timestamp = self.mock_util.get_timestamp()
name = self.mock_util.get_mock_name()
company = self.mock_util.get_mock_company()
phone = self.mock_util.get_mock_phone_number()
email = self.mock_util.get_mock_email()
address = self.mock_util.get_mock_address()
date = self.mock_util.get_mock_date(include_time=False, days_offset=0)
remark = self.mock_util.get_mock_remark()
price = self.mock_util.get_mock_price(min_price=1.00, max_price=999999.99)
bank_info = self.mock_util.get_mock_bank_info()
business_license = self.mock_util.get_mock_enterprise_credentials()
business_scope = self.mock_util.get_mock_business_scope(max_length=200)
company_intro = self.mock_util.get_mock_company_intro(max_length=200)

# ❌ 禁止：硬编码
code = "TEST_001"  # 错误
name = "测试数据"  # 错误
```

## 数据库操作规范

```python
# ✅ 参数化查询（防止SQL注入）
result = self.db.query_one(
    sql="SELECT * FROM table_name WHERE id = %s",
    params=[self.xxx_id]
)

# ✅ 数据清理（逐表删除）
@classmethod
def teardown_class(cls):
    try:
        cls.db.delete(table="child_table", where="code like %s", params=["AT_%"])
        cls.db.delete(table="parent_table", where="code like %s", params=["AT_%"])
    except Exception as e:
        cls.logger.error(f"清理失败: {str(e)}")

# ❌ 禁止：字符串拼接SQL
sql = f"SELECT * FROM table WHERE code = '{code}'"  # SQL注入风险

# ❌ 禁止：循环删除表
for table in tables:  # 错误
    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
```

## 标准CRUD流程顺序

```python
# file_level_order 顺序规范
test_save_*       # 1-3   创建
test_query_*      # 4-6   查询
test_update_*     # 7-9   更新
test_export_*     # 10-12 导出
test_import_*     # 13-15 导入（通常跳过）
test_delete_*     # 16-18 删除
```

## 异步任务测试模板

```python
@case_decorator(
    story="异步任务",
    title="测试异步{功能}并等待完成",
    severity="normal",
    file_level_order=10,
    tags=["{模块}", "异步"]
)
def test_async_{action}_{object}(self):
    """测试异步{功能}"""
    try:
        # 1. 发起异步任务
        set_dict = {"id": self.{object}_id}
        response, _ = self.standard_api_call(
            api_key="{API服务名称}-异步任务发起",
            set_dict=set_dict
        )
        self.assert_util.assert_response_success(response)
        
        # 2. 定义查询函数
        def query_status():
            query_response, _ = self.standard_api_call(
                api_key="{API服务名称}-查询详情服务",
                set_dict={"id": self.{object}_id}
            )
            return query_response.get("data", {}).get("data", {})
        
        # 3. 等待异步任务完成
        result = self.async_wait_util.wait_for_async_status(
            query_func=query_status,
            status_field="asyncExecutionStatus",
            success_status="SUCCEEDED",
            failed_status="FAILED",
            failure_reason_field="asyncExecutionFailureReason",
            max_wait=60,
            interval=3.0
        )
        
        # 4. 断言结果
        if result.status == self.wait_status.SUCCESS:
            a.text(f"✅ 异步任务成功，耗时: {result.total_wait_time:.2f}秒", "结果")
        else:
            raise AssertionError(f"❌ 异步任务失败: {result.error_message}")
            
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

## 参数化测试模板

```python
@pytest.mark.parametrize("test_data", [
    {
        "name": "正常流程",
        "amount": 123.45,
        "expected_success": True,
        "expected_status": "APPROVED"
    },
    {
        "name": "异常流程",
        "amount": -100.00,
        "expected_success": False,
        "expected_error_code": "invalid.amount"
    }
])
@case_decorator(
    story="参数化测试",
    title="测试{功能}多场景",
    severity="normal",
    file_level_order=5,
    tags=["{模块}", "参数化"]
)
def test_{action}_{object}_parametrize(self, test_data):
    """参数化测试{功能}"""
    try:
        # 使用test_data中的参数
        set_dict = {"amount": test_data["amount"]}
        response, _ = self.standard_api_call(
            api_key="{API服务名称}",
            set_dict=set_dict
        )
        
        # 统一断言逻辑
        if test_data["expected_success"]:
            self.assert_util.assert_response_success(response)
        else:
            assert response["err"]["code"] == test_data["expected_error_code"]
            
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

## 关键规则总结

1. **API调用**：95%场景使用 `standard_api_call`，自动处理参数过滤和ID存储
2. **数据生成**：统一使用 `self.mock_util`，禁止硬编码
3. **数据获取**：从缓存安全获取，使用 `.get()` 避免 KeyError
4. **数据清理**：`teardown_class` 中逐表删除，禁止循环
5. **数据库操作**：必须参数化查询，防止SQL注入
6. **异常处理**：所有测试方法必须 try-except 结构
7. **顺序控制**：使用 `file_level_order` 确保串行执行
8. **报告记录**：使用 `a.json()` 和 `a.text()` 记录关键数据

## 立即执行
基于以上规范，分析curl请求，生成完美测试用例！

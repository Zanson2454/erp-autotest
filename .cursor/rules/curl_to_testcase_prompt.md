# CURL 转测试用例提示词模板

> 基于 curl 命令一键生成 ERP 自动化测试用例

---

## 使用方式

将以下模板 + curl 命令一起提供给 AI，即可生成完整的测试用例代码。

---

## AI 提示词模板

```
请基于以下 curl 命令生成 ERP 自动化测试用例：

### curl 命令
```
{CURL_COMMAND}
```

### 生成要求

1. **使用 standard_api_call 方法**
2. **使用 mock_util 生成测试数据**（禁止硬编码）
3. **添加 @case_decorator 装饰器**
4. **添加 setup_class 和 teardown_class**
5. **使用 bind_cache_data 简化数据获取**
6. **禁止用例互调**（禁止 `self.test_xxx()`，改用 helper）
7. **加入幂等处理**（“已存在”错误码时回查并复用）

### 代码规范
- 参考文件: testcase_temp.mdc 和 coding_standards.mdc
- 使用 self.mock_util.generate_unique_code(tag="AT_XXX") 生成编码
- 使用 self.mock_util.get_timestamp() 生成时间戳
- 使用 self.bind_cache_data() 绑定常用数据（如 cust_id, org_id 等）
- 检查 `${ENV_VAR}` 占位符是否已替换，URL 必须带 `https://` 或 `http://`
```

---

## 示例

### 输入 AI 的完整提示词

```
请基于以下 curl 命令生成 ERP 自动化测试用例：

### curl 命令
curl 'http://test.example.com/api/trantor/portal/data-service' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: JSESSIONID=xxx' \
  -H 'Referer: http://test.example.com/' \
  --data-raw '{"serviceKey":"GEN_PARTNER_SAVE_ACTION_SERVICE","params":{"request":{"code":"P001","name":"测试合作伙伴","partnerType":"CUSTOMER","status":"ENABLED"}}}'

### 生成要求

1. 使用 standard_api_call 方法
2. 使用 mock_util 生成测试数据（禁止硬编码）
3. 添加 @case_decorator 装饰器
4. 添加 setup_class 和 teardown_class
5. 使用 bind_cache_data 简化数据获取

### 代码规范
- 参考文件: testcase_temp.mdc 和 coding_standards.mdc
- 使用 self.mock_util.generate_unique_code(tag="AT_XXX") 生成编码
- 使用 self.mock_util.get_timestamp() 生成时间戳
- 使用 self.bind_cache_data() 绑定常用数据（如 cust_id, org_id 等）
```

### AI 生成的代码

```python
import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("主数据管理")
@allure.feature("合作伙伴管理")
class TestPartnerManagement(GenMdBaseTest):
    """合作伙伴管理测试类"""
    
    partner_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.bind_cache_data()  # 绑定常用数据
        cls.logger.info("合作伙伴管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="partner_md", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="合作伙伴管理",
        title="测试创建合作伙伴",
        description="验证GEN_PARTNER_SAVE_ACTION_SERVICE功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["主数据", "合作伙伴", "创建"]
    )
    def test_save_partner(self):
        """测试创建合作伙伴"""
        try:
            # 1. 准备测试数据
            partner_code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
            partner_name = f"测试合作伙伴_{self.mock_util.get_timestamp()}"
            
            # 2. 使用标准化API调用
            set_dict = {
                "code": partner_code,
                "name": partner_name,
                "partnerType": "CUSTOMER",
                "status": "ENABLED"
            }
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                store_id_as="partner"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 保存ID
            if not hasattr(self, 'partner_id'):
                self.partner_id = extracted_id
            
            a.json(response, "响应数据")
            self.logger.info(f"创建合作伙伴成功: ID={self.partner_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

---

## 常用 API Key 参考

| 业务模块 | API Key 模式 | 示例 |
|----------|-------------|------|
| 合作伙伴 | GEN-合作伙伴-{服务} | GEN-合作伙伴-保存服务 |
| 组织 | GEN-组织-{服务} | GEN-组织-保存服务 |
| 物料 | GEN-物料-{服务} | GEN-物料-保存服务 |
| 销售订单 | SLS-SO-{服务} | SLS-SO-保存服务 |
| 采购订单 | PUR-PO-{服务} | PUR-PO-保存服务 |
| 财务 | FIN-{模块}-{服务} | FIN-AP-保存服务 |

---

## 快速绑定数据

```python
# 方式1: 绑定所有常用字段
cls.bind_cache_data()

# 方式2: 只绑定需要的字段
cls.bind_cache_data({
    "cust_id": "partner_info.cust_info.id",
    "org_id": "org_info.gr_come_org_info.id",
})

# 可用字段:
# init_data:
#   - curr_id (币种)
#   - coun_id (国家)
#   - addr_id (地址)
#   - bank_id (银行)
# md_cache_data:
#   - cust_id (客户)
#   - sup_id (供应商)
#   - com_org_id (核算组织)
#   - sls_org_id (销售组织)
#   - inv_org_id (库存组织)
#   - pur_org_id (采购组织)
#   - sls_dc_id (配送中心)
#   - wh_id (仓库)
#   - mat_id (物料)
```

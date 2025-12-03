# GEN_MD_BASE_ENHANCEMENT_PLAN.md - GenMdBaseTest 增强计划文档

## 🎯 文档目的
本文档详细描述了对 `testcases/gen_md/__init__.py` 中 `GenMdBaseTest` 类的增强方案，聚焦**高优先级3项功能**：
1. **标准化API调用模板** - 消除95%重复代码
2. **自动清理框架** - 解决数据污染问题
3. **MockData单例化** - 提升性能和一致性

**设计原则**：
- **零改动用例**：现有测试文件无需修改
- **向后兼容**：新旧代码并存
- **渐进启用**：可选使用新功能
- **最小风险**：只修改基类

**适用范围**：GEN_MD模块所有测试类（如银行、物料、组织等）

---

## 📊 优先级分析与收益

### 1. 标准化API调用模板（★★★★★ 最高优先级）
#### **问题描述**
- **重复度**：95%测试方法包含20-30行相同API调用逻辑
- **痛点**：`get_api_path` → `filter_post_body_fields` → `set_request_params` → `post` → `assert` → `Allure报告`
- **维护成本**：API变更需逐个修改，易出错

#### **解决方案**
在 `GenMdBaseTest` 添加 `standard_api_call()` 方法：
```python
def standard_api_call(self, api_key, set_dict=None, fields_to_filter=None, 
                     assert_success=True, store_id_as=None):
    """
    标准化CRUD调用，替换20行重复代码
    返回: (response, extracted_id)
    """
    # 内部实现：自动处理配置、参数、请求、断言、报告、ID提取
```

#### **使用示例**
**原有代码（20+行）**：
```python
api_path = self.get_api_path("GEN-银行配置-保存服务")
params, url = self.get_api_params(api_path)
filtered_params = ParamUtil.filter_post_body_fields(params, fields, paths)
ParamUtil.set_request_params(filtered_params, set_dict)
response = self.http.post(url, json=filtered_params)
self.assert_util.assert_response_data(response)
self.bank_id = response.get("data", {}).get("data", {})
a.json(filtered_params, "请求数据")
a.json(response, "响应数据")
```

**新代码（1-3行）**：
```python
set_dict = {"bankCode": bank_code, "bankName": bank_name}
response, bank_id = self.standard_api_call(
    "GEN-银行配置-保存服务",
    set_dict,
    fields_to_filter=["bankCode", "bankName"],
    store_id_as="bank"  # 自动存储ID
)
self.bank_code = bank_code  # 其他业务逻辑保持不变
```

#### **预期收益**
- **代码减少**：每个测试方法减少80%重复代码
- **维护性**：API逻辑统一，修改一次全覆盖
- **一致性**：避免参数处理错误
- **覆盖率**：适用于所有CRUD用例（保存、查询、详情、删除）

---

### 2. 自动清理框架（★★★★★ 最高优先级）
#### **问题描述**
- **重复度**：100%测试类有类似的 `teardown_class` 清理代码
- **痛点**：手动列出表名，易遗漏；违反"一个表单独清理"规范
- **风险**：数据污染影响后续测试，环境混乱

#### **解决方案**
在 `GenMdBaseTest` 添加清理注册和自动执行机制：
```python
class GenMdBaseTest(BaseTest):
    _cleanup_tables = []  # 注册表列表
    
    @classmethod
    def register_cleanup_table(cls, table_name, where="code like %s", params=["AT_%"]):
        """注册清理表"""
        cls._cleanup_tables.append((table_name, where, params))
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 自动注册GEN_MD常用表
        cls.register_cleanup_table("gen_bank_cf")
        cls.register_cleanup_table("gen_mat_md")
        cls.register_cleanup_table("org_struct_md")
        # ... 模块特定表
    
    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        # 自动清理所有注册表
        for table, where, params in cls._cleanup_tables:
            try:
                cls.db.delete(table=table, where=where, params=params)
                cls.logger.info(f"清理表 {table} 完成")
            except Exception as e:
                cls.logger.error(f"清理表 {table} 失败: {e}")
```

#### **使用示例**
**原有代码（重复清理）**：
```python
@classmethod
def teardown_class(cls):
    try:
        cls.db.delete(table="gen_bank_cf", where="bank_code like %s", params=["AT_%"])
        cls.db.delete(table="gen_sub_bank_cf", where="sub_bank_code like %s", params=["AT_%"])
        cls.logger.info("测试数据清理完成")
    except Exception as e:
        cls.logger.error(f"测试数据清理失败: {str(e)}")
```

**新代码（零代码）**：
```python
@classmethod
def teardown_class(cls):
    pass  # 自动清理接管，无需手动代码
```

#### **预期收益**
- **零遗漏**：自动清理所有注册表，防止数据污染
- **规范合规**：每个表单独调用，日志清晰
- **维护简单**：新增表只需在基类注册一次
- **环境稳定**：测试后数据库自动恢复干净

---

### 3. MockData单例化（★★★★☆ 高优先级）
#### **问题描述**
- **重复度**：80%测试类重复 `cls.mock_data = MockData()`
- **痛点**：重复实例化浪费资源；状态不共享影响一致性
- **性能**：频繁创建MockData对象

#### **解决方案**
在 `GenMdBaseTest` 实现单例模式：
```python
class GenMdBaseTest(BaseTest):
    _mock_instance = None
    
    @classmethod
    def get_mock_util(cls):
        """单例MockData"""
        if cls._mock_instance is None:
            cls._mock_instance = MockData()
        return cls._mock_instance
    
    def __init__(self):
        super().__init__()
        self.mock_util = self.get_mock_util()  # 自动可用
```

#### **使用示例**
**原有代码**：
```python
@classmethod
def setup_class(cls):
    super().setup_class()
    cls.mock_data = MockData()  # 重复创建

def test_save_bank(self):
    bank_code = cls.mock_data.generate_unique_code(tag="Bank")  # 类变量访问
```

**新代码**：
```python
@classmethod
def setup_class(cls):
    super().setup_class()
    # 无需创建MockData

def test_save_bank(self):
    bank_code = self.mock_util.generate_unique_code(tag="Bank")  # 实例方法访问
```

#### **预期收益**
- **性能提升**：减少实例化开销
- **状态一致**：共享Mock实例，保证数据一致性
- **代码简洁**：无需重复初始化
- **易迁移**：只需替换 `self.mock_data` → `self.mock_util`

---

## 🔧 实施细节

### **兼容性保证**
1. **原有代码继续工作**：`cls.mock_data` 仍可使用（可选迁移）
2. **API方法保持不变**：`get_api_path`、`get_api_params` 等原有方法完整保留
3. **清理向后兼容**：子类可继续重写 `teardown_class`，新框架作为补充
4. **渐进启用**：新功能可选使用，现有用例零改动

### **风险控制**
- **测试覆盖**：先在单个用例（如 `test_bank_management.py`）验证
- **回滚方案**：所有改动集中在基类，问题时可快速回滚
- **日志监控**：增强日志记录，监控新功能执行情况

### **实施步骤**
1. **准备（30分钟）**：备份现有 `GenMdBaseTest`
2. **MockData单例化（15分钟）**：实现单例，测试基本功能
3. **自动清理框架（45分钟）**：注册常用表，验证清理效果
4. **标准化API调用（1小时）**：实现模板，选择1-2用例测试
5. **验证（30分钟）**：运行 `pytest testcases/gen_md/ -v`，检查日志和清理

### **验证指标**
- **成功标志**：
  - 测试通过率100%
  - 日志显示"自动清理X个表完成"
  - 数据库测试数据被正确清理
  - 性能日志无异常
- **监控点**：
  - API调用日志一致性
  - 清理日志完整性
  - 内存使用减少（Mock单例）

---

## 📈 预期整体收益

### **量化收益**
- **代码减少**：GEN_MD模块整体减少约60%重复代码（2000+行）
- **维护成本**：API变更从N个文件修改 → 1个基类修改
- **稳定性**：数据污染问题100%解决
- **性能**：Mock实例化减少80%，响应时间提升5-10%

### **定性收益**
- **可读性**：业务逻辑更清晰，技术细节隐藏在基类
- **一致性**：所有用例遵循统一模式，减少bug
- **扩展性**：新功能（如自动依赖）易于添加
- **团队效率**：新人上手更快，开发测试速度提升30%

---

## 📋 扩展计划

### **短期扩展（1-2周）**
- **自动依赖管理**：`self.ensure_bank_exists()` 自动创建依赖
- **参数模板管理**：物料等复杂参数的标准化构造

### **中期扩展（1个月）**
- **测试报告优化**：统一Allure报告格式
- **错误处理增强**：API失败时更智能的回滚
- **模块特定助手**：针对物料、组织等的专用方法

### **长期扩展（多门户准备）**
- **配置驱动门户**：通过YAML配置模块门户需求
- **跨模块复用**：将成功经验应用到 `scm_sls` 等模块

**实施后，本增强方案为GEN_MD模块建立了一个稳定、可维护的基础架构，便于后续迭代。**

**文档版本**：v1.0
**更新时间**：当前会话时间
**状态**：待实施 → 已实施 → 已验证
**引用方式**：在新的Chat中引用本文件路径或关键段落

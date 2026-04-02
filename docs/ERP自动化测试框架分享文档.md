# ERP自动化测试框架分享文档
> **分享目标**：快速掌握ERP自动化测试框架的使用方法和开发规范
>
> **适用人员**：测试开发工程师
>
> **文档版本**：v2.0
>
> **最后更新**：2026年1月
>

---

## 📚 目录

- [1. 项目概述](#1-项目概述)
- [2. 项目结构](#2-项目结构)
- [3. 业务模块详解](#3-业务模块详解)
- [4. 工具类详解](#4-工具类详解)
  - [4.2.1 standard_api_call - 标准化API调用（核心）](#421-standard_api_call---标准化api调用核心)
  - [4.2.2 async_wait_util - 异步等待工具](#422-async_wait_utilpy---异步等待工具)
- [5. 数据工厂](#5-数据工厂核心概念)
- [6. API配置文件重新获取指南](#6-api配置文件重新获取指南)
- [7. AI提示词最佳实践](#7-ai提示词最佳实践)
- [8. 测试调试与执行](#8-测试调试与执行)
- [9. Cursor使用技巧](#9-cursor使用技巧)
- [10. 测试用例编写指南](#10-测试用例编写指南)
- [11. 常见问题FAQ](#11-常见问题faq)
- [12. 总结](#12-总结)

---

## 1. 项目概述
### 1.1 项目简介
ERP自动化测试框架是基于 **Python + Pytest + FastAPI** 构建的企业级自动化测试框架，提供完整的测试执行、数据管理、报告生成和Web服务功能。

工程地址(权限找[@章昂](https://www.yuque.com/weigu))：[https://erda.cloud/terminus/dop/projects/1000215/apps/1002909/repo/tree/feature/develop](https://erda.cloud/terminus/dop/projects/1000215/apps/1002909/repo/tree/feature/develop)

### 1.2 核心技术栈
| 技术 | 版本 | 用途 |
| --- | --- | --- |
| pytest | 7.4.3 | 测试框架 |
| pytest-xdist | 3.3.1 | 并行执行 |
| FastAPI | 0.104.1 | Web API服务 |
| Allure | 2.13.2 | 测试报告 |
| pymysql | 1.1.0 | 数据库操作 |
| requests | 2.31.0 | HTTP请求 |
| loguru | 0.7.2 | 日志系统 |
| faker | 19.13.0 | Mock数据 |


### 1.3 项目特点
✅ 模块化设计 ✅ 配置驱动 ✅ 数据工厂 ✅ 缓存机制 ✅ Web服务 ✅ 多门户支持 ✅ 标准化API调用 ✅ 异步任务测试

---

### 1.4 注意事项
+ 执行自动化前先替换有效cookie，确保所用cookie有相关组织权限，例如公司组织、采购组织、销售组织等
+ 并发执行自动化时，确保测试用例文件之间不存在相互依赖关系
+ 推荐使用 `standard_api_call` 方法进行API调用，统一处理请求和响应，提高代码可维护性

## 2. 项目结构
### 2.1 核心目录
```plain
erp-autotest/
├── __init__.py                 # ⭐ 项目根初始化
├── main.py                     # FastAPI应用入口
├── pytest.ini                  # pytest配置
├── requirements.txt            # 依赖包
├── .env                        # 环境变量（不提交）
├── config/                     # 配置目录
│   ├── base.yaml              # 基础配置
│   ├── api/                   # API配置文件
│   │   ├── gen_md/
│   │   │   ├── md_api_path.yaml
│   │   │   └── md_api_params.yaml
│   │   ├── scm_inv/
│   │   │   ├── inv_api_path.yaml
│   │   │   └── inv_api_params.yaml
│   │   ├── scm_pur/
│   │   │   ├── pur_api_path.yaml
│   │   │   └── pur_api_params.yaml
│   │   └── ...
│   ├── env/                   # 环境配置（dev/test/prod）
│   └── erp/                   # SQL初始化配置
│       ├── base_init_sql.yaml
│       ├── md_init_sql.yaml
│       ├── pur_init_sql.yaml
│       └── sls_init_sql.yaml
├── testcases/                  # 测试用例
│   ├── __init__.py            # ⭐ 测试包初始化
│   ├── conftest.py            # ⭐⭐ pytest全局配置
│   ├── comm/
│   │   └── base_test.py       # ⭐⭐⭐ 测试基类
│   ├── scm_inv/               # 库存管理
│   │   └── __init__.py        # ⭐⭐ 库存模块基类
│   ├── scm_pur/               # 采购管理
│   │   └── __init__.py        # ⭐⭐ 采购模块基类
│   ├── scm_sls/               # 销售管理
│   ├── prd/                   # 生产管理
│   ├── fin/                   # 财务管理
│   └── gen_md/                # 主数据管理
├── testdata/                   # 测试数据
│   └── cache/                 # 缓存数据（JSON文件）
├── utils/                      # 工具类库
│   ├── request_util.py        # HTTP请求
│   ├── mysql_util.py          # 数据库
│   ├── yaml_util.py           # YAML
│   ├── log_util.py            # 日志
│   ├── cache_util.py          # 缓存
│   ├── assert_util.py         # 断言
│   ├── param_util.py          # 参数处理
│   ├── mock_util.py           # Mock数据
│   ├── file_util.py           # 文件操作
│   ├── report_util.py         # 报告增强
│   ├── response_util.py       # 响应处理
│   ├── exception_util.py      # 异常处理
│   └── dingtalk_util.py       # 钉钉通知
├── erp_data_factory/           # 数据工厂产品包（当前主路径）
│   ├── client.py              # ⭐ SDK入口（ERPDataFactoryClient）
│   ├── cli.py                 # CLI入口（edf）
│   ├── interfaces/            # FastAPI接口
│   ├── application/           # 场景注册/执行/任务管理
│   ├── domain/                # 场景实现
│   ├── compat/                # 兼容层
│   └── legacy/                # 迁移承接层
├── routers/                    # FastAPI路由（Web后台）
│   ├── allure_api.py          # 报告查看API
│   ├── api_manage.py          # 测试执行API
│   └── data_factory_api.py   # 数据工厂API
├── script/                     # 工具脚本
│   ├── case_coverage_stat.py # 用例覆盖率统计
│   ├── find_unreferenced_services.py  # 查找未引用API
│   └── swagger_parser.py     # Swagger解析
├── logs/                       # 日志目录
├── reports/                    # 测试报告
│   ├── allure-results/        # Allure原始数据
│   └── allure-report/         # Allure HTML报告
└── static/                     # 静态资源（Swagger UI）
```

### 2.2 核心文件说明
#### 2.2.1 根目录 `__init__.py` ⭐
**作用**：项目根路径管理和初始化

**核心功能**：

```python
# 1. 获取项目根目录并添加到sys.path
def _get_project_root() -> Path:
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

PROJECT_ROOT = _get_project_root()

# 2. 提供路径获取函数
def get_module_path(module_name: str) -> Path:
    return PROJECT_ROOT / module_name

def get_config_path() -> Path:
    return PROJECT_ROOT / "config"
```

**作用**：确保模块导入路径正确，统一管理项目路径

---

#### 2.2.2 `testcases/conftest.py` ⭐⭐
**作用**：pytest全局配置文件

**核心功能**：命令行参数定义、环境配置加载、测试标记注册、测试用例排序

---

#### 2.2.3 `testcases/comm/base_test.py` ⭐⭐⭐
**作用**：测试基类，所有测试类的父类

**核心组件**：LoginService（登录服务）、BaseTestInitializer（初始化器）、BaseTest（测试基类）

**BaseTest - 测试基类**

```python
class BaseTest:
    @classmethod
    def setup_class(cls):
        """测试类初始化（执行一次）"""
        # 1. 获取环境
        env = os.getenv("TEST_ENV", "test")
        
        # 2. 初始化
        initializer = BaseTestInitializer(env)
        cls.env_config = initializer.initialize_environment()
        cls.init_data = initializer.initialize_base_data()
        
        # 3. 登录
        login_result = initializer.initialize_authentication(cls.env_config)
        cls.user_info = login_result.user_info
        cls.session = login_result.session
        
        # 4. HTTP工具
        cls.http = HttpUtil(
            url=login_result.portal_url,
            session=login_result.session,
            headers=login_result.portal_headers
        )
        
        # 5. 数据库
        cls.db = initializer.initialize_database(cls.env_config, "erp_db")
        cls.iam_db = initializer.initialize_database(cls.env_config, "iam_db")
        
        # 6. 工具类
        utilities = initializer.initialize_utilities()
        for name, util in utilities.items():
            setattr(cls, name, util)
    
    def setup_method(self, method):
        """每个测试方法执行前"""
        self.test_data = {}
        self.test_start_time = time.time()
    
    def teardown_method(self, method):
        """每个测试方法执行后"""
        duration = time.time() - self.test_start_time
        self.logger.info(f"耗时: {duration:.3f}秒")
```

**BaseTest提供的类属性**：

```python
cls.env_config      # 环境配置
cls.init_data       # 初始化数据
cls.user_info       # 用户信息
cls.session         # 会话对象
cls.http            # HTTP工具
cls.db              # ERP数据库
cls.iam_db          # IAM数据库
cls.logger          # 日志工具
cls.assert_util     # 断言工具
cls.mock_util       # Mock工具
cls.cache           # 缓存工具
cls.yaml_util       # YAML工具
```

---

## 3. 业务模块详解
### 3.1 模块基类的作用
每个业务模块都有自己的`__init__.py`，定义模块专属测试基类。

**作用**：统一初始化、加载配置、加载缓存、多门户登录、提供便捷方法

### 3.2 库存模块 `scm_inv/__init__.py` ⭐⭐
**核心代码**：

```python
class ScmInvBaseTest(BaseTest):
    """库存模块基类"""
    
    # 定义多门户
    _PORTAL_TYPE_KEYS = {
        "admin": "TERP_PORTAL",
        "cust": "TERP_CUST_PC"
    }
    
    @classmethod
    def setup_class(cls):
        # 1. 调用父类初始化
        super().setup_class()
        
        # 2. 登录多个门户
        cls.login_service = LoginService(cls.env_config)
        admin_result = cls.login_service.login(
            portal_key=cls._PORTAL_TYPE_KEYS["admin"]
        )
        
        # 3. 初始化HTTP工具
        cls.http = HttpUtil(
            url=admin_result.portal_url,
            session=admin_result.session,
            headers=admin_result.portal_headers
        )
        
        # 4. 加载库存API配置
        cls.apis = cls.yaml_util.read_yaml("config/api/scm_inv/inv_api_path.yaml")
        cls.api_params = cls.yaml_util.read_yaml("config/api/scm_inv/inv_api_params.yaml")
        
        # 5. 初始化缓存数据
        DataFactory.init_sql_cache(
            sql_config_path="config/erp/md_init_sql.yaml",
            db_config_name="erp_db",
            cache_key="inv_init_cache",
            cache_dir="testdata/cache"
        )
        cls.inv_cache_data = CacheUtil.get('inv_init_cache')
        
        # 6. 设置模块参数
        cls.path_params = {"tmodule": "SCM_INV"}
        cls.nickname = cls.user_info["nickname"]
        cls.user_id = cls.user_info["id"]
    
    def get_api_path(self, api_key):
        """获取API路径"""
        return super().get_api_path(api_key, self.apis)
    
    def get_api_params(self, api_path, with_query_params=None):
        """获取API参数"""
        return super().get_api_params(api_path, self.api_params, with_query_params)
```

**ScmInvBaseTest新增属性**：

```python
cls.login_service       # 登录服务
cls.admin_headers       # 管理员headers
cls.cust_portal_headers # 客户门户headers
cls.apis                # API路径配置
cls.api_params          # API参数配置
cls.inv_cache_data      # 库存缓存数据
cls.path_params         # 模块参数
cls.nickname            # 用户昵称
cls.user_id             # 用户ID
```

### 3.3 采购模块 `scm_pur/__init__.py` ⭐⭐
**与库存模块类似**，只是加载的配置不同：

| 项目 | 库存模块 | 采购模块 |
| --- | --- | --- |
| 基类 | ScmInvBaseTest | ScmPurBaseTest |
| API配置路径 | config/api/scm_inv/ | config/api/scm_pur/ |
| API配置文件 | inv_api_path.yaml, inv_api_params.yaml | pur_api_path.yaml, pur_api_params.yaml |
| 缓存key | inv_init_cache | pur_init_cache |
| SQL配置 | md_init_sql.yaml | pur_init_sql.yaml |
| 模块标识 | SCM_INV | SCM_PUR |


### 3.4 测试用例示例 ⭐⭐⭐

```python
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator
import allure

@allure.epic("主数据管理")
@allure.feature("合作伙伴管理")
class TestPartnerManagement(GenMdBaseTest):
    """合作伙伴管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
        cls.logger.info("合作伙伴管理测试类初始化完成")
    
    @case_decorator(
        story="创建合作伙伴",
        title="测试创建合作伙伴",
        description="验证创建合作伙伴的基本功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["主数据", "合作伙伴"]
    )
    def test_save_partner(self):
        """测试创建合作伙伴"""
        try:
            # 1. 准备测试数据
            partner_code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
            partner_name = f"测试合作伙伴_{self.mock_util.get_timestamp()}"
            
            # 2. 使用标准化API调用（推荐）
            set_dict = {
                "code": partner_code,
                "name": partner_name,
                "partnerType": "CUSTOMER"
            }
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                store_id_as="partner"  # 自动存储为 self.partner_id
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 记录关键数据
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(table="partner_md", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
```

---

## 4. 工具类详解
### 4.1 工具类总览
| 工具类 | 文件 | 核心功能 |
| --- | --- | --- |
| HTTP请求 | `request_util.py` | 封装requests，提供统一HTTP请求接口 |
| 数据库 | `mysql_util.py` | MySQL操作，支持连接池和事务管理 |
| YAML | `yaml_util.py` | YAML文件读写，支持环境变量替换 |
| 日志 | `log_util.py` | 基于loguru的日志封装，支持多种输出 |
| 缓存 | `cache_util.py` | JSON文件缓存，支持过期时间和自动刷新 |
| 断言 | `assert_util.py` | 丰富的断言方法，自动记录日志 |
| 参数处理 | `param_util.py` | API参数提取、过滤、设置 |
| Mock数据 | `mock_util.py` | 基于faker生成测试数据 |
| 文件操作 | `file_util.py` | 文件读写、路径处理 |
| 报告增强 | `report_util.py` | Allure装饰器、报告美化 |
| 响应处理 | `response_util.py` | HTTP响应解析和验证 |
| 异常处理 | `exception_util.py` | 异常捕获装饰器 |
| 钉钉通知 | `dingtalk_util.py` | 钉钉机器人消息推送 |
| 异步等待 | `async_wait_util.py` | 异步任务状态轮询和等待机制 |


### 4.2 重点工具类详解

#### 4.2.1 standard_api_call - 标准化API调用（⭐ 核心方法）

**作用**：统一处理API请求和响应，简化测试用例编写

**基本用法**：

```python
# 最简单的用法（95%的场景）
response, extracted_id = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict={"textCode": "AT_001", "textName": "测试"}
)
```

**完整参数说明**：

```python
def standard_api_call(
    self, 
    api_key,                    # API服务名称（必填）
    set_dict=None,              # 业务参数字典（可选）
    fields_to_filter=None,      # 字段过滤列表（可选，默认从set_dict.keys()获取）
    store_id_as=None,           # 自动存储ID属性名（可选）
    use_param_util=True,        # 是否使用ParamUtil过滤（可选，默认True）
    param_path=None,            # 参数路径（可选，默认["params", "request"]）
    method="POST",              # HTTP方法（可选，默认POST）
    query_params=None,          # URL查询参数（可选）
    extra_body_params=None      # 额外的body参数（可选）
)
```

**常见场景示例**：

```python
# 场景1：新增/更新
set_dict = {"textCode": "AT_001", "textName": "测试文本"}
response, extracted_id = self.standard_api_call(
    api_key="GEN-文本类型-保存服务",
    set_dict=set_dict,
    store_id_as="text_type"  # 自动存储为 self.text_type_id
)

# 场景2：查询详情/删除
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-查询详情服务",
    set_dict={"id": self.text_type_id}
)

# 场景3：分页查询
response, _ = self.standard_api_call(
    api_key="GEN-文本类型-查询分页服务",
    set_dict={
        "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
        "fields": [{"name": "textCode", "type": "TEXT"}]
    }
)

# 场景4：复杂接口（手动模式）
set_dict = {
    "request": {"poItemType": "AT_001", "poItemTypeName": "测试"},
    "modelKey": self.MODEL_KEY
}
response, _ = self.standard_api_call(
    api_key="(系统)保存主数据服务",
    set_dict=set_dict,
    param_path=["params"],
    use_param_util=False,
    query_params={"tmodule": "SCM_PUR", "modelKey": self.MODEL_KEY}
)
```

**详细文档**：参考 `docs/STANDARD_API_CALL_GUIDE.md`

---

#### 4.2.2 async_wait_util.py - 异步等待工具 ⭐

**作用**：支持异步任务状态轮询和等待机制

**使用示例**：

```python
# 1. 定义查询函数
def query_status():
    response, _ = self.standard_api_call(
        api_key="XXX-查询详情服务",
        set_dict={"id": self.xxx_id}
    )
    return response.get("data", {}).get("data", {})

# 2. 等待异步任务完成
result = self.async_wait_util.wait_for_async_status(
    query_func=query_status,
    status_field="asyncExecutionStatus",
    success_status="SUCCEEDED",
    failed_status="FAILED",
    failure_reason_field="asyncExecutionFailureReason",
    max_wait=60,
    interval=3.0
)

# 3. 断言结果
if result.status == self.wait_status.SUCCESS:
    a.text(f"✅ 异步任务成功完成，总耗时: {result.total_wait_time:.2f}秒", "异步任务结果")
else:
    raise AssertionError(f"异步任务执行失败: {result.error_message}")
```

---

#### 4.2.3 mysql_util.py - 数据库工具

**使用示例**：

```python
# 查询数据
result = self.db.query_one(
    sql="SELECT * FROM partner_md WHERE id = %s",
    params=[self.partner_id]
)

# 插入数据
inserted_id = self.db.insert(
    table="partner_md",
    data={"code": "AT_CODE001", "name": "测试数据"}
)

# 更新数据
affected_rows = self.db.update(
    table="partner_md",
    data={"name": "更新后的名称"},
    where="id = %s",
    params=[self.partner_id]
)

# 删除数据
affected_rows = self.db.delete(
    table="partner_md",
    where="code like %s",
    params=["AT_%"]
)
```

---

#### 4.2.4 assert_util.py - 断言工具

**使用示例**：

```python
self.assert_util.assert_response_success(response)  # 成功响应
self.assert_util.assert_response_data(response)     # 数据响应
self.assert_util.assert_by_operator(actual, "=", expected)  # 自定义
```

---

#### 4.2.5 mock_util.py - Mock数据工具

**使用示例**：

```python
code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
timestamp = self.mock_util.get_timestamp()
name = self.mock_util.get_mock_name()
phone = self.mock_util.get_mock_phone_number()
```

---

#### 4.2.6 其他工具类
+ **request_util.py**：HTTP请求封装，支持会话管理
+ **cache_util.py**：缓存管理，支持过期刷新
+ **log_util.py**：结构化日志，基于loguru
+ **yaml_util.py**：YAML文件读写
+ **param_util.py**：参数处理（已被 standard_api_call 封装）
+ **file_util.py**：文件操作、Excel/CSV处理
+ **report_util.py**：`case_decorator`装饰器、Allure报告美化
+ **response_util.py**：响应解析和验证
+ **exception_util.py**：异常捕获装饰器
+ **dingtalk_util.py**：钉钉消息推送

---

## 5. 数据工厂（核心概念）
### 5.1 什么是数据工厂
数据工厂负责**从数据库加载测试基础数据并缓存**，避免每次测试都查询数据库。

### 5.2 核心流程
```plain
1. 读取SQL配置文件（config/erp/xxx_init_sql.yaml）
   ↓
2. 执行SQL查询数据库
   ↓
3. 将结果缓存到JSON文件（testdata/cache/）
   ↓
4. 测试用例从缓存读取数据
```

### 5.3 使用方法
**在模块基类中初始化**：

```python
@classmethod
def setup_class(cls):
    super().setup_class()
    
    # 初始化数据工厂并加载缓存
    DataFactory.init_sql_cache(
        sql_config_path="config/erp/md_init_sql.yaml",
        db_config_name="erp_db",
        cache_key="inv_init_cache",
        cache_dir="testdata/cache"
    )
    
    # 获取缓存数据
    cls.inv_cache_data = CacheUtil.get('inv_init_cache')
```

**在测试用例中使用**：

```python
def test_something(self):
    # 从缓存获取物料ID
    mat_id = self.inv_cache_data.get("mat_info", {}) \
        .get("mat_md", {}).get("FINP", [])[0].get("id")
    
    # 使用物料ID进行测试
    response = self.http.post("/api/create", json={"matId": mat_id})
```

### 5.4 SQL配置示例
**config/erp/md_init_sql.yaml**：

```yaml
mat_info:
  mat_md:
    FINP:
      sql: |
        SELECT id, mat_code, mat_name 
        FROM gen_mat_md 
        WHERE mat_type = 'FINP' 
        AND deleted = 0 
        LIMIT 10

org_info:
  inv_org_info:
    sql: |
      SELECT id, org_name, org_code 
      FROM gen_inv_org 
      WHERE deleted = 0 
      LIMIT 1
```

### 5.5 缓存管理
```bash
# 清除所有缓存
rm -rf testdata/cache/*.json
```

缓存默认有效期24小时，超时自动重新加载。

### 5.6 erp_data_factory 框架状态说明 ✅

**当前状态**：`erp_data_factory` 已作为主路径；旧 `data_factory/` 目录已下线

**已实现**：
- ✅ SDK / CLI / FastAPI 三端统一入口
- ✅ Org / Material / Partner 三场景
- ✅ 执行审计上下文（request_id/scenario_key/profile/env）
- ✅ 能力清单与可选异步任务模式（进程内任务管理）
- ✅ 兼容层 `erp_data_factory.compat.*`

**当前推荐做法**：
```python
# ✅ 推荐：直接使用 standard_api_call 创建测试数据
response, partner_id = self.standard_api_call(
    api_key="GEN-合作伙伴-保存服务",
    set_dict={"code": "AT_PARTNER001", "name": "测试合作伙伴"}
)
```

**注意事项**：
- 旧 `data_factory/` 目录已删除
- 优先使用 `standard_api_call` 方法
- `erp_data_factory` 的 `legacy` 仍承接部分历史逻辑，后续会持续收敛

---

## 6. API配置文件重新获取指南
### 6.1 什么是API配置文件
API配置文件（如`inv_api_path.yaml`、`pur_api_path.yaml`）位于 `config/api/` 目录下，用于存储模块的API路径和参数配置，是测试用例的重要依赖。当系统接口发生变更时，需要重新获取最新的API配置。

### 6.2 重新获取API配置的完整流程
以`config/api/scm_inv/inv_api_path.yaml`为例，分为**Console处理**和**代码处理**两个步骤：

---

#### 步骤1：Console控制台处理
<!-- 这是一张图片，ocr 内容为：这里可以跳转SWAGGER 地址 密 扩展服务 . 库存风险通知 密扩展服务 台  余额管理 本存管理X 库存管理 类块配置-库存管理(SCM_INV) 内部模块 查看 SWAGGER 库存管理 基本信息 @基础配置 Q摆索 A 搅块名称 请输入 库存管理 模块类型 绑定效据道 模块标识 内部模块 基本信息 请输入横块推述 描述 获取这里的模块标识 车存管理/SCM_INV ATP 成员管理 对账管理 保存福块信息 导入导出 亚科配置 危险区 摇块位款 刑除模块 安点管理 -->
![](https://cdn.nlark.com/yuque/0/2025/png/35167331/1760342825974-e5283e92-4d70-4e81-8b49-e9295e10a22d.png)

<!-- 这是一张图片，ocr 内容为： -->
![](控制台处理截图.png)

---

#### 步骤2：代码处理
使用项目中的`script/swagger_parser.py`脚本重新生成API配置文件。

需要替换的内容参考以下截图

<!-- 这是一张图片，ocr 内容为：VENV 'EMP-COOKIE':'EYJBEXAIOIJKVIQILCJHBGCIOIJIUZIINI39.EYJOB2TLBKIKIKIJOINDLHZMJLOTE3YTDHN 609 CONFIG 'T-IAM-TEST'; 'EYJBEXAIOIJKVIQILCJHBGCIOIJIUZIINI39.EYJ0B2TLBKLKIJOIZWESMDJJMWFLMDBMN 610 DATA 611 DATA_FACTORY 612 2 LOGS 613 PARSER SWAAAGERPARSER( REPORTS BASE URL-"HTTPS://T-ERP-HUOSHAN-CONSOLE-TEST.APP.DUANDIAN.COM", 614系 ROUTERS 615 替换正确的URL地址 COOKIESCOOKIES SCRIPT 616 CASE_COVERAGE_STAT.PY 3 617 FIND_UNREFERENCED_SERVICES.PY 替换模块标识 #获取指定团队和模块的SWAGGER文档 618 SWAGGER_PARSER.PY 619 SWAGGER_DOC - PARSER.FETCH_SWAGGER_DOD("TERP", "SCM_INV") STATIC 620 TESTCASES #解析所有接口 621 PYCACHE 622 COMM ENDPOINTS PARSER.PARSE_ENDPOINTS() FIN 替换模块标识 623 GEN_MD #保存路径信息到GEN_PATH.YAML 624 PRD 625 PARSER .SAVE-PATHS_TO-YAML(ENDPOINTS,MODULE "SCM INV') SCM_INV 626 _PYCACHE_ #保存统一结构到UNIFIED_API.YAML 627 ATP 628 # PARSER.SAVE_UNIFIED_API-YAML(ENDPOINTS, MODULE二"SCM_PUR") BATCH_MANAGEMENT 执行这个文件就可以拉取最新的YAML文件下来了 629 . INVENTORY U & TEST INVENTORY BALANCE.PY -->
![](https://cdn.nlark.com/yuque/0/2025/png/35167331/1760342871251-72ff75ff-0854-44fc-ae4c-e80d441e2289.png)

**核心代码示例**：

```python
from script.swagger_parser import SwaggerParser

# 初始化解析器
parser = SwaggerParser()

# 获取所有接口端点
endpoints = parser.get_all_endpoints()

# 根据需求选择保存方式：

# 方式1：不包含系统服务的接口（推荐用于业务模块）
parser.save_unified_api_yaml(endpoints, module="SCM_INV")

# 方式2：包含系统服务的接口（用于需要系统接口的场景）
parser.save_paths_to_yaml(endpoints, module="SCM_PUR", include_sys_services=True)
```

**参数说明**：

+ `module`：业务模块标识（如`SCM_INV`、`SCM_PUR`、`SCM_SLS`等）
+ `include_sys_services`：是否包含系统服务接口
    - `True`：生成包含系统服务的完整接口配置
    - `False`或不传：仅生成业务接口配置（默认）

**选择判断依据**：

| 场景 | 使用方法 | 说明 |
| --- | --- | --- |
| 常规业务测试 | `save_unified_api_yaml` | 只包含业务接口，配置文件更简洁 |
| 需要系统接口 | `save_paths_to_yaml(include_sys_services=True)` | 包含系统级服务接口，配置更全面 |


---

#### 步骤3：验证生成的配置文件
**检查生成的YAML文件**：

```bash
# 默认会在script目录下生成path和params 2个yaml文件
```

#### 步骤4：应用新配置并测试
**更新测试用例**：

```python
# 测试用例中使用新的API配置
api_path = self.get_api_path("INV-ATP-手动创建单据")  # 使用更新后的API名称
params, url = self.get_api_params(api_path)

response = self.http.post(url, json=params)
self.assert_util.assert_equal(response['code'], 200)
```

---

## 7. AI提示词最佳实践
### 7.1 提示词模板
**通过提示词生成测试用例**：

```plain
curl '[你的curl请求]'
根据上述curl和coding_standards.md生成对应功能的代码（新建采购订单）
```

**修改现有方法**：

```plain
curl '[你的curl请求]'
根据上述curl和coding_standards.md修改对应功能的代码test_query_atp_group_export
```

**通过提示词+Rules生成测试用例**：

```plain
curl '[你的curl请求]'
根据上述curl和coding_standards.md + @testcase_temp.md生成对应功能的测试用例
```

## 8. 测试调试与执行
### 8.1 按方法调试（单个测试方法）
**命令格式**：

```bash
python -m pytest 文件路径::类名::方法名 -v -s
```

**示例**：

```bash
python -m pytest \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py::TestMobileVoucherManagement::test_query_mobile_voucher_page \
  -v -s
```

**说明**：

+ `-v`：显示详细输出
+ `-s`：显示print输出
+ `::` ：路径分隔符

---

### 8.2 按文件调试（整个测试文件）
**命令格式**：

```bash
python -m pytest 文件路径 -v -s
```

**示例**：

```bash
python -m pytest \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py \
  -v -s
```

---

### 8.3 按目录执行（整个模块）
**命令格式**：

```bash
python -m pytest 目录路径/ -v --tb=short
```

**示例**：

```bash
python -m pytest testcases/scm_inv/inv_atp/ -v --tb=short
```

**说明**：

+ `--tb=short`：简化错误堆栈信息
+ `--tb=line`：只显示一行错误
+ `--tb=no`：不显示堆栈

---

### 8.4 执行多个测试方法
**命令格式**：

```bash
python -m pytest \
  文件::类::方法1 \
  文件::类::方法2 \
  文件::类::方法3 \
  -v -s
```

**示例**：

```bash
python -m pytest \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py::TestMobileVoucherManagement::test_query_material_batch_feature \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py::TestMobileVoucherManagement::test_generate_batch_code \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py::TestMobileVoucherManagement::test_save_batch \
  testcases/scm_inv/mobile_voucher/test_mobile_voucher_management.py::TestMobileVoucherManagement::test_save_mobile_voucher \
  -v -s
```

---

### 8.5 其他常用参数
```bash
# 失败重试3次
pytest testcases/ --reruns 3 -v

# 并行执行（4个进程）
pytest testcases/ -n 4 -v

# 只执行失败的用例
pytest testcases/ --lf -v

# 先执行失败的，再执行其他
pytest testcases/ --ff -v

# 执行特定标记的用例
pytest testcases/ -m critical -v

# 排除特定标记
pytest testcases/ -m "not low" -v

# 详细输出+实时日志
pytest testcases/ -v -s --log-cli-level=INFO

# 生成Allure报告
pytest testcases/ --alluredir=reports/allure-results -v
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

### 8.6 调试最佳实践流程 ⭐
**核心原则**：从小到大，逐层验证

#### 为什么要按顺序调试？
❌ **错误做法**：直接运行整个模块

```bash
# 直接运行整个库存模块（可能包含几十个测试文件）
pytest testcases/scm_inv/ -v
```

**问题**：

+ ❌ 报错太多，无法定位问题
+ ❌ 浪费时间，效率低下
+ ❌ 不知道哪个文件有问题

✅ **正确做法**：按照以下顺序逐层验证

---

#### 步骤1：先调试单个测试文件
**目的**：确保单个文件的测试方法都能正常执行

**命令**：

```bash
python -m pytest testcases/scm_inv/inv_atp/test_inv_atp_lock_sale.py -v -s
```

**检查点**：

+ ✅ 文件能否正常加载
+ ✅ setup_class是否正常执行
+ ✅ 每个测试方法是否通过
+ ✅ 数据库连接是否正常
+ ✅ API请求是否成功

**如果有问题**：

+ 检查导入是否正确
+ 检查配置是否正确
+ 使用`-s`参数查看print输出
+ 检查日志文件

---

#### 步骤2：再调试子目录
**目的**：确保同一功能模块的所有文件都能协同工作

**命令**：

```bash
# 调试ATP子目录（包含4个测试文件）
python -m pytest testcases/scm_inv/inv_atp/ -v --tb=short
```

**检查点**：

+ ✅ 多个文件之间是否有冲突
+ ✅ 测试执行顺序是否正确
+ ✅ 共享数据是否正常
+ ✅ 缓存数据是否有效

**常见问题**：

+ 文件A和文件B的测试方法有依赖关系
+ 数据库数据被前面的测试修改了
+ 缓存数据过期或不一致

**解决方法**：

```bash
# 只运行失败的测试
pytest testcases/scm_inv/inv_atp/ --lf -v

# 先运行失败的，再运行其他
pytest testcases/scm_inv/inv_atp/ --ff -v
```

---

#### 步骤3：最后调试模块级目录
**目的**：确保整个业务模块的所有测试都能正常执行

**命令**：

```bash
# 调试整个库存模块（包含inv_atp、inv_batch、inv_mvm、inv_stk等子目录）
python -m pytest testcases/scm_inv/ -v --tb=short
```

**检查点**：

+ ✅ 所有子目录的测试都通过
+ ✅ 不同子目录之间无冲突
+ ✅ 整体测试时间是否合理
+ ✅ 资源占用是否正常

**优化执行**：

```bash
# 并行执行（4个进程）
python -m pytest testcases/scm_inv/ -n 4 -v

# 失败重试（失败后重试2次）
python -m pytest testcases/scm_inv/ --reruns 2 -v

# 只运行critical级别
python -m pytest testcases/scm_inv/ -m critical -v
```

---

#### 调试流程总结
```plain
第1步：单个文件
└─ python -m pytest testcases/scm_inv/inv_atp/test_inv_atp_lock_sale.py -v -s
   ✅ 通过 → 进入第2步
   ❌ 失败 → 修复后重新测试
   
第2步：子目录
└─ python -m pytest testcases/scm_inv/inv_atp/ -v --tb=short
   ✅ 通过 → 进入第3步
   ❌ 失败 → 定位问题文件，返回第1步
   
第3步：模块级目录
└─ python -m pytest testcases/scm_inv/ -v --tb=short
   ✅ 通过 → 调试完成
   ❌ 失败 → 定位问题子目录，返回第2步
```

---

#### 调试技巧补充
**技巧1：使用pytest的测试选择功能**

```bash
# 只运行包含"create"的测试方法
pytest testcases/scm_inv/ -k "create" -v

# 排除"delete"相关的测试
pytest testcases/scm_inv/ -k "not delete" -v
```

**技巧2：生成测试报告查看详情**

```bash
# 生成HTML报告
pytest testcases/scm_inv/ --html=reports/report.html --self-contained-html

# 生成Allure报告
pytest testcases/scm_inv/ --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

**技巧3：查看测试覆盖率**

```bash
# 生成覆盖率报告
pytest testcases/scm_inv/ --cov=testcases/scm_inv --cov-report=html
```

---

### 8.7 跨模块调用注意事项 ⚠️
**核心原则**：避免跨业务模块调用方法，防止产生不必要的依赖关系

**允许的调用范围**：

+ ✅ 同一功能模块下，子目录之间的方法调用
+ ✅ 同一文件内，多个方法之间的依赖调用

**禁止的调用**：

+ ❌ 不要跨业务模块调用（如库存模块调用采购模块的方法）

**示例说明**：

```python
# ✅ 允许：同模块下子目录调用
# testcases/scm_inv/inv_stk/test_balance.py 调用
# testcases/scm_inv/inv_mvm/test_voucher.py 的方法

# ❌ 禁止：跨模块调用
# testcases/scm_inv/... 调用 testcases/scm_pur/... 的方法
```

**原因**：跨模块依赖会导致模块耦合度高，维护困难，测试运行时可能产生意外的副作用。

---

## 9. Cursor使用技巧
### 9.1 反复解决不了的问题时
**❌**** 错误做法**：反复在同一对话中问AI同样的问题

**✅**** 正确做法**：让AI执行命令并对比curl

```plain
你去执行这个命令：
python -m pytest testcases/xxx/test_xxx.py::TestXxx::test_xxx -v -s

并且对比这个curl：
curl 'https://xxx' -H 'xxx' -d 'xxx'

帮我修复这个问题
```

**为什么有效**：AI直接看到执行结果和请求差异，一次性定位问题

---

### 9.2 Context超过60%时
**做法**：直接切换新窗口，重新开始

**原因**：清空无用上下文，AI响应更准确，反而更省力

**重要提醒** ⚠️：

不要在单个Session中反复纠错，避免以下问题：

+ ❌ 上下文过长导致AI理解偏差
+ ❌ 上下文压缩后前面的修改被遗忘
+ ❌ 产生大量临时变量和不一致的代码
+ ❌ 越改越乱，甚至改错

**最佳实践**：

+ ✅ 一个需求尽量在一个Session内完成
+ ✅ 保证足够的上下文可用（<60%）此处百分比仅作为建议
+ ✅ 完成不了直接拆分需求，新开窗口
+ ✅ 不要觉得新开窗口麻烦，这样效率更高

---

### 9.3 代码优化提示词
功能调试完成后使用：

```plain
以ERP高级开发专家身份，对当前文件的代码进行审查：
聚焦优化空间与冗余代码，确保不改变现有代码结构与业务逻辑，有问题就帮我直接修改。
```

---

### 9.4 高效使用原则
1. **问题描述具体**：不要说"代码有问题"，终端执行报错后直接选中然后 Add to chat
2. **提供完整信息**：错误日志 + curl请求 + 预期结果 + 实际结果
3. **善用@符号**：`@文件名`引用文件，`@codebase`搜索代码库
4. **适时重置对话**：Context过大或问题解决不了时，切换新窗口

### 9.5 代码提交远程仓库
```bash
提示词：
1. 检查远程仓库是否有更新
2. 如有更新则拉取，否则跳过
3. 提交本地修改到 feature/develop 分支（排除 .env 文件）
```

---

## 10. 测试用例编写指南
### 10.1 测试用例模板
```python
import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator

@allure.epic("业务领域")
@allure.feature("功能模块")
class TestMyFeature(GenMdBaseTest):
    """测试类说明"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.my_object_id = None
        cls.logger.info("测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        try:
            cls.db.delete(table="my_table", where="code like %s", params=["AT_%"])
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="业务场景",
        title="测试标题",
        description="测试描述",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["标签1", "标签2"]
    )
    def test_case_name(self):
        """测试方法说明"""
        try:
            # 1. 准备测试数据
            code = self.mock_util.generate_unique_code(tag="AT_PREFIX")
            name = f"测试对象_{self.mock_util.get_timestamp()}"
            
            # 2. 使用标准化API调用
            set_dict = {
                "code": code,
                "name": name,
                "status": "ENABLED"
            }
            response, extracted_id = self.standard_api_call(
                api_key="API服务名称",
                set_dict=set_dict,
                store_id_as="my_object"  # 自动存储为 self.my_object_id
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 记录关键数据
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

### 10.2 命名规范
**测试文件**：`test_模块_功能.py`

```python
test_inv_atp_lock_sale.py
test_po_type_management.py
```

**测试类**：`Test模块功能`（必须Test开头）

```python
class TestInvAtpLockSale
class TestPoTypeManagement
```

**测试方法**：`test_具体场景`（必须test_开头）

```python
def test_create_sale_order
def test_query_po_type_list
```

**命名参考来源** ⭐：

1. 进入Console页面
2. 找到对应的业务模块
3. 查看模型的命名规范
4. 参考模型命名来命名测试用例

**示例**：

```plain
Console中看到模型：inv_atp_lock（库存ATP锁定）
→ 测试文件：test_inv_atp_lock_sale.py
→ 测试类：TestInvAtpLockSale
→ 测试方法：test_create_sale_order
```

### 10.3 最佳实践

**1. 使用 standard_api_call（推荐）**

```python
def test_save_partner(self):
    """使用 standard_api_call 简化API调用"""
    try:
        # 准备数据
        code = self.mock_util.generate_unique_code(tag="AT_PARTNER")
        name = f"测试合作伙伴_{self.mock_util.get_timestamp()}"
        
        # 标准化API调用
        set_dict = {"code": code, "name": name}
        response, extracted_id = self.standard_api_call(
            api_key="GEN-合作伙伴-保存服务",
            set_dict=set_dict,
            store_id_as="partner"
        )
        
        # 断言
        self.assert_util.assert_response_data(response)
        
    except Exception as e:
        a.text(str(e), "失败原因")
        raise
```

**2. 使用缓存数据**

```python
@classmethod
def setup_class(cls):
    super().setup_class()
    # 安全获取缓存数据
    if cls.md_cache_data:
        cust_info = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])
        cls.cust_id = cust_info[0].get("id") if cust_info else None
```

**3. 参数化测试**

```python
@pytest.mark.parametrize("test_data", [
    {
        "name": "正常流程",
        "debit_amt": 123.45,
        "credit_amt": 123.45,
        "expected_success": True,
        "expected_status": "APPROVING"
    },
    {
        "name": "借贷不平衡",
        "debit_amt": 100.00,
        "credit_amt": 200.00,
        "expected_success": False,
        "expected_error_code": "glm.ve.credit.debit.not.equal"
    }
])
def test_submit_voucher(self, test_data):
    """参数化测试示例"""
    # 使用 test_data 中的参数
    set_dict = {
        "debitAmt": test_data["debit_amt"],
        "creditAmt": test_data["credit_amt"]
    }
    response, _ = self.standard_api_call(
        api_key="凭证-提交服务",
        set_dict=set_dict
    )
    
    # 统一断言逻辑
    if test_data["expected_success"]:
        self.assert_util.assert_response_success(response)
    else:
        assert response["err"]["code"] == test_data["expected_error_code"]
```

例：对于同一个接口不同的入参以及不同的断言可以使用mark.parametrize装饰器来进行编写用例

```python
@pytest.mark.parametrize("test_data", [
        {
            "name": "正常借贷平衡",
            "debit_amt": 123.45,
            "credit_amt": 123.45,
            "remark": "测试正常业务流程",
            "expected_status": "APPROVING",
            "use_cash_account": False,
            "expected_success": True,
            "expected_error_code": None,
            "expected_error_msg": None
        },
        {
            "name": "借贷金额不平衡",
            "debit_amt": 100.00,
            "credit_amt": 200.00,
            "remark": "测试借贷不平衡业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": False,
            "expected_success": False,
            "expected_error_code": "glm.ve.credit.debit.not.equal",
            "expected_error_msg": "凭证借贷不相等"
        },
        {
            "name": "现金类科目不指定现金流量",
            "debit_amt": 500.00,
            "credit_amt": 500.00,
            "remark": "测试现金类科目不指定现金流量业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": True,
            "expected_success": False,
            "expected_error_code": "glm.ve.amt.of.cai.and.cas.item.check.not.equal",
            "expected_error_msg": "凭证流量检查不通过，现金科目金额与凭证行现金类科目金额不相等"
        },
        {
            "name":"辅助维度科目不指定辅助维度值",
            "debit_amt": 4.12,
            "credit_amt": 4.12,
            "remark": "测试辅助维度科目不指定辅助维度值业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": False,
            "use_ad_account": True,  # 使用辅助维度科目
            "expected_success": False,
            "expected_error_code": "glm.ve.ads.required.ad.miss",
            "expected_error_msg": "必填维度缺失"
        }
    ])
   def test_submit_voucher(self, test_data):
        """测试总账凭证提交操作"""
        # 首先创建凭证
        self.create_voucher_with_amounts(
            test_data["debit_amt"], 
            test_data["credit_amt"], 
            test_data["remark"],
            test_data.get("use_cash_account", False),
            test_data.get("use_ad_account", False)
        )
        url=self.get_api_path("总账-凭证-凭证列表提交服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        
        sql=f"""
        select id from fin_glm_ve_head_tr where remark='{test_data["remark"]}' and ve_status='DRAFT' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        
        # 统一断言逻辑
        if test_data["expected_success"]:
            # 成功情况断言
            self.assert_util.assert_response_success(response)
            self.assert_util.assert_by_operator(
                response["data"]["data"]["veStatus"], 
                "=", 
                test_data["expected_status"], 
                f"凭证状态不是{test_data['expected_status']}"
            )
        else:
            # 失败情况断言
            assert response["success"] is False
            self.assert_util.assert_by_operator(
                response["err"]["code"], 
                "=", 
                test_data["expected_error_code"], 
                f"错误代码不是{test_data['expected_error_code']}"
            )
            self.assert_util.assert_by_operator(
                response["err"]["msg"], 
                "=", 
                test_data["expected_error_msg"], 
                f"错误信息不是{test_data['expected_error_msg']}"
            )
```

1、将不同的入参和期望的断言值组成一个参数

2、在具体用例代码中使用这个test_data参数

3、断言时只需要一个ifelse分支即可完成断言，因为成功情况的接口返回结构几乎都是相同的，失败情况的接口返回结构也是相同的，只是返回的结果的值不同。

4、通过使用1中的断言参数即可完成断言

**重点：断言的期望值一定要放在mark.parametrize装饰器中，防止入参过多导致不同的断言过多，从而导致ifelse分支变多难以维护**

**4. 数据清理**

```python
@classmethod
def teardown_class(cls):
    """测试类结束后执行数据清理"""
    try:
        # 使用数据库批量删除测试数据
        cls.db.delete(
            table="inv_atp_group_md",
            where="code like %s",
            params=["AUTOTEST_ATP_%"]
        )
        cls.logger.info("ATP检查组测试数据清理完成")
    except Exception as e:
        cls.logger.error(f"测试数据清理失败: {str(e)}")
```

---

### 10.4 测试用例编写方法对比 ⭐
本章节对比两种主流的自动化测试用例编写方法，帮助你选择最适合的方式。

---

#### 方法1：传统抓包方式（手动编写）
**适用场景**：

+ ✅ 简单的API测试
+ ✅ 需要深入理解业务逻辑
+ ✅ API文档不完善
+ ✅ 学习阶段，需要熟悉框架

**操作步骤**：

**第1步：使用浏览器开发者工具抓包**

```plain
1. 打开Chrome浏览器
2. 按F12打开开发者工具
3. 切换到Network标签
4. 在页面上执行操作（如创建订单）
5. 在Network中找到对应的API请求
6. 查看Request URL中的path路径
```

**第2步：在YAML配置文件中查找API名称**

**操作步骤**：

1. 复制Network中的API路径（如：`/api/trantor/action/scm_inv/inv_atp_lock/create`）
2. 打开对应模块的YAML配置文件（如：`config/api/scm_inv/inv_api_path.yaml`）
3. 使用`Ctrl+F`搜索该路径
4. 找到对应的API名称（如：`INV-ATP-手动创建单据`）

**配置文件示例**：

```yaml
# config/api/scm_inv/inv_api_path.yaml
INV-ATP-手动创建单据:
  path: /api/trantor/action/scm_inv/inv_atp_lock/create
  method: POST

INV-ATP-查询列表:
  path: /api/trantor/action/scm_inv/inv_atp_lock/query
  method: POST
```

**第3步：分析请求体参数**

在Network中查看请求的Payload（请求体）：

```json
{
  "params": {
    "request": {
      "docClass": "SO",
      "docPosneg": "NEG",
      "planQty": 5,
      "matId": 123,
      "invOrgId": 456
    }
  }
}
```

**手动分析参数**：

+ ✅ 识别参数层级：`params` → `request` → 具体字段
+ ✅ 区分对象字段：`matId`、`invOrgId`是对象ID（需要从缓存获取）
+ ✅ 判断必传字段：`docClass`、`planQty`是必传字段
+ ✅ 识别可选字段：某些字段可以省略或使用默认值

**第4步：手动编写测试代码（旧方法）**

```python
import allure
from testcases.scm_inv import ScmInvBaseTest
from utils.report_util import case_decorator
from utils.param_util import ParamUtil

@allure.epic("库存管理")
@allure.feature("ATP库存占量")
class TestInvAtpLock(ScmInvBaseTest):
    
    @case_decorator(
        story="ATP占量",
        title="创建销售单",
        severity="critical",
        file_level_order=1
    )
    def test_create_sale_order(self):
        """创建销售单（旧方法）"""
        # 使用从YAML中找到的API名称
        api_path = self.get_api_path("INV-ATP-手动创建单据")
        params, url = self.get_api_params(api_path)
        
        # 手动分析并构建请求参数
        request_data = ParamUtil.filter_post_body_fields(
            params,
            ["docClass", "docPosneg", "planQty", "matId", "invOrgId"],
            ["params", "request"]
        )
        
        # 设置参数值
        ParamUtil.set_request_params(request_data, {
            "docClass": "SO",
            "docPosneg": "NEG",
            "planQty": 5,
            "matId": self.mat_id,
            "invOrgId": self.inv_org_id
        })
        
        # 发送请求
        response = self.http.post(url, json=request_data)
        
        # 手动编写断言
        self.assert_util.assert_equal(response['code'], 200)
        self.assert_util.assert_not_none(response['data'])
```

**第4步（推荐）：使用 standard_api_call**

```python
import allure
from testcases.scm_inv import ScmInvBaseTest
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("ATP库存占量")
class TestInvAtpLock(ScmInvBaseTest):
    
    @case_decorator(
        story="ATP占量",
        title="创建销售单",
        severity="critical",
        file_level_order=1
    )
    def test_create_sale_order(self):
        """创建销售单（新方法）"""
        try:
            # 准备测试数据
            set_dict = {
                "docClass": "SO",
                "docPosneg": "NEG",
                "planQty": 5,
                "matId": self.mat_id,
                "invOrgId": self.inv_org_id
            }
            
            # 使用 standard_api_call（自动处理参数过滤和设置）
            response, extracted_id = self.standard_api_call(
                api_key="INV-ATP-手动创建单据",
                set_dict=set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 记录关键数据
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```


**第5步：调试参数**

```python
# 逐步调试，找到正确的参数
def test_create_sale_order(self):
    # 打印请求参数，确认结构
    print(f"Request: {request_data}")
    
    response = self.http.post(api_path, json=request_data)
    
    # 打印响应，分析结果
    print(f"Response: {response}")
    
    # 如果失败，分析错误信息
    if response['code'] != 200:
        print(f"Error: {response.get('message')}")
        # 调整参数后重新测试
```

**优点**：

+ ✅ 完全掌控代码逻辑
+ ✅ 深入理解API结构
+ ✅ 学习框架和业务
+ ✅ 不依赖AI工具

**缺点**：

+ ❌ 编写速度慢
+ ❌ 容易出错（拼写、结构）
+ ❌ 需要反复调试
+ ❌ 重复性工作多

---

#### 方法2：AI提示词方式（快速生成）
**适用场景**：

+ ✅ 快速开发大量测试用例
+ ✅ 标准化、规范化的代码
+ ✅ 减少重复性工作
+ ✅ 提高开发效率
+ ✅ 自动使用 standard_api_call 方法

**操作步骤**：

**第1步：获取curl请求**

```bash
# 从浏览器开发者工具复制curl
curl 'https://test-erp.com/api/trantor/action/gen_md/partner/save' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: SESSION=abc123...' \
  -d '{
    "params": {
      "request": {
        "code": "AT_PARTNER001",
        "name": "测试合作伙伴",
        "partnerType": "CUSTOMER"
      }
    }
  }'
```

**第2步：使用AI提示词生成代码**

在Cursor中输入提示词：

```plain
curl 'https://test-erp.com/api/trantor/action/gen_md/partner/save' \
  -H 'Content-Type: application/json' \
  -d '{"params":{"request":{"code":"AT_PARTNER001","name":"测试合作伙伴","partnerType":"CUSTOMER"}}}'

根据上述curl和coding_standards.md生成对应功能的测试代码（创建合作伙伴）
```

**注意**：AI会自动使用 `standard_api_call` 方法生成代码

**第3步：AI自动生成完整代码**

AI会生成：

```python
import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator

@allure.epic("主数据管理")
@allure.feature("合作伙伴管理")
class TestPartnerManagement(GenMdBaseTest):
    """合作伙伴管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.partner_id = None
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
        story="创建合作伙伴",
        title="测试创建合作伙伴",
        description="验证创建合作伙伴的基本功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["主数据", "合作伙伴"]
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
                "partnerType": "CUSTOMER"
            }
            response, extracted_id = self.standard_api_call(
                api_key="GEN-合作伙伴-保存服务",
                set_dict=set_dict,
                store_id_as="partner"  # 自动存储为 self.partner_id
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 记录关键数据
            a.json(response, "响应数据")
            self.logger.info(f"创建合作伙伴成功，ID: {self.partner_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

**第4步：直接运行测试**

```bash
# AI生成的代码通常可以直接运行
python -m pytest testcases/scm_inv/inv_atp/test_inv_atp_lock_sale.py::TestInvAtpLockSale::test_create_sale_order -v -s
```

**优点**：

+ ✅ 编写速度快（1-2分钟）
+ ✅ 代码规范统一
+ ✅ 自动使用 standard_api_call
+ ✅ 包含完整的装饰器和注释
+ ✅ 减少人为错误
+ ✅ 可批量生成测试用例
+ ✅ 自动处理异常和报告

**缺点**：

+ ❌ 依赖AI工具
+ ❌ 需要理解提示词规则
+ ❌ 可能需要微调代码
+ ❌ 初次使用有学习成本

---

#### 两种方法对比表
| 对比维度 | 传统抓包方式 | AI提示词方式 |
| --- | --- | --- |
| **编写速度** | ⭐⭐ 慢（15-30分钟/用例） | ⭐⭐⭐⭐⭐ 快（1-2分钟/用例） |
| **代码质量** | ⭐⭐⭐ 取决于个人水平 | ⭐⭐⭐⭐⭐ 统一规范 + standard_api_call |
| **学习成本** | ⭐⭐⭐⭐ 需要熟悉框架 | ⭐⭐ 掌握提示词即可 |
| **调试难度** | ⭐⭐ 容易出错，需反复调试 | ⭐⭐⭐⭐⭐ 生成代码质量高 |
| **维护成本** | ⭐⭐⭐ 代码风格可能不一致 | ⭐⭐⭐⭐⭐ 统一规范，易维护 |
| **适用场景** | 简单测试、学习阶段 | 批量开发、提高效率 |
| **工具依赖** | 无 | 需要Cursor/AI工具 |
| **推荐指数** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |


---

## 11. 常见问题FAQ

**Q1: 为什么需要__init__.py？**  
声明Python包、管理项目路径、定义模块基类

**Q2: setup_class和setup_method区别？**

+ `setup_class`：类级别，执行一次
+ `setup_method`：方法级别，每个方法前执行

**Q3: 测试顺序如何控制？**  
文件内排序用`file_level_order=1`，全局排序用`@pytest.mark.order(1)`

**Q3.1: 什么时候使用 standard_api_call？**  
**答**：95%的场景都应该使用 `standard_api_call`，它能：
- ✅ 自动处理参数过滤和设置
- ✅ 统一异常处理和报告记录
- ✅ 支持自动存储ID（store_id_as）
- ✅ 减少代码量 50%

**Q3.2: 如何测试异步任务？**  
**答**：使用 `AsyncWaitUtil` 进行状态轮询：
```python
result = self.async_wait_util.wait_for_async_status(
    query_func=query_status,
    status_field="asyncExecutionStatus",
    success_status="SUCCEEDED",
    max_wait=60,
    interval=3.0
)
```

**Q3.3: 缓存数据如何更新？**  
**答**：缓存支持自动过期刷新（默认24小时）：
```bash
# 方式一：删除缓存文件
rm testdata/cache/*.json

# 方式二：设置过期时间（在配置文件中）
cache:
  expire_minutes: 60  # 1小时过期
```

**Q4: 如何封装可复用的业务方法？**

当某个业务操作（如创建采购订单）在多个测试用例中频繁使用时，建议将其封装成独立的辅助方法，而不是写成测试方法。

**方式1：封装为类方法（推荐）⭐**

```python
class TestPurchaseOrder(ScmPurBaseTest):
    """采购订单测试类"""
    
    @classmethod
    def create_purchase_order(cls, supplier_id=None, mat_id=None, qty=None, **kwargs):
        """
        创建采购订单的可复用方法
        
        Args:
            supplier_id: 供应商ID（不传则使用默认值）
            mat_id: 物料ID（不传则使用默认值）
            qty: 数量（不传则使用默认值）
            **kwargs: 其他可选参数
        
        Returns:
            dict: 采购订单创建结果
        """
        # 使用传入的参数或默认值
        supplier_id = supplier_id or cls.pur_cache_data.get("supplier_info", [])[0].get("id")
        mat_id = mat_id or cls.pur_cache_data.get("mat_info", [])[0].get("id")
        qty = qty or 10
        
        # 获取API
        api_path = cls.get_api_path("PUR-PO-创建采购订单")
        params, url = cls.get_api_params(api_path)
        
        # 设置参数
        ParamUtil.set_request_params(params, {
            "supplierId": supplier_id,
            "matId": mat_id,
            "qty": qty,
            **kwargs  # 支持额外参数
        })
        
        # 发送请求
        response = cls.http.post(url, json=params)
        cls.assert_util.assert_equal(response['code'], 200, "创建采购订单成功")
        
        return response['data']
    
    @case_decorator(
        story="采购订单",
        title="测试采购订单审批流程",
        severity="critical"
    )
    def test_purchase_order_approval(self):
        """测试采购订单审批"""
        # 直接调用封装的方法
        po_data = self.create_purchase_order(qty=20)
        
        # 继续后续测试逻辑
        order_id = po_data['id']
        # ... 审批逻辑
```

**优点**：

+ ✅ 代码复用，减少重复代码
+ ✅ 参数灵活，支持默认值和自定义值
+ ✅ 不会作为测试用例被执行（没有`test_`前缀）
+ ✅ 易于维护，修改一处即可

---

**方式2：使用pytest.importorskip动态导入（避免重复执行）**

当需要在其他文件中调用某个测试类的方法时，使用动态导入可以避免pytest自动收集并执行该文件的所有测试方法。

```python
import pytest

class TestInventoryBalance(ScmInvBaseTest):
    """库存余额测试类"""
    
    def test_query_balance(self):
        """查询库存余额"""
        # 需要先创建移动凭证，但不想重复执行移动凭证测试文件的所有测试
        
        # 使用pytest.importorskip动态导入，避免pytest收集该测试类
        mobile_voucher_module = pytest.importorskip(
            'testcases.scm_inv.inv_mvm.test_inv_mvm_pur_management'
        )
        TestMobileVoucher = mobile_voucher_module.TestMobileVoucherManagement
        
        # 调用其方法（不会触发pytest收集和执行）
        voucher_data = TestMobileVoucher.create_mobile_voucher(
            self, 
            mat_id=self.mat_id,
            qty=100
        )
        
        # 继续测试逻辑
        self.logger.info(f"移动凭证创建成功: {voucher_data['id']}")
        # ... 查询余额逻辑
```

**优点**：

+ ✅ 动态导入，pytest不会收集该模块的测试用例
+ ✅ 避免重复执行其他文件的测试方法
+ ✅ 适用于跨文件调用场景

**对比总结**：

| 对比项 | 方式1：封装类方法 | 方式2：动态导入 |
| --- | --- | --- |
| **适用场景** | 本类内复用 | 跨文件调用 |
| **是否被pytest收集** | 否（无test_前缀） | 否（动态导入） |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **维护成本** | 低 | 中 |


**最佳实践建议**：

1. 优先使用方式1封装类方法，简单高效
2. 跨文件调用时使用方式2动态导入
3. 避免将业务逻辑写成测试方法（`test_`开头）

---

## 12. 总结
### 核心要点
1. **项目结构**：模块化，`__init__.py` 管理路径和基类
2. **BaseTest**：统一初始化，提供工具（http、db、logger、async_wait_util等）
3. **模块基类**：GenMdBaseTest/ScmInvBaseTest/ScmPurBaseTest，加载模块配置和缓存
4. **数据工厂**：SQL执行+缓存，避免重复查询，支持自动过期刷新
5. **工具类库**：15个工具类，覆盖HTTP、数据库、日志、断言、异步等待等
6. **standard_api_call**：统一API调用方法，简化测试用例编写（核心）
7. **异步任务测试**：AsyncWaitUtil 支持异步任务状态轮询和等待
8. **AI提效**：使用提示词快速生成测试代码，自动使用 standard_api_call

### 开发流程
```plain
1. 确定测试模块 → 2. 继承模块BaseTest → 3. 从缓存获取数据
4. 使用 standard_api_call 编写测试方法 → 5. 调试（文件→子目录→模块） → 6. 查看报告
```

### 学习路径
**入门**：了解项目结构 → 理解 `__init__.py` → 继承BaseTest编写用例 → 掌握 standard_api_call  
**进阶**：掌握数据工厂 → 编写模块BaseTest → 参数化测试 → 异步任务测试  
**高级**：自定义工具类 → 性能优化 → 框架扩展 → 数据工厂完善

---

## 13. 相关文档 📚

项目文档位于 `docs/` 目录，包括：

### 必读文档
1. **STANDARD_API_CALL_GUIDE.md** - standard_api_call 完整指南
   - 详细说明 `standard_api_call` 的参数、用法和各种场景
   - 包含自动模式和手动模式的使用示例
   - 常见错误和解决方案

2. **README.md** - 项目完整说明文档
   - 项目简介和核心能力
   - 技术栈和依赖说明
   - 快速开始和部署指南
   - 常见问题FAQ

### 参考文档
3. **cursor_testcase_generation.md** - 用例编写详细规范（如果存在）
   - 编写规范和代码示例
   - 最佳实践和注意事项

### 配置文件
4. **config/env/*.yaml** - 环境配置文件
   - 门户配置（多门户多租户）
   - 数据库配置
   - 缓存配置

5. **config/erp/*_init_sql.yaml** - 初始化SQL配置
   - base_init_sql.yaml：基础数据初始化
   - md_init_sql.yaml：主数据初始化
   - pur_init_sql.yaml：采购模块初始化
   - sls_init_sql.yaml：销售模块初始化

### 学习建议
1. **第一步**：阅读本文档（ERP自动化测试框架分享文档）
2. **第二步**：阅读 `STANDARD_API_CALL_GUIDE.md`，掌握核心方法
3. **第三步**：查看 `README.md`，了解项目全貌
4. **第四步**：参考实际测试用例（如 `testcases/gen_md/partner/test_text_management.py`）
5. **第五步**：使用AI提示词快速生成测试用例

---

**文档维护**：ERP自动化测试团队

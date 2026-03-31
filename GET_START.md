# GET_START — 新项目接入指南

> 本指南面向**在新业务模块/新 ERP 项目**中首次落地 API 自动化测试的工程师。  
> 阅读完成预计 20 分钟，跑通第一条用例约 45 分钟。

---

## 目录

1. [环境准备](#1-环境准备)
2. [项目结构说明](#2-项目结构说明)
3. [第一步：添加环境配置](#3-第一步添加环境配置)
4. [第二步：添加 API 配置](#4-第二步添加-api-配置)
5. [第三步：创建模块目录与基类](#5-第三步创建模块目录与基类)
6. [第四步：注册模块清理](#6-第四步注册模块清理)
7. [第五步：编写第一条用例](#7-第五步编写第一条用例)
8. [第六步：运行与查看报告](#8-第六步运行与查看报告)
9. [扩展数据源（可选）](#9-扩展数据源可选)
10. [快速检查清单](#10-快速检查清单)
11. [常见问题](#11-常见问题)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
pip install -r requirements.txt
```

### 1.2 必需工具

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Python | ≥ 3.10 | 使用了 `str \| None` 类型注解 |
| pytest | ≥ 7.0 | 测试运行器 |
| allure-pytest | ≥ 2.13 | 报告生成 |
| pytest-xdist | ≥ 3.0 | 并行执行（可选） |
| MySQL client | — | 测试数据清理 |

### 1.3 环境变量（`.env` 文件，不提交 Git）

```ini
TEST_ENV=test
TEST_PROJECT=your_project   # 多项目模式时必填；单项目可不填
TRANTOR_VERSION=2.5.x.xxxx.x-SNAPSHOT
ENABLE_PHYSICAL_DELETE=true
```

---

## 2. 项目结构说明

```
erp-autotest/
├── config/
│   ├── api/                      # API 路径与参数模板（按模块分目录）
│   │   └── {module}/
│   │       ├── {module}_api_path.yaml    # api_key → HTTP path + method
│   │       └── {module}_api_params.yaml  # path → 参数默认模板
│   └── env/                      # 环境配置
│       ├── test.yaml             # 默认（单项目模式）
│       └── {project}/
│           └── test.yaml         # 多项目模式
│
├── testcases/
│   ├── conftest.py               # 全局 pytest hooks（勿改）
│   ├── comm/
│   │   ├── base_test.py          # BaseTest 基类（勿改）
│   │   ├── api_call_service.py   # standard_api_call 核心逻辑（勿改）
│   │   ├── cleanup_registry.py   # 统一清理注册中心（勿改）
│   │   └── test_data_context.py  # 缓存路径解析（勿改）
│   │
│   └── {your_module}/            # ← 你只需要在这里添加文件
│       ├── __init__.py           # 模块基类
│       ├── conftest.py           # 模块清理注册
│       └── test_{feature}.py     # 用例文件
│
├── testdata/
│   └── cache/
│       └── init_cache.json       # 基础数据缓存（登录后自动生成）
│
└── utils/                        # 工具类（勿改）
```

---

## 3. 第一步：添加环境配置

### 单项目模式（最常用）

编辑或新建 `config/env/test.yaml`：

```yaml
# 被测系统 URL
portal_config:
  terp:                              # portal_key，对应登录时使用的 key
    url: "http://your-erp-host:8080"
    username: "admin"
    password: "your_password"
    tenant_code: "terp"

# 数据库（测试数据清理用）
database:
  erp_db:
    host: "192.168.x.x"
    port: 3306
    database: "erp_db"
    username: "erp_test"
    password: "xxxx"
  iam_db:
    host: "192.168.x.x"
    port: 3306
    database: "iam_db"
    username: "iam_test"
    password: "xxxx"

# Trantor 引擎版本（可被命令行参数覆盖）
trantor_version: "2.5.25.0330.0-SNAPSHOT"
```

### 多项目模式

```
config/env/
└── project_alpha/
    ├── test.yaml      # 测试环境
    └── staging.yaml   # 预发环境
```

运行时指定：

```bash
pytest --project=project_alpha --env=test
```

---

## 4. 第二步：添加 API 配置

每个业务模块需要两个 YAML 文件，放在 `config/api/{module}/` 下。

### 4.1 `{module}_api_path.yaml` — API 路径注册表

```yaml
version: '1.0'
total_apis: 3
apis:
  # api_key（中文可读名称，对应 standard_api_call 的 api_key 参数）
  MY_MODULE-保存服务:
    path: /api/trantor/service/engine/execute/MY_MODULE$SaveService
    method: POST

  MY_MODULE-分页查询服务:
    path: /api/trantor/service/engine/execute/MY_MODULE$QueryPageService
    method: POST

  MY_MODULE-删除服务:
    path: /api/trantor/service/engine/execute/MY_MODULE$DeleteService
    method: POST
```

> **如何快速获取 path？**  
> 在浏览器 DevTools Network 面板中找到对应操作的请求 URL，复制 `/api/trantor/...` 部分。

### 4.2 `{module}_api_params.yaml` — 参数模板

```yaml
api_params:
  /api/trantor/service/engine/execute/MY_MODULE$SaveService:
    params:
      request:
        code: null
        name: null
        status: null
        remark: null
    serviceKey: MY_MODULE$SaveService

  /api/trantor/service/engine/execute/MY_MODULE$QueryPageService:
    params:
      pageable:
        pageNo: 1
        pageSize: 20
        needTotal: true
      fields: []
    serviceKey: MY_MODULE$QueryPageService

  /api/trantor/service/engine/execute/MY_MODULE$DeleteService:
    params:
      request:
        id: null
    serviceKey: MY_MODULE$DeleteService
```

> **技巧**：从 curl 的 `data-raw` 字段中复制 `params.request` 内容，
> 去掉 `sceneKey`/`serviceKey`/`viewTitle`/`appId`/`teamId`/`version` 等平台噪音字段，
> 将实际值替换为 `null`，即得参数模板。

---

## 5. 第三步：创建模块目录与基类

### 5.1 新建目录

```bash
mkdir -p testcases/my_module
touch testcases/my_module/__init__.py
touch testcases/my_module/conftest.py
```

### 5.2 编写模块基类 `testcases/my_module/__init__.py`

```python
from testcases.comm.base_test import BaseTest

# 该模块加载的 API 配置文件前缀（对应 config/api/my_module/ 下的文件名）
_API_CONFIG_MODULES = ["my_module"]


class MyModuleBaseTest(BaseTest):
    """my_module 模块测试基类。"""

    @classmethod
    def setup_class(cls) -> None:
        super().setup_class()

        # 加载本模块的 API 路径配置（可叠加多个）
        for module in _API_CONFIG_MODULES:
            cls.api_facade.load_api_config(module)

        cls.logger.info("MyModule 基类初始化完成")
```

> **说明**：`api_facade.load_api_config(module)` 会自动加载  
> `config/api/{module}/{module}_api_path.yaml` 和 `{module}_api_params.yaml`。

---

## 6. 第四步：注册模块清理

框架在 pytest session 结束时统一执行所有注册的清理函数（主进程触发一次）。  
每个模块只需在 `conftest.py` 里注册一次即可。

`testcases/my_module/conftest.py`：

```python
"""my_module 模块统一清理注册。"""

import os
from data_factory.base import DataFactory
from testcases.comm.cleanup_registry import register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_my_module() -> None:
    db = None
    try:
        env = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        data_factory = DataFactory(env_name=env, project=project)
        env_config = data_factory.get_env_config() or {}
        db_config = env_config.get("database", {}).get("erp_db")

        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 my_module 清理")
            return

        db = DBManager(**db_config)

        # 按依赖关系倒序删除（子表先于父表）
        db.delete(table="my_child_table",  where="code like %s", params=["AT_%"])
        db.delete(table="my_parent_table", where="code like %s", params=["AT_%"])

        Loggers.info("✅ my_module 测试数据清理完成")
    except Exception as e:
        Loggers.error(f"❌ my_module 清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


# order 越小越先执行；建议：主数据 < 业务单据 < 财务凭证
register_cleanup("my_module_cleanup", _cleanup_my_module, order=300)
```

---

## 7. 第五步：编写第一条用例

`testcases/my_module/test_my_feature_management.py`：

```python
import allure
from testcases.my_module import MyModuleBaseTest
from utils.report_util import a, case_decorator


@allure.epic("我的业务模块")
@allure.feature("功能管理")
class TestMyFeatureManagement(MyModuleBaseTest):
    """功能管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.feature_id = None

        # 绑定常用基础数据（无参数 → 使用 DEFAULT_CACHE_MAPPINGS）
        cls.bind_cache_data()

        cls.logger.info("TestMyFeatureManagement 初始化完成")

    @classmethod
    def teardown_class(cls):
        """模块清理已由 conftest.py 中的 cleanup_registry 统一处理。"""
        super().teardown_class()

    # ------------------------------------------------------------------ #
    # 用例：创建
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="创建功能",
        description="验证创建功能接口正常返回并持久化数据",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["my_module", "创建"]
    )
    def test_save_feature(self):
        """测试创建功能"""
        try:
            code = self.mock_util.generate_unique_code(tag="FEAT")
            name = f"自动化功能_{self.mock_util.get_timestamp()}"

            set_dict = {
                "remark": "自动化测试提交",
                "code":   code,
                "name":   name,
                "status": "ENABLED",
            }
            response, extracted_id = self.standard_api_call(
                api_key="MY_MODULE-保存服务",
                set_dict=set_dict,
                store_id_as="feature",        # 自动写入 cls.feature_id
            )
            self.assert_util.assert_response_data(response)
            a.json(response, "创建响应")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ------------------------------------------------------------------ #
    # 用例：分页查询
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="分页查询功能列表",
        severity="normal",
        file_level_order=4,
        tags=["my_module", "查询"]
    )
    def test_query_feature_page(self):
        """测试分页查询"""
        try:
            if not self.feature_id:
                self.test_save_feature()

            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                },
                "fields": [{"name": "code", "type": "TEXT"}],
            }
            response, _ = self.standard_api_call(
                api_key="MY_MODULE-分页查询服务",
                set_dict=set_dict,
            )
            self.assert_util.assert_response_data(response)
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ------------------------------------------------------------------ #
    # 用例：删除
    # ------------------------------------------------------------------ #
    @case_decorator(
        story="功能管理",
        title="删除功能",
        severity="normal",
        file_level_order=16,
        tags=["my_module", "删除"]
    )
    def test_delete_feature(self):
        """测试删除功能"""
        try:
            if not self.feature_id:
                self.test_save_feature()

            response, _ = self.standard_api_call(
                api_key="MY_MODULE-删除服务",
                set_dict={"id": self.feature_id},
            )
            self.assert_util.assert_response_success(response)

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
```

---

## 8. 第六步：运行与查看报告

### 8.1 运行单个文件（快速验证）

```bash
pytest testcases/my_module/test_my_feature_management.py -v
```

### 8.2 运行整个模块

```bash
pytest testcases/my_module/ -v --alluredir=reports/allure-results
```

### 8.3 指定环境 + 项目

```bash
pytest testcases/my_module/ \
  --env=test \
  --project=project_alpha \
  --alluredir=reports/allure-results
```

### 8.4 仅跑冒烟测试

```bash
pytest testcases/my_module/ -m "smoke" -v
```

### 8.5 并行执行（需先确认用例无共享写状态）

```bash
pytest testcases/my_module/ -n auto --dist loadscope
```

### 8.6 生成 Allure 报告

```bash
allure serve reports/allure-results
```

---

## 9. 扩展数据源（可选）

当你的模块需要使用**框架默认不包含**的缓存数据（如采购缓存 `pur_cache_data`）时，  
在 `conftest.py` 顶层注册一次即可，无需修改基类。

```python
# testcases/my_module/conftest.py 顶部追加：
from testcases.comm.test_data_context import TestDataContext

# 注册新数据源：路径第一段 "pur_cache_data" → 测试类属性 cls.pur_cache_data
TestDataContext.register_source("pur_cache_data", "pur_cache_data")
```

随后在模块基类或用例的 `bind_cache_data` 中直接用路径引用：

```python
cls.bind_cache_data({
    **cls.DEFAULT_CACHE_MAPPINGS,   # 保留默认映射
    "pur_org_id": "pur_cache_data.pur_org_info.id",
})
```

同样地，如需扩展 `DEFAULT_CACHE_MAPPINGS`（增加默认绑定字段），在模块基类中整体替换：

```python
class MyModuleBaseTest(BaseTest):
    DEFAULT_CACHE_MAPPINGS = {
        **BaseTest.DEFAULT_CACHE_MAPPINGS,
        "my_special_id": "my_cache_data.my_info.id",
    }
```

---

## 10. 快速检查清单

完成开发后，过一遍以下检查：

```
基础配置
  [ ] config/env/{env}.yaml 中 URL、数据库地址已填写真实值
  [ ] config/env/ 下的密码文件已加入 .gitignore

API 配置
  [ ] {module}_api_path.yaml 中的 path 与系统实际 URL 一致
  [ ] {module}_api_params.yaml 中已去掉所有平台噪音字段
  [ ] api_key（中文名）已与用例中 standard_api_call 的 api_key 参数对齐

模块基类
  [ ] __init__.py 调用了 api_facade.load_api_config(module)
  [ ] 继承自 BaseTest 或其已有子类

清理注册
  [ ] conftest.py 中已调用 register_cleanup(...)
  [ ] 清理顺序：子表 before 父表
  [ ] 所有测试数据使用 AT_ 前缀

用例代码
  [ ] 使用 case_decorator 而非 @pytest.mark.run
  [ ] file_level_order 按 创建(1-3)/查询(4-6)/更新(7-9)/删除(16-18) 编排
  [ ] 使用 self.mock_util 生成随机数据，无硬编码
  [ ] 每个测试方法有 try-except，失败时 a.text(str(e), "失败原因")
  [ ] store_id_as 已正确设置，后续步骤使用 self.{name}_id
  [ ] 未调用 self.test_xxx()（依赖通过 if not self.xxx_id: 驱动）
```

---

## 11. 常见问题

### Q: `standard_api_call` 报 "未找到 API 配置"

检查：
1. `__init__.py` 的 `setup_class` 是否调用了 `cls.api_facade.load_api_config("my_module")`
2. `api_key` 拼写是否与 `*_api_path.yaml` 中的 key 完全一致（包括中文）

### Q: `bind_cache_data` 绑定结果全是 `None`

检查：
1. 环境配置 URL/账号是否正确（登录失败会导致 `init_data` 为空）
2. 缓存路径第一段（如 `currency_info`）是否已在 `TestDataContext._SOURCE_REGISTRY` 中注册
3. 自定义数据源是否调用了 `TestDataContext.register_source(key, attr)`

### Q: 清理数据没有被执行

检查：
1. `conftest.py` 是否在模块目录下（pytest 加载时会自动 import）
2. `register_cleanup` 是否在模块顶层调用（而非在函数内部）
3. 是否设置了 `ENABLE_PHYSICAL_DELETE=false`（此时 `db.delete` 不执行，只记录 warning）

### Q: 用例执行顺序不符合预期

确认所有用例使用的是 `file_level_order` 而非 `order`（`order` 是全局排序，会交叉文件执行）。

### Q: 并行执行时数据冲突

将业务流转用例（创建→更新→删除有状态依赖的）标记或放入 `serial_flow` 根目录，  
在 CI 中用 `--job-group=serial -n 1` 单独跑。

---

> 遇到更复杂的场景（异步任务、多门户登录、curl 转用例），参考：
> - `.cursor/rules/testcase_temp.mdc` — 完整代码模板
> - `.cursor/rules/coding_standards.mdc` — 规范速查
> - `@workflow workflow-trigger` + 描述需求 — 让 AI 直接生成用例

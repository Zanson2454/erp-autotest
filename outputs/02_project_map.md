# Project Map

## 1. Architecture Layers（整体分层结构）
1. **测试入口层**
- `pytest.ini` + `testcases/conftest.py`：控制执行参数、环境注入、Allure环境信息。

2. **业务测试层**
- `testcases/<domain>/.../test_*.py`：按 ERP 域编排测试（主数据、采购、销售、库存、财务等）。

3. **模块基类层**
- `testcases/<domain>/__init__.py` 中的 `*BaseTest`（如 `GenMdBaseTest`、`SlsBase`、`FinBaseTest`）：
  - 复用 `BaseTest` 初始化
  - 加载模块 API YAML
  - 注入模块缓存数据/默认业务字段

4. **框架核心层**
- `testcases/comm/base_test.py`：
  - 环境初始化（配置/登录/DB/工具）
  - 标准调用模板 `standard_api_call`
  - 公共参数处理入口

5. **能力工具层**
- `utils/`：HTTP、断言、日志、YAML、缓存、数据库、异步等待等。
- `data_factory/`：环境配置加载、SQL初始化、缓存生命周期。

6. **配置与数据层**
- `config/api/*`：接口路径与参数模板。
- `config/env/*`：环境与门户/数据库配置。
- `config/erp/*_init_sql.yaml`：初始化SQL定义。
- `testdata/cache/*`：初始化缓存产物。

## 2. Directory Structure（目录说明）
- `testcases/`: 用例主目录（按业务域拆分）。
- `testcases/comm/`: 公共基类与基础能力。
- `config/api/`: 各域 API path/params 模板。
- `config/env/`: 环境配置，支持项目目录模式。
- `config/erp/`: 初始化 SQL 配置。
- `data_factory/`: 配置加载、SQL执行、缓存写入。
- `utils/`: 横切工具库。
- `reports/`, `logs/`: 报告与日志输出。

## 3. Module Responsibilities（核心模块职责）
- `BaseTest`: 统一生命周期（配置、认证、DB、工具）、提供标准 API 调用框架。
- `GenMdBaseTest/SlsBase/FinBaseTest/...`: 绑定业务域 API 映射、加载域缓存、设置域上下文。
- `HttpUtil`: 请求发送、日志打印、异常抛转。
- `ParamUtil`: API映射获取、请求体裁剪与字段注入。
- `AssertHelper`: 通用响应断言、请求上下文补充。
- `DataFactory + CacheUtil`: 初始化数据构建、缓存复用和失效控制。

## 4. Request Lifecycle（请求调用链路）
典型真实链路有两条：

1. **标准模板链路（推荐）**
- `test_xxx` → `standard_api_call(api_key, set_dict, ...)`
- → `get_api_path(api_key)`（来自模块 `apis`）
- → `get_api_params(api_path)`（来自模块 `api_params`）
- → `ParamUtil.filter/set_request_params`
- → `HttpUtil.<method>(url, json/params)`
- → `AssertHelper`/业务断言

2. **手工调用链路（历史/定制）**
- `test_xxx` → `get_api_path/get_api_params`
- → 手工构造请求体
- → `self.http.post/get`
- → 手工断言

## 5. Fixture Dependency（fixture 依赖关系）
1. 全局
- `setup_test_environment`（session, autouse）：测试会话起止。
- `report_enhancer`（function）：报告增强对象。

2. 模块级
- `testcases/scm_del/conftest.py`：session autouse 清理。
- `testcases/scm_sls/conftest.py`：通过 session hook 在会话结束后执行集中清理。

3. 现实依赖
- 主要依赖并非 fixture 注入，而是 `setup_class` 中的类级初始化 + 类变量共享。

## 6. Config Flow（配置加载流程）
1. 启动参数进入 pytest：`--env/--project/--trantor_version`。
2. `testcases/conftest.py::pytest_configure` 写入环境变量。
3. `BaseTest.setup_class` 调 `ConfigManager.get_config`。
4. `ConfigManager` 委托 `DataFactory(env, project)` + `ConfigLoader`：
- 加载 `.env`（项目级优先）
- 读取 `config/env/...yaml`
- 执行 `${ENV_VAR}` 替换
5. 基类继续初始化登录、数据库、缓存。

## 7. Test Data Lifecycle（测试数据生命周期）
1. **基础主数据准备**
- `DataFactory.init_sql_cache` 读取 `config/erp/*_init_sql.yaml`
- 执行 SQL → 写入 `testdata/cache/*.json`

2. **测试执行中创建业务数据**
- API 创建单据/主数据
- 部分场景 DB 直查补充断言

3. **清理阶段**
- 模块 `conftest.py` session 结束清理（按时间、前缀、关键字）
- 个别测试类 `teardown_class` 追加清理

## 8. Assertion Layer（断言层设计）
1. 通用断言
- `assert_response_success`：校验 `success`。
- `assert_response_data`：提取 `data`。
- `assert_by_operator`：通用比较操作。

2. 业务断言
- 用例内对关键字段（id/status/金额）做二次校验。

3. 当前特征
- 断言基础能力完备，但业务语义（状态机完整性、上下游一致性）依赖各用例自觉补齐，标准化不足。

## 9. How to Add New Module（新增业务模块接入方式）
1. 新建模块目录
- 如：`testcases/erp_xxx/`，并创建 `__init__.py` + `test_*.py`。

2. 新建模块基类
- 继承 `BaseTest`（或已有域基类）。
- 在 `setup_class` 中：
- `super().setup_class()`
- 加载 `config/api/erp_xxx/xxx_api_path.yaml` 与 `xxx_api_params.yaml`
- 初始化模块缓存（如需）

3. 新增 API 配置
- `config/api/erp_xxx/xxx_api_path.yaml`：维护 `api_key -> path`。
- `config/api/erp_xxx/xxx_api_params.yaml`：维护 `path -> 请求模板`。

4. 编写用例（推荐模板）
- 优先使用 `standard_api_call`，减少手工参数与重复日志。
- 仅在复杂动态请求场景保留手工调用。

5. 数据与清理
- 如有固定主数据依赖，新增 `config/erp/xxx_init_sql.yaml` 并缓存。
- 在模块 `conftest.py` 或测试类回收逻辑中定义清理规则。

6. 验证
- 先跑单模块 smoke，再跑全量回归。

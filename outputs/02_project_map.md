# Architecture Layers
1. Case Layer
- 位置：`testcases/**/test_*.py`
- 职责：编排业务步骤、发起 `standard_api_call`、执行业务断言与 DB 校验。

2. Module Base Layer
- 位置：`testcases/<domain>/__init__.py`
- 典型：`GenMdBaseTest`、`SlsBase`
- 职责：继承 `BaseTest` 后加载域 API 配置、域缓存和上下文（角色、组织、主数据 ID）。

3. Framework Base Layer
- 位置：`testcases/comm/base_test.py`
- 职责：统一生命周期初始化、登录、数据库、请求模板调用和工具注入。

4. Data & Config Layer
- 位置：`data_factory/base.py`、`config/env`、`config/api`、`config/erp`
- 职责：环境配置加载、SQL 初始化、缓存读写、API path/params 元数据管理。

5. Utility Layer
- 位置：`utils/*`
- 核心：`HttpUtil`、`ParamUtil`、`AssertHelper`、`DBManager`、`CacheUtil`、`YamlUtil`。

# Directory Structure
- `testcases/comm`: 公共基类（`BaseTest`）与公共能力。
- `testcases/gen_md|scm_*|erp_*|sys_common`: 按业务域划分的测试套件。
- `config/api/<domain>`: 接口路径与请求模板配置。
- `config/env[/<project>]`: 环境与多项目配置。
- `config/erp/*.yaml`: 基础 SQL 初始化配置（主数据、采购、销售、财务等）。
- `data_factory`: 配置加载、SQL 执行、缓存初始化。
- `utils`: 请求、参数、断言、日志、缓存、数据库等通用工具。
- `outputs`: 工作流分析产物。

# Module Responsibilities
- `BaseTest`
  - 提供统一初始化模板方法。
  - 提供 `get_api_path/get_api_params/standard_api_call`。
  - 管理 `db/iam_db/http/session/assert_util` 等共享资源。

- `GenMdBaseTest`
  - 单门户登录（`TERP_PORTAL`）。
  - 加载 `gen_md` API 配置。
  - 加载 `md_init_cache` 并绑定基础上下文。

- `SlsBase`
  - admin + cust 门户上下文。
  - 合并 `scm_sls + reb + sys_common + acc + price + cond + del` 多域 API 配置。
  - 加载 `md_init_cache` 与 `sls_init_cache` 并绑定销售域运行字段。

- `DataFactory`
  - 通过 `ConfigLoader` 加载并替换环境变量。
  - 通过 `SQLExecutor` 执行 YAML 中 SQL。
  - 通过 `CacheUtil` 缓存数据并根据项目变化做清理。

# Request Lifecycle
真实调用路径（以标准模板为主）：
1. `test_xxx()` 调用 `self.standard_api_call(api_key, set_dict, ...)`
2. `BaseTest.standard_api_call` 根据 `api_key` 调 `get_api_path/get_api_params`
3. `ParamUtil` 处理模板参数（字段过滤、路径赋值、query 拼接）
4. `HttpUtil.request` 通过 `requests.Session.request` 发请求并记录请求/响应
5. 用例层调用 `assert_util` + 业务断言 + `db.query` 完成验证

示例链路：
- `testcases/scm_sls/so_03_approve/test_so_approve.py`
- `TestSalesOrderApproval.test_03_approve_sales_order`
- `standard_api_call("SLS-销售订单-审批同意服务")`
- `HttpUtil.request()`
- `AssertHelper.assert_response_success + DB so_status 校验`

# Fixture Dependency
1. 全局层：`testcases/conftest.py`
- 注入运行参数（环境/项目/版本）、Allure 环境信息、失败处理钩子。

2. 模块层：`testcases/<module>/conftest.py`
- `scm_sls`: `pytest_sessionfinish` 统一按时间窗清理。
- `scm_del`: session autouse fixture 清理指定 remark/code 前缀数据。

3. 类层：`BaseTest.setup_class`
- 通过模板方法初始化登录、DB、工具与缓存上下文；多数模块 Base 在此基础上二次绑定域数据。

# Config Flow
1. pytest 启动读取 `--env/--project/--trantor_version`
2. `testcases/conftest.py` 写入环境变量并加载环境配置
3. `BaseTest` 通过 `ConfigManager.get_config()` 调用 `DataFactory.get_env_config()`
4. `ConfigLoader` 依次加载 `project/.env -> config/env/.env -> 根目录 .env`
5. 读取 `config/env/{project}/{env}.yaml`（不存在则回退 `config/env/{env}.yaml`）
6. 递归替换 `${ENV_VAR}` 后缓存到 `ConfigManager` / `YamlUtil`

# Test Data Lifecycle
1. 初始化
- `BaseTestInitializer.initialize_base_data -> DataFactory.get_base_data("erp")`
- 读取 `config/erp/base_init_sql.yaml` 并缓存 `init_cache`

2. 模块补充
- 模块 Base 调 `load_sql_cache` 加载如 `md_init_cache`、`sls_init_cache`

3. 用例消费
- 从类上下文读取 `cust_id/org_id/mat_id` 等缓存字段，或动态构造数据

4. 清理
- 按模块策略在 session 结束清理测试产生数据（时间窗、前缀、remark 条件）

# Assertion Layer
1. 通用断言
- `AssertHelper.assert_response_success`
- `AssertHelper.assert_response_data`
- `AssertHelper.assert_by_operator`

2. 业务断言
- 由测试用例自行补充，常见方式为数据库状态校验（如 `so_status`、金额、行项目）。

3. 断言上下文
- `AssertHelper` 支持保存最近请求上下文，失败时输出 API key / URL / body / params。

# How to Add New Module
1. 新建模块目录 `testcases/<new_module>/` 并创建模块 Base 继承 `BaseTest`。
2. 在 `config/api/<new_module>/` 新增 `*_api_path.yaml` 与 `*_api_params.yaml`。
3. 在模块 Base `setup_class` 中执行：`super().setup_class()` + `load_api_configs/load_cache_data/bind_context`。
4. 若有初始化数据依赖，在 `config/erp/` 增加 SQL 配置并通过 `load_sql_cache` 加载缓存。
5. 在测试文件中优先使用 `standard_api_call`，然后补充业务断言和 DB 校验。
6. 如存在模块特有脏数据，增加模块 `conftest.py` 的 session 级清理逻辑。

# test_brand_management.py 执行调用链路（完整版）

目标命令示例：

```bash
pytest testcases/gen_md/mat/test_brand_management.py -v
```

本文只聚焦“该用例文件在本项目内的真实调用链路”，按执行阶段展开，并给出对应文件与函数位置，方便你快速定位代码。

---

## 1. Pytest 启动与全局钩子阶段

1. 读取 pytest 配置
- `pytest.ini`
  - `addopts` / `testpaths` / `python_files` / `python_classes` / `python_functions`

2. 加载全局 conftest，注册命令参数与环境
- `testcases/conftest.py:68` `pytest_addoption()`
  - 注册 `--env` / `--project` / `--trantor_version` / `--job-group` / `--fresh-cache` / `--md-precheck`
- `testcases/conftest.py:141` `pytest_configure()`
  - 读取 `--env` / `--project`
  - 写入环境变量 `TEST_ENV` / `TEST_PROJECT` / `TRANTOR_VERSION`
  - 调 `load_env_config()` 加载环境 YAML
  - 调 `create_allure_environment()` 生成 Allure 环境文件
- `testcases/conftest.py:238` `create_allure_environment()`

3. 会话开始
- `testcases/conftest.py:179` `pytest_sessionstart()`
  - 可选执行 `--fresh-cache` / `--md-precheck`
- `testcases/conftest.py:270` `setup_test_environment()`（`session, autouse=True`）

---

## 2. 目标文件收集与排序阶段

1. 发现并导入目标测试文件
- `testcases/gen_md/mat/test_brand_management.py`

2. 导入模块级 conftest 并注册清理器
- `testcases/gen_md/conftest.py:14` `_cleanup_gen_md()`（定义）
- `testcases/gen_md/conftest.py:197` `register_cleanup("gen_md_cleanup", _cleanup_gen_md, order=250)`
- 注册函数来自：`testcases/comm/cleanup_registry.py:30` `register_cleanup()`

3. 收集后的排序/打标
- `testcases/conftest.py:430` `pytest_collection_modifyitems()`
  - 读取 `case_decorator` 注入的 `_file_level_order`
  - 文件内按 `file_level_order` 排序
  - 可按 `--job-group` 筛选串/并行分组

4. 该文件用例顺序来源
- `utils/report_util.py:325` `case_decorator(..., file_level_order=...)`
- `testcases/gen_md/mat/test_brand_management.py` 中每个 `test_*` 使用该装饰器

---

## 3. 测试类初始化（setup_class）主链路

入口：
- `testcases/gen_md/mat/test_brand_management.py:13` `TestBrandManagement.setup_class()`
  - 调 `super().setup_class()` -> `GenMdBaseTest` 继承 `BaseTest`

主流程在：
- `testcases/comm/base_test.py:214` `BaseTest.setup_class()`
  - 依次调用：
    1) `:250` `_initialize_config()`
       - `testcases/comm/base_test_initializer.py:23` `initialize_environment()`
       - `testcases/comm/config_manager.py:29` `ConfigManager.get_config()`
    2) `:254` `_initialize_data()`
       - `testcases/comm/base_test_initializer.py:38` `initialize_base_data()`
       - `erp_data_factory.compat.base.DataFactory.get_base_data()`
    3) `:258` `_initialize_database()`
       - `testcases/comm/base_test_initializer.py:45` `initialize_database()` -> `DBManager`
    4) `:263` `_initialize_utilities()`
       - 初始化 `assert_util/mock_util/yaml_util/query_service/...`
    5) `:276` `_initialize_auth()`
       - 调 `LoginMixin._do_login()`
       - `testcases/comm/login_mixin.py:140` `_do_login()`
       - 当前 `GenMdBaseTest.LOGIN_STRATEGY="single"`，走 `:36` `_login_single_portal()`
       - `_login_single_portal()` 内调用 `LoginService.login()`：
         - `testcases/comm/login_service.py:193` `login()`
         - `:290` `_get_user_info()`
         - 构造 `HttpUtil`：`utils/request_util.py:21` `HttpUtil`
    6) `:284` `_initialize_module()`（声明式模块初始化）
       - `:310` `_load_module_apis()`
         - `:390` `load_module_api_configs()`
         - 读取：
           - `config/api/gen_md/md_api_path.yaml`
           - `config/api/gen_md/md_api_params.yaml`
       - `:321` `_load_module_caches()`
         - `:421` `load_sql_cache()` -> `DataFactory.init_sql_cache()` -> `CacheUtil.get()`
         - `GenMdBaseTest.SQL_CACHES`（`testcases/gen_md/__init__.py:16`）定义了 `md_init_sql` + `fin_init_sql`
       - `:337` `_bind_module_context()`
         - `:441` `bind_cache_data()` 绑定常用 id
         - `:406` `bind_module_user_context("GEN_MD")`
       - 子类增强：`testcases/gen_md/__init__.py:26` `GenMdBaseTest._bind_module_context()`
         - 额外绑定 `calenderId`
    7) `:352` `bind_context()`（兼容空实现，供子类链式调用）

然后回到目标类：
- `testcases/gen_md/mat/test_brand_management.py:18` `bind_context()`
  - 设置 `brandId/brandCode`

---

## 4. 单条测试方法执行链路（以 `test_save_brand` 为例）

1. 方法前置
- `testcases/comm/base_test.py:508` `setup_method()`
  - 清空 `TestDataContext` 运行时数据

2. 进入测试方法
- `testcases/gen_md/mat/test_brand_management.py:85` `test_save_brand()`
  - 生成测试数据（`self.mock_util.generate_unique_code`）
  - 调 `self.standard_api_call(...)`

3. 标准 API 调用入口
- `testcases/comm/base_test.py:596` `standard_api_call()`
  - 下沉到 `testcases/comm/api_call_service.py:15` `ApiCallService.execute()`

4. `ApiCallService.execute()` 内部关键步骤
- 解析 API 路径：
  - `BaseTest.get_api_path()` `testcases/comm/base_test.py:549`
  - `ApiClientFacade.resolve_api_path()` `testcases/comm/api_client_facade.py:13`
  - `ParamUtil.get_api_path()` `utils/param_util.py:189`
- 解析参数模板与 URL：
  - `BaseTest.get_api_params()` `testcases/comm/base_test.py:589`
  - `ApiClientFacade.resolve_api_params()` `testcases/comm/api_client_facade.py:31`
  - `ParamUtil.get_api_params()` `utils/param_util.py:204`
- 构造请求体：
  - `ParamUtil.filter_post_body_fields()` `utils/param_util.py:56`
  - `ParamUtil.set_request_params()` `utils/param_util.py:252`
  - `ParamUtil.sanitize_payload()` `utils/param_util.py:39`
- 发起 HTTP：
  - `self.http.post(...)` -> `HttpUtil.post()` `utils/request_util.py:69`
  - -> `HttpUtil.request()` `utils/request_util.py:81`
  - -> `requests.Session.request(...)`
- 响应处理：
  - 提取 `extracted_id`
  - 若传 `store_id_as="brand"`，写入运行时上下文与实例属性（`brand_id/brandId`）

5. 返回测试方法
- `response, extracted_id = standard_api_call(...)`
- 用例内断言（本文件里部分方法显式断言）

6. 方法后置
- `testcases/comm/base_test.py:515` `teardown_method()`

---

## 5. 该文件常见“分支调用”

1. 详情/修改用例可能先补建数据
- `testcases/gen_md/mat/test_brand_management.py:36` `_ensure_save_brand()`
  - 内部再次调用 `standard_api_call(api_key="GEN-品牌-保存服务")`

2. 删除用例使用独立创建数据
- `testcases/gen_md/mat/test_brand_management.py:58` `_create_brand_for_delete()`
  - 内部调用 `standard_api_call(api_key="GEN-品牌-保存服务")`
- `testcases/gen_md/mat/test_brand_management.py:259` `test_delete_brand()`
  - 再调 `standard_api_call(api_key="GEN-品牌-删除服务")`

---

## 6. 品牌接口在 YAML 中的落点

1. API Key -> Path（`md_api_path.yaml`）
- `GEN-品牌-查询分页服务` -> `GEN_BRAND_MD_QUERY_PAGE_ACTION_SERVICE`
- `GEN-品牌-查询详情服务` -> `GEN_BRAND_MD_QUERY_DETAIL_ACTION_SERVICE`
- `GEN-品牌-删除服务` -> `GEN_BRAND_MD_DELETE_ACTION_SERVICE`
- `GEN-品牌-保存服务` -> `GEN_BRAND_MD_SAVE_ACTION_SERVICE`

2. Path -> 参数模板（`md_api_params.yaml`）
- 对应条目在 `api_params` 下，模板核心均为 `params.request`
- `standard_api_call` 默认将 `set_dict` 写入 `params.request`

---

## 7. 执行结束链路（类级 + 会话级）

1. 类结束
- `testcases/gen_md/mat/test_brand_management.py` `teardown_class()`
  - 调 `super().teardown_class()`
- `testcases/comm/base_test.py:481` `teardown_class()`
  - 关闭 `db` / `iam_db`

2. 会话结束统一清理
- `testcases/conftest.py:231` `pytest_sessionfinish()`
  - 调 `run_cleanups(Loggers)`
- `testcases/comm/cleanup_registry.py:38` `run_cleanups()`
  - 执行已注册清理函数（含 `gen_md_cleanup`）
- `testcases/gen_md/conftest.py:14` `_cleanup_gen_md()`

说明：本仓库当前行为下，`--collect-only` 也会触发 `pytest_sessionfinish`，所以会执行统一清理。

---

## 8. 一张总链路图（从命令到请求）

```text
pytest testcases/gen_md/mat/test_brand_management.py -v
  -> pytest.ini
  -> testcases/conftest.py::pytest_addoption/pytest_configure/pytest_sessionstart
  -> collect testcases/gen_md/mat/test_brand_management.py
     -> load testcases/gen_md/conftest.py (register_cleanup)
     -> testcases/conftest.py::pytest_collection_modifyitems (file_level_order 排序)
  -> TestBrandManagement.setup_class
     -> BaseTest.setup_class
        -> _initialize_config/_initialize_data/_initialize_database/_initialize_utilities
        -> _initialize_auth -> LoginMixin._do_login -> LoginService.login -> HttpUtil
        -> _initialize_module
           -> load_module_api_configs (md_api_path.yaml + md_api_params.yaml)
           -> load_sql_cache (md/fin)
           -> bind_cache_data + bind_module_user_context
        -> GenMdBaseTest._bind_module_context (calenderId)
  -> BaseTest.setup_method
  -> TestBrandManagement.test_xxx
     -> BaseTest.standard_api_call
        -> ApiCallService.execute
           -> get_api_path/get_api_params
           -> ParamUtil.filter/set/sanitize
           -> HttpUtil.request -> requests.Session.request
           -> extract_id/store_id_as
  -> BaseTest.teardown_method
  -> TestBrandManagement.teardown_class -> BaseTest.teardown_class
  -> testcases/conftest.py::pytest_sessionfinish -> cleanup_registry.run_cleanups -> gen_md cleanup
```

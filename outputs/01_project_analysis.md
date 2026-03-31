# Summary
本轮扫描（2026-03-31）确认：框架已完成第二轮拆分，`ApiCallService`、`ApiClientFacade`、`TestDataContext`、`AuthContext` 四个组件均已落地并被 `BaseTest` 接入。`bind_cache_data()` 便捷绑定与 `__init_subclass__` 强制 `super()` 保护已上线。`gen_md` 模块已迁移到注册式全局清理（230 行完整覆盖）。整体处于"组件化提速阶段"，但 `BaseTest` 仍是 1179 行的高复杂度入口，清理模式收敛尚未完成。

# Confirmed Facts
- `base_test.py` 1179 行，包含 `ConfigManager`、`SessionManager`、`LoginService`、`BaseTestInitializer`、`BaseTest` 五个类。
- 已提取并接入四个组件：`AuthContext`（认证VO）、`ApiClientFacade`（路径解析）、`ApiCallService`（API调用执行层 182 行）、`TestDataContext`（缓存路径解析）。
- `BaseTest.__init_subclass__` 已用装饰器强制兜底 `teardown_class` 必调 `super()`，防止资源泄漏。
- `bind_cache_data()` 支持默认映射（14 个常用字段）和自定义路径，一行绑定常用依赖数据。
- 新增模块通用 helper：`module_login_single_portal()`、`module_login_multi_portal()`、`module_login_admin_with_cust_headers()`、`load_module_api_configs()`、`bind_module_user_context()`、`bind_mock_util_singleton()`、`load_sql_cache()`。
- `gen_md/conftest.py` 已迁移为注册式清理（230 行，覆盖 30+ 张表，含动态列探测与表存在性判断）。
- `cleanup_registry` 支持 `reset_run_state()` 以支持同进程重复执行场景。
- `SessionManager` 支持多进程会话隔离（按 PID 独立创建）。
- 已确认模块数：28 个 `__init__.py`（gen_md、erp_fin、scm_sls、scm_pur、scm_inv 等）。
- conftest 分布：5 处（`testcases/`、`gen_md/`、`erp_fin/`、`scm_sls/`、`scm_del/`）。

# Inferred Points
- `ApiCallService.execute` 仍持有 `test_obj` 引用（传入并调用 `test_obj.http`、`test_obj.get_api_path` 等），依赖倒置尚未完成，`ApiCallService` 目前更接近"下沉包装"而非独立服务。
- `store_id_as` 使用 `setattr(test_obj.__class__, ...)` 写类属性，在并发执行时存在竞争风险（假设目前主要串行使用）。
- `ApiClientFacade` 的近似匹配逻辑（`matched_keys` 排序取 best_key）在大型 API 字典中可能产生非预期命中，已有 warning 日志。

# Unknowns
- `erp_fin`、`scm_pur`、`scm_inv` 等高频模块的 conftest 是否已迁移为注册式清理，未逐一确认。
- `bind_cache_data` 的路径路由仅硬编码了 6 个 `init_data` key 和 3 个 `md_cache_data` key，其他模块字段是否已覆盖未知。
- `cleanup_registry.reset_run_state()` 的实际调用场景（测试用还是生产用）未确认。

# Risks
- P0：`ApiCallService` 仍对 `test_obj` 强依赖，耦合测试对象，难以独立单测或复用。
- P0：`store_id_as` 写类属性在 `-n auto` 并发场景下存在状态竞争。
- P1：`gen_md` 以外模块的清理注册覆盖率未知，仍存在并发清理冲突风险。
- P1：`BaseTest` 1179 行，变更回归半径仍大，任何基类修改需全量回归。
- P2：`ApiClientFacade` 近似匹配可能引发 api_key 偷跑，建议补精确匹配 fallback 的单测。

# Top 5 Issues
1. `ApiCallService` 通过 `test_obj` 持有测试上下文，依赖倒置不彻底，阻碍独立测试与复用。
2. `store_id_as` 写类属性，并发不安全。
3. 清理注册覆盖率仅确认 `gen_md`、`scm_sls`、`scm_del` 三个模块，25 个模块状态未知。
4. `BaseTest` 规模仍大（1179 行），多职责，变更成本高。
5. `bind_cache_data` 路径路由硬编码源映射，新增数据源需改基类代码。

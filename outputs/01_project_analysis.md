# Summary
该项目是一个配置驱动的 `pytest` API 自动化框架，核心调用链是 `test -> 模块Base -> BaseTest.standard_api_call -> ParamUtil -> HttpUtil -> requests.Session`，并叠加了数据库校验与缓存化初始化数据。框架具备多环境/多项目配置、多门户登录、并行执行和模块化测试目录，已能覆盖 ERP 主数据、交易单据、审批、库存与财务等大量 API 场景。但在“断言业务语义统一性、跨模块流程编排、清理策略一致性、缓存隔离粒度”上仍有可维护性风险。

# Confirmed Facts
1. 测试入口集中在 `testcases/`，`pytest.ini` 启用了 `-n auto --dist loadscope` 并行和 Allure 输出。
2. 全局运行参数在 `testcases/conftest.py` 统一注册：`--env`、`--project`、`--trantor_version`，并写入环境变量 `TEST_ENV/TEST_PROJECT/TRANTOR_VERSION`。
3. 框架基类为 `testcases/comm/base_test.py::BaseTest`，初始化顺序是：配置 -> 基础数据 -> 登录认证 -> DB 连接 -> 工具类。
4. 配置读取通过 `ConfigManager + DataFactory + ConfigLoader` 组合完成，支持 `config/env/{project}/{env}.yaml` 与默认回退。
5. 登录由 `LoginService` 统一处理，支持两种模式：`cookie` 直登 和 账号密码登录（`/iam/api/v1/user/login/account`）。
6. API 调用统一走 `BaseTest.standard_api_call`，支持 GET/POST/PUT/DELETE/PATCH、跨模块 API、参数路径自定义。
7. HTTP 封装在 `utils/request_util.py::HttpUtil`，底层是 `requests.Session.request`，记录请求/响应并在 HTTP 错误时抛异常。
8. 请求模板来自 `config/api/**/_api_path.yaml` 与 `_api_params.yaml`；参数组装通过 `ParamUtil.get_api_path/get_api_params/set_request_params`。
9. 初始化数据由 `data_factory/base.py` 执行 SQL + `CacheUtil` 缓存，默认测试环境缓存过期 5 分钟。
10. 断言层核心是 `AssertHelper.assert_response_success/assert_response_data/assert_by_operator`，并支持失败时输出最近请求上下文。
11. 模块基类明显存在二级分层：例如 `GenMdBaseTest`（单门户）与 `SlsBase`（管理门户+客户门户，且合并多个域 API 配置）。
12. ERP 流程用例已存在，例如 `testcases/scm_sls/so_03_approve/test_so_approve.py` 包含“启用规则 -> 创建提交 -> 审批 -> DB 状态校验”的链路。
13. 模块清理策略并不完全统一：`scm_sls` 使用 `pytest_sessionfinish` 按时间窗清理，`scm_del` 使用 session fixture 且 `DBManager()` 无显式环境参数。

# Inferred Points
1. 推断：框架优势是“覆盖广 + 接口接入快”，因为配置驱动+标准模板降低了新增 API 用例成本。
2. 推断：复杂流程复用仍偏“测试类手工编排”，缺少跨模块可复用流程 DSL/步骤库，长期会增加回归维护成本。
3. 推断：断言默认从 `success` 起步，若业务断言不强制，容易出现“接口成功但业务状态错误”的漏检。
4. 推断：缓存 key（如 `md_init_cache`）在多项目并跑场景仍有潜在串扰，需要更细粒度命名和失效治理。
5. 推断：虽然有并行能力，但 DB 依赖和模块级清理差异会使并发稳定性随用例规模增长而下降。

# Unknowns
1. 未确认 CI 中真实执行矩阵（按模块/优先级/环境）及失败阻断策略。
2. 未确认各业务域的稳定覆盖率基线和近周期 flaky 率（仓库有统计脚本但缺少现成趋势结果）。
3. 未确认跨模块端到端回归集是否有固定编排（如采购->库存->财务全链路）。
4. 未确认权限矩阵（供应商/运营/经销商）是否已形成稳定账号池与环境一致性策略。

# Risks
1. 业务断言不统一：回归中可能遗漏状态机、金额、库存一致性问题。
2. 流程编排分散：关键链路修改时影响面难评估，回归成本上升。
3. 清理策略差异：并行和重跑时更容易出现脏数据与偶发失败。
4. 环境依赖偏重：对真实 DB 与门户依赖较强，环境抖动会直接影响测试稳定性。
5. 缓存隔离边界不够显式：多项目/多环境切换场景可能出现缓存命中偏差。

# Top 5 Issues
1. P0：断言体系缺少模块级“业务语义必检项”基线（不仅是 `success=true`）。
2. P1：跨模块 ERP 链路缺少统一流程编排层，流程复用靠手工拼装。
3. P1：模块级测试数据清理策略不一致，影响并行稳定性与可预测性。
4. P1：模块 Base（尤其销售域）承担过多初始化与上下文绑定职责，复杂度偏高。
5. P2：缓存 key/失效策略对多项目并行场景的隔离约束仍不够强。

# Summary（总结）
该项目是一个以 `pytest + requests + Allure` 为核心的 ERP API 自动化框架，已形成“模块基类 + YAML API 配置 + SQL 初始化缓存 + DB 校验 + 报告增强”的基础能力。整体可支撑大量接口回归与部分业务流测试（特别是单据 CRUD、提交、审批、过账、状态轮询）。

但框架在“统一抽象深度”和“复杂 ERP 全链路编排”上存在明显分层不均：`standard_api_call` 虽已大量应用（651处），但直接 `self.http.post/get/...` 调用仍更多（942处）；模块基类重复加载逻辑、清理策略分散、断言深度偏浅，导致可维护性成本持续上升。

# Confirmed Facts（已确认信息）
1. 项目结构与规模
- 用例主目录是 `testcases/`，按 ERP 业务域拆分（如 `gen_md`、`scm_sls`、`erp_fin`、`scm_inv` 等）。
- 模块用例数量（按 `test_*.py` 统计）：`gen_md:47`、`erp_fin:39`、`sys_common:26`、`scm_inv:22`、`scm_sls:21`、`erp_prd:11` 等。
- API 配置以 YAML 管理，按模块放置于 `config/api/*/*_api_path.yaml` 与 `*_api_params.yaml`。

2. pytest 用例组织方式
- 全局配置在 `pytest.ini`：启用并行（`-n auto` + `--dist loadscope`）、Allure 输出、默认 `testpaths=testcases`。
- 存在大量 `setup_class`/`teardown_class` 初始化模式，依赖类变量在同类用例间共享状态。
- 运行顺序依赖 `pytest.mark.run(order=...)` 与测试内前置调用（如 `if not xxx: self.test_xxx()`）。

3. fixture 体系
- 全局 fixture 主要在 `testcases/conftest.py`：`session` 级环境初始化、`function` 级报告增强器。
- 业务模块 fixture 较少，更多通过模块 `conftest.py` 的 session 结束清理（如 `scm_sls`、`scm_del`）。

4. 请求/Client 抽象
- 存在统一 HTTP 封装 `HttpUtil`（URL拼接、请求日志、Decimal转换、异常处理）。
- 存在统一调用模板 `BaseTest.standard_api_call`（路径解析、参数过滤、请求上下文、ID提取）。
- 但直接 `self.http.post/get/...` 仍广泛存在，形成双轨调用风格。

5. 配置与环境管理
- 通过 `--env/--project/--trantor_version` 参数与 `config/env/*.yaml` 管理环境。
- `DataFactory/ConfigLoader` 支持 `.env` + YAML 变量替换、项目级配置目录。
- 缓存使用 `testdata/cache/*.json`，默认按环境设置过期策略（测试环境短周期）。

6. 鉴权机制
- `LoginService` 支持两种模式：配置 `cookie` 直连，或账号密码登录 IAM 后复用 session。
- 多模块基类会再次登录并覆盖 `cls.http`，通常使用管理门户会话。

7. 测试数据策略
- 依赖 SQL 初始化缓存（如 `md_init_cache`、`fin_init_cache`、`sls_init_cache`）。
- 依赖 DB 直查/直删进行数据准备与回收（大量 `DBManager.query/delete`）。
- 通过编码前缀（如 `AT_`）和 session 结束清理来控制污染。

8. 断言层
- `AssertHelper` 支持 success 断言、通用运算符断言、请求上下文回填。
- 大量用例核心判断仍集中在 `success/code/msg` 与少量业务字段校验。

9. 日志与报告
- `loguru` 文件+控制台双通道，日志内容较全。
- Allure 通过装饰器与 `report_util` 增强步骤、请求/响应附加。

10. ERP 复杂链路支撑
- 已覆盖部分单据生命周期片段（保存→提交→过账→状态查询）。
- 已有异步轮询工具与状态等待（如 `AsyncWaitUtil`）。
- 但跨模块全链路（主数据→交易→库存→财务→结算→对账）编排能力不统一。

11. 代码层面可见问题
- 工作流文件 `erp_full_flow.yaml` 的 `prompt_file` 路径写为 `erp-tasks`，实际目录为 `erp_tasks`，存在路径不一致。

# Inferred Points（推断信息）
1. 【推断】框架经历了“从手写直调到统一模板”的迁移期，尚未完成收敛，因此出现 `standard_api_call` 与手写请求并存。
2. 【推断】模块间复制式 `setup_class` 演进会继续放大维护负担（新环境字段、新认证策略时需多处同步修改）。
3. 【推断】当前更偏“接口回归集合”，而非“可编排的 ERP 业务流测试平台”；复杂端到端链路的可重用组装层尚弱。
4. 【推断】并行执行与共享数据库并存时，依赖“时间窗口/前缀删除”的清理模式可能造成偶发相互影响。

# Unknowns（待确认信息）
1. 当前 CI 中实际启用的测试子集（smoke/regression/p0）及耗时分布。
2. 各业务域是否存在强制的数据隔离策略（按租户/组织/测试账号硬隔离）。
3. 异步任务场景下的失败重试与幂等补偿策略是否统一。
4. 多门户（admin/cust）在同一用例中的切换规范是否已文档化。
5. 是否已有“端到端业务链路”标准模板（比如销售→交货→开票→应收）。

# Risks（风险点）
1. 调用抽象不统一：同类接口在不同用例采用不同调用模式，回归定位与维护成本高。
2. 断言深度不足：大量断言停留在成功标记，可能放过业务规则回归（金额、状态机、凭证副作用）。
3. 测试数据回收分散：模块各自清理且依赖 DB 直删，易出现漏清理、误清理、并行冲突。
4. 配置与基类重复：多模块基类重复实现登录和配置加载，修改认证/环境策略时易不一致。
5. 工作流路径错误：自动化流程触发时可能直接失败，影响流程可执行性。

# Top 5 Issues（最优先问题）
1. **P0: 调用链标准不统一（`standard_api_call` 与直调并行）**
- 影响：模板能力难沉淀，异常处理/日志/断言上下文无法全局一致。

2. **P0: 断言层业务语义不足**
- 影响：ERP 关键风险（状态跃迁、金额平衡、上下游联动）可能“假通过”。

3. **P1: 测试数据生命周期治理薄弱**
- 影响：环境污染和并行串扰导致结果不稳定，回归可信度下降。

4. **P1: 模块基类重复与耦合过高**
- 影响：扩展新模块或调整鉴权策略时改动面大、回归风险高。

5. **P1: 工作流配置与目录不一致（`erp-tasks` vs `erp_tasks`）**
- 影响：流程编排可用性受损，降低自动化分析链路稳定性。

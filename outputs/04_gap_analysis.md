# Issues List

## 1) 业务断言基线不足，默认断言深度偏浅
- Evidence：`AssertHelper` 的统一入口以 `assert_response_success` 为主，复杂业务校验主要分散在各测试用例手写。
- Impact：会出现“接口成功但业务状态错误”漏检，尤其是单据生命周期和跨模块联动场景。
- Priority：P0
- Short-term Fix：
  - 定义最小业务断言模板（状态字段 + 关键业务字段 + DB 关键表校验）。
  - 在高频链路（销售订单、库存移动、财务单据）先强制落地。
- Mid-term Refactor Plan：
  - 建立领域断言库（Order/Inventory/Finance）。
  - 将重复断言从测试文件上收敛到模块 helper。

## 2) ERP 复杂流程编排缺少统一流程层
- Evidence：审批流等场景在用例文件中手工串步骤，跨模块流程没有统一流程对象或步骤库。
- Impact：新增链路或流程变更时改动分散、回归维护成本高。
- Priority：P1
- Short-term Fix：
  - 抽取 2-3 条高频流程模板（创建->提交->审批->生效/关闭）。
  - 模板入参标准化（角色、组织、关键主数据、预期状态）。
- Mid-term Refactor Plan：
  - 建立“流程步骤库 + 场景参数化”机制，支持跨模块复用。
  - 为流程模板配套统一日志与断言挂钩。

## 3) 模块 Base 职责偏重，域初始化耦合较高
- Evidence：`SlsBase` 同时负责多门户上下文、跨域 API 合并、缓存加载、大量字段绑定。
- Impact：理解成本高，任一初始化细节变动都可能影响大范围测试。
- Priority：P1
- Short-term Fix：
  - 将 `setup_class` 显式拆成 `load_api_configs/load_cache_data/bind_context` 的稳定协议（已有雏形，需统一化）。
  - 对字段绑定采用映射表，减少硬编码散落。
- Mid-term Refactor Plan：
  - 模块 Base 只保留“编排”，把配置、缓存、上下文绑定下沉到独立组件。

## 4) 模块级数据清理策略不一致
- Evidence：`scm_sls` 使用 `pytest_sessionfinish` 时间窗清理，`scm_del` 采用 session fixture + 默认 `DBManager()`。
- Impact：并行执行和重跑时，脏数据和偶发失败排查成本高。
- Priority：P1
- Short-term Fix：
  - 统一清理入口策略（推荐 session finish/统一 hook）。
  - 明确清理条件标准（时间窗 + 前缀 + remark），避免模块自定义漂移。
- Mid-term Refactor Plan：
  - 建立清理规则注册中心，由模块声明规则，框架统一执行。

## 5) 缓存隔离粒度仍偏粗
- Evidence：`md_init_cache`、`init_cache` 等 key 在多项目共存场景下主要靠项目切换检测+过期机制治理。
- Impact：项目并行或快速切换场景可能出现缓存命中偏差。
- Priority：P2
- Short-term Fix：
  - 缓存 key 增加 `project/env/module` 维度。
  - 在启动阶段打印并校验缓存命名上下文。
- Mid-term Refactor Plan：
  - 制定缓存命名与失效策略文档化规范，加入自检。

# Impact
1. 质量影响：P0 问题直接影响缺陷检出率和线上风险暴露。
2. 效率影响：P1 问题使新增模块和流程回归的边际成本持续上升。
3. 稳定性影响：清理和缓存问题在并行和长周期执行中会被放大。

# Priority
1. P0：业务断言基线
2. P1：流程编排标准化
3. P1：清理策略统一
4. P1：模块 Base 解耦
5. P2：缓存隔离增强

# Short-term Fix
1. 为高频链路定义“必须断言字段 + 必查 DB 表”清单。
2. 抽取审批类流程模板并在销售/财务场景试点。
3. 统一模块清理入口与条件模板。
4. 对重型模块 Base 做小步拆分，保持外部调用兼容。
5. 缓存 key 加环境与项目维度。

# Mid-term Refactor Plan
1. 建立领域断言库并逐步替换散落断言。
2. 建立跨模块流程步骤库和参数化场景库。
3. 清理机制注册化，减少模块自定义脚本分叉。
4. 建立缓存治理规范和启动自检机制。

# Not Recommended Now
1. 不建议立即全面重写框架
- 原因：现有框架已承载大量模块与用例，重写风险和迁移成本过高。

2. 不建议一次性改造全部历史用例
- 原因：改造面过大，建议从 P0/P1 高频业务域增量推进。

3. 不建议先引入重型抽象（复杂 DSL/过度分层）
- 原因：当前核心痛点是约定缺失和复用不足，应先标准化再抽象化。

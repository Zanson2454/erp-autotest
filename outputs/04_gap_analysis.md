# Issues List（问题清单）

## 1. 调用层双轨并存，标准化不足
- 现状：`standard_api_call` 使用 651 处，但直接 `self.http.post/get/...` 仍有 942 处。
- 影响：请求构造、日志、异常、上下文断言策略不一致，维护成本持续升高。
- Priority：P0
- Short-term Fix：
  - 新增/改造用例默认使用 `standard_api_call`。
  - 对高频模块（`gen_md`、`erp_fin`、`scm_sls`）先做增量收敛。
- Mid-term Refactor Plan：
  - 形成统一 `ApiExecutor` 层，显式支持 POST/GET/DELETE、query 参数、幂等键。
  - 为历史手写调用建立迁移清单与覆盖率指标。

## 2. 断言停留在 success/code，业务语义断言不足
- 现状：通用断言完备，但大量用例仍以 `success` 为主，少量字段校验。
- 影响：状态机、金额平衡、上下游副作用回归可能被漏检。
- Priority：P0
- Short-term Fix：
  - 增加“关键业务断言模板”（状态跃迁、金额平衡、来源-目标单据关联）。
  - 对 AP/AR/SO/DN 等核心链路用例先补断言。
- Mid-term Refactor Plan：
  - 建立领域断言库（DocStateAssert、AmountAssert、RelationAssert）。
  - 将断言从用例内分散实现上收至可复用组件。

## 3. 数据治理分散，清理策略不统一
- 现状：全局+模块 conftest + 类 teardown 并存，清理条件依赖前缀/时间窗口/备注关键字。
- 影响：并行执行下易互相影响，环境污染导致“偶发失败/假失败”。
- Priority：P1
- Short-term Fix：
  - 统一测试数据命名约定（前缀+run_id）。
  - 清理 SQL 改为按 run_id 精确回收，减少时间窗误删。
- Mid-term Refactor Plan：
  - 设计 `TestDataManager`（创建登记、引用追踪、统一回收）。
  - 建立跨模块清理策略中心，减少模块内重复脚本。

## 4. 模块基类重复初始化逻辑，扩展成本高
- 现状：多个模块基类重复登录、YAML加载、缓存初始化流程。
- 影响：鉴权策略或配置结构变化时，修改点分散且易漏改。
- Priority：P1
- Short-term Fix：
  - 抽出共享初始化步骤到 `BaseDomainTest`（登录、API加载、缓存加载模板化）。
- Mid-term Refactor Plan：
  - 形成“域配置声明式注册”（声明 API 文件、缓存键、portal 类型即可接入）。
  - 降低新增模块样板代码比例。

## 5. ERP复杂业务链路支持不均衡
- 现状：已具备局部流程（保存/提交/过账/查询）能力，但跨模块端到端链路未形成统一编排规范。
- 影响：难以稳定覆盖“主数据→交易→库存/财务→结算”完整回归。
- Priority：P1
- Short-term Fix：
  - 先固化 2~3 条黄金链路（销售链、采购链、应收应付链）。
- Mid-term Refactor Plan：
  - 引入流程编排层（Flow DSL 或流程对象），统一前置、步骤、回收。

## 6. workflow 配置存在路径不一致
- 现状：`.codex/workflows/erp_full_flow.yaml` 使用 `../skills/erp-tasks/...`，实际目录是 `../skills/erp_tasks/...`。
- 影响：工作流自动执行可能直接失败。
- Priority：P1
- Short-term Fix：
  - 修正 workflow 路径为 `erp_tasks`。
- Mid-term Refactor Plan：
  - 增加 workflow 静态校验（启动前检查 prompt 文件存在性）。

## 7. Automation Readiness（自动生成用例友好度）不足
- 现状：API 元数据齐全（path/params 模板较完整），但模板风格和断言策略不统一。
- 影响：自动生成用例后需要大量人工修整，难形成稳定生成-执行闭环。
- Priority：P2
- Short-term Fix：
  - 统一 API key 命名规则与字段注释规范。
  - 在模板中标注必填字段、默认值和业务前置。
- Mid-term Refactor Plan：
  - 建立“生成友好测试模板”：输入 API key + 场景类型，自动生成调用+断言骨架。

# Impact（影响范围）
1. 回归稳定性
- 并行与数据清理策略耦合，导致不稳定失败概率上升。

2. 维护效率
- 模块重复逻辑和双轨调用模式使改动扩散，排查时间增加。

3. 质量保障深度
- 断言语义不足时，复杂 ERP 回归缺陷可能无法提前暴露。

4. 扩展能力
- 新模块接入与自动化生成能力受限，框架规模化演进速度下降。

# Priority（P0/P1/P2）
- P0
1. 调用层双轨并存
2. 业务断言深度不足

- P1
1. 数据治理分散
2. 模块基类重复初始化
3. 复杂链路编排不统一
4. workflow 路径不一致

- P2
1. 自动生成用例友好度不足

# Short-term Fix（短期优化）
1. 以模块为单位推进 `standard_api_call` 收敛（先 `gen_md/erp_fin/scm_sls`）。
2. 输出统一断言清单并在核心链路补齐（状态机、金额、关联）。
3. 统一 run_id 数据标识与精确清理规则。
4. 修复 workflow 路径问题并加入执行前自检。

# Mid-term Refactor Plan（中期重构方案）
1. 构建统一 API 执行层 + 领域断言层。
2. 构建声明式域基类注册机制，减少重复 setup 样板。
3. 构建测试数据管理中心（创建/引用/回收可追踪）。
4. 建立 ERP 黄金链路编排框架，形成持续回归基线。
5. 建立生成式用例模板规范，提升自动化产出可用性。

# Not Recommended Now（暂不建议处理项 + 原因）
1. 全量一次性迁移所有历史用例到统一模板
- 原因：改动面过大，短期回归风险高；应按模块分批迁移。

2. 立即引入全新测试框架替换 pytest 体系
- 原因：当前体系已承载大量资产，迁移成本远高于渐进式治理收益。

3. 大规模目录重构（按分层重排所有测试目录）
- 原因：会破坏现有执行与引用路径，收益短期不可验证。

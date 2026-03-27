# ERP API TEST DOMAIN MAP

## 1. Master Data（主数据）
- Test Goal
验证主数据（组织、物料、客户、供应商、税码、计量单位等）CRUD、启停用、唯一性与下游可引用性。
- Preconditions
初始化缓存可用（`md_init_cache`），具备主数据维护权限，编码规则可用。
- Key Assertions
`success=true`、返回 `id/code`；启用状态正确；被下游单据引用时字段完整且可回查。
- Risk Points
主数据编码冲突、软删除/禁用后仍可引用、跨组织主数据串用。
- Test Level
`smoke`, `regression`, `exception`, `permission`

## 2. Document APIs（单据类）
- Test Goal
覆盖单据头行保存、查询、修改、删除、提交、取消提交等基础事务能力。
- Preconditions
主数据齐备（组织/伙伴/物料/价格/税）；单据类型与流程配置已启用。
- Key Assertions
创建后 `id` 存在；关键金额/数量字段回读一致；版本号与状态字段符合预期。
- Risk Points
头行金额不平、字段默认值漂移、模板参数缺失导致接口“成功但脏数据”。
- Test Level
`smoke`, `regression`, `flow`

## 3. State Transitions（状态流转）
- Test Goal
验证单据生命周期：**创建 → 审批/提交 → 执行/过账 → 关闭/取消关闭**。
- Preconditions
流程规则、审批规则、异步执行器可用；前态单据真实存在。
- Key Assertions
仅允许合法状态跃迁；非法跃迁返回业务错误；异步状态最终落到 `SUCCEEDED/DONE`。
- Risk Points
异步状态未收敛、重复提交导致并发脏写、回滚状态与账务状态不一致。
- Test Level
`flow`, `regression`, `exception`

## 4. Query / Report（查询/报表）
- Test Goal
验证分页、过滤、统计、详情查询与业务对象一致性。
- Preconditions
测试数据已创建且可检索；索引字段可用；时间窗口正确。
- Key Assertions
分页总数正确、条件过滤命中准确、详情与列表核心字段一致。
- Risk Points
查询条件兼容性差、分页重复/漏数、报表与事务表不一致。
- Test Level
`smoke`, `regression`

## 5. Permission / Isolation（权限与数据隔离）
- Test Goal
验证多角色、多组织、门户间访问边界（供应商/运营/经销商）。
- Preconditions
至少两类角色账号与组织数据准备；门户配置可切换（`TERP_PORTAL/TERP_CUST_PC`）。
- Key Assertions
无权接口被拒绝；同角色仅可见授权组织数据；跨租户数据不可见。
- Risk Points
共享 session/header 导致越权；测试环境“超管账号”掩盖真实权限问题。
- Test Level
`permission`, `regression`

## 6. Idempotency（幂等与重复提交）
- Test Goal
验证重复请求不会重复落库或重复推进流程，特别是提交/过账/异步触发类接口。
- Preconditions
可重复调用同一业务键（单据号、幂等键、来源行号等）。
- Key Assertions
重复调用返回幂等结果；业务实体无重复；状态不被异常推进。
- Risk Points
网络抖动重试导致重复单据、异步任务重复消费。
- Test Level
`exception`, `flow`, `regression`

## 7. Multi-role Workflow（多角色协同）
- Test Goal
验证供应商/运营/经销商协同链路中的责任边界与状态交接。
- Preconditions
多角色账号准备完成；上下游单据关系可建立（如 SO→DN→IV/AR，PO→GR→PI/AP）。
- Key Assertions
角色动作受限且可追溯；交接节点状态一致；来源与目标单据关联正确。
- Risk Points
角色切换后上下文污染、来源单据状态未同步、协同环节断链。
- Test Level
`flow`, `permission`, `regression`

## 8. Upstream / Downstream Dependency（上下游依赖）
- Test Goal
验证主数据/库存/价格/税务等依赖变化对下游单据与财务结果的影响。
- Preconditions
上游依赖可控（库存、价格、税率、组织维度）；下游单据链路可执行。
- Key Assertions
上游变更后下游重算正确；依赖缺失时报错明确；跨模块引用ID一致。
- Risk Points
缓存旧值导致断言假通过、跨模块服务版本不一致。
- Test Level
`flow`, `regression`, `exception`

---

## ERP API TEST DOMAIN MAP（完整测试模型总结）
1. 以“单据生命周期”为主轴组织测试：
- `创建`（字段与默认值）
- `审批/提交`（状态机）
- `执行/过账`（异步与账务副作用）
- `关闭`（终态与回溯查询）

2. 以“数据依赖层”做前置门禁：
- 主数据：组织、伙伴、物料、税码、币种
- 交易依赖：价格、库存、审批规则
- 财务依赖：单据类型、结算项类型、会计期间

3. 以“角色与隔离”做横向约束：
- 供应商/运营/经销商在同一链路的操作边界
- 组织/租户级可见性与可操作性验证

4. 以“风险分层”安排执行集：
- `smoke`：主流程可达（创建/提交/查询）
- `flow`：跨模块端到端（SO→DN→发票→应收，应付链路同理）
- `regression`：规则矩阵与历史缺陷回归
- `permission/exception`：权限边界、幂等、异常输入、重复提交

5. 与当前项目结合的落地建议（模型映射）
- 优先把高价值链路收敛到统一模板（`standard_api_call + 统一断言规范`）。
- 对异步状态流转统一轮询策略，避免各模块重复实现。
- 建立“主数据→单据→财务”的最小黄金链路作为持续回归基线。

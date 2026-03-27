# ERP API TEST DOMAIN MAP

## 1. Master Data（主数据）
- Test Goal：验证主数据的增删改查、唯一性、启停用和被业务单据引用的有效性。
- Preconditions：基础组织/角色可用；主数据接口模板在 `config/api` 已配置；`md_init_cache` 可用。
- Key Assertions：
  - 接口成功 + 关键字段回写正确（code/name/status）。
  - DB 主表记录与接口回包一致。
  - 被下游单据引用时，禁用/启用状态行为符合预期。
- Risk Points：重复编码、脏主数据污染、主数据状态与业务引用不一致。
- Test Level：smoke / regression / exception。

## 2. Document APIs（单据类）
- Test Goal：验证单据创建、保存、提交、撤销、关闭等核心动作。
- Preconditions：主数据依赖齐全（客户/供应商/组织/仓库/物料/币种/价格）；操作者有权限。
- Key Assertions：
  - 单据主子表落库完整，编码规则正确。
  - 行项目数量/金额汇总正确。
  - 单据状态按动作变化（草稿、审批中、生效、关闭等）。
- Risk Points：主子表不一致、重复创建、状态与业务动作错配。
- Test Level：smoke / flow / regression。

## 3. State Transitions（状态流转）
- Test Goal：覆盖生命周期 `创建 -> 审批 -> 执行 -> 关闭` 的状态机正确性。
- Preconditions：审批规则启用；触发流转的单据和角色准备完成。
- Key Assertions：
  - 合法迁移可达、非法迁移被拦截。
  - 每次迁移后的状态字段可追踪。
  - 关键状态可通过 DB 二次验证（如 `so_status`）。
- Risk Points：跳状态、并发重复迁移、审批节点缺失。
- Test Level：flow / regression / exception。

## 4. Query / Report（查询/报表）
- Test Goal：验证查询条件、分页、排序、聚合统计和导出一致性。
- Preconditions：有可检索样本数据；组织和时间维度覆盖典型场景。
- Key Assertions：
  - `total/pageNo/pageSize` 正确。
  - 过滤条件命中准确，排序稳定。
  - 关键聚合值与 DB 对账一致。
- Risk Points：统计口径偏差、分页不稳定、跨组织数据串读。
- Test Level：smoke / regression。

## 5. Permission / Isolation（权限与数据隔离）
- Test Goal：验证不同角色、门户、组织下的读写边界。
- Preconditions：至少具备管理端+客户端账号（如 `TERP_PORTAL`、`TERP_CUST_PC`）。
- Key Assertions：
  - 无权限操作被拒绝。
  - 跨组织/跨租户数据不可见。
  - 不同角色接口返回字段范围符合策略。
- Risk Points：越权写入、越权读取、会话污染导致角色串号。
- Test Level：permission / regression / exception。

## 6. Idempotency（幂等与重复提交）
- Test Goal：验证保存/提交/审批等关键动作在重试或并发下不会产生重复业务结果。
- Preconditions：识别幂等关键接口；准备重复请求或并发触发条件。
- Key Assertions：
  - 重复请求结果可预期（复用/幂等拦截/版本冲突提示）。
  - DB 仅存在一条有效业务记录或一组一致版本记录。
  - 不出现重复库存扣减或重复财务影响。
- Risk Points：重复单据、重复过账、补偿失败。
- Test Level：exception / regression / flow。

## 7. Multi-role Workflow（多角色协同）
- Test Goal：验证供应商/运营/经销商在同一业务流程中的协同闭环。
- Preconditions：多角色账号可登录；审批规则与待办机制可用。
- Key Assertions：
  - 任务路由到正确角色。
  - 前一角色动作后，后一角色可见并可处理。
  - 流程日志责任链完整可追踪。
- Risk Points：任务错派、待办丢失、角色上下文错用。
- Test Level：flow / permission / regression。

## 8. Upstream / Downstream Dependency（上下游依赖）
- Test Goal：验证上游主数据/单据变化对下游模块的传播一致性。
- Preconditions：构建跨域数据链（采购/销售/库存/财务）；关键字段可追踪。
- Key Assertions：
  - 上游状态变化正确影响下游可执行状态。
  - 数量/金额/组织字段跨模块传递一致。
  - 异常回滚后上下游状态一致。
- Risk Points：链路断裂、字段失配、回滚不完整。
- Test Level：flow / regression / exception。

## ERP Lifecycle Focus（单据生命周期）
必须覆盖并结构化沉淀以下链路：
1. 创建：依赖主数据齐备，草稿可保存。
2. 审批：规则生效，状态可追踪。
3. 执行：库存/资金/业务状态同步更新。
4. 关闭：终态后操作受限且可校验。

## Dependency Focus（数据依赖）
- 主数据依赖：客户、供应商、组织、物料、仓库、币种、税和价格。
- 交易依赖：审批规则、库存可用量、结算/财务配置、异步任务状态。
- 平台依赖：门户认证、权限模型、流程引擎、通知任务。

## Multi-role Focus（多角色）
- 供应商：供货反馈、对账、状态回传。
- 运营：单据发起、审批推进、异常处理。
- 经销商/客户：订单协同、交付确认、回写反馈。

## Complete Summary
当前框架具备构建 ERP API 测试模型的核心基础：
- 配置驱动 + 标准化调用模板，适合大规模 API 覆盖。
- DB 校验与多门户登录已就位，可支撑状态和权限场景。
- 模块基类可沉淀域上下文（主数据、组织、角色）。

要把模型稳定落地为“长期可维护的回归体系”，建议优先补强：
1. 生命周期流程模板化（减少手工流程拼装）。
2. 权限矩阵标准用例集（角色和组织隔离可复用）。
3. 幂等/并发异常基线集（重复提交、补偿一致性）。
4. 断言语义库（状态、库存、金额等域断言标准化）。

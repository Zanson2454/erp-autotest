# ERP 自动化测试提效专项详细设计（LLD）

## 1. 文档信息
- 文档版本: v1.1
- 状态: Draft -> Review -> Approved
- 创建日期: 2026-04-03
- 对应 PRD: `plan/ERP_DSL_IDEMPOTENCY_PRD.md`
- 对应执行计划: `plan/ERP_DSL_IDEMPOTENCY_EXECUTION_PLAN.md`
- 变更记录:
1. v1.1: 冻结唯一键/Context/DTO/开关方案，移除阻塞型未决项。

## 2. 设计目标
1. 将高频业务动作沉淀为可组合、可测试、可复用的 Flow DSL。
2. 建立幂等造数能力，降低二次执行与并发执行下的环境不稳定。
3. 在不打断现有回归的前提下完成渐进式迁移。

## 3. 架构与模块边界
## 3.1 分层结构
1. Testcase 层: 业务断言与场景编排入口。
2. Flow 层: 面向业务语义动作（创建、提交、审核、出库、对账等）。
3. Service/Call 层: 统一通过 `standard_api_call` 发起 API 调用。
4. Repository 层: 只读查询（组织、物料）用于 ensure 判断。
5. Ensure 层: 先查后建 + 并发冲突回查，返回稳定业务对象。
6. Context 层: 用例运行态上下文隔离（ID、状态、关联对象）。

## 3.2 文件映射
1. `testcases/comm/base_flow.py`: Flow 抽象基类与统一异常处理。
2. `testcases/comm/test_context.py`: 上下文隔离与生命周期管理。
3. `repository/mdm_repo.py`: 组织/物料只读查询。
4. `erp_data_factory/domain/scenarios/common_skill.py`: ensure 逻辑增量。
5. `testcases/conftest.py`: `ensure_*` fixture 注入。
6. `testcases/scm_pur/pur_flow.py`: 采购流程 DSL。
7. `testcases/scm_sls/sls_flow.py`: 销售流程 DSL。
8. `testcases/scm_inv/inv_flow.py`: 库存流程 DSL。

## 4. 核心接口设计
## 4.1 BaseFlow 协议
约束：
1. 入参: Pydantic 模型。
2. 出参: 业务对象（DTO/Domain Object），禁止透传底层 Response。
3. 错误: Flow 层统一抛业务异常，保留底层异常 cause 与上下文。

建议接口：
```python
class BaseFlow:
    def execute(self, req_model) -> DomainObject: ...
    def _call_api(self, service_key: str, payload: dict) -> dict: ...
    def _wrap_error(self, action: str, e: Exception) -> FlowError: ...
```

DTO 最小字段规范（所有 Flow 返回对象必须满足）：
1. `id: str|int`（业务主键）
2. `biz_code: str|None`（业务单号/编码）
3. `status: str`（标准化状态）
4. `raw_status: str|None`（原系统状态，可选）
5. `trace_id: str|None`（链路追踪 ID）

## 4.2 TestContext 接口
目标：保证 xdist 并发时上下文不串扰。

建议接口：
```python
class TestContext:
    def set(self, key: str, value: object) -> None: ...
    def get(self, key: str, default=None): ...
    def clear(self) -> None: ...
    def snapshot(self) -> dict: ...
```

实现建议：
1. 采用“进程内 ContextVar + 用例 nodeid 命名空间”方案，不使用全局共享可变字典。
2. key 规范为 `{worker_id}:{nodeid}:{biz_key}`，保证 xdist 多 worker 隔离。
3. 在用例 teardown 或 Flow 结束钩子强制 `clear()`。

## 4.3 Repository 接口
目标：提供 ensure 判断所需最小只读能力。

建议接口：
```python
class MdmRepository:
    def get_org_by_name(self, org_name: str): ...
    def get_material_by_name(self, material_name: str): ...
```

约束：
1. SQL 必须参数化。
2. 仅返回必要字段（id/name/code/status）。
3. 业务唯一键定义:
   - 组织: `org_name + tenant_id`
   - 物料: `material_code + tenant_id`

## 4.4 Ensure 接口
目标：同参数重复调用返回同一业务实体，避免重复造数。

建议接口：
```python
def ensure_org_exists(name: str, **kwargs) -> OrgRef: ...
def ensure_material_exists(name: str, **kwargs) -> MaterialRef: ...
```

执行流程（关键）：
1. Query: Repository 按业务唯一键查询。
2. Reuse: 存在则直接返回引用对象。
3. Create: 不存在则调用标准创建流程。
4. Conflict Fallback: 创建遇唯一键冲突时回查并返回。
5. Trace: 记录来源 `created/reused` 到 Allure。

## 5. 业务流程设计（试点）
## 5.1 采购 PurFlow
1. `create_order(req)` -> 返回 `PurchaseOrderRef`。
2. `submit(order_id)` -> 返回 `FlowActionResult`。
3. `approve(order_id)` -> 返回 `FlowActionResult`。

## 5.2 销售 SlsFlow
1. `create_so(req)` -> `SalesOrderRef`。
2. `delivery(so_id)` -> `DeliveryRef`。
3. `reconcile(delivery_id)` -> `ReconcileResult`。

## 5.3 库存 InvFlow
1. `query_stock(req)` -> `InventorySnapshot`。
2. `adjust_location(req)` -> `AdjustResult`。
3. 支持语义断言 `snapshot.get_qty()`。

## 6. 异常与日志设计
## 6.1 异常分层
1. `FlowError`: 业务动作失败（可直接定位业务步骤）。
2. `RepositoryError`: 查询失败或返回异常。
3. `EnsureError`: 幂等流程失败（查询/创建/冲突回查）。

## 6.2 可观测性
1. 每个 Flow 动作必须写入 action 名、关键 ID、耗时、结果。
2. `ensure_*` 必须打点来源 `created/reused`。
3. 失败记录到 Allure `a.text/a.json`，保留原始错误信息。

## 7. 并发与幂等策略
1. 并发隔离: Context 按进程/用例隔离，禁止跨测试共享可变状态。
2. 幂等判断: 以业务唯一键为主，不以随机名称作为唯一判断条件。
3. 并发兜底: 创建冲突后回查，确保最终返回稳定 ID。
4. 重试策略: 仅对可判定的瞬态失败重试，不对业务校验失败重试。

## 8. 迁移与兼容策略
1. 迁移方式: 白名单 + 批次推进（pur/sls/inv/gen）。
2. 兼容方式: 保留旧入口，新增标记 `dsl_pilot` 控制灰度。
3. 开关实现:
   - 环境变量: `USE_FLOW_DSL=true|false`（默认 `false`）
   - pytest 参数: `--use-flow-dsl`（优先级高于环境变量）
   - 配置落点: `config/env/*.yml` + `pytest.ini` 自定义 option 映射
4. 约束: 禁止新增 `self.test_xxx()` 互调与直接 `self.http.post` 调用。
5. Legacy: 本期冻结新增引用，下期在“连续两迭代无引用”后删除。

## 9. 测试设计
## 9.1 单元/组件测试
1. BaseFlow: 入参校验、异常包装、返回对象转换。
2. Repository: 参数化查询与边界返回。
3. Ensure: 重复调用不新增、冲突回查成功返回。

## 9.2 集成测试
1. 冷启动: `python script/project_bootstrap.py` + 核心集回归。
2. 并发: `pytest testcases/scm_pur testcases/scm_sls -n 4`。
3. 二次运行: 连续两次同链路回归对比 Setup 耗时。

## 9.3 验收 Gate（与执行计划一致）
1. W1 Gate: 协议完整 + Context 并发隔离通过。
2. W2 Gate: Ensure 幂等单次/并发通过。
3. W3 Gate: 三条 DSL 试点可替代旧链路。
4. W4 Gate: 首批迁移 + 指标达成报告。

## 10. 发布、回滚与运维
1. 发布策略: 先试点模块，再逐批扩面。
2. 回滚策略: 按批次回滚，不做整仓回滚。
3. 触发条件: Gate 不通过、核心链路回归失败、指标显著劣化。
4. 应急动作: 关闭 DSL 开关并回退至旧路径。

## 11. 未决问题（仅保留非阻塞项）
1. 指标采集是否引入固定脚本自动生成周报（建议 W0 完成）。

## 12. 评审结论
- 评审人:
- 评审日期:
- 评审结论: `Approved` / `Changes Requested`

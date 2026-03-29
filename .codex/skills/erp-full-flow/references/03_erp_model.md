基于当前 ERP 系统，请从 API 自动化测试角度构建测试模型。

Classify APIs into：

1. Master Data（主数据）
2. Document APIs（单据类）
3. State Transitions（状态流转）
4. Query / Report（查询/报表）
5. Permission / Isolation（权限与数据隔离）
6. Idempotency（幂等与重复提交）
7. Multi-role Workflow（多角色协同）
8. Upstream / Downstream Dependency（上下游依赖）

对于每一类，输出：

- Test Goal（测试目标）
- Preconditions（前置条件）
- Key Assertions（关键断言点）
- Risk Points（风险点）
- Test Level（适合：smoke / regression / flow / permission / exception）

特别要求（ERP特性）：
- 必须考虑单据生命周期（创建→审批→执行→关闭）
- 必须考虑数据依赖（主数据、库存、价格等）
- 必须考虑多角色（供应商/运营/经销商）

最后输出：

ERP API TEST DOMAIN MAP（完整测试模型总结）
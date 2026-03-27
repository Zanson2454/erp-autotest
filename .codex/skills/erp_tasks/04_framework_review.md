请对当前 pytest API 自动化框架做架构级审查。

Focus on：

1. Layer Separation（分层是否清晰）
2. Client Abstraction（接口封装是否统一）
3. Auth Handling（鉴权是否集中）
4. Fixture Design（fixture 是否职责单一）
5. Test Data Reuse（测试数据是否可复用）
6. Assertion Depth（断言是否仅停留在 code/msg）
7. Environment Coupling（是否依赖环境）
8. ERP Workflow Support（是否支持复杂业务链路）
9. Extensibility（扩展新模块成本）
10. Automation Readiness（是否适合自动生成用例）

Output format：

- Issues List（问题清单）
- Impact（影响范围）
- Priority（P0/P1/P2）
- Short-term Fix（短期优化）
- Mid-term Refactor Plan（中期重构方案）
- Not Recommended Now（暂不建议处理项 + 原因）

要求：
- 不要给泛泛建议
- 必须结合项目实际结构
- 优先指出“会导致后期难维护”的问题
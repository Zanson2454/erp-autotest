You are working inside a pytest API automation project for ERP systems.
<!-- 中文：工作场景为面向 ERP 的 pytest API 自动化测试工程。 -->

GLOBAL RULES (MANDATORY):
<!-- 中文：全局强制规则，Agent 必须遵守。 -->

1. Never start coding before analysis.
   <!-- 中文：未经充分分析不得开始写代码。 -->
2. Always follow workflow: analysis → design → confirmation → implementation.
   <!-- 中文：固定流程——分析 → 设计 → 确认 → 再实现。 -->
3. Do not introduce new abstraction layers unless necessary.
   <!-- 中文：非必要不新增抽象层。 -->
4. Avoid over-engineering.
   <!-- 中文：避免过度设计。 -->
5. Do not put business logic into fixtures.
   <!-- 中文：业务逻辑不要塞进 fixture。 -->
6. Do not put all assertions inside test cases.
   <!-- 中文：断言不应全部堆在测试用例里（可下沉到工具/封装层等既有模式）。 -->
7. Follow existing project structure strictly.
   <!-- 中文：严格遵循现有项目结构与约定。 -->
8. Prefer minimal, incremental changes over large refactors.
   <!-- 中文：优先小而稳的增量修改，避免大块重构。 -->
9. Any refactor suggestion must include:
   <!-- 中文：凡提出重构须同时给出收益、成本与影响面。 -->
   - benefits
     <!-- 中文：收益（为何值得做）。 -->
   - cost
     <!-- 中文：成本（人力、风险、周期等）。 -->
   - impact scope
     <!-- 中文：影响范围（模块、用例、数据与环境）。 -->

P0 GOVERNANCE (IMMEDIATE ENFORCEMENT):
<!-- 中文：P0 治理项（立刻执行，违规即阻断）。 -->

1. Never hardcode secrets in repository code.
   <!-- 中文：禁止在仓库代码中硬编码任何敏感信息（token、webhook、密码、密钥、账号等）。 -->
2. Use environment variables or secret managers for all sensitive values.
   <!-- 中文：敏感值必须通过环境变量或密钥管理注入，不得写入源码。 -->
3. If a class overrides teardown_class, it must call super().teardown_class().
   <!-- 中文：子类重写 teardown_class 时，必须调用 super().teardown_class()，确保父类资源释放不丢失。 -->
4. Resource cleanup must be deterministic and placed in finally-equivalent paths.
   <!-- 中文：资源清理必须是确定性的，需放在 finally 等兜底路径，避免异常中断导致泄漏。 -->
5. Any P0 violation must be fixed before merge; no "follow-up ticket" deferral.
   <!-- 中文：P0 问题必须在合入前修复，不接受“后续再修”的延期策略。 -->

ERP-SPECIFIC RULES:
<!-- 中文：与 ERP 业务测试相关的专项规则。 -->

1. Consider state transitions, dependencies, permissions, idempotency.
   <!-- 中文：需考虑状态流转、依赖、权限、幂等等因素。 -->
2. Do not generate shallow tests (e.g. only checking code == 0).
   <!-- 中文：禁止只写浅层用例（例如仅校验 code==0）。 -->
3. Ensure test logic reflects business semantics.
   <!-- 中文：用例逻辑应体现业务语义，而非仅限接口表层。 -->

OUTPUT RULES:
<!-- 中文：对 Agent 输出形式的要求。 -->

1. Clearly separate:
   <!-- 中文：输出中需明确区分以下几类信息。 -->
   - confirmed facts
     <!-- 中文：已确认事实。 -->
   - inferred assumptions
     <!-- 中文：推断或假设（需标注为假设）。 -->
   - unknowns
     <!-- 中文：尚不明确项。 -->
2. Provide structured outputs, not vague explanations.
   <!-- 中文：给出结构化结论，避免含糊表述。 -->

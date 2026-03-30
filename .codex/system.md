You are working inside a pytest API automation project for ERP systems.
<!-- 中文：工作场景为面向 ERP 的 pytest API 自动化测试工程。 -->
<!-- 中文：本文件是“Agent 运行时约束”，主要影响分析顺序、实现方式与输出结构；请优先按 P0 -> Global Rules -> ERP-SPECIFIC -> OUTPUT 的优先级执行。 -->

## 中文要点（可见版）
（说明：以下为中文阅读辅助；约束仍以原英文条款为准。）
- 必须先分析再写代码：确认 API、参数、基类与数据来源等，再进入实现。
- 必须遵循流程：analysis → design → confirmation → implementation。
- 尽量不新增抽象层、避免过度设计，保持与项目结构一致。
- 业务逻辑不要放进 fixtures；断言也不要全部挤在测试函数里（可下沉到已有工具/封装）。
- 如涉及重构/建议，必须同时给出：`benefits`、`cost`、`impact scope`。
- P0：禁止在代码中硬编码敏感信息；P0 违规必须在合入前修复（不接受延期）。
- 清理资源要确定性落在 `finally`/等价兜底；重写 `teardown_class` 时必须调用 `super().teardown_class()`。
- ERP 业务：要考虑状态流转、依赖/权限、幂等；避免浅层用例；测试逻辑要反映业务语义。
- 输出：区分 `confirmed facts`（已确认）、`inferred assumptions`（假设）、`unknowns`（未知），并给出结构化结论。

GLOBAL RULES (MANDATORY):
<!-- 中文：全局强制规则，Agent 必须遵守。 -->

1. Never start coding before analysis.
   <!-- 中文：未经充分分析不得开始写代码。 -->
   <!-- 中文：分析包含：确认 API 名称/参数、确认基类与数据来源（init_data/md_cache_data）、确认已有封装/工具调用方式。 -->
2. Always follow workflow: analysis → design → confirmation → implementation.
   <!-- 中文：固定流程——分析 → 设计 → 确认 → 再实现。 -->
   <!-- 中文：design/confirmation 用于避免生成错误的测试骨架或漏掉幂等/清理/断言等关键点。 -->
3. Do not introduce new abstraction layers unless necessary.
   <!-- 中文：非必要不新增抽象层。 -->
   <!-- 中文：优先复用现有 BaseTest/standard_api_call/case_decorator/工具封装；除非复用成本很高且能证明收益。 -->
4. Avoid over-engineering.
   <!-- 中文：避免过度设计。 -->
   <!-- 中文：保持改动最小、可读、可维护；不要为了“看起来更优雅”引入复杂结构。 -->
5. Do not put business logic into fixtures.
   <!-- 中文：业务逻辑不要塞进 fixture。 -->
   <!-- 中文：fixture 只负责数据准备/初始化资源；业务断言与业务流转应放在测试方法或已存在的 helper/工具中。 -->
6. Do not put all assertions inside test cases.
   <!-- 中文：断言不应全部堆在测试用例里（可下沉到工具/封装层等既有模式）。 -->
   <!-- 中文：仍需保证关键断言在测试链路中可追踪（例如通过标准断言工具 assert_util）。 -->
7. Follow existing project structure strictly.
   <!-- 中文：严格遵循现有项目结构与约定。 -->
   <!-- 中文：新用例优先放到既定目录（如 testcases/xxx），遵循 file_level_order 的串行规则。 -->
8. Prefer minimal, incremental changes over large refactors.
   <!-- 中文：优先小而稳的增量修改，避免大块重构。 -->
   <!-- 中文：若需要重构，必须先评估风险与影响范围（见下方 refactor suggestion 条件）。 -->
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
<!-- 中文：P0 条款优先级最高；只要命中 P0 违规，即使其余代码看似正确也必须先修复再提交/合入。 -->

1. Never hardcode secrets in repository code.
   <!-- 中文：禁止在仓库代码中硬编码任何敏感信息（token、webhook、密码、密钥、账号等）。 -->
   <!-- 中文：例如：不要写死 Authorization、Cookie、DB 密码、外部服务 key；统一通过 env 或 CI 注入。 -->
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
<!-- 中文：输出时要把“我已确认的内容”和“我推断/假设的内容”分开，避免把假设当事实。 -->

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

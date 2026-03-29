基于已有分析结果，请生成 project_map.md。

目标：让新成员可以快速理解该自动化框架。

必须包含：

1. Architecture Layers（整体分层结构）
2. Directory Structure（目录说明）
3. Module Responsibilities（核心模块职责）
4. Request Lifecycle（请求调用链路）
5. Fixture Dependency（fixture 依赖关系）
6. Config Flow（配置加载流程）
7. Test Data Lifecycle（测试数据生命周期）
8. Assertion Layer（断言层设计）
9. How to Add New Module（新增业务模块接入方式）

要求：
- 使用结构化 Markdown
- 结合当前项目实际，不要抽象描述
- 说明真实调用路径（例如：test → fixture → client → API）
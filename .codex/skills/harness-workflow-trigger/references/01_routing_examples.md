目标：将用户表达稳定路由到 Harness 子 skill。

输出格式（必须）：
- 命中关键词：
- 路由结果：
- 理由：
- 备选路由：

示例：
1) 输入：“最近回归失败现场太碎，想把 trace 和日志绑一起”
- 命中关键词：现场、trace、日志
- 路由结果：semantic-context-construction
- 理由：问题核心是失败现场结构化
- 备选路由：contract-constraint-design

2) 输入：“需要定义 AI 修复后自动重跑并回写记录的流程”
- 命中关键词：AI 修复、自动重跑、回写
- 路由结果：agentic-protocol-orchestration
- 理由：核心是协议和状态机
- 备选路由：failure-knowledge-flywheel

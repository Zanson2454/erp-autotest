---
name: workflow-trigger
description: 工作流触发器 - 检测任务关键词，自动调用对应的 superpowers 系统级 skill
---

# Workflow Trigger Skill

## 触发规则

当检测到以下关键词时，自动调用对应的系统级 skill：

| 关键词 | 触发 Skill | 说明 |
|--------|-----------|------|
| 设计、功能、方案、架构 | `brainstorming` | 创意工作 |
| 调试、排查、修复、错误 | `systematic-debugging` | 问题排查 |
| 测试、单元测试、测试驱动 | `test-driven-development` | 测试开发 |
| 代码审查、review、审查 | `receiving-code-review` | 接收审查 |
| 计划、任务拆分、实施计划 | `writing-plans` | 任务规划 |
| 完成、合并、PR、提交 | `finishing-a-development-branch` | 完成工作 |

## 自动调用逻辑

1. 解析用户输入
2. 匹配关键词
3. 触发对应的 superpowers skill
4. 执行 skill 定义的流程

## 手动指定

如果自动匹配不准确，可以手动指定：

```
@workflow [skill_name]
```

例如：
- `@workflow brainstorming`
- `@workflow systematic-debugging`
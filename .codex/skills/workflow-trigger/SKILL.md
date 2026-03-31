---
name: workflow-trigger
description: 统一工作流触发器 - 解析用户任务并路由到已落地的项目 skills
---

# Workflow Trigger Skill

## 定位

本 skill 是项目内唯一的自动触发入口，用于避免多个触发器重复匹配。

## 启用中的路由规则（仅已落地 skills）

当检测到以下关键词时，自动路由到对应 skill：

| 关键词 | 路由 Skill | 说明 |
|---|---|---|
| 录制转用例、curl 转用例、recorded_flow、raw_curls、mitm 录制、录制回放转 pytest | `curl-to-testcase` | 将录制产物转为项目标准测试用例 |
| ERP 全流程分析、项目盘点、框架审查、项目地图 | `erp-full-flow` | 端到端框架分析与评估输出 |
| 设计、方案、架构、功能规划、如何实现 | `brainstorming-trigger` | 需求澄清与方案设计 |
| 报错、排查、调试、问题定位、为什么不工作 | `debugging-trigger` | 快速分诊与定位路径 |
| 语义化现场、上下文注入、trace 关联、可观测性对齐、环境快照 | `semantic-context-construction` | 只负责失败现场采集与结构化 |
| 契约化约束、断言边界、前后置条件、容错规则、Harness、AI Native Testing | `contract-constraint-design` | 只负责契约与断言边界定义 |
| 协同协议、agent 编排、tool-use、自修复链路、MCP 测试流 | `agentic-protocol-orchestration` | 只负责角色权限、状态机和工具白名单 |
| 失败知识回流、先验知识、失败复盘沉淀、RAG 测试知识 | `failure-knowledge-flywheel` | 只负责失败知识沉淀与复用 |
| 防腐工程、熵增治理、僵尸用例、误报治理、文档同步 | `digital-anti-entropy` | 只负责自动化资产治理 |

## Harness 固定串联顺序

当任务涉及完整 Harness 闭环时，按以下顺序执行，避免职责重叠：

`semantic-context-construction -> contract-constraint-design -> agentic-protocol-orchestration -> failure-knowledge-flywheel -> digital-anti-entropy`

## 路由优先级

1. 若同时出现“现场采集”和“知识沉淀”，优先 `semantic-context-construction`。
2. 若同时出现“契约约束”和“协议编排”，优先 `contract-constraint-design`。
3. 明确出现角色权限、状态流转、tool-use 时，优先 `agentic-protocol-orchestration`。
4. 未命中规则时，回退到通用分析并提示用户补充信息。

## 预留目标说明

历史路由中的 `bugfix`、`sql-debug`、`api-test`、`test-case-design`、`regression-checklist`、`performance-test`、`code-review` 当前未在本仓库落地，暂不参与自动路由。

## 手动指定

```text
@workflow [skill_name]
```

例如：
- `@workflow debugging-trigger`
- `@workflow erp-full-flow`
- `@workflow semantic-context-construction`

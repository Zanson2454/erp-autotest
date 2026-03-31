---
name: workflow-trigger
description: Route user requests to project workflows and skills in Cursor. Use when users ask for recorded-curl conversion, ERP full-flow analysis, debugging triage, or framework governance tasks.
---

# Workflow Trigger (Cursor)

## Purpose
Single routing entry for this repository. It decides which project skill/workflow to run and avoids duplicate trigger logic.

## Routing Table
- `录制转用例`, `curl 转用例`, `recorded_flow`, `raw_curls` -> `.codex/skills/curl-to-testcase/SKILL.md`
- `ERP 全流程分析`, `项目盘点`, `项目地图`, `框架审查` -> `.codex/skills/erp-full-flow/SKILL.md`
- `设计`, `方案`, `架构`, `如何实现` -> `.codex/skills/brainstorming/SKILL.md`
- `报错`, `排查`, `调试`, `定位` -> `.codex/skills/systematic-debugging/SKILL.md`
- `语义化现场`, `上下文注入`, `trace 关联` -> `.codex/skills/semantic-context-construction/SKILL.md`
- `契约化约束`, `断言边界`, `容错规则` -> `.codex/skills/contract-constraint-design/SKILL.md`
- `协同协议`, `agent 编排`, `tool-use` -> `.codex/skills/agentic-protocol-orchestration/SKILL.md`
- `失败知识`, `复盘沉淀`, `先验知识` -> `.codex/skills/failure-knowledge-flywheel/SKILL.md`
- `防腐工程`, `熵增治理`, `误报治理` -> `.codex/skills/digital-anti-entropy/SKILL.md`

## Priority Rules
1. If context collection and knowledge reuse both appear, run semantic context first.
2. If constraints and orchestration both appear, run contract constraints first.
3. If role/permission/state machine/tool whitelist appears, prioritize protocol orchestration.
4. If no route matches, ask for one concrete goal and expected output.

## Full Harness Sequence
`semantic-context-construction -> contract-constraint-design -> agentic-protocol-orchestration -> failure-knowledge-flywheel -> digital-anti-entropy`

## Keyword to Template Mapping
- `recorded_flow`, `raw_curls`, `录制转用例` -> use template `cURL -> Testcase` in `.cursor/workflows/request_templates.md`
- `全流程分析`, `项目地图`, `框架审查` -> use template `ERP Full Flow Audit` in `.cursor/workflows/request_templates.md`
- `报错`, `失败`, `排查`, `root cause` -> use template `Systematic Debugging` in `.cursor/workflows/request_templates.md`

## Fast Start
1. Run manual trigger.
2. Paste one matching template from `.cursor/workflows/request_templates.md`.
3. Fill only required placeholders and keep one clear goal.

## Manual Trigger
```text
@workflow workflow-trigger
```

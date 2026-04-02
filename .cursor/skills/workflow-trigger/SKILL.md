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

## Priority Rules
1. If design and debugging both appear, run debugging first.
2. If full audit and local bugfix both appear, run full audit first.
3. If no route matches, ask for one concrete goal and expected output.

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

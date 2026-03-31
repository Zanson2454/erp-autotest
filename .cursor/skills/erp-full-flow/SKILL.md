---
name: erp-full-flow
description: Run end-to-end ERP pytest automation framework analysis and output structured assessment docs. Use for project takeover, framework review, project map, or full-flow audit requests.
---

# erp-full-flow (Cursor Adapter)

## Purpose
Cursor-facing entry for full framework analysis. Delegate to:
- `.codex/skills/erp-full-flow/SKILL.md`
- `.cursor/workflows/erp_full_flow_playbook.md`

## Trigger Hints
- "ERP 全流程分析"
- "项目盘点"
- "项目地图"
- "框架审查"

## Execution Contract
1. Read the codex skill and playbook.
2. Produce or refresh outputs under `outputs/`.
3. Mark `P0/P1/P2` risks and impact scope.

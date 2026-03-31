# ERP Full Flow Playbook (Cursor)

## Trigger
- Recommended: `@workflow workflow-trigger` + "做一次 ERP 自动化框架全流程分析"（统一入口，避免多触发器混淆）
- Direct: `@workflow erp-full-flow`（直接调用，跳过路由层）

## Inputs
- Repository root code and config
- Existing output files in `outputs/`

## Steps
1. Read `.codex/skills/erp-full-flow/references/01_scan_project.md` and update `outputs/01_project_analysis.md`.
2. Read `.codex/skills/erp-full-flow/references/02_project_map.md` and update `outputs/02_project_map.md`.
3. Read `.codex/skills/erp-full-flow/references/03_erp_model.md` and update `outputs/03_erp_test_domain_map.md`.
4. Read `.codex/skills/erp-full-flow/references/04_framework_review.md` and update `outputs/04_gap_analysis.md`.

## Output Contract
Each output should contain:
- Confirmed facts
- Inferred assumptions
- Unknowns
- Priority risks (`P0/P1/P2`) and impact scope

## Guardrails
- Analyze before recommending changes.
- Do not hardcode secrets.
- Prefer incremental suggestions over broad refactors.
- If `outputs/0x_*.md` already exists, preserve existing content and only update changed/new sections. Do not full-overwrite.

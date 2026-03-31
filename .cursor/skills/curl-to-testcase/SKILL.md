---
name: curl-to-testcase
description: Convert recorded curl flows into project-standard pytest ERP API testcases. Use when users mention recorded_flow, raw_curls, mitm recordings, or curl-to-testcase generation.
---

# curl-to-testcase (Cursor Adapter)

## Purpose
Cursor-facing entry that delegates execution to the project skill:
- `.codex/skills/curl-to-testcase/SKILL.md`

## Trigger Hints
- "录制转用例"
- "curl 转 pytest"
- "recorded_flow"
- "raw_curls"

## Execution Contract
1. Read `.codex/skills/curl-to-testcase/SKILL.md`.
2. Follow its workflow and guardrails exactly.
3. Return:
   - touched files
   - testcase/method list
   - api path -> api_key mapping
   - confirmed facts / inferred assumptions / unknowns

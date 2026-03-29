---
name: erp-full-flow
description: 端到端分析 ERP 的 pytest API 自动化项目并输出结构化评估文档。用于项目接手、框架盘点、可维护性评估、ERP 业务测试模型梳理，或用户要求“全量分析当前自动化框架/输出项目地图与改进建议”时。
---

# ERP Full Flow

## Overview

按固定四步完成项目分析，输出四份 Markdown 结果，覆盖项目扫描、结构地图、ERP 测试模型和框架级审查。优先基于真实代码与配置给结论，明确区分“已确认信息”和“推断信息”。

## Workflow

1. 执行项目扫描：读取 `references/01_scan_project.md`，输出项目结构与关键问题。
2. 生成项目地图：读取 `references/02_project_map.md`，输出可供新成员快速上手的结构化地图。
3. 生成 ERP 测试模型：读取 `references/03_erp_model.md`，输出领域测试模型与关键断言点。
4. 执行框架审查：读取 `references/04_framework_review.md`，输出架构审查结论与分级建议。

## Output Files

- `outputs/01_project_analysis.md`
- `outputs/02_project_map.md`
- `outputs/03_erp_test_domain_map.md`
- `outputs/04_gap_analysis.md`

## Execution Rules

- 先读代码再下结论，不给泛化建议。
- 对每份输出同时给出：已确认信息、推断信息、待确认项。
- 不直接改业务代码；本 skill 以分析产出为主。
- 发现高风险问题时，标注优先级（P0/P1/P2）与影响范围。

## References

- 流程定义：`references/erp_full_flow.yaml`
- 第 1 步提示词：`references/01_scan_project.md`
- 第 2 步提示词：`references/02_project_map.md`
- 第 3 步提示词：`references/03_erp_model.md`
- 第 4 步提示词：`references/04_framework_review.md`

## Manual Trigger

```text
@workflow erp-full-flow
```

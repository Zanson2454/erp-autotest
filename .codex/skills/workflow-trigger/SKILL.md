---
name: workflow-trigger
description: 统一工作流触发器 - 解析用户任务并路由到最合适的项目 skill
---

# Workflow Trigger Skill

## 定位

本 skill 是项目内唯一的自动触发入口，用于避免多个触发器重复匹配。

## 触发规则

当检测到以下关键词时，自动路由到对应 skill：

| 关键词 | 路由 Skill | 说明 |
|---|---|---|
| ERP 全流程分析、项目盘点、框架审查、项目地图 | `erp-full-flow` | 端到端框架分析与评估输出 |
| 设计、方案、架构、功能规划、如何实现 | `brainstorming-trigger` | 需求澄清与方案设计 |
| 报错、排查、调试、问题定位、为什么不工作 | `debugging-trigger` | 快速分诊与定位路径 |
| 修复、缺陷、修 bug、hotfix、回归失败 | `bugfix` | 最小修复与验证 |
| SQL、慢查询、索引、锁、死锁、执行计划 | `sql-debug` | 数据库与 SQL 专项排查 |
| 接口测试、API 测试、联调、鉴权、幂等 | `api-test` | 接口测试分析与脚本建议 |
| 测试用例、测试点、需求测试、场景设计 | `test-case-design` | 功能用例设计 |
| 回归、发布前检查、影响面、冒烟 | `regression-checklist` | 回归清单与发布检查 |
| 性能、压测、并发、TPS、QPS、瓶颈 | `performance-test` | 性能测试方案与分析 |
| review、代码审查、PR 审查 | `code-review` | 工程化审查 |

## 路由优先级

1. 如果同时命中“排查”和“修复”，优先 `bugfix`。
2. 明确出现 SQL 关键词时，优先 `sql-debug`。
3. 未命中规则时，回退到通用分析并提示用户补充信息。

## 手动指定

```text
@workflow [skill_name]
```

例如：
- `@workflow bugfix`
- `@workflow api-test`
- `@workflow erp-full-flow`

---
name: workflow-trigger
description: 统一工作流触发器 - 解析用户任务并路由到已落地的项目 skills
---

# Workflow Trigger Skill

## 定位

本 skill 是项目内唯一的自动触发入口，用于避免多个触发器重复匹配。

## 全局简化原则（前置）

- 宁可先做可控重复，也不要为“抽象复用”引入复杂结构。
- 不要为解决局部复杂问题，把已有设计演进为更复杂的体系。
- 只有在明确出现重复成本失控（维护成本、缺陷率、认知负担显著上升）时，才允许做结构升级。

## 输出语言约束

- 总结性内容（结论、变更摘要、下一步建议）默认使用中文。
- 专有名词、命令、代码标识符可保留英文，不强制翻译。

## 中文注释全局约束（强制）

- 在本仓库新增或修改代码时，注释与 docstring 默认使用中文。
- 禁止占位式无效注释（例如“方法实现说明”“类职责说明”这类空话模板）。
- 注释必须提供真实信息，至少覆盖以下之一：
  - 文件职责与边界
  - 类职责与使用场景
  - 函数输入/输出/关键副作用
  - 异常语义与失败路径
- 对标识符、协议字段、第三方接口名可保留英文原文，避免误译。
- 发现历史占位注释时，优先替换为有效中文说明；若无法补充有效信息，删除该注释。

## 启用中的路由规则（仅已落地 skills）

当检测到以下关键词时，自动路由到对应 skill：

| 关键词 | 路由 Skill | 说明 |
|---|---|---|
| 录制转用例、curl 转用例、recorded_flow、raw_curls、mitm 录制、录制回放转 pytest | `curl-to-testcase` | 将录制产物转为项目标准测试用例 |
| ERP 全流程分析、项目盘点、框架审查、项目地图 | `erp-full-flow` | 端到端框架分析与评估输出 |
| 设计、方案、架构、功能规划、如何实现 | `brainstorming-trigger` | 需求澄清与方案设计 |
| 报错、排查、调试、问题定位、为什么不工作 | `debugging-trigger` | 快速分诊与定位路径 |

## 推荐串联模板（实用优先）

### 1. 录制转用例（高频）

`workflow-trigger -> curl-to-testcase -> debugging-trigger（仅在生成后失败时）`

### 2. 问题排查到修复闭环

`workflow-trigger -> debugging-trigger -> brainstorming-trigger（需要修复方案对比时）`

### 3. 项目接手与全量盘点

`workflow-trigger -> erp-full-flow -> brainstorming-trigger（需要后续改造方案时）`

## 路由优先级

1. 若同时出现“方案设计”和“问题定位”，优先 `debugging-trigger`（先定位再设计）。
2. 若同时出现“全量盘点”和“局部修复”，优先 `erp-full-flow`（先全局后局部）。
3. 未命中规则时，回退到通用分析并提示用户补充信息。

## 预留目标说明

历史路由中的 `bugfix`、`sql-debug`、`api-test`、`test-case-design`、`regression-checklist`、`performance-test`、`code-review` 当前未在本仓库落地，暂不参与自动路由。

## 手动指定

```text
@workflow [skill_name]
```

例如：
- `@workflow debugging-trigger`
- `@workflow erp-full-flow`
- `@workflow brainstorming-trigger`

## 全局简化原则（后置重申）

- 若方案在“少量重复 + 简单结构”和“高度抽象 + 复杂结构”之间可选，默认选择前者。
- 禁止以一次性问题为理由引入跨模块复杂编排。

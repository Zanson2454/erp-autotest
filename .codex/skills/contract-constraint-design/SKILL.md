---
name: contract-constraint-design
description: 契约化约束设计技能 - 为测试流程定义输入输出契约、断言边界和容错规则
---

# Contract Constraint Design

## 职责边界

- 负责：输入输出契约、断言分层、容错规则。
- 不负责：工具协议编排（交给 `agentic-protocol-orchestration`）、失败现场采集（交给 `semantic-context-construction`）。

## 串联位置

Harness 固定链路第 2 步。

## 适用场景

- 断言松散导致误报/漏报
- 多系统联调时边界不清，责任归属模糊
- 需要将“口头规则”沉淀为可执行约束

## 执行步骤

1. 定义测试对象契约：输入、输出、前置、后置、不变量。
2. 将契约映射为分层断言：强约束、弱约束、观测项。
3. 定义异常分级与容错策略（可重试、可降级、必须中断）。
4. 建立契约变更审查点，防止 silent regression。

## 输出格式

### 1. 契约定义
- 输入契约：
- 输出契约：
- 前后置条件：

### 2. 断言矩阵
| 约束项 | 断言级别 | 失败动作 |
|---|---|---|

### 3. 风险与待确认
- 高风险漂移点：
- 待业务确认规则：

## 验收指标

- 误报率下降
- 漏报率下降
- 契约变更可追踪率 100%

## References

- 输出模板：`references/01_output_template.md`
- 指标口径：`references/02_metrics_definition.md`
- 执行检查单：`references/03_execution_checklist.md`

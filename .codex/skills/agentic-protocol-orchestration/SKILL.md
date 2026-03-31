---
name: agentic-protocol-orchestration
description: 协同协议编排技能 - 设计人、AI、测试工具之间的可执行协作协议
---

# Agentic Protocol Orchestration

## 职责边界

- 负责：角色权限、状态机、tool-use 白名单、回滚接管策略。
- 不负责：业务契约细节（交给 `contract-constraint-design`）、失败知识沉淀（交给 `failure-knowledge-flywheel`）。

## 串联位置

Harness 固定链路第 3 步。

## 适用场景

- AI 可调用工具多但边界不清，存在误操作风险
- 需要定义“AI 修复 -> 重跑 -> 验证 -> 记录”的自动链路
- 多角色协作时责任与状态流转不一致

## 执行步骤

1. 定义参与角色与权限边界（人、agent、工具）。
2. 设计 tool-use 白名单与调用前置条件。
3. 定义状态机：待处理 -> 修复中 -> 重跑中 -> 已验证 -> 已归档。
4. 设计失败回滚与人工接管策略。

## 输出格式

### 1. 协议定义
- 角色与权限：
- 工具白名单：
- 禁止动作：

### 2. 状态流转
- 当前状态：
- 转移条件：
- 审计记录字段：

### 3. 异常处置
- 自动回滚条件：
- 人工接管触发条件：

## 验收指标

- 自动修复链路成功率
- 人工介入次数下降
- 协议违规调用为 0

## References

- 输出模板：`references/01_output_template.md`
- 指标口径：`references/02_metrics_definition.md`
- 执行检查单：`references/03_execution_checklist.md`

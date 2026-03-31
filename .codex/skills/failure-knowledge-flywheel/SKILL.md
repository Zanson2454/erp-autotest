---
name: failure-knowledge-flywheel
description: 失败知识飞轮技能 - 将失败样本自动沉淀为可检索、可复用的先验知识
---

# Failure Knowledge Flywheel

## 职责边界

- 负责：失败知识结构化沉淀、检索命中、复用回写。
- 不负责：现场证据采集（交给 `semantic-context-construction`）、流程协议设计（交给 `agentic-protocol-orchestration`）。

## 串联位置

Harness 固定链路第 4 步。

## 适用场景

- 同类问题重复出现，排障成本高
- 失败案例散落在日志和群聊，无法沉淀
- 需要构建“失败 -> 修复 -> 回归”的自动学习闭环

## 执行步骤

1. 采集失败事件：症状、根因、修复动作、验证结果。
2. 结构化入库：统一标签（模块/错误码/版本/环境）。
3. 生成检索视图：按问题类型和影响范围可检索。
4. 在新失败分诊时优先召回历史先验并给出命中证据。

## 输出格式

### 1. 失败知识卡
- 现象：
- 根因：
- 修复：
- 验证：

### 2. 检索命中
- 命中案例：
- 相似度依据：
- 复用建议：

### 3. 闭环状态
- 是否已回归验证：
- 是否纳入防回归用例：

## 验收指标

- 同类问题平均定位耗时下降
- 失败知识复用率提升
- 防回归覆盖率提升

## References

- 输出模板：`references/01_output_template.md`
- 指标口径：`references/02_metrics_definition.md`
- 执行检查单：`references/03_execution_checklist.md`

---
name: semantic-context-construction
description: 语义化现场构建技能 - 将失败现场转为 AI 可理解、可追溯、可复现的结构化上下文
---

# Semantic Context Construction

## 职责边界

- 负责：失败现场采集、证据关联、结构化输出。
- 不负责：失败知识沉淀（交给 `failure-knowledge-flywheel`）、契约设计（交给 `contract-constraint-design`）。

## 串联位置

Harness 固定链路第 1 步。

## 适用场景

- 用例失败但证据分散，AI 无法稳定定位根因
- 需要将日志、trace、数据状态统一到同一上下文包
- 回归偶发失败，需要高保真还原现场

## 执行步骤

1. 定义最小上下文字段：请求、响应、trace_id、关键日志、数据快照、环境参数。
2. 在失败钩子注入采集逻辑（fixture / hook / decorator）。
3. 按统一 schema 输出上下文包（JSON 或 Markdown 结构块）。
4. 校验上下文完整率并标记缺失字段。

## 输出格式

### 1. 已确认信息
- 失败入口：
- 关键 trace_id：
- 关键状态快照：

### 2. 推断信息
- 可能异常链路：
- 可能受影响模块：

### 3. 待确认项
- 缺失证据：
- 下一步采集动作：

## 验收指标

- 上下文完整率 >= 90%
- 关键字段缺失率 <= 5%
- 同类问题复现时间下降

## References

- 输出模板：`references/01_output_template.md`
- 指标口径：`references/02_metrics_definition.md`
- 执行检查单：`references/03_execution_checklist.md`

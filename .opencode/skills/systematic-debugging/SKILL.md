---
name: debugging-trigger
description: 问题排查触发器 - 当用户进行问题排查、调试时自动调用
---

# Debugging Trigger

## 触发关键词

- 报错
- 排查
- 调试
- 修复
- 问题
- 错误
- 为什么
- 不工作

## 行为

当检测到以上关键词时，Opencode 会自动：
1. 调用 `systematic-debugging` skill
2. 按照 skill 定义的问题排查流程
3. 定位并修复问题

## 禁用手动调用

本 skill 用于自动触发，无需手动调用。
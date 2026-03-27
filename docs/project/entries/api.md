---
title: "\u4E3A\u4EC0\u4E48API\u8BA1\u8D39\u8981\u533A\u5206\u8F93\u5165\u8F93\u51FA"
tags:
- API
- "\u8BA1\u8D39"
- LLM
- Token
- "\u4F18\u5316"
created_at: '2026-03-27T06:11:17+00:00'
updated_at: '2026-03-27T06:11:17+00:00'
submitted_at: '2026-03-27T06:11:17+00:00'
date: '2026-03-27'
word_count: 86
image_count: 0
type: note
status: mature
related: []
---

# 为什么API计费要区分输入输出

大模型 API的输入和输出 token通常要分别计费

## 输入阶段
- 将输入prompt做embedding
- 进行一次前向传播
- 保存KV cache

## 输出阶段
- 自回归生成并保存新token
- 每次都要访问缓存、前向传播
- 访存带宽大，时间消耗长，计算次数多
- 会更贵一些

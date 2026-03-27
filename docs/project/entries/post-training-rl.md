---
title: "Post-Training \u8BE6\u89E3\uFF1ARL \u65B9\u6CD5\u8BBA"
tags:
- AI
- Post-Training
- RL
- PPO
- GRPO
- DPO
- ML
created_at: '2026-03-27T04:17:05+00:00'
updated_at: '2026-03-27T04:17:05+00:00'
submitted_at: '2026-03-27T04:17:05+00:00'
date: '2026-03-27'
word_count: 372
image_count: 0
type: note
status: mature
related: []
---

# Post-Training 详解：RL 方法论

# Post-Training 详解

## 数据量需求
- 需要几十M到几B的数据
- 用于模型的微调和优化

## 常用方法

### Online RL（在线强化学习）
智能体在训练过程中持续与环境进行交互，数据的采集和训练是交替循环进行的。

#### PPO (Proximal Policy Optimization)
- RM 给出绝对分数的估计值
- 梯度/优势为：**实际得分 - Critic 预估分**

#### GRPO (Group Relative Policy Optimization)  
- RM 给出组内各个数据的分数
- 得到一个排序，根据排序计算优势

### Offline RL（离线强化学习）
收集一组成对数据集进行模型训练。

#### DPO (Direct Preference Optimization)
- 训练数据：输入 prompt、好的 Response、坏的 Response
- Loss 函数：log σ(Good|prompt - Bad|prompt)
- 无需显式的 Reward Model

## 关键区别

| 方法 | 数据采集 | 特点 | 适用场景 |
|------|--------|------|--------|
| Online RL (PPO) | 动态交互 | 实时反馈，收敛快 | 需要快速迭代 |
| Online RL (GRPO) | 动态交互 | 相对评分，稳定性好 | 大规模训练 |
| Offline RL (DPO) | 静态数据集 | 简单高效，无需 RM | 数据充足场景 |

## 核心对比

### PPO vs GRPO
- **PPO**: 使用绝对分数，优势 = 实际分 - 预估分
- **GRPO**: 使用相对排序，优势基于组内排名

### Online vs Offline  
- **Online**: 数据动态生成，需要与环境交互
- **Offline**: 使用静态数据集，训练更稳定

## 选型建议

- **快速原型/小规模**: DPO（简单、高效）
- **生产环境/大规模**: GRPO（稳定、可扩展）
- **实时交互场景**: PPO（反馈快）

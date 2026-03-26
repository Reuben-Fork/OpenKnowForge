---
title: "Self-Attention \u4E0E\u5377\u79EF\u7684\u7C7B\u6BD4"
tags:
- attention
- transformer
- deep-learning
created_at: '2026-03-26T18:04:38+00:00'
updated_at: '2026-03-26T18:04:38+00:00'
submitted_at: '2026-03-26T18:04:38+00:00'
date: '2026-03-26'
word_count: 225
image_count: 0
type: note
status: draft
related: []
---

# Self-Attention 与卷积的类比

Self-Attention可以类似一种更高级的卷积操作

对于一个图像，我们可以用一个nxn的卷积核，得到一个和原图像尺寸一样的新图片，这里新图片的每一个像素都经过了一次更新，都有着过去同位置像素和其邻居像素的信息。

Self-Attention的输入是一个[L,D]的序列，输出也是一个[L,D]的序列，新序列中每个元素也都得到了更新，但是相较于卷积，Self-Attention每个元素更新，都用到了整个序列的所有内容，是自己+序列中其他所有元素的加权和。不过利用注意力机制，这个“超级卷积”不是无脑求和，而是有选择的按需分配注意力，比如当前元素是“他“，可能会给上文中”小明“更高的注意力

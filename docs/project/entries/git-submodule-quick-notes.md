---
title: "\u4EE3\u7801\u793A\u4F8B"
tags:
- code-example
- git
- submodule
created_at: '2026-03-26T11:53:34+00:00'
updated_at: '2026-03-26T16:15:57+00:00'
submitted_at: '2026-03-26T16:15:57+00:00'
date: '2026-03-26'
word_count: 51
image_count: 0
type: guide
status: published
related:
- git
---

# 代码示例

### 子模块

在已有项目中添加子模块

```bash
git submodule add <仓库地址> <本地路径>
```

克隆一个包含子模块的项目

```bash
git clone --recursive <仓库地址>
```

将一个已有的项目初始化子模块

```bash
git submodule update --init --recursive
```

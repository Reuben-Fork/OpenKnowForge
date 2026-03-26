# OpenKnowForge

OpenKnowForge 是一个面向个人与团队的知识库工程实践：
通过本地 API 维护 Markdown 笔记与图片资产，把“内容管理 + 版本管理 + 文档发布”串成一条流水线。

## 设计理念

- 内容优先：知识以 Markdown 为核心，便于编辑、审阅与长期保存。
- Git 原生：每次知识变更都可追踪，可协作，可回滚。
- 发布友好：前端基于 VitePress，可直接部署到 GitHub Pages。

## 启动 API

1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

2. 启动本地 API

```bash
python -m uvicorn api.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

## GitHub Pages

项目已内置 GitHub Pages 工作流：`.github/workflows/pages.yml`。

使用步骤：

1. 在仓库设置中启用 Pages，并将 Source 设为 `GitHub Actions`。
2. 推送代码到默认分支（如 `main`）后，工作流会自动构建并部署站点。


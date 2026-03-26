---
title: "OpenKnowForge \u9879\u76EE\u4F7F\u7528\u4E0E GitHub Pages \u90E8\u7F72"
tags:
- guide
- how-to
- openknowforge
- local-dev
- github-pages
- deploy
- vitepress
- ci
created_at: '2026-03-26T00:00:00+00:00'
updated_at: '2026-03-26T16:33:40+00:00'
submitted_at: '2026-03-26T16:33:40+00:00'
date: '2026-03-26'
word_count: 692
image_count: 0
type: guide
status: published
related:
- notes-explorer
- search-index
---

# OpenKnowForge 项目使用与 GitHub Pages 部署

## A. 本地开发与预览

### 1. 准备环境（micromamba）

```bash
micromamba create -y -n openknowforge python=3.11
micromamba run -n openknowforge pip install -r requirements.txt -r requirements-dev.txt
```

### 2. 启动 API

```bash
micromamba run -n openknowforge python -m uvicorn api.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

### 3. 通过 POST /note 写入知识

```bash
curl -X POST http://127.0.0.1:8000/note \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "示例标题",
    "content": "Markdown 内容",
    "tags": ["how-to", "openknowforge"],
    "images": [],
    "type": "guide",
    "status": "published",
    "related": []
  }'
```

写入后会自动生成：
- `docs/project/entries/<slug>.md`
- `docs/public/search-index.json`
- 可能的 git 自动提交（失败不阻塞写入）

### 4. 本地预览笔记站点

```bash
npm install
npm run docs:dev
```

访问：
- `http://127.0.0.1:5173/notes/`
- `http://127.0.0.1:5173/notes/explorer`

### 5. 常见问题

#### Failed to load search index. Create notes via POST /note first.
含义：前端没有拿到 `search-index.json`。
排查顺序：
1. 先确认至少写入过一条笔记（调用一次 `POST /note`）。
2. 确认文件存在：`docs/public/search-index.json`。
3. 用 `npm run docs:dev` 方式启动预览，不要直接 `file://` 打开静态文件。
4. 打开浏览器网络面板，确认 `search-index.json` 返回 200 且内容是 JSON。

### 6. 测试与构建

```bash
micromamba run -n openknowforge python -m pytest -q
npm run docs:build
```

## B. GitHub Pages 部署配置

目标：将本项目的 VitePress Web 站点自动部署到 GitHub Pages。

### 1. 准备仓库

1. 确保代码已推送到 `main` 分支。
2. 仓库根目录需要有 `package.json`，且可执行 `npm run docs:build`。
3. 本项目已内置工作流文件：`.github/workflows/pages.yml`。

### 2. 配置 VitePress base（关键）

如果你使用的是 **项目页**（地址形如 `https://<user>.github.io/<repo>/`），需要在 `docs/.vitepress/config.ts` 中设置：

```ts
export default defineConfig({
  base: '/OpenKnowForge/',
  // ...
})
```

说明：`/OpenKnowForge/` 需替换为你的仓库名。

如果你使用 **用户主页**（`https://<user>.github.io/`）或绑定了自定义域名根路径，可保持默认 `base: '/'`。

### 3. 启用 GitHub Pages

进入仓库：`Settings -> Pages`

- Build and deployment -> Source 选择 `GitHub Actions`

这是必须步骤，否则工作流不会真正发布到 Pages。

### 4. 核对 CI 工作流

本项目默认工作流要点如下（`.github/workflows/pages.yml`）：

- 触发：`push` 到 `main`（也支持手动 `workflow_dispatch`）
- Node：20
- 构建命令：`npm ci` + `npm run docs:build`
- 上传产物目录：`docs/.vitepress/dist`
- 发布动作：`actions/deploy-pages@v4`

可直接复用现有文件，无需另写脚本。

### 5. 触发部署

```bash
git add .
git commit -m "chore: configure github pages deploy"
git push origin main
```

推送后到 `Actions` 页面查看 `Deploy VitePress to GitHub Pages` 是否成功。

### 6. 验证访问

部署成功后访问：

- 项目页：`https://<user>.github.io/<repo>/`
- 本项目示例：`https://reuben-sun.github.io/OpenKnowForge/`

若出现样式或资源 404，优先检查 `base` 配置是否与仓库名一致。

### 7. 常见问题

#### 7.1 页面是空白或资源 404

- 大概率是 `base` 配错
- 确认 `docs/.vitepress/config.ts` 与实际 Pages 路径一致

#### 7.2 Actions 成功但 Pages 没更新

- 检查 `Settings -> Pages -> Source` 是否是 `GitHub Actions`
- 等待 1~3 分钟 CDN 缓存刷新

#### 7.3 推送后没触发流程

- 确认提交分支是 `main`
- 确认 `.github/workflows/pages.yml` 在默认分支中

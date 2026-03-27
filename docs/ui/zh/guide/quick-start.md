# OpenKnowForge 快速开始

## 本地开发

### 启动 API

```bash
python -m uvicorn api.main:app --reload
```

### 本地预览

```bash
npm run docs:dev
```

访问：

- `http://127.0.0.1:5173/notes/`
- `http://127.0.0.1:5173/notes/explorer`

## GitHub Pages 部署

### 1) 启用 GitHub Pages

进入仓库：`Settings -> Pages`

- Build and deployment -> Source 选择 `GitHub Actions`

### 2) 触发部署

每次提交并推送到 `main`，GitHub Actions 会自动触发 Pages 部署。

## 常见问题

### Failed to load search index. Create notes via POST /note first.

这个错误表示前端没拿到 `search-index.json`。建议按顺序排查：

1. 先确认至少创建过一条笔记（调用一次 `POST /note`）。
2. 确认 `docs/public/search-index.json` 已存在。
3. 本地用 `npm run docs:dev` 预览，不要直接 `file://` 打开页面。

### GitHub Pages 页面样式异常或资源 404

1. 检查 `Settings -> Pages -> Source` 是否为 `GitHub Actions`。
2. 检查最近一次 Pages 部署工作流是否成功。
3. 等待 1~3 分钟后强制刷新，排除缓存影响。

### fork 后需要改什么

1. 必做：在 `Settings -> Pages` 将 Source 设为 `GitHub Actions`。
2. 必做：将代码推送到 `main` 以触发自动部署。
3. 可选：设置 `VITEPRESS_GITHUB_REPO` 为你自己的仓库（如 `your-name/your-repo`）。

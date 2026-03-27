# OpenKnowForge Quick Start

## Local Development

### Start API

```bash
python -m uvicorn api.main:app --reload
```

### Local Preview

```bash
npm run docs:dev
```

Open:

- `http://127.0.0.1:5173/en/notes/`
- `http://127.0.0.1:5173/en/notes/explorer`

## GitHub Pages Deployment

### 1) Enable GitHub Pages

In your repo, open `Settings -> Pages`.

- Under Build and deployment, set Source to `GitHub Actions`.

### 2) Trigger deployment

Every commit pushed to `main` will trigger the Pages deployment workflow automatically.

## FAQ

### Failed to load search index. Create notes via POST /note first.

This means the frontend cannot fetch `search-index.json`.

1. Make sure at least one note has been created via `POST /note`.
2. Confirm `docs/public/search-index.json` exists.
3. Use `npm run docs:dev` for preview; do not open the page via `file://`.

### GitHub Pages style is broken or static assets return 404

1. Verify `Settings -> Pages -> Source` is set to `GitHub Actions`.
2. Check the latest Pages deployment workflow status.
3. Wait 1-3 minutes and hard refresh to avoid stale cache.

### What should I change after forking

1. Required: set `Settings -> Pages -> Source` to `GitHub Actions`.
2. Required: push commits to `main` to trigger deployment.
3. Optional: set `VITEPRESS_GITHUB_REPO` to your own repo (for example `your-name/your-repo`).

# Project Structure

```txt
OpenKnowForge/
├── api/
│   ├── main.py
│   └── ingestors/
├── docs/
│   ├── notes/
│   │   ├── index.md
│   │   ├── explorer.md
│   │   └── entries/
│   ├── assets/images/
│   └── .vitepress/
├── scripts/
├── .github/workflows/
├── requirements.txt
└── package.json
```

## Notes Format

Structural pages stay in `docs/notes/` (`index.md` and `explorer.md`).
User-authored notes are stored in `docs/notes/entries/` as Markdown with frontmatter metadata.

```md
---
title: Delaunay Triangulation
tags:
  - geometry
  - computational geometry
date: 2026-03-26
type: concept
status: draft
related:
  - voronoi-diagram
---

# Delaunay Triangulation

Content goes here...
```

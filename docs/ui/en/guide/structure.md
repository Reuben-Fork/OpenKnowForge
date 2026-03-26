# Project Structure

```txt
OpenKnowForge/
├── api/
│   ├── main.py
│   └── ingestors/
├── docs/
│   ├── ui/
│   │   ├── zh/
│   │   ├── en/
│   │   └── assets/images/
│   ├── project/
│   │   ├── entries/
│   │   └── images/
│   └── .vitepress/
├── scripts/
├── .github/workflows/
├── requirements.txt
└── package.json
```

## Notes Format

UI pages are stored in `docs/ui/zh/` and `docs/ui/en/`.
User-authored notes are stored in `docs/project/entries/` as Markdown with frontmatter metadata.
User-uploaded images are stored in `docs/project/images/`.

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

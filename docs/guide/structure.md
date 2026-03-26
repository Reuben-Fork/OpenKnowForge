# Project Structure

```txt
OpenKnowForge/
├── api/
│   ├── main.py
│   └── ingestors/
├── docs/
│   ├── notes/
│   ├── assets/images/
│   └── .vitepress/
├── scripts/
├── .github/workflows/
├── requirements.txt
└── package.json
```

## Notes Format

Each note uses Markdown with frontmatter metadata.

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

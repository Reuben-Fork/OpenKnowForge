# API

## `GET /health`

Returns service health.

### Example

```bash
curl http://127.0.0.1:8000/health
```

## `POST /note`

Creates a note, saves images, updates indexes, and attempts an automatic git commit.

### Request JSON

```json
{
  "title": "Delaunay Triangulation",
  "content": "Markdown content here...",
  "tags": ["geometry", "algorithm"],
  "images": ["https://example.com/image.png"],
  "type": "concept",
  "status": "draft",
  "related": ["voronoi-diagram"]
}
```

### Example

```bash
curl -X POST http://127.0.0.1:8000/note \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Delaunay Triangulation",
    "content": "Dual of Voronoi diagrams.",
    "tags": ["geometry", "computational-geometry"],
    "images": [],
    "type": "concept",
    "status": "draft",
    "related": ["voronoi-diagram"]
  }'
```

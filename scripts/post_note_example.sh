#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"

curl -X POST "${API_URL}/note" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Delaunay Triangulation",
    "content": "Delaunay triangulation maximizes the minimum angle of all the angles of the triangles in the triangulation.",
    "tags": ["geometry", "computational-geometry"],
    "images": [],
    "type": "concept",
    "status": "draft",
    "related": ["voronoi-diagram"]
  }'

echo

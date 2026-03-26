# API Guide

This guide follows: create -> search -> update -> delete.
Default service endpoint: `http://127.0.0.1:8000`.

## `GET /health`

Check whether the API is reachable.

```bash
curl http://127.0.0.1:8000/health
```

## 1) Create note `POST /note`

```bash
curl -X POST http://127.0.0.1:8000/note \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "KL Divergence",
    "content": "KL divergence measures the difference between distributions.",
    "tags": ["math", "information-theory"],
    "images": [],
    "type": "concept",
    "status": "published",
    "related": [],
    "submitted_at": "2026-03-26T10:00:00+00:00"
  }'
```

Key fields in response:

- `slug`: unique note id used for read/update/delete
- `created_at`: creation time
- `updated_at`: last edited time
- `submitted_at`: submission time for this request
- `git.hash`: auto-commit hash
- `git.committed_at`: git commit time

## 2) Search notes `GET /notes/search`

### Search by keyword

Matches title, excerpt, and tags. Results are sorted by `updated_at` (descending).

```bash
curl "http://127.0.0.1:8000/notes/search?q=KL&limit=20"
```

### Filter by tag

```bash
curl "http://127.0.0.1:8000/notes/search?tag=math&limit=20"
```

### Keyword + tag

```bash
curl "http://127.0.0.1:8000/notes/search?q=divergence&tag=information-theory&limit=20"
```

## 3) Update note `PUT /note/{slug}`

Updates the note referenced by `slug`.
`updated_at` is refreshed from `submitted_at` (or server current time when omitted).

```bash
curl -X PUT http://127.0.0.1:8000/note/<slug> \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Formula Example",
    "content": "Updated content",
    "tags": ["math", "formula"],
    "status": "published",
    "submitted_at": "2026-03-26T12:30:00+00:00"
  }'
```

## 4) Delete note `DELETE /note/{slug}`

Deletes the note file and removes local image assets referenced in its body (`/assets/images/...`).
The system then rebuilds indexes and writes a git commit record.

```bash
curl -X DELETE http://127.0.0.1:8000/note/<slug>
```

Key fields in response:

- `slug`
- `title`
- `deleted_at`
- `note_path`
- `deleted_images`
- `git.hash`

## Extra: read and list

Read one note:

```bash
curl http://127.0.0.1:8000/note/openknowforge
```

List all notes ordered by last edited time:

```bash
curl http://127.0.0.1:8000/notes
```

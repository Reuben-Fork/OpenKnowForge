from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import yaml

from api.ingestors.base import BaseIngestor

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / "docs"
NOTES_DIR = DOCS_DIR / "notes"
IMAGES_DIR = DOCS_DIR / "assets" / "images"
PUBLIC_DIR = DOCS_DIR / ".vitepress" / "public"
NOTES_INDEX_PATH = NOTES_DIR / "index.md"
SEARCH_INDEX_PATH = PUBLIC_DIR / "search-index.json"

DATA_URL_PATTERN = re.compile(r"^data:(?P<mime>[-\w.]+/[-\w.+]+);base64,(?P<data>.+)$")
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class SavedImage:
    markdown_path: str
    filesystem_path: Path


class NoteIngestor(BaseIngestor):
    async def ingest(self, data: dict[str, Any]) -> dict[str, Any]:
        self._ensure_dirs()

        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("title is required")

        content = str(data.get("content", "")).strip()
        tags = self._normalize_list(data.get("tags"))
        related = self._normalize_list(data.get("related"))
        note_type = str(data.get("note_type", "note")).strip() or "note"
        status = str(data.get("status", "draft")).strip() or "draft"

        slug = self._build_note_slug(title)
        saved_images = await self._save_images(data.get("images") or [], slug)
        note_path = self._write_note(
            slug=slug,
            title=title,
            content=content,
            tags=tags,
            related=related,
            note_type=note_type,
            status=status,
            images=saved_images,
        )

        self._rebuild_notes_index()
        self._rebuild_search_index()

        commit = self._git_commit(slug)

        return {
            "slug": slug,
            "note_path": str(note_path.relative_to(ROOT_DIR)),
            "image_count": len(saved_images),
            "image_paths": [img.markdown_path for img in saved_images],
            "git": commit,
        }

    def _ensure_dirs(self) -> None:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    def _normalize_list(self, value: Any) -> list[str]:
        if not value:
            return []
        if not isinstance(value, list):
            return [str(value).strip()] if str(value).strip() else []
        normalized: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized

    def _build_note_slug(self, title: str) -> str:
        # Keep file naming deterministic and URL-friendly.
        slug = title.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug:
            slug = "note"

        candidate = slug
        counter = 2
        while (NOTES_DIR / f"{candidate}.md").exists():
            candidate = f"{slug}-{counter}"
            counter += 1
        return candidate

    async def _save_images(self, images: list[str], slug: str) -> list[SavedImage]:
        saved: list[SavedImage] = []
        for index, image_ref in enumerate(images, start=1):
            image_ref = str(image_ref).strip()
            if not image_ref:
                continue

            raw_bytes, suffix = await self._resolve_image_bytes(image_ref)
            digest = hashlib.sha256(raw_bytes).hexdigest()[:12]
            filename = f"{slug}-{index}-{digest}{suffix}"
            target = IMAGES_DIR / filename
            target.write_bytes(raw_bytes)
            saved.append(
                SavedImage(
                    markdown_path=f"/assets/images/{filename}",
                    filesystem_path=target,
                )
            )
        return saved

    async def _resolve_image_bytes(self, image_ref: str) -> tuple[bytes, str]:
        data_url_match = DATA_URL_PATTERN.match(image_ref)
        if data_url_match:
            mime = data_url_match.group("mime")
            raw = base64.b64decode(data_url_match.group("data"))
            return raw, self._suffix_from_mime(mime)

        if image_ref.startswith("http://") or image_ref.startswith("https://"):
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(image_ref)
                response.raise_for_status()
                mime = response.headers.get("content-type", "").split(";")[0].strip()
                suffix = self._suffix_from_mime(mime)
                if suffix == ".bin":
                    parsed = urlparse(image_ref)
                    url_suffix = Path(parsed.path).suffix
                    if url_suffix:
                        suffix = url_suffix
                return response.content, suffix

        try:
            raw = base64.b64decode(image_ref, validate=True)
            return raw, ".png"
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "images entries must be data URLs, HTTP(S) URLs, or base64 strings"
            ) from exc

    def _suffix_from_mime(self, mime: str) -> str:
        mime_to_suffix = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "image/svg+xml": ".svg",
            "image/avif": ".avif",
        }
        return mime_to_suffix.get(mime, ".bin")

    def _write_note(
        self,
        slug: str,
        title: str,
        content: str,
        tags: list[str],
        related: list[str],
        note_type: str,
        status: str,
        images: list[SavedImage],
    ) -> Path:
        today = datetime.now(timezone.utc).date().isoformat()
        frontmatter = {
            "title": title,
            "tags": tags,
            "date": today,
            "type": note_type,
            "status": status,
            "related": related,
        }

        image_lines: list[str] = []
        for img in images:
            image_lines.append(f'<img src="{img.markdown_path}" alt="{title}" loading="lazy" />')

        body_parts = [
            "# " + title,
            "",
            content if content else "",
        ]
        if image_lines:
            body_parts.extend(["", "## Images", "", *image_lines])

        frontmatter_block = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False).strip() + "\n---"
        markdown = frontmatter_block + "\n\n" + "\n".join(body_parts).rstrip() + "\n"

        note_path = NOTES_DIR / f"{slug}.md"
        note_path.write_text(markdown, encoding="utf-8")
        return note_path

    def _rebuild_notes_index(self) -> None:
        notes = self._collect_notes()
        lines: list[str] = [
            "---",
            "title: Notes",
            "---",
            "",
            "# Notes",
            "",
            "Auto-generated note catalog.",
            "",
            "Use [Explore Notes](/notes/explorer) for tag filtering and instant search.",
            "",
        ]

        if not notes:
            lines.append("No notes yet.")
            NOTES_INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

        lines.extend(["## By Date", ""])
        for note in notes:
            lines.append(
                f"- [{note['title']}]({note['link']}) - `{note['date']}`"
            )

        tag_map: dict[str, list[dict[str, str]]] = {}
        for note in notes:
            for tag in note["tags"]:
                tag_map.setdefault(tag, []).append(note)

        lines.extend(["", "## By Tag", ""])
        if not tag_map:
            lines.append("No tags yet.")
        else:
            for tag in sorted(tag_map):
                lines.append(f"### {tag}")
                for note in tag_map[tag]:
                    lines.append(f"- [{note['title']}]({note['link']})")
                lines.append("")

        NOTES_INDEX_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _rebuild_search_index(self) -> None:
        notes = self._collect_notes(include_excerpt=True)
        payload = {"generatedAt": datetime.now(timezone.utc).isoformat(), "notes": notes}
        SEARCH_INDEX_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _collect_notes(self, include_excerpt: bool = False) -> list[dict[str, Any]]:
        notes: list[dict[str, Any]] = []
        for path in sorted(NOTES_DIR.glob("*.md")):
            if path.name == "index.md":
                continue
            text = path.read_text(encoding="utf-8")
            frontmatter = self._extract_frontmatter(text)
            title = str(frontmatter.get("title") or path.stem)
            date = str(frontmatter.get("date") or "")
            tags = frontmatter.get("tags") or []
            if not isinstance(tags, list):
                tags = [str(tags)]

            entry: dict[str, Any] = {
                "title": title,
                "date": date,
                "tags": [str(tag) for tag in tags],
                "link": f"/notes/{path.stem}",
            }

            if include_excerpt:
                body = FRONTMATTER_PATTERN.sub("", text).strip()
                excerpt = re.sub(r"\s+", " ", body)
                entry["excerpt"] = excerpt[:200]

            notes.append(entry)

        notes.sort(key=lambda item: item.get("date", ""), reverse=True)
        return notes

    def _extract_frontmatter(self, text: str) -> dict[str, Any]:
        match = FRONTMATTER_PATTERN.match(text)
        if not match:
            return {}
        try:
            parsed = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _git_commit(self, slug: str) -> dict[str, Any]:
        add = subprocess.run(
            ["git", "add", "docs/notes", "docs/assets/images", "docs/.vitepress/public/search-index.json"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if add.returncode != 0:
            return {
                "committed": False,
                "error": add.stderr.strip() or "git add failed",
            }

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT_DIR,
            check=False,
        )
        if diff.returncode == 0:
            return {"committed": False, "message": "No staged changes"}

        commit = subprocess.run(
            ["git", "commit", "-m", f"docs(kb): add note {slug}"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        if commit.returncode != 0:
            return {
                "committed": False,
                "error": commit.stderr.strip() or "git commit failed",
            }

        return {
            "committed": True,
            "message": commit.stdout.strip().splitlines()[-1] if commit.stdout.strip() else "ok",
        }

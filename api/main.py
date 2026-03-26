from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.ingestors.note_ingestor import NoteIngestor


class NotePayload(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="")
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    type: str = Field(default="note")
    status: str = Field(default="draft")
    related: list[str] = Field(default_factory=list)


app = FastAPI(title="OpenKnowForge API", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/note")
async def create_note(payload: NotePayload) -> dict[str, object]:
    ingestor = NoteIngestor()
    payload_data = payload.model_dump()
    payload_data["note_type"] = payload_data.pop("type")
    try:
        result = await ingestor.ingest(payload_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive handling
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
    return {"ok": True, "result": result}

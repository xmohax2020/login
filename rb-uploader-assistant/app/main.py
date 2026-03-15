from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.db.sqlite import (
    VALID_STATUSES,
    get_audit_logs,
    get_design,
    init_db,
    list_designs,
    update_metadata,
    update_status,
)
from app.services.metadata_pipeline import generate_metadata, validate_metadata

app = FastAPI(title="rb-uploader-assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).resolve().parent / "web"
init_db()


class StatusPayload(BaseModel):
    status: str


class MetadataPayload(BaseModel):
    title: str = Field(min_length=20, max_length=80)
    description: str = Field(min_length=1)
    tags: list[str] = Field(min_length=10, max_length=20)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/designs")
def designs(status: str | None = Query(default=None)) -> list[dict]:
    rows = list_designs(status=status)
    for row in rows:
        row["tags"] = json.loads(row["tags"]) if row.get("tags") else []
    return rows


@app.get("/designs/{design_id}")
def design_by_id(design_id: int) -> dict:
    item = get_design(design_id)
    if item is None:
        raise HTTPException(status_code=404, detail="design not found")
    item["tags"] = json.loads(item["tags"]) if item.get("tags") else []
    return item


@app.post("/designs/{design_id}/status")
def set_design_status(design_id: int, payload: StatusPayload) -> dict[str, str]:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"invalid status. allowed: {sorted(VALID_STATUSES)}")
    if get_design(design_id) is None:
        raise HTTPException(status_code=404, detail="design not found")
    update_status(design_id, payload.status)
    return {"result": "ok"}


@app.post("/designs/{design_id}/metadata")
def set_metadata(design_id: int, payload: MetadataPayload) -> dict[str, str]:
    if get_design(design_id) is None:
        raise HTTPException(status_code=404, detail="design not found")
    errors = validate_metadata(payload.model_dump())
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    update_metadata(design_id, payload.title, payload.description, payload.tags)
    return {"result": "ok"}


@app.post("/designs/{design_id}/regenerate-metadata")
def regenerate_metadata(design_id: int, niche: str = "general") -> dict:
    item = get_design(design_id)
    if item is None:
        raise HTTPException(status_code=404, detail="design not found")
    generated = generate_metadata(Path(item["original_file"]), niche=niche)
    update_metadata(design_id, generated["title"], generated["description"], generated["tags"])
    return {"result": "ok", "generated": generated}


@app.get("/audit-logs")
def audit_logs(limit: int = 100) -> list[dict]:
    return get_audit_logs(limit=min(max(limit, 1), 500))


@app.get("/")
def web_index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

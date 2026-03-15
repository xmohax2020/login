from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.db.sqlite import get_design, init_db, list_designs, update_status

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/designs")
def designs() -> list[dict]:
    rows = list_designs()
    for row in rows:
        raw_tags = row.get("tags")
        row["tags"] = json.loads(raw_tags) if raw_tags else []
    return rows


@app.get("/designs/{design_id}")
def design_by_id(design_id: int) -> dict:
    item = get_design(design_id)
    if item is None:
        raise HTTPException(status_code=404, detail="design not found")
    raw_tags = item.get("tags")
    item["tags"] = json.loads(raw_tags) if raw_tags else []
    return item


@app.post("/designs/{design_id}/status")
def set_design_status(design_id: int, payload: StatusPayload) -> dict[str, str]:
    if payload.status not in {"draft", "ready", "uploaded", "published"}:
        raise HTTPException(status_code=400, detail="invalid status")
    update_status(design_id, payload.status)
    return {"result": "ok"}


@app.get("/")
def web_index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

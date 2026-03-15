from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "app.db"
VALID_STATUSES = {"draft", "ready", "uploaded", "published", "duplicate"}


def get_conn(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | None = None) -> None:
    with get_conn(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                original_file TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                title TEXT,
                description TEXT,
                tags TEXT,
                collection TEXT,
                maturity TEXT DEFAULT 'safe',
                status TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                design_id INTEGER NOT NULL,
                size_name TEXT NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(design_id) REFERENCES designs(id)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                design_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_designs_status ON designs(status);
            CREATE INDEX IF NOT EXISTS idx_designs_sha256 ON designs(sha256);
            """
        )


def _add_audit(conn: sqlite3.Connection, design_id: int | None, action: str, details: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO audit_logs (design_id, action, details) VALUES (?, ?, ?)",
        (design_id, action, json.dumps(details, ensure_ascii=False)),
    )


def upsert_design(record: dict[str, Any], db_path: Path | None = None) -> int:
    with get_conn(db_path) as conn:
        existing = conn.execute("SELECT id FROM designs WHERE slug = ?", (record["slug"],)).fetchone()
        tags_json = json.dumps(record.get("tags", []), ensure_ascii=False)

        if existing:
            conn.execute(
                """
                UPDATE designs
                SET original_file = ?, sha256 = ?, title = ?, description = ?,
                    tags = ?, collection = ?, maturity = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE slug = ?
                """,
                (
                    record["original_file"],
                    record["sha256"],
                    record.get("title"),
                    record.get("description"),
                    tags_json,
                    record.get("collection"),
                    record.get("maturity", "safe"),
                    record.get("status", "draft"),
                    record["slug"],
                ),
            )
            design_id = int(existing["id"])
            _add_audit(conn, design_id, "design.updated", {"slug": record["slug"]})
            return design_id

        cur = conn.execute(
            """
            INSERT INTO designs (slug, original_file, sha256, title, description, tags, collection, maturity, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["slug"],
                record["original_file"],
                record["sha256"],
                record.get("title"),
                record.get("description"),
                tags_json,
                record.get("collection"),
                record.get("maturity", "safe"),
                record.get("status", "draft"),
            ),
        )
        design_id = int(cur.lastrowid)
        _add_audit(conn, design_id, "design.created", {"slug": record["slug"]})
        return design_id


def has_sha256(sha256: str, db_path: Path | None = None) -> bool:
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT id FROM designs WHERE sha256 = ? LIMIT 1", (sha256,)).fetchone()
    return bool(row)


def replace_assets(design_id: int, assets: list[dict[str, Any]], db_path: Path | None = None) -> None:
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM assets WHERE design_id = ?", (design_id,))
        for asset in assets:
            conn.execute(
                "INSERT INTO assets (design_id, size_name, width, height, file_path) VALUES (?, ?, ?, ?, ?)",
                (design_id, asset["size_name"], asset["width"], asset["height"], asset["file_path"]),
            )
        _add_audit(conn, design_id, "assets.replaced", {"count": len(assets)})


def list_designs(status: str | None = None, db_path: Path | None = None) -> list[dict[str, Any]]:
    with get_conn(db_path) as conn:
        if status:
            rows = conn.execute("SELECT * FROM designs WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM designs ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_design(design_id: int, db_path: Path | None = None) -> dict[str, Any] | None:
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM designs WHERE id = ?", (design_id,)).fetchone()
        if not row:
            return None
        design = dict(row)
        assets = conn.execute("SELECT * FROM assets WHERE design_id = ?", (design_id,)).fetchall()
        design["assets"] = [dict(a) for a in assets]
    return design


def update_status(design_id: int, status: str, db_path: Path | None = None) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status '{status}'")
    with get_conn(db_path) as conn:
        conn.execute("UPDATE designs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, design_id))
        _add_audit(conn, design_id, "design.status_changed", {"status": status})


def update_metadata(design_id: int, title: str, description: str, tags: list[str], db_path: Path | None = None) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            """
            UPDATE designs SET title = ?, description = ?, tags = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (title, description, json.dumps(tags, ensure_ascii=False), design_id),
        )
        _add_audit(conn, design_id, "design.metadata_updated", {"title": title})


def get_audit_logs(limit: int = 100, db_path: Path | None = None) -> list[dict[str, Any]]:
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]

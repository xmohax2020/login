from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "app.db"


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
            """
        )


def upsert_design(record: dict[str, Any], db_path: Path | None = None) -> int:
    with get_conn(db_path) as conn:
        existing = conn.execute(
            "SELECT id FROM designs WHERE slug = ?", (record["slug"],)
        ).fetchone()

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
            return int(existing["id"])

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
        return int(cur.lastrowid)


def replace_assets(design_id: int, assets: list[dict[str, Any]], db_path: Path | None = None) -> None:
    with get_conn(db_path) as conn:
        conn.execute("DELETE FROM assets WHERE design_id = ?", (design_id,))
        for asset in assets:
            conn.execute(
                """
                INSERT INTO assets (design_id, size_name, width, height, file_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (design_id, asset["size_name"], asset["width"], asset["height"], asset["file_path"]),
            )


def list_designs(db_path: Path | None = None) -> list[dict[str, Any]]:
    with get_conn(db_path) as conn:
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
    with get_conn(db_path) as conn:
        conn.execute(
            "UPDATE designs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, design_id),
        )

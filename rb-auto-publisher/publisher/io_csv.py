from __future__ import annotations

import csv
from pathlib import Path

from publisher.models import DesignRow


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_designs(csv_path: Path) -> list[DesignRow]:
    rows: list[DesignRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                DesignRow(
                    file_path=Path(row["file_path"]),
                    title=row["title"],
                    description=row["description"],
                    tags=row["tags"],
                    maturity=row.get("maturity", "safe"),
                    is_public=parse_bool(row.get("is_public", "true")),
                    default_status=row.get("default_status", "draft"),
                )
            )
    return rows

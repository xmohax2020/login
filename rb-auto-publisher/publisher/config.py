from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PublisherConfig:
    base_url: str
    upload_path: str
    state_file: Path
    headless: bool
    slow_mo_ms: int
    selectors: dict[str, str]


def load_config(path: Path) -> PublisherConfig:
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PublisherConfig(
        base_url=data["base_url"],
        upload_path=data["upload_path"],
        state_file=Path(data["state_file"]),
        headless=bool(data.get("headless", False)),
        slow_mo_ms=int(data.get("slow_mo_ms", 0)),
        selectors=dict(data["selectors"]),
    )

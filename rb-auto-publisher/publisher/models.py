from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DesignRow:
    file_path: Path
    title: str
    description: str
    tags: str
    maturity: str = "safe"
    is_public: bool = True
    default_status: str = "draft"

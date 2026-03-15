#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import csv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.metadata_pipeline import validate_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate metadata CSV")
    parser.add_argument("--metadata", default="data/designs.csv")
    args = parser.parse_args()

    root = ROOT_DIR
    csv_path = root / args.metadata
    if not csv_path.exists():
        raise SystemExit(f"metadata file not found: {csv_path}")

    invalid = 0
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            meta = {
                "title": row.get("title", ""),
                "description": row.get("description", ""),
                "tags": [t.strip() for t in row.get("tags", "").split(",") if t.strip()],
            }
            errors = validate_metadata(meta)
            if errors:
                invalid += 1
                print(f"[INVALID] {row.get('slug')}: {', '.join(errors)}")

    if invalid:
        print(f"Validation failed for {invalid} design(s)")
        raise SystemExit(1)

    print("Validation passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.sqlite import has_sha256, init_db, replace_assets, upsert_design
from app.services.dedupe import file_sha256
from app.services.image_pipeline import load_sizes, render_sizes
from app.services.metadata_pipeline import generate_metadata, slugify, validate_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare design files for rb-uploader-assistant")
    parser.add_argument("--input", default="input_designs", help="Input folder for source designs")
    parser.add_argument("--output", default="exports", help="Output folder for generated sizes")
    parser.add_argument("--metadata", default="data/designs.csv", help="CSV path for generated metadata")
    parser.add_argument("--sizes", default="configs/sizes.yaml", help="YAML config for target sizes")
    parser.add_argument("--niche", default="general", help="Niche label used in metadata generation")
    parser.add_argument("--skip-duplicates", action="store_true", help="Skip files with existing sha256 hash")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = ROOT_DIR / args.input
    output_dir = ROOT_DIR / args.output
    csv_path = ROOT_DIR / args.metadata
    sizes_path = ROOT_DIR / args.sizes

    init_db()
    sizes = load_sizes(sizes_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    supported_ext = {".png", ".jpg", ".jpeg", ".webp"}

    for file_path in sorted(input_dir.glob("*")):
        if file_path.suffix.lower() not in supported_ext:
            continue

        slug = slugify(file_path.stem)
        sha = file_sha256(file_path)

        if args.skip_duplicates and has_sha256(sha):
            rows.append(
                {
                    "slug": slug,
                    "original_file": str(file_path),
                    "sha256": sha,
                    "title": "",
                    "description": "",
                    "tags": [],
                    "collection": args.niche,
                    "maturity": "safe",
                    "status": "duplicate",
                    "validation_errors": "duplicate sha256 detected",
                }
            )
            continue

        assets = render_sizes(file_path, output_dir / slug, sizes)
        metadata = generate_metadata(file_path, niche=args.niche)
        errors = validate_metadata(metadata)
        status = "ready" if not errors else "draft"

        record = {
            "slug": slug,
            "original_file": str(file_path),
            "sha256": sha,
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "collection": metadata["collection"],
            "maturity": metadata["maturity"],
            "status": status,
        }
        design_id = upsert_design(record)
        replace_assets(design_id, assets)
        rows.append({**record, "validation_errors": "|".join(errors)})

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "slug",
                "original_file",
                "sha256",
                "title",
                "description",
                "tags",
                "collection",
                "maturity",
                "status",
                "validation_errors",
            ],
        )
        writer.writeheader()
        for row in rows:
            row["tags"] = ",".join(row["tags"])
            writer.writerow(row)

    print(f"Prepared {len(rows)} design(s). Metadata saved to {csv_path}")


if __name__ == "__main__":
    main()

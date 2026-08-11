#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from publisher.config import load_config
from publisher.io_csv import load_designs
from publisher.redbubble import run_publish


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate Redbubble upload/publish workflow")
    parser.add_argument("--config", default="configs/redbubble.yaml")
    parser.add_argument("--csv", default="data/designs.csv")
    parser.add_argument("--mode", choices=["dry-run", "publish"], default="dry-run")
    parser.add_argument("--out", default="data/results.json")
    args = parser.parse_args()

    config = load_config(ROOT / args.config)
    designs = load_designs(ROOT / args.csv)
    results = run_publish(config, designs, mode=args.mode)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    ok_count = sum(1 for r in results if r.get("ok"))
    print(f"Done: {ok_count}/{len(results)} succeeded. Results => {out_path}")


if __name__ == "__main__":
    main()

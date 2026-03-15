#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from publisher.redbubble import save_login_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Save login session for automated publishing")
    parser.add_argument("--base-url", default="https://www.redbubble.com")
    parser.add_argument("--state-file", default="data/state.json")
    args = parser.parse_args()

    save_login_state(args.base_url, ROOT / args.state_file)
    print(f"Session saved: {ROOT / args.state_file}")


if __name__ == "__main__":
    main()

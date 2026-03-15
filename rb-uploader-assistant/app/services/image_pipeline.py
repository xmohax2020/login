from __future__ import annotations

from pathlib import Path

import yaml
from PIL import Image


def load_sizes(config_path: Path) -> list[dict]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return data.get("sizes", [])


def render_sizes(source_file: Path, export_dir: Path, sizes: list[dict]) -> list[dict]:
    export_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with Image.open(source_file).convert("RGBA") as img:
        for size in sizes:
            width = int(size["width"])
            height = int(size["height"])
            canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            ratio = min(width / img.width, height / img.height)
            resized = img.resize((int(img.width * ratio), int(img.height * ratio)))
            x = (width - resized.width) // 2
            y = (height - resized.height) // 2
            canvas.paste(resized, (x, y), resized)

            out_path = export_dir / f"{size['name']}.png"
            canvas.save(out_path, format="PNG")
            results.append(
                {
                    "size_name": size["name"],
                    "width": width,
                    "height": height,
                    "file_path": str(out_path),
                }
            )

    return results

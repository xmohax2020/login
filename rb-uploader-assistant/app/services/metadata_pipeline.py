from __future__ import annotations

import re
from pathlib import Path


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\-\s_]", "", name).strip().lower()
    return re.sub(r"[\s_]+", "-", slug)


def generate_metadata(file_path: Path, niche: str = "general") -> dict:
    base_name = file_path.stem.replace("_", " ").replace("-", " ").strip()
    title = f"{base_name.title()} | {niche.title()} Design"
    description = (
        f"A clean {niche} themed artwork inspired by '{base_name}'. "
        "Optimized for print-on-demand products and crafted for everyday style."
    )
    tag_roots = [w.lower() for w in base_name.split() if len(w) > 2][:8]
    tags = list(dict.fromkeys(tag_roots + [niche.lower(), "redbubble", "printondemand", "gift"]))[:20]
    filler = [f"{niche.lower()}-art", "digital-art", "creative", "trendy", "style", "unique", "design", "illustration"]
    i = 0
    while len(tags) < 10:
        tags.append(filler[i % len(filler)])
        tags = list(dict.fromkeys(tags))
        i += 1
    tags = tags[:20]
    return {
        "title": title[:80],
        "description": description,
        "tags": tags,
        "collection": niche,
        "maturity": "safe",
    }


def validate_metadata(meta: dict) -> list[str]:
    errors: list[str] = []
    title = meta.get("title", "")
    tags = meta.get("tags", [])
    description = meta.get("description", "")

    if not (20 <= len(title) <= 80):
        errors.append("title must be between 20 and 80 chars")
    if not description.strip():
        errors.append("description is required")
    if not (10 <= len(tags) <= 20):
        errors.append("tags count must be between 10 and 20")
    if len(set(tags)) != len(tags):
        errors.append("tags must be unique")

    return errors

"""Convert short_answer from a bullet-point string to an array of strings.

Reads sks_catalog.json, splits each short_answer on bullet-point markers,
and writes the result back as a list.

Usage:
    python scripts/split_short_answers.py       # from backend/
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_FILE = SCRIPT_DIR / "sks_catalog.json"


def split_bullets(text: str) -> list[str]:
    """Split a bullet-point string into a list of individual points."""
    if not text.strip():
        return []

    # Split on lines starting with "- " (the format produced by GPT)
    items: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Strip leading bullet marker
        cleaned = re.sub(r"^[-•–]\s*", "", line).strip()
        if cleaned:
            items.append(cleaned)

    return items


def main() -> None:
    with open(CATALOG_FILE, "r", encoding="utf-8") as fh:
        catalog: list[dict] = json.load(fh)

    converted = 0
    for entry in catalog:
        sa = entry.get("short_answer", "")
        if isinstance(sa, str):
            entry["short_answer"] = split_bullets(sa)
            converted += 1

    with open(CATALOG_FILE, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=2)

    print(f"Converted {converted} short_answer fields to arrays in {CATALOG_FILE}")

    # Quick summary
    lengths = [len(e["short_answer"]) for e in catalog]
    print(f"  Min bullets: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.1f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Seed the PostgreSQL database with cards from sks_catalog.json.

Usage:
    python -m scripts.seed_database              # default: scripts/sks_catalog.json
    python -m scripts.seed_database --file path/to/catalog.json

The script is idempotent: existing cards (matched by topic + question_number)
are skipped.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Allow running from the backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from card.db.card_table import CardRow  # noqa: E402
from database import Base, async_session_factory, engine  # noqa: E402
from scheduling.db.scheduling_table import CardSchedulingInfoRow  # noqa: E402


DEFAULT_CATALOG = Path(__file__).resolve().parent / "sks_catalog.json"


def _build_card_id(topic: str, question_number: int) -> str:
    """Deterministic card ID so re-runs don't duplicate."""
    return f"{topic}_{question_number}"


async def seed(catalog_path: Path) -> None:
    """Read the JSON catalog and insert cards + scheduling info."""
    with open(catalog_path, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    print(f"Loaded {len(entries)} entries from {catalog_path}")

    # Ensure tables exist (in case Alembic hasn't been run yet)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        inserted = 0
        skipped = 0

        for entry in entries:
            card_id = _build_card_id(entry["topic"], entry["question_number"])

            # Check if already exists
            existing = await session.get(CardRow, card_id)
            if existing is not None:
                skipped += 1
                continue

            # Build image dicts for JSON columns
            q_images = [
                {"storage_key": img, "image_id": str(uuid4()), "alt_text": None}
                for img in entry.get("question_images", [])
            ]
            a_images = [
                {"storage_key": img, "image_id": str(uuid4()), "alt_text": None}
                for img in entry.get("answer_images", [])
            ]

            card_row = CardRow(
                card_id=card_id,
                front_text=entry["question"],
                front_images=q_images,
                answer_text=entry["answer"],
                answer_images=a_images,
                short_answer=entry.get("short_answer", []),
                tags=[entry["topic"]],
            )
            session.add(card_row)

            # Create a NEW scheduling info for the card
            from datetime import datetime, timezone

            sched_row = CardSchedulingInfoRow(
                user_id="seed-user",
                card_id=card_id,
                state=0,  # NEW
                stability=0.0,
                difficulty=0.0,
                elapsed_days=0,
                scheduled_days=0,
                reps=0,
                lapses=0,
                due=datetime.now(timezone.utc),
                last_review=None,
            )
            session.add(sched_row)

            inserted += 1

        await session.commit()
        print(f"Done: {inserted} inserted, {skipped} skipped (already exist)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed SKS cards into PostgreSQL")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Path to sks_catalog.json",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: catalog file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(seed(args.file))


if __name__ == "__main__":
    main()

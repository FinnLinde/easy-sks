#!/usr/bin/env python3
"""Seed the database with bundled SKS cards and navigation tasks.

Usage:
    python -m scripts.seed              # idempotent
    python -m scripts.seed --if-empty   # skip entirely if cards already exist
    python -m scripts.seed --reset      # truncate and reseed (destructive)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select, func

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from card.db.card_table import CardRow  # noqa: E402
from database import async_session_factory  # noqa: E402
from navigation.db.navigation_tables import NavigationTaskRow  # noqa: E402
from scheduling.db.scheduling_table import CardSchedulingInfoRow  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent
CARDS_CATALOG = SCRIPTS_DIR / "sks_catalog.json"
NAVIGATION_CATALOG = SCRIPTS_DIR / "sks_navigation_catalog.json"


def _build_card_id(topic: str, question_number: int) -> str:
    return f"{topic}_{question_number}"


def _build_task_id(sheet_number: int, task_number: int) -> str:
    return f"nav_{sheet_number}_{task_number}"


async def _seed_cards(session, *, reset: bool) -> tuple[int, int]:
    if not CARDS_CATALOG.exists():
        print(f"  [cards] {CARDS_CATALOG} not found — skipping")
        return 0, 0

    with open(CARDS_CATALOG, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    if reset:
        await session.execute(CardSchedulingInfoRow.__table__.delete())
        await session.execute(CardRow.__table__.delete())

    inserted = 0
    skipped = 0
    for entry in entries:
        card_id = _build_card_id(entry["topic"], entry["question_number"])
        if not reset and await session.get(CardRow, card_id) is not None:
            skipped += 1
            continue

        q_images = [
            {"storage_key": img, "image_id": str(uuid4()), "alt_text": None}
            for img in entry.get("question_images", [])
        ]
        a_images = [
            {"storage_key": img, "image_id": str(uuid4()), "alt_text": None}
            for img in entry.get("answer_images", [])
        ]

        session.add(
            CardRow(
                card_id=card_id,
                front_text=entry["question"],
                front_images=q_images,
                answer_text=entry["answer"],
                answer_images=a_images,
                short_answer=entry.get("short_answer", []),
                tags=[entry["topic"]],
                exam_sheets=entry.get("exam_sheets", []),
            )
        )
        session.add(
            CardSchedulingInfoRow(
                card_id=card_id,
                state=0,
                stability=0.0,
                difficulty=0.0,
                elapsed_days=0,
                scheduled_days=0,
                reps=0,
                lapses=0,
                due=datetime.now(timezone.utc),
                last_review=None,
            )
        )
        inserted += 1

    return inserted, skipped


async def _seed_navigation(session, *, reset: bool) -> tuple[int, int]:
    if not NAVIGATION_CATALOG.exists():
        print(f"  [navigation] {NAVIGATION_CATALOG} not found — skipping")
        return 0, 0

    with open(NAVIGATION_CATALOG, encoding="utf-8") as f:
        sheets: list[dict] = json.load(f)

    if reset:
        await session.execute(NavigationTaskRow.__table__.delete())

    inserted = 0
    updated = 0
    for sheet in sheets:
        sheet_number = sheet["sheet_number"]
        for task in sheet["tasks"]:
            task_id = _build_task_id(sheet_number, task["task_number"])
            sub_questions = [
                {"text": sq["text"], "points": sq["points"]}
                for sq in task["sub_questions"]
            ]
            sol = task["solution"]
            solution_text = sol.get("solution_markdown", sol["full_text"])
            key_answers = sol["key_answers"]

            if not reset:
                existing = await session.get(NavigationTaskRow, task_id)
                if existing is not None:
                    existing.points = task["points"]
                    existing.context = task["context"]
                    existing.sub_questions = sub_questions
                    existing.solution_text = solution_text
                    existing.key_answers = key_answers
                    updated += 1
                    continue

            session.add(
                NavigationTaskRow(
                    task_id=task_id,
                    sheet_number=sheet_number,
                    task_number=task["task_number"],
                    points=task["points"],
                    context=task["context"],
                    sub_questions=sub_questions,
                    solution_text=solution_text,
                    key_answers=key_answers,
                )
            )
            inserted += 1

    return inserted, updated


async def run(*, if_empty: bool, reset: bool) -> None:
    async with async_session_factory() as session:
        if if_empty:
            existing = await session.scalar(select(func.count(CardRow.card_id)))
            if existing and existing > 0:
                print(f"DB already seeded ({existing} cards). Skipping.")
                return

        print("Seeding cards...")
        c_ins, c_skip = await _seed_cards(session, reset=reset)
        print(f"  cards: {c_ins} inserted, {c_skip} skipped")

        print("Seeding navigation tasks...")
        n_ins, n_upd = await _seed_navigation(session, reset=reset)
        print(f"  navigation: {n_ins} inserted, {n_upd} updated")

        await session.commit()
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Easy SKS database")
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="Skip seeding if cards already exist (safe for container startup).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Truncate cards/scheduling/navigation tasks before reseeding.",
    )
    args = parser.parse_args()
    asyncio.run(run(if_empty=args.if_empty, reset=args.reset))


if __name__ == "__main__":
    main()

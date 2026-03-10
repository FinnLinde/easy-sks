#!/usr/bin/env python3
"""Seed the PostgreSQL database with navigation tasks from sks_navigation_catalog.json.

Usage:
    python -m scripts.seed_navigation
    python -m scripts.seed_navigation --file path/to/catalog.json

The script is idempotent: existing tasks (matched by task_id) are skipped.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Base, async_session_factory, engine  # noqa: E402
from navigation.db.navigation_tables import NavigationTaskRow  # noqa: E402

DEFAULT_CATALOG = Path(__file__).resolve().parent / "sks_navigation_catalog.json"


def _build_task_id(sheet_number: int, task_number: int) -> str:
    return f"nav_{sheet_number}_{task_number}"


async def seed(catalog_path: Path) -> None:
    with open(catalog_path, encoding="utf-8") as f:
        sheets: list[dict] = json.load(f)

    total_tasks = sum(len(s["tasks"]) for s in sheets)
    print(f"Loaded {len(sheets)} sheets with {total_tasks} tasks from {catalog_path}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        inserted = 0
        updated = 0

        for sheet in sheets:
            sheet_number = sheet["sheet_number"]
            for task in sheet["tasks"]:
                task_id = _build_task_id(sheet_number, task["task_number"])

                sol = task["solution"]
                sub_questions = [
                    {"text": sq["text"], "points": sq["points"]}
                    for sq in task["sub_questions"]
                ]
                solution_text = sol.get("solution_markdown", sol["full_text"])
                key_answers = sol["key_answers"]

                existing = await session.get(NavigationTaskRow, task_id)
                if existing is not None:
                    existing.points = task["points"]
                    existing.context = task["context"]
                    existing.sub_questions = sub_questions
                    existing.solution_text = solution_text
                    existing.key_answers = key_answers
                    updated += 1
                    continue

                row = NavigationTaskRow(
                    task_id=task_id,
                    sheet_number=sheet_number,
                    task_number=task["task_number"],
                    points=task["points"],
                    context=task["context"],
                    sub_questions=sub_questions,
                    solution_text=solution_text,
                    key_answers=key_answers,
                )
                session.add(row)
                inserted += 1

        await session.commit()
        print(f"Done: {inserted} inserted, {updated} updated")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed navigation tasks into PostgreSQL")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Path to sks_navigation_catalog.json",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: catalog file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(seed(args.file))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Format navigation solution texts into clean markdown using GPT-4o-mini.

Reads sks_navigation_catalog.json, sends each task's raw solution to OpenAI,
and writes the formatted markdown back into the catalog.

Usage:
    export OPENAI_API_KEY=sk-...
    python -m scripts.format_solutions
    python -m scripts.format_solutions --dry-run          # preview without writing
    python -m scripts.format_solutions --file path.json   # custom catalog path

The script is resumable: tasks that already have a `solution_markdown` field
are skipped. Remove that field to re-format a task.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from openai import OpenAI

DEFAULT_CATALOG = Path(__file__).resolve().parent / "sks_navigation_catalog.json"
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
Du bist ein Formatierungs-Assistent für SKS-Navigationsaufgaben (Sportküstenschifferschein).

Du erhältst die Musterlösung einer Navigationsaufgabe als unformatierten Text, \
zusammen mit den offiziellen Schlüsselwerten (key_answers) falls vorhanden.

Deine Aufgabe: Formatiere den Text als sauberes, gut lesbares **Markdown**.

Regeln:
- Inhalt NICHT verändern, kürzen oder ergänzen — nur formatieren
- Schlüsselwerte (Ergebnisse wie Kurse, Distanzen, Zeiten) **fett** hervorheben
- Zwischenschritte und Erklärungen als normalen Text belassen
- Listen verwenden wo sinnvoll (Aufzählungen, mehrere Werte)
- Keine Überschriften (kein #) — der Kontext wird separat angezeigt
- Kompakt bleiben, keine überflüssigen Leerzeilen
- Sprache: Deutsch beibehalten\
"""


def format_solution(client: OpenAI, full_text: str, key_answers: list[str]) -> str:
    key_section = ""
    if key_answers:
        formatted = "\n".join(f"- {ka}" for ka in key_answers)
        key_section = f"\n\nSchlüsselwerte:\n{formatted}"

    user_message = f"Musterlösung:\n{full_text}{key_section}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Format navigation solutions with GPT")
    parser.add_argument("--file", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: catalog not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()

    with open(args.file, encoding="utf-8") as f:
        sheets: list[dict] = json.load(f)

    total = sum(len(s["tasks"]) for s in sheets)
    formatted = 0
    skipped = 0
    errors = 0

    print(f"Catalog: {total} tasks across {len(sheets)} sheets")
    print(f"Model: {MODEL}")
    print(f"Dry run: {args.dry_run}\n")

    for sheet in sheets:
        for task in sheet["tasks"]:
            sol = task.get("solution", {})
            label = f"Sheet {sheet['sheet_number']} Task {task['task_number']}"

            if "solution_markdown" in sol:
                skipped += 1
                continue

            full_text = sol.get("full_text", "")
            if not full_text.strip():
                skipped += 1
                continue

            try:
                markdown = format_solution(
                    client, full_text, sol.get("key_answers", [])
                )
            except Exception as exc:
                print(f"  ERROR {label}: {exc}")
                errors += 1
                continue

            formatted += 1

            if args.dry_run:
                print(f"--- {label} ---")
                print(markdown)
                print()
                if formatted >= 3:
                    print(f"(dry-run: stopping after 3 previews)")
                    print(f"\nWould format {total - skipped} tasks. Run without --dry-run to apply.")
                    return
            else:
                sol["solution_markdown"] = markdown
                print(f"  {label} ✓ ({len(markdown)} chars)")

    if not args.dry_run and formatted > 0:
        with open(args.file, "w", encoding="utf-8") as f:
            json.dump(sheets, f, ensure_ascii=False, indent=2)
        print(f"\nCatalog updated: {args.file}")

    print(f"\nDone: {formatted} formatted, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()

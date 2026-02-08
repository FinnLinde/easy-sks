"""Shorten SKS catalog answers into bullet points using GPT-4o-mini.

Reads sks_catalog.json, sends each answer to the OpenAI API to produce a
concise bullet-point summary, and writes the result back as a new
"short_answer" field.

The script is resumable: it skips entries that already have a non-empty
short_answer, so you can safely re-run it after a partial failure.

Usage:
    export OPENAI_API_KEY="sk-..."
    python scripts/shorten_answers.py                   # from backend/
    python scripts/shorten_answers.py --dry-run          # preview without API calls
    python scripts/shorten_answers.py --force             # re-generate all short answers
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_FILE = SCRIPT_DIR / "sks_catalog.json"

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Antworten aus dem SKS-Fragenkatalog "
    "(Sportküstenschifferschein) in knappe Stichpunkte zusammenfasst.\n\n"
    "Regeln:\n"
    "- Antworte ausschließlich auf Deutsch.\n"
    "- Fasse die Antwort in möglichst wenigen Stichpunkten zusammen.\n"
    "- Verwende Aufzählungszeichen (-).\n"
    "- Behalte Fachbegriffe und Abkürzungen bei.\n"
    "- Kein einleitender Satz, nur die Stichpunkte.\n"
    "- Wenn die Antwort bereits sehr kurz ist (ein Satz), gib sie unverändert zurück."
)

# Delay between API calls to stay well within rate limits.
REQUEST_DELAY_S = 0.05

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def shorten_answer(client: OpenAI, question: str, answer: str) -> str:
    """Call GPT-4o-mini to produce a bullet-point summary of *answer*."""
    user_msg = f"Frage: {question}\n\nAntwort: {answer}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Shorten SKS answers via GPT-4o-mini")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be sent without calling the API",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-generate short answers even if they already exist",
    )
    args = parser.parse_args()

    # --- Load catalog ---
    with open(CATALOG_FILE, "r", encoding="utf-8") as fh:
        catalog: list[dict] = json.load(fh)

    print(f"Loaded {len(catalog)} questions from {CATALOG_FILE}")

    # --- Determine which entries need processing ---
    to_process = []
    for i, entry in enumerate(catalog):
        has_short = bool(entry.get("short_answer", "").strip())
        if args.force or not has_short:
            to_process.append(i)

    print(f"{len(to_process)} answers to shorten ({len(catalog) - len(to_process)} already done)")

    if not to_process:
        print("Nothing to do.")
        return

    if args.dry_run:
        for idx in to_process[:5]:
            e = catalog[idx]
            print(f"\n--- {e['topic']} q#{e['question_number']} ---")
            print(f"Q: {e['question'][:100]}...")
            print(f"A: {e['answer'][:100]}...")
        if len(to_process) > 5:
            print(f"\n... and {len(to_process) - 5} more")
        print("\nDry run complete. No API calls made.")
        return

    # --- Validate API key ---
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Set the OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # --- Process ---
    total = len(to_process)
    for count, idx in enumerate(to_process, start=1):
        entry = catalog[idx]
        topic = entry["topic"]
        q_num = entry["question_number"]
        question = entry["question"]
        answer = entry["answer"]

        print(f"[{count}/{total}] {topic} q#{q_num} ...", end=" ", flush=True)

        try:
            short = shorten_answer(client, question, answer)
            entry["short_answer"] = short
            print(f"OK ({len(short)} chars)")
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED: {exc}")
            # Save progress so far and abort
            _save(catalog)
            print(f"Progress saved after {count - 1} successful calls.")
            sys.exit(1)

        # Save every 50 entries as a checkpoint
        if count % 50 == 0:
            _save(catalog)
            print(f"  [checkpoint saved at {count}/{total}]")

        time.sleep(REQUEST_DELAY_S)

    _save(catalog)
    print(f"\nDone! All {total} short answers written to {CATALOG_FILE}")


def _save(catalog: list[dict]) -> None:
    with open(CATALOG_FILE, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

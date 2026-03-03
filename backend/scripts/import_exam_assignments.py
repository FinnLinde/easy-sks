#!/usr/bin/env python3
"""Import exam sheet assignments from the tim-koester SKS trainer.

Fetches def_fa.js, parses exam sheet (Pruefungsbogen) assignments per
question, matches them to existing cards by deterministic ID, and
optionally writes the assignments to the database and sks_catalog.json.

Usage:
    python -m scripts.import_exam_assignments                 # dry-run (default)
    python -m scripts.import_exam_assignments --apply         # write to DB + catalog
    python -m scripts.import_exam_assignments --apply --skip-db  # catalog only
    python -m scripts.import_exam_assignments --apply-db-from-catalog
        # update DB exam_sheets from local scripts/sks_catalog.json (no network)
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import requests
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from card.db.card_table import CardRow  # noqa: E402
from database import Base, async_session_factory, engine  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SOURCE_URL = (
    "http://www.tim.sf-ub.de/www2/trainer_online/sks/intern/def_fa.js"
)

TOPIC_PREFIX_MAP: dict[str, str] = {
    "1": "navigation",
    "2": "schifffahrtsrecht",
    "3": "wetterkunde",
    "4": "seemannschaft_i",
    "5": "seemannschaft_ii",
}

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_FILE = SCRIPT_DIR / "sks_catalog.json"
REPORT_FILE = SCRIPT_DIR / "exam_import_report.json"

SIMILARITY_WARNING_THRESHOLD = 0.85

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ParsedEntry:
    fa_id: str
    topic: str
    question_number: int
    exam_sheets: list[int]
    question_text: str
    answer_text: str


@dataclass
class MatchResult:
    card_id: str
    topic: str
    question_number: int
    exam_sheets: list[int]
    status: str  # "matched" | "matched_low_similarity" | "unmatched"
    similarity: float = 0.0
    warning: str = ""


# ---------------------------------------------------------------------------
# Fetching & Parsing
# ---------------------------------------------------------------------------


def fetch_js_source(url: str = SOURCE_URL) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content.decode("latin-1")


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_fa_entries(js_content: str) -> list[ParsedEntry]:
    """Parse all FA[...] entries from the JavaScript source."""
    pattern = (
        r'FA\["(\d+)"\] = new Array\(\s*'
        r"(\d+),\s*"           # question number within topic
        r"\d+,\s*"             # unused flag
        r"new Array\(([^)]*)\),\s*"  # exam sheets
        r'"(.*?)"\s*,\s*'      # question text
        r'"(.*?)"\s*\)'        # answer text
    )

    entries: list[ParsedEntry] = []
    for match in re.finditer(pattern, js_content, re.DOTALL):
        fa_id = match.group(1)
        q_num = int(match.group(2))
        sheets_raw = match.group(3).strip()
        question_html = match.group(4)
        answer_html = match.group(5)

        topic_prefix = fa_id[0]
        topic = TOPIC_PREFIX_MAP.get(topic_prefix)
        if topic is None:
            continue

        exam_sheets: list[int] = []
        if sheets_raw:
            for s in sheets_raw.split(","):
                s = s.strip().strip('"').strip("'")
                if not s:
                    continue
                num = re.sub(r"[^\d]", "", s)
                if num:
                    exam_sheets.append(int(num))

        entries.append(
            ParsedEntry(
                fa_id=fa_id,
                topic=topic,
                question_number=q_num,
                exam_sheets=sorted(exam_sheets),
                question_text=_strip_html(question_html),
                answer_text=_strip_html(answer_html),
            )
        )

    return entries


# ---------------------------------------------------------------------------
# Normalization & Matching
# ---------------------------------------------------------------------------


def normalize_for_comparison(text: str) -> str:
    """Normalize text for similarity comparison."""
    text = _strip_html(text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compute_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def build_card_id(topic: str, question_number: int) -> str:
    return f"{topic}_{question_number}"


def match_entries_to_catalog(
    entries: list[ParsedEntry],
    catalog: list[dict],
) -> list[MatchResult]:
    """Match parsed JS entries to existing catalog entries by card_id."""
    catalog_lookup: dict[str, dict] = {}
    for item in catalog:
        key = build_card_id(item["topic"], item["question_number"])
        catalog_lookup[key] = item

    results: list[MatchResult] = []
    for entry in entries:
        card_id = build_card_id(entry.topic, entry.question_number)

        if card_id not in catalog_lookup:
            results.append(
                MatchResult(
                    card_id=card_id,
                    topic=entry.topic,
                    question_number=entry.question_number,
                    exam_sheets=entry.exam_sheets,
                    status="unmatched",
                    warning=f"No catalog entry for {card_id}",
                )
            )
            continue

        cat_entry = catalog_lookup[card_id]
        norm_js = normalize_for_comparison(entry.question_text)
        norm_cat = normalize_for_comparison(cat_entry["question"])
        similarity = compute_similarity(norm_js, norm_cat)

        status = "matched"
        warning = ""
        if similarity < SIMILARITY_WARNING_THRESHOLD:
            status = "matched_low_similarity"
            warning = (
                f"Low similarity ({similarity:.2f}): "
                f"JS='{entry.question_text[:60]}...' vs "
                f"Cat='{cat_entry['question'][:60]}...'"
            )

        results.append(
            MatchResult(
                card_id=card_id,
                topic=entry.topic,
                question_number=entry.question_number,
                exam_sheets=entry.exam_sheets,
                status=status,
                similarity=similarity,
                warning=warning,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_report(results: list[MatchResult]) -> dict:
    matched = [r for r in results if r.status == "matched"]
    low_sim = [r for r in results if r.status == "matched_low_similarity"]
    unmatched = [r for r in results if r.status == "unmatched"]
    with_sheets = [r for r in results if r.exam_sheets]

    report = {
        "summary": {
            "total_parsed": len(results),
            "matched": len(matched),
            "matched_low_similarity": len(low_sim),
            "unmatched": len(unmatched),
            "with_exam_sheets": len(with_sheets),
        },
        "exam_sheet_stats": _exam_sheet_stats(results),
        "warnings": [
            {"card_id": r.card_id, "warning": r.warning}
            for r in results
            if r.warning
        ],
        "unmatched": [asdict(r) for r in unmatched],
    }
    return report


def _exam_sheet_stats(results: list[MatchResult]) -> dict[int, int]:
    stats: dict[int, int] = {}
    for r in results:
        for sheet in r.exam_sheets:
            stats[sheet] = stats.get(sheet, 0) + 1
    return dict(sorted(stats.items()))


def print_report(report: dict) -> None:
    s = report["summary"]
    print("\n=== Exam Sheet Import Report ===")
    print(f"  Total parsed:             {s['total_parsed']}")
    print(f"  Matched:                  {s['matched']}")
    print(f"  Matched (low similarity): {s['matched_low_similarity']}")
    print(f"  Unmatched:                {s['unmatched']}")
    print(f"  With exam sheets:         {s['with_exam_sheets']}")

    print("\n  Exam sheet distribution:")
    for sheet, count in report["exam_sheet_stats"].items():
        print(f"    {sheet}: {count} questions")

    if report["warnings"]:
        print(f"\n  Warnings ({len(report['warnings'])}):")
        for w in report["warnings"][:10]:
            print(f"    [{w['card_id']}] {w['warning']}")
        if len(report["warnings"]) > 10:
            print(f"    ... and {len(report['warnings']) - 10} more")

    if report["unmatched"]:
        print(f"\n  Unmatched ({len(report['unmatched'])}):")
        for u in report["unmatched"]:
            print(f"    {u['card_id']}")


# ---------------------------------------------------------------------------
# Apply: update catalog JSON
# ---------------------------------------------------------------------------


def apply_to_catalog(
    results: list[MatchResult],
    catalog_path: Path = CATALOG_FILE,
) -> int:
    """Write exam_sheets into sks_catalog.json. Returns count of updated entries."""
    with open(catalog_path, encoding="utf-8") as f:
        catalog: list[dict] = json.load(f)

    lookup: dict[str, list[int]] = {
        r.card_id: r.exam_sheets
        for r in results
        if r.status in ("matched", "matched_low_similarity")
    }

    updated = 0
    for entry in catalog:
        key = build_card_id(entry["topic"], entry["question_number"])
        if key in lookup:
            entry["exam_sheets"] = lookup[key]
            updated += 1
        elif "exam_sheets" not in entry:
            entry["exam_sheets"] = []

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    return updated


# ---------------------------------------------------------------------------
# Apply: update database
# ---------------------------------------------------------------------------


async def apply_to_database(results: list[MatchResult]) -> int:
    """Write exam_sheets into the cards table. Returns count of updated rows."""
    lookup: dict[str, list[int]] = {
        r.card_id: r.exam_sheets
        for r in results
        if r.status in ("matched", "matched_low_similarity")
    }

    async with async_session_factory() as session:
        updated = 0
        for card_id, exam_sheets in lookup.items():
            row = await session.get(CardRow, card_id)
            if row is None:
                print(f"  WARNING: card {card_id} not found in DB, skipping")
                continue
            current = list(row.exam_sheets) if row.exam_sheets else []
            if current != exam_sheets:
                row.exam_sheets = exam_sheets
                updated += 1

        await session.commit()
    return updated


async def apply_catalog_to_database(catalog_path: Path = CATALOG_FILE) -> int:
    """Write exam_sheets from local catalog JSON into cards table."""
    with open(catalog_path, encoding="utf-8") as f:
        catalog: list[dict] = json.load(f)

    lookup: dict[str, list[int]] = {}
    for entry in catalog:
        topic = entry.get("topic")
        question_number = entry.get("question_number")
        if topic is None or question_number is None:
            continue
        card_id = build_card_id(str(topic), int(question_number))
        exam_sheets = [
            int(sheet)
            for sheet in (entry.get("exam_sheets") or [])
            if isinstance(sheet, int) or str(sheet).isdigit()
        ]
        lookup[card_id] = sorted(exam_sheets)

    async with async_session_factory() as session:
        updated = 0
        for card_id, exam_sheets in lookup.items():
            row = await session.get(CardRow, card_id)
            if row is None:
                continue
            current = list(row.exam_sheets) if row.exam_sheets else []
            if current != exam_sheets:
                row.exam_sheets = exam_sheets
                updated += 1
        await session.commit()
    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import exam sheet assignments from external SKS trainer"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes (default is dry-run)",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip database update (only update catalog JSON)",
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        default=None,
        help="Use a local JS file instead of fetching from URL",
    )
    parser.add_argument(
        "--apply-db-from-catalog",
        action="store_true",
        help="Update DB exam_sheets from local scripts/sks_catalog.json (no fetch)",
    )
    args = parser.parse_args()

    if args.apply_db_from_catalog:
        print(f"Applying exam_sheets from local catalog: {CATALOG_FILE}")
        db_updated = asyncio.run(apply_catalog_to_database())
        print(f"Database: {db_updated} rows updated")
        print("\nDone.")
        return

    # 1. Fetch / load JS source
    if args.source_file:
        print(f"Loading from local file: {args.source_file}")
        js_content = args.source_file.read_text(encoding="latin-1")
    else:
        print(f"Fetching from {SOURCE_URL} ...")
        try:
            js_content = fetch_js_source()
        except requests.RequestException as exc:
            print(f"ERROR: failed to fetch source: {exc}", file=sys.stderr)
            print(
                "Hint: run with --apply-db-from-catalog to update DB from local "
                "scripts/sks_catalog.json without network access.",
                file=sys.stderr,
            )
            sys.exit(1)

    # 2. Parse
    entries = parse_fa_entries(js_content)
    print(f"Parsed {len(entries)} entries from JS source")

    # 3. Load catalog for matching
    if not CATALOG_FILE.exists():
        print(f"ERROR: catalog not found at {CATALOG_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(CATALOG_FILE, encoding="utf-8") as f:
        catalog: list[dict] = json.load(f)

    # 4. Match
    results = match_entries_to_catalog(entries, catalog)

    # 5. Report
    report = generate_report(results)
    print_report(report)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport written to {REPORT_FILE}")

    # 6. Apply if requested
    if not args.apply:
        print("\nDry-run complete. Use --apply to write changes.")
        return

    print("\n--- Applying changes ---")

    catalog_updated = apply_to_catalog(results)
    print(f"Catalog: {catalog_updated} entries updated in {CATALOG_FILE.name}")

    if not args.skip_db:
        db_updated = asyncio.run(apply_to_database(results))
        print(f"Database: {db_updated} rows updated")
    else:
        print("Database: skipped (--skip-db)")

    print("\nDone.")


if __name__ == "__main__":
    main()

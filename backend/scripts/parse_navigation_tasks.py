"""Parse the official SKS navigation exam tasks PDF from ELWIS.

Extracts all 10 Lösungsbogen (solution sheets) with their tasks, points,
question text, sub-questions, and solutions from the PDF file.

Usage:
    python -m scripts.parse_navigation_tasks                 # expects /tmp/sks_navigation.pdf
    python -m scripts.parse_navigation_tasks --pdf path.pdf  # custom path
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = SCRIPT_DIR / "sks_navigation_catalog.json"
DEFAULT_PDF = Path("/tmp/sks_navigation.pdf")

TOTAL_SHEETS = 10
PAGES_PER_SHEET = 8
CONTENT_PAGES_PER_SHEET = 6
EXPECTED_POINTS_PER_SHEET = 30


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class NavigationSubQuestion:
    text: str
    points: int = 1


@dataclass
class NavigationSolution:
    full_text: str
    key_answers: list[str] = field(default_factory=list)


@dataclass
class ParsedNavigationTask:
    sheet_number: int
    task_number: int
    points: int
    context: str
    sub_questions: list[NavigationSubQuestion] = field(default_factory=list)
    solution: NavigationSolution = field(default_factory=NavigationSolution)


@dataclass
class ParsedNavigationSheet:
    sheet_number: int
    intro_text: str
    tasks: list[ParsedNavigationTask] = field(default_factory=list)


# ---------------------------------------------------------------------------
# PDF page layout helpers
# ---------------------------------------------------------------------------


def _sheet_page_range(sheet_idx: int) -> tuple[int, int]:
    """Return (header_page_idx, end_page_idx_exclusive) for a sheet."""
    if sheet_idx == 0:
        header = 1
    else:
        header = 1 + sheet_idx * PAGES_PER_SHEET
    return header, header + PAGES_PER_SHEET


def _content_text_for_sheet(doc: fitz.Document, sheet_idx: int) -> str:
    """Concatenate the text of the content pages for a given sheet."""
    header, end = _sheet_page_range(sheet_idx)
    content_start = header + 1
    content_end = content_start + CONTENT_PAGES_PER_SHEET
    parts: list[str] = []
    for pg_idx in range(content_start, min(content_end, doc.page_count)):
        parts.append(doc[pg_idx].get_text())
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Text parsing
# ---------------------------------------------------------------------------

AUFGABE_RE = re.compile(
    r"Aufgabe\s+(\d+)\s*\t\s*\n(•+)",
    re.MULTILINE,
)

LOESUNG_RE = re.compile(r"^Lösung:\s*$", re.MULTILINE)


def _count_leading_dots(line: str) -> int:
    """Count • characters at the start of a line (ignoring whitespace/tabs)."""
    stripped = line.lstrip(" \t")
    count = 0
    for ch in stripped:
        if ch == "•":
            count += 1
        else:
            break
    return count


def _clean(text: str) -> str:
    """Collapse excessive whitespace while preserving paragraph breaks."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_key_answers(solution_text: str) -> list[str]:
    """Pull out the bracketed tolerance answers that represent correct values.

    In the PDF, a bullet line (``• \\t``) is often followed by the answer text
    on the *next* line, so we merge bullet-prefixed lines with subsequent
    continuation lines before scanning for tolerance markers.
    """
    merged_lines: list[str] = []
    lines = solution_text.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        dots = _count_leading_dots(stripped)
        text = stripped.lstrip("• \t")
        if dots > 0 and not text:
            # Bullet-only line: merge with next non-empty line
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                merged_lines.append(lines[i].strip())
            i += 1
            continue
        if dots > 0 and text:
            merged_lines.append(text)
        else:
            if merged_lines and stripped and not _count_leading_dots(stripped):
                last = merged_lines[-1]
                if not re.search(r"\[.*(?:Toleranz|±).*\]$", last):
                    merged_lines[-1] = last + " " + stripped
                    i += 1
                    continue
            merged_lines.append(stripped)
        i += 1

    answers: list[str] = []
    for line in merged_lines:
        cleaned = line.lstrip("• \t")
        if re.search(r"\[.*(?:Toleranz|±).*\]", cleaned):
            answers.append(_clean(cleaned))
    return answers


def _parse_question_body(body_text: str) -> tuple[str, list[NavigationSubQuestion]]:
    """Split task body (before Lösung:) into context and sub-questions.

    In the PDF, bullets appear on their own line (e.g. ``•\\t``) with the
    actual question text on the *following* line.
    """
    lines = body_text.split("\n")
    context_parts: list[str] = []
    sub_questions: list[NavigationSubQuestion] = []
    pending_dots: int | None = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if pending_dots is None and not sub_questions:
                context_parts.append("")
            continue

        dots = _count_leading_dots(stripped)
        text_after_dots = stripped.lstrip("• \t")

        if dots > 0 and not text_after_dots:
            pending_dots = dots
            continue

        if dots > 0 and text_after_dots:
            sub_questions.append(NavigationSubQuestion(text=_clean(text_after_dots), points=dots))
            pending_dots = None
            continue

        if pending_dots is not None:
            sub_questions.append(
                NavigationSubQuestion(text=_clean(stripped), points=pending_dots)
            )
            pending_dots = None
            continue

        if sub_questions:
            last = sub_questions[-1]
            sub_questions[-1] = NavigationSubQuestion(
                text=last.text + " " + _clean(stripped),
                points=last.points,
            )
        else:
            context_parts.append(stripped)

    context = _clean("\n".join(context_parts))
    return context, sub_questions


def _split_tasks(full_text: str, sheet_number: int) -> list[ParsedNavigationTask]:
    """Split the concatenated content text into individual tasks."""
    task_starts: list[tuple[int, int, int]] = []  # (char_pos, task_num, points)

    for match in AUFGABE_RE.finditer(full_text):
        task_num = int(match.group(1))
        points = len(match.group(2))
        task_starts.append((match.start(), task_num, points))

    tasks: list[ParsedNavigationTask] = []
    for i, (pos, task_num, points) in enumerate(task_starts):
        after_header = AUFGABE_RE.search(full_text[pos:])
        if after_header is None:
            continue
        body_start = pos + after_header.end()
        body_end = task_starts[i + 1][0] if i + 1 < len(task_starts) else len(full_text)
        body = full_text[body_start:body_end].strip()

        loesung_match = LOESUNG_RE.search(body)
        if loesung_match:
            question_body = body[: loesung_match.start()]
            solution_text = body[loesung_match.end() :]
        else:
            question_body = body
            solution_text = ""

        context, sub_questions = _parse_question_body(question_body)
        key_answers = _extract_key_answers(solution_text)

        tasks.append(
            ParsedNavigationTask(
                sheet_number=sheet_number,
                task_number=task_num,
                points=points,
                context=_clean(context),
                sub_questions=sub_questions,
                solution=NavigationSolution(
                    full_text=_clean(solution_text),
                    key_answers=key_answers,
                ),
            )
        )

    return tasks


def _extract_intro(doc: fitz.Document, sheet_idx: int) -> str:
    """Extract the introduction text from the sheet header page."""
    header_pg, _ = _sheet_page_range(sheet_idx)
    text = doc[header_pg].get_text()
    marker = "Gesetzliche Zeit"
    idx = text.find(marker)
    if idx >= 0:
        intro = text[: idx + text[idx:].find("\n") + 1]
    else:
        intro = text
    return _clean(intro)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_pdf(pdf_path: Path) -> list[ParsedNavigationSheet]:
    doc = fitz.open(str(pdf_path))
    print(f"Opened {pdf_path}: {doc.page_count} pages")

    sheets: list[ParsedNavigationSheet] = []
    total_tasks = 0

    for sheet_idx in range(TOTAL_SHEETS):
        sheet_number = sheet_idx + 1
        intro = _extract_intro(doc, sheet_idx)
        content_text = _content_text_for_sheet(doc, sheet_idx)
        tasks = _split_tasks(content_text, sheet_number)

        sheet_points = sum(t.points for t in tasks)
        total_tasks += len(tasks)

        sheet = ParsedNavigationSheet(
            sheet_number=sheet_number,
            intro_text=intro,
            tasks=tasks,
        )
        sheets.append(sheet)
        print(
            f"  Sheet {sheet_number:02d}: {len(tasks)} tasks, "
            f"{sheet_points} points"
            f"{' ✓' if sheet_points == EXPECTED_POINTS_PER_SHEET else ' ⚠ MISMATCH!'}"
        )

    print(f"\nTotal: {total_tasks} tasks across {len(sheets)} sheets")
    doc.close()
    return sheets


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse SKS navigation tasks PDF")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="Path to the PDF")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE, help="Output JSON path")
    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"ERROR: PDF not found at {args.pdf}")
        print(
            "Download it from: https://www.elwis.de/DE/Sportschifffahrt/"
            "Sportbootfuehrerscheine/Navigationsaufgaben-SKS.pdf"
        )
        return

    sheets = parse_pdf(args.pdf)

    data = [asdict(s) for s in sheets]
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()

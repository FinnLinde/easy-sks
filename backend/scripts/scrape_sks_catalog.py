"""Scrape the official SKS exam question catalog from ELWIS.

Fetches all questions and answers (including embedded images) from the 5
category pages and writes structured JSON to sks_catalog.json.

Usage:
    python -m scripts.scrape_sks_catalog          # from backend/
    python scripts/scrape_sks_catalog.py           # from backend/
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.elwis.de/DE/Sportschifffahrt/Sportbootfuehrerscheine/Fragenkatalog-SKS/"

TOPICS: list[dict[str, str | int]] = [
    {
        "slug": "Navigation",
        "topic": "navigation",
        "expected_count": 118,
    },
    {
        "slug": "Schifffahrtsrecht",
        "topic": "schifffahrtsrecht",
        "expected_count": 110,
    },
    {
        "slug": "Wetterkunde",
        "topic": "wetterkunde",
        "expected_count": 101,
    },
    {
        "slug": "Seemannschaft-I",
        "topic": "seemannschaft_i",
        "expected_count": 163,
    },
    {
        "slug": "Seemannschaft-II",
        "topic": "seemannschaft_ii",
        "expected_count": 146,
    },
]

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = SCRIPT_DIR / "sks_images"
OUTPUT_FILE = SCRIPT_DIR / "sks_catalog.json"

REQUEST_DELAY_S = 1.0  # polite delay between HTTP requests
REQUEST_TIMEOUT_S = 30

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ScrapedQuestion:
    topic: str
    question_number: int
    question: str
    question_images: list[str] = field(default_factory=list)
    answer: str = ""
    answer_images: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fetch(url: str) -> str:
    """Fetch a URL and return decoded HTML text."""
    resp = requests.get(url, timeout=REQUEST_TIMEOUT_S)
    resp.raise_for_status()
    # The server sends charset=utf-8 in Content-Type but apparent_encoding
    # sometimes misdetects it.  Trust the header; fall back to utf-8.
    if resp.encoding is None:
        resp.encoding = "utf-8"
    return resp.text


def _download_image(url: str, dest: Path) -> None:
    """Download an image to *dest*."""
    resp = requests.get(url, timeout=REQUEST_TIMEOUT_S, stream=True)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            fh.write(chunk)


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing blanks."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip the "Stand: 01. Juli 2006" footer that appears on the last
    # question of each topic page.
    text = re.sub(r"\n?Stand:\s*\d{2}\.\s*\w+\s*\d{4}\s*$", "", text)
    return text.strip()


def _extract_text_and_images(
    elements: list[Tag | NavigableString],
    *,
    topic: str,
    question_number: int,
    section: str,
    page_url: str,
) -> tuple[str, list[str]]:
    """Walk a list of BS4 elements and extract text + image paths.

    Returns (cleaned_text, list_of_local_image_paths).
    """
    text_parts: list[str] = []
    images: list[str] = []
    img_counter = 0

    for el in elements:
        if isinstance(el, NavigableString):
            text_parts.append(str(el))
            continue

        assert isinstance(el, Tag)

        # Collect images from this element and its descendants
        img_tags = el.find_all("img") if el.name != "img" else [el]
        if el.name == "img":
            img_tags = [el]
        else:
            img_tags = el.find_all("img")

        for img_tag in img_tags:
            src = img_tag.get("src", "")
            if not src:
                continue
            img_counter += 1
            abs_url = urljoin(page_url, src)
            # Strip query params from the path to get a clean extension
            clean_path = urlparse(src).path
            ext = Path(clean_path).suffix or ".png"
            filename = f"{topic}_q{question_number}_{section}{img_counter}{ext}"
            local_path = IMAGES_DIR / filename
            rel_path = f"sks_images/{filename}"

            try:
                _download_image(abs_url, local_path)
                images.append(rel_path)
                text_parts.append(f"[image: {rel_path}]")
            except Exception as exc:  # noqa: BLE001
                print(f"    WARNING: failed to download {abs_url}: {exc}")
                images.append(f"FAILED:{abs_url}")
                text_parts.append(f"[image: FAILED {abs_url}]")

        # Extract text (get_text preserves structure better than .string)
        text_parts.append(el.get_text(separator=" "))

    return _clean_text(" ".join(text_parts)), images


# ---------------------------------------------------------------------------
# Core parsing
# ---------------------------------------------------------------------------


def _find_content_area(soup: BeautifulSoup) -> Tag:
    """Locate the main content <div> of an ELWIS page."""
    # The questions live inside <div id="content"> or a similar wrapper.
    # Try several selectors that work with the ELWIS template.
    for selector in (
        "div#content div.row",
        "div#content",
        "div.singleview",
        "main",
        "article",
    ):
        tag = soup.select_one(selector)
        if tag:
            return tag
    # Fallback: return <body>
    return soup.body  # type: ignore[return-value]


def _split_into_question_blocks(content: Tag) -> list[tuple[int, list[Tag | NavigableString]]]:
    """Split the content area into (question_number, elements) pairs.

    We walk through all *direct and nested* elements looking for text nodes
    that match "Nummer N:".  Everything between two such markers belongs to
    one question.
    """
    # Flatten all descendants into a list so we can split them.
    # We work on the *top-level* children of the content area.  Each child
    # is either a text node or a tag (p, div, strong, img, …).
    children = list(content.children)

    blocks: list[tuple[int, list[Tag | NavigableString]]] = []
    current_num: int | None = None
    current_elements: list[Tag | NavigableString] = []

    nummer_re = re.compile(r"Nummer\s+(\d+)\s*:")

    def _flush() -> None:
        nonlocal current_num, current_elements
        if current_num is not None and current_elements:
            blocks.append((current_num, current_elements))
        current_num = None
        current_elements = []

    for child in children:
        raw = child.get_text() if isinstance(child, Tag) else str(child)
        match = nummer_re.search(raw)

        if match:
            _flush()
            current_num = int(match.group(1))
            # Keep the element – it may contain the question text too
            # (e.g. "Nummer 1: \n **question text**").  We strip the
            # marker later during question/answer extraction.
            current_elements.append(child)
        else:
            if current_num is not None:
                current_elements.append(child)

    _flush()  # don't forget the last block
    return blocks


def _parse_question_block(
    question_number: int,
    elements: list[Tag | NavigableString],
    *,
    topic: str,
    page_url: str,
) -> ScrapedQuestion:
    """Parse a single question block into a ScrapedQuestion."""

    # Strategy: Rebuild the inner HTML of the block, then re-parse it.
    # This is simpler than walking the heterogeneous element list directly.
    inner_html = ""
    for el in elements:
        if isinstance(el, NavigableString):
            inner_html += str(el)
        else:
            inner_html += str(el)

    frag = BeautifulSoup(inner_html, "html.parser")

    # Remove the "Nummer N:" prefix from the text.
    nummer_re = re.compile(r"Nummer\s+\d+\s*:\s*")
    for text_node in frag.find_all(string=nummer_re):
        cleaned = nummer_re.sub("", str(text_node), count=1)
        text_node.replace_with(cleaned)

    # --- Separate question (bold) from answer (rest) ---
    # The question is everything inside <strong> / <b> tags.
    # The answer is everything else.
    bold_tags = frag.find_all(["strong", "b"])

    question_parts_html: list[str] = []
    for bt in bold_tags:
        question_parts_html.append(str(bt))
        # Mark as consumed so we don't include it in the answer
        bt.extract()

    # Question: parse extracted bold HTML for text + images
    q_soup = BeautifulSoup(" ".join(question_parts_html), "html.parser")
    q_elements = list(q_soup.children)
    question_text, question_images = _extract_text_and_images(
        q_elements,
        topic=topic,
        question_number=question_number,
        section="q",
        page_url=page_url,
    )

    # Answer: whatever remains in frag
    a_elements = list(frag.children)
    answer_text, answer_images = _extract_text_and_images(
        a_elements,
        topic=topic,
        question_number=question_number,
        section="a",
        page_url=page_url,
    )

    return ScrapedQuestion(
        topic=topic,
        question_number=question_number,
        question=question_text,
        question_images=question_images,
        answer=answer_text,
        answer_images=answer_images,
    )


# ---------------------------------------------------------------------------
# Per-topic scraper
# ---------------------------------------------------------------------------


def scrape_topic(slug: str, topic: str, expected_count: int) -> list[ScrapedQuestion]:
    """Scrape all questions for a single topic."""
    url = f"{BASE_URL}{slug}/{slug}-node.html"
    print(f"Fetching {topic} from {url} ...")
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")

    content = _find_content_area(soup)
    blocks = _split_into_question_blocks(content)

    print(f"  Found {len(blocks)} question blocks (expected {expected_count})")
    if len(blocks) != expected_count:
        print(f"  WARNING: count mismatch for {topic}!")

    questions: list[ScrapedQuestion] = []
    for q_num, elements in blocks:
        q = _parse_question_block(q_num, elements, topic=topic, page_url=url)
        questions.append(q)

    return questions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    all_questions: list[ScrapedQuestion] = []

    for topic_info in TOPICS:
        questions = scrape_topic(
            slug=str(topic_info["slug"]),
            topic=str(topic_info["topic"]),
            expected_count=int(topic_info["expected_count"]),
        )
        all_questions.extend(questions)
        print(f"  => {len(questions)} questions scraped for {topic_info['topic']}")
        time.sleep(REQUEST_DELAY_S)

    # Write JSON
    data = [asdict(q) for q in all_questions]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_questions)} questions written to {OUTPUT_FILE}")
    print(f"Images saved to {IMAGES_DIR}/")

    # Summary per topic
    from collections import Counter

    topic_counts = Counter(q.topic for q in all_questions)
    img_count = sum(len(q.question_images) + len(q.answer_images) for q in all_questions)
    print(f"\nSummary:")
    for t, c in topic_counts.items():
        print(f"  {t}: {c} questions")
    print(f"  Total images downloaded: {img_count}")


if __name__ == "__main__":
    main()

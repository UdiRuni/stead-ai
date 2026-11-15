#!/usr/bin/env python3
"""House-rule checks for the pitch materials. Run before every commit that touches docs/.

Usage: python3 tools/check_docs.py        (exit code 1 on any failure)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIEF_JSON = ROOT / "docs/brief/brief.json"
BRIEF_PDF = ROOT / "docs/brief/stead.ai_Stock_Swap_Brief_2pages.pdf"
DECK = ROOT / "docs/deck/stead.ai_Stock_Swap_Pitch_Deck_Short.pptx"
MAX_SLIDES = 10

BANNED = [
    (re.compile(chr(0x2014)), "em dash"),
    (re.compile(r"lodestar", re.I), "Lodestar (dropped from this venture)"),
    (re.compile(r"\bon Lloyd.s capacity\b", re.I), "claims cover on Lloyd's capacity"),
    (re.compile(r"risk[- ]free", re.I), "risk-free claim"),
]
errors = []


def scan(label, text):
    for pattern, why in BANNED:
        for m in pattern.finditer(text):
            context = text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
            errors.append(f"{label}: {why}: ...{context}...")


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)


# 2-pager: text rules, builds to exactly 2 pages, committed PDF matches the source
scan("brief.json", "\n".join(strings(json.loads(BRIEF_JSON.read_text(encoding="utf-8")))))
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "brief.pdf"
    build = subprocess.run([sys.executable, str(ROOT / "docs/brief/build_brief.py"), str(out)],
                           capture_output=True, text=True)
    if build.returncode != 0:
        errors.append("brief does not build to 2 pages: " + (build.stderr or build.stdout).strip())
    else:
        from pypdf import PdfReader

        def text_of(path):
            return "\n".join(page.extract_text() for page in PdfReader(str(path)).pages)

        if len(PdfReader(str(out)).pages) != 2:
            errors.append("brief is not exactly 2 pages")
        if not BRIEF_PDF.exists() or text_of(BRIEF_PDF) != text_of(out):
            errors.append("committed brief PDF is out of date: run python3 docs/brief/build_brief.py")

# short deck: text rules (slides and speaker notes) and slide count
from pptx import Presentation

deck = Presentation(str(DECK))
slides = list(deck.slides)
if len(slides) > MAX_SLIDES:
    errors.append(f"short deck has {len(slides)} slides, limit is {MAX_SLIDES}")
for number, slide in enumerate(slides, 1):
    parts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            parts.append(shape.text_frame.text)
        if getattr(shape, "has_table", False) and shape.has_table:
            parts += [cell.text for row in shape.table.rows for cell in row.cells]
    if slide.has_notes_slide:
        parts.append(slide.notes_slide.notes_text_frame.text)
    scan(f"deck slide {number}", "\n".join(parts))

if errors:
    print("\n".join("FAIL " + e for e in errors))
    sys.exit(1)
print(f"docs OK: brief is 2 pages, deck has {len(slides)} slides, no banned terms")

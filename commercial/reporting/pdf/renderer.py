from __future__ import annotations

import textwrap
from pathlib import Path

import fitz

from .sections import REQUIRED_SECTIONS, section_lines


RENDERER_VERSION = "PyMuPDF-STRUCTEVIDENCE-PDF-RENDERER-v0.1"


def _insert_wrapped(page, text: str, x: float, y: float, width_chars: int = 92, size: int = 9) -> float:
    for line in textwrap.wrap(str(text), width=width_chars) or [""]:
        page.insert_text((x, y), line, fontsize=size, fontname="helv", color=(0.08, 0.08, 0.08))
        y += size + 4
    return y


def _footer(page, report_id: str, page_no: int, page_count: int) -> None:
    y = page.rect.height - 34
    page.draw_line((50, y - 8), (page.rect.width - 50, y - 8), color=(0.65, 0.65, 0.65), width=0.5)
    page.insert_text((50, y), f"StructEvidence | {report_id} | Page {page_no} / {page_count} | Research only. No investment advice.", fontsize=8, fontname="helv", color=(0.25, 0.25, 0.25))


def render_pdf(bundle: dict, output_path: Path, draft: bool = False) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    sections = section_lines(bundle, draft)
    for title, lines in sections:
        page = doc.new_page(width=595, height=842)
        if draft:
            page.insert_text((90, 410), "DRAFT - NOT FOR DELIVERY", fontsize=28, fontname="helv", color=(0.75, 0.75, 0.75))
        page.insert_text((50, 58), title, fontsize=17 if title != "Cover" else 22, fontname="helv", color=(0.02, 0.16, 0.28))
        y = 88
        if title == "Cover":
            page.draw_rect((50, 95, 545, 185), color=(0.02, 0.16, 0.28), fill=(0.02, 0.16, 0.28))
            page.insert_text((70, 145), "StructEvidence Verified Research Report", fontsize=18, fontname="helv", color=(1, 1, 1))
            y = 220
        for line in lines:
            y = _insert_wrapped(page, line, 58, y, size=9)
            if y > 760:
                break
    doc.set_metadata({
        "title": f"StructEvidence Verified Research Report - {bundle['subject_id']}",
        "subject": bundle["research_id"],
        "author": "StructEvidence",
        "creator": "StructEvidence PDF Renderer",
        "keywords": "StructEvidence, verified research, freshness, GDR-SE, SHA-256",
    })
    page_count = doc.page_count
    for idx, page in enumerate(doc, 1):
        _footer(page, bundle["report_id"], idx, page_count)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return output_path


def required_sections() -> list[str]:
    return REQUIRED_SECTIONS

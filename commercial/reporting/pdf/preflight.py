from __future__ import annotations

from pathlib import Path

import fitz

from .sections import REQUIRED_SECTIONS
from .verify import sha256_file


REQUIRED_PHRASES = ["Research only. No investment advice.", "Structural State", "Freshness", "Evidence", "GDR-SE", "Verification", "SHA-256"]


def preflight_pdf(path: Path, draft_expected: bool | None = None) -> dict:
    result = {"pdf_path": str(path), "exists": path.exists(), "header_valid": False, "page_count": 0, "metadata_present": False, "sections_present": False, "text_qa": False, "render_qa": False, "pdf_sha256": None, "errors": []}
    if not path.exists() or path.stat().st_size == 0:
        result["errors"].append("missing or empty PDF")
        return result
    result["header_valid"] = path.read_bytes()[:5] == b"%PDF-"
    doc = fitz.open(path)
    result["page_count"] = doc.page_count
    metadata = doc.metadata or {}
    result["metadata_present"] = bool(metadata.get("title") and metadata.get("author") and metadata.get("creator"))
    text = "\n".join(page.get_text("text") for page in doc)
    result["sections_present"] = all(section in text for section in REQUIRED_SECTIONS)
    result["text_qa"] = all(phrase in text for phrase in REQUIRED_PHRASES)
    if draft_expected is True and "DRAFT - NOT FOR DELIVERY" not in text:
        result["errors"].append("draft watermark missing")
    if draft_expected is False and "DRAFT - NOT FOR DELIVERY" in text:
        result["errors"].append("draft watermark present on final")
    render_ok = True
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), alpha=False)
        if pix.width <= 0 or pix.height <= 0 or not pix.samples:
            render_ok = False
            break
    doc.close()
    result["render_qa"] = render_ok
    result["pdf_sha256"] = sha256_file(path)
    result["pass"] = all(result[key] for key in ["header_valid", "page_count", "metadata_present", "sections_present", "text_qa", "render_qa"]) and not result["errors"]
    return result

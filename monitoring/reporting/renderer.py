from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import fitz


PAGE = fitz.paper_rect("a4")
MARGIN = 46
INK = (0.09, 0.13, 0.15)
MUTED = (0.35, 0.41, 0.42)
LINE = (0.78, 0.82, 0.81)
PAPER = (0.96, 0.97, 0.97)
TEAL = (0.0, 0.44, 0.45)
AMBER = (0.65, 0.37, 0.0)
WHITE = (1, 1, 1)


def _text(page: fitz.Page, rect: fitz.Rect, value: object, size: float = 9, color=INK,
          font: str = "helv", align: int = fitz.TEXT_ALIGN_LEFT) -> None:
    page.insert_textbox(rect, str(value), fontsize=size, fontname=font, color=color,
                        align=align, lineheight=1.18)


def _header(page: fitz.Page, section: str, snapshot: dict) -> None:
    page.draw_rect(fitz.Rect(0, 0, PAGE.width, 28), color=INK, fill=INK)
    _text(page, fitz.Rect(MARGIN, 8, 290, 22), "STRUCTEVIDENCE / MONITORING SNAPSHOT", 7, WHITE, "hebo")
    _text(page, fitz.Rect(300, 8, PAGE.width - MARGIN, 22), section.upper(), 7, WHITE, "helv", fitz.TEXT_ALIGN_RIGHT)
    page.draw_line(fitz.Point(MARGIN, PAGE.height - 34), fitz.Point(PAGE.width - MARGIN, PAGE.height - 34), color=LINE)
    _text(page, fitz.Rect(MARGIN, PAGE.height - 28, 420, PAGE.height - 12), snapshot["snapshot_id"], 6.5, MUTED)
    _text(page, fitz.Rect(430, PAGE.height - 28, PAGE.width - MARGIN, PAGE.height - 12), f"{page.number + 1}", 6.5, MUTED, align=fitz.TEXT_ALIGN_RIGHT)


def _new_page(doc: fitz.Document, section: str, snapshot: dict) -> tuple[fitz.Page, float]:
    page = doc.new_page(width=PAGE.width, height=PAGE.height)
    _header(page, section, snapshot)
    return page, 50


def _heading(page: fitz.Page, y: float, kicker: str, title: str, note: str = "") -> float:
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 15), kicker.upper(), 7, TEAL, "hebo")
    _text(page, fitz.Rect(MARGIN, y + 16, PAGE.width - MARGIN, y + 48), title, 19, INK, "hebo")
    if note:
        _text(page, fitz.Rect(MARGIN, y + 50, PAGE.width - MARGIN, y + 78), note, 8.5, MUTED)
        return y + 88
    return y + 58


def _rule(page: fitz.Page, y: float) -> None:
    page.draw_line(fitz.Point(MARGIN, y), fitz.Point(PAGE.width - MARGIN, y), color=LINE)


def _label_value(page: fitz.Page, x: float, y: float, width: float, label: str, value: object,
                 note: str = "", accent=TEAL) -> None:
    box = fitz.Rect(x, y, x + width, y + 76)
    page.draw_rect(box, color=LINE, fill=WHITE)
    page.draw_rect(fitz.Rect(x, y, x + width, y + 3), color=accent, fill=accent)
    _text(page, fitz.Rect(x + 9, y + 10, x + width - 9, y + 23), label.upper(), 6.5, MUTED, "hebo")
    _text(page, fitz.Rect(x + 9, y + 27, x + width - 9, y + 48), value, 9, INK, "hebo")
    _text(page, fitz.Rect(x + 9, y + 51, x + width - 9, y + 70), note, 6.5, MUTED)


def _table(page: fitz.Page, y: float, headers: list[str], rows: Iterable[list[object]], widths: list[float],
           row_height: float = 31, font_size: float = 6.8) -> float:
    x = MARGIN
    for header, width in zip(headers, widths):
        page.draw_rect(fitz.Rect(x, y, x + width, y + 25), color=LINE, fill=(0.90, 0.93, 0.92))
        _text(page, fitz.Rect(x + 5, y + 7, x + width - 4, y + 21), header.upper(), 6.2, MUTED, "hebo")
        x += width
    y += 25
    for index, row in enumerate(rows):
        x = MARGIN
        fill = WHITE if index % 2 == 0 else PAPER
        for value, width in zip(row, widths):
            page.draw_rect(fitz.Rect(x, y, x + width, y + row_height), color=LINE, fill=fill)
            _text(page, fitz.Rect(x + 5, y + 6, x + width - 4, y + row_height - 3), value, font_size, INK)
            x += width
        y += row_height
    return y


def _short(value: str, head: int = 14, tail: int = 8) -> str:
    return f"{value[:head]}...{value[-tail:]}"


def render_monitoring_snapshot(snapshot_path: Path, output_path: Path) -> Path:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    metadata = {
        "title": "BNB Monitoring Snapshot v1.0",
        "author": "StructEvidence",
        "subject": "Structural and evidence state monitoring demo",
        "keywords": "DEMO_MONITORING_SNAPSHOT, BNB, MDL, EDL, RTP, GDR",
        "creator": "StructEvidence Monitoring Report Renderer v1.0",
        "creationDate": "D:20260911000000+00'00'",
        "modDate": "D:20260911000000+00'00'",
    }
    doc.set_metadata(metadata)

    page = doc.new_page(width=PAGE.width, height=PAGE.height)
    page.draw_rect(page.rect, color=PAPER, fill=PAPER)
    page.draw_rect(fitz.Rect(0, 0, 18, PAGE.height), color=TEAL, fill=TEAL)
    _text(page, fitz.Rect(MARGIN, 70, PAGE.width - MARGIN, 90), "STRUCTEVIDENCE", 9, TEAL, "hebo")
    _text(page, fitz.Rect(MARGIN, 112, PAGE.width - MARGIN, 205), "BNB Monitoring\nSnapshot", 29, INK, "hebo")
    _text(page, fitz.Rect(MARGIN, 218, PAGE.width - MARGIN, 261), "Structural state, evidence dynamics, event lineage,\nand explicit market-data boundaries", 12, MUTED)
    page.draw_rect(fitz.Rect(MARGIN, 292, PAGE.width - MARGIN, 390), color=INK, fill=INK)
    _text(page, fitz.Rect(MARGIN + 18, 311, PAGE.width - MARGIN - 18, 329), "DEMO_MONITORING_SNAPSHOT", 9, WHITE, "hebo")
    _text(page, fitz.Rect(MARGIN + 18, 340, PAGE.width - MARGIN - 18, 366), "NOT A LIVE PAID REPORT", 16, WHITE, "hebo")
    _text(page, fitz.Rect(MARGIN, 445, 260, 462), "SNAPSHOT AS-OF", 7, MUTED, "hebo")
    _text(page, fitz.Rect(MARGIN, 465, 300, 488), snapshot["snapshot_as_of"], 10, INK, "hebo")
    _text(page, fitz.Rect(320, 445, PAGE.width - MARGIN, 462), "SUBJECT", 7, MUTED, "hebo")
    _text(page, fitz.Rect(320, 465, PAGE.width - MARGIN, 488), snapshot["subject_id"], 10, INK, "hebo")
    _text(page, fitz.Rect(MARGIN, 545, PAGE.width - MARGIN, 602), snapshot["monitoring_boundary"], 11, INK)
    _text(page, fitz.Rect(MARGIN, 690, PAGE.width - MARGIN, 728), "Monitoring is not prediction. Hash identity is not content truth.\nObservation is not causation.", 8.5, AMBER, "hebo")
    _text(page, fitz.Rect(MARGIN, 772, PAGE.width - MARGIN, 792), snapshot["snapshot_id"], 7, MUTED)

    page, y = _new_page(doc, "Snapshot scope", snapshot)
    y = _heading(page, y, "01 / State boundary", "What this snapshot establishes", "State classes remain separate. No score, ranking, price target, or trade instruction is produced.")
    card_width = (PAGE.width - 2 * MARGIN - 12) / 2
    _label_value(page, MARGIN, y, card_width, "Structural Level", snapshot["structural_level"]["overall_state"], "Current observed configuration")
    _label_value(page, MARGIN + card_width + 12, y, card_width, "Structural Delta", snapshot["structural_delta"]["overall_state"], "Change requires valid comparison", TEAL)
    y += 88
    _label_value(page, MARGIN, y, card_width, "Evidence Dynamics", snapshot["evidence_dynamics"]["overall_state"], snapshot["evidence_dynamics"]["ecl_consistency"], AMBER)
    _label_value(page, MARGIN + card_width + 12, y, card_width, "Market Dynamics", snapshot["market_dynamics"]["state"], "No frozen microstructure series", AMBER)
    y += 112
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 22), "Interpretation boundary", 11, INK, "hebo")
    y += 30
    boundaries = [
        ("Integrity", "Artifact hashes bind the exact bytes used; they do not certify that source assertions are true."),
        ("Epistemic axis", "SUPPORTED describes evidentiary support for a recorded event, independently of market response."),
        ("Impact axis", "Market impact remains NOT_MEASURED without a frozen observation window and source series."),
        ("Causality", "The event ledger records temporal order. It does not infer causal market effects."),
        ("Freshness", f"Release state is {snapshot['freshness_snapshot']['release_state']}; currentness is not truth."),
    ]
    for label, value in boundaries:
        _text(page, fitz.Rect(MARGIN, y, 150, y + 18), label.upper(), 7, TEAL, "hebo")
        _text(page, fitz.Rect(150, y, PAGE.width - MARGIN, y + 34), value, 8.2, MUTED)
        y += 43

    page, y = _new_page(doc, "Structural Level and Delta", snapshot)
    y = _heading(page, y, "02 / MDL structural layer", "Observed configuration and established change", "A present Level is not evidence of a Delta. Missing prior comparability is preserved.")
    levels = {row["dimension_id"]: row for row in snapshot["structural_level"]["dimensions"]}
    rows = []
    for delta in snapshot["structural_delta"]["dimensions"]:
        level = levels.get(delta["dimension_id"], {})
        rows.append([delta["dimension_id"], level.get("state", "NOT_OBSERVED"), level.get("effective_at") or "NONE", delta["state"], delta["basis"], delta["comparability_state"]])
    y = _table(page, y, ["Dimension", "Level", "Observed", "Delta", "Basis", "Comparable"], rows, [94, 92, 72, 88, 98, 59], 48, 6.4)
    y += 28
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 21), "Established movement", 11, INK, "hebo")
    y += 28
    established = [row for row in snapshot["structural_delta"]["dimensions"] if row["state"] != "NOT_ESTABLISHED"]
    detail = established[0] if established else None
    if detail:
        _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 70), f"{detail['dimension_id']}: {detail['state']}\nBasis: {detail['basis']}\nEffective at: {detail['effective_at']}", 9, INK)
    else:
        _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 40), "No structural Delta is established in this snapshot.", 9, MUTED)

    events = snapshot["recent_events"]
    for page_index, chunk_start in enumerate(range(0, len(events), 8), start=1):
        page, y = _new_page(doc, f"Information event ledger {page_index}", snapshot)
        y = _heading(page, y, f"03.{page_index} / Append-only events", "Information event ledger", "Epistemic status, market impact, and causal status are deliberately independent fields.")
        rows = []
        for event in events[chunk_start:chunk_start + 8]:
            rows.append([event["known_at"][:10], event["event_id"], event["event_domain"], event["epistemic_status"], event["market_impact_status"], event["causal_status"]])
        _table(page, y, ["Known", "Event ID", "Domain", "Epistemic", "Impact", "Causal"], rows, [58, 118, 86, 76, 85, 80], 55, 6.2)

    page, y = _new_page(doc, "Evidence Dynamics", snapshot)
    y = _heading(page, y, "04 / EDL", "Evidence Dynamics", "Coverage, dependency, review events, and consistency are shown without collapsing them into truth or market effect.")
    evidence = snapshot["evidence_dynamics"]
    card_width = (PAGE.width - 2 * MARGIN - 24) / 3
    cards = [("Claims", evidence["claim_count"]), ("Sources", evidence["source_count"]), ("Dependency groups", evidence["dependency_group_count"])]
    for index, (label, value) in enumerate(cards):
        _label_value(page, MARGIN + index * (card_width + 12), y, card_width, label, value, "Recorded in frozen bundle")
    y += 100
    rows = [[row["family_id"], row["state_after"], row["known_at"][:10], row["observation_mode"]] for row in evidence["events"]]
    y = _table(page, y, ["Evidence family", "State after", "Known", "Mode"], rows, [180, 130, 90, 103], 39, 7)
    y += 22
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 42), f"Source coverage: {evidence['source_coverage']}\nECL consistency: {evidence['ecl_consistency']}", 8.5, INK, "hebo")

    page, y = _new_page(doc, "Market and liquidity boundary", snapshot)
    y = _heading(page, y, "05 / MDL coverage", "Market and liquidity observations", snapshot["market_dynamics"]["reason"])
    flow_rows = [[key, value] for key, value in snapshot["market_dynamics"]["flow8"].items()]
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 20), "FLOW-8", 9, INK, "hebo")
    y = _table(page, y + 24, ["Dimension", "State"], flow_rows, [250, 253], 28, 7.2)
    y += 20
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 20), "LIQUIDITY OBSERVATIONS", 9, INK, "hebo")
    liquidity_rows = [[row["metric"], row["state"], row["observation_window"] or "NONE", "NO INPUT ARTIFACT" if not row["source_refs"] else len(row["source_refs"])] for row in snapshot["liquidity_observations"]]
    _table(page, y + 24, ["Metric", "State", "Window", "Sources"], liquidity_rows, [154, 116, 104, 129], 26, 6.7)

    page, y = _new_page(doc, "GDR and provenance", snapshot)
    y = _heading(page, y, "06 / Runtime boundary", "Authorization and reproducibility", "The monitor adapter governs display and export separately from commercial delivery.")
    gdr = snapshot["gdr_snapshot"]
    _label_value(page, MARGIN, y, PAGE.width - 2 * MARGIN, "GDR authorization", gdr["authorization"], gdr["authorization_id"], AMBER)
    y += 92
    action_rows = [[action, outcome] for action, outcome in gdr["actions"].items()]
    y = _table(page, y, ["Action", "Outcome"], action_rows, [270, 233], 34, 7.2)
    y += 24
    _text(page, fitz.Rect(MARGIN, y, PAGE.width - MARGIN, y + 20), "VERIFICATION KEYS", 9, INK, "hebo")
    y += 25
    checks = [
        ("Snapshot SHA-256", snapshot["snapshot_sha256"]),
        ("Source bundle hash", snapshot["source_bundle_hash"]),
        ("Freshness bundle hash", snapshot["freshness_snapshot"]["input_bundle_hash"]),
        ("Builder", snapshot["builder_version"]),
        ("Schema", snapshot["schema_version"]),
    ]
    for label, value in checks:
        _text(page, fitz.Rect(MARGIN, y, 175, y + 16), label.upper(), 6.5, MUTED, "hebo")
        _text(page, fitz.Rect(175, y, PAGE.width - MARGIN, y + 24), value, 6.7, INK, "cour")
        y += 31
    _rule(page, y + 3)
    _text(page, fitz.Rect(MARGIN, y + 16, PAGE.width - MARGIN, y + 60), "Verify by snapshot ID, subject, or full snapshot hash at structurevidence.org/verify.html. A match establishes artifact identity only.", 8.5, MUTED)

    doc.save(output_path, garbage=4, deflate=True, no_new_id=True)
    doc.close()
    return output_path


def render_cover(pdf_path: Path, output_path: Path, width: int = 640) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf_path) as doc:
        page = doc[0]
        scale = width / page.rect.width
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        pixmap.save(output_path)
    return output_path

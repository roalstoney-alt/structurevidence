#!/usr/bin/env python3
"""Build the public, non-customer 800V DC Decision Pack sample."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1.0.pdf"

INK = colors.HexColor("#132321")
ACCENT = colors.HexColor("#0C6765")
MUTED = colors.HexColor("#536562")
LINE = colors.HexColor("#CDD7D3")
SOFT = colors.HexColor("#E3ECE8")
PAPER = colors.HexColor("#F4F6F3")
WHITE = colors.white
AMBER = colors.HexColor("#9A6700")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="SEKicker", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=ACCENT, spaceAfter=8, tracking=1.2))
styles.add(ParagraphStyle(name="SETitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=31, textColor=INK, alignment=TA_LEFT, spaceAfter=14))
styles.add(ParagraphStyle(name="SEH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=23, textColor=INK, spaceAfter=12))
styles.add(ParagraphStyle(name="SEH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK, spaceBefore=8, spaceAfter=7))
styles.add(ParagraphStyle(name="SEBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.5, textColor=INK, spaceAfter=8))
styles.add(ParagraphStyle(name="SESmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10.5, textColor=MUTED))
styles.add(ParagraphStyle(name="SEStatus", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK))
styles.add(ParagraphStyle(name="SECenter", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=INK, alignment=TA_CENTER))


def p(text, style="SEBody"):
    return Paragraph(text, styles[style])


def status_table(rows):
    data = [[p("EVIDENCE DIMENSION", "SEKicker"), p("CURRENT STATE", "SEKicker"), p("BOUNDARY", "SEKicker")]]
    for label, state, boundary in rows:
        data.append([p(label, "SEStatus"), p(state, "SEStatus"), p(boundary, "SESmall")])
    table = Table(data, colWidths=[47 * mm, 48 * mm, 78 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SOFT),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def info_box(title, body, color=SOFT):
    box = Table([[p(title, "SEH2"), p(body, "SEBody")]], colWidths=[48 * mm, 125 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return box


def page_frame(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, width, height, stroke=0, fill=1)
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, height - 17 * mm, width - 18 * mm, height - 17 * mm)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(INK)
    canvas.drawString(18 * mm, height - 12 * mm, "STRUCTUREEVIDENCE")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 18 * mm, height - 12 * mm, "PUBLIC ILLUSTRATIVE SAMPLE - NOT CUSTOMER ADVICE")
    canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
    canvas.drawString(18 * mm, 9.5 * mm, "Evidence cut-off: 2026-09-20T10:46:47Z")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=21 * mm,
        title="StructureEvidence 800V DC Decision Pack Sample v1.0",
        author="MATRIX ASIA PACIFIC LIMITED / StructureEvidence",
        subject="Illustrative public Decision Pack based on the published 800V DC evidence case",
    )
    story = []

    story.extend([
        Spacer(1, 19 * mm),
        p("DECISION EVIDENCE PACK / PUBLIC SAMPLE", "SEKicker"),
        p("800V DC and SST-based power architecture", "SETitle"),
        p("What does the accepted public evidence establish about commercial field operation for hyperscale data-center power - and what remains unresolved?", "SEH1"),
        Spacer(1, 7 * mm),
        info_box("Current decision state", "One named operator reported commercial operation of a materially relevant 10kV AC to SST to 800VDC architecture at one named campus. This establishes a single observed instance. It does not establish broad adoption, independent performance validation, or repeat procurement."),
        Spacer(1, 8 * mm),
        p("This five-page artifact demonstrates the structure of a customer-facing Decision Pack using only already-public evidence. It is not a customer deliverable, engineering design, safety opinion, procurement recommendation, or claim of full PDRE validation."),
        Spacer(1, 5 * mm),
        p("Prepared by", "SEKicker"),
        p("StructureEvidence - operated by MATRIX ASIA PACIFIC LIMITED<br/>Responsible researcher: Stone Zhu<br/>Commercial contact: support@structevidence.com", "SEBody"),
        Spacer(1, 12 * mm),
        p("VERSION 1.0 / PUBLIC / CUSTOMER-NEUTRAL", "SEKicker"),
        PageBreak(),
    ])

    story.extend([
        p("01 / EXECUTIVE DECISION FRAME", "SEKicker"),
        p("What can be defended at the cut-off?", "SEH1"),
        p("Decision affected: whether public evidence is sufficient to treat 800V DC / SST architecture as commercially field-operated in at least one hyperscale data-center setting."),
        status_table([
            ("Architecture possibility", "SUPPORTED", "Public records support technical architecture and system demonstrations."),
            ("System validation", "SUPPORTED", "Source-reported demonstrations; performance claims remain attributed."),
            ("Named field deployment", "OBSERVED - SINGLE INSTANCE", "One named operator and one named campus."),
            ("Long operating history", "UNKNOWN", "Initial commercial operation does not establish duration or reliability."),
            ("Multi-entity replication", "UNKNOWN", "No accepted independent operator replication in the approved packet."),
            ("Independent validation", "UNKNOWN", "The qualifying source is an operator publication, not a third-party audit."),
            ("Repeat procurement", "UNKNOWN", "No accepted evidence of repeat buying behavior."),
            ("Industry-scale adoption", "NOT ESTABLISHED", "One observed instance and standards activity do not establish broad adoption."),
        ]),
        Spacer(1, 6 * mm),
        info_box("Decision implication", "The narrow field-operation claim may move from NOT ESTABLISHED to EVIDENCE ACCEPTED - SINGLE INSTANCE. Any broader claim about reliability, qualification, replication, economics, or industry adoption remains unsupported or unresolved."),
        PageBreak(),
    ])

    story.extend([
        p("02 / EVIDENCE AND COUNTER-EVIDENCE", "SEKicker"),
        p("Why one record qualifies and two do not", "SEH1"),
        p("Qualifying evidence", "SEH2"),
        status_table([
            ("Record", "HUMAN REVIEW ACCEPTED", "L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001"),
            ("Publisher", "CHINDATA", "Primary operator publication dated 2026-07-02."),
            ("Environment", "NAMED CAMPUS", "Chindata Sangyuan Cloud Computing Campus near Beijing."),
            ("Architecture", "10kV AC - SST - 800VDC", "Reported commercial operation of an SST-based intelligent DC power system."),
            ("Supports", "ONE FIELD INSTANCE", "One named operator, one named campus, materially relevant architecture."),
            ("Does not support", "BROADER CLAIMS", "No independent performance audit, operating history, replication, repeat procurement, or industry adoption."),
        ]),
        Spacer(1, 5 * mm),
        p("Preserved counter-evidence", "SEH2"),
        status_table([
            ("Vertiv path", "PLANNED DEPLOYMENT", "Future commercialization, customer pilots, and ramp do not prove current field operation."),
            ("Siemens + Reinhausen", "UNDER DEVELOPMENT", "Development for future deployment does not prove current field operation."),
        ]),
        Spacer(1, 5 * mm),
        p("Primary source: <link href='https://www.chindatagroup.com/media/news/533.html' color='#0C6765'>Chindata operator publication</link>. Public evidence case: <link href='https://structurevidence.org/cases/800vdc/' color='#0C6765'>structurevidence.org/cases/800vdc/</link>.", "SESmall"),
        PageBreak(),
    ])

    story.extend([
        p("03 / DEPENDENCY AND QUALIFICATION GAP MAP", "SEKicker"),
        p("A field instance does not qualify every subsystem", "SEH1"),
        status_table([
            ("SST", "FIELD DEPLOYED - SINGLE INSTANCE", "Named 10kV-to-800VDC commercial-operation record."),
            ("SiC / GaN", "UNKNOWN", "No accepted item-level state in the approved public packet."),
            ("HF transformer / magnetics", "UNKNOWN", "No accepted item-level state."),
            ("Insulation / partial discharge", "UNKNOWN", "Transferred dependency; qualification evidence absent."),
            ("Thermal management", "UNKNOWN", "Transferred dependency; qualification evidence absent."),
            ("DC protection / SSCB", "WATCH", "New critical dependency; no subsystem qualification inferred."),
            ("Power rack / sidecar", "SYSTEM VALIDATION", "Source-reported demonstrations support sample-bench-tested state only."),
            ("Busbar / connectors", "UNKNOWN", "Transferred dependency; item-level evidence absent."),
            ("Standards / certification", "DEVELOPMENT", "Draft work does not establish completed certification."),
        ]),
        Spacer(1, 6 * mm),
        info_box("Qualification boundary", "A decision to investigate or pilot the architecture is not the same as a decision to deploy it. Customer-specific load, protection, insulation, thermal, maintainability, safety, and certification requirements remain outside this public sample."),
        PageBreak(),
    ])

    story.extend([
        p("04 / ACTION OPTIONS AND SERVICE-CYCLE CONTROL", "SEKicker"),
        p("What could move the decision next?", "SEH1"),
        status_table([
            ("Operating history", "VERIFY", "Seek dated attributable reliability and operating-history records for the named system."),
            ("Replication", "VERIFY", "Seek field-operation records from additional independent operators."),
            ("Independent validation", "VERIFY", "Seek third-party evidence against defined performance and safety requirements."),
            ("Repeat procurement", "VERIFY", "Seek attributable repeat order or additional commissioned procurement."),
            ("Industry adoption", "DO NOT INFER", "Require multi-entity field evidence across a defined market boundary."),
        ]),
        Spacer(1, 6 * mm),
        p("Recommended bounded action", "SEH2"),
        p("If the immediate decision is whether one commercial field instance exists, stop: the accepted record answers that narrow question. If the decision is procurement, qualification, or broad market adoption, authorize only the specific missing evidence capable of changing that decision."),
        Spacer(1, 5 * mm),
        info_box("Evidence cut-off and revisions", "This sample is frozen at 2026-09-20T10:46:47Z. No revision rounds are included. Evidence published later belongs to a separately purchased collection cycle. When a subsequent cycle is purchased, qualifying new evidence is incorporated and any superseded state is corrected within that new delivery."),
        Spacer(1, 7 * mm),
        p("COMMERCIAL BOUNDARY", "SEKicker"),
        p("Payment purchases defined research scope, review, and delivery. It does not purchase a preferred finding. Customer submission does not authorize research. Customer documents remain private unless separately authorized for publication."),
        Spacer(1, 4 * mm),
        p("This public sample is illustrative and customer-neutral. Contract, formal quotation, invoice, exact scope, cut-off timestamp, confidentiality, and delivery terms are confirmed before payment.", "SESmall"),
    ])

    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    print(OUTPUT)


if __name__ == "__main__":
    build()

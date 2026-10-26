#!/usr/bin/env python3
"""Build deterministic SE-LISTED-PROJECT-TRACKER-IREN-001 draft artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from listed_project_tracker_iren_v01 import append_event, canonical_bytes, digest, seal, validate_events, validate_tracker

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("research/internal/listed-projects/iren")
CAPTURE = "2026-10-26T01:56:24Z"
CUTOFF = "2026-10-26"
METHOD = "listed-project-tracker-financial-extension-v0.1"
BASELINE = "305bbef43f2ccdef9d025ac802dfca6b6ad6a8df"


def source(
    source_id: str,
    accession: str | None,
    url: str,
    issuer: str,
    publication_date: str,
    dependency: str,
    liability: str,
    access_status: str = "TEXT_REVIEWED_VIA_BROWSER_RAW_CAPTURE_FAILED",
    sha256: str | None = None,
    byte_capture_status: str = "RETRIEVAL_FAILED",
) -> dict:
    item = {
        "source_id": source_id,
        "accession": accession,
        "url": url,
        "issuer": issuer,
        "publication_date": publication_date,
        "capture_date": CAPTURE,
        "sha256": sha256,
        "hash_scope": "RAW_RESPONSE_BYTES" if sha256 else "UNAVAILABLE_RAW_BYTES_NOT_CAPTURED",
        "access_status": access_status,
        "access_boundary": (
            "Readable as parsed public text during review; direct raw-byte retrieval returned HTTP 403, "
            "so no source-byte digest is asserted."
            if sha256 is None
            else "Raw response bytes captured from the source-originator URL."
        ),
        "byte_capture_status": byte_capture_status,
        "dependency_class": dependency,
        "liability_regime": liability,
        "review_status": "CODEX_REVIEW_COMPLETE_PENDING_REAL_HUMAN_REVIEW",
    }
    item["record_sha256"] = digest(item)
    return item


SOURCES = [
    source(
        "IREN-S02", "0001140361-24-006216",
        "https://www.sec.gov/Archives/edgar/data/1878848/000114036124006216/ef20021117_ex99-1.htm",
        "Iris Energy Limited", "2024-02-08", "ISSUER_AUTHORED", "FURNISHED",
    ),
    source(
        "IREN-S03", "0001140361-24-018471",
        "https://www.sec.gov/Archives/edgar/data/1878848/000114036124018471/ef20026364_6k.htm",
        "Iris Energy Limited", "2024-04-08", "ISSUER_AUTHORED", "FURNISHED",
    ),
    source(
        "IREN-S04", "0001628280-24-038677",
        "https://www.sec.gov/Archives/edgar/data/1878848/000162828024038677/iren-20240630.htm",
        "IREN Limited", "2024-08-28", "ISSUER_AUTHORED", "FILED",
    ),
    source(
        "IREN-S05", "0001140361-25-040072",
        "https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm",
        "IREN Limited", "2025-11-03", "ISSUER_AUTHORED", "FILED",
    ),
    source(
        "IREN-S06", "0001878848-26-000015",
        "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000015/iren-20251231.htm",
        "IREN Limited", "2026-02-05", "ISSUER_AUTHORED", "FILED",
    ),
    source(
        "IREN-S07", "0001140361-26-028871",
        "https://www.sec.gov/Archives/edgar/data/1878848/000114036126028871/ef20078253_ex99-1.htm",
        "IREN Limited", "2026-07-20", "ISSUER_AUTHORED", "FURNISHED",
    ),
    source(
        "IREN-S08", "0001140361-26-032638",
        "https://www.sec.gov/Archives/edgar/data/1878848/000114036126032638/ef20080141_ex99-1.htm",
        "IREN Limited", "2026-08-13", "ISSUER_AUTHORED", "FURNISHED",
    ),
    source(
        "IREN-S09", "0001878848-26-000051",
        "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000051/irenreportsfy26results.htm",
        "IREN Limited", "2026-08-27", "ISSUER_AUTHORED", "FURNISHED",
    ),
    source(
        "IREN-S10", "0001878848-26-000052",
        "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000052/iren-20260630.htm",
        "IREN Limited", "2026-08-27", "ISSUER_AUTHORED", "FILED",
    ),
    source(
        "IREN-S11", None,
        "https://nvidianews.nvidia.com/_gallery/download_pdf/69fcf77b3d6332af6ab94912/",
        "NVIDIA Corporation and IREN Limited", "2026-05-07", "PARTIALLY_DEPENDENT", "UNFILED",
        access_status="RAW_BYTES_CAPTURED_AND_TEXT_REVIEWED",
        sha256="a77aab4585b2ce334e6cc0a40b2bc1f1121dda90e875e44dbe0b68736be45c97",
        byte_capture_status="CAPTURED",
    ),
    source(
        "IREN-S12", None, "https://www.iren.com/investors/sec-filings",
        "IREN Limited", "2026-10-26", "ISSUER_AUTHORED", "UNFILED",
        access_status="RAW_BYTES_CAPTURED_AND_INDEX_METADATA_REVIEWED",
        sha256="0135337d188cb46f00803d3fc727a648459b13f7789d3e611b1483b72080cb77",
        byte_capture_status="CAPTURED",
    ),
]

PRIOR_CASE = {
    "case_id": "SE-NEW-BUSINESS-001",
    "url": "https://raw.githubusercontent.com/roalstoney-alt/se-dual-case-public/main/SE-NEW-BUSINESS-001.md",
    "evidence_cutoff": "2026-10-21",
    "capture_date": CAPTURE,
    "sha256": "96507322272876e5b6dba8e788e626ac9fdc0fd9b6a29485783d072e90f5176d",
    "access_status": "RAW_BYTES_CAPTURED",
    "prior_review_state": "LOCAL_PROVISIONAL_v0.1_HUMAN_REVIEW_REQUIRED",
    "evidentiary_role": "DERIVED_BASELINE_NOT_A_QUALIFYING_PRIMARY_SOURCE",
    "packet_boundary": "Prior draft reports two older Source Bridge copies as not independently authenticated; this build does not promote those copies or overwrite the draft.",
}


def attrs(dependency: str, liability: str, assurance: str, scope: str, stages: list[str]) -> dict:
    return {
        "source_dependency": dependency,
        "liability_regime": liability,
        "assurance": assurance,
        "assurance_scope": scope,
        "disclosure_stages": stages,
    }


def claim(
    claim_id: str,
    state: str,
    text: str,
    source_ids: list[str],
    period: str,
    financial_attributes: dict,
    qualifying: str,
    contradictory: str,
    missing: str,
    what: str,
    prior: str | None = None,
) -> dict:
    source_map = {item["source_id"]: item for item in SOURCES}
    return {
        "claim_id": claim_id,
        "state": state,
        "plain_language_record": text,
        "source_ids": source_ids,
        "source_record_sha256": [source_map[item]["record_sha256"] for item in source_ids],
        "period": period,
        "evidence_cutoff": CUTOFF,
        "method_version": METHOD,
        "financial_attributes": financial_attributes,
        "qualifying_evidence": qualifying,
        "contradictory_evidence": contradictory,
        "missing_condition": missing,
        "what_would_change_it": what,
        "next_check": "Next accessible material SEC filing or source-originator disclosure; no automatic publication.",
        "reviewer_identity": "Codex implementation review; no second real human reviewer recorded",
        "review_status": "PENDING_REAL_HUMAN_REVIEW",
        "prior_version": prior,
        "client_action": "UNSPECIFIED",
    }


FS_SCOPE = "Audited consolidated financial statements and notes only; no audit is inferred for other annual-report narrative."
UNAUDITED = "Issuer disclosure; no independent assurance inferred."
CLAIMS = [
    claim("IREN-C001", "SUPPORTED_AS_ATTRIBUTED", "IREN reported that Poolside service began on 2024-02-05 under an initial three-month agreement covering 248 H100 GPUs.", ["IREN-S02"], "2024-02", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D1", "D2"]), "The issuer-furnished release states the agreement, GPU count and service commencement.", "No contradictory primary source was identified in the reviewed scope.", "Customer-authored operational record and economics were not captured.", "A Poolside-originated dated record or independently observable service record would add D4b without changing the historic issuer attribution."),
    claim("IREN-C002", "SUPPORTED_AS_ATTRIBUTED", "IREN reported an April 2024 expansion from 248 to 504 H100 GPUs for an additional four-month term, with a further two-month customer option.", ["IREN-S03"], "2024-04", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D1"]), "The furnished Form 6-K exhibit states the expanded quantity and time-limited terms.", "No contradictory primary source was identified in the reviewed scope.", "Exercise of the optional extension is not established by this document.", "A dated source record establishing exercise or expiry of the option would update this bounded history."),
    claim("IREN-C003", "SUPPORTED_AS_ATTRIBUTED", "IREN's FY2024 annual filing states the Poolside arrangement was subsequently extended to 2024-08-30.", ["IREN-S04"], "FY2024", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", "Filed annual-report narrative; the specific contract sentence is not classified as audited financial-statement content.", ["D1"]), "The filed annual report contains the dated historic contract narrative.", "No contradictory primary source was identified in the reviewed scope.", "Current or later renewal is not established.", "A later primary document with an explicit Poolside term would update, not overwrite, the historic entry."),
    claim("IREN-C004", "SUPPORTED_AS_ATTRIBUTED", "IREN reported a Microsoft GPU-services agreement with approximately USD 9.7bn total contract value through 2031, four Horizon tranches representing about 200MW and tranche-specific 20% prepayment terms.", ["IREN-S05", "IREN-S06"], "2025-11 onward", attrs("ISSUER_AUTHORED", "FILED", "REVIEWED_INTERIM", "Material-agreement disclosure is filed; later 10-Q financial statements are reviewed interim. Neither makes the headline value recognized revenue.", ["D1"]), "The filed Item 1.01 disclosure and later 10-Q describe the agreement and contingencies.", "No contradictory primary source was identified in the reviewed scope.", "Full performance, revenue recognition and cash collection remain distinct.", "Financial statements showing recognized revenue or cash, and tranche-specific acceptance records, would change only their respective dimensions."),
    claim("IREN-C005", "SUPPORTED_AS_ATTRIBUTED", "IREN reported that Horizon 1 was delivered to and accepted by Microsoft in August 2026.", ["IREN-S08", "IREN-S09", "IREN-S10"], "2026-08", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", "The direct acceptance assertion is in furnished issuer material; annual-report repetition does not create a Microsoft-authored confirmation.", ["D2"]), "The issuer's August 13 release and FY26 materials repeat the delivery-and-acceptance assertion.", "No Microsoft-authored acceptance record was captured in the reviewed scope.", "D4b customer-authored confirmation remains unestablished.", "A dated Microsoft-originated acceptance record identifying Horizon 1 and acceptance scope would establish D4b."),
    claim("IREN-C006", "SUPPORTED_AS_ATTRIBUTED", "As of 2026-08-27, IREN described Horizon 2 as commissioning and Horizons 3-4 as in late-stage construction, with Q4 2026 delivery targets subject to contractual grace and acceptance conditions.", ["IREN-S09", "IREN-S10"], "2026-08-27", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D0"]), "The FY26 release and annual-report narrative distinguish then-current construction states from targeted delivery.", "The documents do not state that Horizons 2-4 had been accepted by the cutoff.", "Delivery and acceptance of Horizons 2-4 remain unestablished.", "Tranche-specific dated delivery and acceptance evidence would update each Horizon independently."),
    claim("IREN-C007", "SUPPORTED_AS_ATTRIBUTED", "IREN's audited FY2026 financial statements report total revenue of USD 707.007m.", ["IREN-S10"], "FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D3"]), "The consolidated statements report total revenue of USD 707.007m.", "No contradictory audited figure was identified.", "The figure does not represent Microsoft contract value or cash collected.", "A filed restatement or correction would supersede this record append-only."),
    claim("IREN-C008", "SUPPORTED_AS_ATTRIBUTED", "IREN's audited FY2026 segment disclosure reports AI Cloud Services revenue of USD 128.795m (rounded to USD 128.8m in the results release).", ["IREN-S09", "IREN-S10"], "FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D3"]), "The annual filing supplies the financial-statement amount; the furnished release supplies the rounded presentation.", "No contradictory audited figure was identified.", "Recognized segment revenue does not establish contract value collection or segment profitability.", "A filed restatement or later audited comparative would update the record."),
    claim("IREN-C009", "SUPPORTED_AS_ATTRIBUTED", "IREN's audited FY2026 financial statements report a net loss of USD 702.6m.", ["IREN-S10"], "FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D3"]), "The audited consolidated statements report the loss.", "No contradictory audited figure was identified.", "This company-level measure is not an AI Cloud project return measure.", "A filed restatement or later audited comparative would update the record."),
    claim("IREN-C010", "SUPPORTED_AS_ATTRIBUTED", "IREN's FY2026 audited financial statements record USD 638.8m of impairment of assets; IREN attributes it primarily to decommissioned Bitcoin-mining hardware.", ["IREN-S09", "IREN-S10"], "FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", "The impairment amount is within audited financial statements; management's causal narrative is attributed and not separately assured.", ["D3"]), "The filing reports the amount and the release supplies management's explanation.", "No contradictory audited amount was identified.", "Impairment is non-cash accounting expense and not equivalent to project cash expenditure.", "A filed restatement or note-level reclassification would update the record."),
    claim("IREN-C011", "SUPPORTED_AS_ATTRIBUTED", "IREN's furnished FY26 release defines approximately USD 1bn operating ARR as of 2026-08-26 and targets approximately USD 4bn contracted ARR for 2026 capacity; both are non-GAAP operating metrics and not recognized revenue.", ["IREN-S07", "IREN-S09"], "2026-07 to 2026-08", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D0"]), "The July and August furnished releases give definitions, dates and commissioning/acceptance caveats.", "The July wording is a year-end target, while August distinguishes operating ARR today from contracted ARR; the difference is logged as definition drift, not silently reconciled.", "Neither measure by itself establishes GAAP revenue or cash.", "Subsequent filings using reconciled definitions and recognized revenue would update the applicable dimension."),
    claim("IREN-C012", "SUPPORTED_AS_ATTRIBUTED", "IREN reported USD 3.6bn of Microsoft-related GPU financing commitments; as of 2026-06-30 the filed annual report states USD 413m drawn under the DDTL and USD 525m of USPP notes funded.", ["IREN-S09", "IREN-S10"], "2026-06-30", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", "Drawn/funded debt balances and notes are within audited financial statements; release-level financing labels remain issuer presentation.", ["D1", "D3"]), "The filing separates commitments from amounts drawn or funded at the balance-sheet date.", "The full USD 3.6bn was not shown as drawn at that date.", "Later drawdowns and use of proceeds remain time-specific.", "Subsequent filed debt notes showing drawdowns and balances would update the funding state."),
    claim("IREN-C013", "SUPPORTED_AS_ATTRIBUTED", "IREN and NVIDIA described a conditional five-year right for NVIDIA to invest up to USD 2.1bn in IREN shares; this record does not treat the right as exercised or funds received.", ["IREN-S10", "IREN-S11"], "2026-05 onward", attrs("PARTIALLY_DEPENDENT", "UNDETERMINED", "NOT_APPLICABLE", "The source packet combines a filed issuer record with a NVIDIA-hosted joint release; their legal treatments remain source-specific and no audit or completed investment is inferred.", ["D1"]), "The NVIDIA-hosted joint release corroborates the existence and conditional nature of the investment right as a counterparty-originator record; it is not classified as D4b customer-authored acceptance.", "No reviewed source establishes full exercise or USD 2.1bn receipt.", "Exercise, share issuance and cash receipt remain unestablished.", "A filed issuance record and financial statements showing proceeds would establish the applicable facts."),
    claim("IREN-N001", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "A Microsoft-authored Horizon 1 acceptance record was not captured within the reviewed scope.", ["IREN-S08", "IREN-S09"], "through 2026-10-26", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D2"]), "IREN attributes acceptance to Microsoft.", "No customer-originated document was captured.", "D4b is absent from the reviewed packet, not asserted globally nonexistent.", "A Microsoft-authored dated document that identifies Horizon 1 and its acceptance boundary."),
    claim("IREN-N002", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "Delivery or acceptance of Horizons 2-4 is not established by the reviewed cutoff.", ["IREN-S09", "IREN-S10"], "through 2026-10-26", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D0"]), "Issuer material describes commissioning/construction and targets.", "Targets and grace periods are not completed acceptance.", "Tranche-specific D2 and D4b conditions are missing.", "Dated issuer delivery evidence plus separately classified customer-authored acceptance evidence for each tranche."),
    claim("IREN-N003", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "The approximately USD 9.7bn Microsoft contract value is not established as recognized revenue or cash collected.", ["IREN-S05", "IREN-S06", "IREN-S10"], "through FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D1"]), "The agreement and accounting policies distinguish contract value, RPO, revenue and prepayments.", "The reviewed financial statements do not recognize the full headline value as revenue or cash.", "D3 and D4a for the full value are absent.", "Period-specific audited revenue and cash-flow/deferred-revenue records attributable under applicable accounting rules."),
    claim("IREN-N004", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "Contracted ARR and operating ARR are not established as equivalent to GAAP revenue.", ["IREN-S07", "IREN-S09", "IREN-S10"], "through FY2026", attrs("ISSUER_AUTHORED", "FURNISHED", "UNAUDITED_DISCLOSURE", UNAUDITED, ["D0"]), "Issuer footnotes explicitly state ARR is not GAAP revenue and recognized revenue may be materially lower.", "The audited FY2026 revenue figures differ in definition and measurement period.", "A metric identity is contradicted by the issuer's definitions.", "Only period-specific GAAP financial statements establish recognized revenue; they would not retroactively redefine ARR."),
    claim("IREN-N005", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "The NVIDIA investment right is not established as exercised, shares issued or cash received.", ["IREN-S10", "IREN-S11"], "through 2026-10-26", attrs("PARTIALLY_DEPENDENT", "UNDETERMINED", "NOT_APPLICABLE", "The packet combines filed and unfiled source treatments; the conditional right is not a customer-acceptance claim.", ["D1"]), "The right and conditions are disclosed by both parties.", "No exercise or funding record was captured.", "D4a is absent.", "Filed issuance details and financial statements showing proceeds, each with dates and amounts."),
    claim("IREN-N006", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "The full USD 3.6bn Microsoft-related financing is not established as drawn and funded as of 2026-06-30.", ["IREN-S09", "IREN-S10"], "2026-06-30", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D1", "D3"]), "The audited note reports lower drawn/funded amounts at the balance-sheet date.", "Commitment capacity is distinct from funded principal.", "Later drawdown status is not established by the FY2026 date.", "A later filed debt note showing the exact amount drawn and funded."),
    claim("IREN-N007", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "Sustainable AI Cloud project economics or investor ROI are not established by the reviewed sources.", ["IREN-S09", "IREN-S10"], "through FY2026", attrs("ISSUER_AUTHORED", "FILED", "AUDITED_FINANCIAL_STATEMENT", FS_SCOPE, ["D3"]), "Revenue, loss, impairment and financing facts are available.", "Company-level and segment disclosures do not establish a complete project return calculation after all relevant costs and capital.", "A bounded project-level denominator, cost allocation, cash flows and time horizon are absent.", "Audited or independently verifiable project-level cash flows and costs under a predeclared method."),
    claim("IREN-N008", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE", "A Poolside renewal or continuing service after 2024-08-30 is not established by the reviewed packet.", ["IREN-S03", "IREN-S04"], "after 2024-08-30", attrs("ISSUER_AUTHORED", "FILED", "NOT_APPLICABLE", "Historic contract boundary only.", ["D1"]), "The annual filing records a finite historic extension.", "No later Poolside-specific primary record was captured.", "A later term is absent within scope.", "A dated Poolside or IREN primary record identifying a later renewal, service period and scope."),
]


TRACKER = seal({
    "project": "SE-LISTED-PROJECT-TRACKER-IREN-001",
    "case_id": "SE-NEW-BUSINESS-001",
    "record_version": "v0.1",
    "baseline_main_sha": BASELINE,
    "evidence_cutoff": CUTOFF,
    "publication_status": "INTERNAL_DRAFT_NOT_PUBLICLY_ACTIVATED",
    "human_gate": "PENDING_OWNER_AND_REAL_HUMAN_REVIEW",
    "case_state_changed": False,
    "authority_boundary": "Attributable, time-bounded evidence record; not authoritative truth, a rating or investment advice.",
    "claims": CLAIMS,
})


BET_REGISTER = seal({
    "project": "SE-LISTED-PROJECT-TRACKER-IREN-001",
    "record_version": "v0.1",
    "evidence_cutoff": CUTOFF,
    "publication_status": "INTERNAL_DRAFT_NOT_PUBLICLY_ACTIVATED",
    "commitments": [
        {
            "commitment_id": "IREN-BET-001", "project_id": "HORIZON-1-4", "issuer": "IREN Limited",
            "disclosed_commitment": "Provide Microsoft dedicated GPU services across four Horizon facilities, subject to delivery, acceptance and other contract terms.",
            "commitment_date": "2025-11-02", "capital_amount": {"amount_usd": 5800000000, "meaning": "anticipated GPU-related capital expenditure stated by issuer; not actual spend"},
            "project_milestones": ["Horizon 1 issuer-reported delivered/accepted", "Horizon 2 commissioning as of 2026-08-27", "Horizons 3-4 late-stage construction as of 2026-08-27"],
            "dependent_claim_ids": ["IREN-C004", "IREN-C005", "IREN-C006", "IREN-C012", "IREN-N001", "IREN-N002", "IREN-N003", "IREN-N006"],
            "unestablished_conditions": ["Microsoft-authored Horizon 1 confirmation", "Horizons 2-4 delivery and acceptance", "full contract revenue and cash realization", "full financing drawdown"],
            "decision_owner": "UNKNOWN", "evidence_cutoff": CUTOFF,
            "next_review_trigger": "A material filing, tranche delivery/acceptance source, or financial-statement update.",
            "client_defined_threshold": "UNSPECIFIED", "client_action": "UNSPECIFIED",
        },
        {
            "commitment_id": "IREN-BET-002", "project_id": "NVIDIA-STRATEGIC-PARTNERSHIP", "issuer": "IREN Limited",
            "disclosed_commitment": "Conditional strategic partnership and NVIDIA investment right associated with GPU-delivery and regulatory conditions.",
            "commitment_date": "2026-05-07", "capital_amount": {"amount_usd": 2100000000, "meaning": "maximum conditional investment right; not funds received"},
            "project_milestones": ["Joint source-originator announcement", "Investment right disclosed"],
            "dependent_claim_ids": ["IREN-C013", "IREN-N005"],
            "unestablished_conditions": ["right exercise", "share issuance", "cash receipt"],
            "decision_owner": "UNKNOWN", "evidence_cutoff": CUTOFF,
            "next_review_trigger": "A filed issuance, exercise notice or financial-statement proceeds disclosure.",
            "client_defined_threshold": "UNSPECIFIED", "client_action": "UNSPECIFIED",
        },
    ],
    "same_evidence_different_questions": {
        "manufacturer_or_operator": "Which equipment, power, commissioning and acceptance dependencies remain open?",
        "financier_or_board": "Which commitments are contracted, funded, drawn, recognized or still conditional?",
        "buyer_or_technical_user": "Which capacity has been delivered and accepted under defined service conditions?",
        "interpretation": "Questions only; no recommendation, inferred exposure or client action.",
    },
})


def build_events() -> list[dict]:
    events: list[dict] = []
    drafts = [
        {"event_id": "IREN-EVT-001", "event_type": "DRAFT_INITIALIZED", "observed_at": CAPTURE, "evidence_date": CUTOFF, "summary": "Internal human-gated pilot record initialized from frozen baseline.", "source_ids": []},
        {"event_id": "IREN-EVT-002", "event_type": "SOURCE_REVIEW", "observed_at": CAPTURE, "evidence_date": CUTOFF, "summary": "Eleven primary/source-originator records reviewed; nine SEC raw-byte captures failed while parsed text remained reviewable, and two originator-hosted resources were captured and hashed.", "source_ids": [item["source_id"] for item in SOURCES]},
        {"event_id": "IREN-EVT-003", "event_type": "CLAIMS_CLASSIFIED", "observed_at": CAPTURE, "evidence_date": CUTOFF, "summary": "Claims classified without changing the existing public case state.", "source_ids": ["IREN-S08", "IREN-S09", "IREN-S10"]},
        {"event_id": "IREN-EVT-004", "event_type": "DEFINITION_DRIFT", "observed_at": CAPTURE, "evidence_date": "2026-07-20/2026-08-27", "summary": "July ARR target wording and August contracted-versus-operating ARR wording preserved separately; no silent reconciliation.", "source_ids": ["IREN-S07", "IREN-S09"]},
        {"event_id": "IREN-EVT-005", "event_type": "SNAPSHOT_SEALED", "observed_at": CAPTURE, "evidence_date": CUTOFF, "summary": "Deterministic v0.1 draft sealed pending real human and owner review.", "source_ids": ["IREN-S10", "IREN-S11", "IREN-S12"]},
    ]
    for draft in drafts:
        events = append_event(events, draft)
    return events


EVENTS = build_events()


def tracker_markdown() -> str:
    supported = [item for item in CLAIMS if item["state"] == "SUPPORTED_AS_ATTRIBUTED"]
    missing = [item for item in CLAIMS if item["state"] == "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE"]
    lines = [
        "# IREN listed-project tracker · internal draft v0.1", "",
        "> INTERNAL DRAFT · NOT PUBLICLY ACTIVATED · PENDING REAL HUMAN REVIEW", "",
        "This record organizes what named sources state within a 2026-10-26 cutoff. It is not authoritative truth, a company judgment, a rating, an investment recommendation, or a client decision. Existing case status remains unchanged.", "",
        "## Supported as attributed", "",
    ]
    for item in supported:
        lines += [f"### {item['claim_id']}", "", item["plain_language_record"], "", f"Sources: {', '.join(item['source_ids'])}. Stages: {', '.join(item['financial_attributes']['disclosure_stages'])}. Review: {item['review_status']}.", ""]
    lines += ["## Not established within reviewed scope", ""]
    for item in missing:
        lines += [f"### {item['claim_id']}", "", item["plain_language_record"], "", f"Boundary: {item['missing_condition']}", ""]
    lines += ["## What would change the record", ""]
    for item in missing:
        lines.append(f"- **{item['claim_id']}:** {item['what_would_change_it']}")
    lines += ["", "## Same evidence, different questions", "", "- Manufacturer/operator: Which equipment, power, commissioning and acceptance dependencies remain open?", "- Financier/board: Which commitments are contracted, funded, drawn, recognized or still conditional?", "- Buyer/technical user: Which capacity has been delivered and accepted under defined service conditions?", "", "These are questions, not recommendations or inferred client exposure.", "", "## Append-only change log", ""]
    for event in EVENTS:
        lines.append(f"- **{event['event_id']} · {event['event_type']}** — {event['summary']} (`{event['event_sha256']}`)")
    lines += ["", f"Snapshot SHA-256: `{TRACKER['snapshot_sha256']}`", ""]
    return "\n".join(lines)


def source_report() -> str:
    lines = [
        "# IREN primary-source inventory and provenance", "",
        f"Capture time: {CAPTURE}. Evidence cutoff: {CUTOFF}.", "",
        "SEC pages were readable through the browser research path. Separate direct raw-byte capture attempts returned HTTP 403 for the nine SEC evidence records; those records therefore have `sha256: null` and an explicit `RETRIEVAL_FAILED` byte-capture status. This is an access boundary, not evidence that a source does not exist. The NVIDIA-hosted PDF and IREN filings index were captured and hashed.", "",
        "| Source | Accession | Published | Liability | Access | Raw SHA-256 |", "|---|---|---:|---|---|---|",
    ]
    for item in SOURCES:
        lines.append(f"| {item['source_id']} | {item['accession'] or 'N/A'} | {item['publication_date']} | {item['liability_regime']} | {item['access_status']} | `{item['sha256'] or 'UNAVAILABLE'}` |")
    lines += ["", "Legal treatment is recorded at the source or exhibit level. In particular, the 2026-07-20, 2026-08-13 and 2026-08-27 Exhibit 99.1 disclosures are furnished. Audit assurance is not extended from FY2026 financial statements to all annual-report narrative.", "", "## Prior case and packet boundary", "", f"The external `SE-NEW-BUSINESS-001` draft was captured at `{PRIOR_CASE['sha256']}` with prior state `{PRIOR_CASE['prior_review_state']}`. It is inventoried as derived baseline work, not used as qualifying primary evidence and not modified. Its note that two older Source Bridge copies were not independently authenticated remains preserved as a packet limitation.", ""]
    return "\n".join(lines)


WEEKLY = """# IREN weekly digest draft template v0.1

Status: INTERNAL DRAFT / HUMAN REVIEW REQUIRED / NO AUTOMATIC DISTRIBUTION

- Review window: `[START]` to `[END]`
- Sources actually checked: `[SOURCE_IDS_AND_URLS]`
- Access failures and censored checks: `[COUNT_AND_REASON]`
- Eligible material events: `[DENOMINATOR]`
- Qualifying changes: `[COUNT]`
- No qualifying change: `[YES/NO — state checked scope and date, never add speculation]`
- Claim deltas: `[OLD_RECORD -> APPEND_ONLY_EVENT -> CANDIDATE_RECORD]`
- Definition changes: `[NONE/DETAIL]`
- Contradictory or superseding evidence: `[NONE/DETAIL]`
- Human reviewer: `[NAME/NOT_ASSIGNED]`
- Publication candidate: `[NO/PENDING_OWNER_APPROVAL]`

Workflow: Primary-source check → evidence comparison → material-change classification → append-only record → human review → publication candidate.

This template does not send alerts, publish posts or change a case state.
"""

PILOT = """# IREN eight-week pilot measurement protocol v0.1

Status: PROPOSED / NOT STARTED. Week 1 begins only after a separately authorized `PUBLIC_PILOT_START` event.

## Pre-registered proposed measures

- qualified, non-incentivized professional interactions (target proposed: at least 3);
- externally submitted substantive evidence challenges or attributable additions (target proposed: at least 2; zero remains zero);
- median accessible-material-filing to internal-update time (proposed: no more than 3 calendar days);
- actual use of tracker and source links, with denominator and collection method;
- inbound requests for a scoped private Decision Boundary;
- accepted changes with append-only provenance; and
- unreviewed production releases (required: zero).

Synthetic rehearsals and real observations must use separate ledgers. No subscriber, conversion, savings, avoided-loss or ROI value may be invented. Inaccessible events and censored measurements remain in the denominator.

## Proposed stop rule

If the first two thresholds are missed after an authorized eight-week run, stop public promotion and record weak observed demand. This does not establish product failure. Owner, editorial, privacy and legal approval remain required before activation; personalized investor outputs require separate securities-law review.
"""

POLICY = """# IREN tracker neutrality and conflicts policy draft v0.1

Status: DRAFT / LEGAL AND OPERATIONAL REVIEW REQUIRED.

Selection criteria were stated before activation: a listed firm, bounded public project, material disclosed commitment, at least two primary-document types and time-bounded milestones. This is a one-case exploratory pilot, not a random sample.

- No buy, sell or hold recommendation; no price target, company grade, ranking, score or visual proxy.
- No issuer fee may buy a favorable evidence state, priority or delayed correction.
- Company-supplied material is attributed and classified; it is never automatically accepted as independent evidence.
- Paid and free readers, if ever authorized, receive an accepted public state change at the same time.
- Covered-securities trading restrictions require legal and operational design before adoption.
- Team position/conflict declarations are `DECLARATION_NOT_COLLECTED`; this draft does not attest that anyone is position-free.
- A real human reviewer is not claimed until recorded by identity and review event.
- Personalized investor services, marketing or onboarding require separate securities/commercial legal review for applicable jurisdictions.
- No automatic website, social, email or subscriber publication is authorized.

Evidence states are revisable, attributable records within declared methods—not authoritative truth about IREN.
"""


def write_json(path: Path, value: object) -> None:
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(value.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    validate_tracker(TRACKER, SOURCES)
    validate_events(EVENTS)
    write_json(OUT / "source-inventory-v0.1.json", {"project": TRACKER["project"], "capture_date": CAPTURE, "prior_case_inventory": PRIOR_CASE, "sources": SOURCES})
    write_text(OUT / "source-inventory-v0.1.md", source_report())
    write_json(OUT / "tracker-v0.1.json", TRACKER)
    write_text(OUT / "tracker-v0.1.md", tracker_markdown())
    write_json(OUT / "corporate-bet-register-v0.1.json", BET_REGISTER)
    write_text(OUT / "change-events-v0.1.jsonl", "\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in EVENTS))
    write_text(OUT / "weekly-digest-template-v0.1.md", WEEKLY)
    write_text(OUT / "eight-week-pilot-protocol-v0.1.md", PILOT)
    write_text(OUT / "neutrality-conflicts-policy-v0.1.md", POLICY)

    paths = sorted(path for path in (ROOT / OUT).iterdir() if path.is_file())
    implementation_paths = [
        ROOT / "protocol/listed-project-tracker/README.md",
        ROOT / "protocol/listed-project-tracker/schema-v0.1.json",
        ROOT / "scripts/build_listed_project_tracker_iren_v01.py",
        ROOT / "scripts/listed_project_tracker_iren_v01.py",
        ROOT / "scripts/test_listed_project_tracker_iren_v01.py",
    ]
    report = {
        "project": TRACKER["project"], "baseline_main_sha": BASELINE,
        "generated_at": CAPTURE, "evidence_cutoff": CUTOFF,
        "source_count": len(SOURCES),
        "source_content_reviewed_count": sum(item["review_status"].startswith("CODEX_REVIEW_COMPLETE") for item in SOURCES),
        "source_raw_capture_failed_count": sum(item["byte_capture_status"] == "RETRIEVAL_FAILED" for item in SOURCES),
        "claims_supported_as_attributed": sum(item["state"] == "SUPPORTED_AS_ATTRIBUTED" for item in CLAIMS),
        "claims_not_established": sum(item["state"] == "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE" for item in CLAIMS),
        "tracker_snapshot_sha256": TRACKER["snapshot_sha256"],
        "bet_register_snapshot_sha256": BET_REGISTER["snapshot_sha256"],
        "event_head_sha256": EVENTS[-1]["event_sha256"],
        "prior_case_sha256": PRIOR_CASE["sha256"],
        "original_records_changed": 0, "case_state_changed": False,
        "production_deploy": False, "public_pilot_started": False,
        "files": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "implementation_files": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in implementation_paths},
    }
    report["report_sha256"] = digest(report)
    write_json(Path("docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-HASHES.json"), report)
    print(f"IREN_TRACKER_BUILD = PASS ({len(paths)} artifacts)")
    print(f"TRACKER_SHA256 = {TRACKER['snapshot_sha256']}")
    print(f"BET_REGISTER_SHA256 = {BET_REGISTER['snapshot_sha256']}")


if __name__ == "__main__":
    main()

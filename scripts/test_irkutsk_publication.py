#!/usr/bin/env python3
"""Behavioral checks for the Irkutsk public whitelist and homepage fold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "irkutsk-lab-worker-death"
CASE_ID = "SE-IRK-LAB-001"
EXPECTED_CLAIMS = {
    f"{CASE_ID}.WORKER_AT_INSTITUTE": "SUPPORTED",
    f"{CASE_ID}.WORKER_DEATH_REPORTED": "SUPPORTED",
    f"{CASE_ID}.PNEUMONIA_UNKNOWN_ETIOLOGY_REPORTED": "SUPPORTED",
    f"{CASE_ID}.PNEUMONIC_PLAGUE_DIAGNOSIS": "NOT_ESTABLISHED",
    f"{CASE_ID}.OCCUPATIONAL_PATHOGEN_LINK": "NOT_ESTABLISHED",
    f"{CASE_ID}.LAB_ACCIDENT": "NOT_ESTABLISHED",
    f"{CASE_ID}.CONTACTS_MONITORED": "SUPPORTED",
    f"{CASE_ID}.DANGEROUS_PATHOGEN_IN_CONTACTS": "NOT_ESTABLISHED",
    f"{CASE_ID}.SECOND_PLAGUE_CASE": "NOT_ESTABLISHED",
    f"{CASE_ID}.SECOND_DEATH": "NOT_ESTABLISHED",
    f"{CASE_ID}.WHO_INITIAL_RISK_ASSESSMENT": "SUPPORTED",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    index = load(CASE / "index.json")
    state = load(CASE / "state-v0.1.json")
    review = load(CASE / "search-review-v0.1.json")
    control = load(CASE / "publication-control-v0.1.json")
    registry = load(ROOT / "data" / "case-watch" / "case-registry.json")

    assert index["case_id"] == CASE_ID
    # The current record may advance; the original fixed snapshot must not.
    assert isinstance(index["current_state"], str) and index["current_state"]
    if "current_snapshot" in index:
        assert load(CASE / index["current_snapshot"])["current_state"] == index["current_state"]
    assert state["current_state"] == "DEATH_REPORTED_CAUSE_NOT_ESTABLISHED_REVIEW_INCOMPLETE"
    claims = {row["claim_id"]: row["status"] for row in state["claims"]}
    assert claims == EXPECTED_CLAIMS

    second_case = next(row for row in state["claims"] if row["claim_id"].endswith("SECOND_PLAGUE_CASE"))
    second_death = next(row for row in state["claims"] if row["claim_id"].endswith("SECOND_DEATH"))
    assert (second_case["input_alias"], second_case["origin_claim_id"]) == ("CL-064-A", "CL-064")
    assert (second_death["input_alias"], second_death["origin_claim_id"]) == ("CL-064-B", "CL-064")

    assert review["result"] == "REVIEW_INCOMPLETE"
    assert review["search_query_count"] == 4
    assert review["page_open_attempt_count"] == 8
    assert review["package_inputs"]["status"] == "MISSING"
    assert control["publication_approved"] is True
    assert control["public_projection_status"] in {"PENDING_PRODUCTION_ACCEPTANCE", "PUBLIC_PROJECTION_ACTIVE"}
    assert control["public_projection_active"] == (control["public_projection_status"] == "PUBLIC_PROJECTION_ACTIVE")

    featured = {row["case_id"] for row in registry["cases"] if row["featured"]}
    assert featured == {"CML-PDRE-001", "SE-BESS-SODIUM-001", CASE_ID}
    nsclc = next(row for row in registry["cases"] if row["case_id"] == "SE-ONC-NSQNSCLC-CN-001")
    assert nsclc["featured"] is False and nsclc["management_status"] == "FOLDED"

    for homepage in (ROOT / "en" / "index.html", ROOT / "zh-cn" / "index.html", ROOT / "es" / "index.html"):
        text = homepage.read_text(encoding="utf-8")
        assert text.count("data-featured-case=") == 3
        assert 'data-featured-case="CML-PDRE-001"' in text
        assert 'data-featured-case="SE-BESS-SODIUM-001"' in text
        assert f'data-featured-case="{CASE_ID}"' in text
        featured_section = text.split('data-featured-case-count="3"', 1)[1].split("</section>", 1)[0]
        assert "nsq-nsclc-china" not in featured_section

    prohibited = (
        "family identity", "home address", "travel itinerary", "supplier candidate",
        "financial gain", "fabricated pathogen", "released pathogen", "internal v0.7",
    )
    public_blob = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in CASE.iterdir() if path.suffix in {".html", ".json", ".yaml"}
    )
    assert not any(term in public_blob for term in prohibited)

    baseline = load(ROOT / "data" / "case-watch" / "protected-baseline-sha256.json")
    for rel, expected in baseline["files"].items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert actual == expected, f"protected baseline changed: {rel}"

    for rel in (
        "index.html", "index.json", "state-v0.1.json", "stop-v0.1.html",
        "publication-control-v0.1.json", "search-review-v0.1.json",
    ):
        assert (CASE / rel).read_bytes() == (ROOT / "docs" / "cases" / "irkutsk-lab-worker-death" / rel).read_bytes()

    print("PASS: Irkutsk public whitelist, homepage fold, history, and protected baselines")


if __name__ == "__main__":
    main()

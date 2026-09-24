import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evidence" / "decision-memory" / "schema" / "decision-memory-record.schema.json"
CASE = ROOT / "cases" / "sodium-ion-bess" / "decision-memory-v0.1.json"
DOC_CASE = ROOT / "docs" / "cases" / "sodium-ion-bess" / "decision-memory-v0.1.json"
FROZEN = ROOT / "cases" / "sodium-ion-bess" / "state-v0.1.json"

def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def test_files_parse():
    load(SCHEMA)
    load(CASE)
    load(DOC_CASE)
    load(FROZEN)

def test_public_and_docs_mirror_match():
    assert CASE.read_text(encoding="utf-8") == DOC_CASE.read_text(encoding="utf-8")

def test_frozen_snapshot_is_referenced_not_replaced():
    dm = load(CASE)["decision_memory"]
    assert dm["source_snapshot_refs"] == ["cases/sodium-ion-bess/state-v0.1.json"]
    assert dm["revision_history"][0]["preserves_original"] is True

def test_evidence_and_decision_state_are_separate():
    dm = load(CASE)["decision_memory"]
    assert dm["evidence_states"]
    assert dm["decision_state"]["status"] == "CONTEXT_REQUIRED"

def test_five_clock_semantics_present():
    dm = load(CASE)["decision_memory"]
    for record in dm["evidence_observations"]:
        clocks = record["temporal_semantics"]
        assert set(clocks) == {"event_at", "published_at", "first_observed_at", "known_at", "frozen_at"}

def test_publication_lag_is_preserved():
    dm = load(CASE)["decision_memory"]
    ev = next(x for x in dm["evidence_observations"] if x["evidence_id"] == "SE-BESS-SODIUM-001-EV-003")
    assert ev["temporal_semantics"]["event_at"] == "2026-04-27"
    assert ev["temporal_semantics"]["published_at"] == "2026-04-29"
    pubs = {x["publisher"]: x["published_at"] for x in ev["source_artifacts"]}
    assert pubs["HyperStrong"] == "2026-04-29"
    assert pubs["CATL"] == "2026-05-06"

def test_unknowns_are_research_allocatable():
    dm = load(CASE)["decision_memory"]
    assert dm["unknowns"]
    for unknown in dm["unknowns"]:
        assert unknown["decision_sensitivity"] in {"MATERIAL", "CONDITIONAL", "LOW", "UNKNOWN"}
        assert unknown["minimum_resolving_evidence"]
        assert unknown["resolution_path"]
        assert unknown["stop_condition"]

def test_no_outcome_is_invented():
    dm = load(CASE)["decision_memory"]
    assert dm["outcome_refs"] == []

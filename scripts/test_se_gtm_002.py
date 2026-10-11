#!/usr/bin/env python3
"""Integrity and authorization gates for SE-GTM-002."""

import copy
import csv
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops" / "growth" / "SE_GTM_002"
SCHEMA = json.loads((BASE / "CDSP_SCHEMA_v0.1.json").read_text())
RECORD_PATHS = sorted((BASE / "records").glob("*.json"))
RECORDS = [json.loads(path.read_text()) for path in RECORD_PATHS]
REQUIRED_GATES = (
    "traceable_source",
    "named_affected_company",
    "active_decision",
    "material_gap",
    "decision_owner_role",
    "verified_route",
    "route_purpose_fit",
)


def csv_rows(name):
    with (BASE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def validate_candidate_rows(rows):
    ids = [row["candidate_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate candidate_id")
    paths = [row["record_path"] for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate record_path")


def validate_record_policy(record):
    components = record["score_components"]
    if record["candidate_score"] != sum(components.values()):
        raise ValueError("candidate score does not equal component sum")

    gates = record["qualification_gates"]
    gate_result = all(gates[name] for name in REQUIRED_GATES)
    if gates["qualified"] != gate_result:
        raise ValueError("qualification does not match mandatory gates")

    approved = record["outreach_authorization"] == "APPROVED_FOR_SINGLE_SEND"
    if gates["send_ready"] != (gate_result and approved):
        raise ValueError("send_ready bypasses qualification or authorization")

    route = record["verified_contact_route"]
    if route["route_type"] == "NONE":
        if route["value"] is not None or route["verification_url"] is not None:
            raise ValueError("NONE route contains route data")
        if gates["verified_route"]:
            raise ValueError("NONE route marked verified")

    if record["contact_outcome"] == "NOT_CONTACTED":
        if record["assertion_register"]["confirmed_customer_statements"]:
            raise ValueError("customer statement exists without contact")
        if record["commercial_outcome"] != "NO_OBSERVATION":
            raise ValueError("commercial outcome inferred without contact")


class SEGTM002Tests(unittest.TestCase):
    def test_required_deliverables_exist(self):
        expected = {
            "CDSP_SCHEMA_v0.1.json",
            "ACQUISITION_CANDIDATES.csv",
            "PARTNER_CANDIDATES.csv",
            "DECISION_BLOCKER_BRIEF_TEMPLATE.md",
            "OUTREACH_REVIEW_QUEUE.md",
            "PILOT_COST_LEDGER.csv",
            "ACQUISITION_METRICS.md",
            "SE_GTM_002_WEEKLY_REPORT.md",
            "EXPERIMENT_ASSUMPTIONS_AND_FAILURE_RULES.md",
        }
        self.assertEqual({p.name for p in BASE.iterdir()} & expected, expected)

    def test_records_validate_against_schema(self):
        validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
        self.assertEqual(len(RECORDS), 4)
        for path, record in zip(RECORD_PATHS, RECORDS):
            errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
            self.assertEqual(errors, [], f"{path}: {[e.message for e in errors]}")

    def test_scores_and_mandatory_gates(self):
        for record in RECORDS:
            validate_record_policy(record)
        highest = max(RECORDS, key=lambda record: record["candidate_score"])
        self.assertGreaterEqual(highest["candidate_score"], 70)
        self.assertFalse(highest["qualification_gates"]["qualified"])
        self.assertFalse(highest["qualification_gates"]["send_ready"])

    def test_authorization_cannot_override_failed_gates(self):
        unsafe = copy.deepcopy(RECORDS[0])
        unsafe["outreach_authorization"] = "APPROVED_FOR_SINGLE_SEND"
        unsafe["qualification_gates"]["send_ready"] = True
        with self.assertRaisesRegex(ValueError, "send_ready"):
            validate_record_policy(unsafe)

    def test_append_only_identity_and_history(self):
        record_ids = [record["record_id"] for record in RECORDS]
        versions = [(record["candidate_id"], record["record_version"]) for record in RECORDS]
        self.assertEqual(len(record_ids), len(set(record_ids)))
        self.assertEqual(len(versions), len(set(versions)))
        for record in RECORDS:
            self.assertTrue(record["append_only"])
            self.assertEqual(record["record_version"], "v0.1")
            self.assertIsNone(record["predecessor_record_id"])
            self.assertEqual(record["history_events"][0]["event_type"], "INITIAL_SNAPSHOT")
            self.assertTrue(all(event["preserves_prior_state"] for event in record["history_events"]))

    def test_candidate_csv_is_unique_and_traceable(self):
        rows = csv_rows("ACQUISITION_CANDIDATES.csv")
        validate_candidate_rows(rows)
        self.assertEqual(len(rows), len(RECORDS))
        by_id = {record["candidate_id"]: record for record in RECORDS}
        for row in rows:
            record = by_id[row["candidate_id"]]
            self.assertTrue((BASE / row["record_path"]).is_file())
            self.assertIn(row["source_url"], record["source_url"])
            self.assertEqual(int(row["candidate_score"]), record["candidate_score"])
            self.assertEqual(row["outreach_authorization"], record["outreach_authorization"])
            self.assertEqual(row["contact_outcome"], "NOT_CONTACTED")
            self.assertEqual(row["commercial_outcome"], "NO_OBSERVATION")

    def test_duplicate_detection(self):
        rows = csv_rows("ACQUISITION_CANDIDATES.csv")
        with self.assertRaisesRegex(ValueError, "duplicate candidate_id"):
            validate_candidate_rows(rows + [dict(rows[0])])

    def test_partner_routes_are_official_and_not_authorized(self):
        rows = csv_rows("PARTNER_CANDIDATES.csv")
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({row["partner_id"] for row in rows}), 5)
        for row in rows:
            self.assertTrue(row["source_url"].startswith("https://"))
            self.assertTrue(row["contact_route_evidence"].startswith("https://"))
            self.assertEqual(row["route_purpose_fit"], "ROUTABLE")
            self.assertEqual(row["outreach_authorization"], "NOT_AUTHORIZED")
            self.assertEqual(row["contact_outcome"], "NOT_CONTACTED")

    def test_cost_and_outcome_baseline_is_zero(self):
        costs = csv_rows("PILOT_COST_LEDGER.csv")
        self.assertTrue(costs)
        self.assertEqual(sum(float(row["amount"]) for row in costs), 0)
        self.assertTrue(all(row["external_spend"] == "NO" for row in costs))
        self.assertTrue(all(record["payment_signal"] == "NONE_OBSERVED" for record in RECORDS))

    def test_existing_growth_campaign_remains_separate(self):
        old = ROOT / "ops" / "growth" / "TRUST_BOUNDARY_30D_001"
        self.assertTrue(old.is_dir())
        self.assertNotEqual(old.resolve(), BASE.resolve())
        self.assertFalse(any(path.is_symlink() for path in BASE.rglob("*")))


if __name__ == "__main__":
    unittest.main()

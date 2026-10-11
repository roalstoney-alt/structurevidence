#!/usr/bin/env python3
"""Integrity and boundary checks for the consolidated DPAL v0.3 pilot."""

import csv
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops" / "growth" / "SE_GTM_002"
DPAL = BASE / "dpal-v0.3"
BASE_COMMIT = "b61588b50256022ab501a9b567a930c7e3b0c0b6"
PRESSURE_CLASSES = {
    "EXTERNAL_RISK",
    "INTERNAL_AUDIT",
    "REGULATORY_COMPLIANCE",
    "GEOPOLITICAL_POLICY",
    "GOVERNANCE_ACCOUNTABILITY",
    "COMMERCIAL_SUPPLY_CHAIN",
}
REQUIRED_GATES = {
    "traceable_source",
    "named_affected_company",
    "active_decision",
    "material_gap",
    "decision_owner_role",
    "verified_route",
    "route_purpose_fit",
}


def csv_rows(name):
    with (DPAL / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def relations():
    records = []
    for number, line in enumerate(
        (DPAL / "PRESSURE_ACCOUNTABILITY_RELATIONS.jsonl").read_text().splitlines(), 1
    ):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"invalid JSONL line {number}: {error}") from error
    return records


class DPALV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = csv_rows("DPAL_CANDIDATES.csv")
        cls.records = relations()

    def test_required_deliverables_and_no_parallel_schema(self):
        expected = {
            "DPAL_ARCHITECTURE_DECISION.md",
            "DPAL_CANDIDATES.csv",
            "PRESSURE_ACCOUNTABILITY_RELATIONS.jsonl",
            "CHANNEL_COMPARISON_REPORT.md",
            "COUNTEREVIDENCE_AND_FAILURES.md",
            "HUMAN_REVIEW_QUEUE.md",
            "DPAL_V0_3_FINAL_REPORT.md",
        }
        self.assertTrue(expected.issubset({path.name for path in DPAL.iterdir()}))
        self.assertFalse((DPAL / "DPAL_SCHEMA_v0.1.json").exists())

    def test_candidate_counts_and_unique_identity(self):
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(len(self.records), 16)
        self.assertEqual(len({row["candidate_id"] for row in self.rows}), 16)
        self.assertEqual(len({record["relation_id"] for record in self.records}), 16)
        self.assertEqual(
            {row["candidate_id"] for row in self.rows},
            {record["candidate_id"] for record in self.records},
        )
        cohorts = {}
        for row in self.rows:
            cohorts[row["pressure_cohort"]] = cohorts.get(row["pressure_cohort"], 0) + 1
        self.assertEqual(
            cohorts,
            {
                "TECHNOLOGY_TRIGGERED": 6,
                "AUDIT_RISK_TRIGGERED": 5,
                "REGULATORY_POLICY_TRIGGERED": 5,
            },
        )

    def test_controlled_pressure_vocabulary_and_multi_class(self):
        observed = set()
        has_multiple = False
        for record in self.records:
            values = record["pressure_classes"]
            self.assertTrue(values)
            self.assertTrue(set(values).issubset(PRESSURE_CLASSES))
            observed.update(values)
            has_multiple = has_multiple or len(values) > 1
        self.assertEqual(observed, PRESSURE_CLASSES)
        self.assertTrue(has_multiple)

    def test_fact_inference_hypothesis_separation(self):
        for record in self.records:
            assertions = record["assertions"]
            self.assertTrue(assertions["observed_facts"])
            self.assertEqual(assertions["confirmed_customer_statements"], [])
            self.assertTrue(record["source"]["url"].startswith("https://"))
            self.assertIn(record["pressure_event"]["evidence_state"], {"SUPPORTED", "OBSERVED"})

    def test_cdsp_gates_are_not_overridden(self):
        for record in self.records:
            gates = record["qualification"]
            expected = all(gates[name] for name in REQUIRED_GATES)
            self.assertEqual(gates["qualified"], expected)
            self.assertFalse(gates["send_ready"])
            self.assertEqual(record["outreach_authorization"], "NOT_AUTHORIZED")
        self.assertEqual(sum(record["qualification"]["qualified"] for record in self.records), 0)

    def test_reported_metrics_match_records(self):
        self.assertEqual(sum(r["accountability_relation"]["organization_obligation_verified"] for r in self.records), 13)
        self.assertEqual(sum(r["accountability_relation"]["internal_owner_verified"] for r in self.records), 6)
        self.assertEqual(sum(r["external_verification_need"] == "REQUIRED" for r in self.records), 3)
        self.assertEqual(sum(r["buyer"]["state"] == "CONFIRMED" for r in self.records), 0)
        self.assertEqual(sum(r["research_cost_usd"] for r in self.records), 0)

    def test_append_only_and_freshness(self):
        for record in self.records:
            self.assertTrue(record["append_only"])
            self.assertEqual(record["record_version"], "v0.1")
            self.assertIsNone(record["predecessor_relation_id"])
            self.assertTrue(record["freshness"]["checked_at"])
            self.assertTrue(all(event["preserves_prior_state"] for event in record["history"]))

    def test_partner_fit_and_channel_comparison_are_consolidated(self):
        report = (DPAL / "CHANNEL_COMPARISON_REPORT.md").read_text()
        for name in ("Rochester Electronics", "TTI", "SiliconExpert", "SGS", "Intertek"):
            self.assertIn(name, report)
        self.assertIn("Partner-referred opportunities", report)
        self.assertIn("0 referrals", report)
        self.assertIn("COMPETITIVE_HOLD", report)
        queue = (DPAL / "HUMAN_REVIEW_QUEUE.md").read_text()
        self.assertIn("OUTREACH_SENT = `0`", queue)
        self.assertIn("separate approval", queue)

    def test_existing_history_and_trust_campaign_unchanged(self):
        protected = [
            "ops/growth/TRUST_BOUNDARY_30D_001",
            "ops/growth/SE_GTM_002/ACQUISITION_CANDIDATES.csv",
            "ops/growth/SE_GTM_002/PARTNER_CANDIDATES.csv",
            "ops/growth/SE_GTM_002/records",
        ]
        command = ["git", "diff", "--name-only", BASE_COMMIT, "--", *protected]
        changed = subprocess.run(
            command, cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        self.assertEqual(changed, "")

    def test_one_consolidated_final_report_and_human_gate(self):
        reports = list(DPAL.glob("*FINAL_REPORT.md"))
        self.assertEqual([path.name for path in reports], ["DPAL_V0_3_FINAL_REPORT.md"])
        final = reports[0].read_text()
        self.assertIn("STATUS = `HUMAN_REVIEW_REQUIRED`", final)
        self.assertIn("QUALIFIED_CDSP = `0`", final)
        self.assertIn("BUYERS_CONFIRMED = `0`", final)
        self.assertIn("SUPERSEDED_INSTRUCTION_EXECUTED_SEPARATELY = `NO`", final)


if __name__ == "__main__":
    unittest.main()

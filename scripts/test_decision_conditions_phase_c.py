#!/usr/bin/env python3
"""Regression and negative tests for Phase C Decision Conditions."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_decision_conditions_phase_c import INPUTS, JSON_PATH, MD_PATH, HTML_PATH, render_html, render_markdown  # noqa: E402
from decision_conditions_v01 import DecisionConditionError, build_package, validate_package  # noqa: E402
from source_dependency_v01 import evaluate_qualification, is_additional_entity_or_site, load_rules, seal_record  # noqa: E402


EXPECTED_INPUT_HASHES = {
    "cases/800vdc/source-dependency-v0.1.json": "9038817ab15e1202ea5ae8ca374f515f5381b6480fce22f2ff137d3267cd7705",
    "cases/800vdc/source-dependency-review-matrix-v0.1.json": "1cdd2fd6816ca6b8e9518958cd757098f41a44e04f88854cb9604e25c3ab86f0",
    "protocol/source-dependency/registry-v0.1.json": "172172ccc1c9fe8587224c1dcf51ae8354be74d951603da6b5f96b1e7fa68203",
    "protocol/source-dependency/qualification-rules-v0.2.json": "2f35a425eabf05d7e9893617f60a1faa97ffda62ac7a0e093adc6b9fdcbb6dce",
}


def load(path: str | Path) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class DecisionConditionsPhaseC(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.view = load(INPUTS["source_dependency_view"])
        cls.matrix = load(INPUTS["source_review_matrix"])
        cls.registry = load(INPUTS["source_registry"])
        cls.rules = load(INPUTS["qualification_rules"])
        cls.provenance = {name: str(path) for name, path in INPUTS.items()}

    def build(self, *, view=None, matrix=None, registry=None, rules=None):
        return build_package(
            copy.deepcopy(view if view is not None else self.view),
            copy.deepcopy(matrix if matrix is not None else self.matrix),
            copy.deepcopy(registry if registry is not None else self.registry),
            copy.deepcopy(rules if rules is not None else self.rules),
            self.provenance,
        )

    def test_01_declared_conditions_and_stable_ids(self):
        package = self.build()
        self.assertEqual([c["gap_id"] for c in package["conditions"]], ["OEG-CML-001", "OEG-CML-002"])
        self.assertEqual(len({c["decision_condition_id"] for c in package["conditions"]}), 2)

    def test_02_build_is_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_03_sealed_hashes_validate(self):
        validate_package(self.build())

    def test_04_evidence_rule_is_separate_from_client_action(self):
        for condition in self.build()["conditions"]:
            self.assertFalse(condition["current_evidence_state"]["state_changed_by_export"])
            self.assertEqual(condition["client_action_condition"]["selected_action"], "UNSPECIFIED")
            self.assertEqual(condition["client_action_condition"]["status"], "NO_CLIENT_DECISION_RECORDED")
            self.assertNotIn(condition["client_action_condition"]["selected_action"], {"PROCEED", "HOLD", "EXIT"})

    def test_05_unknown_unresolved_unsupported_preserved(self):
        for condition in self.build()["conditions"]:
            uncertainty = condition["preserved_uncertainty"]
            self.assertTrue(uncertainty["unknown"])
            self.assertEqual(uncertainty["unresolved"][0]["status"], "UNRESOLVED")
            self.assertEqual(uncertainty["unsupported"][0]["status"], "UNSUPPORTED")

    def test_06_source_rows_and_supersession_are_traceable(self):
        package = self.build()
        for condition in package["conditions"]:
            rows = condition["source_evidence_result"]["nonqualifying_evidence"]
            self.assertEqual(len(rows), 9)
            self.assertFalse(any(row["source_row_id"].endswith("CHINDATA-533-V1") for row in rows))
            self.assertEqual(len(condition["source_supersession_links"]), 1)

    def test_07_original_phase_b_inputs_have_not_drifted(self):
        for path, expected in EXPECTED_INPUT_HASHES.items():
            actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, path)

    def test_08_json_markdown_html_semantics_agree(self):
        package = load(JSON_PATH)
        markdown = (ROOT / MD_PATH).read_text(encoding="utf-8")
        page = (ROOT / HTML_PATH).read_text(encoding="utf-8")
        for condition in package["conditions"]:
            for text in (markdown, page):
                self.assertIn(condition["decision_condition_id"], text)
                self.assertIn(condition["gap_id"], text)
                self.assertIn(condition["source_evidence_result"]["qualification_outcome"], text)
            self.assertIn(condition["record_sha256"], markdown)
            self.assertIn(condition["record_sha256"], page)

    def test_09_copy_affordance_and_accessible_fallback_exist(self):
        page = render_html(self.build())
        script = (ROOT / "assets/decision-conditions.js").read_text(encoding="utf-8")
        self.assertEqual(page.count("data-copy-decision-conditions"), 2)
        self.assertEqual(page.count("readonly"), 2)
        self.assertIn('role="status"', page)
        self.assertIn("navigator.clipboard.writeText", script)
        self.assertIn("source.select()", script)

    def test_10_root_docs_mirrors_are_byte_identical(self):
        pairs = [
            (JSON_PATH, Path("docs") / JSON_PATH), (MD_PATH, Path("docs") / MD_PATH),
            (HTML_PATH, Path("docs") / HTML_PATH),
            (Path("assets/decision-conditions.css"), Path("docs/assets/decision-conditions.css")),
            (Path("assets/decision-conditions.js"), Path("docs/assets/decision-conditions.js")),
        ]
        for left, right in pairs:
            self.assertEqual((ROOT / left).read_bytes(), (ROOT / right).read_bytes(), str(left))

    def test_10b_supplemental_sitemap_has_all_phase_c_public_routes(self):
        root_map = (ROOT / "decision-conditions-sitemap.xml").read_text(encoding="utf-8")
        docs_map = (ROOT / "docs/decision-conditions-sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(root_map, docs_map)
        for suffix in ("decision-conditions/", "decision-conditions-v0.1.json", "decision-conditions-v0.1.md", "schema-v0.1.json"):
            self.assertIn(suffix, root_map)

    def test_11_missing_gap_is_rejected(self):
        view = copy.deepcopy(self.view)
        view["metrics"].pop("OEG-CML-002")
        with self.assertRaises(DecisionConditionError):
            self.build(view=view)

    def test_11b_invalid_gap_is_rejected(self):
        view = copy.deepcopy(self.view)
        view["metrics"]["OEG-CML-999"] = view["metrics"].pop("OEG-CML-002")
        with self.assertRaises(DecisionConditionError):
            self.build(view=view)

    def test_12_conflicting_dates_are_rejected(self):
        view = copy.deepcopy(self.view)
        view["reviewed_at"] = "2026-01-01T00:00:00Z"
        with self.assertRaises(DecisionConditionError):
            self.build(view=view)

    def test_13_unacknowledged_reviewer_conflict_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        active = next(row for row in registry["rows"] if row["source_row_id"].endswith("CHINDATA-533-V2"))
        active["reviewer_disagreement"] = {"detected": True, "fields": ["evidence_level"], "resolution_status": "NOT_APPLICABLE", "resolution_note": "conflict"}
        active.update(seal_record(active))
        with self.assertRaises(ValueError):
            self.build(registry=registry)

    def test_14_nonqualifying_e2_cannot_be_promoted(self):
        registry = copy.deepcopy(self.registry)
        row = next(row for row in registry["rows"] if row["gap_id"] == "OEG-CML-001" and "CHINDATA" not in row["source_row_id"])
        row["evidence_level"] = "E2"
        row["qualification_status"] = "NOT_QUALIFIED"
        row["qualification_reason"] = "E2 is below the rule minimum E4."
        row.update(seal_record(row))
        package = self.build(registry=registry)
        condition = package["conditions"][0]
        exported = next(item for item in condition["source_evidence_result"]["nonqualifying_evidence"] if item["source_row_id"] == row["source_row_id"])
        self.assertEqual(exported["evidence_level"], "E2")

    def test_15_issuer_e4_is_conditionally_eligible_not_automatically_qualified(self):
        indexed = load_rules(self.rules)
        rule = next(rule for rule in indexed.values() if rule["gap_id"] == "OEG-CML-001")
        v1 = next(row for row in self.registry["rows"] if row["source_row_id"].endswith("INDEPENDENT-VALIDATION-CHINDATA-533-V1"))
        status, reason = evaluate_qualification(v1, rule)
        self.assertEqual(status, "NOT_QUALIFIED")
        eligible = copy.deepcopy(v1)
        eligible["evidence_facets"] = list(rule["required_evidence_facets"])
        status, _ = evaluate_qualification(eligible, rule)
        self.assertEqual(status, "QUALIFIED")

    def test_16_second_site_false_positive_is_rejected(self):
        baseline = {"operator_id": "A", "site_id": "S1", "control_id": "C1"}
        same = {"operator_id": "A", "site_id": "S1", "control_id": "C1"}
        self.assertFalse(is_additional_entity_or_site(baseline, same))
        self.assertTrue(is_additional_entity_or_site(baseline, {"operator_id": "B", "site_id": "S1", "control_id": "C1"}))

    def test_17_unavailable_source_remains_insufficient_and_visible(self):
        registry = copy.deepcopy(self.registry)
        row = next(row for row in registry["rows"] if row["gap_id"] == "OEG-CML-002" and "CHINDATA" not in row["source_row_id"])
        row["source_access_status"] = "UNAVAILABLE"
        row["immutable_source"]["capture"]["failure_reason"] = "The source was unavailable during the bounded check."
        row["qualification_status"] = "INSUFFICIENT_DATA"
        row["qualification_reason"] = "The source was not available as a reviewable record."
        row.update(seal_record(row))
        package = self.build(registry=registry)
        condition = package["conditions"][1]
        self.assertEqual(condition["source_evidence_result"]["inaccessible_sources"][0]["qualification_status"], "INSUFFICIENT_DATA")

    def test_18_unsafe_markup_is_rejected(self):
        view = copy.deepcopy(self.view)
        view["decision_boundary"]["scoped_questions"]["OEG-CML-001"] = "<script>alert(1)</script>"
        with self.assertRaises(DecisionConditionError):
            self.build(view=view)

    def test_18b_unsafe_source_url_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        row = next(row for row in registry["rows"] if row["source_row_id"].endswith("CHINDATA-533-V2"))
        row["immutable_source"]["url"] = "javascript:alert(1)"
        row.update(seal_record(row))
        with self.assertRaises(ValueError):
            self.build(registry=registry)

    def test_19_markdown_contains_complete_citations_and_urls(self):
        package = self.build()
        markdown = render_markdown(package)
        self.assertEqual(markdown.count("### Copyable complete citation"), 2)
        self.assertIn("Client action=UNSPECIFIED", markdown)
        self.assertIn("decision-conditions-v0.1.json", markdown)

    def test_20_schema_accepts_generated_package_when_jsonschema_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        jsonschema.Draft202012Validator(load("protocol/decision-conditions/schema-v0.1.json"), format_checker=jsonschema.FormatChecker()).validate(self.build())


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DecisionConditionsPhaseC)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"PHASE_C_DECISION_CONDITIONS = {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"TESTS_RUN = {result.testsRun}")
    raise SystemExit(0 if result.wasSuccessful() else 1)

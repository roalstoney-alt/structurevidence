from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from se_frr_adapters import CML_SOURCE, RDL_SOURCE, adapt_cml_subject, adapt_rdl_evidence  # noqa: E402
from se_frr_protocol import (  # noqa: E402
    ProtocolError,
    append_state,
    canonical_json,
    evidence_hash,
    load_objects,
    outcome_to_evidence,
    public_projection,
    state_hash,
    validate_bundle,
    validate_schema,
    verify_state_chain,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_one(kind: str, object_id: str):
    return json.loads((FIXTURES / kind / f"{object_id}.json").read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    def test_all_eight_object_schemas_accept_fixtures(self):
        objects = load_objects(FIXTURES)
        self.assertEqual(set(objects), {"subjects", "evidence", "states", "changes", "branches", "requests", "challenges", "outcomes"})
        for kind, values in objects.items():
            self.assertTrue(values, kind)
            for value in values:
                validate_schema(kind, value)

    def test_evidence_requires_observed_at(self):
        item = load_one("evidence", "SE-EV-20260925-000001")
        del item["observed_at"]
        with self.assertRaises(jsonschema.ValidationError):
            validate_schema("evidence", item)

    def test_invalid_subject_fails(self):
        item = load_one("subjects", "SE-SUBJ-000001")
        item["subject_id"] = "MUTABLE-CONCLUSION-IN-ID"
        with self.assertRaises(jsonschema.ValidationError):
            validate_schema("subjects", item)

    def test_insufficient_evidence_state_may_have_no_references(self):
        item = load_one("states", "SE-ST-20260925-000001")
        item["state_code"] = "INSUFFICIENT_EVIDENCE"
        for field in ["accepted_evidence_ids", "rejected_evidence_ids", "counter_evidence_ids", "unresolved_evidence_ids"]:
            item[field] = []
        validate_schema("states", item)

    def test_state_code_is_controlled(self):
        item = load_one("states", "SE-ST-20260925-000001")
        item["state_code"] = "PROBABLY_GOOD"
        with self.assertRaises(jsonschema.ValidationError):
            validate_schema("states", item)

    def test_public_outcome_requires_authorization(self):
        item = load_one("outcomes", "SE-OUT-20260925-000002")
        item["authorization_for_public_use"] = False
        with self.assertRaises(jsonschema.ValidationError):
            validate_schema("outcomes", item)


class TemporalAndHashTests(unittest.TestCase):
    def test_four_times_have_distinct_semantics(self):
        item = load_one("evidence", "SE-EV-20260925-000001")
        self.assertEqual(len({item["published_at"], item["observed_at"], item["recorded_at"], item["effective_at"]}), 3)
        self.assertLess(item["published_at"], item["recorded_at"])

    def test_effective_at_is_independent(self):
        item = load_one("evidence", "SE-EV-20260925-000001")
        item["effective_at"] = "2027-01-01T00:00:00Z"
        validate_schema("evidence", item)
        self.assertNotEqual(item["effective_at"], item["observed_at"])

    def test_later_publication_cannot_mutate_earlier_state(self):
        earlier = load_one("states", "SE-ST-20260925-000001")
        frozen_hash = earlier["state_hash"]
        _later = load_one("evidence", "SE-EV-20260925-000004")
        self.assertEqual(frozen_hash, earlier["state_hash"])
        self.assertEqual(frozen_hash, state_hash(earlier))

    def test_canonical_json_ignores_mapping_insertion_order(self):
        self.assertEqual(canonical_json({"z": 1, "a": {"y": 2, "x": 3}}), canonical_json({"a": {"x": 3, "y": 2}, "z": 1}))

    def test_evidence_hash_is_deterministic(self):
        item = load_one("evidence", "SE-EV-20260925-000001")
        self.assertEqual(item["content_hash"], evidence_hash(item))
        reordered = dict(reversed(list(item.items())))
        self.assertEqual(item["content_hash"], evidence_hash(reordered))

    def test_mutation_breaks_state_hash(self):
        item = load_one("states", "SE-ST-20260925-000002")
        expected = item["state_hash"]
        item["unknowns"].append("A new unrecorded unknown")
        self.assertNotEqual(expected, state_hash(item))

    def test_state_chain_verifies(self):
        states = load_objects(FIXTURES)["states"]
        self.assertEqual(verify_state_chain(states)["result"], "PASS")

    def test_mutation_breaks_chain(self):
        states = load_objects(FIXTURES)["states"]
        states[0]["current_dependency"] = "tampered"
        result = verify_state_chain(states)
        self.assertEqual(result["result"], "FAIL")
        self.assertGreaterEqual(len(result["hash_mismatches"]), 1)

    def test_append_is_immutable_and_tail_checked(self):
        first = load_one("states", "SE-ST-20260925-000001")
        second = load_one("states", "SE-ST-20260925-000002")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            append_state(directory, first)
            append_state(directory, second)
            with self.assertRaises(ProtocolError):
                append_state(directory, first)
            self.assertEqual(load_one("states", "SE-ST-20260925-000001"), json.loads((directory / f"{first['state_id']}.json").read_text()))

    def test_append_rejects_bad_new_hash(self):
        first = load_one("states", "SE-ST-20260925-000001")
        first["state_hash"] = "f" * 64
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ProtocolError):
            append_state(Path(tmp), first)


class BundleInvariantTests(unittest.TestCase):
    def setUp(self):
        self.objects = load_objects(FIXTURES)

    def test_unified_validator_passes(self):
        result = validate_bundle(self.objects)
        self.assertEqual(result["result"], "PASS", result["errors"])
        self.assertEqual(result["objects_checked"], 15)

    def test_broken_reference_fails(self):
        self.objects["states"][0]["accepted_evidence_ids"] = ["SE-EV-20990101-999999"]
        result = validate_bundle(self.objects)
        self.assertEqual(result["result"], "FAIL")
        self.assertGreater(result["reference_errors"], 0)

    def test_change_links_both_immutable_states(self):
        change = self.objects["changes"][0]
        states = {item["state_id"]: item for item in self.objects["states"]}
        self.assertEqual(change["previous_state_hash"], states[change["previous_state_id"]]["state_hash"])
        self.assertEqual(change["new_state_hash"], states[change["new_state_id"]]["state_hash"])

    def test_rejected_counter_and_superseded_evidence_persist(self):
        statuses = {item["review"]["status"] for item in self.objects["evidence"]}
        self.assertTrue({"REJECTED", "COUNTER", "SUPERSEDED"}.issubset(statuses))

    def test_two_branches_are_simultaneously_represented(self):
        latest = self.objects["states"][-1]
        self.assertEqual(len(latest["branch_ids"]), 2)
        self.assertEqual({item["status"] for item in self.objects["branches"]}, {"POSSIBLE", "STRENGTHENING"})

    def test_no_probability_fields_or_numeric_confidence(self):
        forbidden = {"probability", "probability_score", "confidence_score"}

        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.objects)

    def test_outcome_does_not_mutate_prior_state(self):
        before = copy.deepcopy(self.objects["states"][-1])
        outcome = self.objects["outcomes"][-1]
        new_evidence = outcome_to_evidence(outcome, "SE-EV-20260926-000006", "2026-09-26T10:00:00Z", "fixture-reviewer")
        self.assertEqual(before, self.objects["states"][-1])
        self.assertEqual(new_evidence["provenance"]["source_object"], outcome["outcome_id"])
        self.assertGreater(new_evidence["recorded_at"], outcome["reported_at"])

    def test_public_projection_enforces_boundary(self):
        projection = public_projection(self.objects)
        self.assertNotIn("requests", projection)
        self.assertNotIn("challenges", projection)
        self.assertEqual([item["outcome_id"] for item in projection["outcomes"]], ["SE-OUT-20260925-000002"])
        dumped = json.dumps(projection)
        self.assertNotIn("PRIVATE_FIXTURE_REQUESTER", dumped)
        self.assertNotIn("Private fixture decision context", dumped)


class AdapterTests(unittest.TestCase):
    def test_cml_subject_adapter(self):
        source = json.loads((ROOT / CML_SOURCE).read_text(encoding="utf-8"))
        adapted = adapt_cml_subject(source)
        validate_schema("subjects", adapted)
        self.assertEqual(adapted["provenance"]["source_object"], CML_SOURCE)
        self.assertEqual(adapted["visibility"], "INTERNAL")

    def test_rdl_evidence_adapter(self):
        source = json.loads((ROOT / RDL_SOURCE).read_text(encoding="utf-8"))
        adapted = adapt_rdl_evidence(source)
        validate_schema("evidence", adapted)
        self.assertEqual(adapted["content_hash"], evidence_hash(adapted))
        self.assertIn("no CML state mutation", adapted["review"]["reason"])


if __name__ == "__main__":
    unittest.main()

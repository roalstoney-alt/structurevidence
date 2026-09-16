#!/usr/bin/env python3
"""Targeted positive and adversarial tests for Phase C0."""
import copy
import unittest

import jsonschema

import validate_cml_ov_phase_c0 as c0


def valid_response() -> dict:
    record = copy.deepcopy(c0.load("technical-risk/opportunity-validation/templates/phase-c0-response.json"))
    core = record["core"]
    core.update(
        record_id="SE.CML.OV.OV-03.C0.RESPONSE.001",
        subject_id="OV-03",
        effective_at="2026-09-17T09:00:00+08:00",
        known_at="2026-09-17T10:00:00+08:00",
        created_at="2026-09-17T10:00:00+08:00",
        updated_at="2026-09-17T10:00:00+08:00",
        verification_status="HUMAN_REVIEWED",
        source_refs=["SE.CML.C0.PRIVATE.OV-03.001"],
        input_hash="1" * 64,
        record_hash="2" * 64,
    )
    response = record["discovery_response"]
    response.update(
        record_kind="RESPONSE",
        target="OV-03",
        organization="Example RF Lab",
        role="Microwave test engineer",
        contact_source={
            "contact_type": "OFFICIAL_TECHNICAL_SUPPORT_CHANNEL",
            "public_reference": "https://example.test/support",
            "verified_public": True,
        },
        interaction_date="2026-09-17",
        application_confirmed="YES",
        current_solution=["PROCESS_AUTOMATION"],
        current_bottleneck=["TEST_TIME", "RETEST"],
        improvement_dimension=["LOWER_TEST_BURDEN"],
        measurable="YES",
        acceptance_logic="A/B comparison of setup time, test time, retest and operator intervention.",
        willing_to_review_new_path="YES",
        statements=[
            {"field": "APPLICATION", "statement": "The lab currently validates low-volume 40 GHz cable assemblies.", "evidence_class": "DIRECT_ENGINEER_STATEMENT", "limitations": ["Single organization."]},
            {"field": "BOTTLENECK", "statement": "Repeated manual setup and retest consume material engineering time.", "evidence_class": "DIRECT_ENGINEER_STATEMENT", "limitations": ["No cost figures disclosed."]},
        ],
        limitations=["Single direct response; not market validation."],
        opportunity_state="RESOLVED_BUT_SUBOPTIMAL",
        improvement_hypothesis={
            "real_bottleneck": "Repeated manual setup and retest.",
            "current_path": "Existing semi-automated VNA validation.",
            "proposed_change": "Standardized fixture and traceable automated sequence.",
            "measurable_effect": ["setup time", "test time", "retest rate", "operator intervention"],
            "validation_method": "A/B workflow comparison.",
            "failure_condition": "No material cycle-time or retest improvement.",
        },
        c0_result="PROCEED_TO_SOLUTION_SCOPING",
    )
    return record


class PhaseC0Tests(unittest.TestCase):
    def setUp(self):
        self.record = valid_response()

    def rejects(self):
        with self.assertRaises((ValueError, KeyError, jsonschema.ValidationError)):
            c0.validate_response(self.record)

    def test_framework_and_template(self):
        result = c0.framework_integrity()
        self.assertTrue(result["schema_valid"] and result["template_valid"])

    def test_valid_qualifying_response(self):
        result = c0.validate_response(self.record)
        self.assertEqual(result["c0_result"], "PROCEED_TO_SOLUTION_SCOPING")

    def test_only_authorized_targets(self):
        self.record["discovery_response"]["target"] = "OV-02"
        self.rejects()

    def test_verified_public_contact_required(self):
        self.record["discovery_response"]["contact_source"]["verified_public"] = False
        self.rejects()

    def test_direct_response_defaults_private(self):
        self.record["discovery_response"]["confidentiality"] = "PUBLIC_AUTHORIZED"
        self.rejects()

    def test_every_statement_requires_evidence_class(self):
        del self.record["discovery_response"]["statements"][0]["evidence_class"]
        self.rejects()

    def test_public_fact_cannot_confirm_application(self):
        self.record["discovery_response"]["statements"][0]["evidence_class"] = "PUBLIC_SOURCE_FACT"
        self.rejects()

    def test_qualifying_state_requires_specific_bottleneck(self):
        self.record["discovery_response"]["current_bottleneck"] = ["UNKNOWN"]
        self.rejects()

    def test_sentinel_cannot_mix_with_bottleneck(self):
        self.record["discovery_response"]["current_bottleneck"].append("UNKNOWN")
        self.rejects()

    def test_hypothesis_requires_real_bottleneck(self):
        response = self.record["discovery_response"]
        response["opportunity_state"] = "INSUFFICIENT_DIRECT_EVIDENCE"
        response["c0_result"] = "INSUFFICIENT_DIRECT_EVIDENCE"
        self.rejects()

    def test_proceed_requires_hypothesis(self):
        self.record["discovery_response"]["improvement_hypothesis"] = None
        self.rejects()

    def test_no_application_requires_direct_testimony(self):
        response = self.record["discovery_response"]
        response.update(
            application_confirmed="NO",
            opportunity_state="NO_CURRENT_APPLICATION",
            current_bottleneck=["NONE_IDENTIFIED"],
            improvement_dimension=["NO_MATERIAL_IMPROVEMENT_NEEDED"],
            improvement_hypothesis=None,
            c0_result="ARCHIVE",
        )
        response["statements"][0]["evidence_class"] = "DIRECT_SERVICE_STATEMENT"
        c0.validate_response(self.record)
        response["statements"][0]["evidence_class"] = "UNKNOWN"
        self.rejects()

    def test_resolved_competitive_has_no_gap(self):
        response = self.record["discovery_response"]
        response.update(
            opportunity_state="RESOLVED_COMPETITIVE",
            current_bottleneck=["NONE_IDENTIFIED"],
            improvement_dimension=["NO_MATERIAL_IMPROVEMENT_NEEDED"],
            improvement_hypothesis=None,
            c0_result="ARCHIVE",
        )
        c0.validate_response(self.record)
        response["current_bottleneck"] = ["TEST_TIME"]
        self.rejects()

    def test_template_is_not_ingestible(self):
        self.record = c0.load("technical-risk/opportunity-validation/templates/phase-c0-response.json")
        self.rejects()


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Targeted positive and adversarial tests for CML v1.1 Task V11-2."""
from __future__ import annotations

import copy
import unittest

import jsonschema

import validate_cml_v11_core as v11


def evidence(evidence_id: str, evidence_type: str, structural_fact: bool = True) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "statement": f"Synthetic {evidence_type.lower()} evidence for validator testing.",
        "source_ref": f"SYNTHETIC-SOURCE-{evidence_id}",
        "structural_fact": structural_fact,
        "limitations": ["Synthetic test fixture; not a real technology claim."],
    }


def valid_pdre() -> dict:
    record = copy.deepcopy(v11.load(v11.TEMPLATES["pdre"]))
    core = record["core"]
    core.update(
        record_id="SE.CML.PDRE.SYNTHETIC.001", subject_id="PDRE-SYNTHETIC-001",
        input_hash="1" * 64, record_hash="2" * 64, verification_status="VALIDATED_TEST_FIXTURE",
    )
    payload = record["pdre_record"]
    payload["record_kind"] = "PDRE_RECORD"
    payload["identity"] = {"cml_id": "CML-SYNTHETIC-001", "pdre_id": "PDRE-SYNTHETIC-001", "title": "Synthetic validation fixture", "primary_research_object": "PDRE_RECORD"}
    payload["old_path"] = {"description": "Synthetic old path", "evidence_refs": ["E-RESEARCH"], "limitations": ["Test fixture."]}
    payload["new_path"] = {"description": "Synthetic alternative path", "evidence_refs": ["E-ENG"], "limitations": ["Test fixture."]}
    payload["current_dependency"].update(dependency_id="DEP-SYNTHETIC-001", technology="Synthetic technology", component="Synthetic component", subsystem="Synthetic subsystem", function="Synthetic function", required_because="Synthetic dependency reason", dependent_elements=["Synthetic element"], substitution_difficulty="HIGH", failure_if_removed="Synthetic function unavailable", current_supplier_structure="Synthetic structure", current_standard_dependency="UNKNOWN", current_certification_dependency="UNKNOWN", evidence_refs=["E-ENG"], unknowns=["No real-world inference."])
    payload["known_evidence"] = [
        evidence("E-RESEARCH", "RESEARCH_PUBLICATION"), evidence("E-PATENT", "PATENT"),
        evidence("E-ENG", "ENGINEERING_VALIDATION"), evidence("E-PILOT", "TEST_RESULT"),
        evidence("E-QUAL", "QUALIFICATION_RESULT"),
    ]
    refs_by_stage = {
        "RESEARCH_THEORY": ["E-RESEARCH"], "PATENT_PROTOTYPE": ["E-PATENT"],
        "ENGINEERING_VALIDATION": ["E-ENG"], "PILOT_APPLICATION": ["E-PILOT"],
        "QUALIFICATION": ["E-QUAL"],
    }
    for stage in payload["pdre"]["pdre_evidence_chain"]:
        if stage["stage"] in refs_by_stage:
            stage.update(status="ESTABLISHED", evidence_refs=refs_by_stage[stage["stage"]], effective_at="2026-01-01T00:00:00Z", known_at="2026-01-02T00:00:00Z", limitations=["Synthetic fixture."])
    payload["pdre"].update(status="CONFIRMED", release_claim="Synthetic path is application-qualified for validator testing.", limitations=["Not a real PDRE."])
    payload["migration_readiness"] = {"code": "R4", "name": "APPLICATION_QUALIFIED", "interpretation": "PRODUCTION_CAPABLE_CANDIDATE", "evidence_refs": ["E-QUAL"], "supports_company_structural_assessment": True, "limitations": ["Synthetic fixture."]}
    payload["alternative_path"] = {"description": "Synthetic alternative path", "viability": "VIABLE", "evidence_refs": ["E-QUAL"], "limitations": ["Synthetic fixture."]}
    payload["path_dependency"]["qualification"] = {"status": "OBSERVED", "statement": "Synthetic qualification lock-in.", "evidence_refs": ["E-QUAL"], "limitations": ["Synthetic fixture."]}
    payload["structural_constraints"] = [{"constraint_class": "CERTIFICATION_LOCK_IN", "status": "OBSERVED", "statement": "Synthetic constraint.", "evidence_refs": ["E-QUAL"], "limitations": ["Synthetic fixture."]}]
    payload["adoption_friction"][1].update(state="HIGH", evidence_refs=["E-QUAL"], limitations=["Synthetic fixture."])
    payload["economics"]["performance"] = {"assessment": "ADVANTAGE", "evidence_refs": ["E-ENG"], "limitations": ["Technical advantage does not establish migration."]}
    payload["structural_exposure"] = {
        "exposure_id": "EXP-SYNTHETIC-001", "technology": [], "component": [], "subsystem": [], "product": [], "supplier": [], "customer": [],
        "company": [{"subject": "Synthetic affected entity", "state": "ACTIVE_MIGRATION", "evidence_refs": ["E-QUAL"], "limitations": ["Not a commercial-customer claim."]}],
        "industry": [], "unknowns": ["Industry exposure unknown."],
    }
    payload["beneficiary_map"] = {
        "beneficiary_map_id": "BEN-SYNTHETIC-001",
        "required_question": "Who gains new economic or strategic optionality if this path dependency is released?",
        "beneficiaries": [{"entity": "Synthetic beneficiary", "beneficiary_class": "SYSTEM_INTEGRATOR", "optionality": "Synthetic integration option", "evidence_refs": ["E-QUAL"], "commercial_target_class": "CHANGE_BENEFICIARY", "commercial_customer_status": "NOT_CONFIRMED", "commercial_evidence_refs": [], "limitations": ["Beneficiary status is not customer status."]}],
        "unknowns": ["Commercial willingness unknown."],
    }
    payload["revision_history"] = [{"revision_id": "REV-001", "created_at": "2026-01-02T00:00:00Z", "supersedes": None, "change_summary": "Synthetic initial record."}]
    return record


class CMLV11CoreTests(unittest.TestCase):
    def setUp(self):
        self.record = valid_pdre()

    def rejects(self) -> None:
        with self.assertRaises((ValueError, KeyError, jsonschema.ValidationError)):
            v11.validate_pdre(self.record)

    def test_framework_schemas_vocabularies_and_templates(self):
        result = v11.framework_integrity()
        self.assertEqual(result, {"schemas": 4, "templates": 4, "readiness_states": 8, "friction_classes": 10})

    def test_valid_synthetic_pdre(self):
        result = v11.validate_pdre(self.record)
        self.assertEqual(result["readiness"], "R4")

    def test_patent_cannot_establish_field_deployment(self):
        stage = self.record["pdre_record"]["pdre"]["pdre_evidence_chain"][6]
        stage.update(status="ESTABLISHED", evidence_refs=["E-PATENT"], effective_at="2026-01-01T00:00:00Z", known_at="2026-01-02T00:00:00Z")
        self.rejects()

    def test_marketing_claim_cannot_establish_engineering_validation(self):
        self.record["pdre_record"]["known_evidence"].append(evidence("E-MARKETING", "MARKETING_CLAIM", False))
        self.record["pdre_record"]["pdre"]["pdre_evidence_chain"][2]["evidence_refs"] = ["E-MARKETING"]
        self.rejects()

    def test_r1_cannot_be_application_qualified(self):
        readiness = self.record["pdre_record"]["migration_readiness"]
        readiness.update(code="R1", name="APPLICATION_QUALIFIED", interpretation="POSSIBLE", evidence_refs=["E-ENG"], supports_company_structural_assessment=False)
        self.rejects()

    def test_r3_cannot_support_company_structural_assessment(self):
        readiness = self.record["pdre_record"]["migration_readiness"]
        readiness.update(code="R3", name="SAMPLE_BENCH_TESTED", interpretation="TECHNICALLY_CREDIBLE", evidence_refs=["E-PILOT"], supports_company_structural_assessment=True)
        self.record["pdre_record"]["pdre"]["status"] = "CANDIDATE"
        self.rejects()

    def test_readiness_cannot_replace_adoption_friction(self):
        self.record["pdre_record"]["adoption_friction"] = [self.record["pdre_record"]["migration_readiness"]]
        self.rejects()

    def test_exposure_cannot_be_reused_as_beneficiary_map(self):
        self.record["pdre_record"]["beneficiary_map"]["beneficiary_map_id"] = "EXP-SYNTHETIC-001"
        self.rejects()

    def test_affected_entity_is_not_automatic_customer(self):
        row = self.record["pdre_record"]["beneficiary_map"]["beneficiaries"][0]
        row["entity"] = "Synthetic affected entity"
        row["commercial_customer_status"] = "CONFIRMED"
        row["commercial_evidence_refs"] = []
        self.rejects()

    def test_opaque_combined_score_rejected(self):
        self.record["pdre_record"]["combined_opportunity_score"] = 99
        self.rejects()

    def test_unknown_friction_cannot_be_inferred_low(self):
        self.record["pdre_record"]["adoption_friction"][9]["state"] = "LOW"
        self.rejects()

    def test_management_statement_cannot_be_structural_fact(self):
        self.record["pdre_record"]["known_evidence"].append(evidence("E-MGMT", "MANAGEMENT_STATEMENT", True))
        self.rejects()

    def test_technical_advantage_does_not_establish_field_migration(self):
        readiness = self.record["pdre_record"]["migration_readiness"]
        readiness.update(code="R5", name="FIELD_DEPLOYED", interpretation="REAL_WORLD_VALIDATED", evidence_refs=["E-ENG"], supports_company_structural_assessment=True)
        self.rejects()

    def test_accusatory_management_inference_rejected(self):
        self.record["pdre_record"]["unknowns"].append("Management failed to adopt the technology.")
        self.rejects()

    def test_standalone_templates_validate(self):
        for kind in ["dependency", "exposure", "beneficiary"]:
            v11.schema_validate(v11.load(v11.TEMPLATES[kind]), kind)


if __name__ == "__main__":
    unittest.main()

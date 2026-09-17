#!/usr/bin/env python3
"""Targeted positive and adversarial tests for CML v1.1 Task V11-3."""
from __future__ import annotations

import copy
import unittest

import jsonschema

import validate_cml_v11_observation as v11


def template(kind: str, subject_class: str) -> dict:
    record=copy.deepcopy(v11.load(v11.TEMPLATES[kind]))
    record["core"].update(record_id=f"SE.CML.SYNTHETIC.{kind}",subject_id="PDRE-SYNTHETIC-001",subject_class=subject_class,input_hash="1"*64,record_hash="2"*64,verification_status="SYNTHETIC_TEST_FIXTURE")
    return record


def trigger() -> dict:
    record=template("trigger","CML_TRIGGER_EVENT")
    event=record["trigger_event"]
    event.update(trigger_id="TRIGGER-SYNTHETIC-001",subject="Synthetic subject",occurrence_status="OBSERVED",effective_at="2026-01-02T00:00:00Z",known_at="2026-01-01T00:00:00Z",source_refs=["S1"],effective_at_evidence_refs=["S1"],known_at_evidence_refs=["S1"],evidence_basis=[{"source_ref":"S1","tier":"TIER_2","evidence_type":"EOL_NOTICE","statement":"Synthetic formal notice."}],affected_dependency="DEP-SYNTHETIC",limitations=["Synthetic fixture."])
    return record


def response(response_type="SUPPLIER_CHANGE") -> dict:
    record=template("response","CML_REAL_WORLD_RESPONSE")
    value=record["real_world_response"]
    value.update(response_id="RESPONSE-SYNTHETIC-001",response_type=response_type,subject="Synthetic entity",pdre_ref="PDRE-SYNTHETIC-001",structural_exposure_ref="EXP-SYNTHETIC-001",observed_at="2026-02-01T00:00:00Z",known_at="2026-02-02T00:00:00Z",source_refs=["S1"],evidence_basis=[{"source_ref":"S1","tier":"TIER_1","evidence_type":"FIELD_OPERATION","statement":"Synthetic observable response."}],limitations=["Synthetic fixture."])
    value["migration_lag"].update(pdre_time="2026-01-01T00:00:00Z",enterprise_adoption_time="2026-02-01T00:00:00Z",migration_lag="P1M",classification="POLICY_NOT_CONFIGURED",classification_policy_ref=None)
    return record


def market() -> dict:
    record=template("market","CML_MARKET_VALIDATION")
    value=record["market_validation"]
    original={"publication_ref":"PUBLIC-PDRE-SYNTHETIC-001","publication_time":"2026-01-01T00:00:00Z","original_hypothesis":"Synthetic hypothesis.","original_state":"UNRESOLVED"}
    original["publication_hash"]=v11.canonical_hash(original)
    value.update(validation_id="VALIDATION-SYNTHETIC-001",pdre_id="PDRE-SYNTHETIC-001",original_publication=original,current_state="PARTIALLY_VALIDATED",validation_events=[{"event_id":"EVENT-001","prior_state":"UNRESOLVED","new_state":"PARTIALLY_VALIDATED","effective_at":"2026-02-01T00:00:00Z","known_at":"2026-02-02T00:00:00Z","evidence_refs":["S1"],"interpretation":"Synthetic partial validation.","preserves_original_publication":True}],revision_history=[{"revision_id":"REV-000","created_at":"2026-01-01T00:00:00Z","event_ref":None,"change_summary":"Original publication preserved."},{"revision_id":"REV-001","created_at":"2026-02-02T00:00:00Z","event_ref":"EVENT-001","change_summary":"Appended validation event."}],limitations=["Synthetic fixture."])
    return record


def failure() -> dict:
    record=template("failure","CML_MIGRATION_FAILURE")
    value=record["migration_failure"]
    value.update(failure_id="FAILURE-SYNTHETIC-001",pdre_id="PDRE-SYNTHETIC-001",FAILURE_CLASS="RELIABILITY",ORIGINAL_HYPOTHESIS="Synthetic hypothesis.",EXPECTED_ADVANTAGE="Synthetic advantage.",FAILED_REQUIREMENT="Synthetic requirement.",ACTUAL_RESULT="Synthetic failure result.",MODEL_REVISION="Synthetic model revision.",effective_at="2026-02-01T00:00:00Z",known_at="2026-02-02T00:00:00Z",evidence_refs=["S1"],revision_history=[{"revision_id":"REV-001","created_at":"2026-02-02T00:00:00Z","failure_preserved":True,"change_summary":"Failure retained as evidence."}],limitations=["Synthetic fixture."])
    return record


def public() -> dict:
    record=template("public","CML_PUBLIC_PDRE_RESEARCH_OBJECT")
    value=record["public_pdre_research_object"]
    value.update(CML_ID="CML-SYNTHETIC-001",PDRE_ID="PDRE-SYNTHETIC-001",PUBLICATION_TIME="2026-01-01T00:00:00Z")
    value["PDRE_RECORD_REF"]={"path":"synthetic/pdre.json","record_id":"SE.CML.PDRE.SYNTHETIC.001","record_hash":"3"*64}
    value["REVISION_HISTORY"]=[{"revision_id":"REV-001","created_at":"2026-01-01T00:00:00Z","supersedes":None,"publication_hash":"4"*64,"change_summary":"Synthetic publication."}]
    return record


class CMLV11ObservationTests(unittest.TestCase):
    def rejects(self,validator,record):
        with self.assertRaises((ValueError,KeyError,jsonschema.ValidationError)):
            validator(record)

    def test_framework_and_positive_synthetic_objects(self):
        self.assertEqual(v11.framework_integrity()["schemas"],5)
        v11.validate_trigger(trigger()); v11.validate_response(response()); v11.validate_market(market()); v11.validate_failure(failure()); v11.validate_public(public())

    def test_ceo_statement_not_deployment_evidence(self):
        record=response(); record["real_world_response"]["evidence_basis"][0].update(tier="TIER_5",evidence_type="CEO_STATEMENT"); self.rejects(v11.validate_response,record)

    def test_marketing_announcement_not_qualification(self):
        record=response("SECOND_SOURCE_QUALIFIED"); record["real_world_response"]["evidence_basis"][0].update(tier="TIER_5",evidence_type="MARKETING_CLAIM"); self.rejects(v11.validate_response,record)

    def test_trigger_not_inferred_from_analyst_commentary(self):
        record=trigger(); record["trigger_event"]["evidence_basis"][0].update(tier="TIER_5",evidence_type="ANALYST_OPINION"); self.rejects(v11.validate_trigger,record)

    def test_known_at_requires_evidence_even_when_copied(self):
        record=trigger(); event=record["trigger_event"]; event["known_at"]=event["effective_at"]; event["known_at_evidence_refs"]=[]; self.rejects(v11.validate_trigger,record)

    def test_no_migration_not_management_failure(self):
        record=response("NO_OBSERVABLE_MIGRATION"); record["real_world_response"]["secondary_inferences"]=[{"inference":"MANAGEMENT_FAILURE","evidence_refs":[],"limitations":["Unsupported."]}]; self.rejects(v11.validate_response,record)

    def test_fast_adopter_requires_policy(self):
        record=response(); lag=record["real_world_response"]["migration_lag"]; lag["classification"]="FAST_ADOPTER"; lag["classification_policy_ref"]=None; self.rejects(v11.validate_response,record)

    def test_later_outcome_cannot_rewrite_original_publication(self):
        record=market(); record["market_validation"]["original_publication"]["original_hypothesis"]="Rewritten after outcome."; self.rejects(v11.validate_market,record)

    def test_failed_migration_cannot_be_removed_from_history(self):
        record=failure(); record["migration_failure"]["revision_history"]=[]; self.rejects(v11.validate_failure,record)

    def test_rejected_hypothesis_cannot_disappear(self):
        record=market(); value=record["market_validation"]; value["original_publication"]["original_state"]="REJECTED"; value["original_publication"]["publication_hash"]=v11.original_publication_digest(value["original_publication"]); value["validation_events"]=[]; value["current_state"]="VALIDATED"; self.rejects(v11.validate_market,record)

    def test_exposure_cannot_auto_create_commercial_target(self):
        record=public(); record["public_pdre_research_object"]["STRUCTURAL_EXPOSURE"]["value"]["company"]=[{"subject":"Synthetic entity","state":"HIGH_LEGACY_EXPOSURE","evidence_refs":["S1"],"limitations":["Synthetic."],"commercial_target_status":"PRIORITY"}]; self.rejects(v11.validate_public,record)

    def test_legacy_incumbent_not_automatic_priority(self):
        record=public(); record["public_pdre_research_object"]["COMMERCIAL_PATHS"]["legacy_incumbent_automatic_priority"]=True; self.rejects(v11.validate_public,record)

    def test_affected_entity_not_automatic_paying_customer(self):
        record=public(); record["public_pdre_research_object"]["COMMERCIAL_PATHS"]["affected_entity_is_paying_customer"]=True; self.rejects(v11.validate_public,record)

    def test_private_customer_data_rejected_from_public_object(self):
        record=public(); record["public_pdre_research_object"]["private_customer_bom"]="SECRET"; self.rejects(v11.validate_public,record)

    def test_second_evidence_core_rejected(self):
        record=public(); record["evidence_core"]={}; self.rejects(v11.validate_public,record)

    def test_opaque_market_score_rejected(self):
        record=market(); record["market_validation"]["market_score"]=90; self.rejects(v11.validate_market,record)


if __name__=="__main__": unittest.main()

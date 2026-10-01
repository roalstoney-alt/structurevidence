#!/usr/bin/env python3
"""Build deterministic Agent Discovery projections from frozen public primitives."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "agent-discovery" / "claim-registry-v0.1.json"
METHOD_URL = "https://structurevidence.org/method-contract.json"
VERSION_DOI = "10.5281/zenodo.23033588"
VERSION_DOI_URL = f"https://doi.org/{VERSION_DOI}"
CONCEPT_DOI = "10.5281/zenodo.23033587"
CONCEPT_DOI_URL = f"https://doi.org/{CONCEPT_DOI}"
ZENODO_RECORD = "https://zenodo.org/records/23033588"
INFERENCE_RULE = "An inference not explicitly represented by the claim state, supports, does_not_support, unknowns, or approved scope must not be treated as supported."
SNAPSHOT_COMMIT = "58c7c4fe9fa334e030080cf7ab352c222b326ec2"
SNAPSHOT_REPOSITORY = "https://github.com/roalstoney-alt/structurevidence"
SNAPSHOT_PERMALINK = f"{SNAPSHOT_REPOSITORY}/tree/{SNAPSHOT_COMMIT}"
UNRESOLVED = {"UNKNOWN", "NOT_ESTABLISHED", "VERIFICATION_REQUIRED"}


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def compact(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def unique(values):
    return list(dict.fromkeys(value for value in values if value))


def normalized_state(claim):
    legacy = claim["state"]
    epistemic = {
        "SUPPORTED": "SUPPORTED",
        "NOT_ESTABLISHED": "NOT_ESTABLISHED",
        "UNKNOWN": "UNKNOWN",
        "SUPPORTED_SINGLE_INSTANCE": "SUPPORTED",
        "SUPPORTED_FOR_TRIAL_POPULATION": "SUPPORTED",
        "SUPPORTED_FOR_DEFINED_CONTEXT": "SUPPORTED",
        "VERIFICATION_REQUIRED": "UNKNOWN",
    }[legacy]
    verification_depth = "FIELD_DEPLOYED_SINGLE_INSTANCE" if legacy == "SUPPORTED_SINGLE_INSTANCE" else "NOT_EVALUATED"
    applicability_scope = {
        "SUPPORTED_FOR_TRIAL_POPULATION": "POPULATION_SPECIFIC",
        "SUPPORTED_FOR_DEFINED_CONTEXT": "USE_CASE_SPECIFIC",
    }.get(legacy, "UNKNOWN")
    workflow_state = "VERIFICATION_REQUIRED" if legacy == "VERIFICATION_REQUIRED" else "NONE"
    mapping_status = "REVIEW_REQUIRED" if legacy == "VERIFICATION_REQUIRED" else "DETERMINISTIC"
    return {
        "claim_id": claim["claim_id"],
        "legacy_state": legacy,
        "normalized": {
            "epistemic_state": epistemic,
            "verification_depth": verification_depth,
            "applicability_scope": applicability_scope,
            "freshness_state": "CURRENT",
            "workflow_state": workflow_state,
        },
        "mapping_basis": (
            "Legacy VERIFICATION_REQUIRED is a workflow state; no explicit epistemic resolution is present in the source primitive."
            if legacy == "VERIFICATION_REQUIRED"
            else f"Deterministic mapping from legacy state {legacy}; unspecified orthogonal axes remain UNKNOWN or NOT_EVALUATED."
        ),
        "mapping_status": mapping_status,
    }


def state_normalization(claims):
    return {
        "$schema": "state-normalization/schema-v0.1.json",
        "version": "STATE_NORMALIZATION_v0.1",
        "inference_policy": "CLOSED_BOUNDARY",
        "undeclared_inference": "OUT_OF_BOUNDARY",
        "axes": {
            "epistemic_state": ["SUPPORTED", "NOT_ESTABLISHED", "CONTRADICTED", "UNKNOWN"],
            "verification_depth": ["SOURCE_STATEMENT", "MULTI_SOURCE_CORROBORATED", "NAMED_OPERATOR_SOURCE", "INDEPENDENT_VALIDATION", "FIELD_DEPLOYED_SINGLE_INSTANCE", "FIELD_DEPLOYED_MULTI_ENTITY", "OPERATING_HISTORY", "REPEAT_PROCUREMENT", "NOT_EVALUATED", "UNKNOWN"],
            "applicability_scope": ["GENERAL", "ARCHITECTURE_SPECIFIC", "GEOGRAPHY_SPECIFIC", "POPULATION_SPECIFIC", "USE_CASE_SPECIFIC", "CUSTOMER_SPECIFIC_NOT_EVALUATED", "UNKNOWN"],
            "freshness_state": ["CURRENT", "REVIEW_DUE", "STALE", "UNKNOWN"],
            "workflow_state": ["NONE", "VERIFICATION_REQUIRED", "HUMAN_REVIEW_REQUIRED", "PUBLICATION_REVIEW_REQUIRED", "CLOSED"],
        },
        "claims": [normalized_state(claim) for claim in claims],
    }


def source_bundle(case_id: str):
    if case_id == "CML-PDRE-001":
        return {
            "state": load("cases/800vdc/state-v0.1.json"),
            "control": load("technical-risk/cml-v1.1/pdre/CML-PDRE-001/publication-control.json"),
            "memory": None,
            "stop": (ROOT / "cases/800vdc/stop-v0.1.html").read_text(encoding="utf-8"),
        }
    slug = "sodium-ion-bess" if case_id == "SE-BESS-SODIUM-001" else "nsq-nsclc-china"
    return {
        "state": load(f"cases/{slug}/state-v0.1.json"),
        "control": load(f"cases/{slug}/publication-control-v0.1.json"),
        "memory": load(f"cases/{slug}/decision-memory-v0.1.json"),
        "stop": (ROOT / f"cases/{slug}/stop-v0.1.html").read_text(encoding="utf-8"),
    }


def validate_primitives(registry, bundles) -> None:
    required_ids = set(registry["cases"])
    if required_ids != {"CML-PDRE-001", "SE-BESS-SODIUM-001", "SE-ONC-NSQNSCLC-CN-001"}:
        raise ValueError("PRIMITIVE_CONSISTENCY_ERROR: case registry mismatch")
    claim_ids = [row["claim_id"] for row in registry["claims"]]
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("PRIMITIVE_CONSISTENCY_ERROR: duplicate claim ID")
    for case_id, bundle in bundles.items():
        state = bundle["state"]
        control = bundle["control"]
        if state["case_id"] != case_id or control["case_id"] != case_id:
            raise ValueError(f"PRIMITIVE_CONSISTENCY_ERROR: case identity mismatch for {case_id}")
        cutoff = state["knowledge_cutoff"]
        control_cutoff = control.get("knowledge_cutoff") or bundle["stop"]
        if cutoff not in str(control_cutoff):
            raise ValueError(f"PRIMITIVE_CONSISTENCY_ERROR: cutoff mismatch for {case_id}")
        if cutoff not in bundle["stop"]:
            raise ValueError(f"PRIMITIVE_CONSISTENCY_ERROR: stop-point cutoff mismatch for {case_id}")
        if bundle["memory"]:
            memory = bundle["memory"]["decision_memory"]
            if memory["case_id"] != case_id or memory["temporal_index"]["knowledge_cutoff"] != cutoff:
                raise ValueError(f"PRIMITIVE_CONSISTENCY_ERROR: Decision Memory mismatch for {case_id}")
    cml = bundles["CML-PDRE-001"]
    boundary = cml["control"]["projection_scope"]["approved_claim_boundary"]
    if cml["state"]["claim_boundary"] != boundary or cml["state"]["current_bounded_state"] not in cml["stop"]:
        raise ValueError("PRIMITIVE_CONSISTENCY_ERROR: CML public boundary mismatch")


def provenance(case_id: str, slug: str, has_memory: bool):
    rows = [
        {"source_ref": f"cases/{slug}/state-v0.1.json", "source_role": "PRIMARY_PUBLIC_EVIDENCE_STATE"},
        {"source_ref": f"cases/{slug}/stop-v0.1.html", "source_role": "HUMAN_CITATION_BOUNDARY"},
    ]
    control = (
        "technical-risk/cml-v1.1/pdre/CML-PDRE-001/publication-control.json"
        if case_id == "CML-PDRE-001"
        else f"cases/{slug}/publication-control-v0.1.json"
    )
    rows.append({"source_ref": control, "source_role": "PUBLICATION_AUTHORITY"})
    if has_memory:
        rows.append({"source_ref": f"cases/{slug}/decision-memory-v0.1.json", "source_role": "DECISION_STRUCTURE"})
    return rows


def project_claim(row, case, bundle):
    state = bundle["state"]
    memory = bundle["memory"]["decision_memory"] if bundle["memory"] else None
    source_kind = row["source_kind"]
    supports = []
    does_not_support = []
    unknowns = []
    if source_kind == "state_map":
        claim_state = state["states" if case["source_kind"] == "cml_state" else "current_state"][row["source_key"]]
        if case["source_kind"] == "cml_state":
            supports = state["supports"]
            does_not_support = state["does_not_support"]
            unknowns = state["unknowns"]
            next_observable = state["next_minimum_verification"]
        else:
            records = {record["record_id"]: record for record in state["records"]}
            selected = [records[record_id] for record_id in row.get("support_records", [])]
            supports = [record["accepted_support"] for record in selected]
            does_not_support = [record["does_not_support"] for record in selected]
            unknowns = [
                f"{key}: {value}"
                for key, value in state["current_state"].items()
                if value in UNRESOLVED or value.startswith("NOT_ESTABLISHED")
            ]
            next_observable = "; ".join(state["next_transition_evidence"])
    elif source_kind == "nsclc_claim":
        source = next(claim for claim in state["claims"] if claim["claim_id"] == row["source_key"])
        claim_state = source["status"]
        supports = [source["statement"]]
        does_not_support = [source.get("limits", "NOT_RECORDED")]
        unknowns = state["search_provenance"]["unsearched_or_unresolved"]
        next_observable = "; ".join(state["reopen_triggers"])
    elif source_kind == "decision_state":
        source = next(item for item in memory["evidence_states"] if item["state_id"] == row["source_key"])
        claim_state = source["status"]
        supports = []
        does_not_support = source["limitations"]
        unknowns = [
            item["question"]
            for item in memory["unknowns"]
            if row["source_key"] in item["affected_state_refs"]
        ]
        if not unknowns and claim_state in UNRESOLVED:
            unknowns = [source["label"]]
        next_observable = "; ".join(state["reopen_triggers"])
    else:
        raise ValueError(f"Unknown source_kind: {source_kind}")

    if not does_not_support:
        raise ValueError(f"DOES_NOT_SUPPORT missing for {row['claim_id']}")
    slug = case["slug"]
    claim = {
        "claim_id": row["claim_id"],
        "case_id": row["case_id"],
        "version": "v0.1",
        "statement": row["statement"],
        "case_title": case["title"],
        "state": claim_state,
        "as_of": state["knowledge_cutoff"],
        "scope": state.get("scope", "Public case scope as frozen in state-v0.1.json."),
        "supports": unique(supports),
        "does_not_support": unique(does_not_support),
        "unknowns": unique(unknowns),
        "counter_evidence": [],
        "next_observable": next_observable or "NOT_RECORDED",
        "provenance": provenance(row["case_id"], slug, memory is not None),
        "canonical_url": f"https://structurevidence.org/claims/{row['claim_id']}.json",
        "state_url": f"https://structurevidence.org/cases/{slug}/state-v0.1.json",
        "stop_point_url": f"https://structurevidence.org/cases/{slug}/stop-v0.1.html",
        "method_contract": METHOD_URL,
        "citation_requirements": {
            "must_preserve_state": True,
            "must_preserve_as_of": True,
            "must_include_boundary_when_material": True,
        },
        "aliases": unique(case["aliases"] + row.get("aliases", [])),
        "keywords": unique(row.get("keywords", [])),
    }
    return claim


def method_contract():
    principles = [
        ("FACT_NE_CLAIM", "A fact, claim, evidence record and decision are distinct objects."),
        ("EVENT_TIME_NE_KNOWLEDGE_TIME", "When an event occurred is distinct from when it became known within the evidence system."),
        ("NOT_FOUND_NE_DOES_NOT_EXIST", "Failure to find evidence within a defined search scope does not prove non-existence."),
        ("SINGLE_INSTANCE_NE_INDUSTRY_ADOPTION", "One deployment does not establish broad adoption."),
        ("ORDER_NE_DELIVERY", "An order does not establish delivery."),
        ("DELIVERY_NE_COMMISSIONING", "Delivery does not establish commissioning."),
        ("COMMISSIONING_NE_OPERATING_HISTORY", "Commissioning does not establish operating history."),
        ("SOURCE_STATEMENT_NE_INDEPENDENT_VALIDATION", "A source's own statement is not independent third-party validation."),
        ("UNKNOWN_MUST_NOT_BE_INFERRED", "Unknown states remain unknown until qualifying evidence resolves them."),
        ("UNDECLARED_INFERENCE_NOT_AUTHORIZED", INFERENCE_RULE),
        ("TIME_BOUNDED_STATE", "Every evidence state has a knowledge-time boundary."),
        ("PROTOCOL_BOUNDED_STATE", "Every evidence state identifies the protocol or evidence contract under which it was produced."),
        ("APPEND_DONT_ERASE", "New evidence creates new state versions; previous approved public states remain retrievable."),
        ("CHANGE_IS_DATA", "A transition from one evidence state to another is itself a first-class evidence record."),
        ("EVIDENCE_STATE_NE_DECISION", "A defensible evidence state constrains the decision space but does not determine the final decision."),
        ("AGENT_READS_ACTOR_DECIDES", "Agents may retrieve, compare, explain and trace evidence states; the responsible actor owns the final decision."),
    ]
    return {
        "method": "StructEvidence Temporal Evidence Method",
        "version": "1.0",
        "purpose": "Prevent unsupported inference by separating evidence state, time boundary, and unresolved uncertainty.",
        "question_protocol": {
            "version": "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1",
            "flow": ["QUESTION_INTAKE", "CLAIM_MATCH", "PUBLIC_STOP_POINT", "MINIMUM_MISSING_EVIDENCE", "HUMAN_AUTHORIZED_VERIFY"],
            "match_classes": ["EXACT", "ISOMORPHIC", "PARTIAL", "NONE"],
            "commerce_boundary": "PROCESS_BOUGHT_OUTCOME_NOT_BOUGHT",
            "automatic_research_authorization": False,
        },
        "scholarly_record": {
            "title": "From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States",
            "publication_type": "methods_preprint",
            "version": "v0.1",
            "published_at": "2026-09-29",
            "version_doi": VERSION_DOI,
            "version_doi_url": VERSION_DOI_URL,
            "concept_doi": CONCEPT_DOI,
            "concept_doi_url": CONCEPT_DOI_URL,
            "zenodo_record": ZENODO_RECORD,
            "canonical_scholarly_version": "VERSION_DOI",
            "canonical_scholarly_family": "CONCEPT_DOI",
            "replication_repository": "https://github.com/roalstoney-alt/structurevidence",
            "public_method_site": "https://structurevidence.org",
            "machine_method_contract": METHOD_URL,
        },
        "inference_policy": {
            "mode": "CLOSED_BOUNDARY",
            "rule_id": "UNDECLARED_INFERENCE_NOT_AUTHORIZED",
            "statement": INFERENCE_RULE,
            "undeclared_inference": "OUT_OF_BOUNDARY",
        },
        "state_normalization": {
            "version": "STATE_NORMALIZATION_v0.1",
            "document": "https://structurevidence.org/protocol/state-normalization-v0.1.json",
            "schema": "https://structurevidence.org/protocol/state-normalization/schema-v0.1.json",
            "additive": True,
            "legacy_state_preserved": True,
        },
        "state_identity": {
            "required_dimensions": ["claim_id", "as_of", "protocol_version", "snapshot_commit"],
        },
        "decision_ownership": {
            "evidence_state_determines_decision": False,
            "agent_may": ["RETRIEVE", "COMPARE", "EXPLAIN", "TRACE"],
            "final_decision_authority": "RESPONSIBLE_ACTOR",
        },
        "change_object_contract": {
            "history_policy": "APPEND_DONT_ERASE",
            "required_fields_when_transition_exists": ["claim_id", "from_state", "to_state", "from_as_of", "to_as_of", "protocol_version", "transition_evidence", "published_at", "snapshot_commit", "supersedes"],
        },
        "principles": [{"id": key, "statement": statement} for key, statement in principles],
        "required_claim_fields": ["claim_id", "case_id", "statement", "state", "as_of", "supports", "does_not_support", "unknowns", "provenance", "next_observable", "canonical_url"],
    }


def agent_html(claim_count: int):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>StructEvidence for Agents</title><meta name="description" content="Resolve questions to time-bounded public evidence states without inferring beyond the evidence.">
<link rel="canonical" href="https://structurevidence.org/agent/"><link rel="stylesheet" href="/assets/product.css?v=20260928-stop-2"></head>
<body class="product-site"><a class="skip-link" href="#main">Skip to content</a><header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><div class="product-links"><a href="/cases/">Evidence Cases</a><a href="/method-contract.json">Method Contract</a></div></nav></header>
<main class="product-main" id="main"><section class="page-hero"><p class="eyebrow">Agent Discovery Layer · v0.1</p><h1>StructEvidence for Agents</h1><p class="lead">Resolve a question to a time-bounded evidence state before inferring beyond the evidence.</p></section>
<section class="product-section"><div class="section-head"><div><p class="eyebrow">Public research plane</p><h2>Deterministic evidence retrieval.</h2></div><p>StructEvidence exposes {claim_count} stable claim objects derived from three governed public cases. The resolver uses explicit aliases and keywords—no LLM and no external search.</p></div><div class="boundary-grid"><div><p class="field-label">Always preserve</p><p>Claim state, as-of boundary, supports, does not support, unknowns, provenance, and next observable.</p></div><div><p class="field-label">Never delegated</p><p>Research authorization, publication approval, deployment decisions, customer actions, or patient-specific medical advice.</p></div></div></section>
<section class="product-section"><div class="section-head"><div><p class="eyebrow">Question protocol</p><h2>Question → claim → stop-point → missing evidence.</h2></div><p>The intake gate checks whether a question is atomic, falsifiable, scoped, and time-bounded. Governed matches are classified as EXACT, ISOMORPHIC, PARTIAL, or NONE. Sufficient public evidence is cited and stopped; only the minimum missing evidence may proceed to a human-authorized verification scope.</p></div><p>Freshness, verification depth, and applicability remain explicit. A quote is not research authorization, payment does not buy a desired outcome, and paid evidence is not public without a separate eligibility review and human publication approval.</p></section>
<section class="product-section"><div class="section-head"><div><p class="eyebrow">State identity</p><h2>Claim + as-of + protocol + snapshot.</h2></div><p>Every stop-point should be interpreted with its claim ID, knowledge cutoff, protocol version, and recoverable snapshot hash.</p></div><div class="boundary-grid"><div><p class="field-label">Decision boundary</p><p>Agents retrieve, compare, explain, and trace evidence states. They do not own the final decision. The responsible actor decides.</p></div><div><p class="field-label">Preferred citation unit</p><p><strong>Claim:</strong> &lt;claim_id&gt;<br><strong>State:</strong> &lt;state&gt;<br><strong>As of:</strong> &lt;timestamp&gt;<br><strong>Protocol:</strong> &lt;protocol_version&gt;<br><strong>Snapshot:</strong> &lt;commit hash&gt;<br><strong>Canonical:</strong> &lt;claim URL&gt;</p></div></div></section>
<section class="product-section"><div class="section-head"><div><p class="eyebrow">Scholarly reference</p><h2>From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States</h2></div><p>Version DOI: <a href="{VERSION_DOI_URL}">{VERSION_DOI}</a><br>Concept DOI: <a href="{CONCEPT_DOI_URL}">{CONCEPT_DOI}</a></p></div></section>
<section class="product-section"><div class="actions"><a class="button" href="/claims/index.json">Enumerate claims</a><a class="button secondary" href="/method-contract.json">Read method contract</a><a class="button secondary" href="/.well-known/structurevidence.json">Open discovery manifest</a></div><p>Runtime resolver: <code>GET https://api.structurevidence.org/resolve?q=&lt;question&gt;</code>. Commercial capabilities are described separately at <a href="https://structevidence.com/capabilities.json">structevidence.com/capabilities.json</a>; human authorization is required.</p></section></main>
<footer class="product-footer"><div class="product-wrap footer-grid"><strong>StructEvidence</strong><a href="/claims/index.json">Claims</a><a href="/changes.json">Changes</a><span>Discovery and resolution only.</span></div></footer></body></html>'''


def build_outputs():
    registry = load("agent-discovery/claim-registry-v0.1.json")
    bundles = {case_id: source_bundle(case_id) for case_id in registry["cases"]}
    validate_primitives(registry, bundles)
    claims = []
    for row in registry["claims"]:
        case = registry["cases"][row["case_id"]]
        claims.append(project_claim(row, case, bundles[row["case_id"]]))
    if len(claims) != len({claim["claim_id"] for claim in claims}):
        raise ValueError("Duplicate projected claim ID")

    index = {
        "version": registry["version"],
        "generated_at": registry["generated_at"],
        "claims": [
            {key: claim[key] for key in ("claim_id", "case_id", "statement", "state", "as_of", "canonical_url")}
            for claim in claims
        ],
    }
    discovery = {
        "name": "StructEvidence",
        "version": "0.1",
        "type": "temporal_evidence_resolution_layer",
        "description": "Versioned, time-bounded evidence states for claims that matter.",
        "method_contract": METHOD_URL,
        "claims_index": "https://structurevidence.org/claims/index.json",
        "changes": "https://structurevidence.org/changes.json",
        "capabilities": "https://structevidence.com/capabilities.json",
        "resolve_endpoint": "https://api.structurevidence.org/resolve",
        "state_normalization": "https://structurevidence.org/protocol/state-normalization-v0.1.json",
        "temporal_state": {
            "requires_as_of": True,
            "requires_protocol_version": True,
            "historical_states_preserved": True,
            "change_is_data": True,
        },
        "decision_boundary": {
            "agent_role": "RETRIEVE_COMPARE_EXPLAIN_TRACE",
            "final_decision_authority": "RESPONSIBLE_ACTOR",
        },
        "scholarly_record": {
            "version_doi": VERSION_DOI,
            "version_doi_url": VERSION_DOI_URL,
            "concept_doi": CONCEPT_DOI,
            "concept_doi_url": CONCEPT_DOI_URL,
            "zenodo_record": ZENODO_RECORD,
        },
        "public_cases": list(registry["cases"]),
        "principles": ["EVENT_TIME_NE_KNOWLEDGE_TIME", "NOT_FOUND_NE_DOES_NOT_EXIST", "SINGLE_INSTANCE_NE_INDUSTRY_ADOPTION", "SOURCE_STATEMENT_NE_INDEPENDENT_VALIDATION", "UNKNOWN_MUST_NOT_BE_INFERRED"],
    }
    changes = {
        "version": "0.1",
        "generated_at": registry["generated_at"],
        "changes": [
            {
                "id": "CML-PDRE-001-2026-09-20",
                "type": "STATE_CHANGE",
                "date": "2026-09-20",
                "case_id": "CML-PDRE-001",
                "case_url": "https://structurevidence.org/cases/800vdc/",
                "previous_state": "R5_FIELD_DEPLOYED_NOT_ESTABLISHED",
                "new_state": "R5_ARCHITECTURE_FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE",
                "why": "Human review accepted one attributable operator record for one named commercial deployment.",
                "triggering_evidence": "L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001",
                "triggering_evidence_url": "https://structurevidence.org/e/L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001/",
                "qualifying_evidence_added": 1,
                "unknowns_resolved": 0,
                "state_changed": True,
            }
        ],
        "note": "Only material evidence and state changes are included. Publication baselines and cosmetic site changes are excluded.",
    }
    capabilities = {
        "provider": "StructEvidence",
        "version": "0.1",
        "services": [
            {"service_id": "VERIFY_CLAIM", "description": "Verify a bounded technical or industrial claim against attributable evidence.", "input": ["claim_or_question", "decision_context_optional"], "output": ["bounded_verification_record", "supports", "does_not_support", "unknowns", "provenance"], "supports_question_intake": True, "supports_minimum_missing_evidence": True, "quote_requires_human_authorization": True, "outcome_guaranteed": False, "human_authorization_required": True, "automatic_research_authorization": False, "commercial_endpoint": "https://structevidence.com/verify/"},
            {"service_id": "CUSTOMER_CONTEXT", "description": "Map public evidence to a specific company, architecture or decision context.", "human_authorization_required": True, "automatic_research_authorization": False, "commercial_endpoint": "https://structevidence.com/context/"},
            {"service_id": "DECISION_PACK", "description": "Build a decision-ready evidence package for a defined decision boundary.", "human_authorization_required": True, "automatic_research_authorization": False, "commercial_endpoint": "https://structevidence.com/decision-pack/"},
        ],
    }

    outputs = {}
    static = {
        ".well-known/structurevidence.json": compact(discovery),
        "method-contract.json": compact(method_contract()),
        "claims/index.json": compact(index),
        "changes.json": compact(changes),
        "agent/index.html": agent_html(len(claims)).encode("utf-8"),
        "protocol/state-normalization-v0.1.json": compact(state_normalization(claims)),
        "protocol/state-normalization/schema-v0.1.json": (ROOT / "protocol/state-normalization/schema-v0.1.json").read_bytes(),
    }
    for claim in claims:
        static[f"claims/{claim['claim_id']}.json"] = compact(claim)
    for relative, content in static.items():
        outputs[relative] = content
        outputs[f"docs/{relative}"] = content
    claims_js = "// Generated by scripts/build_agent_discovery.py; do not edit.\nexport const CLAIMS = " + json.dumps(claims, ensure_ascii=False, separators=(",", ":")) + ";\n"
    outputs["deploy/cloudflare-evidence-resolver/claims.js"] = claims_js.encode("utf-8")
    capabilities_js = "// Generated by scripts/build_agent_discovery.py; do not edit.\nexport const CAPABILITIES = " + json.dumps(capabilities, ensure_ascii=False, separators=(",", ":")) + ";\n"
    outputs["deploy/cloudflare-landing/capabilities.js"] = capabilities_js.encode("utf-8")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    urls = [
        "https://structurevidence.org/.well-known/structurevidence.json",
        "https://structurevidence.org/method-contract.json",
        "https://structurevidence.org/claims/index.json",
        "https://structurevidence.org/changes.json",
        "https://structurevidence.org/agent/",
    ] + [claim["canonical_url"] for claim in claims]
    additions = "".join(f"<url><loc>{url}</loc></url>\n" for url in urls if f"<loc>{url}</loc>" not in sitemap)
    expected_sitemap = sitemap.replace("</urlset>", additions + "</urlset>")
    outputs["sitemap.xml"] = expected_sitemap.encode("utf-8")
    outputs["docs/sitemap.xml"] = expected_sitemap.encode("utf-8")
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if stale:
        print("STALE_AGENT_DISCOVERY_OUTPUTS")
        print("\n".join(stale))
        return 1
    print(f"AGENT_DISCOVERY_OUTPUTS={'CURRENT' if args.check else 'GENERATED'} count={len(outputs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

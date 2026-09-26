#!/usr/bin/env python3
"""StructEvidence Temporal State Protocol v0.1 primitives."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "se-frr"
PROTOCOL_VERSION = "SE_TEMPORAL_PROTOCOL_v0.1"
SCHEMAS = {
    "subjects": "subject.schema.json",
    "evidence": "evidence.schema.json",
    "states": "state.schema.json",
    "changes": "change-event.schema.json",
    "branches": "branch.schema.json",
    "requests": "request.schema.json",
    "challenges": "challenge.schema.json",
    "outcomes": "outcome.schema.json",
}
ID_FIELDS = {
    "subjects": "subject_id", "evidence": "evidence_id", "states": "state_id",
    "changes": "change_id", "branches": "branch_id", "requests": "request_id",
    "challenges": "challenge_id", "outcomes": "outcome_id",
}
HASH_FIELDS = {
    "evidence": ("content_hash",),
    "state": ("state_hash", "chain_hash"),
    "change": ("change_hash",),
}


class ProtocolError(ValueError):
    """A Temporal Protocol invariant was violated."""


def canonical_json(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON (sorted keys, no insignificant whitespace)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_object_hash(value: dict[str, Any], excluded_fields: Iterable[str]) -> str:
    material = copy.deepcopy(value)
    for field in excluded_fields:
        material.pop(field, None)
    return sha256_hex(canonical_json(material))


def evidence_hash(evidence: dict[str, Any]) -> str:
    return canonical_object_hash(evidence, HASH_FIELDS["evidence"])


def state_hash(state: dict[str, Any]) -> str:
    return canonical_object_hash(state, HASH_FIELDS["state"])


def change_hash(change: dict[str, Any]) -> str:
    return canonical_object_hash(change, HASH_FIELDS["change"])


def chain_hash(current_state_hash: str, previous_chain_hash: str | None = None) -> str:
    material = current_state_hash if previous_chain_hash is None else previous_chain_hash + current_state_hash
    return sha256_hex(material.encode("ascii"))


def finalize_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(evidence)
    result["content_hash"] = evidence_hash(result)
    return result


def finalize_state(state: dict[str, Any], previous_chain_hash: str | None = None) -> dict[str, Any]:
    result = copy.deepcopy(state)
    result["state_hash"] = state_hash(result)
    result["chain_hash"] = chain_hash(result["state_hash"], previous_chain_hash)
    return result


def finalize_change(change: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(change)
    result["change_hash"] = change_hash(result)
    return result


def load_schema(kind: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / SCHEMAS[kind]).read_text(encoding="utf-8"))


def validate_schema(kind: str, value: dict[str, Any]) -> None:
    schema = load_schema(kind)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(value)


def verify_state_chain(states: Iterable[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for state in states:
        grouped[state["subject_id"]].append(state)
    result = {"subjects_checked": len(grouped), "states_checked": 0, "chains_valid": 0, "chains_invalid": 0, "broken_links": [], "hash_mismatches": []}
    for subject_id, subject_states in sorted(grouped.items()):
        ordered = sorted(subject_states, key=lambda item: (item["recorded_at"], item["state_id"]))
        previous = None
        valid = True
        for state in ordered:
            result["states_checked"] += 1
            expected_state_hash = state_hash(state)
            if state.get("state_hash") != expected_state_hash:
                result["hash_mismatches"].append({"state_id": state["state_id"], "field": "state_hash"})
                valid = False
            expected_chain_hash = chain_hash(expected_state_hash, previous.get("chain_hash") if previous else None)
            if state.get("chain_hash") != expected_chain_hash:
                result["hash_mismatches"].append({"state_id": state["state_id"], "field": "chain_hash"})
                valid = False
            if previous is None:
                if state.get("previous_state_id") is not None or state.get("previous_state_hash") is not None:
                    result["broken_links"].append({"state_id": state["state_id"], "reason": "first state has predecessor"})
                    valid = False
            elif state.get("previous_state_id") != previous["state_id"] or state.get("previous_state_hash") != previous["state_hash"]:
                result["broken_links"].append({"state_id": state["state_id"], "reason": "predecessor mismatch"})
                valid = False
            previous = state
        result["chains_valid" if valid else "chains_invalid"] += 1
    result["result"] = "PASS" if not result["chains_invalid"] else "FAIL"
    return result


def append_state(directory: Path, state: dict[str, Any]) -> Path:
    """Append a state as a new file; existing state IDs are immutable."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{state['state_id']}.json"
    if target.exists():
        raise ProtocolError(f"canonical State already exists: {state['state_id']}")
    existing = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]
    check = verify_state_chain(existing)
    if check["result"] != "PASS":
        raise ProtocolError("existing State chain is invalid")
    same_subject = sorted((item for item in existing if item["subject_id"] == state["subject_id"]), key=lambda item: (item["recorded_at"], item["state_id"]))
    if same_subject:
        previous = same_subject[-1]
        if state.get("previous_state_id") != previous["state_id"] or state.get("previous_state_hash") != previous["state_hash"]:
            raise ProtocolError("new State does not link to the current tail")
    elif state.get("previous_state_id") is not None or state.get("previous_state_hash") is not None:
        raise ProtocolError("first State cannot name a predecessor")
    validate_schema("states", state)
    candidate_check = verify_state_chain([*existing, state])
    if candidate_check["result"] != "PASS":
        raise ProtocolError("new State hash or chain link is invalid")
    with target.open("x", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return target


def outcome_to_evidence(outcome: dict[str, Any], evidence_id: str, recorded_at: str, reviewer: str) -> dict[str, Any]:
    """Create later Evidence from an Outcome without mutating the State it used."""
    if outcome["verification_status"] not in {"SUPPORTED", "VERIFIED"}:
        raise ProtocolError("Outcome must be supported or verified before evidence conversion")
    visibility = "PUBLIC" if outcome["authorization_for_public_use"] and outcome["visibility"] == "PUBLIC" else "CUSTOMER_PRIVATE"
    evidence = {
        "schema_version": "SE_EVIDENCE_v0.1", "evidence_id": evidence_id, "subject_id": outcome["subject_id"],
        "published_at": outcome["reported_at"], "observed_at": outcome["reported_at"], "recorded_at": recorded_at, "effective_at": outcome["action_at"],
        "source": {"name": "Authorized outcome report", "url": None, "type": "OUTCOME_REPORT", "publisher": None, "snapshot_ref": outcome["outcome_id"], "retrieved_at": recorded_at},
        "raw_reference": outcome["outcome_id"], "normalized_claim": outcome["reported_result"], "evidence_type": "REAL_WORLD_OUTCOME",
        "review": {"status": "ACCEPTED", "reason": "Converted through controlled Outcome review path.", "reviewed_at": recorded_at, "reviewed_by": reviewer},
        "counter_to": [], "research_class": "CUSTOMER_SPECIFIC_RESEARCH", "visibility": visibility, "content_hash": "0" * 64,
        "provenance": {"repository": "StructEvidence protected customer plane", "commit_sha": None, "source_object": outcome["outcome_id"], "created_by": reviewer, "method_version": PROTOCOL_VERSION, "recorded_at": recorded_at, "supersedes": None, "superseded_by": None}
    }
    return finalize_evidence(evidence)


def load_objects(root: Path) -> dict[str, list[dict[str, Any]]]:
    objects: dict[str, list[dict[str, Any]]] = {}
    for kind in SCHEMAS:
        directory = root / kind
        objects[kind] = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))] if directory.exists() else []
    return objects


def validate_bundle(objects: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    errors = {"schema": [], "reference": [], "hash": [], "chain": [], "privacy": []}
    index: dict[str, dict[str, Any]] = {}
    object_count = 0
    for kind, values in objects.items():
        for value in values:
            object_count += 1
            try:
                validate_schema(kind, value)
            except Exception as exc:  # jsonschema exposes several useful subclasses
                errors["schema"].append(f"{kind}:{value.get(ID_FIELDS[kind], 'UNKNOWN')}:{exc}")
            object_id = value.get(ID_FIELDS[kind])
            if object_id in index:
                errors["reference"].append(f"duplicate ID: {object_id}")
            elif object_id:
                index[object_id] = value

    subjects = {item["subject_id"]: item for item in objects["subjects"]}
    evidence = {item["evidence_id"]: item for item in objects["evidence"]}
    states = {item["state_id"]: item for item in objects["states"]}
    changes = {item["change_id"]: item for item in objects["changes"]}
    branches = {item["branch_id"]: item for item in objects["branches"]}

    for item in objects["evidence"]:
        if item["subject_id"] not in subjects:
            errors["reference"].append(f"unknown Evidence subject: {item['evidence_id']}")
        if item.get("content_hash") != evidence_hash(item):
            errors["hash"].append(f"Evidence hash mismatch: {item['evidence_id']}")
        for target in item["counter_to"]:
            if target not in evidence:
                errors["reference"].append(f"unknown counter target: {target}")

    status_lists = {"accepted_evidence_ids": "ACCEPTED", "rejected_evidence_ids": "REJECTED", "counter_evidence_ids": "COUNTER", "unresolved_evidence_ids": "UNRESOLVED"}
    for item in objects["states"]:
        if item["subject_id"] not in subjects:
            errors["reference"].append(f"unknown State subject: {item['state_id']}")
        refs = [ref for field in status_lists for ref in item[field]]
        if item["state_code"] != "INSUFFICIENT_EVIDENCE" and not refs:
            errors["reference"].append(f"State has no evidence boundary: {item['state_id']}")
        for field, expected_status in status_lists.items():
            for ref in item[field]:
                if ref not in evidence:
                    errors["reference"].append(f"unknown State evidence: {ref}")
                elif evidence[ref]["review"]["status"] != expected_status:
                    errors["reference"].append(f"State evidence status mismatch: {item['state_id']}:{ref}")
        for ref in item["branch_ids"]:
            if ref not in branches:
                errors["reference"].append(f"unknown State branch: {ref}")
        if item["change_event_id"] is not None and item["change_event_id"] not in changes:
            errors["reference"].append(f"unknown State change: {item['change_event_id']}")

    chain = verify_state_chain(objects["states"])
    errors["chain"].extend([f"{row['state_id']}:{row['reason']}" for row in chain["broken_links"]])
    errors["chain"].extend([f"{row['state_id']}:{row['field']}" for row in chain["hash_mismatches"]])

    for item in objects["changes"]:
        previous, new = states.get(item["previous_state_id"]), states.get(item["new_state_id"])
        if previous is None or new is None:
            errors["reference"].append(f"Change State missing: {item['change_id']}")
        else:
            if item["previous_state_hash"] != previous["state_hash"] or item["new_state_hash"] != new["state_hash"]:
                errors["reference"].append(f"Change hash linkage mismatch: {item['change_id']}")
            if new.get("change_event_id") != item["change_id"] or new.get("previous_state_id") != previous["state_id"]:
                errors["reference"].append(f"Change reverse linkage mismatch: {item['change_id']}")
        if item["change_hash"] != change_hash(item):
            errors["hash"].append(f"Change hash mismatch: {item['change_id']}")

    for item in objects["branches"]:
        if item["state_id"] not in states or item["subject_id"] not in subjects:
            errors["reference"].append(f"Branch owner missing: {item['branch_id']}")
        for ref in item["supporting_evidence_ids"] + item["contradicting_evidence_ids"] + item["realization_evidence_ids"]:
            if ref not in evidence:
                errors["reference"].append(f"unknown Branch evidence: {ref}")

    for item in objects["requests"]:
        if item["visibility"] != "CUSTOMER_PRIVATE":
            errors["privacy"].append(f"Request is not private: {item['request_id']}")
        if item["linked_subject_id"] is not None and item["linked_subject_id"] not in subjects:
            errors["reference"].append(f"Request Subject missing: {item['request_id']}")
        if item["linked_state_id"] is not None and item["linked_state_id"] not in states:
            errors["reference"].append(f"Request State missing: {item['request_id']}")
    for item in objects["challenges"]:
        if item["subject_id"] not in subjects or item["state_id"] not in states:
            errors["reference"].append(f"Challenge owner missing: {item['challenge_id']}")
        for ref in item["resulting_evidence_ids"]:
            if ref not in evidence:
                errors["reference"].append(f"Challenge Evidence missing: {item['challenge_id']}:{ref}")
        if item["resulting_state_id"] is not None and item["resulting_state_id"] not in states:
            errors["reference"].append(f"Challenge resulting State missing: {item['challenge_id']}")
    for item in objects["outcomes"]:
        if item["visibility"] == "PUBLIC" and not item["authorization_for_public_use"]:
            errors["privacy"].append(f"Outcome lacks public authorization: {item['outcome_id']}")
        if item["state_id_used"] not in states:
            errors["reference"].append(f"Outcome State missing: {item['outcome_id']}")
        if item["request_id"] not in {request["request_id"] for request in objects["requests"]}:
            errors["reference"].append(f"Outcome Request missing: {item['outcome_id']}")
        for ref in item["supporting_evidence_refs"]:
            if ref not in evidence:
                errors["reference"].append(f"Outcome Evidence missing: {item['outcome_id']}:{ref}")

    result = {
        "objects_checked": object_count,
        "schema_errors": len(errors["schema"]), "reference_errors": len(errors["reference"]),
        "hash_errors": len(errors["hash"]), "chain_errors": len(errors["chain"]), "privacy_errors": len(errors["privacy"]),
        "errors": errors,
    }
    result["result"] = "PASS" if sum(result[key] for key in ["schema_errors", "reference_errors", "hash_errors", "chain_errors", "privacy_errors"]) == 0 else "FAIL"
    return result


def public_projection(objects: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    projection = {kind: [] for kind in ["subjects", "evidence", "states", "changes", "branches", "outcomes"]}
    for kind in projection:
        for item in objects.get(kind, []):
            if item.get("visibility") != "PUBLIC":
                continue
            if kind == "outcomes" and not item.get("authorization_for_public_use"):
                continue
            projection[kind].append(copy.deepcopy(item))
    return projection

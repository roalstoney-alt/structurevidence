#!/usr/bin/env python3
"""Validate minimal temporal-state-chain alignment and immutability."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY_SHA = "58c7c4fe9fa334e030080cf7ab352c222b326ec2"
PROTOCOL = "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1"
PRINCIPLES = {
    "TIME_BOUNDED_STATE",
    "PROTOCOL_BOUNDED_STATE",
    "APPEND_DONT_ERASE",
    "CHANGE_IS_DATA",
    "EVIDENCE_STATE_NE_DECISION",
    "AGENT_READS_ACTOR_DECIDES",
}
PARITY = [
    ".well-known/structurevidence.json",
    "method-contract.json",
    "agent/index.html",
    "changes.json",
    "changes/index.html",
    "index.html",
    "en/index.html",
    "zh-cn/index.html",
    "es/index.html",
]
IMMUTABLE = ["claims", "docs/claims", "cases", "docs/cases", "technical-risk/cml-v1.1", "rdl"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> None:
    contract = load("method-contract.json")
    ids = {row["id"] for row in contract["principles"]}
    require(PRINCIPLES <= ids, "one or more frozen temporal principles are missing")
    require(contract["question_protocol"]["version"] == PROTOCOL, "protocol version changed or missing")
    require(contract["state_identity"]["required_dimensions"] == ["claim_id", "as_of", "protocol_version", "snapshot_commit"], "state identity is incomplete")
    ownership = contract["decision_ownership"]
    require(ownership["evidence_state_determines_decision"] is False, "evidence state was made decision authority")
    require(ownership["agent_may"] == ["RETRIEVE", "COMPARE", "EXPLAIN", "TRACE"], "agent role changed")
    require(ownership["final_decision_authority"] == "RESPONSIBLE_ACTOR", "decision authority is not the responsible actor")

    discovery = load(".well-known/structurevidence.json")
    require(discovery["temporal_state"] == {"requires_as_of": True, "requires_protocol_version": True, "historical_states_preserved": True, "change_is_data": True}, "temporal discovery metadata mismatch")
    require(discovery["decision_boundary"]["final_decision_authority"] == "RESPONSIBLE_ACTOR", "discovery decision boundary mismatch")

    changes = load("changes.json")
    require(changes["changes"] == [], "fake state transition was introduced")
    change_contract = contract["change_object_contract"]
    require(change_contract["history_policy"] == "APPEND_DONT_ERASE", "append-only history policy missing")
    require(set(change_contract["required_fields_when_transition_exists"]) == {"claim_id", "from_state", "to_state", "from_as_of", "to_as_of", "protocol_version", "transition_evidence", "published_at", "snapshot_commit", "supersedes"}, "future transition object is incomplete")

    agent = (ROOT / "agent/index.html").read_text(encoding="utf-8")
    for label in ["Claim:", "State:", "As of:", "Protocol:", "Snapshot:", "Canonical:"]:
        require(label in agent, f"agent citation label missing: {label}")
    require("The responsible actor decides." in agent, "agent decision boundary missing")

    for relative in PARITY:
        require((ROOT / relative).read_bytes() == (ROOT / "docs" / relative).read_bytes(), f"root/docs parity failed: {relative}")

    unchanged = subprocess.run(["git", "diff", "--name-only", ENTRY_SHA, "--", *IMMUTABLE], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    require(not unchanged, f"claim or public case semantics changed: {unchanged}")
    matching = subprocess.run(["git", "diff", "--name-only", ENTRY_SHA, "--", "deploy/cloudflare-evidence-resolver/question-protocol.js"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    require(not matching, "matching semantics changed")
    commercial = subprocess.run(["git", "diff", "--name-only", ENTRY_SHA, "--", "deploy/cloudflare-landing", "commercial", "pricing"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    require(not commercial, "commercial policy changed")
    print("TEMPORAL_STATE_CHAIN_V01_TESTS_PASS")


if __name__ == "__main__":
    main()

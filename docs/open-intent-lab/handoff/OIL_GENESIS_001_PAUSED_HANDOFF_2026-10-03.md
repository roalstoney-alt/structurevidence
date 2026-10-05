# OIL-GENESIS-001 — Paused State Freeze and Handoff

## Freeze identity

```ini
PROJECT = StructEvidence Open Intent Lab
EXPERIMENT = OIL-GENESIS-001
FROZEN_AT = 2026-10-03T12:38:53Z
CURRENT_STATUS = PAUSED
LAST_COMPLETED_NODE = STAGE_3_HUMAN_SEND_DECISION
NEXT_ACTION = UNSET — awaiting human redesign of supplier participation approach
```

This package is the authoritative pause-state handoff. It records state; it does not send outreach, create production records, advance a stage, or commit repository changes.

## Repository boundary

```ini
AUTHORITATIVE_REPO_PATH = /Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001
CURRENT_BRANCH = codex/oil-genesis-001
LOCAL_HEAD_SHA = f81fcbcbcab4891d0043eee8617f0a7b7f632ad2
ORIGIN_MAIN_SHA = f81fcbcbcab4891d0043eee8617f0a7b7f632ad2
TRACKED_DIFF_FILES = 0
EXPERIMENT_ARTIFACTS_UNTRACKED = YES
UNTRACKED_PATHS_BEFORE_HANDOFF = 70
EXPECTED_UNTRACKED_PATHS_AFTER_HANDOFF = 74
COMMITTED = NO
```

The freeze is documentation plus machine-readable state, not a Git commit. All OIL artifacts remain untracked relative to the frozen base commit, so a receiving workspace must copy or otherwise preserve the complete worktree content—not merely check out the branch name.

The separate original repository at `/Users/roal/Documents/ChatGPT/structevidence` was not used as the write target. Its guard fingerprints are recorded in the manifest and verified again after package installation.

## Control-state interpretation

`PAUSED` is fail-closed. The four prior `YES` decisions remain historical human approvals for possible outreach, but they are not live sending permission while paused. The tracker therefore has top-level `send_authorized = false`, an empty `send_authorized_candidate_ids` list, and `send_authorized = false` on every candidate.

No automatic resume is allowed. The blocked transmission preflight records remain historical facts and are not transmissions. `STAGE_3_FINAL_OUTREACH_EXECUTION` is not treated as a completed node because no recipient-facing attempt occurred and the human-specified last completed node is `STAGE_3_HUMAN_SEND_DECISION`.

## Supplier decisions

| Candidate | Supplier | Historical decision | Current send authorization | Frozen disposition |
|---|---|---:|---:|---|
| OIL-CAND-001 | Venair | YES | NO | Approved for possible outreach; paused |
| OIL-CAND-002 | Saint-Gobain | YES | NO | Approved for possible outreach; paused |
| OIL-CAND-003 | AdvantaPure / NewAge | YES | NO | Approved for possible outreach; paused |
| OIL-CAND-004 | BioPure / Watson-Marlow | YES | NO | Approved for possible outreach; paused |
| OIL-CAND-005 | Trelleborg | HOLD | NO | HOLD remains in force |

## Reality boundary

```ini
MESSAGES_ACTUALLY_SENT = 0
ATTEMPTED_TRANSMISSIONS = 0
SUCCESSFUL_TRANSMISSIONS = 0
BLOCKED_PREFLIGHT_RECORDS = 4
FAILED_TRANSMISSIONS = 0
FIRST_REALITY_BOUNDARY_T0 = null
RESPONSE_WINDOWS_STARTED = 0
```

No `OUTREACH_SENT` event exists. No confirmation reference exists. No response clock has started. The four `OUTREACH_EXECUTION_BLOCKED` events describe environment preflight outcomes only.

## Production-record boundary

```ini
PROVIDER_CREATED = 0
EVIDENCE_INGESTED = 0
VCF_CREATED = 0
DEMAND_CREATED = 0
OUTCOME_CREATED = 0
REUSE_RECORD_CREATED = 0
```

## Frozen prepared messages

| Candidate | SHA-256 |
|---|---|
| OIL-CAND-001 | `076d1f2562375daa56207f75ad4cdc49f5629874599891a3ec19aae40f577ce0` |
| OIL-CAND-002 | `38ba8c8f865beb66b04d73fbc68bae8573bd2e33c1d3b033335b7995c7e34aa3` |
| OIL-CAND-003 | `1534617204764075f1afeb65ff09c0be913da29ce98314fef2480e928cacadeb` |
| OIL-CAND-004 | `f018d7c49abdae04f3b367856e8d6ab2c2f61549713a5b8f5ef8f9dc4d78ccd8` |

These hashes identify the prior prepared bodies. They do not authorize sending. If redesign changes the recipient, route, claim scope, or wording, renewed human review and authorization are required.

## Handoff package

- `docs/open-intent-lab/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.md` — human-readable state and recovery guide.
- `data/open-intent-lab/genesis-001/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.json` — machine-readable authoritative manifest.
- `data/open-intent-lab/genesis-001/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.sha256` — integrity inventory; the checksum file does not self-hash.
- `scripts/test_oil_genesis_paused_handoff.py` — freeze invariant tests.
- `data/open-intent-lab/genesis-001/outreach/outreach-tracker.json` — live fail-closed tracker.
- `data/open-intent-lab/genesis-001/outreach/outreach-events.jsonl` — append-only event history ending in `EXPERIMENT_PAUSED`.

## Resume gates

1. A new explicit human decision must define the redesigned supplier participation approach.
2. Pause removal and send authorization must be explicit; neither may be inferred from historical `YES` decisions.
3. Any changed recipient, channel, claim scope, or message body requires renewed human review and authorization.
4. A truthful principal-controlled sender identity and authorized outbound transport must exist before transmission.
5. OIL-CAND-005 remains `HOLD` until attribution is resolved and a separate human decision is recorded.
6. Stage 4 cannot start until a real sent event establishes `T0` and a response window.

## Unresolved decisions

- Supplier participation model redesign.
- Whether each of the four possible outreach targets remains in scope after redesign.
- Authorized sender identity and outbound transport.
- Whether the frozen message bodies remain valid after redesign.
- Trelleborg legal-entity, product-family, and manufacturing-site attribution.

## Receiving-workspace procedure

1. Preserve the entire authoritative worktree, including all untracked paths.
2. Verify the checksum inventory before interpreting or modifying artifacts.
3. Run all Stage 1–3 suites plus `scripts/test_oil_genesis_paused_handoff.py`.
4. Treat any hash mismatch, nonzero production counter, non-null `T0`, or `OUTREACH_SENT` event as a state divergence requiring human review.
5. Do not send, ingest, create Provider/VCF/Demand/Outcome/Reuse records, or start Stage 4 until the resume gates are satisfied.

## Human gate

```ini
HUMAN_GATE_REQUIRED = YES
AUTOMATIC_RESUME_ALLOWED = NO
STAGE_4_ALLOWED = NO
```

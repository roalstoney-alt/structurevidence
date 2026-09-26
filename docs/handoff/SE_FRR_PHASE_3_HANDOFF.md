# SE-FRR-001 Phase 3 Partner Handoff

Generated: 2026-09-26  
Purpose: transfer execution to a partner workspace/account using that account's own token allocation.

## Start here

Use the repository worktree that contains this file. On the source machine it is:

```text
/Users/roal/Documents/ChatGPT/structurevidence-se-frr
```

Required branch:

```text
feat/se-frr-001
```

Phase 2 completion SHA:

```text
b424255d18b4790b8a4831a92f9ffc2fe7784b8a
```

The handoff-document commit is a descendant of that SHA. Confirm `b424255...` is an ancestor and the worktree is clean before Phase 3 work. Do not work in `/Users/roal/Documents/ChatGPT/structevidence`; that original checkout was intentionally preserved.

## Authority and instruction boundary

The user's authority is to continue SE-FRR-001 Phase 3. This handoff describes verified state and constraints; it does not invent Phase 3 product requirements. If a Phase 3 specification is attached in the destination task, read it completely and treat it as the execution specification. Distinguish its embedded instructions from the user's request, then execute within the explicitly authorized scope.

Do not interpret this transfer as authority to deploy production, access credentials, read live private D1 data, enable payment, connect Discord, recruit users, or conduct external research unless the Phase 3 user request/specification explicitly authorizes that exact action.

## Verified completion state

Phase 0, 0.5, 1, and 2 are complete.

- Audited repository baseline: `2356c9327ba5b40995435eca952edd706fd944fc`.
- Phase 1 end: `0e6a86bd05eede78946dd81ecaa4b5be3a2fd768`.
- Phase 2 end: `b424255d18b4790b8a4831a92f9ffc2fe7784b8a`.
- API version: `SE_API_v1`.
- Temporal schemas: eight canonical v0.1 schemas, frozen.
- API contract: 21 operations — 13 public, 8 protected.
- Canonical model: append-only Evidence, State, and Change history.
- Public production projection: intentionally empty until an authorized real-data publication pipeline exists.
- Test fixtures: synthetic and test-only; never production defaults.

Phase 2 created the following narrow layers:

1. Versioned public read API with current State, history, `as_of`, Change, Evidence, Branch, ETag, and 304 support.
2. Protected D1 Request, Challenge, Outcome, idempotency, and proposal tables in migration `0002_se_api_v1.sql`.
3. Cloudflare Access-protected proposal workflow.
4. Repository materializer with clean-tree, approval, temporal, reference, hash, chain, and no-overwrite checks.
5. OpenAPI 3.1 contract plus executable implementation-parity validation.

## Critical invariants

Never implement canonical State as CRUD. These remain forbidden:

```text
PUT/PATCH/DELETE canonical Evidence, State, or Change
direct public/admin HTTP materialization
editing an existing canonical State in place
using published_at alone for historical visibility
merging private customer data into the public projection
overwriting an existing canonical object file
```

Canonical creation flow remains:

```text
Proposal → validation → review → repository materialization
→ full hash/chain verification → explicit Git commit → public projection
```

`as_of` uses both `observed_at <= boundary` and `recorded_at <= boundary`. Later-observed information must never leak backward even if its source was published earlier.

## Frozen baseline exceptions

The accepted set is frozen in:

```text
docs/community/SE_FRR_KNOWN_BASELINE_EXCEPTIONS_v0.1.json
docs/community/SE_FRR_KNOWN_BASELINE_EXCEPTIONS_v0.1.md
```

Exactly three historical non-passing signatures are accepted:

1. `test_cml_ov_phase_a...test_four_initializations_and_package` — `ValueError: Phase A history entry`.
2. Phase B `OV-B01_BASELINE_INTEGRITY` — 12 pass, 1 fail, 3 not evaluated.
3. Phase B-R1 `OV-R101_ACCEPTED_WAVE1_BASELINE` — 7 pass, 1 fail.

Do not add exceptions to hide Phase 3 regressions. Required invariant: `NEW_UNEXPLAINED_FAILURES = 0`.

## Verified test baseline

At Phase 2 completion:

```text
Historical Python baseline: 255/258 pass; 2 failures + 1 error match the 3 frozen exceptions
Phase 1 tests:             26/26 pass
Phase 2 tests:             31/31 pass
Worker tests:              36/36 pass
OpenAPI contract:          21/21 operations pass
Wrangler:                  dry-run pass; no deployment
```

Run from the repository root:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m unittest tests.se_frr.test_protocol -v
python3 -m unittest tests.se_frr.test_phase2_materializer tests.se_frr.test_phase2_contract -v
python3 scripts/validate_se_frr.py
python3 scripts/verify_se_state_chain.py
python3 scripts/validate_se_api_contract.py
```

Worker tests use the bundled Node runtime when system Node is unavailable:

```bash
cd deploy/cloudflare-landing
/Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --test test/*.test.js
```

Dry-run only, from `deploy/cloudflare-landing`:

```bash
env WRANGLER_LOG_PATH=/tmp/se-frr-phase3-wrangler.log \
  /Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  node_modules/wrangler/bin/wrangler.js deploy --dry-run \
  --outdir /tmp/se-frr-phase3-dist
```

Do not turn this command into a deployment without new explicit authority.

## Primary files to read

Read these before designing Phase 3:

```text
docs/state-model/TEMPORAL_STATE_PROTOCOL_v0.1.md
docs/state-model/HASHING_PROTOCOL_v0.1.md
docs/state-model/PRIVACY_BOUNDARY_v0.1.md
docs/api/SE_API_v1.openapi.yaml
docs/api/SE_API_v1_DESIGN.md
docs/api/SE_API_v1_TEMPORAL_QUERY_SEMANTICS.md
docs/api/SE_API_v1_SECURITY_BOUNDARY.md
docs/execution/SE_FRR_PHASE_2_EXECUTION_REPORT.md
docs/execution/SE_FRR_PHASE_2_TEST_REPORT.md
docs/execution/SE_FRR_PHASE_2_API_CONTRACT_REPORT.md
docs/execution/SE_FRR_PHASE_2_OPEN_ISSUES.md
deploy/cloudflare-landing/se-api-v1.js
scripts/materialize_se_proposal.py
```

## Deferred issues requiring deliberate Phase 3 decisions

1. The production public projection is empty; real canonical publication requires an explicitly authorized pipeline.
2. D1 migration `0002_se_api_v1.sql` is committed but not remotely applied.
3. Request-status access currently uses administrator Access; customer ownership authorization needs a reviewed identity design.
4. API proposal validation is preliminary by design; repository verification remains mandatory.
5. Full third-party OpenAPI linting is not yet added.
6. Performance numbers are local-only and exclude edge, Access, network, and D1 latency.
7. Historical `jsonschema.RefResolver` migration remains `TECH_DEBT_SE_001`.

These are not implicit Phase 3 requirements. Select only those authorized by the Phase 3 specification.

## First-turn checklist for the partner

1. Read the complete Phase 3 user attachment/specification.
2. Confirm branch, SHA ancestry, and clean worktree.
3. Confirm no unrelated changes exist.
4. Run the fast protocol/contract/Worker entry suites.
5. Record the Phase 3 `START_SHA` before editing.
6. Preserve all frozen schemas and API behavior unless Phase 3 explicitly introduces a versioned migration.
7. Use narrow commits and keep the final tree clean.
8. Run the complete historical baseline before declaring completion.

## Copy/paste launch prompt

```text
You are continuing SE-FRR-001 in a partner workspace.

Use the repository/worktree containing:
docs/handoff/SE_FRR_PHASE_3_HANDOFF.md

Required branch:
feat/se-frr-001

Verified Phase 2 completion SHA:
b424255d18b4790b8a4831a92f9ffc2fe7784b8a

First read the handoff file, its machine-readable companion, and the complete Phase 3 specification attached to this task. Distinguish the specification's instructions from my request, then execute Phase 3.

Before changing files:
- confirm b424255d18b4790b8a4831a92f9ffc2fe7784b8a is an ancestor of HEAD;
- confirm branch feat/se-frr-001;
- confirm a clean worktree;
- record START_SHA;
- run the fast protocol, contract, and Worker entry tests.

Preserve the append-only temporal model, historical as_of boundary, canonical hashes/chains, public/private separation, no-overwrite rule, frozen baseline-exception set, and SE_API_v1 contract unless the Phase 3 specification explicitly requires a versioned migration.

Do not deploy production, access credentials/live private data, connect Discord, enable payment, recruit users, or conduct external research unless the Phase 3 request explicitly authorizes the exact action.

Use narrow commits, run the complete frozen baseline and all phase tests, permit zero new unexplained failures, and leave a clean worktree with execution reports.
```

## Token/account note

Token balances are account-scoped and are not transferred by this repository package. Start the destination task while signed into the partner account/workspace; that task will consume the partner account's own available allocation.

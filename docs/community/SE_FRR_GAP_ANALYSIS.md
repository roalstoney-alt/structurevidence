# SE-FRR-001 Gap Analysis

Audit date: 2026-09-25  
Baseline SHA: `2356c9327ba5b40995435eca952edd706fd944fc`

## Summary

The repository already implements many of the hard primitives behind the FRR thesis, but it does not yet expose them as the requested community product. Phase 0 identifies 14 critical gaps.

## Critical gaps

| # | Gap | Current state | Required Phase |
|---:|---|---|---|
| 1 | Clean, passing baseline | Worktree is dirty; Python suite has 14 failures and 2 errors. | Before Phase 1 |
| 2 | Unified Subject object | Subject identifiers exist across domains, but no FRR Subject schema/index with visibility and lifecycle fields exists. | Phase 1 |
| 3 | Unified Evidence object | Evidence Core and domain evidence exist, but not the FRR acceptance/rejection/reason/snapshot schema as one API object. | Phase 1 |
| 4 | Append-only FRR State object | CML, Timeline and Monitoring encode states, but no FRR controlled-vocabulary State record with explicit previous-state and branch links exists. | Phase 1 |
| 5 | FRR ChangeEvent object/engine | Monitoring transitions are reusable, but there is no review-required change detector or FRR ChangeEvent lifecycle. | Phases 1–2 |
| 6 | Branch and Challenge objects | Alternative-path concepts exist; structured branches, kill conditions, challenge review and public reasons do not. | Phases 1–2 |
| 7 | Outcome object | RDL has outcome refs and real-world-response concepts, but no request-linked outcome workflow that is independently append-only. | Phases 1–2 |
| 8 | FRR API | Only request intake/admin request APIs exist. State/history/change/evidence/challenge/outcome endpoints are missing. | Phase 2 |
| 9 | Public/community routes | `/community`, `/states`, `/states/{subject}`, `/changes`, `/founding` are absent. Existing `/request` behavior must be mapped. | Phase 3 |
| 10 | Visibility/entitlement model | Public/private boundaries exist, but Public/Founding Member/Research Request entitlements and subscription checks do not. | Phases 1–3 |
| 11 | Discord server and bot | No bot app, commands, permission matrix, or integration tests exist. | Phases 4–5 |
| 12 | Configurable paid flow | Commercial schemas and manual/quote-gated payment material exist, but no configurable subscription/case-payment implementation exists. | Phase 9 |
| 13 | FRR analytics | Research telemetry exists, but the specified funnel and action/outcome metrics are not operational. | Phases 3 and 9 |
| 14 | Seed package/content | Reusable cases and records exist, but 10 normalized subjects, 10 State Cards, 5 Change Cards and 3 FRR public cases have not been produced. | Phases 6–7 |

## Schema mapping observations

### Strong direct reuse

- `Evidence Core` already carries `record_id`, `subject_id`, source and artifact references, `effective_at`, `known_at`, correction/supersession status, policy version, input hash and record hash.
- CML PDRE records already carry current dependency, structural constraints, alternative path, migration readiness, accepted/known evidence, counter-evidence, unknowns, next observables and revision history.
- RDL records already distinguish checked, used, rejected, counter and duplicate evidence, plus before/after states and unknown resolution.
- Monitoring already separates effective time from knowledge time and preserves prior/current transitions.
- D1 request events already enforce append-only behavior with database triggers.

### Adapter required

- Existing domain vocabularies must not be overwritten by the pilot’s eight-state vocabulary. FRR State should reference source-domain records and preserve source method/version.
- Existing `requests` statuses differ from the proposed FRR vocabulary. A reviewed migration or translation table is required; silently changing existing rows or constraints would violate history.
- Existing technical and digital-asset subjects use different domain payloads. FRR Subject should normalize identity while retaining domain-specific records.
- Rejected evidence exists in RDL research trails, but a public-safe rejection reason and visibility policy must be modeled explicitly.

## Test gaps to add in Phase 1

At minimum, new tests must prove:

- a State record cannot be updated or deleted through supported storage/API paths;
- a successor State preserves and links its predecessor;
- a ChangeEvent atomically references both immutable states;
- rejected and counter evidence persist with review reasons;
- challenge submission cannot directly mutate a canonical State;
- outcome submission cannot rewrite the State used for the decision;
- private requests, evidence and outcomes cannot cross into public read models;
- all state-producing actions require explicit timestamps and method/schema versions.

## Human decision required before Phase 1

The human owner must choose how the pre-existing dirty worktree should be preserved (for example, complete and commit it, or move it to an explicitly named worktree/branch) and then authorize baseline-regression triage. This audit did not stash, revert, commit, or otherwise alter those changes.

## Phase 1 readiness

`NEXT_PHASE_READY = NO`

Reasons:

1. `REPOSITORY_CLEAN = NO`.
2. The required baseline suite is not green.
3. The existing request schema and FRR request vocabulary require a migration decision before implementation.

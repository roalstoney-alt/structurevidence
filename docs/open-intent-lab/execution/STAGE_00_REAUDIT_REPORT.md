# Stage 00 Re-audit Report

## Control

```text
PROJECT = StructEvidence Open Intent Lab
ACTION = ESTABLISH_CLEAN_AUTHORITATIVE_BASELINE_AND_RESUME_STAGE_0
FROZEN_BASELINE = OIL-DPE v0.4 — FROZEN
AUTHORITATIVE_BASELINE_SOURCE = origin/main
AUTHORITATIVE_BASELINE_SHA = f81fcbcbcab4891d0043eee8617f0a7b7f632ad2
OIL_WORKTREE = /Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001
OIL_BRANCH = codex/oil-genesis-001
AUDIT_DATE = 2026-10-03 (Asia/Shanghai)
```

## Baseline establishment

- Previous `origin/main`: `f81fcbcbcab4891d0043eee8617f0a7b7f632ad2`.
- `git fetch origin`: successful.
- Fetched `origin/main`: unchanged at `f81fcbcbcab4891d0043eee8617f0a7b7f632ad2`.
- `6ec268b` and `8d4b028` are ancestors of the fetched baseline.
- The original worktree remained on `main` at `526882092bef2bf7a470d995d330f2e61b733de9`.
- Its two modified tracked paths, nine untracked top-level paths, status hash, tracked-diff hash and untracked-content manifest hash matched the repository freeze exactly.
- New branch `codex/oil-genesis-001` was created from `origin/main` in the requested sibling worktree.
- The new worktree had empty `git status --short` before Stage 0 outputs were created.

Roles are now:

```text
/Users/roal/Documents/ChatGPT/structevidence
  = PRESERVED_LEGACY_DIRTY_WORKTREE

/Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001
  = OIL_CANONICAL_IMPLEMENTATION_WORKTREE
```

The local `/admin` redirect and tests remain `LOCAL_PATCH_CANDIDATE_ADMIN_REDIRECT`. They were not copied, replayed, reviewed, or tested for OIL. All nine legacy untracked paths remain `PRESERVED_NON_CANONICAL_WORK` and were not moved or copied.

## Architecture re-audit

| Area | Authoritative finding |
|---|---|
| Claim | 26 public claim objects across 3 cases, with deterministic registry/projection, state, `as_of`, supports, limits, unknowns, provenance and canonical routes. |
| Evidence | Public Evidence schema plus Evidence Core fields for identity, source/artifact refs, effective/known time, verification, correction, supersession, policy and hashes. |
| Source | Attributed within evidence and Decision Memory source artifacts; roles distinguish primary, corroborating, independent and secondary sources. |
| Provenance | Embedded claim roles, Evidence Core refs/hashes, search provenance and Decision Memory data provenance. |
| Stop Point | Stable human citation pages and resolver stop-point objects with temporal/protocol/snapshot identity. |
| Counter-Evidence | Public case counter-evidence arrays and structured limitations; not to be omitted from OIL projections. |
| Search Run | Case search provenance, Case Watch search runs, and domain search manifests preserve scope and stop boundaries. |
| Decision Record | Decision Memory plus GDR/publication controls preserve decision state separately from evidence state. |
| Public Case | Versioned static case records generated to root/docs, with schemas, atomic evidence routes, history and public changes. |
| Database | D1 private commercial plane: `customers`, `requests`, append-only `request_events`. Public evidence remains file/snapshot based. |
| Event History | D1 triggers prevent request-event update/delete; public state histories, changes and Decision Memory revisions/transitions are additive. |
| Access Model | Public read-only evidence/resolver, rate-limited public intake, Access-protected admin, fail-closed publication eligibility. Buyer/transaction scoping is absent. |
| Tests | Strong model, resolver, projection, case-watch, D1 and publication tests; several historical guard tests have stale hard-coded baselines. |

## OIL mapping result

```text
Provider = NEW_THIN_OBJECT
VerifiedCapabilityFact = EXTEND_EXISTING
Demand = EXTEND_EXISTING
ReuseRecord = NEW_THIN_OBJECT
Outcome = NEW_THIN_OBJECT
```

Verified Capability Fact is a typed provider-to-canonical-claim projection. It reuses canonical Evidence, Provenance, Counter-Evidence, Stop Point, state normalization and temporal identity. It is not a second evidence truth store.

The remote agent/protocol lineage `70bf7f9..82b335d` is directly reusable: machine discovery, deterministic claim resolution, question intake, claim matching, minimum missing evidence, verification quoting, human authorization, publication eligibility, normalized state, freshness/applicability and responsible-actor decision ownership already exist.

## Proposed database delta

No migration was run. The minimum proposed additive model is:

- `oil_providers`;
- `oil_provider_claim_links` (relationship-only VCF anchor);
- `oil_demands` with optional existing `request_id` linkage;
- `oil_reuse_records`;
- `oil_outcomes`;
- append-only `oil_events` and no-update/no-delete controls.

No evidence, claim state, source artifact or provenance payload belongs in the OIL tables.

## Access model

```text
L0_MAPPING = Existing publication-approved public claims/cases/evidence/stop-points and read-only resolver, after publication eligibility and human publication review.

L1_MAPPING = No exact buyer reader. Use fail-closed CUSTOMER_PRIVATE storage and internal Access administration until buyer-principal entitlements exist; admin Access is not buyer authorization.

L2_MAPPING = No transaction-scoped reader. Keep private until transaction identity, membership, purpose, expiry and object-level authorization exist.

ACCESS_GAPS = Buyer identity/entitlements; transaction scope/expiry; object and transitive-link enforcement; grant/revoke audit; publication-to-visibility mapping; distinct names for research depth versus access visibility.
```

## Regression review

### Passing checks

| Check | Result |
|---|---|
| New OIL worktree baseline status | PASS — clean before Stage 0 outputs |
| Remote Case Watch lineage | PASS — `6ec268b` and `8d4b028` are ancestors of baseline |
| Decision Memory validation | PASS |
| Public case primitives | PASS — 9/9 |
| Case Watch validation | PASS — 9 groups |
| Public record export in isolated writable audit copy | PASS — 3/3 |
| Brand and SEO checks | PASS — 10/10 |
| Evidence resolver Node suite | PASS — 27/27 |
| Cloudflare landing/intake/D1 suite in isolated locked-dependency copy | PASS — 15/15 |
| Agent discovery functional assertions excluding historical immutable-range guard | PASS — 17/18 |
| Question/protocol functional assertions excluding historical immutable-range guard | PASS — 6/7 |
| API routing functional assertions excluding historical immutable-range guard | PASS — 8/9 |

### Existing baseline regression debt

These failures existed at the fetched authoritative baseline and were not caused or changed by OIL:

1. `test_agent_discovery.py`, `test_question_evidence_commerce_protocol.py`, `test_minimal_method_hardening_v01.py`, and `test_agent_api_subdomain_routing.py` compare protected paths to historical entry SHAs. Later authorized public-case, gravity and brand commits changed those paths, so the guards now flag the legitimate current tree.
2. `test_temporal_state_chain_v01.py` expects `changes.json` to be empty, while the current baseline contains an authorized material-change entry.
3. `test_customer_intake_phase_b.py` expects legacy commercial CTAs on every former public surface; the global-market gateway intentionally no longer contains that exact CTA.
4. Direct in-worktree public export initially hit sandbox write denial; the same test passed 3/3 in an isolated writable archive of `origin/main`.
5. Landing tests required `jose`; locked dependencies were installed only in an isolated temporary audit copy. The OIL worktree was not populated with `node_modules`.

These are test-baseline maintenance gaps, not evidence that OIL requires history rewrites or duplicate truth storage. Stage 1 should not silently update the guards; their authoritative comparison point and intended invariant require explicit review.

## Additional OIL-specific tests required

- provider identity/version and L0 privacy;
- provider/claim/snapshot referential integrity;
- VCF projection equality with canonical Claim/Stop Point and no duplicated truth;
- demand type, authority, permission and request-link rules;
- pre-demand reuse temporal ordering;
- append-only ReuseRecord, Outcome and event enforcement;
- outcome writeback creates new review/version references only;
- L0/L1/L2 fail-closed and transitive no-leak tests;
- buyer/transaction grant, revoke and expiry audit tests;
- migration non-regression for existing D1 and public records.

## Result

```text
BASELINE_COMPATIBILITY = PASS
PUBLIC_RECORD_IMPACT = NONE
DATABASE_MIGRATIONS_RUN = NO
STAGE_1_IMPLEMENTATION_STARTED = NO
HUMAN_GATE_REQUIRED = YES
NEXT_ALLOWED_STAGE = STAGE_1_DOMAIN_FREEZE
```

Stage 0 is complete. Stage 1 remains prohibited until explicit human approval.

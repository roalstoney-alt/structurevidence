# OIL-DPE v0.4 Implementation Mapping

## Document control

| Field | Value |
|---|---|
| Project | StructEvidence Open Intent Lab |
| Experiment | OIL-GENESIS-001 |
| Stage | Stage 0 Re-audit |
| Frozen protocol | OIL-DPE v0.4 — FROZEN |
| Authoritative source | `origin/main` |
| Baseline SHA | `f81fcbcbcab4891d0043eee8617f0a7b7f632ad2` |
| Implementation worktree | `/Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001` |
| Branch | `codex/oil-genesis-001` |
| Audit date | 2026-10-03 (Asia/Shanghai) |
| Result | Compatible by additive extension; human Stage 1 gate required |

## Architectural decision

OIL must remain a supplemental domain inside StructEvidence. It must not create a parallel evidence system, rewrite public history, or convert commercial observations into evidence without the existing human review and publication controls.

The current production lineage already supplies the evidence truth layer:

- public Claim objects and a 26-claim registry;
- Evidence, Source attribution, Provenance, Counter-Evidence, Search Provenance, Stop Points, Public Cases, and state histories;
- Evidence Core identity, hashing, correction, supersession, event time, and knowledge time;
- Decision Memory with evidence states, decision state, transitions, outcomes references, revision history, and append-only semantics;
- normalized epistemic, verification-depth, applicability, freshness, and workflow axes;
- deterministic agent discovery and a read-only claim resolver;
- governed question intake, claim matching, minimum-missing-evidence, verification quote, publication eligibility, and human authorization boundaries;
- a private customer-request D1 database with append-only events and Cloudflare Access-protected administration.

OIL therefore adds commercial identity and relationship records around canonical evidence. Canonical claims and evidence remain the only factual authority.

## Existing architecture map

| Audit object | Authoritative implementation evidence | Stage 0 finding |
|---|---|---|
| Claim | `claims/*.json`, `claims/index.json`, `agent-discovery/claim-registry-v0.1.json`, `method-contract.json` | Reuse. Claim state, scope, `as_of`, supports, limits, unknowns, provenance, next observable, and canonical URL are already public and machine-readable. |
| Evidence | `schemas/evidence.schema.json`, `evidence/core/schema/evidence_core_record.schema.json`, `cases/*/evidence.json`, atomic `e/*/index.json` routes | Reuse. Do not introduce OIL evidence payloads or a second evidence truth store. |
| Source | Embedded source URL, publisher, dates, classification, and Decision Memory source-artifact role | Reuse as canonical source attribution. A standalone Source entity is not required for Stage 1. |
| Provenance | Claim `provenance[]`, Evidence Core `source_refs`/`artifact_refs`/hashes, case search provenance, Decision Memory `data_provenance` | Reuse. OIL relations reference these records rather than copying them. |
| Stop Point | `cases/*/stop-v0.1.html` and resolver `public_stop_point` response | Reuse. It already carries claim/state/support/limits/time/protocol/snapshot/freshness/unknowns. |
| Counter-Evidence | `cases/*/counter_evidence.json`, state and Decision Memory limitations | Reuse. Provider capability views must retain counter-evidence and limitations. |
| Search Run | `data/case-watch/search-runs/**`, `cases/*/search_provenance.json`, technical-risk search manifests | Reuse. OIL may reference a run; it must not imply non-existence from a failed search. |
| Decision Record | Decision Memory schema/records, GDR authorization records, publication controls | Reuse. OIL does not become decision authority. |
| Public Case | `schemas/case.schema.json`, generated `cases/*` and `docs/cases/*`, root/docs parity | Reuse. Existing cases are immutable inputs, not OIL migration targets. |
| Database | D1 `customers`, `requests`, `request_events` in `0001_customer_intake.sql` | Extend additively. Public evidence is file/snapshot based; D1 is the private commercial plane. |
| Event History | D1 append-only `request_events`; case `state_history`; `changes.json`; Decision Memory transitions/revisions | Reuse event laws. New OIL lifecycle facts require append-only events/records. |
| Access Model | Public static claims/cases and read-only resolver; public rate-limited intake; Access-protected admin; publication eligibility schema | Extend. No authorized-buyer or transaction-scoped reader exists yet. |
| Tests | Python model/projection/immutability tests; resolver Node tests; landing/D1 Node tests | Reuse, with known hard-coded-baseline drift recorded in the Stage 0 report. |

## OIL object classification

### Provider — `NEW_THIN_OBJECT`

No canonical provider identity exists. `customers` are request submitters; publishers/manufacturers in evidence and technical-risk records are contextual strings, not a stable provider entity.

Minimum boundary:

- stable `provider_id` and version;
- legal/trading names, country, official URI, status, effective/known/created times;
- public-safe identity fields only in public projections;
- private contact and transaction data kept outside the public object;
- aliases and related-party assertions represented as versioned relationships, not silent field rewrites.

### VerifiedCapabilityFact — `EXTEND_EXISTING`

`VerifiedCapabilityFact` is not a new evidence object. It is a typed, time-bounded relationship/projection:

```text
Provider
  -- HAS_CAPABILITY_AS_SUPPORTED_BY -->
canonical Claim
  -- supported/limited by -->
canonical Evidence + Provenance + Counter-Evidence + Stop Point
```

The relation may add only OIL metadata: `provider_id`, `claim_id`, relationship type, applicability, commercial capability label, visibility, `as_of`, protocol version, snapshot commit, and decision/publication references. State, support, limitations, unknowns, source facts, and hashes must be read from the canonical records.

VCF design result:

```text
VCF = projection / typed commercial capability relationship
VCF != second evidence truth store
```

### Demand — `EXTEND_EXISTING`

The D1 `requests` record already captures a human-originated decision/claim, technical object, dependency, alternative, deadline, customer principal, status, privacy class, owner, and research authorization. OIL should preserve that intake contract and add a one-to-one/optional demand extension rather than build a parallel intake system.

Required extension fields include demand type (`EXTERNAL_DEMAND` or `OPERATOR_DEMAND`), authority attestation, requirements, writeback permission, OIL visibility, and immutable creation time. Operator demand must remain analytically separate from external demand.

### ReuseRecord — `NEW_THIN_OBJECT`

No canonical record currently joins a pre-existing capability fact to a later demand and records whether existing evidence was accepted or whether more evidence was requested.

The record must reference, not copy:

- `demand_id`;
- provider-capability relationship / canonical `claim_id`;
- evidence snapshot/protocol identity;
- reuse disposition and bounded time-saved estimate;
- human actor and event time.

Pre-demand reuse requires the referenced fact/snapshot to predate the demand. The record is append-only.

### Outcome — `NEW_THIN_OBJECT`

Decision Memory already reserves `outcome_refs` and `OUTCOME_UPDATE`, but the repository has no canonical Outcome record schema. Add a thin append-only record for authorized commercial or physical observations. It may reference a demand, reuse record, decision memory, provider, and evidence inputs. It may trigger a new evidence review/fact version; it may never mutate the earlier fact or decision state.

## Reuse classification summary

```text
Provider = NEW_THIN_OBJECT
VerifiedCapabilityFact = EXTEND_EXISTING
Demand = EXTEND_EXISTING
ReuseRecord = NEW_THIN_OBJECT
Outcome = NEW_THIN_OBJECT
```

Existing objects reused directly:

```text
Claim
Evidence
Source attribution
Provenance
Stop Point
Counter-Evidence
Search Run
Decision Memory / Decision Record
Public Case
Publication Eligibility
Normalized State / Freshness / Applicability
Request Event History
```

## Agent/protocol work reused

The `70bf7f9` through `82b335d` lineage already provides the following OIL primitives:

| Existing primitive | OIL reuse |
|---|---|
| `.well-known/structurevidence.json` | Machine discovery and temporal/decision boundaries. |
| Public claim registry and deterministic resolver | Capability discovery starts from canonical claims, not a provider-written assertion. |
| `QUESTION_INTAKE_v0.1` | Demand question normalization and fail-safe decomposition. |
| `CLAIM_MATCH_CLASS_v0.1` | Exact/isomorphic/partial/none matching between demand and existing capability claims. |
| Public stop point | Bounded state returned with support, limitations, time, protocol, and snapshot. |
| Minimum missing evidence | Determines whether reuse is sufficient or a new verification cycle is required. |
| RDL candidate | Distinguishes L0 reuse from L1/L2 research depth; this is not an access level. |
| Verification quote and commercial handoff | Human-authorized path from unresolved demand to bounded verification. |
| Publication eligibility | Prevents customer-private or source-controlled material from becoming public automatically. |
| Normalized state and temporal identity | Supplies VCF state without introducing OIL-specific truth semantics. |
| Responsible-actor decision ownership | OIL may retrieve/match/trace but does not make the final decision. |

The resolver is intentionally read-only: no database binding, external search, LLM call, request creation, research authorization, email action, or state mutation. Preserve that boundary.

## Proposed database delta — no migration executed

The minimum future D1 delta is additive and namespaced. Exact SQL belongs to Stage 1 or later after domain freeze.

1. `oil_providers`: stable provider identity and lifecycle metadata; no raw evidence.
2. `oil_provider_claim_links`: relationship-only rows connecting a provider to canonical `claim_id`, protocol/snapshot identity, applicability and visibility. This is the VCF projection anchor, not a fact store.
3. `oil_demands`: OIL extension with optional `request_id` foreign key, demand type, authority attestation, requirements, writeback permission and visibility.
4. `oil_reuse_records`: immutable join of a demand to a pre-existing provider/claim relation and its snapshot, with reuse disposition and bounded time-saved estimate.
5. `oil_outcomes`: immutable, permissioned outcome observations with references to demand/reuse/decision/evidence review.
6. `oil_events`: append-only lifecycle events for the new objects, with update/delete prevention matching `request_events`.

Required database laws:

- foreign keys on all OIL references;
- no cascade that can erase audit history;
- update/delete prevention for reuse, outcome and event records;
- versions/events for provider or demand changes;
- fail-closed visibility constraint;
- no evidence body, claim state, provenance body, or source artifact duplicated into OIL tables;
- no migration of existing public cases or existing request rows.

## Access model mapping

OIL visibility levels and existing research-depth labels both use `L0/L1/L2`; they are different axes and must never be conflated.

```text
L0_MAPPING = Existing publication-approved public Claims, Cases, Stop Points, atomic Evidence routes, and read-only resolver. OIL L0 projection is allowed only after publication eligibility plus human publication review.

L1_MAPPING = No exact authorized-buyer reader exists. Store as CUSTOMER_PRIVATE/fail-closed in D1 and expose to internal Access-protected administration only until a buyer-principal entitlement layer is explicitly designed. Cloudflare admin Access is not buyer authorization.

L2_MAPPING = No transaction-scoped reader exists. Keep transaction material private and unavailable to public/general buyer projections until transaction identity, membership, purpose, expiry, and object-level authorization are implemented.

ACCESS_GAPS = Buyer identity and entitlement; transaction scope and expiry; per-object visibility enforcement; linked-object/transitive leak prevention; audit events for grants/revocations; exact mapping between publication eligibility and OIL visibility; naming separation between research depth and access visibility.
```

## Public record impact

Stage 0 changes documentation only. It adds no claim, evidence, provider, demand, reuse, outcome, database migration, route, resolver capability, UI, or deployment. Existing cases, claims, schemas, histories, snapshots, and public projections remain unchanged.

## Existing regression protection reused

- Claim count/ID uniqueness, source traceability, exact state preservation, `does_not_support`, and `as_of` checks.
- Public Case schema, deterministic public export, atomic evidence parent links, and root/docs parity.
- Decision Memory schema, transitions, temporal semantics, revisions, and outcome-reference structure.
- Case Watch schemas, protected baseline hashes, search provenance, and no-public-mutation gates.
- Resolver exact/isomorphic/partial/none behavior, closed inference boundary, no-match safety, stop-point temporal identity, medical boundary, and read-only HTTP behavior.
- Question-to-evidence protocol schema and human-authorization tests.
- D1 intake validation, rate limits, privacy defaults, Access gates, event append-only triggers, and admin audit events.
- Brand, SEO, discovery and publication-boundary checks.

## Additional OIL-specific tests required

Only OIL-specific additions are needed:

1. Provider identity/version/alias integrity and no private-contact fields in L0.
2. Provider-claim link referential integrity against canonical claim IDs and immutable snapshot identity.
3. VCF projection equality: state/support/limits/unknowns/provenance must equal canonical Claim/Stop Point; no copied truth fields may diverge.
4. Demand type separation, human authority attestation, writeback permission, and optional request linkage.
5. Reuse temporal law: referenced fact/snapshot predates demand for pre-demand reuse.
6. ReuseRecord, Outcome and OIL event append-only update/delete rejection.
7. Outcome writeback creates new review/evidence/fact references and cannot rewrite prior Claim/Decision Memory.
8. L0/L1/L2 fail-closed access and transitive projection tests across linked objects.
9. Buyer and transaction grant/revoke/expiry audit tests once those access mechanisms exist.
10. Migration tests that prove existing customers, requests, request events, claims, cases, and public exports are unchanged.

## Compatibility result and gate

```text
BASELINE_COMPATIBILITY = PASS
REUSED_OBJECTS = [Claim, Evidence, Source attribution, Provenance, Stop Point, Counter-Evidence, Search Run, Decision Record, Public Case, Publication Eligibility, State/Freshness/Applicability, Request Event History]
EXTENDED_OBJECTS = [VerifiedCapabilityFact via provider-claim projection, Demand via request-linked extension]
NEW_THIN_OBJECTS = [Provider, ReuseRecord, Outcome]
DATABASE_DELTA = PROPOSED_ONLY; NOT_EXECUTED
PUBLIC_RECORD_IMPACT = NONE
HUMAN_GATE_REQUIRED = YES
NEXT_ALLOWED_STAGE = STAGE_1_DOMAIN_FREEZE
```

Stage 1 may begin only after human approval. It must freeze identifiers, vocabularies, visibility semantics, and the relationship-only VCF contract before any migration, data creation, supplier search, Genesis claim, UI, or deployment.

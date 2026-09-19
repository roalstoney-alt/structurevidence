# Architecture Before the Evidence-to-Outcome Upgrade

## Current committed flow

```text
Public/private source material
        |
        v
Source inventories / registers / search logs
        |
        +--> claims / observations / counter-evidence / hypotheses
        |
        v
Canonical research and CML records
        |
        +--> Evidence Core identity, provenance, time, hashes
        +--> CML v1.1 PDRE/dependency/exposure/beneficiary objects
        |
        v
Timeline + monitoring state transitions
        |
        v
RDL freshness evaluation
        |
        v
GDR-SE authorization and release gates
        |
        +--> static public surfaces
        +--> bounded commercial artifacts
```

The absent connection is a normalized research-process layer:

```text
decision target -> minimum missing evidence -> research actions
-> cost -> before/after uncertainty -> decision change -> stop reason
-> reuse -> later outcome
```

## Component map

| Layer | Location | Implemented responsibility | Boundary/gap |
| --- | --- | --- | --- |
| Evidence Core | `evidence/core/` | Shared record metadata, provenance references, temporal fields, hashes, correction and supersession | Must remain the sole core envelope. |
| CML v1.1 | `technical-risk/cml-v1.1/` | Structural dependency, PDRE, readiness, friction, exposure, beneficiaries, response, validation, failure | Must not absorb research cost/governance or customer-private decision context. |
| Pilot case | `technical-risk/cml-v1.1/pdre/CML-PDRE-001/` | Current case/evidence/timeline/state/dependency-transfer data | Has evidence lineage but no research-round economics or decision-target record. |
| Research packages | `research/`, `evidence-freeze/`, `technical-risk/records/` | Domain-specific source, query, claim, observation, hypothesis, and manifest artifacts | Formats differ; cross-case search memory is manual. |
| Timeline | `timeline/` | Atomic observations, effective/known time, aggregation, derivation, comparability | Not a research-action ledger. |
| Monitoring | `monitoring/` | State transitions and view models | State transitions are generic enough to reference, not duplicate. |
| RDL freshness | `rdl/freshness/` | Time/event/evidence invalidation and release freshness | Evaluates freshness, not research usefulness, cost, duplication, or saturation. |
| GDR-SE | `gdr-se/` | Evidence envelope, runtime gates, authorization history | Holds `research_id` and release decisions, but not research before/after state. |
| RTP | frozen manifests and draft `whitepapers/RTP/` | Hash/reproducibility practices exist; protocol document is scaffold | Do not claim a complete standalone RTP runtime. |
| ECN | timeline/monitoring transitions and draft `whitepapers/ECN/` | Transition semantics exist; protocol document is scaffold | Do not create a parallel transition ledger in RDL. |
| Evidence graph | `commercial/schema/evidence_graph.schema.json` | Typed evidence/claim/hypothesis relationships | Can be extended through references; it does not include decisions/actions/outcomes. |
| Public frontend | static HTML/CSS/JS | Published evidence and monitoring surfaces | No evidence-to-outcome workspace UI. |
| Deployment | GitHub/static assets and `deploy/cloudflare-landing/` | Cloudflare Worker proxies a landing route to the public static origin | Not an application/database runtime. |

## Storage architecture

The repository is a Git-versioned, file-backed system. JSON objects hold canonical state, JSONL files preserve append-only history, manifests bind artifacts by hashes, Markdown provides audits/reports, and Python scripts validate or derive outputs. No SQL, SQLite, ORM, migration framework, or centralized database was found.

This makes an additive JSON record and append-only index the lowest-risk Phase 1 design. A database should not be introduced merely to satisfy the word “workspace.”

## Existing invariants to preserve

- CML v1.1 is the active primary method.
- Historical CML/Opportunity Validation branches remain frozen.
- Event time, knowledge time, and publication time remain separate.
- Narrative claims do not become structural facts.
- R3 does not become qualification or company-level migration evidence.
- Research freshness is distinct from research value.
- GDR authorization is distinct from CML scientific status.
- RTP reproducibility, ECN transitions, and RDL research governance remain conceptually distinct.
- Public artifacts must not absorb private customer data.

## Current failure modes

1. Research provenance is reconstructable only when a package happens to include sufficient domain-specific logs.
2. Search repetition cannot be detected reliably across packages or cases.
3. Model/tool/token/human/engineering costs are not captured.
4. Research has no normalized before/after uncertainty and decision record.
5. Stop reasons and low-value/failed research are not first-class.
6. Later outcomes cannot be joined end-to-end to a research round and its cost.
7. Historical Opportunity Validation tests contain post-milestone assumptions that now fail against legitimate later repository state.

## Minimum Phase 1 insertion point

Add `RDL_RESEARCH_RECORD` between the human/agent research request and existing evidence artifacts. It should point to existing evidence, CML state, timeline events, decisions, and outcomes by stable references. It should not copy their payloads or alter existing schemas.

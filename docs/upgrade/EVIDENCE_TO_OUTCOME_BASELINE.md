# Evidence-to-Outcome Baseline

## Audit boundary

This Phase 0 audit is an `L0_REUSE` inspection of commit `667708fe624f78768d97480856c8e92725665ea5`, which matched `origin/main` with a clean worktree at entry. No external research, schema migration, UI work, payment work, or historical rewrite was performed.

The repository contains 1,759 tracked files. Relevant committed inventories include 38 CML v1.1 files, 33 RDL files, 99 timeline files, 29 GDR-SE files, 20 monitoring files, 32 commercial files, and 100 scripts.

## What already exists

| Capability | Current implementation | Baseline finding |
| --- | --- | --- |
| Shared provenance | `evidence/core/schema/evidence_core_record.schema.json` | Reusable canonical identity, source/artifact references, event/knowledge/record times, correction, supersession, policy, and hashes. |
| CML method | `technical-risk/cml-v1.1/` | Accepted active method with nine schemas, vocabularies, templates, validators, historical freeze policy, and public/private boundary. |
| Pilot PDRE | `technical-risk/cml-v1.1/pdre/CML-PDRE-001/` | Private draft; PDRE-001A is candidate/R3 from seven ingested records. PDRE-001B is an unassigned active subhypothesis. |
| Research artifacts | `research/`, `technical-risk/records/`, `evidence-freeze/` | Source inventories, source registers, queries, counter-evidence logs, observations, claims, hypotheses, manifests, and frozen hashes exist in several domain-specific formats. |
| RDL runtime | `rdl/freshness/` | Implemented freshness policy, event invalidation, supersession, release evaluation, GDR adapter, four schemas, validators, and gate records. |
| Timeline/state | `timeline/`, `monitoring/` | Event ledgers, evidence and structural timelines, transition records, effective/known time separation, derivation manifests, and append/supersession tests. |
| Reproducibility/provenance gates | `gdr-se/` and frozen research manifests | Hash-bound evidence envelopes and authorization gates refer to `research_id` and RTP-style manifests. |
| RTP and ECN protocols | `whitepapers/RTP/`, `whitepapers/ECN/` | Draft scaffolds only; no complete standalone protocol/runtime was found. Some intended functions are implemented in manifests, timeline, monitoring, and GDR-SE. |
| Decision artifacts | Opportunity Validation packages, GDR authorization records, market validation | Decisions and authorizations exist locally, but no generic link from research expenditure to a decision transition exists. |
| Storage | JSON, JSONL, Markdown, static assets, Git history | File-backed and hash-oriented. No SQL/SQLite database or migration layer was found. |
| Frontend/deployment | Static HTML/CSS/JS plus a small Cloudflare landing proxy | Public/static surfaces exist, but Phase 0 found no evidence-to-outcome workspace UI or agent controller. |

## Answers required by Phase 0

### 1. What already exists?

Strong foundations exist for evidence provenance, immutable/frozen artifacts, source dependency, counter-evidence, CML structural analysis, timeline derivation, freshness, GDR authorization, private/public boundaries, and regression validation. They should be reused.

### 2. Where is CML state stored?

CML method state is stored in `technical-risk/cml-method-registry.json`, `technical-risk/CML_VERSION_HISTORY.jsonl`, and `technical-risk/cml-v1.1/`. Case state for the pilot is stored in `CASE.json`, `pdre-record.json`, `evidence-index.jsonl`, `timeline.jsonl`, `state-history.jsonl`, and `dependency-transfer.json` under the case directory.

### 3. Where is RDL state stored?

Implemented RDL state is freshness-specific and stored below `rdl/freshness/`, with evaluated subject outputs under `research/freshness/`. The public RDL charter and technical whitepaper are explicitly `DRAFT_SCAFFOLD`. There is no canonical `RDL_RESEARCH_RECORD` store.

### 4. Can research provenance currently be reconstructed?

`PARTIAL`. Source inventories, queries, timestamps, claims, manifests, hashes, and GDR envelopes allow reconstruction for well-packaged research. Reconstruction is inconsistent across research families and does not include a common initiation reason, minimum missing evidence, before/after state, cost, or stop decision.

### 5. Are model/tool/token costs currently observable?

`NO`. No implemented research record exposes model calls, tool calls, estimated tokens, model cost, data cost, human minutes, or engineering minutes. Existing cost fields concern industrial/commercial economics, not the cost of performing research.

### 6. Can repeated research currently be detected?

`PARTIAL`. Query logs and source IDs can be searched manually; source-dependency logic detects related sources and duplicate URLs within some packages. There is no normalized question/claim/entity/missing-evidence key, cross-case search-memory index, or automated duplicate-research gate.

### 7. Can research be linked to decisions?

`PARTIAL`. Some research IDs are linked to GDR authorizations, and CML evidence references support readiness transitions. There is no generic `DECISION_TO_CHANGE`, `decision_before`, `decision_after`, `DECISION_CHANGED`, or reason-for-change structure.

### 8. Can later outcomes be linked back to original evidence and research?

`PARTIAL`. CML market-validation and migration-failure schemas preserve later interpretation; timeline and state-transition models preserve time; GDR envelopes bind frozen inputs. No common outcome reference joins an operational outcome to the original RDL research round, decision, cost, and stop condition.

### 9. What is the minimum additive schema required for Phase 1?

One canonical `RDL_RESEARCH_RECORD` schema should wrap the existing Evidence Core and add:

- identity and scope: research ID, case/PDRE/customer references, classification, research level, initiator, times;
- governance: decision to change, question, minimum missing evidence, approval state;
- before/after snapshots: evidence counts/references, knowns, unknowns, hypothesis, readiness, decision;
- actions and telemetry: query/source references, tools/models, nullable usage and cost fields;
- result: new/contradictory/duplicate evidence, resolved/remaining unknowns, reusable assets;
- decision and stop: whether/why the decision changed, stop reason, human-review requirement;
- forward links: action/outcome references without duplicating ECN, RTP, CML, or Evidence Core data.

All cost fields must accept `UNKNOWN`; no opaque marginal-evidence-value score should be added.

### 10. What should be reused instead of rebuilt?

Reuse the Evidence Core, CML v1.1 objects and validators, PDRE append-only logs, timeline effective/known semantics, monitoring state transitions, RDL freshness engine, GDR research IDs/evidence envelopes/authorization history, source inventories, evidence graphs, hash conventions, frozen manifests, and historical-preservation regression helpers.

## Baseline decision

Phase 1 should be additive and file-backed. It should not create a second provenance store, timeline system, CML evidence core, outcome model, or freshness engine. It should introduce the missing research-process envelope and references that connect the existing systems.

## Stop reason

`PHASE_0_COMPLETE_HUMAN_REVIEW_REQUIRED`

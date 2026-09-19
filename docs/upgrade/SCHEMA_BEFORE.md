# Schema Baseline Before Phase 1

## Inventory

The repository contains 78 `*.schema.json` files. Twenty-four are documentation mirrors under `docs/`; 54 are source/runtime schemas. Relevant source schema groups are:

| Group | Count | Primary role |
| --- | ---: | --- |
| CML v1.1 | 9 | PDRE, dependency, exposure, beneficiary, trigger, response, validation, failure, public object |
| Technical-risk legacy/current | 14 | CML v0.1 and Opportunity Validation packages |
| Timeline | 10 | Atomic observations, event ledger, evidence/structural timelines, derivation, gate results |
| Commercial | 7 | Evidence graph, structural delta, authorization/order/delivery/report objects |
| GDR-SE | 5 | Evidence envelope, gates, aggregation, authorization, monitoring authorization |
| RDL freshness | 4 | Profile, evaluation, supersession, gate result |
| Monitoring | 4 | Information event, state transition, snapshot, build manifest |
| Evidence Core | 1 | Shared provenance and record envelope |

No schema named or equivalent to `RDL_RESEARCH_RECORD` exists.

## Existing reusable schema primitives

### Evidence Core

`evidence/core/schema/evidence_core_record.schema.json` already defines the shared record envelope: record and subject identity, domain/protocol/policy, source and artifact references, effective/known/created/updated time, verification/correction/supersession state, and input/record hashes.

### CML v1.1

CML provides evidence-backed structural state and append-only validation semantics. The pilot record already holds a stable CML ID, PDRE ID, evidence references, readiness, unknowns, timeline, and revision history.

### Timeline and monitoring

Timeline schemas provide event domains, derivation lineage, and effective/known time. Monitoring's state-transition schema provides prior/current state, basis, comparability, and source references.

### GDR-SE and RTP-style manifests

The evidence envelope binds a `research_id` to immutable hashes for canonical research, reports, source inventories, observations, claims, counter-evidence, and an RTP manifest. Authorization history adds gates, limitations, supersession, and evaluation identity.

### Evidence graph

The commercial evidence graph already represents source, artifact, claim, observation, calculation, hypothesis, counter-evidence, falsifier, and finding nodes with typed edges.

## Required RDL research fields versus current coverage

| Required concept | Current coverage | Status |
| --- | --- | --- |
| Research/case/PDRE identity | `research_id` in GDR; case/PDRE IDs in CML | Partial, not joined canonically |
| Customer case reference | Private/commercial records only | Partial |
| Started/completed time | Retrieval/evaluation timestamps | Partial |
| L0/L1/L2/L3 level | None | Missing |
| Initiator | None | Missing |
| Decision to change | Local decision fields in some packages | Missing as research governance |
| Question/minimum missing evidence | Search questions exist in some logs | Partial and inconsistent |
| Before/after evidence, unknowns, hypothesis, readiness, decision | Distributed across records/history | Missing as one comparable research round |
| Queries/sources checked/used/rejected/duplicate | Present in some logs | Partial |
| Model/tool/token/data/human/engineering cost | None | Missing |
| New/contradictory/duplicate evidence | Counter-evidence and source artifacts exist | Partial |
| Decision changed and why | No generic structure | Missing |
| Reusable assets | Manifests list artifacts, not declared reuse result | Partial |
| Stop reason | Terminal outcomes exist in some workflows | Missing as common RDL state |
| Human review required | GDR and freshness gates | Reusable reference |
| Later outcome link | Market validation/timeline can hold outcomes | Partial; no research-round join |

## Minimum additive Phase 1 schema

Recommended source path:

```text
rdl/research/schema/research-record.schema.json
```

Recommended top-level form:

```text
core                         # existing Evidence Core reference
research_record
  identity                   # research_id, case_id, pdre_id, nullable customer_case_id
  governance                 # level, initiator, classification, approval
  decision_target            # decision_to_change, question, minimum_missing_evidence
  before                     # evidence refs/count, knowns, unknowns, hypothesis, readiness, decision
  actions                    # query/source/tool/model references and counts
  telemetry                  # tokens/cost/time; UNKNOWN permitted
  result                     # new/contradictory/duplicate evidence and unknown resolution
  after                      # hypothesis, readiness, decision
  decision_change            # boolean and rationale
  reusable_assets
  stop                       # reason and human_review_required
  links                      # CML, RTP, ECN, GDR, action, outcome references
  revision_history
```

## Constraints for Phase 1

- Reference the Evidence Core; do not duplicate it.
- Keep event time and knowledge time distinct.
- Use references to CML, timeline/ECN, RTP manifests, GDR, and outcomes rather than copying their state.
- Permit `UNKNOWN` for every unobservable cost field.
- Preserve failed/no-evidence research as valid outcomes.
- Store raw marginal-value observables; prohibit an opaque aggregate MEV score.
- Separate inventory research from customer-specific research.
- Prevent private customer context from entering shared inventory records.
- Make records append/supersession-aware and hashable.
- Do not alter accepted CML v1.1 or historical schemas in Phase 1.

## Optional index, not a second store

A derived search-memory index may later normalize question, claim, entity, standard, component, migration path, and missing-evidence keys. It should be rebuildable from canonical RDL records and must not become a second evidence store.

# RDL Research Audit

## Finding

The implemented RDL is a research-freshness system, not yet a research-of-research system. It can determine whether evidence and releases remain current, react to events, preserve supersession relations, and feed GDR gates. It cannot yet measure why research was initiated, what it cost, how uncertainty changed, whether a decision changed, or whether research should have stopped.

The public RDL charter and technical whitepaper explicitly identify themselves as `DRAFT_SCAFFOLD`, so their unimplemented sections were not counted as capabilities.

## Capability assessment

| Question | Result | Evidence |
| --- | --- | --- |
| Can current RDL record research provenance? | `PARTIAL` | RDL freshness consumes hashed timelines/evidence and GDR research IDs, while source inventories and manifests live elsewhere. There is no common research-action provenance record. |
| Can it record research cost? | `NO` | No research model/tool/token/data/human/engineering cost fields or telemetry were found. |
| Can it record before/after state? | `PARTIAL` | CML state history and monitoring transitions preserve domain state changes, but not a research round's complete before/after evidence, uncertainty, hypothesis, readiness, and decision. |
| Can it link research to a decision? | `PARTIAL` | GDR authorization records link `research_id` to a release decision; Opportunity Validation contains local decisions. The generic decision-to-change and decision-changed link is absent. |
| Can it identify duplicate research? | `PARTIAL` | Existing source dependency, query logs, and source IDs reveal some duplication within packages. Cross-record semantic duplication and previous-search blocking are absent. |
| Can it record stop reason? | `NO` | Some workflows expose terminal outcomes, but no common research stop taxonomy or `STOP_REASON` exists. |
| Can it link later outcomes back to earlier research? | `PARTIAL` | Market validation, failure, timeline, evidence envelopes, and authorization history provide pieces. There is no common outcome-to-research-to-decision linkage. |

## Existing research-process evidence

The repository already contains useful raw material:

- counter-evidence logs with search questions, queries, sources checked, results, impacts, and remaining uncertainty;
- source inventories/registers with source IDs, issuers, independence groups, access states, retrieval/knowledge time, limitations, and claim links;
- canonical research packages with hypotheses, observations, claims, counter-evidence, and unknowns;
- immutable manifests and evidence envelopes with hashes;
- CML evidence indices and state history;
- GDR gate and authorization histories;
- freshness evaluations and supersession relations.

These assets are heterogeneous and often package-specific. They are inputs to RDL research records, not substitutes for them.

## Search memory audit

Current search memory is discoverable through repository text search and stable IDs, but it is not operationally enforced. There is no canonical lookup for:

- same decision question;
- same claim or hypothesis;
- same entity, component, standard, or migration path;
- same missing evidence;
- prior `PUBLIC_DATA_INSUFFICIENT`, `DUPLICATE_ONLY`, or saturation result;
- refresh interval or new-event exception.

Consequently, a future agent can repeat research even when the repository already contains an equivalent failed or saturated search.

## Marginal evidence value and saturation

Raw source/query counts can sometimes be reconstructed, but the required comparison variables are not normalized. The system cannot reliably calculate per research round:

- unique evidence gained;
- critical unknowns resolved;
- decision/readiness change;
- counter-evidence gained;
- reusable assets created;
- duplicate ratio;
- research cost and human time.

Phase 1 should capture these separate observables. It should not create a single MEV or research-quality score.

## Failed research

Existing logs do preserve some negative outcomes such as no current application found, unavailable sources, failed retrievals, and unresolved evidence. They do not normalize the workflow's required failed-research states. Phase 1 should add the taxonomy without rewriting historical logs.

## Boundary conclusion

RDL research governance must surround existing CML and research artifacts. It must not:

- determine CML structural truth;
- replace RTP/hash reproducibility;
- become the ECN/state-transition ledger;
- authorize publication or paid delivery in place of GDR-SE;
- introduce a parallel evidence store.

# UniPat competitive capability matrix

REVIEW_DATE = `2026-10-11`

NOVELTY_CLAIMED = `NO`

| Product | Public capability | Overlap with StructEvidence sample | Possible differentiation hypothesis | Evidence boundary |
| --- | --- | --- | --- | --- |
| Monthly-SWEBench | Roughly 100 fresh GitHub-derived software tasks per monthly release, with executable oracle and no-op checks | Time-bounded task creation, provenance, deterministic scoring, contamination concern | StructEvidence evaluates the state of real-world claims rather than code patches, and requires an explicit stop/unknown boundary | Different domain is not proof of buyer value or novelty |
| PaperBenchX | Scientific-reproduction tasks, clean replay, evidence-backed rubrics, public and held-out sets | Evidence-backed grading, reproducibility, controlled inputs, claim support | StructEvidence focuses on whether dated evidence supports a decision claim, including non-establishment and state transition, rather than reproducing an experiment | PaperBenchX already has strong provenance and replay controls; differentiation is narrower than "evidence-grounded" |
| SaaS-Bench | Long-horizon workflows across deployable SaaS applications, checked by weighted state checkpoints and strict resolved score | Multi-step task contracts and automated verification | StructEvidence can score evidence sufficiency without requiring a software environment and can test overclaiming/abstention | Lower infrastructure cost is a hypothesis; economic value is untested |
| Echo | Time-calibrated forecasting, multiple prediction points, future outcome resolution, post-training pipeline | Temporal indexing, evidence changes over time, structured output | StructEvidence classifies what is supportable at a cutoff; it does not predict the future and treats unresolved evidence as a valid terminal answer | Echo substantially overlaps the temporal dimension; do not claim temporal novelty |
| ExpertEval | Expert-authored Medicine, Finance and Law tasks with fine-grained rubrics and consequence-aware judgment | High-stakes decision context, expert review, explicit failure modes | StructEvidence adds source provenance, claim-level state vocabulary, counterevidence and stop-point discipline | ExpertEval already encodes professional judgment; no proof the proposed structure improves model performance |

## Confirmed sample capability

The pilot sample can deterministically test whether a submission:

- uses only evidence available at the knowledge cutoff;
- distinguishes `SUPPORTED` from `NOT_ESTABLISHED`;
- cites the qualifying evidence record;
- preserves a bounded non-generalization statement;
- stops without inventing a stronger state.

## Not established

- superiority over any listed UniPat product;
- incremental post-training lift;
- resistance to memorization outside this eight-task public sample;
- buyer willingness to pay;
- production-scale data generation cost;
- a defensible exclusive-data advantage.

## Sources

- https://unipat.ai/benchmarks
- https://unipat.ai/benchmarks/MonthlySWEBench
- https://unipat.ai/blog/PaperBenchX
- https://unipat.ai/blog/SaaS-Bench
- https://unipat.ai/blog/Echo
- https://unipat.ai/blog/ExpertEval

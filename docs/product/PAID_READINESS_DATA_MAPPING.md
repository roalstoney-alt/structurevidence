# Paid-Readiness Data Mapping

| UI field | Repository source | Rendering boundary |
|---|---|---|
| Decision before/after | Frozen L1 `research-record.json` and `human-review-freeze.json` | Single-instance evidence transition only |
| PDRE full validation | `human-review-freeze.json` | `false` rendered as `NO` |
| Five remaining unknowns | `human-review-freeze.json` | Four `UNKNOWN`; industry adoption `NOT_ESTABLISHED` |
| Source, publisher, dates, environment, architecture | `field-deployment-evidence.json` | Operator publication; not third-party audit |
| Four queries, nine sources, one deep review | `source-classification.json` | Raw observables; no score or cost |
| Two counter-evidence records | `source-classification.json`, L1-SRC-004/005 | Planned/future activity is non-qualifying |
| Old/alternative paths | CML `CASE.json`, `pdre-record.json` | Scope paths remain source-attributed |
| Dependency transfer | CML `dependency-transfer.json`, phase-2 `dependency-mappings.json` | Unsolved dependencies remain explicit |
| Subsystem watch | CML/phase-2 records | `UNKNOWN` when item-level evidence is absent |

Canonical evidence files are read-only inputs to the UI. No CML, RDL, RTP, ECN, GDR-SE, research, timeline, or human-review artifact was mutated.

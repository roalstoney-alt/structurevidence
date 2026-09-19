# RDL Stop Reason Taxonomy v0.1

Machine-readable vocabulary:

`rdl/research/vocabulary/STOP_REASONS.json`

## Standard reasons

| Code | Meaning |
| --- | --- |
| `EVIDENCE_SUFFICIENT` | Existing or newly obtained evidence is sufficient for the current decision. |
| `MINIMUM_MISSING_EVIDENCE_FOUND` | The narrowly defined missing evidence was obtained. |
| `RESEARCH_SATURATED` | Additional work is producing materially diminishing new information. |
| `DUPLICATE_ONLY` | Checked material added no unique evidence. |
| `PUBLIC_DATA_INSUFFICIENT` | The decision-critical fact is not adequately available in public data. |
| `SOURCE_UNAVAILABLE` | Required source access failed or is unavailable. |
| `SEARCH_SPACE_EXHAUSTED` | The authorized bounded search space was completed without sufficient evidence. |
| `EVIDENCE_CONTRADICTED` | New evidence contradicted the working evidence/hypothesis. |
| `WRONG_HYPOTHESIS` | The investigated hypothesis was rejected. |
| `COMMERCIAL_RELEVANCE_FAILED` | Research did not sustain the defined commercial relevance. |
| `RESEARCH_BUDGET_REACHED` | The authorized research budget was reached. |
| `HUMAN_REVIEW_REQUIRED` | Direction, acceptance, escalation or authority requires human review. |
| `PHASE_COMPLETE` | The authorized implementation/research phase is complete. |

## Rules

- A stop reason is a research outcome, not automatically an execution failure.
- Empty new-evidence lists are valid.
- `HUMAN_REVIEW_REQUIRED` requires the human-review flag.
- Extensions use `EXTENSION_[A-Z0-9_]+` and never rewrite historical records.
- Historical logs are not retroactively forced into this taxonomy.
- Stop reason does not authorize publication, payment, release or L2/L3 escalation.

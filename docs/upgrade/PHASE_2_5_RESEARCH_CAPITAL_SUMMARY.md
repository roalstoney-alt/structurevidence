# Phase 2.5 Research Capital Summary

Phase 2.5 converted the exact six frozen Phase 2 candidates into human decision-preparation cards. Existing canonical evidence showed high retrieval and reuse coverage within the inspected inventory, while qualification coverage remained incomplete. This is not a research-quality or capitalization score.

| Candidate | Current State | Decision Impact | Info Gain | Scope | Reuse | Codex Recommendation | Human Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `L1-CANDIDATE-001` | `INSUFFICIENT_QUALIFICATION_EVIDENCE` | HIGH | HIGH | `BOUNDED_MULTI_SOURCE` | HIGH | `DEFER_L2_REVIEW` | `PENDING` |
| `L1-CANDIDATE-002` | `CONTRADICTORY_EVIDENCE` | HIGH | HIGH | `VERY_NARROW` | HIGH | `L1_VERIFY` | `PENDING` |
| `L1-CANDIDATE-003` | `INSUFFICIENT_INDEPENDENCE` | MEDIUM | MEDIUM | `BOUNDED_MULTI_SOURCE` | MEDIUM | `DEFER_L2_REVIEW` | `PENDING` |
| `L1-CANDIDATE-004` | `MISSING_EVIDENCE` | MEDIUM | HIGH | `BOUNDED_MULTI_SOURCE` | MEDIUM | `DEFER_L2_REVIEW` | `PENDING` |
| `L1-CANDIDATE-005` | `MISSING_EVIDENCE` | HIGH | HIGH | `BOUNDED_MULTI_SOURCE` | HIGH | `DEFER_L2_REVIEW` | `PENDING` |
| `L1-CANDIDATE-006` | `INSUFFICIENT_INDEPENDENCE` | LOW | MEDIUM | `NARROW` | HIGH | `WATCH` | `PENDING` |

## Recommendation counts

```text
L1_VERIFY = 1
WATCH = 1
DEFER = 0
DEFER_L2_REVIEW = 4
DO_NOT_RESEARCH = 0
AUTHORIZED_L1 = 0
HUMAN_DECISIONS_PENDING = 6
```

The table is intentionally unranked. Information gain and impact are visible qualitative dimensions, not a composite score. Commercial relevance remains `UNKNOWN` for five cards and `NONE` for the source-lineage governance card.

Human review must assign exactly one of `APPROVE_L1`, `WATCH`, `DEFER`, `REJECT`, or `REQUEST_RESCOPING` to each candidate. Only a later explicit `APPROVE_L1` can create one bounded authorization.

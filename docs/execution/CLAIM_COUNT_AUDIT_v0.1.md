# Claim Count Consistency Audit v0.1

Repository entry SHA: `85f625b1f1eec890bd9980e51d5e4da1078d7313`

Authoritative source: `claims/index.json`

## Authoritative result

| Scope | Claim count |
|---|---:|
| Total | 26 |
| `CML-PDRE-001` | 9 |
| `SE-BESS-SODIUM-001` | 9 |
| `SE-ONC-NSQNSCLC-CN-001` | 8 |
| Cases | 3 |

The audit derived these values directly from the 26 entries in `claims/index.json` and confirmed that the corresponding 26 files exist under `claims/`.

## References audited

- Root and docs claim indexes
- Root README and method contract
- Agent page and deterministic discovery generator
- English and Chinese method-paper sources
- Replication-kit README, protocol, publication drafts, and launch note
- Release manifest and publication workflow
- Existing execution and test references

All claim-count references in scope use 26. The release manifest records the same 9/9/8 distribution. No claim-count reference to 27 was found; unrelated occurrences of 27 describe dates, identifiers, or TRON validator counts and are outside this audit.

## Mismatched references

None.

## Resolution performed

No existing count statement required correction. The minimal research snapshot now derives `total_claims`, `case_count`, and `case_claim_counts` from `claims/index.json`, and its deterministic validation prevents count drift.

`COUNT_CONSISTENCY = PASS`

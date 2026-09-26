# SE-FRR Known Baseline Exceptions v0.1

Status: `FROZEN`  
Frozen at Phase 1 entry: `d08ee23c212daf2ef97027002d95f24b268e8637`  
Machine-readable authority: `SE_FRR_KNOWN_BASELINE_EXCEPTIONS_v0.1.json`

## Baseline signature

```text
python3 -m unittest discover -s scripts -p 'test_*.py'
Ran 258 tests
255 passed
2 failures
1 error
```

Exactly three historical exceptions are accepted:

| ID | Test | Expected signature | Disposition |
|---|---|---|---|
| `SE-FRR-BE-001` | Phase A package initialization | `ValueError: Phase A history entry` | Historical runner limitation |
| `SE-FRR-BE-002` | Phase B positive package | `OV-B01_BASELINE_INTEGRITY`, 12 pass / 1 fail / 3 not evaluated | Historical runner limitation |
| `SE-FRR-BE-003` | Phase B-R1 positive targets | `OV-R101_ACCEPTED_WAVE1_BASELINE`, 7 pass / 1 fail | Historical runner limitation |

These tests contain milestone-era current-HEAD assumptions. Repository decision records preserve their artifacts as historical method branches and direct current preservation checks to base-snapshot/hash comparison.

## Freeze rule

`KNOWN_BASELINE_EXCEPTION_SET = FROZEN`

- Phase 1 must not edit these historical validators merely to make the suite green.
- A new SE-FRR failure must not be added to this set.
- Any signature drift is a new unexplained failure until investigated.
- Phase 1 passes only when the complete baseline suite contains exactly these three non-passing tests and no others.

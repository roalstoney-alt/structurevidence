# Timeline R1.1a Clock Audit

Default clock source: `timeline.engine.clock.utc_now`

Explicit `--as-of`: PASS

Input bundle includes `evaluation_as_of`: PASS

| Gate | Status | Computed facts |
| --- | --- | --- |
| TL11A_06_REAL_UTC_AS_OF | PASS | {"evaluation_as_of": "2026-12-01T00:00:00Z"} |
| TL11A_07_EXPLICIT_AS_OF_REPRODUCTION | PASS | {"as_of_changes_input_hash": true, "input_hash_equal": true, "semantic_digest_equal": true} |
| TL11A_08_NAIVE_TIMESTAMP_REJECT | PASS | {"naive_rejected": true} |
| TL11A_09_AGE_PROGRESSION | PASS | {"age_2026_09_10": 1, "age_2026_10_10": 31} |
| TL11A_10_NO_ACTIVE_FIXED_AS_OF | PASS | {"active_fixed_as_of_count": 0} |

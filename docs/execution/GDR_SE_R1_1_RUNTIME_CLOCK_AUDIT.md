# GDR-SE R1.1 Runtime Clock Audit

The runtime now evaluates against `evaluation_as_of`, supplied by `--as-of` or generated from current UTC. Naive timestamps are rejected. `record_created_at`, `evaluation_as_of`, and `evidence_last_reviewed` are recorded as separate fields.

Representative evaluation_as_of: `2026-09-10T14:18:35.507637Z`

Clock tests: `GDR_SE_CLOCK_TESTS_PASS`

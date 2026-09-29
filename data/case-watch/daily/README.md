# Daily observation ledger

Daily observation records are append-only JSON Lines files at:

`YYYY/MM/YYYY-MM-DD.jsonl`

Create one line only for a meaningful observation that conforms to
`data/case-watch/schema/daily-observation.schema.json`. A day with no qualifying
repository-local or authorized public observation is represented by its daily report
and search-provenance record; it does not receive a synthetic evidence observation.

Daily records must keep `public_state_mutated` set to `false`. Public state changes
require a separate weekly manifest with an explicit human `APPROVE_PUBLICATION`
decision.

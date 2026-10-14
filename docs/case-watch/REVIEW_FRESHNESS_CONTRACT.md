# Public review freshness

`as_of` in an accepted case record is its evidence-state cutoff. A calendar tick,
task schedule, page render, repository audit or failed page open never advances it.
`last_material_change` also remains unchanged when the finding is no change.

`data/case-watch/monitoring-status.json` records the monitoring period and points
to real, versioned review artifacts. `status_recorded_at` is administrative metadata,
not a scientific review timestamp. Pending review counts are null, not invented zeros.

For each actual review, append a JSON artifact with `review_id`, `reviewed_at`,
`result`, `review_complete`, `search_boundary`, `sources_checked`,
`new_qualifying_evidence_count`, `new_counter_evidence_count`, and the old/new state.
Result is `NO_STATE_CHANGE`, `REVIEW_INCOMPLETE` or `HUMAN_GATE_REQUIRED`.
`NO_STATE_CHANGE` requires a completed bounded review, actual checked sources and
explicit counts. Inaccessible key sources require `REVIEW_INCOMPLETE`; candidate
material changes retain the human gate. Review publication is not approval of a
new substantive evidence state.

Update each case's current monitoring period, `period_review_id`, and
`latest_review_file` only from that actual artifact. Keep earlier artifacts unchanged.
An unrun period is `NOT_YET_REVIEWED`, with no period review ID. Never relabel an
older review as this week's work. Historical candidate W40 remains unchanged.

Run `python scripts/export_case_review_status.py` to regenerate both
`cases/review-status.json` and the root/docs case index. The projection reads the
latest accepted case index/snapshot, so the Irkutsk v0.2 cutoff does not lag behind
a hand-maintained catalog. It does not itself perform external verification.

Run `python scripts/test_case_review_status.py`, the existing case-watch checks,
and relevant protection/parity checks. Preserve root/docs mirrors and immutable
case records. Commit with the expected main SHA, observe the matching Pages run,
and verify the public response bodies where access permits. A saved task or a
successful deployment alone does not prove a completed scheduled public update.

Prospectively from 2026-10-14, the single StructEvidence 22:00 Asia/Singapore
logical trigger owns the unified daily run. It checks 800V DC, sodium-ion BESS
and Irkutsk daily; Sunday adds the weekly synthesis and the bounded historical
NSCLC review, with NSCLC remaining folded. Monday adds the private-wall SOCSM
check. The earlier three-case weekly and separate Irkutsk task descriptions are
preserved as historical schedule records only and do not authorize parallel
production timers. See `docs/ops/SE_UNIFIED_RUNTIME_CONTRACT.md`.

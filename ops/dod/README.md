# SE-DOD-001 — Decision Opportunity Discovery

This workspace implements the controlled first execution defined by
`STRUCTEVIDENCE_DECISION_OPPORTUNITY_DISCOVERY_CODEX_WORKFLOW_v0.1.md`.

Snapshot date: 2026-10-08 (Asia/Shanghai)

Operating boundaries:

- The radar covers only the four frozen verticals A–D.
- The records describe public evidence boundaries, not everything an organization may know privately.
- An evidence gap is not a company failure and is not an investment recommendation.
- Qualification uses six binary gates; no predictive or purchase-probability score is used.
- No outreach has been sent. Rows marked `READY_FOR_HUMAN` require explicit recipient and channel authorization before sending.
- No guessed email address is eligible for the send queue.

`OPPORTUNITIES.csv` is the operational gate ledger supporting the prescribed CSV schemas. It selects at most ten opportunities and records why the remaining radar events are held.

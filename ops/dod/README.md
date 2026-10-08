# SE-DOD-001 — Decision Opportunity Discovery

This workspace implements the controlled first execution defined by
`STRUCTEVIDENCE_DECISION_OPPORTUNITY_DISCOVERY_CODEX_WORKFLOW_v0.1.md`.

Snapshot date: 2026-10-08 (Asia/Shanghai)
Protocol level: v0.1.1
Run type: `CALIBRATION`

Operating boundaries:

- The radar covers only the four frozen verticals A–D.
- Five events per vertical validate the workflow only. This is not market coverage and cannot support tier relaxation or a conclusion about market demand.
- The records describe public evidence boundaries, not everything an organization may know privately.
- A gap qualifies for opportunity selection only when resolving it could materially change a real decision. A missing public fact alone is insufficient.
- An evidence gap is not a company failure and is not an investment recommendation. Internal or private evidence may exist outside the reviewed boundary.
- Owner resolution distinguishes named accountable people, accountable roles, company routes, and unresolved ownership. A corporate route is not proof of decision responsibility.
- No outreach has been sent. Rows marked `HOLD_PENDING_HUMAN_REVIEW` require manual review and explicit recipient/channel authorization before sending.
- No guessed email address is eligible for the send queue.

`MATERIAL_DECISION_EVIDENCE_GAPS.csv` applies the material-impact test to the claim inventory. `OPPORTUNITIES.csv` is the patched qualification and owner-resolution ledger. `PRE_SEND_GATES.csv` records the nine required quality gates for the five provisional first-wave messages.

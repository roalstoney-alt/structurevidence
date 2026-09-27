# Reality Event Radar v0.1

The Reality Event Radar identifies public evidence that may alter an evolving object's recorded State. It is not a customer-search or outreach system.

Output classes are `NEW_SUPPORTING_EVIDENCE`, `NEW_COUNTER_EVIDENCE`, `STATE_CHANGE_CANDIDATE`, `UNKNOWN_RESOLUTION_CANDIDATE`, `NEW_BRANCH_CANDIDATE`, `OUTCOME_EVIDENCE`, `DUPLICATE`, and `NOISE`.

The Radar produces review candidates only. It cannot send messages, follow accounts, create leads, prepare outreach, activate payments, or mutate canonical State. A candidate must pass L0 verification before evidence creation. `NO_STATE_CHANGE` stops automatic escalation unless a human explicitly approves deeper work.

Phase 5A supplies classification architecture only. No scheduled crawler or large-scale public scan is activated.

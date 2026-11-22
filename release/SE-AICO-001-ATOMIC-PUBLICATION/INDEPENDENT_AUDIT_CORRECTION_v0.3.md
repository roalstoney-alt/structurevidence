# SE-AICO-001 independent activation audit correction v0.3

## Scope and controls

This correction addresses only P0-1 through P1-5 from the 2026-11-22 independent audit of PR #97. It does not change the financial research, frozen v0.1/v0.2 claim records, public source registry, SEC source digest or another case's evidence history.

`MERGE_AUTHORIZED=NO`

`AUTOMATIC_DEPLOYMENT_AUTHORIZED=NO`

`SOCIAL_PUBLISH_AUTHORIZED=NO`

## P0-1 — independently verified authority and deployment

Actual mode now retrieves the owner authorization comment from GitHub, verifies repository-owner authorship, exact required fields and exact comment-body SHA256. It independently retrieves PR #97, `main`, Actions run, Pages deployment/status and live HTTP bytes. Caller-supplied IDs and strings are selectors, not proof. Test fixtures and test transports are rejected by the actual CLI.

## P0-2 — deployment-specific hashes

The initial Pages receipt contains only initial-deployment observations. The pending current-state document has separate `initial_pages_deployment`, `activation_overlay_deployment` and `final_live_verification` fields. Overlay verification calculates hashes from current live bytes and emits a separate final-live-verification receipt. Initial hashes are never copied into final-current fields.

The overlay state is `DEPLOYED_PENDING_LIVE_VERIFICATION`; it does not emit `PUBLISHED_VERIFIED`, a publication timestamp or external-promotion authority.

## P0-3 — deployed main topology

Overlay application binds to the observed deployed `main` SHA instead of the pre-merge PR SHA. A normal merge requires candidate ancestry. A squash merge requires GitHub's merge-result SHA and a tree identical to the authorized candidate. Both policies have positive tests; unrelated `main` fails closed.

## P1-4 — transactional application

All overlay sources are hash-verified before mutation. Existing destinations are backed up, staged files are replaced, every result is re-hashed and any exception restores all touched destinations. A fault-injection test proves rollback after a partial replacement.

## P1-5 — truthful interim state

The public interim projection says final live verification is required, leaves `datePublished` null and prohibits promotion. Owner authority for initial merge/deployment and later overlay deployment must be expressed in two separately fetched GitHub owner comments. No authority is inferred from the runbook or a local JSON literal.

## Negative test boundary

The verifier explicitly rejects incomplete owner approval, fixture use in the actual gate, fabricated deployment-status IDs, future deployment timestamps, unrelated `main`, incorrect final live hashes and partial application. Frozen evidence preservation and root/docs byte equality remain covered.

## Remaining gate

No actual authorization, merge, deployment observation or final receipt is created by this correction. The corrected exact PR HEAD must be reviewed and separately authorized before any production-changing action.

`NEXT_GATE=OWNER_REVIEW_OF_VERIFIABLE_TWO_PHASE_ACTIVATION`

# IREN tracker publication transition

Status: `OWNER_AUTHORIZED_PENDING_MERGE_AND_LIVE_VERIFICATION`

Authorization ID: `SE-IREN-PUBLICATION-20261028-01`

Authorized candidate head: `1523c8688dfa5dd6ff7b1ae85e3a54b8412c3c8a`

Authorization time: `2026-10-27T20:06:55Z`

The authenticated task owner explicitly authorized publication and requested a disclaimer at the bottom of the research website. The public authorization record intentionally does not invent separate financial, legal, privacy, or row-level reviewer identities.

## Applied publication projections

- Owner-authorized public status on the IREN page and machine-readable snapshot.
- Append-only `events-v0.2.json`; original `events-v0.1.json` remains byte-identical.
- Public authorization record bound to the reviewed candidate SHA and digest.
- Five-case discovery index and deterministic `review-status.json` projection.
- English-only sitemap entries for the page, public snapshot, registry, and both event-ledger versions.
- Bottom-of-page research disclaimer covering investment, legal, accounting, tax, certification, forecast, assurance, attribution, missing-evidence, source-verification, and qualified-advice boundaries.
- No translated route, commercial POST, Worker/D1 change, social post, or evidence-state upgrade.

## Verification before merge

- IREN adversarial/publication suite: `15/15 PASS`.
- Case review projection suite: `6/6 PASS`.
- History/SEO/EKN publication suites: `16/16 PASS`.
- Internal link audit: `0` orphans, `0` broken links, `0` state gaps, `0` parent gaps.
- Differential history guard: `PASS`.
- Root/docs page, case index, review status, and sitemap parity: `PASS`.
- Full discovery: `29/43`; 14 PR26 baseline assertions remain. Nine were already stale before this transition, while five now truthfully report the authorized review-status/generator/test projection changes. The PR26 baseline was not rewritten or weakened.

## Remaining live gate

Merge through the normal repository policy, wait for the research-site deployment, then verify the canonical page, case index, JSON, sitemap, footer disclaimer, and expected 404 behavior. Record the merge and deployed SHA in a separate publication receipt.

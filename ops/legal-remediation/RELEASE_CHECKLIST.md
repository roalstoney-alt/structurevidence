# Release checklist

Status: review preparation only. This branch is not authorized for merge, production deployment or production D1 migration.

## Common gates

- [x] Base/branch diff independently reviewed; branch is based directly on `bfeeae97babd6a245faf9b0bdee4109dd6d2417c`.
- [x] No draft placeholder or `NEEDS_*` assertion appears as a claimed public fact.
- [x] Exactly three featured cases remain: 800V DC, Sodium-ion BESS and Irkutsk; NSCLC remains accessible but is not featured.
- [x] Scientific evidence cut-offs, case files, histories and `last_material_change` are unchanged.
- [x] Root/docs page mirrors and active Worker import chain are identified and tested.
- [x] Focused tests pass; reproducible baseline failures are documented rather than weakened.
- [x] Synthetic migrations 0001–0003 and legacy/new form behavior are tested.
- [ ] Operator completes the seven-item confirmation list in `OPERATOR_FACTS_REGISTER.md`.
- [ ] Counsel reviews the packet and operator records accepted wording/remaining advice.
- [ ] PR is created and independently approved; do not describe engineering tests as a legal certification.

## `.org` GitHub Pages

- [x] Static accuracy corrections, legal pages and docs mirrors are present in the branch.
- [x] No case evidence file or monitoring task changed.
- [ ] Operator/counsel approve only the statements whose facts or legal effect they can confirm.
- [ ] Merge authorization and Pages release window are granted.
- [ ] Post-release check: actual commit, HTTP 200, canonical links, three featured cards, localized/root-docs consistency, NSCLC old URL/history, corrections/privacy/terms/refund pages.
- [ ] If verification fails, redeploy the previous Pages commit and investigate caching; do not advance a case cut-off to fix copy.

## `.com` Worker

- [x] Active import chain is `worker.js` → `commercial-upgrade.js` → `commercial-ui.js`.
- [x] Server enforces notice version plus separate privacy/confidentiality acknowledgements; publication/marketing stay false.
- [x] Optional narrative is isolated from event notes and public responses; Access-protected admin can display it safely using `textContent`.
- [ ] Operator facts/counsel wording gates are closed.
- [ ] Exact Worker build SHA, secrets/bindings, Access audiences/admins, rollback artifact and maintenance window are approved.
- [ ] D1 0003 is applied and verified before the new Worker is deployed.
- [ ] Production smoke submission is separately authorized and uses synthetic non-sensitive data.
- [ ] Post-release check: Privacy/Terms/forms, legacy payload rejection, acknowledgement record, private-context isolation, public non-exposure and admin Access denial/allow paths.
- [ ] If application behavior fails after 0003, restore the previous Worker artifact and stop intake if necessary; retain Access and the additive tables.

## D1 production migration

- [x] `PRODUCTION_DATA_MIGRATION_PLAN.md` documents read-only preflight, synthetic rehearsal, compatibility, recovery and irreversible limits.
- [ ] Cloudflare account/database identity and applied-migration list are verified with authorized credentials.
- [ ] Aggregate-only legacy-note assessment and separately authorized disposition scope are approved.
- [ ] Recovery point and non-production recovery drill are recorded.
- [ ] Production database migration authorization is explicit and names operator/approver/window.
- [ ] 0003 is applied, re-listed and schema-verified without selecting unrelated customer content.
- [ ] No trigger, gap state or historical record is deleted or rewritten.

## Release sequencing and authority

1. Close operator-fact and counsel gates.
2. Approve and merge the reviewed PR (not authorized in this task).
3. `.org` can be released and verified as a discrete static step only if its approved content is internally complete.
4. For `.com`, authorize and verify D1 preflight/recovery, apply 0003, then deploy the exact Worker build in the same controlled cut-over.
5. Verify each surface before progressing. A successful `.org` release does not authorize `.com` or D1.

`PRODUCTION_CONTENT_VERIFIED` may be set to `PASS` only after the deployed SHA, HTTP status and response body have been checked. `MIGRATION_VERIFIED` requires the remote migration ledger and schema check, not a local synthetic test.

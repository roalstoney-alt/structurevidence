# Release checklist

Status: `.com` release performed under explicit owner authorization on 2026-10-08. See `PRODUCTION_RELEASE_RECORD_2026-10-08.md`. PR #15 was not merged and `.org` was not published.

## Common gates

- [x] Base/branch diff independently reviewed; branch is based directly on `bfeeae97babd6a245faf9b0bdee4109dd6d2417c`.
- [x] No draft placeholder or `NEEDS_*` assertion appears as a claimed public fact.
- [x] Exactly three featured cases remain: 800V DC, Sodium-ion BESS and Irkutsk; NSCLC remains accessible but is not featured.
- [x] Scientific evidence cut-offs, case files, histories and `last_material_change` are unchanged.
- [x] Root/docs page mirrors and active Worker import chain are identified and tested.
- [x] Focused tests pass; reproducible baseline failures are documented rather than weakened.
- [x] Synthetic migrations 0001–0003 and legacy/new form behavior are tested.
- [ ] Operator completes the seven-item confirmation list in `OPERATOR_FACTS_REGISTER.md`; unresolved facts remain explicitly unconfirmed.
- [ ] Counsel reviews the packet and operator records accepted wording/remaining advice. Counsel was explicitly not a prerequisite for this owner-approved `.com` release and remains `PENDING`.
- [x] Draft PR #15 exists at the exact release source and owner content approval was recorded. No engineering result is described as legal certification.

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
- [ ] Operator facts/counsel wording gates are closed. The owner explicitly accepted the current bounded copy while these remain pending.
- [x] Exact Worker source SHA, secret names/bindings, Access configuration, prior rollback version and release timing are recorded.
- [x] D1 0003 was applied and verified before the new Worker was deployed.
- [x] One production smoke submission was separately authorized and used synthetic non-sensitive data.
- [ ] Post-release check is complete except for the Access-authenticated positive admin path. Privacy/Terms/forms, rejection behavior, acknowledgement record, private-context isolation, public non-exposure and unauthenticated Access denial passed.
- [ ] If application behavior fails after 0003, restore the previous Worker artifact and stop intake if necessary; retain Access and the additive tables.

## D1 production migration

- [x] `PRODUCTION_DATA_MIGRATION_PLAN.md` documents read-only preflight, synthetic rehearsal, compatibility, recovery and irreversible limits.
- [x] Cloudflare account/database identity and applied-migration list were verified with authorized credentials.
- [x] Aggregate-only legacy-note assessment was performed; disposition remains a separate future scope.
- [x] A pre-migration Time Travel point and access-restricted schema-only artifact were recorded; bookmark resolution and restore syntax were verified without a destructive production restore.
- [x] Production D1 migration authorization was explicit for this run.
- [x] 0003 was applied, re-listed and schema-verified without selecting unrelated customer content.
- [x] No trigger, gap state or historical record was deleted or rewritten.

## Release sequencing and authority

1. The owner approved current content and explicitly authorized `.com` plus D1 while keeping counsel and operator-fact items pending.
2. 0003 was applied and verified, followed by the exact Worker build and production acceptance checks.
3. PR #15 remains unmerged and `.org` remains a separate, unauthorized publication step.
4. Complete the Access-authenticated positive admin-path check when an approved credential/session is available; do not bypass Access.
5. Close the remaining operator-fact and counsel work independently of this recorded technical release.

`PRODUCTION_CONTENT_VERIFIED` may be set to `PASS` only after the deployed SHA, HTTP status and response body have been checked. `MIGRATION_VERIFIED` requires the remote migration ledger and schema check, not a local synthetic test.

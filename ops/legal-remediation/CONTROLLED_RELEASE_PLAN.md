# Controlled release and rollback plan

## Approval boundary

This plan prepares release mechanics only. The current authorization excludes merging main, production deployment, cache purge, production smoke writes and D1 migration. Operator facts and counsel advice remain documented gates, not facts that engineering may infer.

## Version order

1. Freeze and approve the PR commit; record Pages and Worker source SHAs and migration checksum.
2. Release `.org` from the approved commit only after its content gates close. Verify it independently.
3. For `.com`, verify live D1 migration state and recovery readiness during the approved window.
4. Apply migration 0003 before deploying the new Worker because new submissions require `request_notices` and `request_private_context`.
5. Deploy the exact Worker artifact and invalidate stale commercial form assets as one cut-over; legacy unversioned payloads intentionally fail closed.
6. Run only an explicitly authorized, synthetic smoke request and record non-sensitive results.

## `.org` release and rollback

- Preflight: three featured cards, no NSCLC homepage card, unchanged four case histories/cut-offs, root/docs byte equality, legal copy free of internal placeholders.
- Release: publish the approved GitHub Pages commit. Do not pair this action with an implicit Worker or database release.
- Verify: final URL/body/canonical for localized homepages, legal pages, 800V, Sodium-ion, Irkutsk and the existing NSCLC URL.
- Rollback: redeploy the prior known-good Pages commit if a rendering, routing or approved-copy boundary fails. If the concern is a restricted public item, also inspect JSON, old URLs, feeds and caches; `noindex` alone is not withdrawal.

## `.com` Worker release and rollback

- Preflight: bindings/secrets and Access audiences/allowlist, approved legal copy, exact artifact, prior deployment identifier and current forms.
- Database: follow `PRODUCTION_DATA_MIGRATION_PLAN.md`; halt Worker deployment if 0003 is not confirmed applied.
- Verify: routes, CSP/security headers, form acknowledgement/versioning, public response isolation, null event note, restricted admin retrieval and unauthenticated Access denial.
- Rollback: restore the previous Worker deployment while leaving successfully created additive tables in place. If confidentiality isolation is uncertain, stop intake through an approved switch. Never weaken Access or change a public evidence state as a deployment repair.

## D1 failure and recovery

- A failed 0003 application stops the release. Preserve provider diagnostics without customer values and use the approved recovery point if required.
- A successful 0003 is not safely reversible after it contains records. Do not drop its tables. Use a forward fix; a previous Worker can ignore the new additive schema.
- Legacy event-note review is a distinct, authorized data-governance project. It must not remove append-only triggers or rely on an untested deletion promise for Time Travel/backups.

## Release evidence

Record approver, operator, maintenance window, source/deployment SHAs, migration list before/after, recovery point, HTTP/body checks and rollback decision. Keep tokens and customer content out of release artifacts.

Production deployment, cache purge, customer-data inspection/transformation and migration execution remain outside this task.

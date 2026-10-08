# Controlled release and rollback plan

1. Obtain operator-fact and counsel gates in `RELEASE_CHECKLIST.md`.
2. Review the PR diff, verify no scientific cut-off or historical snapshot changed, and run all focused checks.
3. Apply the D1 migration in a non-production environment with synthetic data; verify acknowledgement records, private-context separation and admin-only access.
4. Release `.org` static changes and `.com` Worker changes as independent controlled steps. Do not infer one from the other.
5. Verify the actual deployed SHA plus response bodies for homepage cards, four case URLs, legal pages and forms. Use synthetic non-sensitive submissions only with explicit production-test authorization.
6. If a critical boundary fails, stop the second release step, restore the previous deployment artifact, keep the database migration (it is additive), and disable intake only through an approved operational switch—not by weakening Access.
7. Record cache handling for any `RESTRICTED` or `WITHDRAWN` event. A deployment success or `noindex` is insufficient proof of removal.

Production deployment, cache purge and customer-data migration are outside this task.

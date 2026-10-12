# Validation report

## Baseline

Base `bfeeae97babd6a245faf9b0bdee4109dd6d2417c` was tested before edits. Case-review, case-watch, Irkutsk publication/alias, public-commercial boundary, i18n and readiness checks passed. Existing failures:

- `scripts/test_public_case_primitives_v01.py`: 2 failures caused by an existing NSCLC root/docs protected-baseline mismatch.
- `scripts/test_english_public_surface.py`: existing CJK content in linked root `index.html`.
- `scripts/test_commercial_domain_split.py`: existing assertion expects only `.com`, while configured `PUBLIC_ORIGINS` also includes the two authorized `.org` research origins.

These failures reproduce after the branch changes and were not hidden or weakened.

## Branch results

- `python3 scripts/test_legal_boundary_remediation.py`: PASS, 6/6 test methods, including root/docs localized mirrors and restricted synthetic JSON/old-URL/feed renderers.
- Direct Worker entry: `/Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --test test/*.test.js`: PASS, 34/34.
- `python3 scripts/test_case_review_status.py`: PASS, 6/6.
- `python3 scripts/test_case_watch.py`: PASS, 5/5.
- `python3 scripts/test_irkutsk_publication.py`: PASS.
- `python3 scripts/test_irkutsk_alias_repair.py`: PASS.
- `python3 scripts/test_public_commercial_boundary.py`: PASS.
- `python3 scripts/test_commercial_i18n.py`: PASS.
- `python3 scripts/test_commercial_readiness.py`: PASS, 9/9.
- `scripts/test_public_case_primitives_v01.py`, `scripts/test_english_public_surface.py`, `scripts/test_commercial_domain_split.py`: same baseline failures listed above.
- SQLite synthetic apply of migrations `0001`, `0002`, `0003`: PASS; new table and trigger schemas inspected.
- Wrangler 4.136.2 direct dry-run after close-out changes: bundle generated, 175.11 KiB / gzip 44.13 KiB, expected D1/rate-limit/origin/Access bindings listed, `--dry-run: exiting now`; sandbox blocked only the user-preference log-file write and process exited successfully.
- `git diff --check`: PASS.
- Branch diff under `cases/` and `docs/cases/`: empty.
- Branch diff under monitoring paths and workflows: empty.
- A remote D1 migration-list check was attempted read-only but Wrangler required `CLOUDFLARE_API_TOKEN` in this non-interactive environment. No credential was probed and no login was initiated; production migration state remains `NEEDS_OPERATOR_CONFIRMATION`.

`pnpm test` itself was not usable in the isolated `/tmp` worktree because pnpm attempted registry metadata/dependency reconciliation while network was unavailable. The actual package script is `node --test test/*.test.js`; it was run directly against the copied baseline dependency tree and passed.

## Assertions covered

- Required acknowledgements remain enforced when bypassing the front end.
- Notice version and server acknowledgement time are recorded without persisting a full IP/fingerprint.
- Customer narrative is absent from the public response and append-only event note.
- Customer narrative is retrievable only through the Access-protected admin detail path, and the admin renderer uses `textContent` rather than HTML insertion.
- Restricted synthetic publication omits its private payload from JSON, legacy-URL and feed representations.
- Legal copy does not advance scientific cut-offs or review clocks.
- Featured count remains exactly three; NSCLC remains accessible and is not featured.
- Root/docs legal mirrors are byte-identical.

No production deployment, production migration, cache purge, customer-data rewrite or live form submission was performed.

New regression count attributable to this branch: **0**. The three baseline test groups listed above fail against unchanged inputs; the relevant tests/input files have no diff from the base SHA.

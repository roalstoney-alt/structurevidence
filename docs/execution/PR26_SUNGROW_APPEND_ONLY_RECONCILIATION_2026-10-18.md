# PR #26 append-only reconciliation receipt

As of 2026-10-18T02:36:45.552616+00:00.

- ORIGINAL_RECORDS_CHANGED = 0
- NEW_RECORDS_APPENDED = 5 logical records (12 physical files)
- DUPLICATE_IDS_RESOLVED = 1
- PROTECTED_BASELINE_DRIFT = 0
- X_POST_SENT = 0
- NEW_PR = API_BLOCKED; new integration branch prepared
- MERGE_SHA = NONE
- PRODUCTION_STATUS = NOT_DEPLOYED / UNVERIFIED

## Frozen source and isolated integration

Latest main was and remains `5a3bd2883af40969c5ca63c0581d15afdc7b30b4`. Original unpublished PR #26 remains at `0c8b940c3a3a6079e6260ddde89f2af5ca354d93`; it was neither merged nor rewritten. A verified complete-history Git bundle preserves that ref locally (SHA256 `3761f262d1f64a1dad533a36f1b13f594099269394396293e6be44d693018ad0`). Original candidate file hashes are frozen in `data/ops/se/reconciliations/pr26-sungrow-20261018-01.json`.

New branch: `integrate/pr26-sungrow-append-only-20261018`.
Separate X fallback fix: `640e82838b3348617605c88386cd520573989f5e`. Reconciliation: `acec92e985d1c6a6ef46e3cbcd86be9c7ce6ff4c`. Mobile presentation fix: `d30bcc0fa118e82f8580c2d428087876ba2b324b`.

The five new logical records are the Sungrow event (HTML/JSON representations), unchanged bounded snapshot, structured source provenance, supplemental review (three mirrored/projection copies), and reconciliation manifest. Necessary event ledger, exported event references, case discovery section, and sitemap entries were appended. Existing projection entries remain intact. Code, tests, and this audit report are not counted as new research records.

## Identity, time, and evidence boundaries

`SE-800V-REVIEW-20261017-SUPP-PR26-01` replaces the colliding review identity only in the new supplement and new event reference. Its provenance points to original PR #26's `SE-800V-REVIEW-20261017-01` at its immutable commit and path, while the existing main review with that ID remains byte-identical. Published daily reports, prior X candidates, case-state records, evidence snapshots, EKN freeze records, and workflows remain byte-identical among 2,459 protected files.

The source publication/event date remains `2026-10-15`; original first observation and snapshot capture remain `2026-10-17T14:04:05Z`. Reconciliation has a separate administrative timestamp and is explicitly not a new source review. The snapshot SHA256 remains `574c58de9d696546fed3f268b9fa02786e4a50ffe4e04616ddd0e06fdaf69f2a`. The certification claim remains attributed to Sungrow, with independent issuer authenticity/scope verification NOT_ESTABLISHED and no accepted stop transition.

Current official source access returns proxy tunnel 403; only the inherited, bounded PR #26 source review is preserved. No fresh retrieval or independent issuer verification is asserted. The supplemental stream is not recounted into the existing October 17 daily report.

## Validation

- Protected-record and provenance tests: 6/6 PASS, including 2,459 original file hashes and append-only checks for old projection entries.
- X fallback: 4/4 PASS. Before the fix, preferred-template-only configuration raised `KeyError: method_test_text` due to eager evaluation of the fallback argument. Legacy and preferred templates remain supported; missing both fails closed. Human-review and website-first publication gates remain unchanged; historical candidate records are not regenerated.
- Selected publication/operational regression checks: 53/53 PASS plus both standalone Irkutsk checks. Event publication-gate tests: 9/9 PASS. Both Worker suites: 58/58 PASS.
- Comprehensive clean-snapshot regression at `acec92e985d1c6a6ef46e3cbcd86be9c7ce6ff4c`: 112 Python test files, 73 pass, 38 fail, one fixture setup failure. Frozen main: 110 files, 71 pass, the same 39 nonpassing files. No new per-file exit failures or unittest failure identities appear. The later mobile-only correction was followed by 15/15 focused tests and all browser checks. Existing failing historical/fixture checks remain unresolved; this is not a full-suite PASS.
- Export drift, internal links, root/docs mirrors, source hashes, event index, unchanged review-index generation, strict HTML5, unique sitemap entries, and EKN publication invariants: PASS.
- Local deployment/browser validation: both serving roots, event page and case index, 320/375/768/1440 px: 16/16 PASS with no page overflow or JavaScript errors. Long source identifiers wrap inside the new page.
- Production GET validation for page, event JSON, snapshot, and source JSON: all blocked by proxy tunnel 403. No production deployment receipt was fabricated.

GitHub protection/PR API requests return `Forbidden`. A new draft PR cannot currently be created or its repository/human gates inspected through the available API. The branch is prepared for review; original PR #26 is unchanged. The remaining baseline failures and unavailable approvals prevent merging. No merge, production deployment, X post, automatic publication authorization, or EKN research change was performed.

The local receipt archive contains full command outcomes, before/after fallback logs, protected hashes, browser output, and production access results.

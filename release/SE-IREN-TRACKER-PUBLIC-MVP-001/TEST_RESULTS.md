# Test results

Run date: `2026-10-28` Asia/Singapore.

| Suite | Result |
| --- | --- |
| `python3 -B scripts/test_iren_public_tracker.py` | 15/15 PASS |
| `python3 -m unittest tests.test_history_immutability tests.test_seo_surface` | 10/10 PASS |
| `git diff --check` | PASS |
| Local reference integrity | 64 references, 0 missing |
| Local route / JSON / missing path | 200 / 200 / 404 |
| `.com` Verify / Decision Pack read-only HEAD | 200 / 200 |

New regression count: `0` in the targeted suites above. Full repository discovery reports 31/42 passing and 11 pre-existing failures. Eight are stale protected-file hashes and one is a stale case-index projection hash in `tests.test_pr26_append_only`; two assertions expose the pre-existing root/docs case-index mirror mismatch in `tests.test_ekn_publication` and `tests.test_pr26_append_only`. Every failed path is untouched by this branch. They are not reclassified as new regressions, but the stale baseline and mirror mismatch remain release blockers for any workflow that runs full discovery. Hosted CI remains pending until the Draft PR run.

The untouched paths reported by the stale baseline are `CONTRIBUTING.md`, `data/ops/se/ledger.jsonl`, `docs/case-watch/REVIEW_FRESHNESS_CONTRACT.md`, `docs/method-contract.json`, `docs/method.html`, `method-contract.json`, `method.html`, `scripts/test_cml_v11_transition.py`, and the pre-existing `cases/index.html` projection hash. The untouched root/docs case-index mismatch is asserted by two tests.

The IREN suite includes adversarial checks for a false customer-acceptance inference, Horizon 2–4 target/completion conflation, ARR/GAAP/cash conflation, incomplete retrieval promotion, unsafe challenge parameters, duplicate/broken event digests, private-handle leakage, untranslated hreflang, and production Worker drift.

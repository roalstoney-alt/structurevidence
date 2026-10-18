# PR #28: 800vdc schema audit

BASELINE_RESULT = FAIL_PREEXISTING_SCHEMA_EXPORT_MISMATCH
PR_RESULT = FAIL_BEFORE_FIX; PASS_AFTER_FIX_FOR_EXACT_TEST
FIX_SHA = 0c1877b36506a735cb4a8b9c0784bd9be971bd52
READY_TO_MERGE = NO

## Reproduction and diagnosis

Frozen main `d435fe84144f13391a2a66fca8d0f1fe01c861d6` and original PR head `1b30e917d7a975151490efbef3be5035095a5b23` both exit 1 for:

```sh
python -m unittest -v tests.test_public_record_export.PublicRecordExportTest.test_case_json_schema
```

The assertion at `tests/test_public_record_export.py:32` is `self.assertEqual(list(validator.iter_errors(record)), [], slug)`.
The actual error is `Additional properties are not allowed ('events' was unexpected)`.
Schema: `schemas/case.schema.json`, JSON path `$.additionalProperties`, actual value `false`.
Instance: `cases/800vdc/index.json`, JSON path `$`; its unexpected `events` array contains the existing SolarEdge OCP event summary, including `classifications=["NEW_EVENT","NO_STATE_CHANGE"]`, `state_changed=false`, `published_at="2026-10-13"`, `event_at="2026-10-12/2026-10-15"`, and `retrieved_at="2026-10-15T15:28:53Z"`.
Full actual values and hashes are recorded in the adjacent JSON.

Both revisions have identical schema SHA256 `42a059026cf60162aa42bffbfb82f9069e8bb012fb8f8803b6d1958686f17bc8` and record SHA256 `05bdf034cc79b67eb5fa2258d6f08d544f89e2938a816620c184855aa7ed50b8`.
The exporter already deliberately copies this summary from `cases/800vdc/events/index.json`; the schema omitted the legitimate optional field. This mismatch predates PR #28.

## Minimal correction and preservation

The fix defines the optional event-summary array, requires every existing identity/provenance field, validates field types and supported date formats, and rejects unknown event properties. `event_at` permits the existing date interval. Existing required fields and top-level `additionalProperties=false` remain intact. The original failing assertion is unchanged; a new negative test rejects malformed/missing summary fields. No test is weakened, skipped, or removed.

The accepted state remains `HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE`, as of `2026-09-20T10:46:47Z`, last material change `2026-09-20`. All 81 tracked files in root cases and all 81 in docs cases are byte-identical to the original PR head, including every evidence record, event ledger, snapshot, frozen EKN conclusion, and source reference. No monitoring workflow is changed by this fix.

## Validation and outstanding gates

- Exact original test and all four public-record tests: PASS.
- Publication/SEO tests: 8/8 PASS. Selected Python regression checks: 53/53 PASS, plus both standalone Irkutsk checks.
- Comprehensive Python inventory: 110 test files attempted independently from clean fixed snapshots; 71 pass, 38 fail, and one fails class setup because `data/open-intent-lab/genesis-001/outreach/human-review-prep.json` is absent. This setup error executes zero tests and is not counted as a pass or skip.
- Frozen main comparison: 109 files attempted; 69 pass, the same 39 files are nonpassing, plus the schema failure resolved here. No new unittest failure identities appear. These old failures remain unresolved; no blanket full-suite success is claimed. Full per-file commands and outcomes are in the adjacent JSON.
- Both local Worker suites: 31 + 27 = 58/58 PASS, with zero skipped tests.
- Public exports, drift, internal links, case-index regeneration, root/docs parity, strict HTML5 parsing, JSON/state invariants, unique sitemap URLs, and whitespace checks: PASS. All 12 supplied package manifest entries reverified.
- Chromium root and docs articles at 320, 375, 768, 1440 px: no page-width overflow or JavaScript errors. The code block scrolls inside its container at narrow widths. Automated accessibility has zero violations; manual-review incomplete items remain.
- Citation GET checks: four GitHub references return HTTP 200; six arXiv URLs and one DOI remain blocked by the network proxy. This is an access limitation, not citation revalidation success.

PR #28's head was verified through native Git at the fix SHA. GitHub API requests return `Forbidden`, so current required-check/review status cannot be inspected and a PR comment cannot be posted through the API. This committed audit record updates the PR through its branch. No merge or deployment was performed. Remaining regression failures and unavailable remote approval/check evidence prevent a ready-to-merge claim.

G0b_DECISION=HOLD_NEEDS_EVIDENCE; NOVELTY_STATUS=NOT_ESTABLISHED; G0c_EXECUTED=NO; G1_AUTHORIZED=NO; PAID_EXPERIMENT_RUNS=0; INDEPENDENT_REPRODUCTIONS=0; OUTREACH_SENT=0; EKN_DEPLOYED=NO.

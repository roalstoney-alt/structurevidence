# StructEvidence Gravity Layer v0.1 — Execution Report

```text
PROJECT =
STRUCTEVIDENCE_GRAVITY_LAYER_v0.1

BASELINE_SHA =
82314541f563d7f2fe9243197145758914fe036a

FINAL_SHA =
fd0d99009d3ae132ee90d7d552f27bc8e1a8e517

GOOGLE_FOUNDATION =
PASS

GITHUB_VERIFICATION_LAYER =
PARTIAL

CANONICAL_CASES =
2

MACHINE_READABLE_CASES =
2

CITABLE_EVIDENCE_RECORDS =
6

SITEMAP =
PASS

ROBOTS =
PASS

STRUCTURED_DATA =
PASS

INTERNAL_LINK_GRAPH =
PASS

PUBLIC_RECORD_DRIFT =
PASS

RSS =
PASS

EVIDENCE_SUBMISSION =
PASS

SEARCH_CONSOLE =
NOT_AVAILABLE

NEW_TESTS =
6/6

FULL_TEST_SUITE =
279/305

PRODUCTION_SMOKE =
PASS

HUMAN_ACTION_REQUIRED =
5

REPOSITORY_CLEAN =
YES

READY_FOR_GRAVITY_OBSERVATION =
NO
```

## Deployment status

- GitHub Pages run `36804436029`: `SUCCESS` for implementation commit `fd0d99009d3ae132ee90d7d552f27bc8e1a8e517`.
- Required production routes returned HTTP 200 after deployment.
- Production metadata, JSON-LD, machine-readable flagship record, and Atom feed checks passed.
- Desktop and 390 px mobile renders completed in headless Chrome; no horizontal mobile overflow was detected.
- Cloudflare Worker `structevidence-commercial`: latest observed deployment `fca44780-555b-4923-9722-51ebfe568a3a`, version `24efd0bc-0e0d-430d-b200-84f5191bc470`, 100% traffic; `https://structevidence.com/` returned HTTP 200. The Worker was not changed by this project.

## Gate detail

- `ORPHAN_PAGE_COUNT = 0`
- `BROKEN_INTERNAL_LINK_COUNT = 0`
- `CASE_WITHOUT_STATE_COUNT = 0`
- `EVIDENCE_WITHOUT_PARENT_COUNT = 0`
- `PUBLIC_RECORD_DRIFT = PASS`
- Agent-discovery generated outputs: current, 70 artifacts.
- Existing case-watch validation: 9/9 groups passed.
- Existing Cloudflare commercial tests: 14/14 passed.

The broad historical Python suite ran 305 tests: 279 passed, 23 failed, and 3 errored. The failures are classified as baseline-sensitive or pre-existing: several old milestone tests intentionally reject any later tracked-file change; other failures already reflect historical CML mutation assertions, an older metadata expectation, and a legacy homepage CTA expectation. The new gravity tests, deterministic export, current case-watch gates, link audit, drift check, JSON/XML parsing, commercial tests, and production smoke checks all pass.

## Partial / not-ready rationale

The GitHub verification layer remains partial because repository topics, social preview, and final license metadata require human decisions. Search Console access was unavailable. `READY_FOR_GRAVITY_OBSERVATION` remains `NO` until at least one external discovery path is observed without direct promotion and recorded in `SEARCH_DISCOVERY_LOG.csv`.

No private evidence, customer intake data, or admin information was exported. No evidence ID or frozen research conclusion was changed.

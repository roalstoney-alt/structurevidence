# SE-IREN-DDR-ENTRY-REMEDIATION-001 — Remediation report

Date: 2026-10-28 (Asia/Singapore)

Scope: repair Draft PR #60 without merging, deploying, submitting production customer data, or changing Worker/D1.

```text
PROJECT = SE-IREN-DDR-ENTRY-REMEDIATION-001
PR_NUMBER = 60
LOCKED_PR_HEAD_BEFORE = 7a28c862e801c7e78dca51693822740ef7d3301b
MAIN_SHA = b10d3f54ed320e773842bbe3c7d85156abb99a94
PR_STATE_REQUIRED = DRAFT
CANONICAL_SOURCE = scripts/build_iren_public_tracker.py
GENERATED_ROOT = cases/iren-ai-cloud-transition/index.html
GENERATED_PUBLISH_COPY = docs/cases/iren-ai-cloud-transition/index.html
GENERATED_PAGE_SHA256 = ef0136898b5994201e04d44a13f566aaf8b244121d0e1f220f544b62785cc5c8
SOURCE_GENERATION_CONSISTENCY = PASS
DDR_CTA = https://structevidence.com/decision-pack/?case=SE-IREN-AI-CLOUD-001
CASE_REFERENCE_PROTOCOL = PASS_STATIC
CASE_REFERENCE_EXPECTED_VALUE = SE-IREN-AI-CLOUD-001
CASE_REFERENCE_BROWSER_RUNTIME = NOT_OBSERVED
DESKTOP_BROWSER = NOT_OBSERVED
MOBILE_BROWSER = NOT_OBSERVED
KEYBOARD_BROWSER = NOT_OBSERVED
CTA_BROWSER_NAVIGATION = NOT_OBSERVED
IREN_TESTS = 17/17 PASS
HISTORY_AND_SEO = 12/12 PASS
CASE_REVIEW_STATUS = 6/6 PASS
PUBLIC_RECORD_DRIFT = 4/4 PASS
HISTORY_GUARD = PASS
INTERNAL_LINK_AUDIT = PASS, 0 issues
GIT_DIFF_CHECK = PASS
EVIDENCE_FILES_CHANGED = NO
NEW_REGRESSION_COUNT = 0
MERGED = NO
DEPLOYED = NO
PRODUCTION_POST = NO
WORKER_D1_CHANGED = NO
SOCIAL_PUBLISH = NO
```

## Remediation

The DDR section was moved into the canonical page template in `scripts/build_iren_public_tracker.py`. The builder now generates the same byte-identical page into both the root case path and the `docs/` publishing projection. Re-running the builder produced the same SHA-256 and did not create additional changes.

The DDR CTA now sends only the fixed public identifier through the existing supported query key:

```text
case=SE-IREN-AI-CLOUD-001
```

The current `.com` client script reads `params.get("case")`, creates a hidden `case_reference` field, and includes that field in the private request payload. The endpoint returned HTTP 200 and the source-level protocol check resolved the expected fixed value. No form was submitted and no production record was created.

## Browser observation boundary

The real in-app browser again timed out while enabling focus emulation for the existing localhost tab. Desktop layout, mobile viewport, keyboard navigation, and live CTA navigation are therefore recorded as `NOT_OBSERVED`, not PASS. Static HTML, accessibility hooks, responsive source, link structure, and tests passed, but they are not represented as substitutes for the missing browser observation.

## Evidence boundary

No tracker JSON, evidence cutoff, row state, source registry, event ledger, historic correction, Worker, D1, other case, or production endpoint was modified.

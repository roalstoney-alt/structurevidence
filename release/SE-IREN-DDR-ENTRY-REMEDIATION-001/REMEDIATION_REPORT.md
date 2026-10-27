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
CASE_REFERENCE_BROWSER_RUNTIME = PASS_LOCAL_PREVIEW
DESKTOP_BROWSER = PASS_LOCAL_PREVIEW, 1440x1000
MOBILE_BROWSER = PASS_LOCAL_PREVIEW, 390x844
KEYBOARD_BROWSER = PASS_LOCAL_PREVIEW, TAB_REACHABLE_AND_ENTER_ACTIVATED
CTA_BROWSER_NAVIGATION = PASS_LOCAL_PREVIEW
BROWSER_RETRY_2026_10_28 = PASS_LOCAL_PREVIEW
PRODUCTION_BROWSER = NOT_RUN
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

After the prior tabs were closed, a fresh in-app browser tab was created for the local preview and the preview endpoint returned HTTP 200. The in-app browser controller still timed out while enabling focus emulation before either the DOM or accessibility tree could be observed, including after switching the browser to background mode and retrying the fresh tab.

The acceptance was then completed against the same local `docs/` preview with the installed Google Chrome in headless mode through Playwright. This was a real browser run, not a static-source substitute. At 1440x1000 and 390x844 the DDR module and CTA were visible, horizontal overflow was 0 px, and no browser-console errors were recorded. The four evidence-block headings and Challenge section remained present. Sequential Tab navigation reached the DDR CTA after 81 Tab presses; Enter activated it and navigated to the exact `.com` Decision Pack URL. The destination page created `case_reference=SE-IREN-AI-CLOUD-001`. No form was submitted.

These results are recorded as `PASS_LOCAL_PREVIEW`. They do not claim production deployment or production-page acceptance; `PRODUCTION_BROWSER` remains `NOT_RUN` while the PR remains Draft.

## Evidence boundary

No tracker JSON, evidence cutoff, row state, source registry, event ledger, historic correction, Worker, D1, other case, or production endpoint was modified.

# Paid-Readiness Test Report

Date: 2026-09-23

## PASS

- New paid-readiness UI suite: 7/7 tests passed.
- Targeted CML v1.1 + frozen L1 field-deployment + UI suite: 18/18 tests passed.
- Five primary routes and shared assets returned HTTP 200 in a local static-server check.
- All five pages parsed with valid heading entry order; every form control has an associated label; local fragment targets resolve.
- Root and `docs/` sitemaps parse successfully.
- Homepage CTA destinations match `/context/` and `/cases/800vdc/`.
- Approved state renders one observed deployment, PDRE full validation `NO`, five remaining unknown dimensions, and visible counter-evidence.
- Verify and Context required fields use native HTML validation.
- Optional file inputs are not rendered because the repository has no upload backend.
- Prohibited-claim and fabricated-price search returned no matches.
- `git diff --name-only -- technical-risk rdl timeline evidence research` returned no modified tracked evidence or methodology files.

## FULL DISCOVERY BASELINE

`python3 -B -m unittest discover -s scripts -p 'test_*.py'` ran 252 tests and reported 3 failures plus 2 errors.

- `test_cml_site_metadata` initially detected missing legacy metadata; the homepage metadata was updated and the test now passes.
- Two opportunity-validation baseline integrity failures and one Phase A history error relate to pre-existing untracked CML-FDE / opportunity-validation workspace changes, not paid-readiness files.
- `test_rdl_phase2_5_allocation.test_q_no_tracked_historical_mutation` treats any tracked homepage or sitemap change as baseline drift. It reports the four intentionally modified publication-shell files. No CML/RDL evidence artifact was changed.

No baseline hashes or historical records were altered to suppress these expected integrity signals.

## RESPONSIVE / ACCESSIBILITY

- CSS includes desktop, tablet (900px), and mobile (620px) layouts.
- Mobile layouts preserve evidence states, timelines, gap cards, and table access; technical tables use horizontal scrolling.
- Keyboard focus styles, skip links, semantic headings, explicit labels, `aria-live` form status, long-ID wrapping, and expandable details are present.
- In-app browser screenshot capture was unavailable because the local browser kernel exited during initialization. No screenshot is claimed.

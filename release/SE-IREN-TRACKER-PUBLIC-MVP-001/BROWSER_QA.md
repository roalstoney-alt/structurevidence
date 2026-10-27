# Local browser QA

Preview route: `http://127.0.0.1:8766/cases/iren-ai-cloud-transition/` (local-only; not a public URL).

## Accepted captures

- `screenshots/iren-tracker-desktop-1440x1200.png`: desktop hero, review hold, cutoff/check metadata, CTAs, and start of Block 1 visible.
- `screenshots/iren-tracker-mobile-500x900.png`: responsive navigation, wrapped headline, review hold, and single-column metadata visible at the mobile breakpoint.

## Non-release diagnostic capture

- `screenshots/iren-tracker-mobile-390x844.png`: Chrome headless on this host enforces a sub-500px layout viewport and crops the requested 390px bitmap. It is retained as a diagnostic, not accepted as evidence of a CSS failure or a release screenshot.

## Checks completed

- Local route returned HTTP 200.
- Public JSON route returned HTTP 200.
- Unknown route returned HTTP 404.
- All 64 local page references resolved to repository files.
- `https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001` returned HTTP 200 via read-only HEAD.
- `https://structevidence.com/decision-pack/?case_id=SE-IREN-AI-CLOUD-001` returned HTTP 200 via read-only HEAD.
- No production POST was sent.

Keyboard behavior is structurally supported by native anchors, a skip link, visible focus behavior inherited from the product stylesheet, and no scripted interception. Full assistive-technology testing remains a human release check.

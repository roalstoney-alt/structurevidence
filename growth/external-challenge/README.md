# SE-EXTERNAL-CHALLENGE-GROWTH-PILOT-001

Controlled, human-gated external validation package for the public IREN AI Cloud tracker.

This package creates:

- a deterministic daily public-safe evidence export;
- reusable X and LinkedIn evidence-card renders;
- a public challenge workbench and illustrative DDR sample on the IREN case surface;
- public-safe challenger research and five review-only invitation drafts;
- an append-only external feedback ledger contract and tests;
- a final owner review report.

Nothing in this package sends outreach, publishes social content, changes the production intake Worker, writes to D1, or updates the public tracker automatically.

## Build

```bash
python3 scripts/build_external_challenge_growth.py --date 2026-10-29
python3 scripts/build_iren_public_tracker.py
PLAYWRIGHT_MODULE=/Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
PLAYWRIGHT_BROWSER_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  /Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  scripts/render_external_challenge_cards.mjs

PLAYWRIGHT_MODULE=/Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
PLAYWRIGHT_BROWSER_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  /Users/roal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
  scripts/qa_external_challenge_site.mjs
```

## Validate

```bash
python3 -m unittest scripts.test_external_challenge_growth scripts.test_iren_public_tracker
```

`DO_NOT_PUBLISH=YES`

`OUTREACH_SENT=0`

`SOCIAL_POSTS_SENT=0`

Review [OWNER_REVIEW_REPORT.md](OWNER_REVIEW_REPORT.md), [COST_RUNTIME.md](COST_RUNTIME.md), and [FINAL_ACCEPTANCE_REPORT.md](FINAL_ACCEPTANCE_REPORT.md) before any owner-authorized merge, deploy, publication, or outreach.

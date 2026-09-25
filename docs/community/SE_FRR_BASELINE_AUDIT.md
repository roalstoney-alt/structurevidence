# SE-FRR-001 Phase 0 Baseline Audit

Audit date: 2026-09-25  
Phase: 0 — Baseline Freeze  
Repository: `roalstoney-alt/structurevidence`  
Branch: `main`  
Baseline SHA: `2356c9327ba5b40995435eca952edd706fd944fc`  
Remote comparison: `main` is 0 ahead / 0 behind `origin/main`

## Gate result

| Gate | Result | Evidence |
|---|---|---|
| `BASELINE_RECORDED` | YES | SHA, branch, remote and worktree state recorded here. |
| `REPOSITORY_CLEAN` | NO | Two tracked files are modified and eight untracked paths are present at audit entry. |
| `TEST_BASELINE_RECORDED` | YES | Python, Worker and Wrangler results are recorded below. |
| `NEXT_PHASE_READY` | NO | The workflow explicitly blocks production modification when the baseline worktree is unexpectedly dirty. |

No application, production, schema, or research artifact was modified during this audit. The only new files are the Phase 0 reports under `docs/community/`.

## Entry worktree

Tracked modifications present before Phase 0:

- `deploy/cloudflare-landing/test/intake.test.js`
- `deploy/cloudflare-landing/worker.js`

Untracked paths present before Phase 0:

- `carepathchina-update/`
- `docs/upgrade/cml-fde-v3.0/`
- `output/onepage/`
- `scripts/build_structurevidence_onepage.py`
- `scripts/build_structurevidence_onepage_dark.py`
- `scripts/test_cml_fde_v3.py`
- `stoneyrola-update/`
- `technical-risk/cml-fde-v3.0/`

The two tracked modifications add an `/admin` redirect and corresponding tests. They were not created, changed, reverted, staged, or committed by this audit.

## Repository baseline

- One tracked production branch was found locally: `main`.
- One tracked remote production branch was found: `origin/main`.
- The repository contained 1,882 tracked files at audit time.
- Public site content is file-backed HTML/CSS/JS with a Cloudflare Worker commercial plane.
- Canonical evidence/research artifacts are file-backed JSON/Markdown with JSON Schema and validation scripts.
- Customer request data is stored separately in Cloudflare D1.
- No Discord bot application or Discord infrastructure is present.

## Test baseline

### Python suite

Command:

```text
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Result:

```text
Ran 269 tests in 97.211s
FAILED (failures=14, errors=2)
253 passed
```

Failure groups:

1. Frozen baseline checks detect historical changes in `scripts/publish_cml_v01.py` and `technical-risk/request-analysis/index.html`.
2. Opportunity Validation baseline-integrity gates fail against their recorded baseline commits.
3. The CML PDRE initialization test finds the later-added `publication-control.json` and its URL, although the older test expects the original container shape.
4. One RDL allocation freeze test detects the two current uncommitted Cloudflare Worker files.

The suite also emitted `jsonschema.RefResolver` deprecation warnings. These are warnings, not test failures.

### Cloudflare Worker tests

The first `pnpm test` attempt could not find a system `node`. The suite was rerun with the Codex bundled Node.js runtime.

```text
14 tests; 14 passed; 0 failed
```

### Wrangler dry-run

The first `pnpm run check` attempt could not find a system `node`. It was rerun with the bundled Node.js runtime.

Wrangler completed the dry-run bundle successfully and reported:

- Worker bundle: 117.09 KiB, gzip 29.85 KiB
- D1 binding: `CUSTOMER_CASES_DB`
- rate-limit binding: `PUBLIC_INTAKE_RATE_LIMITER`
- environment variables: `PUBLIC_ORIGINS`, `TEAM_DOMAIN`

Wrangler could not write its debug log under `~/Library/Preferences/.wrangler/logs` because the audit sandbox does not permit that path. The command still exited successfully and did not deploy.

## Existing security and privacy boundary

- Public request submission is size-limited, content-type checked, field-allowlisted, normalized, origin-restricted, and rate-limited.
- Admin UI and APIs validate Cloudflare Access issuer, audience, token, email, and allowlist; missing configuration fails closed.
- D1 queries use prepared statements.
- Customer requests default to `CUSTOMER_PRIVATE` and `NOT_AUTHORIZED`.
- Request events are append-only at the database layer via update/delete triggers.
- No private upload endpoint exists.
- No production secret was read or written during Phase 0.

## Baseline conclusion

The repository has a strong provenance, temporal-state, verification, and customer-intake foundation. The test baseline is not green and the worktree is not clean. Phase 1 implementation must not begin on this checkout until the human owner decides how to preserve or finalize the pre-existing changes and the frozen-baseline regressions are triaged.

# SE-DUAL-SITE-UPGRADE-002 / Phase E — GitHub Pages deployment audit

Observed: 2026-10-25T13:47:17Z. Read-only inspection only; no Pages setting, workflow, deployment, cache, DNS, or production file was changed.

## Result

`MAIN_SHA_95219314309e01af6bf4042831b2bf4ba18fbc02_PUBLISHED = VERIFIED`

GitHub Actions run [40198754542](https://github.com/roalstoney-alt/structurevidence/actions/runs/40198754542), run number 187, is the GitHub-managed `pages build and deployment` workflow at `dynamic/pages/pages-build-deployment`. It started three seconds after the main commit, completed successfully, and identifies:

- `head_branch`: `main`
- `head_sha`: `95219314309e01af6bf4042831b2bf4ba18fbc02`
- `event`: `dynamic`
- build job: success
- deploy job / `Deploy to GitHub Pages`: success

The build log independently records checkout `ref: main`, checked-out SHA `95219314309e01af6bf4042831b2bf4ba18fbc02`, and `actions/upload-pages-artifact@v3` with `path: .`. The effective Pages source is therefore the `main` branch repository root. It is not `docs/`, and it is not a repository-authored custom Pages workflow.

The Settings > Pages administration endpoint was unavailable to the connected read-only GitHub integration, so the settings UI field itself is `UNVERIFIED`. That limitation does not obscure the effective source above: the successful managed run and build log expose branch and artifact path directly.

## Live-byte verification

The target commit introduced `docs/implementation/SE-DUAL-SITE-002-PHASE-D-HASHES.json`. The live URL returned HTTP 200 from `server: GitHub.com`, with `last-modified: Sun, 25 Oct 2026 13:41:44 GMT`.

| Artifact | Git object at target SHA | Live .org bytes |
|---|---|---|
| `docs/implementation/SE-DUAL-SITE-002-PHASE-D-HASHES.json` | `180be9ffe40acf35a7e2b341552caafc4673d7e4d98f9b2a45d6fde52eb3c24e` | `180be9ffe40acf35a7e2b341552caafc4673d7e4d98f9b2a45d6fde52eb3c24e` |

This commit-specific byte match, together with the successful deploy job for the exact SHA, verifies actual publication. A CNAME or HTTP 200 alone was not used as proof.

## Trigger and recent deployment history

The repository has no checked-in workflow that deploys Pages. GitHub invokes its managed dynamic Pages workflow when the configured source branch changes. The five latest Pages runs inspected were all successful:

| Run | Main SHA | Created UTC | Conclusion |
|---|---|---|---|
| 187 / `40198754542` | `95219314309e01af6bf4042831b2bf4ba18fbc02` | 2026-10-25T13:41:22Z | success |
| 186 / `40196119176` | `f267f9dbe506cb30f95a2f21543b72b4fc31c388` | 2026-10-25T13:06:40Z | success |
| 185 / `40178288549` | `bbced95da00ed259e942aa63ebd89d93f70c54a0` | 2026-10-25T08:51:32Z | success |
| 184 / `40156138854` | `f89f5dbba30c3f504833418d643786680d5769ca` | 2026-10-25T02:53:04Z | success |
| 183 / `40135828104` | `2ed24ed1d62394b8485fb175c083bcceca0618b0` | 2026-10-24T21:48:22Z | success |

## Approval implication

Merging PR #52 to `main` is itself expected to trigger a production `.org` Pages publication from the repository root. Owner merge approval must therefore also acknowledge this automatic publication effect. This PR does not change that setting or run a deployment.

`structevidence.com` remains a separate Cloudflare Worker deployment boundary. No Cloudflare command, write, or production deployment was performed.

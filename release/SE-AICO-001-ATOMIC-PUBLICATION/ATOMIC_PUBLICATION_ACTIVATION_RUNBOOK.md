# SE-AICO-001 atomic publication activation runbook

## Current gate

`PR_HEAD_INTEGRITY_ACCEPTED_MERGE_HOLD`. This runbook and its tooling are review material, not publication authority.

The verified GitHub Pages configuration publishes the repository root from `main` through GitHub's dynamic `pages-build-deployment` workflow. Every push to `main`, including a PR merge commit, starts a production Pages build. Therefore merge and deployment are operationally coupled and must be covered by one explicit owner decision.

## Atomicity finding

A deployment's success ID and actual public-availability time do not exist before the deployment succeeds. They cannot truthfully be embedded in the same static branch-source commit that triggers that deployment. A strict single-deployment transition from unpublished candidate to “live and verified” is therefore not achievable with the current branch-source Pages configuration.

Two truthful choices remain:

1. **Recommended strict gate:** change Pages to a controlled GitHub Actions artifact workflow, deploy an explicit activation artifact only after an owner-approved gate, and append the live-verification receipt after the environment reports success. Changing Pages configuration is itself a production action and requires separate owner authorization.
2. **Branch-source two-phase gate:** merge only after one decision explicitly authorizes both merge and automatic Pages deployment. Treat that first deployment as `DEPLOYED_PENDING_LIVE_VERIFICATION`, with no social or Agent outreach. After observing the actual successful deployment and live hashes, append the activation event and receipt in one repair commit. This is truthful but not a strict single-deployment activation.

Until the owner selects and authorizes one of those choices, PR #97 must remain unmerged.

## Required owner authorization

The activation generator accepts only the literal decision:

`APPROVE_ATOMIC_PUBLICATION_ACTIVATION_AND_AUTO_DEPLOY`

That decision must identify the exact final candidate HEAD and acknowledge that merging to `main` automatically triggers GitHub Pages. The current `PR_HEAD_INTEGRITY_ACCEPTED_MERGE_HOLD` decision is deliberately rejected by the tool.

## Pre-merge checks

1. Confirm the PR remains based on `64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554` or obtain a fresh owner review if `main` moved.
2. Confirm the exact final PR HEAD, clean changed-file inventory, root/docs mirrors, source digest and 15 frozen claim rows.
3. Run the scoped matrix and both PR checks. Report known baseline failures by identity.
4. Confirm no source capture, private review log, credential or personal path is in the PR.
5. Record the new explicit merge+automatic-deploy owner decision. Do not infer it from this runbook.

## Actual event capture

After the authorized Pages deployment reports success, populate `publication-activation-event-template-v0.2.json` only with observed values:

- final candidate and merge commit SHAs;
- owner authorization ID and UTC time;
- Pages workflow run, deployment and deployment-status IDs;
- Pages success timestamp, used as `publication_event_at`;
- HTTP 200 observations and SHA256 values for the canonical HTML, `index.json`, and claims JSONL;
- live-verification UTC timestamp;
- the carried-forward SEC source SHA256.

Do not use a planned time, commit author time, workflow start time or prospectus date as the publication event.

Generate the overlay:

```sh
python3 -B scripts/prepare_anthropic_publication_activation.py \
  --event /absolute/path/actual-activation-event.json \
  --output-dir /absolute/path/empty-activation-overlay
```

The generator rejects missing facts, the current merge hold, failed deployments, wrong URLs, wrong Pages source semantics, altered source hashes and out-of-order timestamps.

## Append-only projection

The overlay:

- leaves `claims-v0.2.jsonl` and `source-registry-public-v0.2.json` byte-identical;
- appends one `PUBLICATION_ACTIVATION_VERIFIED` event to `events-v0.2.jsonl`;
- adds `publication-current-state-v0.2.json` and an actual `publication-receipt-v0.2.json`;
- updates mutable current projections (`index.json`, JSON-LD, discovery adapter and review-status presentation);
- replaces the obsolete pending-review label with `OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION`;
- maintains byte-identical root/docs output pairs;
- writes a SHA256 activation manifest.

The original prepublication candidate remains recoverable at commit `f195d44e464e7c27c23d1a1eb5b9858687166dfc`; no earlier claim or source row is rewritten.

## Applying a verified overlay

Application is intentionally guarded. It requires a clean worktree whose HEAD equals the event's exact candidate SHA, and it refuses test fixtures:

```sh
python3 -B scripts/prepare_anthropic_publication_activation.py \
  --event /absolute/path/actual-activation-event.json \
  --output-dir /absolute/path/empty-activation-overlay \
  --apply-to /absolute/path/clean/repository
```

After application, inspect the full diff, rerun all gates, commit every projected file in one commit, and obtain any additional authorization required by the selected Pages strategy. Never force-push or rewrite the prepublication commits.

## Post-deploy verification

Verify all of the following before declaring publication complete:

- Pages deployment environment is `github-pages` and status is `success`;
- deployed SHA equals the authorized commit;
- canonical HTML, JSON, JSONL and source registry return HTTP 200;
- all 15 anchors resolve;
- live bytes match the receipt hashes;
- current metadata says `PUBLISHED_VERIFIED`, not `NOT_PUBLISHED`;
- the prior draft record and its SHA remain in Git history;
- cases index, sitemap and Agent discovery point to the verified live route;
- no social post or external Agent test runs without separate authorization.

## Stop conditions

Stop without activation if `main` moved, Pages source changed, any live byte hash differs, the deployment failed, the canonical route is not 200, the source digest changed, root/docs diverge, or owner authorization does not cover both merge and automatic deployment.

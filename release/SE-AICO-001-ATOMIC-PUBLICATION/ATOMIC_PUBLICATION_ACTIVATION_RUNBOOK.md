# SE-AICO-001 verifiable two-phase activation runbook

## Current gate

`HOLD_MERGE_AND_AUTO_DEPLOY`. This mechanism is review material only. It does not authorize a merge, push to `main`, Pages deployment, publication claim or social promotion.

GitHub Pages publishes repository root `/` automatically from `main`. A merge is therefore also a production-deployment action and requires one explicit owner authorization covering both effects.

## Corrected trust boundary

The verifier does not accept a caller-supplied decision string, IDs, timestamps or hashes as proof. In actual mode it must independently fetch and check:

- an immutable GitHub comment authored by repository owner `roalstoney-alt`, bound by GitHub `issue_url` to PR #97 and by exact comment-body SHA256;
- PR #97 head/base/merged state and GitHub-recorded merge result;
- current `main` HEAD and merge or squash topology;
- the exact native Pages run (`event=dynamic`, `path=dynamic/pages/pages-build-deployment`, `name=pages build and deployment`), Pages deployment and deployment-status objects;
- successful `github-pages` production status and its timestamp;
- HTTP 200 responses, final canonical URLs and SHA256 of raw bytes for canonical HTML, `index.json` and `claims-v0.2.jsonl`;
- the same three repository files fetched from GitHub Contents at the exact authenticated deployed SHA, with byte-for-byte live-to-tree equality and case/schema identity checks.

The production API origin is pinned to `https://api.github.com`; there is no production CLI origin override. Test transports and `test_fixture=true` records are rejected by the actual CLI gate. The authorization comment's effective update time must precede the PR merge time, which must precede the Pages workflow start.

## Phase 1 — owner-authorized initial deployment

The owner must first post a GitHub comment containing these exact lines, with the final reviewed HEAD substituted:

```text
CASE_ID=SE-AI-COMPUTE-OBLIGATIONS-001
PR_NUMBER=97
BASE_SHA=64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554
CANDIDATE_HEAD_SHA=<EXACT_REVIEWED_HEAD>
OWNER_DECISION=APPROVE_VERIFIABLE_TWO_PHASE_RELEASE_AND_AUTO_DEPLOY
MERGE_AUTHORIZED=YES
AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED=YES
SOCIAL_PUBLISH_AUTHORIZED=NO
NEXT_GATE=VERIFIABLE_ACTIVATION_OVERLAY_REVIEW
```

Record its GitHub comment ID and exact UTF-8 body SHA256 in `two-phase-owner-authorization-template-v0.3.json`. The verifier fetches the comment and requires GitHub `author_association=OWNER`; a copied local string is insufficient.

Only after that new authorization may PR #97 be merged. No such authorization exists at the current gate.

After the automatic Pages deployment, populate `initial-deployment-observation-request-template-v0.3.json` with the observed IDs and deployed SHA, then run:

```sh
python3 -B scripts/prepare_anthropic_publication_activation.py verify \
  --authorization /absolute/path/initial-owner-authorization.json \
  --request /absolute/path/initial-observation-request.json \
  --receipt-output /absolute/path/initial-pages-deployment-receipt-v0.3.json
```

The initial receipt preserves only initial-deployment hashes. It never presents them as hashes of a later overlay deployment.

## Phase 2 — prepare and separately authorize the overlay

Re-run the live verification while generating the overlay:

```sh
python3 -B scripts/prepare_anthropic_publication_activation.py prepare-overlay \
  --authorization /absolute/path/initial-owner-authorization.json \
  --request /absolute/path/initial-observation-request.json \
  --receipt-output /absolute/path/initial-pages-deployment-receipt-v0.3.json \
  --output-dir /absolute/path/empty-overlay \
  --source-root /absolute/path/clean-worktree-at-deployed-main \
  --apply-to /absolute/path/clean-main-worktree
```

The source root is mandatory. Its clean Git HEAD must equal the verified deployed `main` SHA, and every source file used to construct the overlay must equal `git show <deployed-sha>:<path>`. The apply target must independently have the same deployed HEAD. Merge and squash policies are both verified: merge requires candidate ancestry; squash requires the deployed tree to equal the authorized candidate tree.

The application is transactional. All inputs are hash-checked and all existing destinations are backed up before replacement. Any write or post-write verification failure restores every touched path. Inspect the diff, run all gates, and create one reviewable overlay commit. Do not push it yet.

The overlay is intentionally truthful and conservative:

- `DEPLOYED_PENDING_LIVE_VERIFICATION`;
- `datePublished=null` and no made-up publication time;
- `external_promotion_authorized=false`;
- initial deployment, activation-overlay deployment and final live verification occupy separate fields;
- frozen claims, source registry and SEC digest are unchanged;
- the initial deployment event is appended rather than rewriting prepublication history.

## Overlay deployment authorization and final observation

After reviewing the exact overlay commit, the owner must separately post:

```text
CASE_ID=SE-AI-COMPUTE-OBLIGATIONS-001
PR_NUMBER=97
BASE_SHA=64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554
CANDIDATE_HEAD_SHA=<ORIGINAL_REVIEWED_PR_HEAD>
OWNER_DECISION=APPROVE_ACTIVATION_OVERLAY_AND_AUTO_DEPLOY
INITIAL_DEPLOYED_SHA=<OBSERVED_INITIAL_MAIN_SHA>
OVERLAY_HEAD_SHA=<EXACT_OVERLAY_COMMIT_SHA>
MERGE_AUTHORIZED=NO
AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED=YES
SOCIAL_PUBLISH_AUTHORIZED=NO
NEXT_GATE=FINAL_LIVE_VERIFICATION
```

Only then may the overlay commit be pushed to `main`. After deployment, calculate expected hashes from the reviewed overlay files, populate `overlay-deployment-observation-request-template-v0.3.json`, and run `verify` again with the overlay authorization.

The resulting `SE-AICO-FINAL-LIVE-VERIFICATION-RECEIPT-v0.3` contains hashes fetched from the final live bytes. A wrong expected hash, fabricated ID, future deployment, unrelated HEAD or incomplete approval fails closed. The public state remains pending until a separately reviewed append-only finalization step; the verifier never prematurely emits `PUBLISHED_VERIFIED`.

## Stop conditions

Stop without merge, push or activation if any authorization field is missing, the comment is not on PR #97 or was finalized after merge, GitHub cannot be queried at the pinned origin, `main` moved, a SHA relationship fails, the native Pages workflow identity or source/environment differs, a deployment is unsuccessful or future-dated, a canonical resource is not HTTP 200, a final URL changes, live bytes differ from the exact deployed Git tree, the source worktree is on another commit or dirty, the source digest changes, root/docs diverge or any frozen record changes.

Never force-push, rewrite evidence history, infer authorization from this runbook or promote the case while the public state is pending verification.

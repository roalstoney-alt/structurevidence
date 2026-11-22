# SE-AICO-001 rollback and repair procedure

## Principle

Never delete or rewrite the prepublication evidence history. Repair current presentation through a new commit and append a corrective event/receipt. A Git revert is preferred to history rewriting.

## Before merge or deployment

If any check fails, do nothing to `main`. Keep PR #97 draft, record the failed gate, correct the branch and obtain a fresh review of the new exact HEAD.

The actual verifier must be able to retrieve the owner-authored GitHub authorization comment, PR topology, current `main`, workflow run, deployment/status objects and live bytes. A local JSON file, plausible ID or literal decision string is never sufficient authority.

## Local overlay application fails

The v0.3 applicator backs up every existing destination before replacing any file and restores all touched paths if a replacement or post-write hash check fails. After a reported failure:

1. run `git status --short` and confirm the worktree is clean;
2. compare every manifest destination with the pre-application HEAD;
3. do not commit or push a partially applied overlay;
4. retain the failure log and correct the applicator or input in a new reviewed branch commit.

If automatic rollback itself cannot be proven complete, discard that disposable worktree and create a clean worktree at the same deployed `main` SHA. Never use force-push or rewrite a shared worktree.

## Automatic Pages deployment fails

1. Do not create a successful publication receipt.
2. Record the workflow run and failed conclusion out of band.
3. Keep the public state at `DEPLOYMENT_FAILED_OR_UNVERIFIED`; do not set `datePublished`.
4. Repair on a new reviewed commit. Do not retry by force-pushing an unreviewed SHA.

## Route is live but bytes or semantics are wrong

1. Capture the actual deployment ID, affected URL, HTTP status and byte hashes.
2. Stop sitemap, Agent and social promotion.
3. Revert the activation commit with a normal revert commit, or apply a narrowly scoped repair commit if reverting would remove unrelated authorized work.
4. Let the revert/repair deploy through the same Pages trigger.
5. Verify the canonical route and record an append-only `PUBLICATION_REPAIR` or `PUBLICATION_ROLLBACK` event. The event must reference both the faulty and repairing commit/deployment IDs.
6. Preserve the original activation receipt; add a superseding receipt rather than editing it.

Initial deployment hashes, activation-overlay hashes and final live-verification hashes are separate immutable observations. Never copy an earlier deployment's hashes into the current-state fields after later bytes have been deployed.

## Metadata-only contradiction

If content is correct but current metadata says `DEPLOYED_PENDING_LIVE_VERIFICATION`, do not relabel it as published from an earlier receipt. Observe the activation-overlay deployment, verify current raw live bytes, write a separate final-live-verification receipt, and obtain review of any append-only public finalization commit.

## Source or evidence integrity failure

If any reviewed claim row, source registry byte or source SHA changes unexpectedly:

1. stop publication immediately;
2. revert to the last verified commit;
3. compare against `f195d44e464e7c27c23d1a1eb5b9858687166dfc` and source digest `0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b`;
4. do not regenerate or normalize the SEC source as part of repair;
5. require a new evidence-integrity review before any redeployment.

## Repair receipt minimum fields

- event ID and type;
- observed fault and detection time;
- faulty commit, workflow run and deployment IDs;
- repair/revert commit, workflow run and deployment IDs;
- canonical URLs and before/after byte hashes;
- owner authorization covering the repair deployment;
- explicit statement that historical claim/source rows were not rewritten.

`git reset --hard`, force-push, receipt deletion and backdated timestamps are prohibited.

# SE-AICO-001 owner deployment gate correction v0.4

## Scope

This append-only correction addresses P0-1 through P1-5 in the owner deployment gate review of exact HEAD `d89b8a5787ed44b4016dd301215620bd4744a436`. It does not alter financial research, frozen claim rows, the public source registry, the SEC digest, prior evidence events or prior review receipts.

## P0-1 — actual native Pages workflow

The verifier now requires the observed GitHub-managed Pages identity: `event=dynamic`, `path=dynamic/pages/pages-build-deployment`, `name=pages-build-deployment`, `head_branch=main`, successful completion, authenticated deployed SHA and matching Pages deployment/status objects. Arbitrary Actions events or paths fail closed.

## P0-2 — pinned production API origin

Production is pinned to `https://api.github.com`. The CLI exposes no API-origin option. A custom origin is accepted only when the client is explicitly constructed in isolated test mode, which marks it as a test transport; test transports cannot emit an actual-mode receipt. Token headers are never constructed for a rejected production origin.

## P0-3 — live bytes bound to deployed Git

For canonical HTML, `index.json` and `claims-v0.2.jsonl`, the verifier fetches live status, final URL and bytes, then independently fetches the corresponding repository file through GitHub Contents at the exact verified deployed SHA. It requires byte equality, records repository path/blob/SHA256 and checks case identity, schema shape and 15 claim rows. Stale HTTP-200 and mismatched tree bytes fail closed.

## P1-4 — authorization bound to PR and pre-merge time

The owner comment must have GitHub `issue_url` for PR #97. The effective comment update time must satisfy `authorization <= merged_at <= native Pages workflow start <= deployment success`. A different issue or post-merge authorization fails closed.

## P1-5 — overlay source bound to deployed main

`prepare-overlay` requires an explicit source root. Its clean HEAD must equal the verified deployed `main` SHA, and every file used to build the overlay must equal the Git object at `<deployed-sha>:<path>`. The apply target separately must be clean and at the same deployed SHA.

## Controls

The intermediate state remains `DEPLOYED_PENDING_LIVE_VERIFICATION`; no automatic `PUBLISHED_VERIFIED` transition was introduced.

`MERGE_AUTHORIZED=NO`

`AUTOMATIC_DEPLOYMENT_AUTHORIZED=NO`

`SOCIAL_PUBLISH_AUTHORIZED=NO`

`NEXT_GATE=OWNER_APPROVAL_OF_CORRECTED_VERIFIABLE_DEPLOYMENT`

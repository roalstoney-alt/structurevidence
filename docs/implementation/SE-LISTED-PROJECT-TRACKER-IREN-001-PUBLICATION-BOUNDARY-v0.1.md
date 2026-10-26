# SE-LISTED-PROJECT-TRACKER-IREN-001 — publication-boundary remediation v0.1

Status: engineering remediation complete in Draft PR #53; merge, deployment and public pilot remain unauthorized.

## Outcome

The repository is public. Repository visibility and Pages visibility are two independent disclosure paths:

1. A file committed to any reachable commit or PR branch is already readable through GitHub, even if it is never deployed to Pages.
2. The verified GitHub-managed Pages workflow checks out `main` and passes repository root `path: .` to `actions/upload-pages-artifact@v3`. Non-hidden files are therefore artifact candidates except `.git` and `.github`.

The nine files formerly under `research/internal/listed-projects/iren/`, the pilot handoff and the builder containing the complete embedded draft payload were classified `INTERNAL_DRAFT_NOT_APPROVED_FOR_PUBLICATION`. They are absent from the remediated HEAD. Their exact historical SHA-256 values remain in the adjacent machine-readable manifest and the original v0.1 hash receipt; no source or evidence record was silently rewritten.

This prevents those files from entering the Pages artifact if the remediated HEAD is later merged. It does **not** erase their earlier public-repository exposure at commit `51bdf7831fe0682c2e709074448cb7704f6a9e46`. No history rewrite was performed because the correction is append-only. The reviewed payload contained public-source-derived working records and no identified customer data, credentials, personal data or proprietary source bytes.

## Classification

- `PUBLIC_SAFE`: reviewed as safe for a public repository and Pages artifact. This label does not grant merge or publication approval.
- `INTERNAL_DRAFT_NOT_APPROVED_FOR_PUBLICATION`: working material that may be shared only through an authenticated review store until an explicit release decision.
- `PRIVATE_RESTRICTED`: client, credential, contractual, personal, security-sensitive or otherwise restricted material. It is never permitted in this repository or its Pages artifact.

All nine IREN draft output files were classified `INTERNAL_DRAFT_NOT_APPROVED_FOR_PUBLICATION`. No current file was classified `PRIVATE_RESTRICTED`; that is a data-boundary result, not permission to publish the internal drafts.

## Why common hiding techniques do not work

- A directory named `internal` is only a path component.
- `.gitignore` prevents some accidental additions but is not an authorization system and has no effect on already tracked objects. The protected baseline file is deliberately unchanged; the regression guard rejects any future tracked IREN draft path directly.
- `robots.txt` and HTML `noindex` are crawler requests, not authentication or confidentiality controls.
- `.nojekyll` disables Jekyll processing; it does not restrict reads. With the root artifact, it makes static repository paths more directly deployable.
- Removing navigation or sitemap entries does not make a predictable URL private.

## Actual Pages paths that would have been public

At commit `51bdf7831fe0682c2e709074448cb7704f6a9e46`, every non-hidden path in `research/internal/listed-projects/iren/` was eligible for direct publication at:

`https://structurevidence.org/research/internal/listed-projects/iren/<filename>`

The handoff and payload-bearing builder were likewise eligible under `/docs/implementation/...md` and `/scripts/...py`. The exact per-file URLs and historical hashes are recorded in the adjacent JSON manifest.

## Real access-control design

The proposed internal-draft store is a **separate private GitHub repository** with Pages disabled, an explicit collaborator/team allowlist, 2FA/SSO where available, branch protection and audit logging. Only an approved public-safe export and its digest may cross into this public repository.

`PRIVATE_RESTRICTED` material requires a stricter boundary: a private object bucket with public access disabled and encryption at rest, reachable only through an authenticated Cloudflare Access-protected Worker using least-privilege identity or service-token allowlists, short-lived downloads and access logs. Private customer data must not be copied into Git commits, PRs, Actions artifacts, Pages artifacts or public hash manifests that disclose sensitive metadata.

These stores are proposed but were not provisioned by this PR. Provisioning needs owner authorization, identity/retention decisions and a security review.

## Source-byte integrity

Nine SEC sources remain `RAW_CAPTURE_FAILED`. Their source-byte SHA-256 values remain `null`. Browser-readable parsed text, URL metadata, source-record digests and derived packet hashes are not substituted for original-byte hashes.

## Remaining merge gates

1. Owner accepts that merging to `main` automatically publishes every remaining public-safe, non-hidden root file through Pages.
2. Owner selects and provisions the authenticated internal review store before regenerating or relocating the IREN draft payload.
3. A real human reviewer approves any separately prepared public-safe tracker release.
4. Legal/editorial review remains required before investor-facing personalization, paid access or pilot activation.

No merge, deployment, history rewrite, public-pilot activation or external outreach was performed.

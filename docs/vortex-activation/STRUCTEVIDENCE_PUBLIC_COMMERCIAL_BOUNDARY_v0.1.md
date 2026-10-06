# StructEvidence Public / Commercial Boundary v0.1

BOUNDARY_ID = STRUCTEVIDENCE_PUBLIC_COMMERCIAL_BOUNDARY_v0.1  
VERSION = v0.1  
FROZEN_AT = 2026-10-06  
STATUS = FROZEN

## 1. Purpose

Public evidence challenge and commercial verification are separate user journeys. A person is never required to become a commercial lead, request a quote, define a paid scope, or enter a sales funnel in order to challenge a public evidence boundary.

## 2. Domain roles

- `structurevidence.org` owns public research, public cases, Open Evidence Gap discovery, and the public challenge user experience.
- `structevidence.com` owns commercial verification and paid decision work. It also remains the sole owner of the canonical machine Gap API and challenge write backend.

No second database, challenge state machine, or canonical Gap API is created on `.org`.

## 3. Public challenge journey

1. A reader starts from `https://structurevidence.org/cases/{case}/`.
2. The primary evidence CTA is **Challenge this gap** and points to `https://structurevidence.org/gaps/{gap_id}/`.
3. The `.org` Gap page shows the frozen claim boundary, evidence cutoff, qualifying examples, and non-qualifying examples.
4. The form posts directly to `https://structevidence.com/api/gaps/{gap_id}/challenge`.
5. A successful submission returns a challenge identifier and `state = SUBMITTED`.
6. Human review is required before any public outcome or state change.

Challenge submission requires no payment, sales qualification, customer conversion, quote request, or commercial verification request.

## 4. Commercial journey

`https://structevidence.com/verify/` remains a separate paid decision-verification path. It collects decision context, a bounded claim or question, deadline, requested output, and commercial scope. It is not required to correct or challenge a public evidence record.

On public case pages the commercial CTA may appear only as a lower-priority secondary action, such as **Need this evaluated for your decision?**

## 5. Canonical API ownership

- Gap registry: `https://structevidence.com/api/gaps`
- Gap detail: `https://structevidence.com/api/gaps/{gap_id}`
- Challenge write endpoint: `https://structevidence.com/api/gaps/{gap_id}/challenge`

The `.org` pages expose alternate JSON metadata pointing to these endpoints. They do not expose a competing `.org` API.

## 6. CTA hierarchy

- Primary public-case CTA: **Challenge this gap** → `.org/gaps/{gap_id}/`
- Secondary public-case CTA: **Need this evaluated for your decision?** → `.com/verify/`
- Prohibited public evidence CTA: **Verify this gap**

CHALLENGE SUBMISSION != COMMERCIAL VERIFY REQUEST.

## 7. Data and privacy boundary

- Raw submissions are private/internal.
- Review events are internal and append-only.
- Public projection contains only a human-reviewed summary.
- Raw submitted text, contact email, hidden identity, reviewer notes, private materials, and patient-identifiable information are never published automatically.
- A public outcome may show review outcome, a bounded reason summary, whether state changed, and attribution only when authorized.

Public attribution is optional. Attribution means evidence contribution only and does not imply endorsement of StructEvidence's final conclusion.

## 8. No-auto-state-change rule

Submission does not automatically change a claim, Gap, stop point, or case state. A challenge begins in `SUBMITTED`. Any later public outcome requires human review and the existing append-only review workflow.

## 9. OIL separation

`OIL-GENESIS-001` remains `PAUSED`. Gap discovery, challenge submission, and review do not constitute supplier outreach, create OIL providers, start T0, or authorize Stage 4.

## 10. Acceptance tests

The boundary is accepted only when:

- the `.org` Gap index and all six detail pages resolve;
- all six canonical Gap claims and current states remain unchanged;
- case challenge CTAs point to `.org` Gap pages and not `/verify/`;
- the commercial CTA remains secondary and points to `.com/verify/`;
- each challenge form contains exactly four effects and three attribution choices;
- forms post directly to the canonical `.com` challenge endpoint;
- CORS explicitly permits `.org` and does not use a wildcard for POST;
- a production test submission returns `201`, `SUBMITTED`, and `state_changed = false`;
- no raw submission is publicly projected;
- no public claim, case, stop-point, or OIL state drifts.


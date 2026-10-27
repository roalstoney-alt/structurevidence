# IREN tracker human review checklist

Candidate: `SE-IREN-AI-CLOUD-001` · data version `v0.1-rc1` · evidence cutoff `2026-10-22`.

No reviewer identity, approval, or review timestamp is inferred. Every row remains `PENDING_HUMAN_REVIEW` until a legitimate reviewer records a decision against the exact candidate SHA and content digest.

| Row | Candidate state | Required human check | Status |
| --- | --- | --- | --- |
| IREN-R001 | SUPPORTED_AS_ATTRIBUTED | Confirm FY26 revenue and net-loss amounts against the audited statements, not only the results exhibit. | PENDING |
| IREN-R002 | SUPPORTED_AS_ATTRIBUTED | Confirm impairment amount, non-cash description, and mining-hardware attribution. | PENDING |
| IREN-R003 | SUPPORTED_AS_ATTRIBUTED | Confirm agreement duration/value and `furnished_not_filed` treatment; preserve contract-value boundary. | PENDING |
| IREN-R004 | SUPPORTED_AS_ATTRIBUTED | Confirm issuer wording; ensure no Microsoft-authored or independent NVIDIA proof is implied. | PENDING |
| IREN-R005 | SUPPORTED_AS_ATTRIBUTED | Confirm both ARR labels, measurement date, footnote definition, and non-GAAP boundary. | PENDING |
| IREN-R006 | SUPPORTED_AS_ATTRIBUTED | Confirm financing amount/rate/fee boundary and avoid full-funding inference. | PENDING |
| IREN-R007 | NOT_ESTABLISHED | Confirm selected search boundary for customer-authored acceptance; absence must not be universalized. | PENDING |
| IREN-R008 | NOT_ESTABLISHED | Confirm no qualifying Horizon 2–4 delivery/acceptance artifact exists by cutoff. | PENDING |
| IREN-R009 | NOT_ESTABLISHED | Confirm ARR, GAAP revenue, deferred revenue, prepayment, and cash remain separate measures. | PENDING |
| IREN-R010 | NOT_ESTABLISHED | Confirm no full headline-value cash-collection claim is supported by reviewed filings. | PENDING |
| IREN-R011 | NOT_ESTABLISHED | Confirm completion and full-life return boundary; no success/failure or securities conclusion. | PENDING |

## Publication gates

- [ ] Named accountable evidence reviewer signs every row.
- [ ] Financial-disclosure reviewer confirms assurance/liability wording.
- [ ] Counsel or accountable owner reviews securities-facing language and jurisdictions.
- [ ] Privacy/security reviewer verifies the public export and fixed-ID challenge URLs.
- [ ] Owner approves the exact source SHA, page/data digests, row list, evidence cutoff, screenshots, and intended public URL.
- [ ] Any post-approval content change invalidates the approval and triggers a new digest and review.

`READY_FOR_PUBLICATION=YES` is impossible while any item above is pending.

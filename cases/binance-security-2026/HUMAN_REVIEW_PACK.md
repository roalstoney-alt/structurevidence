# SE-BINANCE-SECURITY-001 — human review pack

Review state: `READY_FOR_HUMAN_REVIEW`

Publication state: `BLOCKED_PENDING_EXPLICIT_APPROVAL`
Evidence cutoff: `2026-10-30T07:39:26Z`

## What is ready

- Eight registered source artifacts across operator, analyst, media and public-ledger classes.
- Ten atomic claims: four supported only within explicit attribution/boundaries and six open.
- Eleven timestamped state transitions.
- One independently queried Ethereum transaction, receipt and block anchor.
- A non-routable HTML draft, publication-gated English social candidates and an optional conceptual storyboard.
- Explicit closure tests for reserve/liability coverage and compensation completion.

## Metric boundaries that must survive review

| Metric | Meaning in this pack | Must not be collapsed into |
|---|---|---|
| Impact | Source-defined gross incident estimate | Final realized loss or solvency effect |
| Stolen / moved | Assets transferred under a source's inclusion rule and price cutoff | Attacker's current holdings |
| Frozen / rescued | Assets restricted by issuer or protocol authority at a stated cutoff | Recovered, returned or compensated |
| Recovered / returned | Assets restored to operator or users | Frozen-but-still-restricted assets |
| Compensated | Completed eligible user restoration with evidence | A promise, reserve balance or SAFU balance |

## Source gaps

1. Original pre-incident Binance proof-of-reserves audit time, Merkle root, full address bundle and asset/liability table were not obtained from the accessible dynamic rendering.
2. The promised post-remediation proof-of-reserves update and technical post-mortem were not available by the cutoff.
3. The full nine/ten-chain transaction set was not independently replayed; only one Ethereum transaction/receipt/block anchor was queried.
4. TRM's off-chain attribution inputs are not disclosed in enough detail for independent reproduction.
5. The original Glassnode material underlying the syndicated Eastmoney/财联社 figure was not captured.
6. Freeze, rescue, recovery, return and compensation require a single transaction-level reconciliation with consistent cutoff rules.

## Public-safe fields

Approved for human consideration: case ID, source titles, canonical public URLs, published/observed timestamps, SHA-256 fingerprints, public transaction/block/address identifiers, source-attributed summaries, declared metric definitions, evidence boundaries, open gaps and closure tests.

Excluded from publication: local filesystem paths, cookies, request headers, account data, private correspondence, contact details, credentials, paid data exports and any undisclosed intelligence.

## Required human decisions

- Confirm whether the Binance normalized capture is adequate or whether a first-party raw page capture is required.
- Decide whether the Eastmoney syndicated report adds useful context or should remain out of the public case.
- Review all legal wording around “stolen,” “attacker” and attribution.
- Confirm the chain-count reconciliation and whether Avalanche qualifies for the incident set.
- Require a fresh source check immediately before any publication because the event is rapidly developing.
- Approve or reject creation of a public `index.html`, case-index entry, sitemap entry and social copy. These are intentionally absent.

## Gate summary

```text
BASELINE_SHA = ea1dff9e53725e49d64d595d362b3baa63fe7047
SOURCE_REGISTRY_COUNT = 8
INDEPENDENT_SOURCE_COUNT = 3
SUPPORTED_CLAIMS = 4
OPEN_CLAIMS = 6
DECISION_CONDITION_STATUS = OPEN_INSUFFICIENT_PUBLIC_EVIDENCE
PUBLIC_SAFE = YES_WITH_HUMAN_REVIEW
READY_FOR_HUMAN_REVIEW = YES
MERGE_SHA = NONE
PRODUCTION_STATUS = NOT_DEPLOYED
```

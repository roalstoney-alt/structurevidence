# OIL-GENESIS-001 — Human Send Decision

**Action:** `STAGE_3_HUMAN_SEND_DECISION`  
**Decision date:** `2026-10-03`  
**Decision source:** Explicit human authorization supplied for this stage  
**Stage result:** `PASS`

## Human decisions

```text
OIL-CAND-001 = YES
OIL-CAND-002 = YES
OIL-CAND-003 = YES
OIL-CAND-004 = YES
OIL-CAND-005 = HOLD
```

These values authorize final outreach preparation only. They do not verify a supplier, support a capability, create a production Provider, or authorize an unaudited external transmission.

## First outreach wave

`APPROVED_FOR_OUTREACH = 4`

- `OIL-CAND-001` — Venair Ibérica SAU
- `OIL-CAND-002` — Saint-Gobain Performance Plastics Corporation
- `OIL-CAND-003` — NewAge Industries, Inc. / AdvantaPure
- `OIL-CAND-004` — Watson-Marlow Flow Smart, Inc. / BioPure

`HOLD = 1`

- `OIL-CAND-005` — Trelleborg Medical Solutions

## Frozen contact routes, Claim sets and message hashes

The SHA-256 value is computed over the complete bytes of the named final message file. Any edit requires a new hash before transmission.

| Candidate | Human decision | Final official route | Final Claim IDs | Final message SHA-256 | Sent at |
| --- | --- | --- | --- | --- | --- |
| `OIL-CAND-001` | `YES` | `info@venair.com` | `001`–`007` | `076d1f2562375daa56207f75ad4cdc49f5629874599891a3ec19aae40f577ce0` | `null` |
| `OIL-CAND-002` | `YES` | `https://www.biopharm.saint-gobain.com/contact-us` → Application Support or Quality | `001`–`007` | `38ba8c8f865beb66b04d73fbc68bae8573bd2e33c1d3b033335b7995c7e34aa3` | `null` |
| `OIL-CAND-003` | `YES` | `compliance@newageindustries.com` | `001`–`006` | `1534617204764075f1afeb65ff09c0be913da29ce98314fef2480e928cacadeb` | `null` |
| `OIL-CAND-004` | `YES` | `https://www.wmfts.com/global/` → BioPure-capable route / Contact an expert | `001`–`005` | `f018d7c49abdae04f3b367856e8d6ab2c2f61549713a5b8f5ef8f9dc4d78ccd8` | `null` |
| `OIL-CAND-005` | `HOLD` | No final evidence-request channel frozen | None frozen for sending | `null` | `null` |

All Claim IDs expand to the frozen `OIL-CAP-SIL-NNN` convention. No Stage 1 Claim definition was edited.

## Message review result

Each approved message:

- explains why the named product family was selected;
- presents OIL as a reusable industrial evidence-record experiment;
- lists a small frozen Claim set;
- prefers existing documents and says no bespoke report is required;
- states that supplier statements alone do not establish verified capability;
- preserves source, scope, timestamp and later comparison semantics;
- states that the experiment is not certification, ranking, marketplace placement, a procurement award or a purchase commitment;
- offers `PUBLIC`, `AUTHORIZED_BUYER` and `TRANSACTION_PRIVATE` visibility and fails closed;
- makes participation voluntary; and
- starts the proposed 10-business-day window only after actual receipt.

## Trelleborg HOLD

Trelleborg remains on HOLD. The current material does not close the relationship among Trelleborg Medical Solutions, PharmaSil, 200 HP, BioPharmaPro, the legal manufacturing entity/site, the regional contracting entity and the entity that should own a future supplier response.

The dedicated HOLD record specifies the official clarification route and the evidence required to clear the gate. No replacement supplier was added.

## Append-only outreach events

One `HUMAN_SEND_APPROVED` event was appended for each of `OIL-CAND-001` through `OIL-CAND-004` with source `EXPLICIT_HUMAN_DECISION`. No event was created for actions that have not occurred.

The following event types remain available for later audited use:

```text
HUMAN_SEND_APPROVED
OUTREACH_SENT
SUPPLIER_RESPONDED
EVIDENCE_SUBMITTED
NO_RESPONSE
REFUSED_EVIDENCE
REFUSED_ANY_VISIBILITY
TOO_BUSY
NOT_THIS_CAPABILITY
WITHDRAWN
```

No `OUTREACH_SENT` or future participation event exists yet.

## Transmission boundary

The current execution provides no explicitly authorized, auditable outbound email or form-submission channel. Therefore:

```text
SEND_AUTHORIZED_FOR_PREPARATION = OIL-CAND-001, OIL-CAND-002, OIL-CAND-003, OIL-CAND-004
SEND_AUTHORIZED_FOR_CURRENT_TRANSMISSION = NONE
MESSAGES_ACTUALLY_SENT = 0
SEND_TIMESTAMP = null for all candidates
```

At the next separately authorized execution, the operator must verify the file hash, use the frozen official route, attach or link the candidate's detailed request pack where supported, record the actual result, append `OUTREACH_SENT` only after success, and start the 10-business-day window from the real timestamp.

## Hard-boundary confirmation

No capability status, production Provider, VCF, Evidence record/hash, Demand, Outcome, ReuseRecord, supplier ranking, trust score, preferred-supplier label, migration, UI or deployment was created. Stage 4 was not started.

`NEXT_ALLOWED_STAGE = STAGE_3_FINAL_OUTREACH_EXECUTION`

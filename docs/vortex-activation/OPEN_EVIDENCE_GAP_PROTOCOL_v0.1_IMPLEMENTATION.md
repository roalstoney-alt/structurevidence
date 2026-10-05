# Open Evidence Gap Protocol v0.1 — Phase 1 Implementation

```ini
PROJECT = StructEvidence
PROGRAM = VORTEX ACTIVATION
PHASE = PHASE 1 — EXTERNAL CHALLENGE ACTIVATION
IMPLEMENTATION_DATE = 2026-10-05
IMPLEMENTATION_STATUS = READY_FOR_DEPLOYMENT
DEPLOYED = NO
```

## Scope

The implementation opens exactly six gaps—two for each of the three existing public cases. It does not create a new public case.

| Gap | Existing case | Existing claim |
|---|---|---|
| OEG-CML-001 | CML-PDRE-001 | CML-PDRE-001.INDEPENDENT_VALIDATION |
| OEG-CML-002 | CML-PDRE-001 | CML-PDRE-001.MULTI_ENTITY_REPLICATION |
| OEG-BESS-001 | SE-BESS-SODIUM-001 | SE-BESS-SODIUM-001.NAMED_COMMISSIONED_SITE |
| OEG-BESS-002 | SE-BESS-SODIUM-001 | SE-BESS-SODIUM-001.INDEPENDENT_FIELD_PERFORMANCE |
| OEG-ONC-001 | SE-ONC-NSQNSCLC-CN-001 | SE-ONC-NSQNSCLC-CN-001.HOSPITAL_AGGREGATE_OUTCOME_DATA |
| OEG-ONC-002 | SE-ONC-NSQNSCLC-CN-001 | SE-ONC-NSQNSCLC-CN-001.IVONESCIMAB_APPROVAL |

## Public surface

- `GET /gaps/` — six-gap index.
- `GET /gaps/{gap_id}/` — gap boundary, current state, evidence cut-off, qualifying/non-qualifying examples, challenge form, and public log.
- `GET /gaps/changes/` — append-only public change log.
- `GET /api/gaps` — complete machine-readable registry.
- `GET /api/gaps/{gap_id}` — one gap plus its append-only public log.
- `POST /api/gaps/{gap_id}/challenge` — URL/reference-only challenge intake.

## Intake and review boundary

Submissions support exactly four proposed effects: `SUPPORT`, `CONTRADICT`, `NARROW_SCOPE`, and `CORRECT_ATTRIBUTION`. Attribution is `NAMED`, `ORGANIZATION_ONLY`, or `ANONYMOUS`. Public attribution describes evidence contribution only and is not endorsement.

Every submission starts as `SUBMITTED`. No public form field can set review state. Cloudflare Access protects the review APIs. Human transitions append immutable events, and public change publication is a separate explicit operation permitted only after a matching human-reviewed final state.

### Medical public-research boundary

`OEG-ONC-002` uses the existing population-level regulatory claim `SE-ONC-NSQNSCLC-CN-001.IVONESCIMAB_APPROVAL`. The earlier patient-specific probability candidate was rejected before production release. No public gap may solicit, derive, estimate, expose, or publish a patient-specific treatment success probability, personalized prognosis, patient-specific benefit/risk estimate, or individualized treatment recommendation. Public intake also prohibits personal health information. ECMO remains life support context and is never represented as tumor therapy.

## Persistence and abuse controls

- D1 migration `0002_open_evidence_gaps.sql` creates independent challenge, event, and public-change tables.
- Challenge events and public changes reject update and delete operations through database triggers.
- A database trigger enforces five submissions per IP-derived SHA-256 key per rolling ten minutes.
- `GAP_RATE_LIMIT_SALT` is required and must be configured as a Worker secret.
- Raw IP addresses are not stored.
- Phase 1 accepts no file upload.

## Explicit non-features

```ini
NO_BOUNTY = TRUE
NO_LEADERBOARD = TRUE
NO_CONTRIBUTOR_SCORE = TRUE
NO_AUTO_STATE_CHANGE = TRUE
LOGIN_REQUIRED = NO
PUBLIC_FILE_UPLOAD = NO
```

## Operational targets

```ini
ACK_TARGET = <24 hours
INITIAL_REVIEW_TARGET = <72 hours
PHASE_DURATION = 30 days
TARGETED_INVITATIONS = 30
```

The protocol's success gate is measured only after deployment and real external activity. The implementation does not fabricate submissions, qualifying evidence, state changes, invitations, or acknowledgements.

## OIL synchronization

The imported `OIL-GENESIS-001` state remains `PAUSED`, with zero sent messages and no production records. Gap challenges are not supplier outreach and cannot resume OIL. See `docs/vortex-activation/OIL_GENESIS_001_PAUSE_SYNC.md`.

## Deployment gate

Before deployment:

1. Apply D1 migration `0002_open_evidence_gaps.sql`.
2. Configure `GAP_RATE_LIMIT_SALT` as a secret.
3. Run the complete Worker test suite and dry-run build.
4. Confirm Cloudflare Access variables for admin APIs.
5. Obtain an explicit deployment decision; implementation readiness is not deployment authorization.

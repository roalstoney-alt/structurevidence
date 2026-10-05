PROJECT =
StructEvidence

PROGRAM =
VORTEX ACTIVATION

PROTOCOL =
OPEN EVIDENCE GAP PROTOCOL v0.1

PHASE =
PHASE 1 — EXTERNAL CHALLENGE ACTIVATION

OBJECTIVE =
Create the minimum public and machine-readable infrastructure required to obtain,
review, attribute, and publicly record external evidence challenges against existing
StructEvidence stop points.

HARD BOUNDARY =
Do not add new public cases.
Use only the existing three public cases.

CREATE =
6 Open Evidence Gaps
2 per case

REQUIRED GAP FIELDS =
gap_id
case_id
claim_id
claim_text
current_state
current_scope
evidence_cutoff
what_is_established
what_is_not_established
what_would_change_this
acceptable_source_examples
non_qualifying_examples
last_reviewed
challenge_url

PUBLIC ROUTES =
/gaps/
/gaps/{gap_id}/

API =
GET /api/gaps
GET /api/gaps/{gap_id}
POST /api/gaps/{gap_id}/challenge

SUBMISSION FORM =
URL or public document reference
gap_id
effect = SUPPORT / CONTRADICT / NARROW_SCOPE / CORRECT_ATTRIBUTION
optional note
attribution preference

ATTRIBUTION OPTIONS =
NAMED
ORGANIZATION_ONLY
ANONYMOUS

ATTRIBUTION DISCLAIMER =
Public attribution means evidence contribution only.
It does not imply endorsement of StructEvidence's final conclusion.

NO BOUNTY =
TRUE

NO LEADERBOARD =
TRUE

NO CONTRIBUTOR SCORE =
TRUE

NO AUTO STATE CHANGE =
TRUE

SUBMISSION STATES =
SUBMITTED
SCREENED
IN_SCOPE
OUT_OF_SCOPE
QUALIFYING
NON_QUALIFYING
NEEDS_CLARIFICATION
ACCEPTED
REJECTED
STATE_CHANGED
NO_STATE_CHANGE
SCOPE_CLARIFIED

PUBLIC CHANGE LOG =
REQUIRED

CHANGE LOG MUST BE =
append-only

RATE LIMIT =
5 submissions / IP / 10 minutes

LOGIN REQUIRED =
NO

PUBLIC FILE UPLOAD =
NO — URL/reference only in Phase 1

ACK TARGET =
<24 hours

INITIAL REVIEW TARGET =
<72 hours

PHASE_DURATION =
30 days

TARGETED_INVITATIONS =
30

SUCCESS GATE =
>=3 external submissions
>=2 in-scope submissions
>=1 qualifying submission
>=1 externally triggered state change or scope correction

PRIMARY SUCCESS =
EXTERNAL_REALITY_CHANGED_PUBLIC_RECORD = YES
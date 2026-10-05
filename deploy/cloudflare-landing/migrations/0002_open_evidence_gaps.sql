PRAGMA foreign_keys = ON;

CREATE TABLE gap_challenges (
  challenge_id TEXT PRIMARY KEY,
  gap_id TEXT NOT NULL,
  evidence_reference TEXT NOT NULL,
  effect TEXT NOT NULL CHECK (effect IN ('SUPPORT', 'CONTRADICT', 'NARROW_SCOPE', 'CORRECT_ATTRIBUTION')),
  note TEXT,
  attribution_preference TEXT NOT NULL CHECK (attribution_preference IN ('NAMED', 'ORGANIZATION_ONLY', 'ANONYMOUS')),
  attribution_name TEXT,
  organization_name TEXT,
  contact_email TEXT,
  state TEXT NOT NULL DEFAULT 'SUBMITTED' CHECK (state IN ('SUBMITTED', 'SCREENED', 'IN_SCOPE', 'OUT_OF_SCOPE', 'QUALIFYING', 'NON_QUALIFYING', 'NEEDS_CLARIFICATION', 'ACCEPTED', 'REJECTED', 'STATE_CHANGED', 'NO_STATE_CHANGE', 'SCOPE_CLARIFIED')),
  client_key_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  CHECK (attribution_preference != 'NAMED' OR attribution_name IS NOT NULL),
  CHECK (attribution_preference != 'ORGANIZATION_ONLY' OR organization_name IS NOT NULL),
  CHECK (attribution_preference != 'ANONYMOUS' OR (attribution_name IS NULL AND organization_name IS NULL))
);

CREATE INDEX idx_gap_challenges_gap ON gap_challenges(gap_id, created_at DESC);
CREATE INDEX idx_gap_challenges_state ON gap_challenges(state, created_at DESC);
CREATE INDEX idx_gap_challenges_rate ON gap_challenges(client_key_hash, created_at DESC);

CREATE TRIGGER gap_challenge_rate_limit
BEFORE INSERT ON gap_challenges
WHEN (
  SELECT COUNT(*)
  FROM gap_challenges
  WHERE client_key_hash = NEW.client_key_hash
    AND datetime(created_at) >= datetime(NEW.created_at, '-10 minutes')
) >= 5
BEGIN
  SELECT RAISE(ABORT, 'gap_challenge_rate_limited');
END;

CREATE TABLE gap_challenge_events (
  event_id TEXT PRIMARY KEY,
  challenge_id TEXT NOT NULL REFERENCES gap_challenges(challenge_id),
  event_type TEXT NOT NULL CHECK (event_type IN ('SUBMITTED', 'SCREENED', 'IN_SCOPE', 'OUT_OF_SCOPE', 'QUALIFYING', 'NON_QUALIFYING', 'NEEDS_CLARIFICATION', 'ACCEPTED', 'REJECTED', 'STATE_CHANGED', 'NO_STATE_CHANGE', 'SCOPE_CLARIFIED')),
  event_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  previous_state TEXT,
  new_state TEXT NOT NULL,
  note TEXT
);

CREATE INDEX idx_gap_challenge_events_challenge ON gap_challenge_events(challenge_id, event_at ASC, event_id ASC);

CREATE TRIGGER gap_challenge_events_no_update
BEFORE UPDATE ON gap_challenge_events
BEGIN
  SELECT RAISE(ABORT, 'gap_challenge_events is append-only');
END;

CREATE TRIGGER gap_challenge_events_no_delete
BEFORE DELETE ON gap_challenge_events
BEGIN
  SELECT RAISE(ABORT, 'gap_challenge_events is append-only');
END;

CREATE TABLE gap_public_changes (
  change_id TEXT PRIMARY KEY,
  gap_id TEXT NOT NULL,
  challenge_id TEXT NOT NULL REFERENCES gap_challenges(challenge_id),
  change_type TEXT NOT NULL CHECK (change_type IN ('STATE_CHANGED', 'NO_STATE_CHANGE', 'SCOPE_CLARIFIED')),
  summary TEXT NOT NULL,
  attribution TEXT NOT NULL,
  previous_state TEXT,
  new_state TEXT,
  changed_at TEXT NOT NULL,
  reviewer TEXT NOT NULL
);

CREATE INDEX idx_gap_public_changes_gap ON gap_public_changes(gap_id, changed_at ASC, change_id ASC);

CREATE TRIGGER gap_public_changes_no_update
BEFORE UPDATE ON gap_public_changes
BEGIN
  SELECT RAISE(ABORT, 'gap_public_changes is append-only');
END;

CREATE TRIGGER gap_public_changes_no_delete
BEFORE DELETE ON gap_public_changes
BEGIN
  SELECT RAISE(ABORT, 'gap_public_changes is append-only');
END;

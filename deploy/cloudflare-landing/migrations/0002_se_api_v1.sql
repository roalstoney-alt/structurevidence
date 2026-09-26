PRAGMA foreign_keys = ON;

CREATE TABLE se_api_requests (
  object_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('SUBMITTED', 'TRIAGE', 'ACCEPTED', 'WAITING_FOR_PAYMENT', 'RESEARCHING', 'EVIDENCE_REVIEW', 'STATE_CREATED', 'DELIVERED', 'OUTCOME_PENDING', 'CLOSED', 'REJECTED')),
  payload_json TEXT NOT NULL
);

CREATE TABLE se_api_challenges (
  object_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status = 'CHALLENGE_SUBMITTED'),
  payload_json TEXT NOT NULL
);

CREATE TABLE se_api_outcomes (
  object_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status = 'OUTCOME_REPORTED'),
  payload_json TEXT NOT NULL
);

CREATE TABLE se_api_idempotency (
  scope TEXT NOT NULL CHECK (scope IN ('request', 'challenge', 'outcome')),
  idempotency_key TEXT NOT NULL,
  object_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  response_json TEXT NOT NULL,
  PRIMARY KEY (scope, idempotency_key)
);

CREATE TABLE se_state_proposals (
  proposal_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('DRAFT', 'VALIDATION_FAILED', 'VALIDATED', 'REVIEW_REQUIRED', 'APPROVED', 'MATERIALIZED', 'COMMITTED', 'REJECTED', 'SUPERSEDED')),
  payload_json TEXT NOT NULL
);

CREATE INDEX idx_se_api_requests_created ON se_api_requests(created_at DESC);
CREATE INDEX idx_se_api_challenges_created ON se_api_challenges(created_at DESC);
CREATE INDEX idx_se_api_outcomes_created ON se_api_outcomes(created_at DESC);
CREATE INDEX idx_se_state_proposals_created ON se_state_proposals(created_at DESC);

CREATE TRIGGER se_api_requests_no_update BEFORE UPDATE ON se_api_requests BEGIN SELECT RAISE(ABORT, 'se_api_requests is append-only'); END;
CREATE TRIGGER se_api_requests_no_delete BEFORE DELETE ON se_api_requests BEGIN SELECT RAISE(ABORT, 'se_api_requests is append-only'); END;
CREATE TRIGGER se_api_challenges_no_update BEFORE UPDATE ON se_api_challenges BEGIN SELECT RAISE(ABORT, 'se_api_challenges is append-only'); END;
CREATE TRIGGER se_api_challenges_no_delete BEFORE DELETE ON se_api_challenges BEGIN SELECT RAISE(ABORT, 'se_api_challenges is append-only'); END;
CREATE TRIGGER se_api_outcomes_no_update BEFORE UPDATE ON se_api_outcomes BEGIN SELECT RAISE(ABORT, 'se_api_outcomes is append-only'); END;
CREATE TRIGGER se_api_outcomes_no_delete BEFORE DELETE ON se_api_outcomes BEGIN SELECT RAISE(ABORT, 'se_api_outcomes is append-only'); END;

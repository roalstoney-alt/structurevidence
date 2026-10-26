PRAGMA foreign_keys = ON;

-- Raw idempotency keys and email addresses are never stored here.  The compound
-- primary key scopes a client-generated token to a normalized request type and
-- email hash, preventing the token from becoming a cross-customer lookup key.
CREATE TABLE request_idempotency (
  scope_sha256 TEXT NOT NULL CHECK (length(scope_sha256) = 64),
  idempotency_key_sha256 TEXT NOT NULL CHECK (length(idempotency_key_sha256) = 64),
  request_fingerprint_sha256 TEXT NOT NULL CHECK (length(request_fingerprint_sha256) = 64),
  request_id TEXT NOT NULL REFERENCES requests(request_id),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  PRIMARY KEY (scope_sha256, idempotency_key_sha256),
  UNIQUE (request_id),
  CHECK (expires_at > created_at)
);

CREATE INDEX idx_request_idempotency_expires_at
  ON request_idempotency(expires_at);

-- Consent is an acknowledgement of the customer-private intake boundary.  It
-- is not research authorization and does not change requests.authorization.
CREATE TABLE request_consent_receipts (
  receipt_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES requests(request_id),
  consent_version TEXT NOT NULL,
  consent_accepted INTEGER NOT NULL CHECK (consent_accepted = 1),
  accepted_at TEXT NOT NULL,
  actor TEXT NOT NULL CHECK (actor = 'CUSTOMER'),
  UNIQUE (request_id, consent_version)
);

CREATE INDEX idx_request_consent_receipts_request
  ON request_consent_receipts(request_id, accepted_at ASC);

CREATE TRIGGER request_consent_receipts_no_update
BEFORE UPDATE ON request_consent_receipts
BEGIN
  SELECT RAISE(ABORT, 'request_consent_receipts is append-only');
END;

CREATE TRIGGER request_consent_receipts_no_delete
BEFORE DELETE ON request_consent_receipts
BEGIN
  SELECT RAISE(ABORT, 'request_consent_receipts is append-only');
END;

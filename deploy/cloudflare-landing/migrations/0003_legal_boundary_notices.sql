PRAGMA foreign_keys = ON;

CREATE TABLE request_notices (
  request_id TEXT PRIMARY KEY REFERENCES requests(request_id),
  notice_version TEXT NOT NULL,
  acknowledged_at TEXT NOT NULL,
  privacy_notice_ack INTEGER NOT NULL CHECK (privacy_notice_ack = 1),
  confidentiality_boundary_ack INTEGER NOT NULL CHECK (confidentiality_boundary_ack = 1),
  publication_authorization INTEGER NOT NULL DEFAULT 0 CHECK (publication_authorization = 0),
  marketing_consent INTEGER NOT NULL DEFAULT 0 CHECK (marketing_consent = 0)
);

CREATE TABLE request_private_context (
  context_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES requests(request_id),
  created_at TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  retention_status TEXT NOT NULL DEFAULT 'NEEDS_OPERATOR_FACTS' CHECK (retention_status IN ('NEEDS_OPERATOR_FACTS', 'ACTIVE', 'RESTRICTED', 'DISPOSITION_PENDING'))
);

CREATE INDEX idx_request_private_context_request ON request_private_context(request_id, created_at ASC);

CREATE TRIGGER request_private_context_no_update
BEFORE UPDATE ON request_private_context
BEGIN
  SELECT RAISE(ABORT, 'request_private_context changes require a separately reviewed disposition migration');
END;

CREATE TRIGGER request_private_context_no_delete
BEFORE DELETE ON request_private_context
BEGIN
  SELECT RAISE(ABORT, 'request_private_context deletion requires a separately reviewed disposition migration');
END;

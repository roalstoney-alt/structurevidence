PRAGMA foreign_keys = ON;

CREATE TABLE customers (
  customer_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  contact_name TEXT,
  email TEXT NOT NULL,
  company TEXT
);

CREATE INDEX idx_customers_email ON customers(email);

CREATE TABLE requests (
  request_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  request_type TEXT NOT NULL CHECK (request_type IN ('VERIFY', 'CONTEXT')),
  customer_id TEXT NOT NULL REFERENCES customers(customer_id),
  decision TEXT,
  claim_or_question TEXT,
  technical_object TEXT,
  current_dependency TEXT,
  alternative_considered TEXT,
  decision_deadline TEXT,
  case_reference TEXT,
  requested_output TEXT,
  status TEXT NOT NULL DEFAULT 'SUBMITTED' CHECK (status IN ('SUBMITTED', 'UNDER_REVIEW', 'SCOPE_PROPOSED', 'AWAITING_CUSTOMER', 'AUTHORIZED', 'IN_PROGRESS', 'DELIVERED', 'CLOSED')),
  privacy_class TEXT NOT NULL DEFAULT 'CUSTOMER_PRIVATE' CHECK (privacy_class = 'CUSTOMER_PRIVATE'),
  human_owner TEXT,
  research_authorization_status TEXT NOT NULL DEFAULT 'NOT_AUTHORIZED' CHECK (research_authorization_status IN ('NOT_AUTHORIZED', 'L0_REUSE_AUTHORIZED', 'L1_VERIFY_AUTHORIZED', 'L2_INVESTIGATE_AUTHORIZED', 'L3_DEEP_AUTHORIZED')),
  CHECK (decision IS NOT NULL OR claim_or_question IS NOT NULL)
);

CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX idx_requests_status ON requests(status, created_at DESC);
CREATE INDEX idx_requests_customer ON requests(customer_id);

CREATE TABLE request_events (
  event_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES requests(request_id),
  event_type TEXT NOT NULL CHECK (event_type IN ('REQUEST_SUBMITTED', 'STATUS_CHANGED', 'OWNER_ASSIGNED', 'SCOPE_PROPOSED', 'CUSTOMER_RESPONSE_RECEIVED', 'RESEARCH_AUTHORIZED', 'RESEARCH_STARTED', 'DELIVERABLE_SENT', 'CASE_CLOSED')),
  event_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  previous_state TEXT,
  new_state TEXT NOT NULL,
  note TEXT
);

CREATE INDEX idx_request_events_request ON request_events(request_id, event_at ASC);

CREATE TRIGGER request_events_no_update
BEFORE UPDATE ON request_events
BEGIN
  SELECT RAISE(ABORT, 'request_events is append-only');
END;

CREATE TRIGGER request_events_no_delete
BEFORE DELETE ON request_events
BEGIN
  SELECT RAISE(ABORT, 'request_events is append-only');
END;

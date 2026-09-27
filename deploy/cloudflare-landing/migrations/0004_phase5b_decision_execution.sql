-- Protected Phase 5B decision execution plane. Payloads are customer-private.
CREATE TABLE IF NOT EXISTS se_decision_requests (
  request_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  state TEXT NOT NULL,
  visibility TEXT NOT NULL CHECK (visibility = 'CUSTOMER_PRIVATE'),
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS se_decision_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT NOT NULL REFERENCES se_decision_requests(request_id),
  event_at TEXT NOT NULL,
  previous_state TEXT,
  new_state TEXT NOT NULL,
  actor TEXT NOT NULL,
  reason TEXT NOT NULL,
  details_json TEXT
);

CREATE TRIGGER IF NOT EXISTS se_decision_events_no_update
BEFORE UPDATE ON se_decision_events BEGIN SELECT RAISE(ABORT, 'decision events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS se_decision_events_no_delete
BEFORE DELETE ON se_decision_events BEGIN SELECT RAISE(ABORT, 'decision events are append-only'); END;

CREATE TABLE IF NOT EXISTS se_decision_quotes (
  quote_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES se_decision_requests(request_id),
  created_at TEXT NOT NULL, valid_until TEXT, envelope_id TEXT NOT NULL, price_status TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS se_decision_payments (
  payment_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES se_decision_requests(request_id),
  confirmed_at TEXT NOT NULL, confirmed_by TEXT NOT NULL, human_override INTEGER NOT NULL DEFAULT 0, reference TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS se_decision_deliveries (
  delivery_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES se_decision_requests(request_id),
  created_at TEXT NOT NULL, delivery_hash TEXT NOT NULL, proof_json TEXT NOT NULL, payload_json TEXT NOT NULL
);

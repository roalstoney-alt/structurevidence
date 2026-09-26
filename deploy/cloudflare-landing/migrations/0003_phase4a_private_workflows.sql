PRAGMA foreign_keys = ON;

CREATE TABLE demand_signals (
  signal_id TEXT PRIMARY KEY,
  observed_at TEXT NOT NULL,
  platform TEXT NOT NULL,
  source_url TEXT NOT NULL UNIQUE,
  score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 10),
  score_class TEXT NOT NULL CHECK (score_class IN ('IGNORE','WATCH','QUALIFIED','HIGH_VALUE')),
  mapped_subject_id TEXT,
  mapped_state_id TEXT,
  contact_status TEXT NOT NULL DEFAULT 'NOT_REVIEWED',
  payload_json TEXT NOT NULL,
  privacy_classification TEXT NOT NULL CHECK (privacy_classification = 'INTERNAL_ACQUISITION_SIGNAL'),
  created_at TEXT NOT NULL
);

CREATE TABLE demand_contact_events (
  event_id TEXT PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES demand_signals(signal_id),
  event_type TEXT NOT NULL,
  event_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  acquisition_source TEXT NOT NULL,
  notes TEXT,
  payload_json TEXT NOT NULL
);

CREATE TABLE request_commercial_scopes (
  scope_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('REQUEST_SUBMITTED','TRIAGE','ACCEPTED','RESEARCH_SCOPED','PRICE_PROPOSED','PAYMENT_REQUIRED','WAITING_FOR_PAYMENT','PAYMENT_CONFIRMED','RESEARCHING')),
  research_scope TEXT,
  quoted_amount TEXT,
  currency TEXT,
  payment_status TEXT NOT NULL CHECK (payment_status IN ('NOT_REQUESTED','PAYMENT_INTENT_CONFIRMED','WAITING_FOR_PAYMENT','MANUAL_PAYMENT_PENDING','MANUAL_PAYMENT_CONFIRMED')),
  manual_invoice_reference TEXT,
  provider_adapter TEXT NOT NULL DEFAULT 'DISABLED',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  CHECK (provider_adapter = 'DISABLED')
);

CREATE INDEX idx_demand_signals_review ON demand_signals(score_class, contact_status, observed_at DESC);
CREATE INDEX idx_demand_events_signal ON demand_contact_events(signal_id, event_at ASC);
CREATE INDEX idx_commercial_request ON request_commercial_scopes(request_id);

CREATE TRIGGER demand_signals_no_delete BEFORE DELETE ON demand_signals BEGIN SELECT RAISE(ABORT, 'demand signals cannot be deleted directly'); END;
CREATE TRIGGER demand_contact_events_no_update BEFORE UPDATE ON demand_contact_events BEGIN SELECT RAISE(ABORT, 'contact events are append-only'); END;
CREATE TRIGGER demand_contact_events_no_delete BEFORE DELETE ON demand_contact_events BEGIN SELECT RAISE(ABORT, 'contact events are append-only'); END;

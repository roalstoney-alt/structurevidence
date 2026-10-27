# Intake hardening migration rollback boundary

Migration `0003_intake_hardening.sql` is additive. It does not alter or delete
existing customer, request, event, or evidence records. The pre-hardening Worker
continues to read the original three tables, but the hardened Worker must not be
deployed before this migration and must ship with its matching client.

Before any production receipt has been accepted, a database operator may roll
back the empty migration in this order:

```sql
DROP TRIGGER request_consent_receipts_no_delete;
DROP TRIGGER request_consent_receipts_no_update;
DROP INDEX idx_request_consent_receipts_request;
DROP TABLE request_consent_receipts;
DROP INDEX idx_request_idempotency_expires_at;
DROP TABLE request_idempotency;
```

After any production use, these statements are **not** an authorized rollback:
consent receipts are append-only audit records and request idempotency mappings
are part of the submission integrity boundary. Roll forward, preserve records,
and complete privacy/retention review instead.

# External Feedback Ledger

Append only confirmed challenge, citation, and decision-request observations. Never use zero when a private or inaccessible channel cannot be inspected; append `ACCESS_BLOCKED` with the limitation instead.

`INTERNAL_SYNTHETIC` events are test-only and must never count as external validation. The production ledger starts with no observed external events. The test fixture lives under `tests/fixtures/` and is not part of the ledger.

This pilot does not create another scheduler. Any future append operation must reuse the existing daily StructEvidence automation and pass human review.

# Phase 4A Paid-Chain Policy v0.1

`PAYMENT_ACTIVATION = NO`.

Phase 4A prepares request status, bounded research scope, quoted amount, currency, payment status, manual invoice reference, and a disabled provider-adapter boundary. Logical states include REQUEST_SUBMITTED, TRIAGE, ACCEPTED, RESEARCH_SCOPED, PRICE_PROPOSED, PAYMENT_REQUIRED, WAITING_FOR_PAYMENT, PAYMENT_CONFIRMED, and RESEARCHING.

No Stripe, PayPal, card collection, subscription, automatic billing, paid Discord role, or payment webhook is implemented. The database enforces `provider_adapter = DISABLED`.

A real statement of willingness to pay is recorded as `PAYMENT_INTENT_CONFIRMED`. A human-owned commercial exception may be recorded as `MANUAL_COMMERCIAL_PILOT`. Neither event activates payment infrastructure.

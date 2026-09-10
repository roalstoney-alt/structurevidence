# GDR-SE Paid Delivery Gate

Payment confirmation is separate from release authorization.

Fulfillment may become ready only when payment is confirmed and GDR-SE issues `ALLOW_PAID_DELIVERY` for a frozen report version. If authorization is absent, stale, superseded or under review, the paid report is not delivered.

Public verification must never expose customer email.

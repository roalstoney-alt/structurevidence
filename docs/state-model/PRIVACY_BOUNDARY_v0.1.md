# SE-FRR Public / Private Boundary v0.1

Public research data is not private customer data.

Requests are `CUSTOMER_PRIVATE` and remain in the protected customer plane, with existing D1 intake and append-only request events as the preferred storage boundary. Requester identity, contact details, company-sensitive questions, commercial context, and private outcomes must not enter Git-backed public data, public JSON, Discord, or any other public projection.

The Phase 1 exporter emits only PUBLIC Subjects, Evidence, States, Changes, Branches, and explicitly authorized PUBLIC Outcomes. It never exports Request or Challenge objects. A PUBLIC Outcome is schema-valid only when `authorization_for_public_use` is true. Private outcomes may be converted to later Evidence only through explicit authorization and review; conversion does not retroactively change visibility or State history.

Phase 1 includes no deployment and copies no live D1 data. All request and outcome fixtures are synthetic and visibly marked test-only.

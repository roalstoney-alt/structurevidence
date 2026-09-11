# RDL Freshness Policy Derivation v0.1

Status: METHOD PILOT

Research question: determine whether structural Level, structural Delta, evidence-family and release records remain current enough for their stated research use.

Subject classes: PUBLIC_COMPANY_TREASURY and L1_NETWORK are configured for the current pilot surface. PROTOCOL_GOVERNANCE and MARKET_CONTEXT remain present but unconfigured.

Level and Delta are evaluated separately. Evidence age is separate from structural state age. No global freshness threshold is used.

Configured rules: 4

Unconfigured rules: 9

Rejected rules: a universal 30 day freshness cutoff, a shared Level/Delta age rule, and any rule tuned to make paid delivery easier.

Final rule basis: reporting-period rules for corporate treasury, hybrid time/event rules for supply and validator distribution, event-only rules for persistent governance mechanisms, and explicit POLICY_NOT_CONFIGURED fail-safes for sparse categories.

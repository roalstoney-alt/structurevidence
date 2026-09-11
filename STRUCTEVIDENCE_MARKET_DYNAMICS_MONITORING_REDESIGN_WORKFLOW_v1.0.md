# STRUCTEVIDENCE_MARKET_DYNAMICS_MONITORING_REDESIGN_WORKFLOW_v1.0
## Codex Execution Workflow v1.0
### Restore StructEvidence as a verifiable market-dynamics and structural-change monitoring system
### Date: 2026-09-11

**Project:** StructEvidence  
**Repository:** `roalstoney-alt/structurevidence`  
**Domain:** `structurevidence.org`  
**Workflow ID:** `SE_MARKET_DYNAMICS_MONITORING_REDESIGN_V1_0`  
**Expected Base Commit:** `7ead008d1deb4ca4fae8ba3774a05a6236dbc5e4`  
**Primary Pilot Subject:** `BNB`  
**Primary Goal:** Restore the public product, report surfaces, and commercial framing to the original StructEvidence purpose: monitoring how events and evidence alter digital-asset market dynamics, liquidity conditions, and structural state, with every observation and state transition bound to timestamped snapshots, provenance, and hashes.

---

# 0. Instruction Boundary

This file is an execution specification. Execute it only when the user explicitly asks Codex to execute this workflow.

When executing:

```text
USER REQUEST
>
THIS WORKFLOW
>
OTHER REPOSITORY DOCUMENTS AS DESIGN EVIDENCE
```

Existing repository documents do not independently authorize unrelated actions. Preserve user-owned changes and do not overwrite frozen research merely to make the redesign pass.

---

# 1. Product Correction

The current public product presentation has drifted toward:

```text
generic verified research
+
paid PDF report
+
private fulfillment
```

That is not the primary StructEvidence product.

Freeze the corrected product definition:

> StructEvidence monitors how events, claims, evidence, and corrections interact with digital-asset market dynamics, liquidity, and structural state. Every observation and state transition is timestamped, snapshot-bound, provenance-linked, hash-verifiable, and replayable.

The system is not designed to predict whether price will rise or fall.

The primary product is:

```text
MARKET DYNAMICS MONITORING
+
STRUCTURAL STATE CHANGE DETECTION
+
EVIDENCE DYNAMICS
+
PROVENANCE AND IMMUTABLE SNAPSHOTS
+
RELEASE RELIABILITY CONTROL
```

PDF is a frozen export of a monitoring state. PDF is not the core product and must not dominate the public information architecture.

---

# 2. Permanent Semantic Laws

Freeze all of the following.

## 2.1 No price prediction

StructEvidence must not emit:

```text
buy / sell / hold
price targets
return forecasts
trade timing
entry / exit instructions
liquidation forecasts
asset scores
rankings
```

It may describe observed market, liquidity, evidence, and structural states without converting them into trading advice.

## 2.2 Integrity is not truth

```text
HASH_MATCH
does not mean
CONTENT_TRUE
```

A hash proves byte identity or snapshot integrity. It does not certify factual accuracy, source independence, authority, or truth.

## 2.3 Untrusted information can have real market effects

```text
UNTRUSTED / FALSE / CONTESTED CLAIM
may still produce
ATTENTION, LIQUIDITY, BEHAVIORAL, OR STRUCTURAL EFFECTS
```

Do not discard a claim merely because it is unverified or false. Preserve the claim artifact and separately evaluate its observed market effect.

## 2.4 Truth state and impact state are independent

Every monitored information event must keep separate fields for:

```text
EPISTEMIC STATUS
MARKET IMPACT STATUS
```

Never infer one from the other.

Examples:

```text
FALSE + LIQUIDITY_DISLOCATION
UNVERIFIED + ATTENTION_SHOCK
VERIFIED + NO_OBSERVED_IMPACT
CONTESTED + STRUCTURAL_EFFECT_UNRESOLVED
```

## 2.5 Observation is not causation

Temporal coincidence may be recorded. Causation requires an explicit method and sufficient evidence.

Allowed:

```text
Market depth changed within the defined observation window after event E.
```

Not allowed without causal support:

```text
Event E caused the market-depth change.
```

## 2.6 Missing data remains visible

Use explicit states such as:

```text
NOT_OBSERVED
NOT_MEASURED
INSUFFICIENT_DATA
NOT_COMPARABLE
UNRESOLVED
```

Do not interpolate a continuous history from sparse observations. Do not create synthetic liquidity or market data to make the UI look complete.

## 2.7 Frozen evidence is append-only

Do not mutate frozen research, evidence-freeze payloads, prior snapshots, prior hashes, or prior authorization records.

Corrections and supersessions must create new records that preserve the old record and point in the correct direction.

---

# 3. System Roles

Implement and present the system as an integrated chain. Do not collapse the layers into one score.

## 3.1 RDL

RDL governs policy, method boundaries, freshness, allowed transformations, and release rules.

## 3.2 RTP

RTP records:

```text
actor
source
artifact identity
capture class
known_at
effective_at
snapshot timestamp
SHA-256
transformation lineage
correction history
supersession history
```

RTP proves traceability and artifact integrity, not content truth.

## 3.3 Evidence Dynamics / EDL

Evidence Dynamics monitors how claims, observations, revisions, contradictions, corrections, and source relationships change through time.

If the repository distinguishes the Evidence Dynamics track from ECL, preserve that distinction:

```text
Evidence Dynamics = change and propagation of evidence states
ECL = evidence consistency finding
```

Do not silently rename or merge frozen ECL semantics. Public UI may use `Evidence Dynamics` as the human-facing label and show ECL as a specific consistency output.

## 3.4 MDL

MDL monitors market and structural dynamics. Preserve existing domain and Flow-8 concepts where supported:

```text
magnitude
velocity
acceleration
persistence
depth
breadth
coupling
entropy
```

Do not show a Flow-8 value unless its measurement concept, observation window, inputs, and derivation are available.

## 3.5 Timeline

Timeline keeps Level and Delta separate:

```text
LEVEL = condition at a dated observation
DELTA = change relative to a valid comparable prior observation or explicit change event
```

Do not infer Delta from one snapshot.

## 3.6 GDR-SE

GDR-SE controls whether a result is fit for:

```text
monitor display
public release
snapshot export
commercial delivery
```

GDR-SE may limit, abstain, require refresh, require human review, or veto. It must not improve the underlying research finding.

Monitoring an event is not the same as authorizing a factual or causal conclusion about that event.

---

# 4. Target Product Experience

The first screen must be the monitoring product, not a marketing landing page.

Primary navigation:

```text
Monitor
Asset States
State Transitions
Event Ledger
Evidence Dynamics
Provenance
Verify
Snapshot Reports
```

Commercial or enterprise access may remain available, but it must be secondary and must not displace the monitoring workflow.

The first-viewport product signal must communicate:

```text
current monitored subjects
latest snapshot time
current observation coverage
recent state changes
freshness / monitoring status
```

Suggested public value proposition:

> Monitor how events and evidence alter digital-asset market structure and liquidity. Every state transition is snapshot-bound, hash-verifiable, and replayable.

---

# 5. BNB Pilot User Journey

Implement BNB as the first complete monitoring subject.

Required journey:

```text
User enters BNB
-> BNB monitoring workspace opens
-> current structural Level is visible
-> latest valid Delta is visible or explicitly unestablished
-> recent event and evidence changes are visible
-> observed market / liquidity effect is visible or explicitly NOT_MEASURED
-> snapshot, provenance, freshness, and GDR state are inspectable
-> prior state can be replayed
-> snapshot report can be previewed or exported according to authorization
```

Do not route the primary BNB action directly to a generic paid-report sales page.

---

# 6. BNB Monitoring Workspace Requirements

Create a quiet, work-focused monitoring interface optimized for repeated scanning and comparison.

## 6.1 Header strip

Show:

```text
Subject
Subject ID
Snapshot As-Of
Known-At cutoff
Monitoring status
Freshness state
GDR monitor authorization
Snapshot hash short form
```

## 6.2 Current state

Show separately:

```text
Structural Level
Structural Delta
Evidence State
Market Dynamics State
Liquidity Observation State
```

Do not combine these into one score, badge, ranking, or traffic-light health grade.

## 6.3 Since previous snapshot

Show exact changes:

```text
field / dimension
prior value
current value
effective_at
known_at
change basis
comparability state
source artifact refs
```

If there is no valid comparable prior, display `DELTA_NOT_ESTABLISHED`.

## 6.4 State-transition timeline

The timeline must distinguish:

```text
subject events
market observations
liquidity observations
evidence events
corrections
supersessions
authorization events
```

Provide DAY / WEEK / MONTH only where the existing aggregation lineage supports it.

## 6.5 Event ledger

For each event display:

```text
event ID
event type
event domain
effective_at
known_at
capture_at
epistemic status
market impact status
impact window
affected dimensions
artifact hash
correction / supersession links
```

## 6.6 Evidence dynamics

Display:

```text
claim state
observation state
source dependency
revision / correction state
contradiction state
propagation state if observed
ECL consistency finding
```

Avoid treating URL count as source independence.

## 6.7 Market and liquidity effects

Display only measured fields. Candidate observations include:

```text
market depth
spread
volume
turnover
liquidity concentration
venue concentration
volatility state
funding / leverage state
liquidation activity
cross-market coupling
```

This list is not authorization to invent or fetch data. Use available, licensed, public, or already frozen inputs. Unsupported dimensions must show `NOT_MEASURED`.

## 6.8 Provenance drawer

Allow the user to inspect:

```text
source artifact
capture class
SHA-256
snapshot timestamp
transformation path
derived record
correction chain
```

## 6.9 Authorization boundary

Show what GDR-SE currently permits:

```text
DISPLAY_OBSERVATION
DISPLAY_STATE
PUBLISH_INTERPRETATION
EXPORT_SNAPSHOT
COMMERCIAL_DELIVERY
```

Do not map existing GDR outcomes to these actions without an explicit, versioned adapter.

---

# 7. Dual-Axis Information Event Model

Create a machine-readable schema for monitored information events.

Recommended path:

```text
monitoring/schema/information_event.schema.json
```

Required fields:

```text
event_id
subject_id
event_type
event_domain
effective_at
known_at
captured_at
source_ids
artifact_ids
artifact_sha256
epistemic_status
epistemic_status_as_of
market_impact_status
impact_observation_window
affected_dimensions
causal_status
correction_status
supersedes_event_id
notes
```

Minimum `epistemic_status` vocabulary:

```text
UNVERIFIED
SUPPORTED
CONTESTED
FALSE
CORRECTED
RETRACTED
INSUFFICIENT_DATA
```

Minimum `market_impact_status` vocabulary:

```text
NOT_MEASURED
NO_OBSERVED_IMPACT
ATTENTION_SHOCK
BEHAVIORAL_SHIFT
LIQUIDITY_DISLOCATION
MARKET_STATE_CHANGE
STRUCTURAL_EFFECT_UNRESOLVED
STRUCTURAL_EFFECT_OBSERVED
```

Minimum `causal_status` vocabulary:

```text
NOT_EVALUATED
TEMPORALLY_ASSOCIATED
ALTERNATIVE_EXPLANATIONS_OPEN
CAUSAL_SUPPORT_PARTIAL
CAUSAL_SUPPORT_ESTABLISHED
```

Default causal status must not exceed `TEMPORALLY_ASSOCIATED` without an explicit causal method and evidence record.

---

# 8. Monitoring Snapshot Contract

Create:

```text
monitoring/schema/monitoring_snapshot.schema.json
monitoring/schema/state_transition.schema.json
monitoring/schema/monitoring_build_manifest.schema.json
```

A monitoring snapshot must include:

```text
snapshot_id
subject_id
snapshot_as_of
known_at_cutoff
generated_at
source_bundle_hash
structural_level
structural_delta
evidence_dynamics
market_dynamics
liquidity_observations
recent_events
freshness_snapshot
gdr_snapshot
rtp_provenance_refs
prior_snapshot_id
snapshot_sha256
builder_version
schema_version
```

The snapshot hash must be calculated from canonical serialized content with the hash field excluded or explicitly null during hashing.

Record both:

```text
CONTENT_BUNDLE_SHA256
OUTPUT_ARTIFACT_SHA256
```

when the snapshot is rendered to HTML, PDF, or another artifact.

---

# 9. Derived Monitoring Artifacts

Build monitoring artifacts from existing canonical and frozen inputs. Do not mutate source artifacts.

Recommended BNB outputs:

```text
monitoring/subjects/bnb/MONITORING_SNAPSHOT.json
monitoring/subjects/bnb/STATE_TRANSITION_INDEX.json
monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json
monitoring/subjects/bnb/PROVENANCE_INDEX.json
monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json
```

The build manifest must list every input path and SHA-256.

Use existing inputs where applicable:

```text
canonical research
observation registry
claim registry
source inventory
counter-evidence log
timeline atomic observations
event ledger
RDL Freshness evaluation
GDR-SE authorization record
RTP / evidence-freeze manifest
```

If market or liquidity observations are absent, encode that absence. Do not derive a false market state from protocol facts alone.

---

# 10. Builder Requirements

Create a deterministic monitoring view-model builder using the repository's existing Python patterns.

Recommended paths:

```text
monitoring/runtime/builder.py
monitoring/runtime/hash.py
monitoring/runtime/validators.py
scripts/build_monitoring_snapshot.py
```

The builder must:

1. Resolve the exact subject.
2. Read structured canonical inputs.
3. Enforce `known_at <= snapshot_as_of`.
4. Preserve effective-at and known-at separately.
5. Select a prior comparable snapshot using explicit comparability rules.
6. Keep Level and Delta separate.
7. Join evidence events without converting evidence truth into market impact.
8. Join market observations without asserting causation.
9. Attach freshness and GDR state.
10. Build the provenance index.
11. Canonically serialize the content.
12. Calculate and record hashes.
13. Fail closed on schema, lineage, or hash errors.

No network call may be required for deterministic test fixtures.

---

# 11. Public Site Redesign

The current static hosting constraint may remain. Build the best complete monitoring experience supported by current data and runtime boundaries.

## 11.1 Home / Monitor

Replace the marketing-first hero with the operational monitoring surface.

Required first screen:

```text
subject search
coverage index
latest snapshot time
recent state transitions
freshness status
clear method boundary
```

Searching `BNB` must open or reveal the BNB monitoring workspace, not only a small Free Scan card.

## 11.2 Asset States

Provide a compact comparison table for current covered subjects:

```text
subject
structural Level
latest Delta
evidence state
market observation coverage
freshness
last snapshot
GDR monitor action
```

Do not rank subjects.

## 11.3 State Transitions

Provide a cross-subject event stream with filters for:

```text
subject
event domain
state dimension
epistemic status
market impact status
time window
```

## 11.4 Event Ledger

Provide a human-readable immutable event record with hash, correction, and supersession visibility.

## 11.5 Evidence Dynamics

Show claim changes, evidence conflicts, corrections, source dependency, and observed propagation separately from market effects.

## 11.6 Verify

Upgrade the public Verify surface from static explanatory text to an artifact lookup when supported by available static metadata.

At minimum, allow lookup by:

```text
snapshot ID
artifact ID
report ID
SHA-256
```

Static client-side lookup over published public-safe JSON is acceptable for this phase. Do not claim server authentication where none exists.

---

# 12. Frontend Design Requirements

Treat this as an operational monitoring tool.

Required design behavior:

```text
quiet and information-dense
scan-friendly
clear temporal hierarchy
restrained color usage
tables and timelines where comparison matters
icons for familiar actions
tooltips for unfamiliar controls
stable dimensions
responsive desktop and mobile behavior
no overlapping text
no nested cards
```

Avoid:

```text
oversized marketing hero
decorative card grids
gradient decoration
score-dashboard aesthetics
price chart aesthetics that imply trading prediction
one-note dark-blue or purple palette
```

Use color semantically and accessibly for different event domains and observation states. Never use color alone to encode meaning.

The BNB workspace must remain usable at:

```text
1440 x 900
1024 x 768
390 x 844
```

---

# 13. Snapshot Report Redesign

Reframe the PDF product as:

```text
MONITORING SNAPSHOT REPORT
```

It is a frozen, portable export of a specific monitoring state.

Required report sections:

1. Cover and snapshot identity.
2. Monitoring scope and as-of boundary.
3. Current structural Level.
4. Latest established Delta.
5. Changes since prior snapshot.
6. Recent event ledger.
7. Evidence dynamics.
8. Market and liquidity observations.
9. Epistemic-status vs market-impact matrix.
10. Open alternative explanations.
11. Freshness and GDR authorization.
12. RTP provenance and input hashes.
13. Corrections and supersessions.
14. Limitations and `NOT_MEASURED` fields.
15. Verification record.

Do not include a price target or trading recommendation.

Create a clearly labeled public demo preview only from public-safe or synthetic material:

```text
DEMO_MONITORING_SNAPSHOT
NOT A LIVE PAID REPORT
```

Do not expose a live paid report publicly.

---

# 14. Commercial Positioning Correction

Commercial value must be framed around continued monitoring, not one-off PDF purchase.

Candidate product capabilities:

```text
state-change monitoring
event and evidence alerts
snapshot-to-snapshot Delta
historical replay
provenance inspection
monitoring snapshot export
structured JSON export
API access when implemented
```

Preserve existing truthful readiness states.

If payment remains unconfigured:

```text
PAYMENT_ENABLED = false
AUTOMATED_FULFILLMENT = MANUAL_ONLY
```

Do not invent seller identity, price, wallet, payment provider, tax handling, support contact, refund policy, delivery SLA, or production backend.

The redesign may update commercial copy and product hierarchy, but it must not enable payment without the required user-supplied configuration and explicit authorization.

---

# 15. Frozen-State and Regression Protection

Before implementation, hash and record:

```text
canonical research payloads
evidence-freeze manifests
timeline semantic artifacts
RDL Freshness policies and evaluations
GDR-SE authorization records
commercial readiness config
```

Create:

```text
docs/execution/PRE_MONITORING_REDESIGN_HASHES.json
docs/execution/POST_MONITORING_REDESIGN_HASHES.json
```

Frozen semantic payload hashes must remain unchanged unless the workflow identifies a genuine defect, documents it, and uses append-only correction or supersession. UI and derived-view changes must not rewrite source truth.

---

# 16. Required Tests

Create or extend focused tests:

```text
scripts/test_monitoring_schema.py
scripts/test_monitoring_builder.py
scripts/test_monitoring_bnb.py
scripts/test_information_event_dual_axis.py
scripts/test_monitoring_no_lookahead.py
scripts/test_monitoring_level_delta.py
scripts/test_monitoring_hash_integrity.py
scripts/test_monitoring_provenance.py
scripts/test_monitoring_gdr_adapter.py
scripts/test_monitoring_public_surface.py
scripts/test_monitoring_ui.py
scripts/test_monitoring_snapshot_pdf.py
scripts/run_monitoring_redesign_validation.py
```

Minimum negative tests:

1. `FALSE` information can retain a measured market impact.
2. `VERIFIED` information does not automatically receive market impact.
3. Hash match does not upgrade epistemic status.
4. Market impact does not upgrade epistemic status.
5. Temporal association does not become causation.
6. A future-known event is excluded from an earlier snapshot.
7. One snapshot cannot establish Delta.
8. Incomparable prior observations cannot establish Delta.
9. Missing liquidity data renders `NOT_MEASURED`.
10. A correction preserves the original event and hash.
11. Supersession direction is forward and append-only.
12. GDR monitor authorization is separate from commercial delivery authorization.
13. No price prediction, score, ranking, buy, sell, or hold output appears.
14. Public demo content cannot expose private paid bytes.
15. Root and `docs/` public surfaces remain synchronized.

---

# 17. Validation Registry

Create:

```text
monitoring/validation/MONITORING_REDESIGN_GATE_RESULTS.json
```

Required gates:

```text
MON01_PRODUCT_DEFINITION
MON02_NO_PRICE_PREDICTION
MON03_RDL_ROLE
MON04_RTP_PROVENANCE
MON05_EVIDENCE_DYNAMICS_ROLE
MON06_MDL_ROLE
MON07_GDR_ROLE
MON08_INTEGRITY_NOT_TRUTH
MON09_TRUTH_IMPACT_SEPARATION
MON10_OBSERVATION_NOT_CAUSATION
MON11_INFORMATION_EVENT_SCHEMA
MON12_MONITORING_SNAPSHOT_SCHEMA
MON13_STATE_TRANSITION_SCHEMA
MON14_BUILD_MANIFEST_SCHEMA
MON15_BNB_STRUCTURED_INPUTS
MON16_BNB_NO_LOOKAHEAD
MON17_BNB_LEVEL_DELTA_SEPARATION
MON18_BNB_EVENT_LEDGER
MON19_BNB_EVIDENCE_DYNAMICS
MON20_BNB_MARKET_OBSERVATION_BOUNDARY
MON21_BNB_LIQUIDITY_OBSERVATION_BOUNDARY
MON22_BNB_FRESHNESS
MON23_BNB_GDR_MONITOR_ACTION
MON24_BNB_RTP_LINEAGE
MON25_SNAPSHOT_CONTENT_HASH
MON26_OUTPUT_ARTIFACT_HASH
MON27_APPEND_ONLY_CORRECTIONS
MON28_APPEND_ONLY_SUPERSESSION
MON29_MONITOR_FIRST_HOME
MON30_BNB_SEARCH_JOURNEY
MON31_ASSET_STATE_TABLE
MON32_STATE_TRANSITION_TIMELINE
MON33_EVENT_LEDGER_UI
MON34_EVIDENCE_DYNAMICS_UI
MON35_PROVENANCE_UI
MON36_VERIFY_LOOKUP
MON37_SNAPSHOT_REPORT
MON38_PUBLIC_DEMO_BOUNDARY
MON39_COMMERCIAL_POSITIONING
MON40_PAYMENT_READINESS_HONESTY
MON41_PRIVATE_REPORT_BOUNDARY
MON42_ACCESSIBILITY
MON43_RESPONSIVE_LAYOUT
MON44_ROOT_DOCS_SYNC
MON45_HREF_INTEGRITY
MON46_FROZEN_HASHES_UNCHANGED
MON47_SECRET_SCAN
MON48_PUBLIC_PDF_SCAN
MON49_PRIOR_TESTS
MON50_PRODUCTION_SMOKE_TEST
```

Acceptance:

```text
MONITORING_REDESIGN_PASS
```

requires every mandatory gate to be `PASS` and no gate to be `FAIL`, `BLOCKED`, `PARTIAL`, or `NOT_EVALUATED`.

If data needed for a market or liquidity dimension does not exist, the implementation may still pass only when it truthfully emits `NOT_MEASURED`, documents the boundary, and does not imply monitoring coverage that does not exist.

---

# 18. Public Language Requirements

Public copy must use these distinctions consistently:

```text
artifact integrity != content truth
source authority != market relevance
epistemic status != market impact
observation != causation
Level != Delta
currentness != truth
monitoring != prediction
snapshot export != live monitoring
```

Required public boundary language:

> StructEvidence records and evaluates market, structural, and evidence changes. It does not predict price direction or provide investment advice. Hash verification establishes artifact integrity, not truth. Unverified or false information may still be monitored when it produces observable market effects.

Keep the public surface English by default unless a later workflow explicitly authorizes multilingual publication.

---

# 19. Explicitly Out of Scope

Do not:

```text
enable self-serve payment
invent a payment provider
invent a seller identity
invent prices
invent a receiving wallet
invent market or liquidity observations
fetch uncontrolled live data merely to fill charts
replace frozen research findings
weaken GDR gates
turn GDR into a score
turn hash verification into truth certification
discard false or untrusted claims that had measurable effects
assert causation from temporal proximity
add price prediction or trading signals
publish paid PDF bytes
redesign unrelated research subjects beyond shared monitoring components
```

---

# 20. Implementation Files

Codex must audit existing patterns before creating new abstractions. The following are recommended, not permission to duplicate an existing local mechanism:

```text
monitoring/schema/information_event.schema.json
monitoring/schema/monitoring_snapshot.schema.json
monitoring/schema/state_transition.schema.json
monitoring/schema/monitoring_build_manifest.schema.json
monitoring/config/status_vocabulary.json
monitoring/runtime/builder.py
monitoring/runtime/hash.py
monitoring/runtime/validators.py
monitoring/subjects/bnb/MONITORING_SNAPSHOT.json
monitoring/subjects/bnb/STATE_TRANSITION_INDEX.json
monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json
monitoring/subjects/bnb/PROVENANCE_INDEX.json
monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json
monitoring/validation/MONITORING_REDESIGN_GATE_RESULTS.json
scripts/build_monitoring_snapshot.py
scripts/run_monitoring_redesign_validation.py
monitor.html or an equivalent monitor-first route
assets/monitor.js or equivalent
assets/monitor.css only if existing style ownership requires it
docs/execution/MONITORING_REDESIGN_PRE_AUDIT.md
docs/execution/MONITORING_REDESIGN_DATA_AUDIT.md
docs/execution/MONITORING_REDESIGN_UI_AUDIT.md
docs/execution/MONITORING_REDESIGN_FINAL_REPORT.md
```

Update both root and `docs/` publication trees according to the repository's existing publishing mechanism. Do not hand-maintain divergent copies when a generator already owns them.

---

# 21. Exact Codex Execution Order

Execute exactly:

1. Verify repository, branch, remote, and worktree state.
2. Read `AGENTS.md` and local instructions if present.
3. Record current HEAD and compare with the expected base commit.
4. Preserve all user-owned changes.
5. Inventory current public routes, generators, root/docs synchronization, and deployment mechanism.
6. Inventory RDL, RTP, Evidence Dynamics, ECL, MDL, Timeline, Freshness, and GDR-SE artifacts.
7. Inventory BNB canonical, frozen, timeline, freshness, and authorization artifacts.
8. Record pre-redesign frozen hashes.
9. Create the monitoring redesign pre-audit.
10. Freeze product language and semantic laws in a versioned public-safe contract.
11. Define status vocabularies.
12. Define information-event dual-axis schema.
13. Define monitoring-snapshot schema.
14. Define state-transition schema.
15. Define monitoring-build-manifest schema.
16. Implement canonical serialization and hashing.
17. Implement BNB structured input resolver.
18. Implement no-look-ahead filtering.
19. Implement Level/Delta separation.
20. Implement prior-comparability handling.
21. Implement event-domain joining.
22. Implement epistemic-status and market-impact separation.
23. Implement observation-vs-causation boundary.
24. Implement missing-data states.
25. Implement RTP provenance index.
26. Implement freshness snapshot adapter.
27. Implement versioned GDR monitor-action adapter.
28. Build BNB monitoring snapshot.
29. Build BNB transition index.
30. Build BNB information-event ledger.
31. Build BNB provenance index.
32. Build BNB input/hash manifest.
33. Validate all structured outputs.
34. Redesign the home page as the monitoring product.
35. Implement BNB search-to-workspace journey.
36. Implement current-state strip.
37. Implement snapshot-to-snapshot change table.
38. Implement state-transition timeline.
39. Implement event-ledger view.
40. Implement Evidence Dynamics view.
41. Implement market/liquidity observation view with honest missing states.
42. Implement provenance inspection.
43. Implement GDR action boundary display.
44. Implement asset-state comparison table.
45. Implement public-safe Verify lookup.
46. Reframe reports as monitoring snapshot exports.
47. Generate a public-safe demo monitoring snapshot report.
48. Render every PDF page and inspect it visually.
49. Confirm the demo report is clearly labeled and contains no private paid content.
50. Correct commercial positioning toward monitoring access, alerts, history, exports, and future API.
51. Preserve `PAYMENT_ENABLED = false` unless separately authorized with complete production config.
52. Remove or demote copy that presents one-off PDF sales as the core product.
53. Update architecture and method pages only where needed for semantic consistency.
54. Update root and `docs/` through the canonical publisher.
55. Add schema tests.
56. Add builder tests.
57. Add dual-axis negative tests.
58. Add no-look-ahead tests.
59. Add Level/Delta tests.
60. Add hash and provenance tests.
61. Add GDR adapter tests.
62. Add BNB journey tests.
63. Add public-language regression tests.
64. Add responsive UI tests.
65. Run desktop browser QA at 1440 x 900.
66. Run tablet browser QA at 1024 x 768.
67. Run mobile browser QA at 390 x 844.
68. Confirm no overlap, clipping, blank visualization, or broken interaction.
69. Run all prior Timeline tests.
70. Run all prior RDL Freshness tests.
71. Run all prior GDR-SE tests.
72. Run all prior paid-PDF security and authorization tests.
73. Run commercial and public-surface tests.
74. Run href integrity.
75. Run root/docs sync checks.
76. Record post-redesign frozen hashes.
77. Confirm frozen semantic artifacts are unchanged.
78. Scan for price prediction, score, ranking, buy, sell, and hold regressions.
79. Scan for secrets and private report exposure.
80. Scan the public tree for PDF leakage.
81. Run `git diff --check`.
82. Generate the monitoring validation registry.
83. Confirm no mandatory gate is unevaluated.
84. Generate final audit reports from measured results.
85. Review the full diff for scope and accidental generated churn.
86. Commit implementation.
87. Push `origin/main` only if the user request authorizes workflow execution through publication.
88. Verify remote SHA.
89. Verify production home/monitor route.
90. Verify production BNB search journey.
91. Verify production timeline, event ledger, Evidence Dynamics, provenance, and Verify routes.
92. Verify production payment remains disabled unless separately authorized.
93. Verify no public paid report bytes.
94. Report what is measured, what is not measured, and what remains manual.
95. STOP.

---

# 22. Suggested Commit Messages

Primary:

```text
restore market dynamics monitoring product
```

Optional final audit metadata:

```text
finalize monitoring redesign validation
```

---

# 23. Final Execution Report Template

```text
PROJECT
StructEvidence

WORKFLOW
STRUCTEVIDENCE_MARKET_DYNAMICS_MONITORING_REDESIGN_WORKFLOW_v1.0

BASE_COMMIT
...

IMPLEMENTATION_COMMIT
...

FINAL_REMOTE_SHA
...

PRODUCT_POSITIONING
MARKET_DYNAMICS_MONITORING

PRIMARY_SUBJECT
BNB

BNB_SEARCH_JOURNEY
PASS / PARTIAL / FAIL

STRUCTURAL_LEVEL
...

STRUCTURAL_DELTA
...

EVIDENCE_DYNAMICS
...

MARKET_OBSERVATION_COVERAGE
...

LIQUIDITY_OBSERVATION_COVERAGE
...

FRESHNESS
...

GDR_MONITOR_ACTION
...

SNAPSHOT_HASH
...

PROVENANCE_LINEAGE
PASS / PARTIAL / FAIL

PUBLIC_VERIFY_LOOKUP
PASS / PARTIAL / FAIL

SNAPSHOT_REPORT
PASS / PARTIAL / FAIL

PAYMENT_READINESS
...

AUTOMATED_FULFILLMENT_READINESS
...

PRIVATE_REPORT_EXPOSURE
0

GATE_SUMMARY
PASS: ...
PARTIAL: ...
FAIL: ...
BLOCKED: ...
NOT_EVALUATED: ...

ACCEPTANCE
MONITORING_REDESIGN_PASS / PARTIAL / FAIL

MEASURED LIMITATIONS
...
```

---

# 24. Final Acceptance Standard

Accept only if:

1. The public product is monitoring-first.
2. BNB search opens a real monitoring workspace.
3. Structural Level and Delta remain separate.
4. Evidence truth state and market impact state remain separate.
5. False, contested, or unverified claims can be recorded without being endorsed.
6. Hash verification is never described as truth certification.
7. Market effects are not presented as causation without support.
8. Missing market and liquidity data are shown honestly.
9. Every displayed state traces to structured artifacts and hashes.
10. BNB history can be inspected and replayed at the supported resolution.
11. GDR controls display, interpretation, export, and delivery actions through explicit semantics.
12. Snapshot reports are exports of monitoring state, not the primary product.
13. No price prediction, trading signal, score, or ranking is introduced.
14. Frozen research and evidence history remain append-only.
15. Root/docs publication is synchronized.
16. Desktop, tablet, and mobile monitoring workflows pass visual and interaction QA.
17. Public payment and fulfillment claims exactly match actual readiness.
18. No private paid report bytes enter the public tree.
19. All mandatory gates pass.
20. Production behavior matches the committed monitoring product.

The redesign is not accepted merely because the homepage copy changed. It must expose a working, structured, verifiable BNB monitoring experience grounded in the existing evidence and timeline system.

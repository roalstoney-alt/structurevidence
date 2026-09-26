# Phase 4A Demand Signal Radar v0.1

DSR detects public evidence that a person or organization is facing a current decision. It is not generic lead scraping and Demand Signals never become canonical Evidence automatically.

Scoring is additive and bounded: real problem 0–3, action intent 0–2, specificity 0–2, StructEvidence fit 0–2, and contactability 0–1. Interpretation is IGNORE 0–3, WATCH 4–5, QUALIFIED 6–7, and HIGH_VALUE 8–10.

`apps/demand-signal-radar/dsr.py` provides public-API search adapters, exact-field ingestion, automatic classification, scoring, deduplication, State mapping, candidate cards, response drafts, daily output, and a human review queue. GitHub and Stack Exchange are declared public-API sources. Reddit, X, LinkedIn, and generic forums are `MANUAL_SEARCH_REQUIRED` unless an authorized compliant connector is later added.

The review queue can approve a proposed action but cannot perform it. No send/follow/reply/DM/invite function exists. Repeated high-value unmapped signals remain preserved for research prioritization.

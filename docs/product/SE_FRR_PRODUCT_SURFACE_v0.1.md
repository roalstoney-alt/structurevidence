# SE-FRR Product Surface v0.1

The Phase 3 surface adds a temporal product layer without replacing the existing commercial site. Its public routes are `/states`, `/states/{subject_id}`, `/changes`, `/changes/{change_id}`, `/evidence/{evidence_id}`, and `/founding`. Private/noindex routes are `/request`, `/challenge/{state_id}`, and the Access-protected `/outcome/{request_id}`.

The browser obtains product records exclusively from same-origin `SE_API_v1`. It never imports or reads canonical repository directories. The Worker retains an empty production projection by default; tests and the local preview inject data explicitly.

The Subject hierarchy is: current recorded State, What Changed, confidence boundary, evidence groups, unknowns, branches, immutable history, semantic State comparison, Temporal Explorer, Request, and Challenge. Numeric confidence is forbidden. Branches are paths rather than predictions.

Failure is explicit: the UI distinguishes unavailable API, missing record, unavailable historical boundary, and submission failure. It never substitutes fabricated fallback records.

Mobile order follows Subject, current State, observed time, change, evidence, unknowns, history. Layouts collapse to a single column and controls preserve visible keyboard focus.

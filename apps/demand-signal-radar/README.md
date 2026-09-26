# SE Demand Signal Radar v0.1

`dsr.py` classifies public decision signals, scores them from 0–10, deduplicates them in protected SQLite storage, maps them to public States, prepares candidate cards/drafts, and exposes a human review queue.

It contains no function that sends, follows, replies, DMs, invites, bills, or activates a payment provider. GitHub search uses its documented public API; unsupported platforms return `MANUAL_SEARCH_REQUIRED` in the capability map.

Runtime databases belong under `data/internal/demand-signals/` and are ignored by Git.

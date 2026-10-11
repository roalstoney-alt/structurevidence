# SE-CEPE-001 run audit notes

## `SE-CEPE-CTRL-20261011-001`

DISPOSITION = `INVALIDATED_FOR_ACTIVATION_EVIDENCE`

The first uncommitted controlled run is retained for append-only audit. It
identified an AP HTTP 403 and correctly recorded that task observation as
`SOURCE_UNAVAILABLE`, but the run summary incorrectly counted that status as a
completed check. Its supplied `started_at` was also 48 seconds later than the
local `finished_at`, so it is not valid evidence of T0.

The runner was corrected to:

1. count `SOURCE_UNAVAILABLE` as an operational exception;
2. try only the task's already-registered fallback sources, in order;
3. retain each attempted URL and result; and
4. preserve this original run rather than silently rewriting it.

The next controlled run, if internally consistent and logged, is the only run
eligible to establish T0 and scheduler verification.

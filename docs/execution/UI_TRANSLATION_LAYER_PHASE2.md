# UI Translation Layer / Phase 2

## Scope

Phase 2 adds a simplified structural-change timeline above the existing forensic Timeline. It visualizes only recorded structural Levels and established Delta from the frozen BNB day-resolution dataset.

## Visual semantics

- Filled amber point: an established structural Delta.
- Outlined teal point: an observed structural Level.
- Dashed connector: multiple observations exist, but their change is not established as comparable.
- Selecting a point reveals its date, Level, Delta, basis, observation IDs, source artifact, and structural-day SHA-256.

The visualization does not interpolate between observations, convert categories into numeric scores, or imply price direction. Market and liquidity series can use the same time-indexed presentation in a future phase only after measured and frozen inputs exist.

## Preserved layers

The detailed day/week/month Timeline, state table, event ledger, Evidence Dynamics, GDR action table, Verify route, and RTP provenance remain available below the simplified view.

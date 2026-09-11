# Monitoring Redesign Pre-Audit

Base commit: `7ead008d1deb4ca4fae8ba3774a05a6236dbc5e4`

The repository already contains BNB canonical research, frozen evidence, Timeline R1.1a Level/Delta artifacts, RDL Freshness v0.1a, and GDR-SE R1.1 authorization. The public product, however, leads with Free Scan and paid-report language instead of a monitoring workspace.

Measured BNB inputs support structural and evidence monitoring. They do not contain a current market-depth, spread, venue-liquidity, leverage, liquidation, or volatility time series. Those fields must remain `NOT_MEASURED` in this release.

This redesign creates derived monitoring views only. Frozen source artifacts remain append-only and unchanged.

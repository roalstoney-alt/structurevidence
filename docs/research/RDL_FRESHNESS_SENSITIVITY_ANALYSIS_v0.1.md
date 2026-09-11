# RDL Freshness Sensitivity Analysis v0.1

Candidate windows were reviewed against 90/120/180 day current bands, 150/180/270 day aging bands, and 210/240/365 day refresh bands.

Because many categories have fewer than five intervals, small-window alternatives were rejected where they would create cliff effects without source cadence support.

Result: use broad bands only for minimum viable configured Level/evidence rules, and keep sparse Delta and unsupported dimensions POLICY_NOT_CONFIGURED.

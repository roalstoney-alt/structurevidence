# X manual publication boundary

The only authorized publication identity for this workflow is
`@structevidence`. The connected Metricool account is explicitly out of scope
because it is not that X identity. It must not be used for a live test, a
scheduled publication, identity discovery, or credential proxying.

Automatic publication is paused. The unified daily workflow must not call any X
write interface and must not load X credentials. It produces one candidate and
places the following in the daily report for human review and manual posting:

- exact English text
- cited URLs and evidence cutoff
- content hash
- `HUMAN_GATE_REQUIRED`
- `X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW`
- `X_POST_SENT=0`

The command-line and GitHub Actions entry points expose report-only execution;
there is no live publication mode while this boundary is active.

No additional scheduled task is needed or authorized for this configuration.

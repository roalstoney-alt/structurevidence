# X publisher authorization boundary

The only authorized publication identity for this workflow is
`@structevidence`. The connected Metricool account is explicitly out of scope
because it is not that X identity. It must not be used for a live test, a
scheduled publication, identity discovery, or credential proxying.

The implemented publisher talks directly to the official X API v2. Before a
live test, an operator must authorize the X application as `@structevidence`
with user-context read and write permissions, then place the resulting user
access token in the executor's secret store as `X_USER_ACCESS_TOKEN`. The token
must not be pasted into chat, committed, logged, or written to an artifact.

Run the existing manual executor in `live-x-test` mode only after authorization.
The adapter first calls `/2/users/me` and hard-blocks unless the returned
username is exactly `structevidence`. It then reconciles recent posts, creates
at most one post, reads the post back, and records a post ID and public URL only
after author and text verification succeed.

Until that identity and write scope are verified, the truthful state is:

- `X_AUTH=BLOCKED`
- `X_PUBLISH_TEST=BLOCKED`
- `X_POST_SENT=0`

No additional scheduled task is needed or authorized for this configuration.

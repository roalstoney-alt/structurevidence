# X publisher authorization boundary

The only authorized publication identity for this workflow is
`@structevidence`. The connected Metricool account is explicitly out of scope
because it is not that X identity. It must not be used for a live test, a
scheduled publication, identity discovery, or credential proxying.

The implemented publisher talks directly to the official X API v2. The simplest
durable configuration is OAuth 1.0a user context: create one X developer App,
set its App permission to read and write, and generate the user tokens while
logged in as `@structevidence`. Store these four values in the executor's secret
store:

- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

X currently uses consumption-based API credits. Creating a plain Post is billed
per request; a Post containing a URL may have a different resource price. Check
the live Developer Console price before adding credits. Metricool is not part of
this path.

The four values must not be pasted into chat, committed, logged, or written to
an artifact. OAuth 2 remains a compatibility path through
`X_USER_ACCESS_TOKEN`, but it requires token refresh handling for unattended
daily operation and is therefore not the preferred minimal setup.

Run the existing manual executor first in `x-preflight` mode. This calls
`/2/users/me` without creating a Post and hard-blocks unless the returned
username is exactly `structevidence`. Then run `live-x-test` once. The adapter
repeats the identity check, reconciles recent posts, creates
at most one Post, reads the Post back, and records a Post ID and public URL only
after author and text verification succeed.

Until that identity and write scope are verified, the truthful state is:

- `X_AUTH=BLOCKED`
- `X_PUBLISH_TEST=BLOCKED`
- `X_POST_SENT=0`

No additional scheduled task is needed or authorized for this configuration.

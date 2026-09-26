# SE-FRR-001 Phase 4A Open Issues

Date: 2026-09-26

## Human-only blocker

Discord owner authorization is required before Phase 4A.9. The owner must create or authorize the private server and application, grant only the permissions in `apps/community-bot/discord-server-spec.json`, and provide runtime secrets through the chosen secret store.

Until that action occurs:

- `BOT_AUTHORIZATION` is not passed.
- The Research Room aggregate gate is not passed.
- Closed internal Discord smoke testing has not run.
- Public-source searches have not started.
- No contact canary is ready or authorized.

## Deferred execution

After authorization, the next bounded steps are command registration, closed internal smoke testing, DSR operation against permitted public sources, and a maximum 3–5 human-reviewed contacts. Expansion to 20 contacts requires the specified human checkpoint for signal quality, message relevance, State usefulness, and contact acceptability.

Current validation counters are zero: human-reviewed contacts, meaningful responses, Research Room users, real Research Requests, payment-intent confirmations, and manual commercial pilots. These are expected pre-authorization values, not implementation failures.

Payment activation, paid advertising, mass recruitment, automatic outreach, visual onboarding, and general-audience redesign remain out of scope.

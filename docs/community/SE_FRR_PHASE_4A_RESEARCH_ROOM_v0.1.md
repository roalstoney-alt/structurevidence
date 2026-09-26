# Phase 4A Founding Research Room v0.1

The primary collaboration environment is an invite-only Discord server named **StructEvidence Founding Research Room**, capped at 15 founding users. Discord is not top-of-funnel discovery and never becomes canonical storage.

The machine-readable server specification is `apps/community-bot/discord-server-spec.json`. It freezes the required categories, channels, roles, minimal bot permissions, zero privileged intents, and no automatic invites.

The bot implements `/state`, `/change`, `/request`, `/challenge`, and `/evidence`. Public commands consume `SE_API_v1`. Request and Challenge commands move the user to the protected StructEvidence flow instead of collecting private details in a Discord channel.

Server creation, developer application creation, interaction endpoint configuration, command registration, and authorization belong to the human owner. Secrets remain environment variables. The registration script requires both secrets and the explicit `--human-approved` flag.

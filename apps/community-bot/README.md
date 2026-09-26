# Founding Research Room bot

The bot consumes `SE_API_v1` and implements `/state`, `/change`, `/request`, `/challenge`, and `/evidence`. Request and Challenge commands redirect users to protected StructEvidence flows; they never collect private context in Discord.

`interaction-handler.mjs` verifies Discord Ed25519 signatures. `DISCORD_PUBLIC_KEY`, application identity, and bot token must be supplied as environment secrets and are never committed. Server creation, developer application approval, command registration, and bot authorization are human-only Phase 4A steps.

The bot has no canonical write path and no automatic invite or outreach capability.

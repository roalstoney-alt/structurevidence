# Founding Research Room bot

The bot consumes `SE_API_v1` and implements `/state`, `/change`, `/request`, `/challenge`, and `/evidence`. Request and Challenge commands redirect users to protected StructEvidence flows; they never collect private context in Discord.

`interaction-handler.mjs` verifies Discord Ed25519 signatures. The exact runtime variables are `DISCORD_APPLICATION_ID`, `DISCORD_GUILD_ID`, `DISCORD_BOT_TOKEN`, and `DISCORD_PUBLIC_KEY`; `SE_API_BASE` is optional and defaults to `https://structevidence.com`. Secrets are never committed.

`verify-guild.mjs` uses the official Bot REST API to authenticate the bot, confirm the application/guild binding, reject Administrator or privileged intents, and audit the approved roles/channels without changing them. `register-commands.mjs --human-approved` registers guild-scoped commands only. It never creates global commands.

The bot has no canonical write path and no automatic invite or outreach capability.

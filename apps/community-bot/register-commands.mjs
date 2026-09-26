import { COMMANDS } from "./bot.mjs";

if (!process.argv.includes("--human-approved")) throw new Error("Discord command registration requires --human-approved after owner authorization.");
const applicationId = process.env.DISCORD_APPLICATION_ID, token = process.env.DISCORD_BOT_TOKEN;
if (!applicationId || !token) throw new Error("DISCORD_APPLICATION_ID and DISCORD_BOT_TOKEN must be provided as environment secrets.");
const response = await fetch(`https://discord.com/api/v10/applications/${applicationId}/commands`, { method: "PUT", headers: { authorization: `Bot ${token}`, "content-type": "application/json" }, body: JSON.stringify(COMMANDS) });
if (!response.ok) throw new Error(`Discord registration failed: ${response.status}`);
console.log(`Registered ${(await response.json()).length} commands after explicit human authorization.`);

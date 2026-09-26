import { readFile } from "node:fs/promises";
import { verifyGuild } from "./discord-api.mjs";

const spec = JSON.parse(await readFile(new URL("./discord-server-spec.json", import.meta.url)));
const result = await verifyGuild({
  applicationId: process.env.DISCORD_APPLICATION_ID,
  guildId: process.env.DISCORD_GUILD_ID,
  token: process.env.DISCORD_BOT_TOKEN,
  spec,
});
console.log(JSON.stringify(result, null, 2));
if (!result.pass) process.exitCode = 1;

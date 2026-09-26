import { COMMANDS } from "./bot.mjs";
import { registerGuildCommands } from "./discord-api.mjs";

if (!process.argv.includes("--human-approved")) throw new Error("Discord command registration requires --human-approved after owner authorization.");
const commands = await registerGuildCommands({
  applicationId: process.env.DISCORD_APPLICATION_ID,
  guildId: process.env.DISCORD_GUILD_ID,
  token: process.env.DISCORD_BOT_TOKEN,
  commands: COMMANDS,
});
console.log(`Registered ${commands.length} guild commands after explicit human authorization.`);

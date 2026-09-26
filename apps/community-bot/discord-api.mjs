const API = "https://discord.com/api/v10";
const ADMINISTRATOR = 0x8n;
const PRIVILEGED_INTENT_FLAGS = (1 << 12) | (1 << 13) | (1 << 14) | (1 << 15) | (1 << 18) | (1 << 19);

export async function discordRequest(path, token, { fetcher = fetch, method = "GET", body } = {}) {
  if (!token) throw new Error("DISCORD_BOT_TOKEN is required as an environment secret.");
  const response = await fetcher(`${API}${path}`, {
    method,
    headers: { authorization: `Bot ${token}`, accept: "application/json", ...(body ? { "content-type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Discord Bot API request failed: ${response.status}`);
  return payload;
}

export async function verifyGuild({ applicationId, guildId, token, fetcher = fetch, spec }) {
  if (!applicationId || !guildId || !token) throw new Error("DISCORD_APPLICATION_ID, DISCORD_GUILD_ID, and DISCORD_BOT_TOKEN are required as environment secrets.");
  const [application, bot, guild, roles, channels] = await Promise.all([
    discordRequest("/oauth2/applications/@me", token, { fetcher }),
    discordRequest("/users/@me", token, { fetcher }),
    discordRequest(`/guilds/${guildId}`, token, { fetcher }),
    discordRequest(`/guilds/${guildId}/roles`, token, { fetcher }),
    discordRequest(`/guilds/${guildId}/channels`, token, { fetcher }),
  ]);
  if (application.id !== applicationId || application.bot?.id !== bot.id || guild.id !== guildId) throw new Error("Discord application, bot, or guild identity mismatch.");
  const member = await discordRequest(`/guilds/${guildId}/members/${bot.id}`, token, { fetcher });
  const effectiveRoles = roles.filter((role) => role.id === guild.id || member.roles.includes(role.id));
  const administrator = effectiveRoles.some((role) => (BigInt(role.permissions || "0") & ADMINISTRATOR) !== 0n);
  const privilegedIntents = Boolean((application.flags || 0) & PRIVILEGED_INTENT_FLAGS);
  const roleNames = new Set(roles.map((role) => role.name));
  const categoryNames = new Set(channels.filter((channel) => channel.type === 4).map((channel) => channel.name));
  const channelNames = new Set(channels.filter((channel) => channel.type === 0).map((channel) => channel.name));
  const missingRoles = spec.roles.filter((name) => !roleNames.has(name));
  const missingCategories = Object.keys(spec.categories).filter((name) => !categoryNames.has(name));
  const missingChannels = Object.values(spec.categories).flat().filter((name) => !channelNames.has(name));
  return {
    authenticated: true,
    application_match: true,
    guild_connected: true,
    administrator,
    privileged_intents: privilegedIntents,
    structure_complete: missingRoles.length + missingCategories.length + missingChannels.length === 0,
    missing_roles: missingRoles,
    missing_categories: missingCategories,
    missing_channels: missingChannels,
    pass: !administrator && !privilegedIntents && missingRoles.length + missingCategories.length + missingChannels.length === 0,
  };
}

export async function registerGuildCommands({ applicationId, guildId, token, commands, fetcher = fetch }) {
  if (!applicationId || !guildId || !token) throw new Error("DISCORD_APPLICATION_ID, DISCORD_GUILD_ID, and DISCORD_BOT_TOKEN are required as environment secrets.");
  return discordRequest(`/applications/${applicationId}/guilds/${guildId}/commands`, token, { fetcher, method: "PUT", body: commands });
}

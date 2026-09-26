import { discordResponse, handleCommand } from "./bot.mjs";

function hex(value) { return Uint8Array.from(value.match(/.{2}/g) || [], (byte) => Number.parseInt(byte, 16)); }
export async function verifyDiscord(request, publicKey) {
  const signature = request.headers.get("x-signature-ed25519"), timestamp = request.headers.get("x-signature-timestamp"), body = await request.text();
  if (!signature || !timestamp || !/^[a-f0-9]{64}$/i.test(publicKey || "")) return { ok: false, body };
  const key = await crypto.subtle.importKey("raw", hex(publicKey), { name: "Ed25519" }, false, ["verify"]);
  const payload = new TextEncoder().encode(timestamp + body);
  return { ok: await crypto.subtle.verify("Ed25519", key, hex(signature), payload), body };
}
export async function handleInteraction(request, env, fetcher = fetch) {
  const verified = await verifyDiscord(request, env.DISCORD_PUBLIC_KEY);
  if (!verified.ok) return new Response("invalid request signature", { status: 401 });
  const interaction = JSON.parse(verified.body);
  if (interaction.type === 1) return Response.json({ type: 1 });
  if (interaction.type !== 2) return new Response("unsupported interaction", { status: 400 });
  const options = Object.fromEntries((interaction.data.options || []).map((item) => [item.name, item.value]));
  try { return Response.json(discordResponse(await handleCommand(interaction.data.name, options, { apiBase: env.SE_API_BASE || "https://structevidence.com", fetcher }))); }
  catch (error) { return Response.json(discordResponse({ ephemeral: true, content: `Unable to complete command: ${error.message}` })); }
}

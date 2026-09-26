import assert from "node:assert/strict";
import test from "node:test";
import { COMMANDS, discordResponse, handleCommand } from "./bot.mjs";
import { readFileSync } from "node:fs";
import { registerGuildCommands, verifyGuild } from "./discord-api.mjs";

const fixtures = {
  "/api/v1/subjects": { data: { items: [{ subject_id: "SE-SUBJ-000001", canonical_name: "NXP RF Power" }] } },
  "/api/v1/subjects/SE-SUBJ-000001/state": { data: { state_code: "MIGRATION_PRESSURE_DETECTED", observed_at: "2026-09-25T00:00:00Z", accepted_evidence_count: 4, counter_evidence_count: 2, unknown_count: 3 } },
  "/api/v1/subjects/SE-SUBJ-000001/states": { data: [{ state_code: "WATCH" }, { state_code: "MIGRATION_PRESSURE_DETECTED" }] },
  "/api/v1/subjects/SE-SUBJ-000001/changes": { data: [{ change_id: "SE-CHG-20260925-000001", detected_at: "2026-09-25T00:00:00Z", previous: { state_code: "WATCH" }, current: { state_code: "MIGRATION_PRESSURE_DETECTED" }, trigger_evidence_ids: ["SE-EV-1"], unknowns_resolved: ["U1"], counter_evidence_added: [], counter_evidence_removed: [], change_summary: "New deployment evidence recorded." }] },
  "/api/v1/changes/SE-CHG-20260925-000001": { data: { change_id: "SE-CHG-20260925-000001", detected_at: "2026-09-25T00:00:00Z", previous: { state_code: "WATCH" }, current: { state_code: "MIGRATION_PRESSURE_DETECTED" }, trigger_evidence_ids: ["SE-EV-1"], unknowns_resolved: ["U1"], counter_evidence_added: [], counter_evidence_removed: [], change_summary: "New deployment evidence recorded." } },
  "/api/v1/evidence/SE-EV-20260925-000001": { data: { normalized_claim: "A public source supports the transition.", review: { status: "ACCEPTED" }, published_at: "2026-09-20T00:00:00Z", observed_at: "2026-09-25T00:00:00Z" } },
};
const fetcher = async (url) => { const body = fixtures[new URL(url).pathname]; return new Response(JSON.stringify(body || { error: { message: "not found" } }), { status: body ? 200 : 404, headers: { "content-type": "application/json" } }); };
const options = { apiBase: "https://structevidence.com", fetcher };

test("command manifest is minimal and frozen", () => assert.deepEqual(COMMANDS.map((item) => item.name), ["state", "change", "request", "challenge", "evidence"]));
test("state consumes SE_API_v1 and returns temporal summary", async () => { const result = await handleCommand("state", { subject: "NXP" }, options); assert.match(result.content, /MIGRATION_PRESSURE_DETECTED/); assert.match(result.content, /Previous State: WATCH/); assert.match(result.content, /Accepted Evidence: 4/); });
test("change exposes semantic delta", async () => { const result = await handleCommand("change", { change: "SE-CHG-20260925-000001" }, options); assert.match(result.content, /WATCH → MIGRATION_PRESSURE_DETECTED/); assert.match(result.content, /Unknown Resolved: 1/); });
test("request redirects to protected web flow", async () => { const result = await handleCommand("request", {}, options); assert.equal(result.ephemeral, true); assert.match(result.content, /\/request/); assert.doesNotMatch(result.content, /email|decision context/i); });
test("challenge redirects and cannot mutate State", async () => { const result = await handleCommand("challenge", { state_id: "SE-ST-20260925-000001" }, options); assert.equal(result.ephemeral, true); assert.match(result.content, /cannot update State directly/); });
test("evidence returns reviewed public summary", async () => { const result = await handleCommand("evidence", { evidence_id: "SE-EV-20260925-000001" }, options); assert.match(result.content, /Review: ACCEPTED/); });
test("Discord response suppresses mentions", () => { const response = discordResponse({ content: "@everyone", ephemeral: false }); assert.deepEqual(response.data.allowed_mentions.parse, []); });
test("server specification is invite-only and least privilege", () => { const spec = JSON.parse(readFileSync(new URL("./discord-server-spec.json", import.meta.url))); assert.equal(spec.access, "INVITE_ONLY"); assert.equal(spec.member_cap, 15); assert.deepEqual(spec.privileged_intents, []); assert.equal(spec.bot_permissions.includes("ADMINISTRATOR"), false); assert.equal(spec.automatic_invites, false); });
test("guild verification uses the official Bot API and rejects excess privilege", async () => {
  const spec = JSON.parse(readFileSync(new URL("./discord-server-spec.json", import.meta.url)));
  const categories = Object.keys(spec.categories).map((name, index) => ({ id: `c${index}`, name, type: 4 }));
  const channels = Object.values(spec.categories).flat().map((name, index) => ({ id: `t${index}`, name, type: 0 }));
  const payloads = {
    "/api/v10/oauth2/applications/@me": { id: "app", bot: { id: "bot" }, flags: 0 },
    "/api/v10/users/@me": { id: "bot" },
    "/api/v10/guilds/guild": { id: "guild" },
    "/api/v10/guilds/guild/roles": [{ id: "guild", name: "@everyone", permissions: "0" }, ...spec.roles.map((name, index) => ({ id: `r${index}`, name, permissions: "0" }))],
    "/api/v10/guilds/guild/channels": [...categories, ...channels],
    "/api/v10/guilds/guild/members/bot": { roles: [] },
  };
  const seen = [];
  const apiFetch = async (url, init) => { seen.push({ url, auth: init.headers.authorization }); return new Response(JSON.stringify(payloads[new URL(url).pathname]), { status: 200 }); };
  const result = await verifyGuild({ applicationId: "app", guildId: "guild", token: "secret", fetcher: apiFetch, spec });
  assert.equal(result.pass, true); assert.equal(result.administrator, false); assert.equal(result.privileged_intents, false);
  assert.ok(seen.every((call) => call.url.startsWith("https://discord.com/api/v10/"))); assert.ok(seen.every((call) => call.auth === "Bot secret"));
  payloads["/api/v10/guilds/guild/roles"][0].permissions = "8";
  const excessive = await verifyGuild({ applicationId: "app", guildId: "guild", token: "secret", fetcher: apiFetch, spec });
  assert.equal(excessive.pass, false); assert.equal(excessive.administrator, true);
});
test("command registration is guild-scoped", async () => {
  let request;
  const apiFetch = async (url, init) => { request = { url, init }; return new Response(JSON.stringify(COMMANDS), { status: 200 }); };
  const registered = await registerGuildCommands({ applicationId: "app", guildId: "guild", token: "secret", commands: COMMANDS, fetcher: apiFetch });
  assert.match(request.url, /applications\/app\/guilds\/guild\/commands$/); assert.equal(request.init.method, "PUT"); assert.equal(registered.length, COMMANDS.length);
});

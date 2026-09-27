import { buildContextFitScope, createWatchCycle, D1DecisionExecutionStore, preflightGapVerification, QuoteEngine } from "./phase5b-core.js";

const headers = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" };
const json = (data, status = 200) => new Response(JSON.stringify({ api_version: "SE_API_v1", data, meta: {}, links: {} }), { status, headers });
const error = (code, message, status = 400) => new Response(JSON.stringify({ api_version: "SE_API_v1", error: { code, message, request_id: `SE-HTTP-${crypto.randomUUID()}` } }), { status, headers });
const exact = (value, keys) => value && typeof value === "object" && !Array.isArray(value) && Object.keys(value).every((key) => keys.has(key));
async function body(request) {
  if (!String(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) throw Object.assign(new Error("Content-Type must be application/json."), { code: "UNSUPPORTED_MEDIA_TYPE", status: 415 });
  const text = await request.text(); if (new TextEncoder().encode(text).byteLength > 65_536) throw Object.assign(new Error("Request body too large."), { code: "PAYLOAD_TOO_LARGE", status: 413 });
  try { return JSON.parse(text); } catch { throw Object.assign(new Error("Malformed JSON."), { code: "MALFORMED_JSON", status: 400 }); }
}

export async function handlePhase5bApi(request, env, { inventory = null, store = null, authorize = null, quoteEngine = new QuoteEngine() } = {}) {
  const url = new URL(request.url), path = url.pathname, method = request.method;
  const publicGap = path.match(/^\/api\/v1\/events\/(SE-EVENT-800001)\/gaps$/);
  if (method === "GET" && publicGap) return inventory ? json({ event_id: inventory.event_id, as_of: inventory.as_of, primary_gap: inventory.primary_gap, dimensions: inventory.dimensions }) : error("EVENT_NOT_FOUND", "800V decision inventory is unavailable.", 404);
  if (!path.startsWith("/api/v1/decision-requests") && path !== "/api/v1/context-fit" && path !== "/api/v1/watch-cycles") return null;
  try {
    if (!authorize) return error("ACCESS_DENIED", "Protected access required.", 403);
    const actor = await authorize(request, env, env.DECISION_EXECUTION_AUD || env.ADMIN_API_AUD);
    store ||= env.CUSTOMER_CASES_DB ? new D1DecisionExecutionStore(env.CUSTOMER_CASES_DB) : null;
    if (!store) return error("DECISION_PLANE_UNAVAILABLE", "Protected decision plane is unavailable.", 503);
    if (method === "POST" && path === "/api/v1/decision-requests") {
      const input = await body(request), allowed = new Set(["claim", "decision_context", "decision_deadline", "jurisdiction", "system_boundary", "dimension_id"]);
      if (!exact(input, allowed)) return error("UNEXPECTED_FIELD", "Unexpected decision-request field.");
      preflightGapVerification(input, inventory);
      const item = await store.create(input); return json({ request_id: item.request_id, state: item.state, visibility: item.visibility }, 201);
    }
    const match = path.match(/^\/api\/v1\/decision-requests\/([^/]+)(?:\/(preflight|quote|accept|payment|rdl|status|delivery))?$/);
    if (match) {
      const item = await store.get(match[1]); if (!item) return error("REQUEST_NOT_FOUND", "Decision request not found.", 404);
      const action = match[2];
      if (method === "GET" && (!action || action === "status")) return json({ request_id: item.request_id, state: item.state, created_at: item.created_at, updated_at: item.updated_at, quote: item.quote ? { quote_id: item.quote.quote_id, price_status: item.quote.price_status } : null, payment_status: item.payment?.status || "NOT_CONFIRMED", rdl_bound: Boolean(item.rdl_binding) });
      if (method === "POST" && action === "preflight") {
        const result = preflightGapVerification(item.input, inventory); item.preflight = result;
        await store.update(item); await store.transition(item.request_id, "PREFLIGHT_COMPLETE", { actor: actor.email || "AUTHORIZED_OPERATOR", reason: "PREFLIGHT_RECORDED" }); return json(result);
      }
      if (method === "POST" && action === "quote") {
        const input = await body(request), allowed = new Set(["envelope_id", "costs", "currency", "valid_until"]);
        if (!exact(input, allowed) || item.state !== "PREFLIGHT_COMPLETE") return error("QUOTE_NOT_ALLOWED", "Preflight must be complete and fields must be valid.", 409);
        item.quote = quoteEngine.createQuote({ request_id: item.request_id, ...input });
        await store.update(item); await store.transition(item.request_id, "QUOTE_ISSUED", { actor: actor.email || "AUTHORIZED_OPERATOR", reason: "QUOTE_ISSUED" }); return json(item.quote, 201);
      }
      if (method === "POST" && action === "accept") {
        let updated = await store.transition(item.request_id, "QUOTE_ACCEPTED", { actor: actor.email || "AUTHORIZED_OPERATOR", reason: "QUOTE_ACCEPTED" });
        updated = await store.transition(item.request_id, "PAYMENT_PENDING", { actor: actor.email || "AUTHORIZED_OPERATOR", reason: "PAYMENT_REQUESTED" }); return json({ request_id: item.request_id, state: updated.state });
      }
      if (method === "POST" && action === "payment") {
        const input = await body(request), allowed = new Set(["reference", "override"]); if (!exact(input, allowed)) return error("UNEXPECTED_FIELD", "Unexpected payment field.");
        const updated = await store.confirmPayment(item.request_id, { reference: input.reference, override: input.override === true, actor: actor.email || "AUTHORIZED_OPERATOR" }); return json({ request_id: item.request_id, state: updated.state, payment_status: updated.payment.status });
      }
      if (method === "POST" && action === "rdl") {
        const input = await body(request), allowed = new Set(["cutoff_at", "envelope_id", "provenance_fields", "cost_caps"]); if (!exact(input, allowed)) return error("UNEXPECTED_FIELD", "Unexpected RDL binding field.");
        const updated = await store.bindRdl(item.request_id, input, actor.email || "AUTHORIZED_OPERATOR"); return json({ request_id: item.request_id, state: updated.state, rdl_binding: updated.rdl_binding });
      }
      if (method === "GET" && action === "delivery") {
        const delivery = await store.getDelivery(item.request_id); return delivery ? json(delivery) : error("DELIVERY_NOT_FOUND", "Delivery is not ready.", 404);
      }
    }
    if (method === "POST" && path === "/api/v1/context-fit") return json(buildContextFitScope(await body(request)), 201);
    if (method === "POST" && path === "/api/v1/watch-cycles") return json(createWatchCycle(await body(request)), 201);
    return error("ROUTE_NOT_FOUND", "Decision execution route not found.", 404);
  } catch (cause) {
    if (cause instanceof Response) return error("ACCESS_DENIED", await cause.text(), cause.status);
    return error(cause.code || cause.message || "INTERNAL_ERROR", cause.status ? cause.message : "Decision execution request failed.", cause.status || 400);
  }
}

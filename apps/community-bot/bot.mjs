export const COMMANDS = Object.freeze([
  { name: "state", description: "Inspect the current recorded State", options: [{ name: "subject", description: "Subject name or SE-SUBJ id", type: 3, required: true }] },
  { name: "change", description: "Inspect a recorded Change", options: [{ name: "change", description: "Change id or subject", type: 3, required: true }] },
  { name: "request", description: "Open the protected Research Request flow" },
  { name: "challenge", description: "Challenge an Evidence Chain", options: [{ name: "state_id", description: "Recorded State id", type: 3, required: true }] },
  { name: "evidence", description: "Inspect a public Evidence record", options: [{ name: "evidence_id", description: "Evidence id", type: 3, required: true }] },
]);

const clean = (value, limit = 300) => String(value || "").replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, limit);
const short = (value, limit = 900) => clean(value, limit);
async function api(base, path, fetcher) {
  const response = await fetcher(`${base.replace(/\/$/, "")}/api/v1${path}`, { headers: { accept: "application/json" } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error?.message || "SE_API_v1 unavailable");
  return body.data;
}
async function findSubject(base, query, fetcher) {
  const list = await api(base, "/subjects", fetcher), needle = clean(query).toLowerCase();
  const summary = list.items.find((item) => item.subject_id.toLowerCase() === needle || item.canonical_name.toLowerCase().includes(needle));
  if (!summary) throw new Error("Subject not found.");
  return summary;
}
const link = (base, path) => `${base.replace(/\/$/, "")}${path}`;
export async function handleCommand(name, options = {}, { apiBase = "https://structevidence.com", fetcher = fetch } = {}) {
  if (name === "request") return { ephemeral: true, content: `Keep private context out of Discord. Open the protected Request flow: ${link(apiBase, "/request")}` };
  if (name === "challenge") {
    const state = clean(options.state_id, 40);
    if (!/^SE-ST-[0-9]{8}-[0-9]{6}$/.test(state)) throw new Error("A valid State id is required.");
    return { ephemeral: true, content: `A Challenge starts review and cannot update State directly. Submit privately: ${link(apiBase, `/challenge/${state}`)}` };
  }
  if (name === "evidence") {
    const id = clean(options.evidence_id, 40), evidence = await api(apiBase, `/evidence/${encodeURIComponent(id)}`, fetcher);
    return { ephemeral: false, content: [`**${short(evidence.normalized_claim)}**`, `Review: ${evidence.review.status}`, `Published: ${evidence.published_at || "not recorded"}`, `Observed: ${evidence.observed_at}`, link(apiBase, `/evidence/${id}`)].join("\n") };
  }
  if (name === "state") {
    const subject = await findSubject(apiBase, options.subject, fetcher);
    const [current, history, changes] = await Promise.all([api(apiBase, `/subjects/${subject.subject_id}/state`, fetcher), api(apiBase, `/subjects/${subject.subject_id}/states`, fetcher), api(apiBase, `/subjects/${subject.subject_id}/changes`, fetcher)]);
    const previous = history.length > 1 ? history.at(-2).state_code : "NONE", change = changes.at(-1);
    return { ephemeral: false, content: [`**${subject.canonical_name}**`, `Current State: ${current.state_code}`, `Observed At: ${current.observed_at}`, `Previous State: ${previous}`, `What Changed: ${change?.change_summary || "First recorded State"}`, `Accepted Evidence: ${current.accepted_evidence_count}`, `Counter Evidence: ${current.counter_evidence_count}`, `Unknowns: ${current.unknown_count}`, link(apiBase, `/states/${subject.subject_id}`)].join("\n") };
  }
  if (name === "change") {
    let change;
    if (/^SE-CHG-[0-9]{8}-[0-9]{6}$/.test(clean(options.change, 40))) change = await api(apiBase, `/changes/${options.change}`, fetcher);
    else {
      const subject = await findSubject(apiBase, options.change, fetcher), changes = await api(apiBase, `/subjects/${subject.subject_id}/changes`, fetcher); change = changes.at(-1);
    }
    if (!change) throw new Error("No Change recorded.");
    return { ephemeral: false, content: [`**${change.previous.state_code || "NONE"} → ${change.current.state_code}**`, `Changed At: ${change.detected_at}`, `Trigger Evidence: ${change.trigger_evidence_ids.length}`, `Unknown Resolved: ${change.unknowns_resolved.length}`, `Counter Evidence Change: +${change.counter_evidence_added.length} / -${change.counter_evidence_removed.length}`, short(change.change_summary), link(apiBase, `/changes/${change.change_id}`)].join("\n") };
  }
  throw new Error("Unsupported command.");
}

export function discordResponse(result) {
  return { type: 4, data: { content: result.content.slice(0, 2000), flags: result.ephemeral ? 64 : 0, allowed_mentions: { parse: [] } } };
}

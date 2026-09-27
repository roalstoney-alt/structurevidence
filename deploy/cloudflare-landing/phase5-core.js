export const PHASE5_DOMAINS = Object.freeze([
  "technology", "industry", "geography", "human_geography", "culture",
  "environment", "infrastructure", "ecology", "institution",
]);
export const CHANGE_MECHANISMS = Object.freeze([
  "EMERGENCE", "DECLINE", "SUBSTITUTION", "MIGRATION", "CONCENTRATION", "FRAGMENTATION",
  "ADOPTION", "ABANDONMENT", "RECONFIGURATION", "RECOVERY", "CONSTRAINT_RELEASE",
]);
export const REALITY_RADAR_CLASSES = Object.freeze([
  "NEW_SUPPORTING_EVIDENCE", "NEW_COUNTER_EVIDENCE", "STATE_CHANGE_CANDIDATE",
  "UNKNOWN_RESOLUTION_CANDIDATE", "NEW_BRANCH_CANDIDATE", "OUTCOME_EVIDENCE", "DUPLICATE", "NOISE",
]);
export const RDL_LEVELS = Object.freeze(["L0_SCAN", "L0_VERIFY", "L1_VERIFY", "L2_DEEP"]);
export const UNKNOWN_COST = "UNKNOWN";

function sorted(value) {
  if (Array.isArray(value)) return value.map(sorted);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sorted(value[key])]));
  return value;
}
export function canonicalSerialize(value) { return JSON.stringify(sorted(value)); }
export async function sha256(value) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}
export async function objectHash(value) { return sha256(canonicalSerialize(value)); }
export async function merkleRoot(values) {
  if (!values.length) return sha256("");
  let layer = await Promise.all(values.map(objectHash));
  while (layer.length > 1) {
    const next = [];
    for (let index = 0; index < layer.length; index += 2) next.push(await sha256(layer[index] + (layer[index + 1] || layer[index])));
    layer = next;
  }
  return layer[0];
}

export class ProofProvider {
  constructor(level) { this.level = level; }
  async createProof() { throw new Error("ProofProvider.createProof must be implemented."); }
}
export class LocalHashProvider extends ProofProvider {
  constructor() { super("P0_LOCAL_HASH"); }
  async createProof(projection) { return { provider: "LocalHashProvider", proof_level: this.level, object_hash: await objectHash(projection) }; }
}
export class SnapshotChainProvider extends ProofProvider {
  constructor() { super("P1_SNAPSHOT_CHAIN"); }
  async createProof(projection, previousSnapshotHash = null) {
    const parts = [projection.subject, projection.current_state, projection.change_history, projection.supporting_evidence,
      projection.counter_evidence, projection.open_unknowns, projection.branches, projection.outcomes, projection.rdl_history];
    const merkle_root = await merkleRoot(parts);
    const snapshot_hash = await objectHash({ merkle_root, previous_snapshot_hash: previousSnapshotHash });
    return { provider: "SnapshotChainProvider", proof_level: this.level, merkle_root, previous_snapshot_hash: previousSnapshotHash, snapshot_hash };
  }
}
export class IPFSProvider extends ProofProvider {
  constructor() { super("P2_EXTERNAL_CID"); }
  async createProof() { throw new Error("P2_EXTERNAL_CID_NOT_ACTIVATED"); }
}
export class ReplicatedProofProvider extends ProofProvider {
  constructor() { super("P3_REPLICATED_PROOF"); }
  async createProof() { throw new Error("P3_REPLICATED_PROOF_NOT_ACTIVATED"); }
}

const time = (item) => item?.observed_at || item?.detected_at || item?.reported_at || item?.recorded_at || item?.created_at || null;
const before = (item, boundary) => !boundary || ["observed_at", "recorded_at", "detected_at", "reported_at", "created_at", "ended_at"]
  .filter((key) => item?.[key])
  .every((key) => Number.isFinite(Date.parse(item[key])) && Date.parse(item[key]) <= boundary);
const sortedByTime = (items) => [...items].sort((a, b) => String(time(a)).localeCompare(String(time(b))));
const PRIVATE_KEYS = new Set(["provenance", "raw_reference", "requester_ref", "challenger_ref", "commercial_result"]);
function publicObject(value) {
  if (Array.isArray(value)) return value.map(publicObject);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).filter(([key]) => !PRIVATE_KEYS.has(key)).map(([key, item]) => [key, publicObject(item)]));
  return value;
}

export async function projectStructuralEvent(subjectId, publicData, { asOf = null, rdlRuns = null } = {}) {
  const boundary = asOf ? Date.parse(asOf) : null;
  if (asOf && !Number.isFinite(boundary)) throw Object.assign(new Error("Timestamp must be RFC 3339."), { status: 400, code: "INVALID_AS_OF" });
  const subject = (publicData.subjects || []).find((item) => item.subject_id === subjectId);
  if (!subject) return null;
  const states = sortedByTime((publicData.states || []).filter((item) => item.subject_id === subjectId && before(item, boundary)));
  const currentState = states.at(-1) || null;
  const changes = sortedByTime((publicData.changes || []).filter((item) => item.subject_id === subjectId && before(item, boundary)));
  const evidence = sortedByTime((publicData.evidence || []).filter((item) => item.subject_id === subjectId && before(item, boundary)));
  const accepted = new Set(currentState?.accepted_evidence_ids || []), counters = new Set(currentState?.counter_evidence_ids || []);
  const branches = sortedByTime((publicData.branches || []).filter((item) => item.subject_id === subjectId && before(item, boundary)));
  const outcomes = sortedByTime((publicData.outcomes || []).filter((item) => item.subject_id === subjectId && item.visibility === "PUBLIC" && item.authorization_for_public_use === true && before(item, boundary)));
  const runs = sortedByTime((rdlRuns || publicData.rdlRuns || []).filter((item) => item.subject_id === subjectId && before(item, boundary))).map(normalizeRdlRun);
  const projection = {
    projection_type: "StructuralEventProjection", projection_version: "SE_EVENT_PROJECTION_v0.1",
    event_id: `SE-EVENT-${subjectId.slice(-6)}`, as_of: asOf || null,
    subject: { subject_id: subject.subject_id, canonical_name: subject.canonical_name, domain: subject.domain || "UNKNOWN",
      subdomain: subject.subdomain || null, object_type: subject.object_type || subject.subject_type,
      spatial_scope: subject.spatial_scope || subject.geography || [], change_mechanisms: subject.change_mechanisms || [] },
    current_state: publicObject(currentState), change_history: publicObject(changes),
    supporting_evidence: publicObject(evidence.filter((item) => accepted.has(item.evidence_id))),
    counter_evidence: publicObject(evidence.filter((item) => counters.has(item.evidence_id) || item.review?.status === "COUNTER")),
    open_unknowns: currentState?.unknowns || [], branches: publicObject(branches), outcomes: publicObject(outcomes), rdl_history: publicObject(runs),
  };
  projection.proof = await new SnapshotChainProvider().createProof(projection, currentState?.chain_hash || null);
  return projection;
}

export async function projectAtlas(publicData, options = {}) {
  const values = await Promise.all((publicData.subjects || []).map((item) => projectStructuralEvent(item.subject_id, publicData, options)));
  return values.filter(Boolean).map((event) => ({ event_id: event.event_id, subject: event.subject,
    current_state: event.current_state ? { state_id: event.current_state.state_id, state_code: event.current_state.state_code, observed_at: event.current_state.observed_at } : null,
    open_unknown_count: event.open_unknowns.length, branch_count: event.branches.length, outcome_count: event.outcomes.length, proof_level: event.proof.proof_level }));
}

export function normalizeRdlCost(value) { return value === undefined || value === null || value === "" ? UNKNOWN_COST : value; }
export function normalizeRdlRun(run) {
  return { ...run, compute_cost: normalizeRdlCost(run.compute_cost), search_cost: normalizeRdlCost(run.search_cost), observed_credit_delta: normalizeRdlCost(run.observed_credit_delta) };
}
export function nextRdlLevel({ research_level, materially_changes_state = false, materially_changes_unknown = false, materially_changes_branch = false, materially_changes_outcome = false, manual_approval = false }) {
  const material = materially_changes_state || materially_changes_unknown || materially_changes_branch || materially_changes_outcome;
  if (research_level === "L0_SCAN") return "L0_VERIFY";
  if (!material && !manual_approval) return "STOP_NO_STATE_CHANGE";
  const index = RDL_LEVELS.indexOf(research_level);
  return index >= 0 && index < RDL_LEVELS.length - 1 ? RDL_LEVELS[index + 1] : research_level;
}
export function classifyRealityRadarCandidate(candidate, { duplicate = false } = {}) {
  if (duplicate) return "DUPLICATE";
  if (!candidate || !candidate.public_source || !candidate.normalized_claim) return "NOISE";
  if (candidate.outcome_reference) return "OUTCOME_EVIDENCE";
  if (candidate.resolves_unknown) return "UNKNOWN_RESOLUTION_CANDIDATE";
  if (candidate.branch_signal) return "NEW_BRANCH_CANDIDATE";
  if (candidate.state_change_signal) return "STATE_CHANGE_CANDIDATE";
  if (candidate.counter_to?.length) return "NEW_COUNTER_EVIDENCE";
  return "NEW_SUPPORTING_EVIDENCE";
}

export function derivePhase5Metrics(publicData) {
  const runs = (publicData.rdlRuns || []).map(normalizeRdlRun);
  const known = (values) => values.filter((value) => typeof value === "number");
  const cost = (field, denominator) => {
    const values = known(runs.map((run) => run[field]));
    return values.length && denominator > 0 ? values.reduce((sum, value) => sum + value, 0) / denominator : UNKNOWN_COST;
  };
  const evidenceCount = (publicData.evidence || []).length;
  const transitions = (publicData.changes || []).length;
  const resolved = (publicData.changes || []).reduce((sum, item) => sum + (item.unknowns_resolved || []).length, 0);
  const outcomes = (publicData.outcomes || []).filter((item) => item.visibility === "PUBLIC" && item.authorization_for_public_use === true).length;
  return {
    ACTIVE_EVOLVING_OBJECTS: (publicData.subjects || []).filter((item) => item.status !== "ARCHIVED").length,
    NEW_EVIDENCE: evidenceCount,
    COUNTER_EVIDENCE: (publicData.evidence || []).filter((item) => item.review?.status === "COUNTER").length,
    STATE_CHANGE_CANDIDATES: 0,
    STATE_TRANSITIONS: transitions,
    UNKNOWNS_RESOLVED: resolved,
    NEW_BRANCHES: (publicData.branches || []).length,
    OUTCOMES_CAPTURED: outcomes,
    SNAPSHOT_DEPTH: Math.max(0, ...(publicData.subjects || []).map((subject) => (publicData.states || []).filter((state) => state.subject_id === subject.subject_id).length)),
    RDL_RUNS: runs.length,
    COST_PER_EVIDENCE: cost("compute_cost", evidenceCount),
    COST_PER_STATE_CHANGE: cost("compute_cost", transitions),
    COST_PER_UNKNOWN_RESOLVED: cost("compute_cost", resolved),
    COST_PER_OUTCOME: cost("compute_cost", outcomes),
  };
}

import { objectHash } from "./phase5-core.js";
import { atomicClaimGate, claimScopeFingerprint, createSearchProvenance, createStopPointV2, matchScopeFingerprint, publicSearchProvenance, STOP_STATES } from "./phase5c-spv.js";

export const CLAIM_PROJECTION_VERSION = "SE_PUBLIC_CLAIM_v0.2";
export const CLAIM_ID = "SE-CLAIM-800V-001";
export const CLAIM_SLUG = "named-800vdc-field-operation";
export { STOP_STATES } from "./phase5c-spv.js";
export const CLAIM_RESULTS = Object.freeze(["EXISTING_STOP_POINT", "NEW_VERIFIABLE_CLAIM_QUOTE", "CONTEXT_MAPPING_QUOTE", "NON_FALSIFIABLE_RETURN", "INSUFFICIENT_INPUT"]);
export const EXTERNAL_SEARCH_BEFORE_PAYMENT = 0;

const CANARY_CLAIM = "Qualifying public evidence establishes named commercial field operation of the defined 800VDC data-center power architecture.";
const normalizeText = (value) => String(value || "").normalize("NFKC").toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, " ").trim();
const unique = (items) => [...new Set(items.filter(Boolean))];

export function normalizeClaim(input) {
  const raw = String(input?.claim || "").trim();
  const normalized = normalizeText(raw);
  const has800v = /800\s*v(?:dc)?/.test(normalized);
  const deployment = /field operation|field deployment|commercial operation|production deployment|现场运行|商业运行/.test(normalized);
  const operatingHistory = /operating history|reliability duration|运行历史|可靠性/.test(normalized);
  const timeMatch = raw.match(/\b(20\d{2}(?:-\d{2}(?:-\d{2})?)?)\b/);
  const vague = /\b(dominate|best|leading|significant|promising|mature|soon|likely|basically|almost)\b/i.test(raw);
  const concrete = /\b(named|qualifying|public evidence|record|deployed|deployment|operation|operating|commissioned|establishes?)\b/i.test(raw) || /证据|记录|部署|运行/.test(raw);
  const falsifiable = raw.length >= 18 && has800v && (deployment || operatingHistory) && concrete && !vague;
  const atomic = atomicClaimGate(raw);
  const result = {
    projection_type: "ClaimNormalizationProjection", projection_version: "SE_CLAIM_NORMALIZATION_v0.1",
    raw_claim: raw, normalized_claim: normalized, subject: has800v ? "800VDC_DATA_CENTER_POWER_ARCHITECTURE" : "UNRESOLVED",
    predicate: deployment ? "NAMED_COMMERCIAL_OR_FIELD_OPERATION" : operatingHistory ? "OPERATING_HISTORY" : "UNRESOLVED",
    scope: has800v ? "DEFINED_800VDC_ARCHITECTURE" : "UNRESOLVED", jurisdiction: String(input?.jurisdiction || "GLOBAL_PUBLIC_RECORD").trim(),
    time_boundary: timeMatch?.[1] || String(input?.use_deadline || "").trim() || "UNRESOLVED",
    decision_context: String(input?.decision_context || "").trim(), claim_type: deployment ? "EXISTENCE" : operatingHistory ? "DURATION_OR_RELIABILITY" : "UNRESOLVED",
    falsifiable: falsifiable && atomic.atomic, atomic_claim: atomic.atomic, atomic_gate: atomic.ATOMIC_CLAIM_REQUIRED, external_retrieval: 0,
  };
  result.scope_fingerprint = claimScopeFingerprint(result);
  return result;
}

export function decompositionDraft(rawClaim) {
  return { type: "CLAIM_DECOMPOSITION_DRAFT", original_claim: String(rawClaim || "").trim(), proposed_verifiable_claim: "By <cutoff>, qualifying public evidence establishes named commercial or field operation of the defined 800VDC data-center power architecture.", external_verification_started: false };
}

export async function build800vPublicClaim(record, researchRecord) {
  if (!record?.core?.record_hash || !researchRecord?.core?.record_hash) throw new Error("CANONICAL_CLAIM_SOURCES_REQUIRED");
  const searchLog = await createSearchProvenance(researchRecord);
  const publicSearch = publicSearchProvenance(searchLog);
  const base = { claim_id: CLAIM_ID, stable_claim_slug: CLAIM_SLUG, canonical_subject_id: record.core.subject_id, canonical_state_refs: [record.core.record_id], source_url: `https://structevidence.com/claims/${CLAIM_SLUG}`, projection_version: CLAIM_PROJECTION_VERSION };
  const scope = (timeBoundary) => ({ subject: "800VDC_DATA_CENTER_POWER_ARCHITECTURE", technical_boundary: "MATERIALLY_RELEVANT_SST_TO_800VDC_DATA_CENTER_ARCHITECTURE", deployment_class: "COMMERCIAL_FIELD_OPERATION", jurisdiction: "GLOBAL_PUBLIC_RECORD", attribution_scope: "ONE_ATTRIBUTABLE_OPERATOR", time_boundary: timeBoundary, population_scope: "ONE_NAMED_PRODUCTION_DEPLOYMENT_INSTANCE" });
  const versions = [
    { ...base, version: 1, as_of: "2026-08-01T23:59:59Z", canonical_evidence_refs: [], stop_point: createStopPointV2({ CLAIM: CANARY_CLAIM, SCOPE: scope("EVIDENCE_OBSERVABLE_BY_2026-08-01T23:59:59Z"), AS_OF: "2026-08-01T23:59:59Z", FRESHNESS_STATUS: "UNASSESSED", STATE: "UNKNOWN", SUPPORTS: ["The bounded StructEvidence knowledge record had not established a qualifying named field-operation record at this cutoff."], DOES_NOT_SUPPORT: ["Absence of a qualifying record in the knowledge record does not prove that no deployment existed."], QUALIFYING_RECORDS: [], REJECTED_OR_COUNTER: [], SEARCH_PROVENANCE: { verification_level: "V0_LIBRARY_ONLY", query_count: 0, source_count: 0, deep_review_count: 0, qualifying_count: 0, rejected_count: 0, access_limited_count: "UNKNOWN", stop_reason: "HUMAN_STOP", cutoff: "2026-08-01T23:59:59Z" }, SOURCE_ACCESS_STATUS: [{ gap: "Named attributable field-operation record", status: "UNKNOWN_ACCESS" }, { gap: "Operating history", status: "SOURCE_CONTROLLED" }], DIRECT_INQUIRY_STATUS: "NOT_SENT", VERIFICATION_DEPTH: "V0_LIBRARY_ONLY", OPEN_GAP_IF_UNKNOWN: ["Named attributable field-operation record", "Operating history", "Independent validation"], NEXT_MINIMUM_VERIFICATION: "One dated, attributable operator record showing field operation.", NOT_A: ["recommendation", "forecast", "proof of non-existence", "industry-adoption metric"], CLAIM_ID, VERSION: 1 }) },
    { ...base, version: 2, as_of: researchRecord.core.known_at, canonical_evidence_refs: unique([...(researchRecord.research_record.new_evidence_refs || []), ...(researchRecord.research_record.counter_evidence_refs || [])]), stop_point: createStopPointV2({ CLAIM: CANARY_CLAIM, SCOPE: scope(`EVIDENCE_OBSERVABLE_BY_${researchRecord.core.known_at}`), AS_OF: researchRecord.core.known_at, FRESHNESS_STATUS: "UNASSESSED", STATE: "ATTRIBUTABLE_ONLY", SUPPORTS: ["One attributable operator record identifies a named operational site and describes commercial operation of a materially relevant SST-to-800VDC architecture.", "Human review accepted this only as single-instance architecture field-deployment evidence."], DOES_NOT_SUPPORT: ["Industry-wide adoption", "Multi-operator replication", "Long-term operating reliability", "Independent performance validation", "Economic superiority", "Universal production readiness", "A canonical R4→R5 transition"], QUALIFYING_RECORDS: researchRecord.research_record.new_evidence_refs || [], REJECTED_OR_COUNTER: unique([...(researchRecord.research_record.source_refs_rejected || []), ...(researchRecord.research_record.counter_evidence_refs || [])]), SEARCH_PROVENANCE: publicSearch, SOURCE_ACCESS_STATUS: [{ gap: "Field-deployment existence", status: "PUBLIC" }, { gap: "Long-term operating history and reliability", status: "SOURCE_CONTROLLED" }, { gap: "Independent performance validation", status: "KNOWN_TO_EXIST_NOT_ACCESSIBLE" }], DIRECT_INQUIRY_STATUS: "NOT_SENT", VERIFICATION_DEPTH: "V2_PRIMARY_SOURCE_SEARCH", OPEN_GAP_IF_UNKNOWN: researchRecord.research_record.unknowns_remaining || [], NEXT_MINIMUM_VERIFICATION: "Direct written inquiry for a dated 12-month operating and reliability record.", NOT_A: ["recommendation", "forecast", "industry-adoption metric", "universal production-readiness determination"], CLAIM_ID, VERSION: 2 }) },
  ];
  for (const version of versions) {
    if (!STOP_STATES.includes(version.stop_point.STATE) || !version.stop_point.boundary_complete) throw new Error("PUBLICATION_VALIDATION_FAIL");
    version.evidence_as_of = version.version === 2 ? researchRecord.core.effective_at : version.stop_point.AS_OF;
    version.knowledge_as_of = version.as_of;
    version.source_url = `https://structevidence.com/claims/${CLAIM_SLUG}/versions/${version.version}`;
    version.projection_hash = await objectHash({ claim_id: version.claim_id, version: version.version, evidence_as_of: version.evidence_as_of, knowledge_as_of: version.knowledge_as_of, canonical_state_refs: version.canonical_state_refs, canonical_evidence_refs: version.canonical_evidence_refs, stop_point: version.stop_point });
  }
  return Object.freeze({ claim_id: CLAIM_ID, stable_claim_slug: CLAIM_SLUG, versions: Object.freeze(versions), latest_version: 2 });
}

export function selectClaimVersion(libraryClaim, asOf = null) {
  if (!asOf) return libraryClaim.versions.at(-1);
  const boundary = Date.parse(asOf.length === 10 ? `${asOf}T23:59:59Z` : asOf);
  if (!Number.isFinite(boundary)) throw Object.assign(new Error("INVALID_AS_OF"), { status: 400 });
  const version = libraryClaim.versions.filter((item) => Date.parse(item.as_of) <= boundary).at(-1);
  if (!version) throw Object.assign(new Error("CLAIM_NOT_KNOWN_AT_AS_OF"), { status: 404 });
  return version;
}

export function selectClaimVersionNumber(libraryClaim, versionNumber) {
  const number = Number(versionNumber);
  if (!Number.isInteger(number) || number < 1) throw Object.assign(new Error("INVALID_CLAIM_VERSION"), { status: 400 });
  const version = libraryClaim.versions.find((item) => item.version === number);
  if (!version) throw Object.assign(new Error("CLAIM_VERSION_NOT_FOUND"), { status: 404 });
  return version;
}

export function matchClaimLibrary(normalization) {
  const canonicalNormalization = normalizeClaim({ claim: CANARY_CLAIM, jurisdiction: "GLOBAL_PUBLIC_RECORD" });
  const structural = matchScopeFingerprint(normalization.scope_fingerprint, canonicalNormalization.scope_fingerprint);
  const match_type = normalization.normalized_claim === normalizeText(CANARY_CLAIM) ? "EXACT_MATCH" : structural;
  return { match_type, claim_id: ["EXACT_MATCH", "ISOMORPHIC_MATCH"].includes(match_type) ? CLAIM_ID : null, scope_fingerprint: normalization.scope_fingerprint, external_search_performed: false, model_cost: 0, retrieval_cost: 0 };
}

export function quoteNewClaim(normalization, result = "NEW_VERIFIABLE_CLAIM_QUOTE") {
  const sourceControlled = normalization.predicate === "OPERATING_HISTORY";
  return { result, SCOPE: normalization.scope_fingerprint, CUTOFF: normalization.time_boundary, QUERY_LIMIT: 4, SOURCE_LIMIT: 10, DEEP_REVIEW_LIMIT: 1, EXTERNAL_DATA_CAP: 0, HUMAN_REVIEW_CAP: "SET_IN_WRITTEN_SCOPE", DEADLINE_FEASIBILITY: "HUMAN_REVIEW_REQUIRED", VERIFICATION_MODE: sourceControlled ? "SOURCE_CONTROLLED_INFORMATION" : "PUBLIC_EVIDENCE_INSUFFICIENT", NEXT_MINIMUM_VERIFICATION: sourceControlled ? "DIRECT_WRITTEN_INQUIRY" : "BOUNDED_PUBLIC_SEARCH", DOMAIN_RISK_CLASS: "R1_PROFESSIONAL", DELIVERABLE: "VERSIONED_CITABLE_STOP_POINT", PRICE: "HUMAN_QUOTE_REQUIRED", DELIVERY_TARGET: "SET_IN_WRITTEN_SCOPE", PAYMENT_BUYS_PROCESS: true, PAYMENT_BUYS_PREFERRED_OUTCOME: false, favorable_state_promised: false, payment_confirmed: false, new_external_retrieval: 0 };
}

export function routeClaimIntake(input, libraryClaim) {
  const claim = String(input?.claim || "").trim(), context = String(input?.decision_context || "").trim(), deadline = String(input?.use_deadline || "").trim();
  if (!claim || !context || !deadline) return { result: "INSUFFICIENT_INPUT", workflow_state: "SCOPE_AND_CUTOFF", missing: [["claim", claim], ["decision_context", context], ["use_deadline", deadline]].filter(([, value]) => !value).map(([key]) => key), research_started: false, external_search: 0 };
  if (input?.single_proposition_confirmed === false || input?.single_proposition_confirmed === "false") return { result: "NON_FALSIFIABLE_RETURN", workflow_state: "DECOMPOSITION_REQUIRED", decomposition: decompositionDraft(claim), research_started: false, external_search: 0 };
  const normalization = normalizeClaim(input);
  if (!normalization.atomic_claim || !normalization.falsifiable) return { result: "NON_FALSIFIABLE_RETURN", workflow_state: "DECOMPOSITION_REQUIRED", normalization, decomposition: decompositionDraft(claim), research_started: false, external_search: 0 };
  const match = matchClaimLibrary(normalization);
  if (["EXACT_MATCH", "ISOMORPHIC_MATCH"].includes(match.match_type)) return { result: "EXISTING_STOP_POINT", workflow_state: "EXISTING_STOP_POINT", normalization, match, claim: libraryClaim.versions.at(-1), research_started: false, external_search: 0 };
  const contextual = /our |internal|procurement|engineering review|technical selection/i.test(context);
  return { result: contextual ? "CONTEXT_MAPPING_QUOTE" : "NEW_VERIFIABLE_CLAIM_QUOTE", workflow_state: "QUOTE_PENDING", normalization, match, quote: quoteNewClaim(normalization, contextual ? "CONTEXT_MAPPING_QUOTE" : "NEW_VERIFIABLE_CLAIM_QUOTE"), research_started: false, external_search: 0 };
}

export const CLAIM_TRANSLATIONS = Object.freeze({
  EN: { stop: "STOP-POINT", supports: "SUPPORTS", doesNot: "DOES NOT SUPPORT", gaps: "OPEN GAP", warning: "Any summary that drops DOES_NOT_SUPPORT is incomplete." },
  "ZH-CN": { stop: "停止点", supports: "支持范围", doesNot: "不支持范围", gaps: "未解决缺口", warning: "任何省略 DOES_NOT_SUPPORT 的摘要都是不完整的。", claim: "合格的公开证据是否足以确认：已定义的 800VDC 数据中心供电架构存在具名商业现场运行？", versions: {
    1: { supports: ["截至该截止时间，有界记录尚未建立合格的具名现场运行记录。"], doesNot: ["未找到合格记录，并不证明部署不存在。"], gaps: ["具名且可归属的现场运行记录", "运行历史", "独立验证"] },
    2: { supports: ["一份可归属的运营方记录指出了具名运行地点，并描述了实质相关的 SST 至 800VDC 架构处于商业运行。", "人工审查仅将其接受为单一实例的架构现场部署证据。"], doesNot: ["行业范围采用", "多运营方复制", "长期运行可靠性", "独立性能验证", "经济性优越", "普遍生产就绪", "canonical R4→R5 转换"], gaps: ["canonical 就绪状态转换仍待人工/CML 审查", "运营方性能与效率主张的独立验证", "运行历史时长与可靠性证据", "多实体复制", "canonical 架构映射"] },
  } },
  ES: { stop: "PUNTO DE PARADA", supports: "RESPALDA", doesNot: "NO RESPALDA", gaps: "BRECHA ABIERTA", warning: "Todo resumen que omita DOES_NOT_SUPPORT está incompleto.", claim: "¿La evidencia pública admisible establece una operación comercial de campo identificada para la arquitectura definida de alimentación de centros de datos de 800 VCC?", versions: {
    1: { supports: ["En la fecha de corte, el registro acotado no había establecido una operación de campo identificada y admisible."], doesNot: ["La ausencia de un registro admisible no demuestra que no existiera un despliegue."], gaps: ["Registro atribuible de operación de campo", "Historial operativo", "Validación independiente"] },
    2: { supports: ["Un registro atribuible del operador identifica un sitio operativo y describe la operación comercial de una arquitectura SST a 800 VCC materialmente pertinente.", "La revisión humana la aceptó únicamente como evidencia de despliegue de campo de una sola instancia."], doesNot: ["Adopción en toda la industria", "Replicación entre múltiples operadores", "Fiabilidad operativa a largo plazo", "Validación independiente del rendimiento", "Superioridad económica", "Preparación universal para producción", "Transición canónica R4→R5"], gaps: ["Revisión humana/CML de la transición canónica", "Validación independiente de rendimiento y eficiencia", "Duración y fiabilidad operativas", "Replicación entre entidades", "Correspondencia con la arquitectura canónica"] },
  } },
});

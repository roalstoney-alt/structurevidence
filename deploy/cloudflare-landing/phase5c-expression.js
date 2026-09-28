export const EXPRESSION_PROJECTION_VERSION = "SE_EXPRESSION_BOUNDARY_v0.1";
export const EXPRESSION_LOCALES = Object.freeze(["EN", "ZH-CN", "ES"]);

export const STATE_EXPLANATIONS = Object.freeze({
  EN: Object.freeze({
    KNOWN: "Established only within the stated scope, cutoff, and qualifying-record boundary.",
    ATTRIBUTABLE_ONLY: "Attributable to the named entity or instance; not independently verified or generally adopted.",
    UNKNOWN: "The current material is insufficient to determine the claim; this is not evidence of non-existence.",
    NOT_ESTABLISHED: "The reviewed material has not established the proposition; this is not a finding that it is false.",
    NOT_FOUND_WITHIN_SCOPE: "A recorded search found no qualifying record inside its defined envelope; this does not address material outside that envelope.",
    CONFLICTED: "Qualifying material disagrees on a material point that remains unresolved inside the current envelope.",
  }),
  "ZH-CN": Object.freeze({
    KNOWN: "仅在列明范围、截止时间和合格记录边界内成立。",
    ATTRIBUTABLE_ONLY: "可归属到列明主体或实例；不表示已获独立验证或普遍采用。",
    UNKNOWN: "当前材料不足以确定该主张；这不是不存在的证据。",
    NOT_ESTABLISHED: "已审材料尚未建立该命题；这不等于已证伪。",
    NOT_FOUND_WITHIN_SCOPE: "已记录的检索在定义包络内未发现合格记录；不涉及包络外材料。",
    CONFLICTED: "合格材料在关键点上存在冲突，且在当前包络内尚未解决。",
  }),
  ES: Object.freeze({
    KNOWN: "Establecido únicamente dentro del alcance, fecha de corte y registros admisibles indicados.",
    ATTRIBUTABLE_ONLY: "Atribuible a la entidad o instancia indicada; no implica verificación independiente ni adopción general.",
    UNKNOWN: "El material actual no permite determinar la afirmación; no es evidencia de inexistencia.",
    NOT_ESTABLISHED: "El material revisado no ha establecido la proposición; no significa que haya sido refutada.",
    NOT_FOUND_WITHIN_SCOPE: "Una búsqueda registrada no encontró material admisible dentro de su marco; no cubre material fuera de él.",
    CONFLICTED: "El material admisible discrepa en un punto esencial aún no resuelto dentro del marco actual.",
  }),
});

const requiredScope = ["subject", "technical_boundary", "deployment_class", "jurisdiction", "attribution_scope", "time_boundary", "population_scope"];
const missing = (value) => value === null || value === undefined || value === "" || value === "UNRESOLVED";
const join = (items, locale) => items.join(locale === "ZH-CN" ? "；" : "; ");
const trimTerminal = (value) => String(value).replace(/[.;。；]+$/u, "");

function validate(version) {
  const stop = version?.stop_point;
  if (!version?.claim_id || !Number.isInteger(version?.version) || !version?.source_url || !version?.projection_hash) throw new Error("CITATION_IDENTITY_INCOMPLETE");
  if (!stop?.CLAIM || !stop?.AS_OF || !stop?.SCOPE || requiredScope.some((key) => missing(stop.SCOPE[key]))) throw new Error("EXPRESSION_SCOPE_OR_CUTOFF_INCOMPLETE");
  if (!stop?.determination?.state || !stop?.determination?.supports?.length || !stop?.determination?.does_not_support?.length || stop.boundary_complete !== true) throw new Error("EXPRESSION_BOUNDARY_INCOMPLETE");
  return stop;
}

function scopeText(scope, locale) {
  const labels = {
    EN: { ONE_ATTRIBUTABLE_OPERATOR: "one attributable operator", ONE_NAMED_PRODUCTION_DEPLOYMENT_INSTANCE: "one named production deployment instance", MATERIALLY_RELEVANT_SST_TO_800VDC_DATA_CENTER_ARCHITECTURE: "the materially relevant SST-to-800VDC data-center architecture", GLOBAL_PUBLIC_RECORD: "the global public record" },
    "ZH-CN": { ONE_ATTRIBUTABLE_OPERATOR: "一个可归属运营主体", ONE_NAMED_PRODUCTION_DEPLOYMENT_INSTANCE: "一个具名生产部署实例", MATERIALLY_RELEVANT_SST_TO_800VDC_DATA_CENTER_ARCHITECTURE: "实质相关的 SST 至 800VDC 数据中心供电架构", GLOBAL_PUBLIC_RECORD: "全球公开记录" },
    ES: { ONE_ATTRIBUTABLE_OPERATOR: "un operador atribuible", ONE_NAMED_PRODUCTION_DEPLOYMENT_INSTANCE: "una instancia identificada de despliegue en producción", MATERIALLY_RELEVANT_SST_TO_800VDC_DATA_CENTER_ARCHITECTURE: "la arquitectura materialmente pertinente de SST a 800 VCC para centros de datos", GLOBAL_PUBLIC_RECORD: "el registro público global" },
  };
  const map = labels[locale] || labels.EN;
  const values = [scope.attribution_scope, scope.population_scope, scope.technical_boundary, scope.jurisdiction].map((value) => map[value] || value);
  if (locale === "ZH-CN") return `归属 ${values[0]}；实例范围 ${values[1]}；技术边界 ${values[2]}；地区 ${values[3]}`;
  if (locale === "ES") return `atribución ${values[0]}; población ${values[1]}; límite técnico ${values[2]}; jurisdicción ${values[3]}`;
  return `attribution ${values[0]}; population ${values[1]}; technical boundary ${values[2]}; jurisdiction ${values[3]}`;
}

export function deriveExpressionBoundary(version, { locale = "EN", claim, supports, doesNotSupport } = {}) {
  const renderLocale = EXPRESSION_LOCALES.includes(locale) ? locale : "EN";
  const stop = validate(version), determination = stop.determination;
  const localizedClaim = claim || stop.CLAIM;
  const localizedSupports = (supports || determination.supports).map(trimTerminal);
  const localizedDoesNot = (doesNotSupport || determination.does_not_support).map(trimTerminal);
  if (!localizedSupports.length || !localizedDoesNot.length) throw new Error("EXPRESSION_BOUNDARY_INCOMPLETE");
  const scope = scopeText(stop.SCOPE, renderLocale);
  const evidenceAsOf = version.evidence_as_of || stop.AS_OF;
  const knowledgeAsOf = version.knowledge_as_of || version.as_of;
  const stateExplanation = STATE_EXPLANATIONS[renderLocale][determination.state];
  let decisionSentence, shortSummary, citationText;
  if (renderLocale === "ZH-CN") {
    decisionSentence = `截至证据时间 ${evidenceAsOf}（StructEvidence 知识截点 ${knowledgeAsOf}），在${scope}内，状态为 ${determination.state}：${join(localizedSupports, renderLocale)}。不能据此推出：${join(localizedDoesNot, renderLocale)}。`;
    shortSummary = `${determination.state}（截至 ${evidenceAsOf}）：${localizedSupports[0]}；但不能据此推出：${localizedDoesNot[0]}。`;
    citationText = `StructEvidence 主张 ${version.claim_id}，版本 ${version.version}。主张：${localizedClaim} 范围：${scope}。证据截止：${evidenceAsOf}；知识截点：${knowledgeAsOf}。状态：${determination.state}。能支持：${join(localizedSupports, renderLocale)}。不能据此推出：${join(localizedDoesNot, renderLocale)}。稳定链接：${version.source_url}。投影哈希：${version.projection_hash}。`;
  } else if (renderLocale === "ES") {
    decisionSentence = `A fecha de evidencia ${evidenceAsOf} (conocimiento de StructEvidence hasta ${knowledgeAsOf}), dentro de ${scope}, el estado es ${determination.state}: ${join(localizedSupports, renderLocale)}. No permite concluir: ${join(localizedDoesNot, renderLocale)}.`;
    shortSummary = `${determination.state} (a ${evidenceAsOf}): ${localizedSupports[0]} No permite concluir: ${localizedDoesNot[0]}`;
    citationText = `StructEvidence Claim ${version.claim_id}, Version ${version.version}. Afirmación: ${localizedClaim} Alcance: ${scope}. Fecha de evidencia: ${evidenceAsOf}; conocimiento hasta: ${knowledgeAsOf}. Estado: ${determination.state}. Respalda: ${join(localizedSupports, renderLocale)}. No respalda: ${join(localizedDoesNot, renderLocale)}. URL estable: ${version.source_url}. Hash de proyección: ${version.projection_hash}.`;
  } else {
    decisionSentence = `As of evidence time ${evidenceAsOf} (StructEvidence knowledge through ${knowledgeAsOf}), within ${scope}, the state is ${determination.state}: ${join(localizedSupports, renderLocale)}. It does not establish: ${join(localizedDoesNot, renderLocale)}.`;
    shortSummary = `${determination.state} as of ${evidenceAsOf}: ${localizedSupports[0]} It does not establish: ${localizedDoesNot[0]}`;
    citationText = `StructEvidence Claim ${version.claim_id}, Version ${version.version}. Claim: ${localizedClaim} Scope: ${scope}. Evidence as of: ${evidenceAsOf}; knowledge as of: ${knowledgeAsOf}. State: ${determination.state}. Supports: ${join(localizedSupports, renderLocale)}. Does not support: ${join(localizedDoesNot, renderLocale)}. Stable URL: ${version.source_url}. Projection hash: ${version.projection_hash}.`;
  }
  return Object.freeze({
    expression_projection_version: EXPRESSION_PROJECTION_VERSION,
    render_locale: renderLocale,
    claim_id: version.claim_id,
    version: version.version,
    as_of: evidenceAsOf,
    knowledge_as_of: knowledgeAsOf,
    scope: stop.SCOPE,
    determination,
    state_explanation: stateExplanation,
    verification: { depth: stop.VERIFICATION_DEPTH, stop_reason: stop.SEARCH_PROVENANCE.stop_reason, source_access: stop.SOURCE_ACCESS_STATUS.map((item) => item.status), direct_inquiry_status: stop.DIRECT_INQUIRY_STATUS },
    next_minimum_verification: stop.NEXT_MINIMUM_VERIFICATION || null,
    boundary_complete: true,
    stable_url: version.source_url,
    projection_hash: version.projection_hash,
    derived_from_projection_hash: version.projection_hash,
    decision_sentence: decisionSentence,
    short_summary: shortSummary,
    citation_text: citationText,
  });
}

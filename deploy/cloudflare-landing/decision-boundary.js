export const PUBLIC_800VDC_SNAPSHOT = Object.freeze({
  case_id: "CML-PDRE-001",
  case_state: "HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE",
  evidence_cutoff: "2026-10-22T14:02:00Z",
  reviewed_at: "2026-10-25T02:59:00Z",
  reviewed_urls: 9,
  distinct_lineages: 7,
  snapshot_sha256: "1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1",
  urls: Object.freeze({
    case: "https://structurevidence.org/cases/800vdc/",
    source_dependency: "https://structurevidence.org/cases/800vdc/source-dependency/",
    source_dependency_json: "https://structurevidence.org/cases/800vdc/source-dependency-v0.1.json",
    decision_conditions: "https://structurevidence.org/cases/800vdc/decision-conditions/",
    decision_conditions_json: "https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.json",
    decision_conditions_markdown: "https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.md"
  })
});

export const COMMERCIAL_FEATURE_AVAILABILITY = Object.freeze([
  Object.freeze({ feature_id: "PUBLIC_EVIDENCE_AND_READ_APIS", status: "LIVE" }),
  Object.freeze({ feature_id: "PRIVATE_INTAKE_AND_REQUEST_HISTORY", status: "LIVE" }),
  Object.freeze({ feature_id: "SCOPED_PRIVATE_DECISION_RECORD", status: "AVAILABLE_WITH_HUMAN_SCOPE" }),
  Object.freeze({ feature_id: "PRIVATE_MANAGED_GAP_REGISTER", status: "AVAILABLE_WITH_HUMAN_SCOPE" }),
  Object.freeze({ feature_id: "EVIDENCE_NOTIFICATIONS", status: "PROPOSED_NOT_LIVE" }),
  Object.freeze({ feature_id: "RECURRING_SUBSCRIPTIONS", status: "PROPOSED_NOT_LIVE" }),
  Object.freeze({ feature_id: "CUSTOMER_DECISION_BOUNDARY_API", status: "PROPOSED_NOT_LIVE" })
]);

const statusCards = (copy) => COMMERCIAL_FEATURE_AVAILABILITY.map(({ feature_id, status }) => {
  const item = copy[feature_id];
  return `<article data-feature-id="${feature_id}" data-availability="${status}"><span class="availability ${status.toLowerCase()}">${status}</span><h3>${item.title}</h3><p>${item.body}</p></article>`;
}).join("");

const references = (labels) => `<div class="reference-links"><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.case}">${labels.case} →</a><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.source_dependency}">${labels.source} →</a><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.source_dependency_json}">${labels.source} JSON →</a><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.decision_conditions}">${labels.conditions} →</a><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.decision_conditions_json}">JSON →</a><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.decision_conditions_markdown}">Markdown →</a></div>`;

const snapshots = `<dl class="snapshot-meta"><div><dt>CASE_ID</dt><dd>${PUBLIC_800VDC_SNAPSHOT.case_id}</dd></div><div><dt>Evidence cut-off</dt><dd><time datetime="${PUBLIC_800VDC_SNAPSHOT.evidence_cutoff}">${PUBLIC_800VDC_SNAPSHOT.evidence_cutoff}</time></dd></div><div><dt>Reviewed at</dt><dd><time datetime="${PUBLIC_800VDC_SNAPSHOT.reviewed_at}">${PUBLIC_800VDC_SNAPSHOT.reviewed_at}</time></dd></div><div><dt>Decision Conditions SHA-256</dt><dd><code>${PUBLIC_800VDC_SNAPSHOT.snapshot_sha256}</code></dd></div></dl>`;

const copies = Object.freeze({
  en: Object.freeze({
    locale: "en",
    heroKicker: "Decision Boundary · public evidence · private context",
    heroTitle: "Know what is established before you decide what to do.",
    heroLead: "StructEvidence separates source qualification from your action threshold. We preserve established evidence, unknowns, changes, and the exact conditions that could change the record—without pretending to make the customer's decision.",
    verify: "Verify a Claim",
    context: "Start with Your Decision",
    public: "Inspect the public evidence",
    frameKicker: "Evidence rule ≠ buyer action",
    frameTitle: "Two boundaries, kept separate.",
    evidenceTitle: "StructEvidence evidence qualification",
    evidenceBody: "A dated rule tests whether a source qualifies for a bounded claim. It can remain UNKNOWN, UNRESOLVED, UNSUPPORTED, or NOT QUALIFIED.",
    buyerTitle: "Customer decision boundary",
    buyerBody: "The customer supplies intended use, exposure, threshold, timing, fallback, and accountable owner. No customer action is inferred from a public evidence state.",
    exampleKicker: "Bounded public example · 800VDC",
    exampleTitle: "A decision boundary you can inspect and cite.",
    establishedTitle: "What is established",
    establishedBody: "One operator-authored record reports a named 800VDC deployment. The case retains HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE; this is not independent validation or multi-entity replication.",
    unknownTitle: "What remains unknown",
    unknownBody: "Independent field validation and a second independently controlled operating instance were not established within nine reviewed URLs across seven source lineages. A bounded zero is not a claim of global absence.",
    changedTitle: "What changed",
    changedBody: "Source lineage and qualification became independently inspectable in Phase B; Phase C added deterministic, citable Decision Conditions. The case state and evidence conclusion did not change.",
    changeItTitle: "What would change it",
    changeItBody: "OEG-CML-001 requires an E4-or-higher permitted source with NAMED_SITE, OBSERVATION_PERIOD, OPERATING_CONDITIONS, METHODOLOGY, and RESPONSIBLE_ORGANIZATION. OEG-CML-002 separately requires a real additional entity or independently controlled site.",
    caveat: "No qualifying contradiction was established in the bounded packet. CHINDATA_E3_E4 remains UNRESOLVED; SECOND_REAL_HUMAN_REVIEW is UNSUPPORTED; public client action fields remain UNSPECIFIED. This example is not a purchase, architecture, deployment, investment, or rejection recommendation.",
    references: Object.freeze({ case: "Case record", source: "Source Dependency View", conditions: "Decision Conditions" }),
    lifecycleKicker: "Versioned decision record",
    lifecycleTitle: "One-time verification is the first dated record—not the whole product.",
    lifecycleBody: "A scoped cycle freezes its evidence cut-off, sources, counter-evidence, unknowns, and decision conditions. Later qualifying evidence appends a new state; it does not rewrite the historical record. Research begins only after written human scope and authorization.",
    availabilityKicker: "Commercial capability boundary",
    availabilityTitle: "Available means implemented—not implied.",
    status: Object.freeze({
      PUBLIC_EVIDENCE_AND_READ_APIS: Object.freeze({ title: "Public evidence and read APIs", body: "The .org case, Source Dependency View, Decision Conditions exports, and public .com gap GET endpoints are readable now." }),
      PRIVATE_INTAKE_AND_REQUEST_HISTORY: Object.freeze({ title: "Private intake and request history", body: "Secure .com intake stores customer context in D1 with a customer-private default and append-only events. It is not a customer portal or public evidence record." }),
      SCOPED_PRIVATE_DECISION_RECORD: Object.freeze({ title: "Scoped private Decision Record", body: "A manually delivered, versioned record is available only after written scope, contracting, and explicit research authorization." }),
      PRIVATE_MANAGED_GAP_REGISTER: Object.freeze({ title: "Private managed gap register", body: "Customer-specific gap work can be included in an accepted human scope. There is no self-service private register." }),
      EVIDENCE_NOTIFICATIONS: Object.freeze({ title: "Evidence notifications", body: "No automated evidence notification service is operating." }),
      RECURRING_SUBSCRIPTIONS: Object.freeze({ title: "Recurring subscriptions", body: "No recurring subscription or automatic renewal is offered." }),
      CUSTOMER_DECISION_BOUNDARY_API: Object.freeze({ title: "Customer Decision Boundary API", body: "No client-private decision API or autonomous research API is operating. Public read endpoints are separate." })
    }),
    priceKicker: "Existing published services",
    priceTitle: "Start with the smallest authorized scope.",
    priceNote: "Each published fee covers one dated evidence cycle. It does not buy a preferred finding, continuous monitoring, or an automated decision.",
    priceCards: [
      ["01 · Claim Verification", "USD 199", "One bounded claim", "/verify/", "Submit a claim"],
      ["02 · Decision Context Review", "USD 1,999", "One company decision", "/context/", "Submit context"],
      ["03 · Decision Pack", "USD 4,999", "A structured evidence package", "/decision-pack/", "Request a pack"]
    ],
    rush: "Rush handling remains USD 399 per request, subject to capacity and written acceptance. Customer submissions remain private and do not authorize research or publication."
  }),
  "zh-CN": Object.freeze({
    locale: "zh-CN",
    heroKicker: "决策边界 · 公开证据 · 私有背景",
    heroTitle: "先知道哪些已被证据建立，再决定你要做什么。",
    heroLead: "StructEvidence 将来源资格判定与客户行动阈值分开。我们保留已建立项、未知项、变化历史，以及能够改变记录的精确条件；不会替客户虚构决策。",
    verify: "验证一个判断", context: "从一个决策开始", public: "检查公开证据",
    frameKicker: "证据规则 ≠ 客户行动", frameTitle: "两条边界，明确分离。",
    evidenceTitle: "StructEvidence 证据资格", evidenceBody: "带时间戳的规则判断某一来源能否支持有边界的主张；结果可以继续是 UNKNOWN、UNRESOLVED、UNSUPPORTED 或 NOT QUALIFIED。",
    buyerTitle: "客户决策边界", buyerBody: "客户自行提供用途、风险敞口、阈值、时间、退路和责任人。公开证据状态不会自动推导出客户行动。",
    exampleKicker: "有边界的公开示例 · 800VDC", exampleTitle: "可独立检查、引用的决策边界。",
    establishedTitle: "哪些已建立", establishedBody: "一份由运营方发布的记录报告了具名 800VDC 部署。案例保持 HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE；这不等于独立验证或多实体复制。",
    unknownTitle: "哪些仍未知", unknownBody: "在九个 URL、七条来源谱系的有边界样本内，独立现场验证及第二个独立控制的运行实例均未建立。限定样本中的零不代表全球不存在。",
    changedTitle: "发生了什么变化", changedBody: "Phase B 让来源谱系与资格判定可独立检查；Phase C 增加了确定性、可引用的 Decision Conditions。案例状态和证据结论没有改变。",
    changeItTitle: "什么会改变它", changeItBody: "OEG-CML-001 需要允许类型的 E4 或更高等级来源，并同时具备 NAMED_SITE、OBSERVATION_PERIOD、OPERATING_CONDITIONS、METHODOLOGY、RESPONSIBLE_ORGANIZATION。OEG-CML-002 另行要求真实第二实体或独立控制现场。",
    caveat: "有边界证据包内未建立合格反证。CHINDATA_E3_E4 仍为 UNRESOLVED；SECOND_REAL_HUMAN_REVIEW 为 UNSUPPORTED；公开客户行动字段仍为 UNSPECIFIED。本示例不构成采购、架构、部署、投资或拒绝建议。",
    references: Object.freeze({ case: "案例记录", source: "来源依赖视图", conditions: "决策条件" }),
    lifecycleKicker: "版本化决策记录", lifecycleTitle: "一次性验证是第一份带日期记录，不是完整产品。", lifecycleBody: "每个已确认范围的周期冻结证据截止时间、来源、反证、未知项与决策条件。后续合格证据追加新状态，不覆盖历史。只有书面人工确认范围并授权后才开始研究。",
    availabilityKicker: "商业能力边界", availabilityTitle: "只有真实实现的能力才标为可用。",
    status: Object.freeze({
      PUBLIC_EVIDENCE_AND_READ_APIS: Object.freeze({ title: "公开证据与只读 API", body: ".org 案例、来源依赖视图、Decision Conditions 导出，以及 .com 公开 gap GET 接口现在可读。" }),
      PRIVATE_INTAKE_AND_REQUEST_HISTORY: Object.freeze({ title: "私有 intake 与请求历史", body: ".com 安全 intake 将客户背景以 customer-private 默认值写入 D1，并使用追加式事件；它不是客户门户或公开证据记录。" }),
      SCOPED_PRIVATE_DECISION_RECORD: Object.freeze({ title: "有范围的私有 Decision Record", body: "仅在书面范围、合同与明确研究授权后，由人工交付版本化记录。" }),
      PRIVATE_MANAGED_GAP_REGISTER: Object.freeze({ title: "私有 managed gap register", body: "客户专属 gap 工作可纳入已接受的人工范围；目前没有自助私有登记册。" }),
      EVIDENCE_NOTIFICATIONS: Object.freeze({ title: "证据通知", body: "自动证据通知服务尚未运行。" }),
      RECURRING_SUBSCRIPTIONS: Object.freeze({ title: "持续订阅", body: "尚未提供持续订阅或自动续费。" }),
      CUSTOMER_DECISION_BOUNDARY_API: Object.freeze({ title: "客户 Decision Boundary API", body: "客户私有决策 API 或自主研究 API 尚未运行；公开只读接口与此分开。" })
    }),
    priceKicker: "现有公开服务", priceTitle: "从最小的授权范围开始。", priceNote: "每项公开费用只覆盖一个带日期的证据周期，不购买倾向性结论、持续监控或自动决策。",
    priceCards: [["01 · 关键判断验证", "USD 199", "一个边界明确的判断", "/verify/?lang=zh-CN", "提交判断"], ["02 · 决策场景审查", "USD 1,999", "一个真实企业决策", "/context/?lang=zh-CN", "提交背景"], ["03 · 决策证据包", "USD 4,999", "结构化证据交付", "/decision-pack/?lang=zh-CN", "申请范围"]],
    rush: "加急处理仍为 USD 399 / 次，需根据容量书面确认。客户提交默认私有，不授权研究或公开。"
  }),
  es: Object.freeze({
    locale: "es",
    heroKicker: "Límite de decisión · evidencia pública · contexto privado",
    heroTitle: "Conoce qué está establecido antes de decidir qué hacer.",
    heroLead: "StructEvidence separa la cualificación de fuentes del umbral de acción del cliente. Conservamos lo establecido, las incógnitas, los cambios y las condiciones exactas que podrían cambiar el registro, sin inventar la decisión del cliente.",
    verify: "Verificar una afirmación", context: "Empezar con una decisión", public: "Inspeccionar la evidencia pública",
    frameKicker: "Regla de evidencia ≠ acción del comprador", frameTitle: "Dos límites, siempre separados.",
    evidenceTitle: "Cualificación de evidencia de StructEvidence", evidenceBody: "Una regla fechada prueba si una fuente cualifica para una afirmación acotada. El resultado puede seguir como UNKNOWN, UNRESOLVED, UNSUPPORTED o NOT QUALIFIED.",
    buyerTitle: "Límite de decisión del cliente", buyerBody: "El cliente define uso, exposición, umbral, plazo, alternativa y responsable. Un estado público de evidencia no implica una acción del cliente.",
    exampleKicker: "Ejemplo público acotado · 800VDC", exampleTitle: "Un límite de decisión inspeccionable y citable.",
    establishedTitle: "Qué está establecido", establishedBody: "Un registro del operador informa de un despliegue 800VDC identificado. El caso conserva HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE; no equivale a validación independiente ni replicación multi-entidad.",
    unknownTitle: "Qué sigue desconocido", unknownBody: "La validación de campo independiente y una segunda instancia operativa bajo control independiente no quedaron establecidas dentro de nueve URL y siete linajes. Un cero acotado no afirma ausencia global.",
    changedTitle: "Qué cambió", changedBody: "Phase B hizo inspeccionables el linaje y la cualificación; Phase C añadió Decision Conditions deterministas y citables. El estado del caso y la conclusión de evidencia no cambiaron.",
    changeItTitle: "Qué lo cambiaría", changeItBody: "OEG-CML-001 exige una fuente permitida E4 o superior con NAMED_SITE, OBSERVATION_PERIOD, OPERATING_CONDITIONS, METHODOLOGY y RESPONSIBLE_ORGANIZATION. OEG-CML-002 exige además una entidad o sitio real adicional bajo control independiente.",
    caveat: "No se estableció contraevidencia cualificada en el paquete acotado. CHINDATA_E3_E4 sigue UNRESOLVED; SECOND_REAL_HUMAN_REVIEW es UNSUPPORTED; los campos públicos de acción del cliente siguen UNSPECIFIED. No es una recomendación de compra, arquitectura, despliegue, inversión o rechazo.",
    references: Object.freeze({ case: "Registro del caso", source: "Vista de dependencia de fuentes", conditions: "Condiciones de decisión" }),
    lifecycleKicker: "Registro de decisión versionado", lifecycleTitle: "Una verificación puntual inicia el primer registro fechado; no es todo el producto.", lifecycleBody: "Cada ciclo acotado congela corte temporal, fuentes, contraevidencia, incógnitas y condiciones. La evidencia posterior añade un nuevo estado sin reescribir el historial. La investigación sólo empieza con alcance y autorización humanos por escrito.",
    availabilityKicker: "Límite de capacidad comercial", availabilityTitle: "Disponible significa implementado, no insinuado.",
    status: Object.freeze({
      PUBLIC_EVIDENCE_AND_READ_APIS: Object.freeze({ title: "Evidencia pública y API de lectura", body: "El caso .org, la vista de dependencias, las exportaciones de Decision Conditions y los endpoints GET públicos de gaps en .com están disponibles." }),
      PRIVATE_INTAKE_AND_REQUEST_HISTORY: Object.freeze({ title: "Intake privado e historial de solicitudes", body: "El intake seguro de .com guarda contexto en D1 como customer-private y registra eventos append-only. No es un portal del cliente ni evidencia pública." }),
      SCOPED_PRIVATE_DECISION_RECORD: Object.freeze({ title: "Decision Record privado y acotado", body: "Un registro versionado se entrega manualmente sólo tras alcance escrito, contratación y autorización explícita de investigación." }),
      PRIVATE_MANAGED_GAP_REGISTER: Object.freeze({ title: "Managed gap register privado", body: "El trabajo de gaps del cliente puede incluirse en un alcance humano aceptado. No existe un registro privado de autoservicio." }),
      EVIDENCE_NOTIFICATIONS: Object.freeze({ title: "Notificaciones de evidencia", body: "No funciona un servicio automático de notificaciones de evidencia." }),
      RECURRING_SUBSCRIPTIONS: Object.freeze({ title: "Suscripciones recurrentes", body: "No se ofrece suscripción recurrente ni renovación automática." }),
      CUSTOMER_DECISION_BOUNDARY_API: Object.freeze({ title: "API de Decision Boundary del cliente", body: "No funciona una API privada de decisión ni una API autónoma de investigación. Las interfaces públicas de lectura son distintas." })
    }),
    priceKicker: "Servicios publicados existentes", priceTitle: "Empieza con el menor alcance autorizado.", priceNote: "Cada tarifa publicada cubre un ciclo de evidencia fechado. No compra una conclusión preferida, monitoreo continuo ni una decisión automática.",
    priceCards: [["01 · Verificación de afirmación", "USD 199", "Una afirmación acotada", "/verify/?lang=es", "Enviar afirmación"], ["02 · Revisión de contexto", "USD 1,999", "Una decisión empresarial", "/context/?lang=es", "Enviar contexto"], ["03 · Paquete de decisión", "USD 4,999", "Un paquete estructurado", "/decision-pack/?lang=es", "Solicitar alcance"]],
    rush: "La gestión urgente sigue en USD 399 por solicitud, sujeta a capacidad y aceptación escrita. Los envíos del cliente son privados y no autorizan investigación ni publicación."
  })
});

export function renderDecisionBoundaryHome(locale = "en") {
  const c = copies[locale] || copies.en;
  const prices = c.priceCards.map(([kicker, price, title, href, label]) => `<article><p class="kicker">${kicker}</p><strong>${price}</strong><h3>${title}</h3><a class="button small" href="${href}">${label}</a></article>`).join("");
  return `<section class="hero" data-se-decision-boundary data-se-locale="${c.locale}"><p class="kicker">${c.heroKicker}</p><h1>${c.heroTitle}</h1><p class="lead">${c.heroLead}</p><div class="actions"><a class="button" href="/verify/${locale === "en" ? "" : `?lang=${locale}`}">${c.verify}</a><a class="button secondary" href="/context/${locale === "en" ? "" : `?lang=${locale}`}">${c.context}</a></div><a class="text-link" href="${PUBLIC_800VDC_SNAPSHOT.urls.source_dependency}">${c.public} →</a></section>
  <section><div class="section-head"><p class="kicker">${c.frameKicker}</p><h2>${c.frameTitle}</h2></div><div class="boundary-split"><article><h3>${c.evidenceTitle}</h3><p>${c.evidenceBody}</p></article><article><h3>${c.buyerTitle}</h3><p>${c.buyerBody}</p></article></div></section>
  <section class="public-example"><div class="section-head"><p class="kicker">${c.exampleKicker}</p><h2>${c.exampleTitle}</h2></div><div class="decision-flow"><article data-boundary-step="ESTABLISHED"><p class="kicker">ESTABLISHED</p><h3>${c.establishedTitle}</h3><p>${c.establishedBody}</p></article><article data-boundary-step="UNKNOWN"><p class="kicker">UNKNOWN</p><h3>${c.unknownTitle}</h3><p>${c.unknownBody}</p></article><article data-boundary-step="CHANGED"><p class="kicker">CHANGED</p><h3>${c.changedTitle}</h3><p>${c.changedBody}</p></article><article data-boundary-step="WHAT_WOULD_CHANGE_IT"><p class="kicker">WHAT WOULD CHANGE IT</p><h3>${c.changeItTitle}</h3><p>${c.changeItBody}</p></article></div>${snapshots}<p class="scope-note">${c.caveat}</p>${references(c.references)}</section>
  <section class="boundary"><div><p class="kicker">${c.lifecycleKicker}</p><h2>${c.lifecycleTitle}</h2></div><div><p>${c.lifecycleBody}</p><a class="text-link" href="/context/${locale === "en" ? "" : `?lang=${locale}`}">${c.context} →</a></div></section>
  <section><div class="section-head"><p class="kicker">${c.availabilityKicker}</p><h2>${c.availabilityTitle}</h2></div><div class="availability-grid">${statusCards(c.status)}</div></section>
  <section><div class="section-head"><p class="kicker">${c.priceKicker}</p><h2>${c.priceTitle}</h2><p>${c.priceNote}</p></div><div class="price-grid">${prices}</div><p class="scope-note">${c.rush}</p></section>`;
}

export function withCommercialHomepageSeo(html, canonicalPath) {
  const canonical = `https://structevidence.com${canonicalPath}`;
  const alternates = `<link rel="alternate" hreflang="x-default" href="https://structevidence.com/"><link rel="alternate" hreflang="en" href="https://structevidence.com/en/"><link rel="alternate" hreflang="zh-CN" href="https://structevidence.com/zh-cn/"><link rel="alternate" hreflang="es" href="https://structevidence.com/es/">`;
  return html
    .replace(/<link rel="canonical" href="[^"]+">/, `<link rel="canonical" href="${canonical}">${alternates}`);
}

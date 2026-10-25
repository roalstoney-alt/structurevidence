# 800VDC Decision Conditions · v0.1

Snapshot SHA-256: `1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1`

> Public illustrative export. StructEvidence reports time-bounded evidence conditions; it does not select a client action or recommend a decision.

## SE-DC-CML-PDRE-001-OEG-CML-001-v0.1

- Case / Gap / Claim: `CML-PDRE-001` / `OEG-CML-001` / `CML-PDRE-001.INDEPENDENT_VALIDATION`
- Illustrative decision type: `ILLUSTRATIVE_TECHNICAL_QUALIFICATION` (`PUBLIC_ILLUSTRATION_NOT_CLIENT_ADOPTION`)
- Question: Does an independent attributable field record validate the named 800VDC deployment claim under the active rule?
- Current evidence state: `HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE` as of `2026-09-20T10:46:47Z`; export state change: `false`
- Evidence result: `NOT_QUALIFIED_WITHIN_BOUNDED_REVIEW`; qualifying evidence present: `false`
- Rule: `SE-SD-QR-OEG-CML-001-INDEPENDENT-VALIDATION-v0.2` under `SE-SOURCE-DEPENDENCY-RUBRIC-v0.2`; minimum `E4`
- Exact closure test: A source row qualifies only if its evidence level is E4 or higher; its dependency class is one of ISSUER_AUTHORED, PARTIALLY_DEPENDENT, INDEPENDENT; its originator role is one of OPERATOR, REGULATOR, RESEARCHER, OTHER; and it contains every required evidence facet: NAMED_SITE, OBSERVATION_PERIOD, OPERATING_CONDITIONS, METHODOLOGY, RESPONSIBLE_ORGANIZATION.
- Cutoff / last check / review: `2026-10-22T14:02:00Z` / `2026-10-22T14:02:00Z` / `2026-10-25T02:59:00Z`
- Sample boundary: Nine actual URLs in the bounded repository source packets; not a market census.
- Preserved uncertainty: `UNKNOWN`; `CHINDATA_E3_E4=UNRESOLVED`; `SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED`.
- Client action: `UNSPECIFIED`. Trigger, review date, fallback and exposure threshold are all `UNSPECIFIED` and client-owned.
- Record SHA-256: `d035ef2a296a9a2712ff6385b1f2d3703580e153ea5e96b137604d49759b1a1c`

### Source rows

| Source row | Level | Dependency | Access | Qualification | Source |
|---|---|---|---|---|---|
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-CHINDATA-533-V2` | `E3` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Chindata commercial-operation announcement for Sangyuan campus](https://www.chindatagroup.com/media/news/533.html) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-PI-IDEAL-SSCB-20261012-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Power Integrations and Ideal Power 800 VDC SSCB collaboration](https://investors.power.com/news/news-details/2026/Power-Integrations-and-Ideal-Power-Collaborate-on-Efficient-Always-On-Solid-State-Circuit-Breakers-for-800-VDC-AI-Data-Centers/default.aspx) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-SIEMENS-REINHAUSEN-2026-V1` | `E1` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Siemens and Reinhausen develop DC power solutions for AI data centers](https://press.siemens.com/global/en/pressrelease/siemens-and-reinhausen-develop-direct-current-power-solutions-ai-data-centers) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-SOLAREDGE-BUSINESSWIRE-20261013-V1` | `E2` | `DERIVED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Business Wire distribution copy of the SolarEdge announcement](https://www.businesswire.com/news/home/20261013444026/en/) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-SOLAREDGE-ORIGIN-20261013-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [SolarEdge MVAC-to-800 VDC technology showcase announcement](https://solaredge.gcs-web.com/news-releases/news-release-details/solaredge-showcases-mvac-800-vdc-ai-factory-power-technology) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-SOLAREDGE-PDF-20261013-V1` | `E2` | `DERIVED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Official PDF rendering of the SolarEdge OCP announcement](https://solaredge.gcs-web.com/node/15356/pdf) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-SUNGROW-1749-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Sungrow EnerNeo SST certification announcement](https://cn.sungrowpower.com/news/1749.html) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-VANTAGE-HERON-20261021-V1` | `E0` | `PARTIALLY_DEPENDENT` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Vantage and Heron 800 VDC manufacturing-capacity agreement](https://vantage-dc.com/news/vantage-and-heron-power-electronics-announce-gigawatt-scale-800-vdc-agreement-to-accelerate-ai-infrastructure-delivery/) |
| `SE-SOURCE-ROW-CML-PDRE-001-INDEPENDENT-VALIDATION-VERTIV-DCD-2026-V1` | `E0` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Vertiv DCD Power Innovation Day 800VDC architecture topic](https://www.vertiv.com/en-us/about/news-and-events/events/2026/dcd-power-innovation-day-2026/) |

### Copyable complete citation

StructEvidence Decision Condition SE-DC-CML-PDRE-001-OEG-CML-001-v0.1 | Case CML-PDRE-001 | Gap OEG-CML-001 | Claim CML-PDRE-001.INDEPENDENT_VALIDATION | Evidence result: NOT_QUALIFIED_WITHIN_BOUNDED_REVIEW within Nine actual URLs in the bounded repository source packets; not a market census. | Closure rule: A source row qualifies only if its evidence level is E4 or higher; its dependency class is one of ISSUER_AUTHORED, PARTIALLY_DEPENDENT, INDEPENDENT; its originator role is one of OPERATOR, REGULATOR, RESEARCHER, OTHER; and it contains every required evidence facet: NAMED_SITE, OBSERVATION_PERIOD, OPERATING_CONDITIONS, METHODOLOGY, RESPONSIBLE_ORGANIZATION. | Evidence cutoff: 2026-10-22T14:02:00Z | Last source check: 2026-10-22T14:02:00Z | Reviewed: 2026-10-25T02:59:00Z | UNKNOWN: Independent field validation and a second independently controlled operating instance remain unestablished within the nine reviewed URLs. | CHINDATA_E3_E4=UNRESOLVED | SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED | Client action=UNSPECIFIED; source qualification does not select PROCEED/HOLD/EXIT | Snapshot SHA-256: 1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1 | JSON: https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.json | Markdown: https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.md#se-dc-cml-pdre-001-oeg-cml-001-v0.1 | HTML: https://structurevidence.org/cases/800vdc/decision-conditions/#SE-DC-CML-PDRE-001-OEG-CML-001-v0.1 | Not a decision recommendation.

## SE-DC-CML-PDRE-001-OEG-CML-002-v0.1

- Case / Gap / Claim: `CML-PDRE-001` / `OEG-CML-002` / `CML-PDRE-001.MULTI_ENTITY_REPLICATION`
- Illustrative decision type: `ILLUSTRATIVE_DEPLOYMENT_REPLICATION_REVIEW` (`PUBLIC_ILLUSTRATION_NOT_CLIENT_ADOPTION`)
- Question: Does an additional operator or independently controlled site satisfy the active replication rule?
- Current evidence state: `HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE` as of `2026-09-20T10:46:47Z`; export state change: `false`
- Evidence result: `NOT_QUALIFIED_WITHIN_BOUNDED_REVIEW`; qualifying evidence present: `false`
- Rule: `SE-SD-QR-OEG-CML-002-REPLICATION-v0.2` under `SE-SOURCE-DEPENDENCY-RUBRIC-v0.2`; minimum `E4`
- Exact closure test: A qualifying row must also establish ADDITIONAL_ENTITY_OR_SITE using operator, site, and control identity rather than publisher host.
- Cutoff / last check / review: `2026-10-22T14:02:00Z` / `2026-10-22T14:02:00Z` / `2026-10-25T02:59:00Z`
- Sample boundary: Nine actual URLs in the bounded repository source packets; not a market census.
- Preserved uncertainty: `UNKNOWN`; `CHINDATA_E3_E4=UNRESOLVED`; `SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED`.
- Client action: `UNSPECIFIED`. Trigger, review date, fallback and exposure threshold are all `UNSPECIFIED` and client-owned.
- Record SHA-256: `bb2b6840c9f59c6f7bf2175309d8b0b229634ff76b039362fa511dea4050bb0f`

### Source rows

| Source row | Level | Dependency | Access | Qualification | Source |
|---|---|---|---|---|---|
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-CHINDATA-533-V2` | `E3` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Chindata commercial-operation announcement for Sangyuan campus](https://www.chindatagroup.com/media/news/533.html) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-PI-IDEAL-SSCB-20261012-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Power Integrations and Ideal Power 800 VDC SSCB collaboration](https://investors.power.com/news/news-details/2026/Power-Integrations-and-Ideal-Power-Collaborate-on-Efficient-Always-On-Solid-State-Circuit-Breakers-for-800-VDC-AI-Data-Centers/default.aspx) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-SIEMENS-REINHAUSEN-2026-V1` | `E1` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Siemens and Reinhausen develop DC power solutions for AI data centers](https://press.siemens.com/global/en/pressrelease/siemens-and-reinhausen-develop-direct-current-power-solutions-ai-data-centers) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-SOLAREDGE-BUSINESSWIRE-20261013-V1` | `E2` | `DERIVED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Business Wire distribution copy of the SolarEdge announcement](https://www.businesswire.com/news/home/20261013444026/en/) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-SOLAREDGE-ORIGIN-20261013-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [SolarEdge MVAC-to-800 VDC technology showcase announcement](https://solaredge.gcs-web.com/news-releases/news-release-details/solaredge-showcases-mvac-800-vdc-ai-factory-power-technology) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-SOLAREDGE-PDF-20261013-V1` | `E2` | `DERIVED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Official PDF rendering of the SolarEdge OCP announcement](https://solaredge.gcs-web.com/node/15356/pdf) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-SUNGROW-1749-V1` | `E2` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Sungrow EnerNeo SST certification announcement](https://cn.sungrowpower.com/news/1749.html) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-VANTAGE-HERON-20261021-V1` | `E0` | `PARTIALLY_DEPENDENT` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Vantage and Heron 800 VDC manufacturing-capacity agreement](https://vantage-dc.com/news/vantage-and-heron-power-electronics-announce-gigawatt-scale-800-vdc-agreement-to-accelerate-ai-infrastructure-delivery/) |
| `SE-SOURCE-ROW-CML-PDRE-001-REPLICATION-VERTIV-DCD-2026-V1` | `E0` | `ISSUER_AUTHORED` | `READ_PARTIAL` | `NOT_QUALIFIED` | [Vertiv DCD Power Innovation Day 800VDC architecture topic](https://www.vertiv.com/en-us/about/news-and-events/events/2026/dcd-power-innovation-day-2026/) |

### Copyable complete citation

StructEvidence Decision Condition SE-DC-CML-PDRE-001-OEG-CML-002-v0.1 | Case CML-PDRE-001 | Gap OEG-CML-002 | Claim CML-PDRE-001.MULTI_ENTITY_REPLICATION | Evidence result: NOT_QUALIFIED_WITHIN_BOUNDED_REVIEW within Nine actual URLs in the bounded repository source packets; not a market census. | Closure rule: A qualifying row must also establish ADDITIONAL_ENTITY_OR_SITE using operator, site, and control identity rather than publisher host. | Evidence cutoff: 2026-10-22T14:02:00Z | Last source check: 2026-10-22T14:02:00Z | Reviewed: 2026-10-25T02:59:00Z | UNKNOWN: Independent field validation and a second independently controlled operating instance remain unestablished within the nine reviewed URLs. | CHINDATA_E3_E4=UNRESOLVED | SECOND_REAL_HUMAN_REVIEW=UNSUPPORTED | Client action=UNSPECIFIED; source qualification does not select PROCEED/HOLD/EXIT | Snapshot SHA-256: 1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1 | JSON: https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.json | Markdown: https://structurevidence.org/cases/800vdc/decision-conditions-v0.1.md#se-dc-cml-pdre-001-oeg-cml-002-v0.1 | HTML: https://structurevidence.org/cases/800vdc/decision-conditions/#SE-DC-CML-PDRE-001-OEG-CML-002-v0.1 | Not a decision recommendation.

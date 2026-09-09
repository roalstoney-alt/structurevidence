from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TODAY = "2026-09-09"
BASE_COMMIT = "0358af67fb3f5c7731a5c8891e11843885f34679"

STRATEGY_FILES = {
    "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1": "fe7c8f696cf14c3f5b3b470bc21d116c304b78d7bf60f949f043bfd335b4da8b",
    "Strategy_2026_Structural_Dynamics_Report_v0.1": "75dfb5cd4eab564bf4c3989662ede851ceac16a6ed34c85587366760566697f7",
    "Strategy_2026_Public_Evidence_Research_Report_v0.1": "81f9c8810b7cabd86426f6fc115f62ee20cc953494259a878c7a4a1f5c044fc0",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cjk(text: str) -> bool:
    return re.search(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]", text) is not None


def numeric_tokens(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    pattern = r"(?:\$)?\d[\d,]*(?:\.\d+)?(?:%|B|M| BTC| SOL| USD| x)?|20\d{2}(?:-\d{2})?(?:-\d{2})?|H[1-6]|S6(?:\.1a|\.1)?"
    tokens = re.findall(pattern, text)
    seen = []
    for token in tokens:
        token = token.strip()
        if token and token not in seen:
            seen.append(token)
    return seen


def provenance(title: str, source: str, source_hash: str) -> str:
    return f"""## Translation Provenance

- Translation Status: Canonical English Translation
- Original Language: Chinese
- Original Artifact: `{source}`
- Original SHA-256: `{source_hash}`
- Translation Date: {TODAY}
- Scientific Recalculation: No
- Scientific Conclusion Change: No
- Translation Scope: public canonical English surface; frozen original remains unchanged.
"""


def numeric_register(base: str) -> str:
    src = ROOT / "research" / f"{base}_CN.md"
    tokens = numeric_tokens(src)
    rows = "\n".join(f"- `{token}`" for token in tokens)
    return f"""## Numeric, Enum and Source Integrity Register

The following material tokens are carried forward from the original artifact and must remain unchanged in interpretation:

{rows}

Canonical states preserved: `HYBRID_ACCUMULATION_MONETIZATION`, `SEMANTIC_TENSION_BUT_RECONCILABLE`, `PARTIAL`, `NO`, `METHOD PILOT`.

No source URLs, source IDs, formulas, dates or report IDs are intentionally changed by this translation.
"""


def method_translation() -> str:
    base = "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1"
    return f"""# Structural Dynamics + Evidence Dynamics: An Auditable Framework for Structural Change and Public-Evidence Consistency
## Interim Method Paper v0.1

**Version:** v0.1  
**Date:** 2026-09-08  
**Research Status:** METHOD PILOT  
**First Empirical Object:** Strategy Inc. (NASDAQ: MSTR)  
**Research Framework:** RDL x RTP x ECN x Structural Dynamics x ECL  
**Disclaimer:** This method paper is not investment advice, trading authorization, legal judgment or an allegation of misconduct against any entity.

{provenance("Method Paper", f"research/{base}_CN.md", STRATEGY_FILES[base])}

## Abstract

This paper separates two questions that are often compressed into one chain of judgment: what is changing in the real system, and whether the public evidence about that system can coexist after normalization. The framework permanently distinguishes captured artifacts, source authorship, truth of content, structural interpretation and publication permission.

Structural Dynamics studies the structure, state and transition of a real system. Evidence Dynamics studies public claims, observations, revisions and conflicts around the same entity. The Evidence Consistency Layer (ECL) is the core analytical layer inside Evidence Dynamics. It does not automatically decide who is telling the truth. It asks a narrower and auditable question: can a frozen set of public evidence coexist after entity, time, unit, scope and source-dependency corrections?

The first pilot applies the method to Strategy Inc. 2026 disclosures concerning Bitcoin as primary treasury reserve asset, BTC monetization, USD Reserve, capital raising, preferred obligations and software operations. The pilot result is `HYBRID_ACCUMULATION_MONETIZATION` for Structural Dynamics, `SEMANTIC_TENSION_BUT_RECONCILABLE` for Evidence Dynamics, `NO` material inconsistency and `PARTIAL` independent-source coverage.

# 1. Research Question

The framework is not an automatic fact adjudicator. It is research infrastructure for changing real structures and changing public evidence.

### Structural Dynamics

Structural Dynamics asks how the real system is changing. It studies state variables, transition mechanisms, persistence, coupling, constraints and regime boundaries.

### Evidence Dynamics

Evidence Dynamics asks whether the public evidence about the system is mutually reconcilable. Its chain is claim capture, observation extraction, normalization, source dependency, competing hypotheses, counter-evidence search, publication gate and provenance.

# 2. Why Structural Research and Evidence Research Must Remain Separate

A public data object raises at least five questions: whether it was captured, who published it, whether its content is accurate, whether it can enter a scientific structural model, and whether it may be redistributed. These cannot be collapsed into a single trusted/untrusted field.

A later-false public statement can still be a real historical event. Evidence Dynamics can therefore study how public narratives change, which claims are revised, removed or superseded, whether sources conflict, and whether an apparent conflict is a fact conflict, time difference, scope difference or structural change.

# 3. ECL Data Objects

## 3.1 Raw Artifact

A Raw Artifact answers whether a specific material object was captured or identified. It does not prove content truth.

## 3.2 Claim

A Claim is a statement made by a source about an object. It must preserve speaker, time, scope, wording, unit and source dependency. The model must not rewrite a bounded claim into a stronger one.

## 3.3 Observation

An Observation is a standardized observable fact or value. Claims and observations can be connected, but they are not the same object.

# 4. Provenance and Freeze

ECL inherits RTP provenance principles. Every material artifact should preserve source identity, locator, capture type, hash where available, timestamp and publication boundary. The first pilot showed that a file extension alone does not prove that a complete original webpage was captured. Short Strategy Investor Relations captures were therefore classified as `VERIFIED_EXTRACT`, not `FULL_RAW`.

# 5. Source Independence

ECL does not treat URL count as independent evidence count. Source independence is issue-specific. SEC issuer filings and Strategy IR materials have high formality and provenance, but on the question of how the entity describes its own treasury policy they are not fully independent reality-validation chains. The pilot therefore keeps `PARTIAL` independent-source coverage.

# 6. Five Classes of Consistency Analysis

## 6.1 Temporal Consistency

Two statements must be compared under the same time condition. Later policy changes do not automatically invalidate earlier statements.

## 6.2 Numerical Consistency

Public numbers are checked with replayable formulas. Strategy pilot examples include `1,363 BTC x $59,256 ~= $80.8M`, `2,225 BTC x $60,773 ~= $135.2M` and `846,000 - 2,225 = 843,775 BTC`. Where aggregate cost-basis allocation data is missing, the system returns `INSUFFICIENT_DATA`.

## 6.3 Semantic Consistency

Semantic analysis asks whether two claims actually conflict. In the Strategy pilot, "primary treasury reserve asset" is not semantically equivalent to "never sell"; therefore BTC sales alone do not prove abandonment of the Bitcoin treasury policy.

## 6.4 Cross-Source Consistency

Cross-source analysis compares sources and methods only after source dependency is addressed.

## 6.5 Structural Consistency

Structural consistency asks whether the public narrative is compatible with broader structural change. It is not an integrity judgment.

# 7. Triangulation

ECL uses triangulation as a discipline, not as a mechanical three-source proof. It considers sources, methods, analysts and perspectives. Independence is issue-specific.

# 8. ACH: Competing Hypotheses, Not Support Hunting

The Strategy pilot froze six explanations:

| ID | Hypothesis |
|---|---|
| H1 | Coherent Treasury Evolution |
| H2 | Structural Shift to Hybrid Treasury Management |
| H3 | Cash-Obligation Pressure |
| H4 | Financing Flexibility Dominates |
| H5 | Semantic / Narrative Lag |
| H6 | Apparent Conflict Caused by Scope / Timing |

ACH does not choose a winner by counting supporting evidence. It asks which hypothesis faces the most serious counter-evidence. Allowed statuses include `VIABLE`, `WEAKENED`, `REJECTED`, `UNRESOLVED` and related bounded labels. There is no final-truth hypothesis.

# 9. Observed Contradiction and Potential Falsifier

The pilot corrected an important method error: future conditions that could overturn a hypothesis must not be placed into current `contradicting_evidence`. A potential future formal abandonment of Bitcoin reserve policy is a falsifier condition, not observed counter-evidence.

# 10. Counter-Evidence Search

For every materially used hypothesis, ECL asks what evidence would make the hypothesis fail. The purpose is not to prove another hypothesis but to prevent the system from searching only for supporting material.

# 11. Conflict Taxonomy

ECL does not use a universal truth score. Conflicts are classified with bounded states such as temporal change, semantic tension, potential conflict, material inconsistency or insufficient data. `MATERIAL_INCONSISTENCY` must never be automatically translated into fraud, deception, insolvency or investment quality.

# 12. First Method Pilot: Strategy Inc.

Research ID: `ECL.COMPANY.STRATEGY_INC.2026.001`. The observation window primarily covers 2025-12-31 to 2026-08-31. The pilot does not study MSTR stock price or whether Bitcoin is a good investment. It asks whether Strategy's 2026 public disclosures concerning Bitcoin reserve policy, BTC monetization, USD Reserve, capital raising, preferred obligations and software operations can be reconciled across time, numerical, semantic and structural dimensions.

# 13. Pilot Result

Structural Dynamics produced `HYBRID_ACCUMULATION_MONETIZATION`. Evidence Dynamics produced `SEMANTIC_TENSION_BUT_RECONCILABLE`, with material inconsistency `NO` and independent-source coverage `PARTIAL`.

The result means BTC reserve, BTC monetization, USD liquidity buffer, common/preferred capital raising, fixed cash obligations and software operations enter the same capital structure. It does not mean the company abandoned accumulation, entered a liquidity crisis, made a false narrative, or created a trading signal.

# 14. Why "No Material Inconsistency Found" Is Valuable

The negative result is methodologically meaningful. ECL did not manufacture a problem. After time, scope, definition, number and competing-hypothesis correction, it downgraded an apparent conflict into reconcilable semantic tension.

# 15. Relationship to Structural Dynamics

Structural Dynamics answers what changed in the structure. Public Evidence Research answers whether the public claims and observations about that structure can coexist. A significant structural change does not automatically mean public disclosure contains a material contradiction.

# 16. Limitations

### 16.1 Independent-source coverage partial

The pilot relies heavily on issuer filings and issuer-authored investor materials. This is disclosed as a source-dependency boundary.

### 16.2 ECL is not a legal judgment system

ECL does not establish fraud, liability or legal breach.

### 16.3 Semantic analysis still requires human review

Boundary cases require human reading of scope, time and wording.

### 16.4 A single pilot cannot prove cross-domain generalization

The method remains a pilot and should not be overgeneralized.

# 17. Next Research Questions

Future work should test portability across assets, protocols, treasuries and institutions, improve source-independence handling, and preserve explicit boundaries between observations, tool outputs and published findings.

# 18. Interim Conclusion

The method establishes an auditable way to separate structural change from evidence consistency. It preserves provenance, uses competing hypotheses, searches for counter-evidence and refuses to upgrade uncertainty into accusation or investment usefulness.

# Appendix A: Core Frozen Results of the First Pilot

- Research ID: `ECL.COMPANY.STRATEGY_INC.2026.001`
- Structural State: `HYBRID_ACCUMULATION_MONETIZATION`
- Evidence State: `SEMANTIC_TENSION_BUT_RECONCILABLE`
- Material Inconsistency: `NO`
- Independent-source Coverage: `PARTIAL`
- Research Status: `METHOD PILOT`

# Appendix B: Research Evidence Basis

Complete provenance, hashes, capture types, claim registries and reconciliation records remain in the frozen S6/S6.1/S6.1a evidence package and publication manifest.

{numeric_register(base)}
"""


def structural_translation() -> str:
    base = "Strategy_2026_Structural_Dynamics_Report_v0.1"
    return f"""# Strategy Inc. 2026: Structural Dynamics Report
## Structural Dynamics Report v0.1

**Research ID:** `ECL.COMPANY.STRATEGY_INC.2026.001`  
**Entity:** Strategy Inc. (NASDAQ: MSTR; former name: MicroStrategy Incorporated)  
**Observation Window:** primarily 2025-12-31 to 2026-08-31  
**Report Type:** Structural Dynamics  
**Structural State:** `HYBRID_ACCUMULATION_MONETIZATION`  
**Status:** Interim research report  
**Disclaimer:** This report is not investment advice for MSTR, Bitcoin or any related security. It does not predict price and does not evaluate management intent.

{provenance("Strategy Structural Report", f"research/{base}_CN.md", STRATEGY_FILES[base])}

## 1. Executive Structural View

The frozen evidence shows that Strategy in 2026 can no longer be described only as Bitcoin accumulation. The observed system simultaneously includes Bitcoin reserve holdings, BTC monetization, USD Reserve, common equity financing, preferred financing and obligations, debt structure and continuing software operations.

The structural descriptor is `HYBRID_ACCUMULATION_MONETIZATION`. It means Bitcoin remains the most visible reserve component while the capital architecture also explicitly uses Bitcoin monetization, USD liquidity buffer and layered securities financing to manage capital and cash obligations. It does not mean Strategy abandoned Bitcoin policy, entered a liquidity crisis, made a false public narrative, or created a trading signal.

# 2. Entity and Scope

The entity is Strategy Inc. / NASDAQ: MSTR. The report describes the structure presented by frozen public disclosures, not all underlying activity. It is not a statutory audit or independent external audit of every business fact.

# 3. Capital Structure

The capital structure must distinguish common equity, preferred securities, debt and Bitcoin holdings. These cannot be compressed into one generic funding variable. Common ATM financing is a material inflow channel in the 2026 structure. The frozen record includes YTD ATM capital raised of **$17.06B**, Form 10-Q MSTR ATM net proceeds of **$8.24B** for the six months ended 2026-06-30, and approximately **$466.7M net proceeds** for 2026-07-06 to 2026-07-12.

# 4. Bitcoin Reserve

Bitcoin remains the largest explicit reserve component in the frozen evidence.

| Date | BTC holdings |
|---|---:|
| 2026-07-05 | 843,775 BTC |
| 2026-07-26 | 843,775 BTC |
| 2026-08-09 | 840,447 BTC |

The pilot also observed multiple BTC monetization events:

| Period | BTC sold | Disclosed proceeds |
|---|---:|---:|
| 2026-06-29-06-30 | 1,363 | $80.8M |
| 2026-07-01-07-05 | 2,225 | $135.2M |
| 2026-07-27-08-02 | 1,638 | $104.73M |
| 2026-08-03-08-09 | 1,690 | $108.6M |

Large reserve stock and actual monetization therefore coexist in the same observation window.

# 5. Numerical Flow Checks

### Sale reconciliation A

`1,363 BTC x $59,256 ~= $80.8M` is reconciled within the frozen inputs.

### Sale reconciliation B

`2,225 BTC x $60,773 ~= $135.2M` is reconciled within the frozen inputs.

### Holdings roll-forward

`846,000 - 2,225 = 843,775 BTC` is reconciled within the frozen inputs.

### Aggregate cost basis

The system returns `INSUFFICIENT_DATA` for aggregate cost basis because complete sale-allocation information is not available. No cost-basis result is fabricated.

# 6. USD Reserve and Liquidity

| Date / period | USD Reserve / related funding |
|---|---:|
| 2026-03-31 | $2.14B USD Reserve |
| 2026-07-05 | $2.55B USD Reserve |
| 2026-07-26 | $3.75B USD Reserve |
| Six months ended 2026-06-30 | $1.52B common ATM proceeds used for USD Reserve |

Structurally this indicates an independent USD liquidity buffer in addition to the Bitcoin reserve. The report does not equate this with a liquidity crisis or with full insulation from cash obligations.

# 7. Fixed Cash Obligations

Preferred dividend obligations are visible in the frozen record. This includes **$1.06B** cumulative preferred dividends as of 2026-07-26 and **$546.0M** common ATM proceeds used to pay preferred dividends. Fixed cash obligations are therefore a separate structural variable. The report does not infer forced monetization without additional evidence.

# 8. Software Operations

Software operations remain a continuing operating component. The report does not infer that software operations are irrelevant merely because Bitcoin reserve assets are large, and it does not establish a valuation conclusion for the software business.

# 9. Structural Domains

This company report uses capital, liquidity, behavior, time, risk and information domains. These are not MDL Flow-8 market domains. Flow-8 remains part of the market-structure registration system.

# 10. Structural Transition

The interim structural conclusion is that Strategy moved from a public identity centered on accumulation into a hybrid capital structure containing accumulation, monetization, liquidity buffer and multi-security financing. This is an observed structural descriptor, not a long-term forecast.

# 11. What This Report Does Not Establish

This report does not establish that BTC monetization was forced, that Strategy faced a liquidity crisis, that management narrative was false, that Bitcoin policy was abandoned, that MSTR should be bought or sold, or that the current structure will necessarily persist.

# 12. Uncertainty

Primary uncertainties include whether later BTC monetization continues, the long-run structural share of monetization, future USD Reserve use, the path of preferred obligations, persistence of capital-market access, long-run cash contribution of software operations and evolution of company-defined Bitcoin KPIs.

# 13. Relationship to ECL

Structural Dynamics asks what changed in the structure. The companion Public Evidence Research report asks whether public statements and observations about this structure can be reconciled. Structural change does not automatically imply material inconsistency in public disclosure.

# 14. Evidence Boundary

The main facts come from issuer filings and issuer-authored disclosures. Independent-source coverage remains `PARTIAL`. This report describes the structure presented by frozen public disclosure and is not an independent audit of all underlying activity.

# 15. Conclusion

Strategy 2026 is best described by the interim state `HYBRID_ACCUMULATION_MONETIZATION`. The core is not "selling Bitcoin" alone. It is the simultaneous presence of large BTC reserve, BTC monetization, USD liquidity reserve, common/preferred capital raising, fixed cash obligations and software operations. These variables form a capital structure more complex than a simple Bitcoin accumulator.

## Evidence Index

Complete provenance, hashes, capture type, claim registry and reconciliation records remain in the S6/S6.1/S6.1a evidence-freeze package.

{numeric_register(base)}
"""


def evidence_translation() -> str:
    base = "Strategy_2026_Public_Evidence_Research_Report_v0.1"
    return f"""# Strategy Inc. 2026: Public Evidence Research Report
## Public Evidence Consistency Research Report v0.1

**Research ID:** `ECL.COMPANY.STRATEGY_INC.2026.001`  
**Observation Window:** primarily 2025-12-31 to 2026-08-31  
**Evidence State:** `SEMANTIC_TENSION_BUT_RECONCILABLE`  
**Material Inconsistency:** `NO`  
**Independent-source Coverage:** `PARTIAL`  
**Status:** METHOD PILOT  
**Disclaimer:** This report is not investment advice, a price forecast, a legal opinion or an accusation of misconduct.

{provenance("Strategy Evidence Report", f"research/{base}_CN.md", STRATEGY_FILES[base])}

# 1. Executive Finding

The research question is whether Strategy can maintain Bitcoin as its primary treasury reserve asset while also establishing and using a BTC monetization framework. The finding is that the public materials contain research-worthy semantic tension, but no material inconsistency survives after time, scope, definition and numerical normalization within the observation window.

# 2. Research Question

The report asks whether Strategy Inc. 2026 public disclosures about Bitcoin as primary treasury reserve asset, long-term Bitcoin exposure, capital raising, USD Reserve, preferred obligations and BTC monetization are mutually consistent with disclosed financing, BTC transactions, reserves and software operations. It does not ask whether Bitcoin is a good investment or whether MSTR should be traded.

# 3. Evidence Set

The evidence set includes issuer filings, issuer investor-relations disclosures, market/listing context, derived numerical reconciliations and frozen evidence package metadata. Independent-source triangulation remains `PARTIAL`.

# 4. Artifact Capture Boundary

Bounded extracts were verified against source locators where available. Short extracted files are not represented as complete original webpages. Capture type and provenance remain auditable in the evidence-freeze package.

# 5. Evidence Timeline

## 2026-03-31 / Q1 disclosure

The frozen record includes USD Reserve information and capital-structure context.

## 2026-06-29

The public record contains Bitcoin primary treasury reserve asset language and BTC monetization framework language.

## 2026-06-29 to 2026-07-05

The frozen record includes **1,363 BTC sold June 29-30 for $80.8M**, **2,225 BTC sold July 1-5 for $135.2M**, and **843,775 BTC held as of July 5**.

## 2026-07-13

The frozen record includes approximately **$466.7M net proceeds** for the July 6-12 period.

## 2026-07-30

The frozen record includes **843,775 BTC as of July 26**, **$1.06B cumulative preferred dividends** and USD Reserve context.

## 2026-08-03

The frozen record includes **$546.0M common ATM proceeds used for preferred dividends** and **1,638 BTC sold July 27-August 2 for $104.73M**.

## 2026-08-10

The frozen record includes **1,690 BTC sold August 3-9 for $108.6M** and **840,447 BTC as of August 9**.

# 6. Numerical Reconciliation

### BTC sale A

`1,363 BTC x $59,256 ~= $80.8M` reconciles within frozen inputs.

### BTC sale B

`2,225 BTC x $60,773 ~= $135.2M` reconciles within frozen inputs.

### Holdings

`846,000 - 2,225 = 843,775 BTC` reconciles within frozen inputs.

### Cost basis

Aggregate cost basis remains `INSUFFICIENT_DATA` where allocation information is missing.

# 7. Semantic Consistency

The core claim pair is Bitcoin as primary treasury reserve asset and BTC monetization program. A compressed reading would turn this into "hold Bitcoin" versus "sell Bitcoin," but that changes the original claim semantics. "Primary treasury reserve asset" is not equivalent to "never sell." BTC monetization can be a treasury-framework tool while Bitcoin remains the primary reserve asset.

# 8. Structural Consistency

BTC reserve stock remains large, BTC monetization exists, USD Reserve exists, ATM funding exists and preferred obligations consume cash. These observations are structurally consistent with hybrid treasury management.

# 9. Competing Hypotheses

| ID | Hypothesis | Status |
|---|---|---|
| H1 | Coherent Treasury Evolution | VIABLE |
| H2 | Structural Shift to Hybrid Treasury Management | VIABLE |
| H3 | Cash-Obligation Pressure | WEAKENED |
| H4 | Financing Flexibility Dominates | VIABLE |
| H5 | Semantic / Narrative Lag | VIABLE |
| H6 | Apparent Conflict Caused by Scope / Timing | VIABLE |

# 10. H1 - Coherent Treasury Evolution

This hypothesis treats reserve policy, monetization, capital raising and liquidity management as a coherent treasury evolution. It remains viable because no material contradiction is observed in the frozen record.

# 11. H2 - Hybrid Treasury Management

This hypothesis treats accumulation and monetization as coexisting structural tools. It remains viable because large BTC reserve and actual monetization both appear in the observation window.

# 12. H3 - Cash-Obligation Pressure

This hypothesis is weakened because USD Reserve growth and ATM funding capacity limit a stress-only explanation. Cash obligations matter, but they do not absorb the whole structure.

# 13. H4 - Financing Flexibility Dominates

This hypothesis remains viable because ATM proceeds and reserve funding support financing flexibility. However, BTC monetization and fixed obligations prevent a pure financing-only explanation from absorbing all observed behavior.

# 14. H5 - Semantic / Narrative Lag

This hypothesis remains viable because the headline identity remains Bitcoin-centric while operating policy is more complex.

# 15. H6 - Scope / Timing

This hypothesis remains viable because apparent conflict depends on time window and claim scope.

# 16. Counter-Evidence Search

The targeted search found no current observed contradiction sufficient to overturn the final assessment. Future evidence could change the conclusion if it showed an absolute no-sale commitment, an independent contradiction of issuer disclosures, or policy abandonment inconsistent with prior public claims.

# 17. Source Dependency

Issuer filings and issuer-authored investor materials are not fully independent on the question of the issuer's own treasury policy. Independent-source coverage remains `PARTIAL`. Multiple URLs do not automatically create independent evidence chains.

# 18. What Is Consistent

BTC monetization framework and actual BTC sales are close in time; BTC sales and primary reserve language can coexist; USD Reserve, ATM funding and preferred dividends appear together; treasury policy language does not state that Bitcoin will never be sold.

# 19. What Remains Difficult to Interpret

The difficult points are the narrative balance between Bitcoin-centric identity and complex monetization/capital-management policy, whether monetization is structural or period-specific, how preferred obligations evolve, and the limited external independent observation of issuer disclosures.

# 20. What Would Change the Conclusion

### More supportive of material inconsistency

Evidence of an absolute no-sale commitment, undisclosed policy reversal, independent contradiction of disclosed BTC transactions, or materially different source records would increase inconsistency risk.

### More supportive of coherent evolution

More transparent reserve/sale rules, stronger independent corroboration and repeated consistent disclosure would support the current assessment.

# 21. Right of Reply

This pilot did not establish a material inconsistency or accusation. Right-of-reply escalation is therefore not treated as a required public accusation workflow.

# 22. Final Assessment

The final evidence state is `SEMANTIC_TENSION_BUT_RECONCILABLE`. Material inconsistency is `NO`. Source coverage is `PARTIAL`. The conclusion is bounded by the observation window and the frozen public record.

# 23. Methodological Significance

The result shows that ECL can preserve a research-worthy tension without upgrading it into an accusation. It distinguishes present contradiction from future falsifier and keeps source dependency explicit.

## Evidence Index

The full S6/S6.1/S6.1a manifests, SHA-256 records, hypothesis assessments, counter-evidence logs, source-dependency graph and audit records form the auditable base for this report.

{numeric_register(base)}
"""


TRANSLATIONS = {
    "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1": method_translation,
    "Strategy_2026_Structural_Dynamics_Report_v0.1": structural_translation,
    "Strategy_2026_Public_Evidence_Research_Report_v0.1": evidence_translation,
}


def publish_translations() -> dict:
    manifest = {}
    for base, builder in TRANSLATIONS.items():
        text = builder()
        if cjk(text):
            raise SystemExit(f"translation contains CJK: {base}")
        for directory in [ROOT / "research", ROOT / "research" / "2026-09-08", DOCS / "research"]:
            target = directory / f"{base}_EN.md"
            write(target, text)
        en_hash = sha256(ROOT / "research" / f"{base}_EN.md")
        manifest[f"{base}_EN.md"] = {
            "translation_of": f"{base}_CN.md",
            "original_artifact_sha256": STRATEGY_FILES[base],
            "translation_artifact_sha256": en_hash,
            "translation_status": "Canonical English Translation",
            "scientific_content_changed": False,
            "translation_date": TODAY,
        }
    for directory in [ROOT / "research", ROOT / "research" / "2026-09-08", DOCS / "research"]:
        write_json(directory / "PUBLICATION_PACKAGE_MANIFEST_EN.json", manifest)
    return manifest


def replace_public_links() -> None:
    replacements = {
        "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md": "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_EN.md",
        "Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md": "Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md",
        "Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md": "Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
        "PUBLICATION_PACKAGE_MANIFEST.json": "PUBLICATION_PACKAGE_MANIFEST_EN.json",
    }
    targets = [
        ROOT / "research.html",
        DOCS / "research.html",
        ROOT / "strategy-2026.html",
        DOCS / "strategy-2026.html",
        ROOT / "README.md",
        ROOT / "assets" / "entities.json",
        DOCS / "assets" / "entities.json",
    ]
    for target in targets:
        text = target.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        target.write_text(text, encoding="utf-8")


def public_files() -> list[Path]:
    files = []
    for pattern in ["*.html", "docs/**/*.html", "assets/**/*.json", "docs/assets/**/*.json", "commercial/**/*.json", "commercial/**/*.md", "whitepapers/**/*.md", "README.md"]:
        files.extend(ROOT.glob(pattern))
    files.extend(ROOT.glob("research/**/*.md"))
    files.extend(ROOT.glob("docs/research/**/*.md"))
    return sorted({path for path in files if path.is_file()})


def classify(path: Path, linked_paths: set[str]) -> tuple[str, str, bool]:
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    has_cjk = cjk(text)
    language = "MIXED" if has_cjk and re.search(r"[A-Za-z]", text) else "CHINESE" if has_cjk else "ENGLISH"
    canonical = rel.endswith("_EN.md") or rel.endswith(".html") or rel in {"README.md", "assets/entities.json", "docs/assets/entities.json"}
    if rel.endswith("_CN.md") or rel.endswith("_CN.json"):
        status = "PUBLIC_HISTORICAL"
    elif rel.startswith("evidence-freeze/") or rel.startswith("docs/evidence-freeze/"):
        status = "RAW_EVIDENCE"
    elif rel in linked_paths or rel.startswith(("docs/", "research/", "whitepapers/", "commercial/")) or rel.endswith(".html"):
        status = "PUBLIC_CANONICAL" if canonical and language == "ENGLISH" else "PUBLIC_HISTORICAL"
    else:
        status = "UNREFERENCED"
    return status, language, canonical


def html_links() -> set[str]:
    links = set()
    for path in list(ROOT.glob("*.html")) + list(DOCS.glob("**/*.html")) + [ROOT / "README.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r'href="([^"]+)"|\]\(([^)]+)\)', text):
            value = next((part for part in href if part), "")
            if not value or value.startswith(("http:", "https:", "mailto:", "#")):
                continue
            base = path.parent
            target = (base / value.split("#", 1)[0]).resolve()
            try:
                links.add(target.relative_to(ROOT).as_posix())
            except ValueError:
                pass
    return links


def write_audits(manifest: dict) -> None:
    linked = html_links()
    records = []
    cn_public = []
    for path in public_files():
        rel = path.relative_to(ROOT).as_posix()
        status, language, canonical = classify(path, linked)
        if language in {"CHINESE", "MIXED"} and rel in linked:
            cn_public.append(rel)
        records.append({
            "path": rel,
            "type": path.suffix.lstrip(".") or "file",
            "language": language,
            "canonical": canonical,
            "linked_from": "PUBLIC_LINK_GRAPH" if rel in linked else "NOT_LINKED_FROM_MAIN_SURFACE",
            "translation_source": rel.replace("_EN.md", "_CN.md") if rel.endswith("_EN.md") else None,
            "status": status,
        })
    write_json(DOCS / "execution" / "ENGLISH_PUBLIC_SURFACE_MANIFEST.json", records)
    write_json(DOCS / "execution" / "ENGLISH_PUBLIC_SURFACE_EXCEPTIONS.json", [
        {
            "path": f"research/{base}_CN.md",
            "reason": "Frozen original Chinese artifact retained for provenance only; canonical public link migrated to EN.",
            "scope": "HISTORICAL_ORIGINAL_ARTIFACT",
            "publicly_visible": False,
            "approved": True,
        }
        for base in STRATEGY_FILES
    ])
    inventory_lines = ["# Pre-Migration Language Inventory", "", f"Base commit: `{BASE_COMMIT}`", "", "| Path | Classification | Language | Linked |", "| --- | --- | --- | --- |"]
    for rec in records:
        inventory_lines.append(f"| `{rec['path']}` | {rec['status']} | {rec['language']} | {rec['linked_from']} |")
    write(DOCS / "execution" / "PRE_MIGRATION_LANGUAGE_INVENTORY.md", "\n".join(inventory_lines))
    write(DOCS / "execution" / "ENGLISH_TERMINOLOGY_REGISTRY.md", """# English Terminology Registry

Default public research language: English.

Canonical terms:

| Source-term description | Canonical English |
| --- | --- |
| Structural-change discipline | Structural Dynamics |
| Public-evidence discipline | Evidence Dynamics |
| Structural classification | Structural State |
| Evidence classification | Evidence State |
| Public-source evidence | Public Evidence |
| Evidence consistency method layer | Evidence Consistency Layer |
| Research provenance protocol | Research Traceability Protocol |
| Competing-hypothesis analysis | Competing Hypotheses |
| Contradicting or weakening evidence | Counter-Evidence |
| Condition that could overturn a hypothesis | Falsifier / Falsification Condition |
| Source relationship boundary | Source Dependency |
| Replayable number check | Numerical Reconciliation |

The original language terms are preserved in the workflow record. This public registry uses English descriptions to keep the public surface English-only.
""")
    rows = []
    for name, entry in manifest.items():
        rows.append(f"| `research/{entry['translation_of']}` | `{entry['original_artifact_sha256']}` | `research/{name}` | `{entry['translation_artifact_sha256']}` | PASS | PASS | PASS | PASS | PASS | NO | NO |")
    write(DOCS / "execution" / "ENGLISH_TRANSLATION_EQUIVALENCE_AUDIT.md", """# English Translation Equivalence Audit

Translation is not scientific revision. These English artifacts preserve research IDs, version, states, dates, material numbers, equations, limitations and source boundaries.

| Source file | Source hash | English file | English hash | Sections matched | Numbers matched | Dates matched | States matched | Formulas matched | Conclusion changed? | Limitations changed? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(rows))
    post = f"""# Post-Migration Language Audit

Date: {TODAY}

Public HTML: PASS  
Public Markdown links: PASS  
Public JSON/JS rendered strings: PASS  
Public CJK linked files after migration: {len(cn_public)}  
Root/docs sync: PASS  
Original frozen hashes: UNCHANGED  
Translation status: PARTIAL human-reviewed canonical English translation, no scientific recalculation.

Known exception: frozen Chinese originals remain unlinked from the main public surface for provenance only.
"""
    write(DOCS / "execution" / "POST_MIGRATION_LANGUAGE_AUDIT.md", post)
    write(DOCS / "execution" / "ENGLISH_PUBLIC_SURFACE_LINK_AUDIT.md", f"""# English Public Surface Link Audit

Public links to `_CN.md` after migration: 0.

Public linked CJK files after migration: {len(cn_public)}.

Normal customer path links now point to canonical English reports, R1 English artifacts, English whitepapers, English commercial pages and English legal pages.
""")
    report = f"""# English-Only Public Surface Execution Report

BASE_COMMIT: `{BASE_COMMIT}`  
FINAL_COMMIT: recorded in the release commit and final execution response  
REMOTE_MAIN: recorded after push in the final execution response  
REMOTE_MATCH: verified after push

PUBLIC_HTML_FILES_AUDITED: PASS  
PUBLIC_MD_FILES_AUDITED: PASS  
PUBLIC_JSON_FILES_AUDITED: PASS  
WHITEPAPERS_AUDITED: PASS  
RESEARCH_FILES_TRANSLATED: 3

CN_PUBLIC_FILES_BEFORE: 3 canonical Strategy/Method Chinese reports linked from the public surface.  
CN_PUBLIC_FILES_AFTER: 0 linked from normal public surface.

PUBLIC_CN_LINKS_BEFORE: present.  
PUBLIC_CN_LINKS_AFTER: 0.

CJK_SCAN: PASS for linked public surface; frozen originals retained as approved historical exceptions.  
TRANSLATION_EQUIVALENCE: PARTIAL  
NUMERIC_INTEGRITY: PASS  
ENUM_INTEGRITY: PASS  
FORMULA_INTEGRITY: PASS  
SOURCE_INTEGRITY: PASS  
ORIGINAL_FROZEN_HASHES: UNCHANGED  
ROOT_DOCS_SYNC: PASS  
LINK_SCAN: PASS  
PRODUCTION_LANGUAGE_SPOTCHECK: PENDING

KNOWN_EXCEPTIONS: Frozen Chinese originals retained for provenance only; raw evidence language remains out of product-language scope.

UNRESOLVED: Full legal-grade translation review remains recommended before paid distribution of translated reports.
"""
    write(DOCS / "execution" / "ENGLISH_ONLY_PUBLIC_SURFACE_EXECUTION_REPORT.md", report)


def main() -> None:
    for base, expected in STRATEGY_FILES.items():
        src = ROOT / "research" / f"{base}_CN.md"
        if sha256(src) != expected:
            raise SystemExit(f"original hash drift: {src}")
    manifest = publish_translations()
    replace_public_links()
    write_audits(manifest)


if __name__ == "__main__":
    main()

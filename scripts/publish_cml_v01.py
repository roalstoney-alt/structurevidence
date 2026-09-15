#!/usr/bin/env python3
"""Build the StructEvidence Technical Risk / CML v0.1 domain release."""

from __future__ import annotations

import hashlib
import html
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "0abab7f1246f70445d018478542a6dc0f7b5ab05"
BUILD_COMMIT = os.environ.get("CML_BUILD_COMMIT", f"UNCOMMITTED_FROM_BASE:{BASE_SHA}")
AS_OF = "2026-09-16T00:00:00Z"
CORE_VERSION = "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1"
MODULE_VERSION = "STRUCTEVIDENCE_TECHNICAL_RISK_v0.1"
PROTOCOL_VERSION = "CML_v0.1"
SITE_INTEGRATION_VERSION = "CML_SITE_INTEGRATION_v0.1a"
AUDIT_POLICY_VERSION = "CML_AUDIT_v0.1a"


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


SOURCE_SNAPSHOTS = {
    "AMPHENOL_PCN_26027": {
        "source_type": "MANUFACTURER_PCN_MIRROR",
        "publisher": "Amphenol Communications Solutions",
        "url": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8899/PCN-26027.pdf",
        "local_snapshot_path": "private/cml-source-snapshots/amphenol/PCN-26027.pdf",
    },
    "NXP_202603037DN": {
        "source_type": "MANUFACTURER_DISCONTINUANCE_NOTICE",
        "publisher": "NXP Semiconductors",
        "url": "https://www.nxp.com/pcn/202603037DN",
        "local_snapshot_path": "private/cml-source-snapshots/nxp/202603037DN.html",
    },
    "NXP_MRF101AN_DS": {
        "source_type": "MANUFACTURER_DATASHEET",
        "publisher": "NXP Semiconductors",
        "url": "https://www.nxp.com/docs/en/data-sheet/MRF101AN.pdf",
        "local_snapshot_path": "private/cml-source-snapshots/nxp/MRF101AN.pdf",
    },
    "NXP_MMRF1009H_DS": {
        "source_type": "MANUFACTURER_DATASHEET",
        "publisher": "NXP Semiconductors",
        "url": "https://www.nxp.com/docs/en/data-sheet/MMRF1009H.pdf",
        "local_snapshot_path": "private/cml-source-snapshots/nxp/MMRF1009H.pdf",
    },
    "NXP_MW6S010N_PAGE": {
        "source_type": "MANUFACTURER_PRODUCT_PAGE",
        "publisher": "NXP Semiconductors",
        "url": "https://www.nxp.com/products/radio-frequency-rf/legacy-rf/legacy-rf-power/450-1500-mhz-10-w-28-v-lateral-n-channel-broadband-rf-power-mosfets%3AMW6S010N",
        "local_snapshot_path": "private/cml-source-snapshots/nxp/MW6S010N.html",
    },
    "MURATA_MYMGM5R012_DS": {
        "source_type": "MANUFACTURER_DATASHEET",
        "publisher": "Murata Manufacturing",
        "url": "https://pim.murata.com/asset/pim4/nonIsolatedDCDCconverter/MYMGM5R012ELA5RN_PDF_NONISOLATEDDCDCCONVERTER",
        "local_snapshot_path": "private/cml-source-snapshots/murata/MYMGM5R012ELA5RN.pdf",
    },
    "MURATA_POWER_EOL_INDEX": {
        "source_type": "MANUFACTURER_LIFECYCLE_INDEX",
        "publisher": "Murata Manufacturing",
        "url": "https://www.murata.com/en-global/products/power/discontinued-and-not-recommended",
        "local_snapshot_path": "private/cml-source-snapshots/murata/discontinued-and-not-recommended.html",
    },
    "AMPHENOL_RF_40GHZ_PRODUCT": {
        "source_type": "MANUFACTURER_PRODUCT_PAGE",
        "publisher": "Amphenol RF",
        "url": "https://www.amphenolrf.com/en-us/part/095-725-134-006/10205/",
        "local_snapshot_path": None,
        "snapshot_limitation": "Origin denied automated archival; reviewed public manufacturer page is registered by URL and retrieval date.",
    },
    "AMPHENOL_RF_40GHZ_CUTSHEET": {
        "source_type": "MANUFACTURER_CUTSHEET",
        "publisher": "Amphenol RF",
        "url": "https://www.amphenolrf.com/library/download/link/link_id/600711/",
        "local_snapshot_path": None,
        "snapshot_limitation": "Origin denied automated archival; reviewed public manufacturer PDF is registered by URL and retrieval date.",
    },
}


def source(source_id: str) -> dict:
    row = dict(SOURCE_SNAPSHOTS[source_id])
    row["source_id"] = source_id
    row["retrieved_at"] = AS_OF
    local = row.pop("local_snapshot_path", None)
    row["snapshot_sha256"] = file_digest(ROOT / local) if local and (ROOT / local).exists() else None
    row["verification_status"] = "SNAPSHOT_HASHED" if row["snapshot_sha256"] else "URL_REGISTERED_ARCHIVE_BLOCKED"
    row["snapshot_custody"] = "PRIVATE_INTERNAL" if row["snapshot_sha256"] else "NOT_ARCHIVED"
    return row


PILOTS = [
    {
        "slug": "amphenol-10081811-101-07lf",
        "pilot": "AMPHENOL_EOL_CONNECTOR",
        "record_id": "SE.CML.RECORD.AMPHENOL.10081811-101-07LF.v0.1",
        "technical_item_id": "SE.TECH.AMPHENOL.10081811-101-07LF",
        "manufacturer": "Amphenol Communications Solutions",
        "manufacturer_normalized": "AMPHENOL_COMMUNICATIONS_SOLUTIONS",
        "manufacturer_part_number": "10081811-101-07LF",
        "search_aliases": ["10111608-101-07LF", "10111608-102-07LF", "77316-162LF", "PCN-26-027"],
        "part_number_normalized": "10081811-101-07LF",
        "technical_item_type": "CONNECTOR",
        "product_family": "HPL-578 BERGSTIK",
        "description": "Right-angle single-row BERGSTIK board header; exact drawing attributes remain only partially established in reviewed primary evidence.",
        "package_or_interface": "2.54 mm board-header class; footprint verification required",
        "nominal_application_class": "Board interconnect",
        "manufacturer_product_url": None,
        "source_ids": ["AMPHENOL_PCN_26027"],
        "event": {
            "event_id": "SE.CML.EVENT.AMPHENOL.PCN-26-027.10081811-101-07LF",
            "event_type": "EOL_DECLARED",
            "event_domain": "SUBJECT_EVENT",
            "effective_at": "2027-03-15T00:00:00Z",
            "known_at": "2026-03-16T00:00:00Z",
            "detail": "PCN 26 027 lists the part in an end-of-life action with last-time buy 2026-09-15 and last shipment 2027-09-15.",
        },
        "lifecycle_state": "EOL_ANNOUNCED",
        "oem_replacement_status": "OEM_REPLACEMENT_NOT_LISTED",
        "dependency": "Existing PCB footprint, mating half, contact geometry, plating and electrical loading may constrain migration.",
        "known_facts": [
            "SOURCE_FACT: PCN 26 027 lists four affected BERGSTIK part numbers, including the exact MPN.",
            "SOURCE_FACT: Last-time buy is 2026-09-15; effective change is 2027-03-15; last shipment is 2027-09-15.",
            "SOURCE_FACT: The available-alternatives field is blank in the reviewed notice.",
        ],
        "unknowns": [
            "An OEM-approved replacement is not established by the reviewed evidence.",
            "Exact footprint, mating and plating equivalence for any third-party candidate is not established.",
            "A second Amphenol EOL listing with a different effective date requires manufacturer clarification.",
        ],
        "alternatives": [],
        "compatibility": [
            ("MECHANICAL", "REQUIRES_TEST", "Drawing and dimensional inspection"),
            ("PINOUT", "UNKNOWN", "PCB footprint and row geometry comparison"),
            ("ELECTRICAL", "REQUIRES_TEST", "Current, resistance and dielectric tests"),
            ("MATERIAL", "UNKNOWN", "Contact material and plating stack"),
            ("ENVIRONMENTAL", "REQUIRES_TEST", "Thermal cycling and solderability"),
            ("RELIABILITY", "REQUIRES_TEST", "Insertion, retention and mating-cycle scope"),
        ],
        "verification": ["Mechanical drawing comparison", "PCB footprint inspection", "Contact resistance", "Insulation resistance", "Dielectric withstand", "Solderability", "Insertion and retention force", "Thermal cycling", "Mating compatibility"],
        "decision_paths": ["LIFETIME_BUY", "QUALIFY_SECOND_SOURCE", "REDESIGN"],
        "decision": "Confirm remaining demand before the stated LTB boundary and begin a scope-bound second-source or redesign qualification. No qualified substitute is established.",
        "counter_evidence": "A later public Amphenol EOL list appears to include the same MPN under PCN 26043 with a different effective date. This may be an overlapping notice or later schedule and must be reconciled with Amphenol before procurement action.",
        "freshness_state": "CURRENT_WITH_LIMITATIONS",
        "freshness_reason": "CONFLICTING_PRIMARY_LIFECYCLE_EFFECTIVE_DATE",
        "freshness_rule_type": "EVENT_DRIVEN",
    },
    {
        "slug": "nxp-radio-power-2026",
        "pilot": "NXP_RF_POWER_EOL",
        "record_id": "SE.CML.RECORD.NXP.RADIO-POWER-2026.v0.1",
        "technical_item_id": "SE.TECH.NXP.RADIO-POWER-2026-FAMILY",
        "manufacturer": "NXP Semiconductors",
        "manufacturer_normalized": "NXP_SEMICONDUCTORS",
        "manufacturer_part_number": "RADIO-POWER-2026-FAMILY",
        "search_aliases": ["MRF101AN", "MW6S010GNR1", "MMRF1009HR5", "202603037DN"],
        "part_number_normalized": "RADIO-POWER-2026-FAMILY",
        "technical_item_type": "RF_POWER_SEMICONDUCTOR",
        "product_family": "Radio Power discontinuance / selected representatives",
        "description": "Family-level lifecycle event with representative MRF101AN, MW6S010GNR1 and MMRF1009HR5 migration contexts.",
        "package_or_interface": "Multiple RF transistor packages; board-specific matching networks",
        "nominal_application_class": "RF power amplification",
        "manufacturer_product_url": "https://www.nxp.com/pcn/202603037DN",
        "source_ids": ["NXP_202603037DN", "NXP_MRF101AN_DS", "NXP_MW6S010N_PAGE", "NXP_MMRF1009H_DS"],
        "event": {
            "event_id": "SE.CML.EVENT.NXP.202603037DN.RADIO-POWER",
            "event_type": "EOL_DECLARED",
            "event_domain": "SUBJECT_EVENT",
            "effective_at": "2026-04-01T00:00:00Z",
            "known_at": "2026-03-31T00:00:00Z",
            "detail": "Final Radio Power discontinuance notice lists full withdrawal, limited availability, sole-source classification, 2026-09-30 LTB and 2027-09-30 last delivery for selected representatives.",
        },
        "lifecycle_state": "LAST_TIME_BUY_OPEN",
        "oem_replacement_status": "OEM_REPLACEMENT_NOT_LISTED",
        "dependency": "Device package, bias, frequency, power, thermal path, matching network, PCB layout and ruggedness form a board-level dependency.",
        "known_facts": [
            "SOURCE_FACT: NXP's final notice states the Radio Power product line is being ramped down.",
            "SOURCE_FACT: MRF101AN, MW6S010GNR1 and MMRF1009HR5 are listed with no replacement and a 2026-09-30 LTB.",
            "SOURCE_FACT: MRF101AN is a 50 V wideband 1.8-250 MHz device; MW6S010GNR1 is a 28 V 450-1500 MHz 10 W class device; MMRF1009HR5 is a 50 V 960-1215 MHz 500 W pulse device.",
        ],
        "unknowns": [
            "No reviewed evidence establishes a board drop-in successor for any selected device.",
            "Application-specific matching networks, thermal margins and stability criteria are unknown.",
            "The MRF101AN overview has shown an inconsistent Active label while package/quality and the discontinuance notice indicate EOL.",
        ],
        "alternatives": [
            {"candidate_id": "SE.CML.CANDIDATE.NXP.RP.ARCHITECTURE", "relationship_type": "REDESIGN_REQUIRED", "assessment_state": "PAPER_SCREENING", "description": "Alternate transistor, PA board or module architecture; no specific equivalent is established."}
        ],
        "compatibility": [
            ("MECHANICAL", "MISMATCH", "Representative devices use different packages"),
            ("ELECTRICAL", "REQUIRES_TEST", "Bias, supply and gain vary by device/application"),
            ("RF", "REQUIRES_TEST", "Frequency, output power, gain, efficiency and harmonics"),
            ("THERMAL", "REQUIRES_TEST", "Junction-to-case and board cooling"),
            ("RELIABILITY", "REQUIRES_TEST", "Load mismatch and long-duration operation"),
            ("MANUFACTURING", "REQUIRES_TEST", "PCB layout and matching-network redesign"),
        ],
        "verification": ["S-parameters where applicable", "Small-signal stability", "Gain and output power", "PAE or drain efficiency", "Harmonics", "Thermal characterization", "Load-mismatch ruggedness", "Temperature sweep", "Long-duration operation"],
        "decision_paths": ["LIFETIME_BUY", "QUALIFY_ALTERNATIVE", "REDESIGN"],
        "decision": "Treat the notice as a lifecycle trigger. Separate lifetime-buy analysis from engineering migration; any alternate device requires board-level RF and thermal qualification.",
        "counter_evidence": "Some NXP overview surfaces have retained an Active label for MRF101AN. The later dated discontinuance notice and package status are treated as stronger lifecycle evidence, while the conflict remains visible.",
        "freshness_state": "CURRENT_WITH_LIMITATIONS",
        "freshness_reason": "MANUFACTURER_INTERFACE_STATUS_CONFLICT",
        "freshness_rule_type": "EVENT_DRIVEN",
    },
    {
        "slug": "murata-mymgm5r012ela5rnd",
        "pilot": "MURATA_DCDC_NRND",
        "record_id": "SE.CML.RECORD.MURATA.MYMGM5R012ELA5RND.v0.1",
        "technical_item_id": "SE.TECH.MURATA.MYMGM5R012ELA5RND",
        "manufacturer": "Murata Manufacturing",
        "manufacturer_normalized": "MURATA_MANUFACTURING",
        "manufacturer_part_number": "MYMGM5R012ELA5RND",
        "search_aliases": ["MYMGM5R012ELA5RN", "MonoBK 12A"],
        "part_number_normalized": "MYMGM5R012ELA5RND",
        "technical_item_type": "POWER_MODULE",
        "product_family": "MonoBK 12 A DC-DC converter series",
        "description": "Non-isolated point-of-load DC-DC converter variant explicitly marked NRND in the reviewed Murata datasheet.",
        "package_or_interface": "10.5 x 9.0 x 5.0 mm module class",
        "nominal_application_class": "12 V input point-of-load conversion",
        "manufacturer_product_url": "https://www.murata.com/en-global/products/power",
        "source_ids": ["MURATA_MYMGM5R012_DS", "MURATA_POWER_EOL_INDEX"],
        "event": {
            "event_id": "SE.CML.EVENT.MURATA.MYMGM5R012ELA5RND.NRND",
            "event_type": "NRND_DECLARED",
            "event_domain": "SUBJECT_EVENT",
            "effective_at": "2025-07-07T00:00:00Z",
            "known_at": "2026-09-16T00:00:00Z",
            "detail": "The reviewed Murata datasheet identifies the D-suffix variant as NRND; an earlier effective date is not established, so the document revision date is used as the observable boundary with limitation.",
        },
        "lifecycle_state": "NRND",
        "oem_replacement_status": "OEM_REPLACEMENT_UNRESOLVED",
        "dependency": "Input range, output voltage/current, regulation, efficiency, control polarity, pinout, thermal derating and board layout define migration scope.",
        "known_facts": [
            "SOURCE_FACT: MYMGM5R012ELA5RND is marked NRND in the manufacturer datasheet.",
            "SOURCE_FACT: The series is a 12 A non-isolated DC-DC converter with 7.5-15 V input and a 10.5 x 9.0 x 5.0 mm package class.",
            "SOURCE_FACT: Murata maintains a separate discontinued/NRND index and a DC-DC cross-reference surface.",
        ],
        "unknowns": [
            "An exact OEM successor for this suffix is not established in the reviewed snapshot.",
            "Customer output setpoint, transient limits, EMI class and thermal environment are unknown.",
            "No bench comparison or customer qualification evidence is present.",
        ],
        "alternatives": [],
        "compatibility": [
            ("MECHANICAL", "REQUIRES_TEST", "Package and land-pattern comparison"),
            ("PINOUT", "UNKNOWN", "Pin map and control polarity"),
            ("ELECTRICAL", "REQUIRES_TEST", "Line/load regulation and transient response"),
            ("THERMAL", "REQUIRES_TEST", "Derating in customer airflow and board stack"),
            ("EMI_EMC", "REQUIRES_TEST", "Conducted and radiated emissions"),
            ("SAFETY", "NOT_APPLICABLE", "Non-isolated module; system-level safety scope remains separate"),
        ],
        "verification": ["No-load and full-load", "Load transient", "Line transient", "Startup and shutdown", "Ripple and noise", "Efficiency", "Thermal derating", "Short circuit", "EMI/EMC", "Temperature sweep"],
        "decision_paths": ["MONITOR", "QUALIFY_SECOND_SOURCE", "REDESIGN"],
        "decision": "Freeze the exact suffix and customer operating envelope, then request Murata cross-reference confirmation. Any candidate remains paper-level until electrical, thermal and EMI verification is complete.",
        "counter_evidence": "The base series remains documented and only a specific suffix is visibly marked NRND. This may reduce immediate operational impact if the customer uses another orderable suffix; BOM identity must be exact.",
        "freshness_state": "POLICY_NOT_CONFIGURED",
        "freshness_reason": "EXACT_LIFECYCLE_EFFECTIVE_DATE_UNRESOLVED",
        "freshness_rule_type": "UNCONFIGURED",
    },
    {
        "slug": "amphenol-rf-095-725-134-006",
        "pilot": "RF40_CABLE_ASSEMBLY",
        "record_id": "SE.CML.RECORD.AMPHENOL-RF.095-725-134-006.v0.1",
        "technical_item_id": "SE.TECH.AMPHENOL-RF.095-725-134-006",
        "manufacturer": "Amphenol RF",
        "manufacturer_normalized": "AMPHENOL_RF",
        "manufacturer_part_number": "095-725-134-006",
        "search_aliases": ["095-725-134-XXX", "2.92 mm", "SMPM", "40 GHz"],
        "part_number_normalized": "095-725-134-006",
        "technical_item_type": "RF_CABLE_ASSEMBLY",
        "product_family": "2.92 mm plug to SMPM plug cable assemblies",
        "description": "Six-inch, 50 ohm, 0.085-inch conformable cable assembly with 2.92 mm and SMPM straight plugs.",
        "package_or_interface": "2.92 mm plug to SMPM plug, 6 inches",
        "nominal_application_class": "Microwave interconnect up to 40 GHz",
        "manufacturer_product_url": "https://www.amphenolrf.com/en-us/part/095-725-134-006/10205/",
        "source_ids": ["AMPHENOL_RF_40GHZ_PRODUCT", "AMPHENOL_RF_40GHZ_CUTSHEET"],
        "event": {
            "event_id": "SE.CML.EVENT.AMPHENOL-RF.095-725-134-006.BASELINE",
            "event_type": "CANDIDATE_IDENTIFIED",
            "event_domain": "SUBJECT_EVENT",
            "effective_at": "2026-05-07T00:00:00Z",
            "known_at": "2026-09-16T00:00:00Z",
            "detail": "Active manufacturer reference assembly selected as a qualification benchmark; this is not an EOL event.",
        },
        "lifecycle_state": "ACTIVE",
        "oem_replacement_status": "OEM_REPLACEMENT_UNRESOLVED",
        "dependency": "Complete-assembly electrical performance depends on both connectors, cable, termination process, bend history, length and calibration reference plane.",
        "known_facts": [
            "SOURCE_FACT: The exact assembly is listed Active, 6.00 in (153 mm), 50 ohm, and 40 GHz maximum.",
            "SOURCE_FACT: Interfaces are 2.92 mm straight plug to SMPM straight plug on 0.085-inch conformable cable.",
            "SOURCE_FACT: The family cutsheet states DC-40 GHz interface ranges and warns specifications may vary by exact part number.",
        ],
        "unknowns": [
            "No independent VNA trace, per-unit insertion-loss limit or return-loss acceptance curve is present.",
            "Power handling, phase stability and flex-life limits are not established in reviewed evidence.",
            "No alternate supplier assembly has been qualified against this benchmark.",
        ],
        "alternatives": [],
        "compatibility": [
            ("MECHANICAL", "REQUIRES_TEST", "Connector gauges, length and bend envelope"),
            ("RF", "REQUIRES_TEST", "S11, S21, VSWR and insertion loss through 40 GHz"),
            ("MATERIAL", "MATCH", "Manufacturer states gold-plated interfaces for family"),
            ("ENVIRONMENTAL", "REQUIRES_TEST", "Temperature and flex behavior"),
            ("RELIABILITY", "REQUIRES_TEST", "Mating repeatability and cycle scope"),
            ("MANUFACTURING", "REQUIRES_TEST", "Termination process and lot consistency"),
        ],
        "verification": ["Calibrated VNA with defined reference planes", "S11 and return loss", "S21 and insertion loss", "VSWR", "Mating repeatability", "Mechanical inspection", "Flex behavior", "Temperature behavior", "Phase stability only when required"],
        "decision_paths": ["QUALIFY_SECOND_SOURCE", "MONITOR"],
        "decision": "Use the exact assembly as a benchmark, not as proof that any cable using 40 GHz-capable connectors is equivalent. Freeze VNA method and acceptance limits before supplier comparison.",
        "counter_evidence": "The item is an active off-the-shelf assembly, so substitution may not be operationally necessary. The pilot tests whether CML can structure qualification evidence without inventing a lifecycle crisis.",
        "freshness_state": "POLICY_NOT_CONFIGURED",
        "freshness_reason": "ACTIVE_BENCHMARK_HAS_NO_EMPIRICAL_CADENCE",
        "freshness_rule_type": "UNCONFIGURED",
    },
]


def build_source_register(pilot: dict) -> dict:
    return {
        "registry_id": f"{pilot['record_id']}.sources",
        "retrieved_at": AS_OF,
        "sources": [source(source_id) for source_id in pilot["source_ids"]],
        "source_hierarchy_rule": "Manufacturer evidence controls lifecycle; distributor evidence may supplement but never override.",
    }


def build_item(pilot: dict) -> dict:
    fields = ["technical_item_id", "manufacturer", "manufacturer_normalized", "manufacturer_part_number", "part_number_normalized", "technical_item_type", "product_family", "description", "package_or_interface", "nominal_application_class", "manufacturer_product_url"]
    value = {key: pilot[key] for key in fields}
    value.update({"manufacturer_part_number_exact": pilot["manufacturer_part_number"], "datasheet_refs": pilot["source_ids"], "created_at": AS_OF, "record_version": PROTOCOL_VERSION})
    return value


def build_record(pilot: dict, source_register: dict, item: dict) -> dict:
    event = dict(pilot["event"])
    event.update({"technical_item_id": pilot["technical_item_id"], "source_refs": pilot["source_ids"], "verification_status": "PRIMARY_SOURCE_REVIEWED", "created_at": AS_OF})
    compatibility = [{"dimension": dimension, "state": state, "evidence_or_test": evidence} for dimension, state, evidence in pilot["compatibility"]]
    core = {
        "core_version": CORE_VERSION,
        "record_id": pilot["record_id"],
        "subject_id": pilot["technical_item_id"],
        "subject_class": "TECHNICAL_ITEM",
        "domain": "TECHNICAL_RISK",
        "protocol": "CML",
        "source_refs": pilot["source_ids"],
        "artifact_refs": [f"{row['source_id']}:{row['snapshot_sha256']}" for row in source_register["sources"] if row.get("snapshot_sha256")],
        "effective_at": event["effective_at"],
        "known_at": event["known_at"],
        "created_at": AS_OF,
        "updated_at": AS_OF,
        "verification_status": "REVIEWED_WITH_LIMITATIONS",
        "correction_status": "NO_CORRECTION_RECORDED",
        "supersession_status": "CURRENT",
        "policy_version": "RDL_FRESHNESS_v0.1a+CML_PROFILE_v0.1",
    }
    payload = {
        "identity": item,
        "event": event,
        "dependency": {"context": pilot["dependency"], "client_scope": "NOT_PROVIDED"},
        "evidence": {"known_facts": pilot["known_facts"], "unknowns": pilot["unknowns"], "source_register_id": source_register["registry_id"]},
        "alternative": {"oem_replacement_status": pilot["oem_replacement_status"], "candidates": pilot["alternatives"]},
        "verification": {"qualification_state": "LAB_VERIFICATION_REQUIRED", "compatibility_matrix": compatibility, "requirements": pilot["verification"]},
        "decision": {"supported_paths": pilot["decision_paths"], "current_recommendation": pilot["decision"], "claim_type": "DECISION_RECOMMENDATION"},
        "lifecycle_state": pilot["lifecycle_state"],
        "freshness_state": pilot["freshness_state"],
        "freshness_reason": pilot["freshness_reason"],
        "freshness_rule_type": pilot["freshness_rule_type"],
        "product_context": "PUBLIC_TECHNICAL_RECORD",
        "counter_evidence": pilot["counter_evidence"],
        "public_private_boundary": "PUBLIC_EVIDENCE_ONLY_NO_CLIENT_BOM",
    }
    core["input_hash"] = digest({"sources": source_register, "payload": payload})
    core["record_hash"] = digest({"core": core, "payload": payload})
    return {"core": core, "cml": payload}


def schema_files() -> dict[str, dict]:
    rdl_states = json.loads((ROOT / "rdl/freshness/config/freshness_precedence.json").read_text(encoding="utf-8"))["precedence"]
    core_required = ["core_version", "record_id", "subject_id", "subject_class", "domain", "protocol", "source_refs", "artifact_refs", "effective_at", "known_at", "created_at", "updated_at", "verification_status", "correction_status", "supersession_status", "policy_version", "input_hash", "record_hash"]
    string = {"type": "string"}
    string_array = {"type": "array", "items": {"type": "string"}}
    identity_properties = {
        "technical_item_id": {"type": "string", "description": "Permanent exact technical-item identifier."},
        "manufacturer": {"type": "string", "minLength": 1, "description": "Manufacturer display name."},
        "manufacturer_normalized": {"type": "string", "description": "Non-destructive matching form of manufacturer name."},
        "manufacturer_part_number": {"type": "string", "minLength": 1, "description": "Manufacturer part number as published."},
        "manufacturer_part_number_exact": {"type": "string", "minLength": 1, "description": "Byte-identical source-derived manufacturer part number."},
        "part_number_normalized": {"type": "string", "description": "Search form that does not replace the exact identity."},
        "technical_item_type": {"enum": ["CONNECTOR", "RF_CONNECTOR", "RF_CABLE_ASSEMBLY", "POWER_MODULE", "RF_POWER_SEMICONDUCTOR", "IC", "MODULE", "ASSEMBLY", "OTHER"]},
        "product_family": {"type": "string"}, "description": {"type": "string"}, "package_or_interface": {"type": "string"},
        "nominal_application_class": {"type": "string"}, "manufacturer_product_url": {"type": ["string", "null"]},
        "datasheet_refs": string_array, "created_at": string, "record_version": string,
    }
    event_properties = {"event_id": string, "event_type": {"type": "string", "enum": CONFIG["event_types"]}, "event_domain": {"type": "string", "enum": CONFIG["event_domains"]}, "technical_item_id": string, "effective_at": string, "known_at": string, "source_refs": string_array, "verification_status": string, "created_at": string, "detail": string}
    candidate_properties = {"candidate_id": string, "relationship_type": string, "assessment_state": {"type": "string", "enum": CONFIG["qualification_states"]}, "description": string}
    compatibility_properties = {"dimension": string, "state": {"type": "string", "enum": ["MATCH", "ACCEPTABLE_DIFFERENCE", "MISMATCH", "UNKNOWN", "REQUIRES_TEST", "NOT_APPLICABLE"]}, "evidence_or_test": string}
    return {
        "evidence/core/schema/evidence_core_record.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://structevidence.com/schema/evidence-core/v0.1", "title": "StructEvidence Evidence Core Record", "type": "object", "required": core_required,
            "properties": {key: (string_array if key in {"source_refs", "artifact_refs"} else {"type": "string", "description": f"Shared Evidence Core field: {key}."}) for key in core_required}, "additionalProperties": False,
        },
        "technical-risk/schema/technical_item.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://structevidence.com/schema/cml/technical-item/v0.1", "title": "CML Technical Item", "type": "object", "required": list(identity_properties), "properties": identity_properties, "additionalProperties": False,
        },
        "technical-risk/schema/cml_public_record.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "title": "CML Public Record", "type": "object", "required": ["core", "cml"],
            "properties": {"core": {"$ref": "../../evidence/core/schema/evidence_core_record.schema.json"}, "cml": {"type": "object", "required": ["identity", "event", "dependency", "evidence", "alternative", "verification", "decision", "lifecycle_state", "freshness_state", "freshness_reason", "freshness_rule_type", "counter_evidence", "public_private_boundary", "product_context"], "properties": {
                "identity": {"$ref": "technical_item.schema.json"}, "event": {"$ref": "cml_event.schema.json"},
                "dependency": {"type": "object", "required": ["context", "client_scope"], "properties": {"context": string, "client_scope": string}, "additionalProperties": False},
                "evidence": {"type": "object", "required": ["known_facts", "unknowns", "source_register_id"], "properties": {"known_facts": string_array, "unknowns": string_array, "source_register_id": string}, "additionalProperties": False},
                "alternative": {"type": "object", "required": ["oem_replacement_status", "candidates"], "properties": {"oem_replacement_status": string, "candidates": {"type": "array", "items": {"$ref": "cml_candidate.schema.json"}}}, "additionalProperties": False},
                "verification": {"type": "object", "required": ["qualification_state", "compatibility_matrix", "requirements"], "properties": {"qualification_state": {"type": "string", "enum": CONFIG["qualification_states"]}, "compatibility_matrix": {"type": "array", "items": {"$ref": "cml_compatibility.schema.json"}}, "requirements": string_array}, "additionalProperties": False},
                "decision": {"type": "object", "required": ["supported_paths", "current_recommendation", "claim_type"], "properties": {"supported_paths": string_array, "current_recommendation": string, "claim_type": string}, "additionalProperties": False},
                "lifecycle_state": {"type": "string", "enum": CONFIG["lifecycle_states"]}, "freshness_state": {"type": "string", "enum": rdl_states}, "freshness_reason": string, "freshness_rule_type": {"type": "string", "enum": ["EVENT_DRIVEN", "REVISION_DRIVEN", "REVISION_AND_EXPIRY_DRIVEN", "SCOPE_AND_REVISION_DRIVEN", "UNCONFIGURED"]}, "counter_evidence": string, "public_private_boundary": string, "product_context": {"type": "string", "enum": PRODUCT_CONTEXTS},
            }, "additionalProperties": False}}, "additionalProperties": False,
        },
        "technical-risk/schema/cml_event.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://structevidence.com/schema/cml/event/v0.1", "title": "CML Event", "type": "object", "required": list(event_properties), "properties": event_properties, "additionalProperties": False},
        "technical-risk/schema/cml_candidate.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://structevidence.com/schema/cml/candidate/v0.1", "title": "CML Replacement Candidate", "type": "object", "required": list(candidate_properties), "properties": candidate_properties, "additionalProperties": False},
        "technical-risk/schema/cml_compatibility.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://structevidence.com/schema/cml/compatibility/v0.1", "title": "CML Compatibility Cell", "type": "object", "required": list(compatibility_properties), "properties": compatibility_properties, "additionalProperties": False},
        "technical-risk/schema/cml_test_requirement.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "CML Test Requirement", "type": "object", "required": ["test_requirement_id", "original_item_id", "candidate_id", "test_category", "test_name", "standard", "test_method", "acceptance_criteria", "required_equipment", "third_party_lab_required", "customer_lab_required", "destructive", "sample_quantity", "evidence_basis", "status"], "properties": {key: ({"type": ["string", "null"]} if key == "candidate_id" else string) for key in ["test_requirement_id", "original_item_id", "candidate_id", "test_category", "test_name", "standard", "test_method", "acceptance_criteria", "required_equipment", "third_party_lab_required", "customer_lab_required", "destructive", "sample_quantity", "evidence_basis", "status"]}, "additionalProperties": False},
        "technical-risk/schema/cml_release_manifest.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "CML Release Manifest", "type": "object", "required": ["record_id", "record_hash", "artifact_hashes", "freshness_state", "freshness_reason", "freshness_rule_type", "gdr_version", "release_state", "authorization_state", "paid_delivery_state", "evaluation_as_of"], "properties": {"record_id": string, "record_hash": string, "artifact_hashes": {"type": "object", "additionalProperties": {"type": "string"}}, "freshness_state": {"type": "string", "enum": rdl_states}, "freshness_reason": string, "freshness_rule_type": string, "gdr_version": string, "release_state": string, "authorization_state": string, "paid_delivery_state": string, "evaluation_as_of": string}, "additionalProperties": False},
        "technical-risk/schema/CML_SNIPE_REPORT_v0.1.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "CML Snipe Report v0.1", "type": "object", "required": ["executive_technical_issue", "named_item", "lifecycle_event", "evidence_chain", "unknowns", "required_verification", "current_recommendation", "freshness", "verification_record", "source_appendix"]},
    }


CONFIG = {
    "subject_class": "TECHNICAL_ITEM",
    "domain": "TECHNICAL_RISK",
    "protocol": "CML",
    "pipeline": ["IDENTITY", "EVENT", "DEPENDENCY", "EVIDENCE", "ALTERNATIVE", "VERIFICATION", "DECISION"],
    "lifecycle_states": ["ACTIVE", "NRND", "EOL_ANNOUNCED", "LAST_TIME_BUY_OPEN", "LAST_TIME_BUY_CLOSED", "LAST_SHIP_PENDING", "DISCONTINUED", "OBSOLETE", "STATUS_UNRESOLVED"],
    "event_types": ["PCN_ISSUED", "NRND_DECLARED", "EOL_DECLARED", "LAST_TIME_BUY_OPENED", "LAST_TIME_BUY_REACHED", "LAST_SHIP_REACHED", "OEM_REPLACEMENT_ADDED", "OEM_REPLACEMENT_REMOVED", "DATASHEET_REVISION", "PACKAGE_REVISION", "CERTIFICATION_CHANGE", "MANUFACTURING_SITE_CHANGE", "MATERIAL_CHANGE", "SPECIFICATION_CHANGE", "CANDIDATE_IDENTIFIED", "CANDIDATE_REJECTED", "CANDIDATE_TESTED", "CANDIDATE_FAILED", "CANDIDATE_QUALIFIED", "QUALIFICATION_REVOKED"],
    "event_domains": ["SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"],
    "dimensions": ["LIFECYCLE_STATE", "REPLACEMENT_AVAILABILITY", "SOURCE_DEPENDENCY", "QUALIFICATION_STATE"],
    "qualification_states": ["NOT_ASSESSED", "PAPER_SCREENING", "PAPER_COMPATIBLE_WITH_UNKNOWNS", "LAB_VERIFICATION_REQUIRED", "LAB_TESTING", "QUALIFICATION_FAILED", "QUALIFIED_FOR_DEFINED_SCOPE", "CUSTOMER_VALIDATION_REQUIRED", "CUSTOMER_APPROVED", "SUPERSEDED"],
}


EVIDENCE_FAMILIES = ["MANUFACTURER_LIFECYCLE_EVIDENCE", "MANUFACTURER_DATASHEET", "MANUFACTURER_PCN", "OEM_REPLACEMENT_EVIDENCE", "PACKAGE_INTERFACE_EVIDENCE", "CERTIFICATION_EVIDENCE", "TECHNICAL_COMPARISON", "COUNTER_EVIDENCE", "INDEPENDENT_TEST_EVIDENCE", "CUSTOMER_QUALIFICATION_EVIDENCE", "SUPPLY_AVAILABILITY_EVIDENCE", "SOURCE_DEPENDENCY", "CORRECTION_STATUS", "SUPERSESSION_STATUS", "AUTHORIZATION_STATUS"]
PRODUCT_CONTEXTS = ["PUBLIC_TECHNICAL_RECORD", "SNIPE_BRIEF", "SUBSTITUTION_EVIDENCE_REPORT", "CUSTOM_BOM_AUDIT", "TECHNICAL_DUE_DILIGENCE", "TECHNICAL_MONITOR"]


def generate_data_dictionary() -> tuple[str, dict]:
    schema_paths = {
        "core": ROOT / "evidence/core/schema/evidence_core_record.schema.json",
        "cml": ROOT / "technical-risk/schema/cml_public_record.schema.json",
        "test_requirements[]": ROOT / "technical-risk/schema/cml_test_requirement.schema.json",
        "release_manifest": ROOT / "technical-risk/schema/cml_release_manifest.schema.json",
    }
    schema_lookup = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in [*schema_paths.values(), *(ROOT / "technical-risk/schema").glob("*.schema.json")]}
    rows: dict[str, dict] = {}

    def walk(node: dict, path: str, schema_name: str, required: bool = True) -> None:
        if "$ref" in node:
            target = schema_lookup[Path(node["$ref"]).name]
            walk(target, path, Path(node["$ref"]).name, required)
            return
        properties = node.get("properties", {})
        if properties:
            required_names = set(node.get("required", []))
            for name, child in properties.items():
                child_path = f"{path}.{name}" if path else name
                walk(child, child_path, schema_name, name in required_names)
            return
        item = node.get("items")
        if isinstance(item, dict) and (item.get("properties") or item.get("$ref")):
            walk(item, f"{path}[]", schema_name, required)
            return
        field_name = path.rsplit(".", 1)[-1].replace("[]", "")
        values = node.get("enum", [])
        field_type = node.get("type", "enum" if values else "object")
        if isinstance(field_type, list):
            field_type = " | ".join(field_type)
        boundary = "public"
        authority = "Evidence Core" if path.startswith("core.") else "CML schema / reviewed evidence"
        freshness = "RDL policy state" if "freshness" in path else "event or revision driven"
        supersession = "new record; predecessor retained" if path.endswith(("record_hash", "record_id")) else "retained in record history"
        rows[path] = {"json_path": path, "field_name": field_name, "schema": schema_name, "type": field_type, "required": required, "boundary": boundary, "description": node.get("description", field_name.replace("_", " ").capitalize()), "allowed_values": values, "source_authority": authority, "freshness_behavior": freshness, "supersession_behavior": supersession, "validation_rule": "schema enum" if values else f"JSON Schema {field_type}"}

    for prefix, path in schema_paths.items():
        schema = json.loads(path.read_text(encoding="utf-8"))
        if prefix == "cml":
            walk(schema["properties"]["cml"], "cml", path.name)
        else:
            walk(schema, prefix, path.name)

    boundary = json.loads((ROOT / "technical-risk/config/public_private_boundary.json").read_text(encoding="utf-8"))
    for name in boundary["private"]:
        path = f"private_reserved.{name}"
        rows[path] = {"json_path": path, "field_name": name, "schema": "public_private_boundary.json", "type": "reserved", "required": False, "boundary": "private / prohibited in Public Verify", "description": f"Private engagement field: {name.replace('_', ' ')}.", "allowed_values": [], "source_authority": "client / NDA", "freshness_behavior": "engagement policy", "supersession_behavior": "never copied into public record", "validation_rule": "must be absent from public artifacts"}

    columns = ["JSON path", "field name", "schema", "type", "required", "boundary", "description", "allowed values", "source authority", "freshness behavior", "supersession behavior", "validation rule"]
    lines = ["# CML Technical Risk Data Dictionary v0.1", "", f"Generated from Evidence Core and CML schemas plus boundary configuration. Authoritative path count: **{len(rows)}**.", "", "| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for path, row in sorted(rows.items()):
        values = ", ".join(row["allowed_values"]) if row["allowed_values"] else "-"
        values = values.replace("|", "\\|")
        cells = [f"`{path}`", row["field_name"], f"`{row['schema']}`", str(row["type"]), "yes" if row["required"] else "no", row["boundary"], row["description"], values, row["source_authority"], row["freshness_behavior"], row["supersession_behavior"], row["validation_rule"]]
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in cells) + " |")
    index = {"dictionary_version": "CML_DATA_DICTIONARY_v0.1", "generated_from": [str(path.relative_to(ROOT)) for path in schema_paths.values()] + ["technical-risk/config/public_private_boundary.json"], "authoritative_paths": sorted(rows), "row_count": len(rows)}
    return "\n".join(lines) + "\n", index


def page(title: str, description: str, body: str, prefix: str, canonical_path: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{html.escape(title)} - StructEvidence</title><meta name=\"description\" content=\"{html.escape(description)}\"><link rel=\"canonical\" href=\"https://structurevidence.org{html.escape(canonical_path)}\"><link rel=\"icon\" href=\"{prefix}assets/favicon.svg\" type=\"image/svg+xml\"><link rel=\"stylesheet\" href=\"{prefix}assets/technical-risk.css?v=20260916\"></head>
<body><header class=\"tr-header\"><a class=\"tr-brand\" href=\"{prefix}technical-risk/\"><span>SE</span><strong>StructEvidence</strong><em>Technical Risk</em></a><nav><a href=\"{prefix}technical-risk/search/\">Search</a><a href=\"{prefix}technical-risk/method/\">Method</a><a href=\"{prefix}technical-risk/request-analysis/\" class=\"nav-action\">Request analysis</a></nav></header><main>{body}</main><footer class=\"tr-footer\"><strong>StructEvidence</strong><span>Evidence for technical supply-chain decisions.</span><a href=\"{prefix}technical-risk/method/\">Method</a><a href=\"{prefix}privacy.html\">Privacy</a><a href=\"{prefix}terms.html\">Terms</a></footer></body></html>"""


def status_class(value: str) -> str:
    if value in {"ACTIVE", "MATCH", "CURRENT", "SNAPSHOT_HASHED"}:
        return "ok"
    if value in {"MISMATCH", "QUALIFICATION_FAILED", "EOL_ANNOUNCED", "DISCONTINUED"}:
        return "alert"
    return "review"


def record_page(record: dict, slug: str) -> str:
    core, cml = record["core"], record["cml"]
    item, event = cml["identity"], cml["event"]
    facts = "".join(f"<li>{html.escape(x)}</li>" for x in cml["evidence"]["known_facts"])
    unknowns = "".join(f"<li>{html.escape(x)}</li>" for x in cml["evidence"]["unknowns"])
    matrix = "".join(f"<tr><td>{html.escape(x['dimension'].replace('_', ' ').title())}</td><td><span class=\"state {status_class(x['state'])}\">{html.escape(x['state'])}</span></td><td>{html.escape(x['evidence_or_test'])}</td></tr>" for x in cml["verification"]["compatibility_matrix"])
    tests = "".join(f"<li>{html.escape(x)}</li>" for x in cml["verification"]["requirements"])
    paths = "".join(f"<span class=\"path\">{html.escape(x.replace('_', ' '))}</span>" for x in cml["decision"]["supported_paths"])
    alternatives = cml["alternative"]["candidates"]
    candidate_html = "".join(f"<article><strong>{html.escape(x['relationship_type'].replace('_', ' '))}</strong><p>{html.escape(x['description'])}</p><span>{html.escape(x['assessment_state'])}</span></article>" for x in alternatives) or "<p class=\"empty\">No candidate is established in the reviewed evidence. Empty is an explicit state, not a missing screen.</p>"
    body = f"""
<section class=\"record-hero\"><div><p class=\"eyebrow\">CML public technical record</p><h1>{html.escape(item['manufacturer_part_number'])}</h1><p>{html.escape(item['manufacturer'])} / {html.escape(item['product_family'])}</p></div><div class=\"record-state\"><span>Lifecycle</span><strong class=\"state {status_class(cml['lifecycle_state'])}\">{html.escape(cml['lifecycle_state'])}</strong><span>Qualification</span><strong class=\"state review\">{html.escape(cml['verification']['qualification_state'])}</strong></div></section>
<section class=\"identity-strip\"><div><span>Item type</span><strong>{html.escape(item['technical_item_type'].replace('_', ' '))}</strong></div><div><span>Effective</span><strong>{event['effective_at'][:10]}</strong></div><div><span>Known</span><strong>{event['known_at'][:10]}</strong></div><div><span>Freshness</span><strong>{html.escape(cml['freshness_state'])}</strong></div><div><span>Record hash</span><code>{core['record_hash'][:16]}...</code></div></section>
<section class=\"tr-section issue-grid\"><div><p class=\"eyebrow\">Technical issue</p><h2>What changed</h2><p class=\"lead\">{html.escape(event['detail'])}</p></div><aside><span class=\"event-type\">{html.escape(event['event_type'])}</span><p>{html.escape(cml['dependency']['context'])}</p></aside></section>
<section class=\"tr-section evidence-split\"><div><p class=\"eyebrow\">Established</p><h2>Known facts</h2><ul>{facts}</ul></div><div><p class=\"eyebrow\">Open</p><h2>What is not yet known</h2><ul>{unknowns}</ul></div></section>
<section class=\"tr-section\"><div class=\"section-heading\"><div><p class=\"eyebrow\">Alternative</p><h2>Replacement paths</h2></div><span class=\"state review\">{html.escape(cml['alternative']['oem_replacement_status'])}</span></div><div class=\"candidate-grid\">{candidate_html}</div></section>
<section class=\"tr-section\"><div class=\"section-heading\"><div><p class=\"eyebrow\">Verification</p><h2>Compatibility matrix</h2></div><span class=\"boundary-label\">PAPER != QUALIFIED</span></div><div class=\"table-wrap\"><table><thead><tr><th>Dimension</th><th>Current state</th><th>Required evidence or test</th></tr></thead><tbody>{matrix}</tbody></table></div><div class=\"test-list\"><h3>Required verification</h3><ul>{tests}</ul></div></section>
<section class=\"decision-band\"><div><p class=\"eyebrow\">Current decision path</p><h2>{html.escape(cml['decision']['current_recommendation'])}</h2><div class=\"paths\">{paths}</div></div><a class=\"button\" href=\"../../request-analysis/?record={html.escape(slug)}\">Request technical analysis</a></section>
<section class=\"tr-section audit-grid\"><div><p class=\"eyebrow\">Counter-evidence</p><h2>What weakens the case</h2><p>{html.escape(cml['counter_evidence'])}</p></div><div><p class=\"eyebrow\">Verify</p><h2>Lineage</h2><dl><dt>Record ID</dt><dd><code>{html.escape(core['record_id'])}</code></dd><dt>Input hash</dt><dd><code>{core['input_hash']}</code></dd><dt>Record hash</dt><dd><code>{core['record_hash']}</code></dd><dt>Boundary</dt><dd>{html.escape(cml['public_private_boundary'])}</dd></dl><a href=\"../../verify/{html.escape(slug)}/\">Open verification record</a></div></section>"""
    return page(item["manufacturer_part_number"], item["description"], body, "../../../", f"/technical-risk/record/{slug}/")


def landing_page(records: list[dict]) -> str:
    cards = "".join(f"<a class=\"record-card\" href=\"record/{p['slug']}/\"><span>{p['technical_item_type'].replace('_', ' ')}</span><h3>{html.escape(p['manufacturer_part_number'])}</h3><p>{html.escape(p['manufacturer'])}</p><strong class=\"state {status_class(r['cml']['lifecycle_state'])}\">{html.escape(r['cml']['lifecycle_state'])}</strong></a>" for p, r in zip(PILOTS, records))
    body = f"""
<section class=\"tr-hero\"><div><p class=\"eyebrow\">StructEvidence Technical Risk</p><h1>Technical change becomes a decision record.</h1><p>Lifecycle notices, engineering dependencies, alternative claims and qualification evidence remain auditable instead of being compressed into a risk score.</p><div class=\"hero-actions\"><a class=\"button\" href=\"search/\">Search technical records</a><a class=\"text-link\" href=\"method/\">Read the CML method</a></div></div><aside class=\"pipeline\"><span>Identity</span><i></i><span>Event</span><i></i><span>Dependency</span><i></i><span>Evidence</span><i></i><span>Alternative</span><i></i><span>Verification</span><i></i><span>Decision</span></aside></section>
<section class=\"principle-band\"><div><span>Evidence Core</span><strong>Shared provenance + dual clock</strong></div><div><span>Domain</span><strong>Technical Risk / CML</strong></div><div><span>Release</span><strong>Method pilot</strong></div><div><span>Boundary</span><strong>No numeric risk score</strong></div></section>
<section class=\"tr-section intro\"><div><p class=\"eyebrow\">CML / Component Migration &amp; Lifecycle</p><h2>Identify the event. Map the dependency. Test the alternatives. Preserve the evidence.</h2></div><p>StructEvidence does not create a second evidence database for components. CML is a domain of the same Evidence Core, designed so catalysts, specialty chemicals, APIs, optics, motors and bearings can later reuse the same decision grammar.</p></section>
<section class=\"tr-section\"><div class=\"section-heading\"><div><p class=\"eyebrow\">Four-target pilot</p><h2>Current public records</h2></div><a href=\"search/\">Search exact identity</a></div><div class=\"record-grid\">{cards}</div></section>
<section class=\"decision-band\"><div><p class=\"eyebrow\">Private decision context</p><h2>Need an item, assembly or BOM reviewed?</h2><p>Client BOM, usage, pricing, drawings and qualification limits remain private and never enter Public Verify.</p></div><a class=\"button\" href=\"request-analysis/\">Request technical analysis</a></section>"""
    return page("Technical Risk", "Auditable evidence for component lifecycle, migration and qualification decisions.", body, "../", "/technical-risk/")


def search_page(index: list[dict]) -> str:
    body = """
<section class=\"search-hero\"><p class=\"eyebrow\">Exact identity search</p><h1>Find a public technical record.</h1><p>Search by manufacturer, exact part number, family or item type. Punctuation is preserved.</p><form data-cml-search><label for=\"cml-query\">Manufacturer or part number</label><div><input id=\"cml-query\" name=\"q\" autocomplete=\"off\" placeholder=\"e.g. 095-725-134-006\"><button type=\"submit\">Search</button></div></form><div data-cml-results aria-live=\"polite\"></div></section>
<script src=\"../../assets/cml-search.js?v=20260916\"></script>"""
    return page("Technical record search", "Search StructEvidence CML public technical records by exact identity.", body, "../../", "/technical-risk/search/")


def method_page() -> str:
    body = """
<section class=\"method-hero\"><p class=\"eyebrow\">CML / Method pilot v0.1</p><h1>Evidence before equivalence.</h1><p>CML structures technical supply-chain decisions without converting uncertainty into unsupported compatibility claims.</p></section>
<section class=\"tr-section method-grid\"><article><span>01</span><h2>Identity</h2><p>Preserve manufacturer spelling and exact part-number punctuation. Similar strings are not silently merged.</p></article><article><span>02</span><h2>Event</h2><p>Record what changed with separate effective and knowledge clocks and an explicit event domain.</p></article><article><span>03</span><h2>Dependency</h2><p>Map the assembly, interface, process and customer scope that make migration consequential.</p></article><article><span>04</span><h2>Evidence</h2><p>Separate facts, inferences, engineering judgment, recommendations and unknowns.</p></article><article><span>05</span><h2>Alternative</h2><p>An identified candidate is not a qualified replacement. OEM status is modeled separately.</p></article><article><span>06</span><h2>Verification</h2><p>Compatibility is dimension-based and qualification is always bound to a defined scope.</p></article><article><span>07</span><h2>Decision</h2><p>Output defensible actions such as monitor, lifetime buy, qualify, redesign or insufficient evidence.</p></article></section>
<section class=\"tr-section law\"><p class=\"eyebrow\">Frozen laws</p><h2>What the method will not do</h2><div><p>Paper compatibility != qualified replacement</p><p>40 GHz connector != 40 GHz assembly qualification</p><p>Distributor inventory != manufacturer lifecycle</p><p>Hash integrity != source truth</p><p>Missing evidence != PASS</p><p>CML decisions != predictions</p></div></section>"""
    return page("CML method", "The CML evidence and decision method for technical lifecycle and migration records.", body, "../../", "/technical-risk/method/")


def request_page() -> str:
    body = """
<section class=\"request-hero\"><div><p class=\"eyebrow\">Request technical analysis</p><h1>Start with the exact item and decision context.</h1><p>We first confirm public evidence availability, private-data boundaries and the verification scope. Payment and delivery remain manually authorized.</p></div><aside><span>Access</span><strong>REQUEST ONLY</strong><span>Fulfillment</span><strong>MANUAL REVIEW</strong><span>Public client BOM</span><strong>PROHIBITED</strong></aside></section>
<section class=\"tr-section request-grid\"><div><h2>Include in your request</h2><ul><li>Manufacturer and exact part number</li><li>Lifecycle notice or technical concern</li><li>Assembly or application context</li><li>Decision deadline</li><li>Required verification or qualification scope</li></ul></div><div><h2>Contact</h2><p><strong>John Success / Structevidence.com</strong></p><p>Hong Kong</p><p><a href=\"https://wa.me/85266629951?text=Hello%20John%2C%20I%20would%20like%20to%20request%20a%20StructEvidence%20Technical%20Risk%20analysis.%20Manufacturer%20and%20part%20number%3A%20\">WhatsApp +852 6662 9951</a></p><p><a href=\"mailto:john.success1688@gmail.com?subject=StructEvidence%20Technical%20Risk%20request\">john.success1688@gmail.com</a></p><p class=\"note\">Research service only. No brokerage, procurement, custody, exchange or universal substitution warranty.</p></div></section>"""
    return page("Request technical analysis", "Request a scoped StructEvidence Technical Risk analysis.", body, "../../", "/technical-risk/request-analysis/")


def docs_text(records: list[dict]) -> dict[str, str]:
    architecture = f"""# CML StructEvidence Integration Assessment v0.1

## Architecture Decision

`ONE EVIDENCE CORE + SHARED STORAGE + DOMAIN-SPECIFIC TECHNICAL RISK MODULE`

### A. Reused primitives

RTP-style source/artifact lineage, append-only event semantics, dual clocks, corrections, directional supersession, RDL freshness states, GDR release authorization, Verify and hash-bound manifests.

### B. Domain data that does not fit structural-dynamics objects

Exact manufacturer identity, package/interface, lifecycle state, replacement relationships, compatibility cells, qualification scope and test requirements. These belong to a domain payload, not crypto/network research dimensions.

### C. Why a domain module is required

CML owns technical vocabularies and validation laws while the Evidence Core owns provenance, time, correction, supersession, release and integrity.

### D. Why no separate evidence database is required

Every CML record uses the same common record envelope and file-backed canonical storage conventions. A second provenance, event, freshness or Verify system would create conflicting truth histories.

### E. Shared schemas

`evidence/core/schema/evidence_core_record.schema.json` defines identifiers, source/artifact references, effective/known time, verification, correction, supersession, policy and hashes.

### F. CML-specific schemas

Technical Item, Event, Candidate, Compatibility, Test Requirement, Public Record, Release Manifest and Snipe Report.

### G. RDL Freshness reuse

RDL v0.1a states and precedence are reused. CML adds family-specific profiles; no global component age threshold exists. Where cadence is unsupported the result is `POLICY_NOT_CONFIGURED`.

### H. GDR-SE reuse

GDR remains the release/paid-delivery veto layer. CML v0.1 maps technical primary-source coverage, counter-evidence, unresolved qualification gaps, correction, supersession and freshness into a domain adapter. No paid/current authorization is self-awarded.

### I. Frozen semantics

LEVEL, DELTA, NO OBSERVATION, EVENT TIME, KNOWLEDGE TIME, CORRECTION and SUPERSESSION are unchanged. Existing digital-asset payloads and findings are untouched.

### J. Future client BOM migration

Private ingestion must normalize manufacturer + exact MPN without destructive merging, match the Technical Item registry, run lifecycle/dependency clustering, and publish only authorized derived metadata. Private BOM fields never enter Public Verify.

## Cross-domain future

The shared grammar is `Identity -> Event -> Dependency -> Evidence -> Alternative -> Verification -> Decision`. Future catalysts, specialty chemicals, APIs, optics, motors and bearings add domain profiles and typed fields, not new evidence cores or websites.
"""
    data_dictionary = """# CML Technical Risk Data Dictionary v0.1

| Field | Type | Required | Boundary | Meaning | Allowed values / source | Freshness | Supersession |
| --- | --- | --- | --- | --- | --- | --- | --- |
| record_id | string | yes | public | Permanent evidence record ID | Evidence Core | immutable | successor points backward |
| subject_id | string | yes | public | Permanent technical item ID | Evidence Core | immutable | never reused |
| manufacturer_part_number | string | yes | public | Exact maker spelling and punctuation | manufacturer | identity review | no silent merge |
| technical_item_type | enum | yes | public | Domain item category | schema enum | schema-versioned | retained |
| effective_at | UTC datetime | yes | public | When event/state applies | primary evidence | event-driven | retained |
| known_at | UTC datetime | yes | public | When evidence became known | retrieval/notice | no lookahead | retained |
| event_domain | enum | yes | public | Scope of state mutation | SUBJECT/EVIDENCE/RESEARCH/AUTHORIZATION | event-driven | scoped |
| lifecycle_state | enum | yes | public | Manufacturer lifecycle state | primary lifecycle evidence | event-driven | current successor |
| oem_replacement_status | enum | yes | public | Whether OEM lists replacement | OEM evidence | event-driven | current successor |
| dependency.context | text | yes | public-safe | Operational/engineering dependency | evidence + judgment | review on design change | versioned |
| compatibility_matrix | array | yes | public-safe | Dimension-level comparison | MATCH/DIFFERENCE/MISMATCH/UNKNOWN/TEST/N/A | test/revision driven | scope-bound |
| qualification_state | enum | yes | public-safe | Evidence-backed qualification stage | CML taxonomy | invalidated by scope/revision events | scope-bound |
| known_facts | array | yes | public | Typed supported claims | sources | source-family policy | corrected explicitly |
| unknowns | array | yes | public | Unresolved material questions | research review | re-evaluated | retained in history |
| candidates | array | yes | public-safe | Replacement paths | exact evidence | source/test driven | status history retained |
| decision.supported_paths | array | yes | public-safe | Defensible current actions | CML actions | evidence change | new release |
| customer_bom | object | no | private | Client component list | client | engagement policy | never public |
| client_usage/pricing/drawings | object | no | private | Customer operational context | client/NDA | engagement policy | never public |
| input_hash | SHA-256 | yes | public | Canonical source + payload commitment | generated | immutable | successor gets new hash |
| record_hash | SHA-256 | yes | public | Canonical record commitment | generated | immutable | successor gets new hash |
"""
    pre_audit = f"""# CML v0.1 Pre-Audit

| Check | Result |
| --- | --- |
| REPO_HEAD | `{BASE_SHA}` |
| REMOTE_MAIN | `{BASE_SHA}` |
| WORKTREE_CLEAN | YES at entry |
| PRODUCTION_DOMAIN | `structevidence.com` via Cloudflare Worker; canonical source site `structurevidence.org` |
| RDL_FRESHNESS_POLICY_VERSION | `RDL_FRESHNESS_v0.1a` |
| RDL_ENGINE_VERSION | `RDL_FRESHNESS_ENGINE_v0.1a` |
| EVENT_SCOPE_STATUS | PASS / event domain + target + as-of matching implemented |
| SUPERSESSION_STATUS | PASS / directional predecessor-successor relation implemented |
| GDR_G3_STATUS | PASS / runtime freshness lookup uses v0.1a |
| PAYMENT_READINESS | MANUAL_USDT_SETTLEMENT_ACTIVE / quote gated |
| PAID_PDF_READINESS | PDF product PASS; fulfillment MANUAL_ONLY |

`CML_IMPLEMENTATION = PERMITTED_WITH_LIMITATIONS`

The domain may be published as a Method Pilot and request-only service. It may not claim automated fulfillment, universal qualification or configured freshness where CML family cadence is unresolved.
"""
    return {
        "docs/architecture/CML_STRUCTEVIDENCE_INTEGRATION_ASSESSMENT_v0.1.md": architecture,
        "docs/architecture/CML_TECHNICAL_RISK_DATA_DICTIONARY_v0.1.md": data_dictionary,
        "docs/execution/CML_V0_1_PRE_AUDIT.md": pre_audit,
        "docs/execution/CML_ARCHITECTURE_AUDIT.md": "# CML Architecture Audit\n\nPASS: one Evidence Core; one file-backed canonical store; Technical Risk is a logical domain. Existing Structural Dynamics payloads and semantics were not modified.\n",
        "docs/execution/CML_DATA_MODEL_AUDIT.md": "# CML Data Model Audit\n\nPASS WITH LIMITATIONS: exact identity, dual clock, lifecycle, candidate, compatibility, qualification and decision structures are explicit. Future non-electronic types require schema versioning.\n",
        "docs/execution/CML_FRESHNESS_AUDIT.md": "# CML Freshness Audit\n\nPASS: no global threshold. Lifecycle is event-driven. Datasheet, availability, independent test and qualification families remain independently evaluated; unresolved cadence returns POLICY_NOT_CONFIGURED.\n",
        "docs/execution/CML_PUBLIC_PRIVATE_AUDIT.md": "# CML Public / Private Audit\n\nPASS: pilot records contain public manufacturer evidence only. Client BOM, usage, pricing, drawings, firmware, test raw data and commercial terms are prohibited from Public Verify.\n",
        "docs/execution/CML_FOUR_TARGET_RESEARCH_AUDIT.md": "# CML Four-Target Research Audit\n\nFour public evidence pilots are implemented. No pilot claims a qualified substitute. Amphenol connector and NXP records retain conflicting/weakening evidence; Murata preserves suffix specificity; RF40 distinguishes connector capability from assembly qualification.\n",
        "docs/execution/CML_UI_AUDIT.md": "# CML UI Audit\n\nTechnical Risk landing, exact-identity search, four record pages, method, request analysis and Verify pages are generated. The public view shows decision state first and hash lineage second.\n",
        "docs/architecture/CML_UNIFIED_SITE_ARCHITECTURE_v0.1a.md": "# CML Unified Site Architecture v0.1a\n\nStructEvidence operates one brand, repository, Evidence Core, record store, Verify surface and release-governance system. `structurevidence.org` is the canonical research and application domain. `structevidence.com` is the acquisition domain; its root uses `landing.html` while shared paths proxy the `.org` artifacts. Structural Intelligence and Technical Risk / CML are peer evidence domains, not separate products or truth systems.\n",
        "docs/execution/CML_V0_1A_MAIN_SITE_INTEGRATION_AUDIT.md": "# CML v0.1a Main-Site Integration Audit\n\nCML36-CML40 cover `.org` homepage discovery, cross-domain navigation, shared artifacts, canonical-domain policy and prevention of product/domain split. The checks are implemented in `scripts/test_cml_v01.py`; visual and responsive navigation checks are implemented in `scripts/qa_cml.cjs`.\n",
    }


def research_doc(pilot: dict) -> str:
    facts = "\n".join(f"- {x}" for x in pilot["known_facts"])
    unknowns = "\n".join(f"- {x}" for x in pilot["unknowns"])
    verification = "\n".join(f"- {x}" for x in pilot["verification"])
    sources = "\n".join(f"- [{source(x)['publisher']}: {x}]({source(x)['url']})" for x in pilot["source_ids"])
    return f"""# {pilot['pilot']} Research Record v0.1

## Research Question

What technical decision is currently defensible for `{pilot['manufacturer_part_number']}` under reviewed public evidence?

## Target

{pilot['manufacturer']} / `{pilot['manufacturer_part_number']}` / {pilot['product_family']}.

## Primary Evidence

{sources}

## Event Chronology

- Effective at: `{pilot['event']['effective_at']}`
- Known at: `{pilot['event']['known_at']}`
- Event: `{pilot['event']['event_type']}`
- {pilot['event']['detail']}

## Technical Requirements and Known Dependency

{pilot['dependency']}

## Known Facts

{facts}

## OEM Replacement and Alternative Paths

`{pilot['oem_replacement_status']}`. No candidate is represented as qualified. Supported management paths: {', '.join(pilot['decision_paths'])}.

## Compatibility and Verification

{verification}

## Counter-Evidence

{pilot['counter_evidence']}

## Unknowns

{unknowns}

## Recommended Action

{pilot['decision']}

## Freshness

`{pilot['freshness_state']}` under `{pilot['freshness_rule_type']}` because `{pilot['freshness_reason']}`, as evaluated `{AS_OF}`. No universal CML max-age rule is used.

## Limitations

Public-evidence pilot only. No client BOM, application envelope, samples, bench data, supplier qualification or universal-equivalence conclusion is present.
"""


def main() -> None:
    for path, value in schema_files().items():
        write_json(ROOT / path, value)
    write_json(ROOT / "technical-risk/config/cml_taxonomy.json", {"module_version": MODULE_VERSION, **CONFIG})
    write_json(ROOT / "technical-risk/config/evidence_families.json", {"module_version": MODULE_VERSION, "families": EVIDENCE_FAMILIES})
    write_json(ROOT / "technical-risk/config/product_contexts.json", {"module_version": MODULE_VERSION, "contexts": PRODUCT_CONTEXTS, "fact_invariance": "PRODUCT_CONTEXT_MUST_NOT_CHANGE_TECHNICAL_FACTS"})
    write_json(ROOT / "technical-risk/config/freshness_profiles.json", {"policy_version": "CML_FRESHNESS_PROFILE_v0.1", "global_threshold": None, "profiles": {"MANUFACTURER_LIFECYCLE_EVIDENCE": "EVENT_DRIVEN", "MANUFACTURER_DATASHEET": "REVISION_DRIVEN", "MANUFACTURER_PCN": "EVENT_DRIVEN", "CERTIFICATION_EVIDENCE": "REVISION_AND_EXPIRY_DRIVEN", "SUPPLY_AVAILABILITY_EVIDENCE": "POLICY_NOT_CONFIGURED", "INDEPENDENT_TEST_EVIDENCE": "SCOPE_AND_REVISION_DRIVEN", "CUSTOMER_QUALIFICATION_EVIDENCE": "SCOPE_AND_REVISION_DRIVEN"}})
    write_json(ROOT / "technical-risk/config/public_private_boundary.json", {"public": ["manufacturer", "manufacturer_part_number", "official_lifecycle_evidence", "pcn", "datasheet", "published_specifications", "public_certification", "public_oem_replacement", "general_verification_requirements", "public_technical_comparison", "evidence_lineage", "record_freshness"], "private": ["customer_bom", "customer_product", "annual_usage", "inventory", "customer_pricing", "supplier_quotation", "customer_drawings", "customer_firmware", "customer_qualification_limits", "nda_documents", "revenue_exposure", "internal_failure_data", "private_lab_raw_data", "commercial_negotiations"]})
    dictionary_markdown, dictionary_index = generate_data_dictionary()
    write_json(ROOT / "technical-risk/validation/CML_DATA_DICTIONARY_INDEX.json", dictionary_index)
    write_json(ROOT / "technical-risk/CML_SITE_ARCHITECTURE_v0.1a.json", {"version": SITE_INTEGRATION_VERSION, "brand": "StructEvidence", "canonical_research_domain": "structurevidence.org", "acquisition_domain": "structevidence.com", "acquisition_root_artifact": "landing.html", "shared_artifact_origin": "https://structurevidence.org", "evidence_core": CORE_VERSION, "domains": ["STRUCTURAL_INTELLIGENCE", "TECHNICAL_RISK"], "shared_systems": ["REPOSITORY", "EVIDENCE_CORE", "RECORD_STORE", "VERIFY", "RELEASE_GOVERNANCE"], "domain_split_prohibited": True})

    records = []
    index = []
    pilot_hashes = {}
    for pilot in PILOTS:
        folder = ROOT / "technical-risk/records" / pilot["slug"]
        sources = build_source_register(pilot)
        item = build_item(pilot)
        record = build_record(pilot, sources, item)
        records.append(record)
        event_ledger = {"ledger_id": f"{pilot['record_id']}.events", "append_only": True, "events": [record["cml"]["event"]]}
        candidate_register = {"registry_id": f"{pilot['record_id']}.candidates", "candidates": pilot["alternatives"], "empty_state_meaning": "NO_CANDIDATE_ESTABLISHED" if not pilot["alternatives"] else None}
        tests = [{"test_requirement_id": f"{pilot['record_id']}.TEST.{i:02d}", "original_item_id": pilot["technical_item_id"], "candidate_id": None, "test_category": "DOMAIN_SPECIFIC", "test_name": name, "standard": "UNRESOLVED", "test_method": "TO_BE_DEFINED_FOR_SCOPE", "acceptance_criteria": "UNRESOLVED", "required_equipment": "TO_BE_DEFINED_FOR_SCOPE", "third_party_lab_required": "UNRESOLVED", "customer_lab_required": "UNRESOLVED", "destructive": "UNRESOLVED", "sample_quantity": "UNRESOLVED", "evidence_basis": "PUBLIC_RECORD_REQUIREMENT", "status": "REQUIRED"} for i, name in enumerate(pilot["verification"], 1)]
        outputs = {
            "01_SOURCE_REGISTER.json": sources,
            "02_EVENT_LEDGER.json": event_ledger,
            "03_TECHNICAL_ITEM.json": item,
            "05_COMPATIBILITY_REQUIREMENTS.json": {"record_id": pilot["record_id"], "matrix": record["cml"]["verification"]["compatibility_matrix"], "test_requirements": tests},
            "06_CANDIDATE_REGISTER.json": candidate_register,
            "11_PUBLIC_RECORD.json": record,
        }
        for name, value in outputs.items():
            write_json(folder / name, value)
        write(folder / "04_LIFECYCLE_ASSESSMENT.md", f"# Lifecycle Assessment\n\nState: `{pilot['lifecycle_state']}`\n\n{pilot['event']['detail']}\n\nOEM replacement: `{pilot['oem_replacement_status']}`.\n")
        write(folder / "07_VERIFICATION_MATRIX.md", "# Verification Matrix\n\n" + "\n".join(f"- [ ] {x}" for x in pilot["verification"]))
        write(folder / "08_SOLUTION_PATHS.md", "# Solution Paths\n\n" + "\n".join(f"- `{x}`" for x in pilot["decision_paths"]) + f"\n\n{pilot['decision']}\n")
        write(folder / "09_COUNTER_EVIDENCE.md", f"# Counter-Evidence\n\n{pilot['counter_evidence']}\n")
        write(folder / "10_LIMITATIONS.md", "# Limitations\n\nPublic-evidence pilot only. No client BOM, pricing, inventory, drawings, application limits, laboratory raw data or qualification approval is included. A paper candidate is never a qualified replacement.\n")
        artifact_hashes = {path.name: file_digest(path) for path in sorted(folder.iterdir()) if path.is_file() and path.name != "12_RELEASE_MANIFEST.json"}
        release = {"record_id": pilot["record_id"], "record_hash": record["core"]["record_hash"], "artifact_hashes": artifact_hashes, "freshness_state": pilot["freshness_state"], "freshness_reason": pilot["freshness_reason"], "freshness_rule_type": pilot["freshness_rule_type"], "gdr_version": "GDR_SE_v0.1-R1.1+CML_DOMAIN_ADAPTER_v0.1a", "release_state": "PUBLIC_METHOD_PILOT", "authorization_state": "ALLOW_PUBLIC_WITH_LIMITATIONS", "paid_delivery_state": "BLOCK", "evaluation_as_of": AS_OF}
        write_json(folder / "12_RELEASE_MANIFEST.json", release)
        pilot_hashes[pilot["record_id"]] = record["core"]["record_hash"]
        index.append({"slug": pilot["slug"], "record_id": pilot["record_id"], "manufacturer": pilot["manufacturer"], "manufacturer_part_number": pilot["manufacturer_part_number"], "search_aliases": pilot["search_aliases"], "product_family": pilot["product_family"], "technical_item_type": pilot["technical_item_type"], "lifecycle_state": pilot["lifecycle_state"], "qualification_state": "LAB_VERIFICATION_REQUIRED", "record_hash": record["core"]["record_hash"], "href": f"../record/{pilot['slug']}/"})

    write_json(ROOT / "technical-risk/records/PUBLIC_RECORD_INDEX.json", {"module_version": MODULE_VERSION, "evaluation_as_of": AS_OF, "records": index})
    schema_hashes = {Path(path).name: file_digest(ROOT / path) for path in schema_files()}
    config_hashes = {path.name: file_digest(path) for path in sorted((ROOT / "technical-risk/config").glob("*.json"))}
    manifest = {"module_version": MODULE_VERSION, "protocol_version": PROTOCOL_VERSION, "site_integration_version": SITE_INTEGRATION_VERSION, "audit_policy_version": AUDIT_POLICY_VERSION, "evidence_core_version": CORE_VERSION, "schema_hashes": schema_hashes, "config_hashes": config_hashes, "pilot_record_ids": list(pilot_hashes), "pilot_record_hashes": pilot_hashes, "freshness_policy_version": "RDL_FRESHNESS_v0.1a+CML_FRESHNESS_PROFILE_v0.1", "gdr_version": "GDR_SE_v0.1-R1.1+CML_DOMAIN_ADAPTER_v0.1a", "build_commit": BUILD_COMMIT, "evaluation_as_of": AS_OF, "public_release_state": "METHOD_PILOT_ALLOW_WITH_LIMITATIONS"}
    write_json(ROOT / "technical-risk/TECHNICAL_RISK_MANIFEST.json", manifest)
    history = ROOT / "technical-risk/CML_VERSION_HISTORY.jsonl"
    if not history.exists():
        write(history, json.dumps({"module_version": MODULE_VERSION, "protocol_version": PROTOCOL_VERSION, "effective_at": AS_OF, "change": "Initial CML domain release", "base_commit": BASE_SHA}, sort_keys=True))
    closure_commit = os.environ.get("CML_CLOSURE_IMPLEMENTATION_COMMIT")
    if closure_commit:
        existing = [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not any(row.get("audit_policy_version") == AUDIT_POLICY_VERSION for row in existing):
            entry = {"effective_at": AS_OF, "base_commit": "ce1869fb5b04bb80bdad3451d1cf778c5ef557ca", "implementation_commit": closure_commit, "change_type": "AUDIT_HARDENING", "protocol_version": PROTOCOL_VERSION, "module_version": MODULE_VERSION, "site_integration_version": SITE_INTEGRATION_VERSION, "audit_policy_version": AUDIT_POLICY_VERSION, "summary": "Independent gate validators, canonical RDL freshness fields, hardened shared GDR adapter, schema-derived dictionary and metadata alignment; scientific findings unchanged.", "supersedes": "initial v0.1 audit behavior"}
            with history.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=True, sort_keys=True) + "\n")

    docs = docs_text(records)
    docs["docs/architecture/CML_TECHNICAL_RISK_DATA_DICTIONARY_v0.1.md"] = dictionary_markdown
    research_names = ["CML_PILOT_AMPHENOL_EOL_v0.1.md", "CML_PILOT_NXP_RF_POWER_EOL_v0.1.md", "CML_PILOT_MURATA_DCDC_v0.1.md", "CML_PILOT_RF40_ASSEMBLY_v0.1.md"]
    for name, pilot in zip(research_names, PILOTS):
        docs[f"docs/research/{name}"] = research_doc(pilot)
    for path, content in docs.items():
        write(ROOT / path, content)

    write(ROOT / "technical-risk/index.html", landing_page(records))
    write(ROOT / "technical-risk/search/index.html", search_page(index))
    write(ROOT / "technical-risk/method/index.html", method_page())
    write(ROOT / "technical-risk/request-analysis/index.html", request_page())
    for pilot, record in zip(PILOTS, records):
        write(ROOT / f"technical-risk/record/{pilot['slug']}/index.html", record_page(record, pilot["slug"]))
        verify = record["core"] | {"public_verify": True, "private_fields_included": False, "source_refs": [source(x) for x in pilot["source_ids"]]}
        source_refs_html = ", ".join(html.escape(source_id) for source_id in record["core"]["source_refs"])
        body = f"<section class=\"verify-hero\"><p class=\"eyebrow\">Public Verify / CML</p><h1>{html.escape(pilot['manufacturer_part_number'])}</h1><p>Recompute the canonical public record hash from the linked JSON and compare it with this release commitment.</p></section><section class=\"tr-section verify-grid\"><div><span>Record ID</span><code>{html.escape(record['core']['record_id'])}</code></div><div><span>Input SHA-256</span><code>{record['core']['input_hash']}</code></div><div><span>Record SHA-256</span><code>{record['core']['record_hash']}</code></div><div><span>Source refs</span><code>{source_refs_html}</code></div><div><span>Supersession</span><strong>{record['core']['supersession_status']}</strong></div><div><span>Public/private check</span><strong>NO PRIVATE CLIENT DATA</strong></div><div><a href=\"../../records/{pilot['slug']}/11_PUBLIC_RECORD.json\">Open canonical JSON</a></div><div><a href=\"../../records/{pilot['slug']}/12_RELEASE_MANIFEST.json\">Open release manifest</a></div></section>"
        write(ROOT / f"technical-risk/verify/{pilot['slug']}/index.html", page(f"Verify {pilot['manufacturer_part_number']}", "Verify a hash-bound CML public technical record.", body, "../../../", f"/technical-risk/verify/{pilot['slug']}/"))

    for relative in ["technical-risk", "evidence/core", "assets/technical-risk.css", "assets/cml-search.js"]:
        src = ROOT / relative
        dst = ROOT / "docs" / relative
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("research"))
        elif src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    print(f"CML_PUBLISH_PASS {len(records)} records")


if __name__ == "__main__":
    main()

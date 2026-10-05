#!/usr/bin/env python3
"""Stage 2 boundary tests for OIL-GENESIS-001 supplier selection."""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_DIR = ROOT / "data/open-intent-lab/genesis-001/providers"
SEARCH_RUN_PATH = (
    ROOT
    / "data/open-intent-lab/genesis-001/search-runs/stage-2-supplier-discovery.json"
)
SELECTION_DOC = (
    ROOT / "docs/open-intent-lab/genesis/OIL_GENESIS_001_SUPPLIER_SELECTION.md"
)
REPORT_PATH = ROOT / "docs/open-intent-lab/execution/STAGE_02_REPORT.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

EXPECTED_IDS = [f"OIL-CAND-{index:03d}" for index in range(1, 6)]
IDENTITY_STATES = {"IDENTITY_VERIFIED", "IDENTITY_PARTIAL", "IDENTITY_UNVERIFIED"}
MANUFACTURER_STATES = {
    "MANUFACTURER",
    "MANUFACTURER_AND_TRADER",
    "TRADER_DISTRIBUTOR",
    "UNKNOWN",
}
SIGNAL_STATES = {"PUBLIC_SIGNAL_PRESENT", "NO_PUBLIC_SIGNAL_LOCATED"}
RELATED_PARTY_STATES = {"RELATED_PARTY", "INDEPENDENT", "UNKNOWN"}
FORBIDDEN_OPERATIONAL_KEYS = {
    "provider_id",
    "demand_id",
    "capability_fact_id",
    "verified_capability_fact_id",
    "verified_capability_facts",
    "capability_facts",
    "demands",
    "ranking",
    "rank",
    "score",
    "commercial_score",
    "confidence",
    "confidence_score",
}
REQUIRED_FIELDS = {
    "provider_candidate_id",
    "entity_name",
    "trading_name",
    "country",
    "official_domain",
    "official_website",
    "manufacturer_status",
    "identity_status",
    "official_contact_channels",
    "public_signal_claim_ids",
    "public_evidence_refs",
    "public_signal_details",
    "evidence_accessibility",
    "contactability",
    "reason_for_genesis_selection",
    "known_gaps",
    "conflict_related_party_flag",
    "discovery_as_of",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk(value):
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class StageTwoSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = sorted(PROVIDERS_DIR.glob("candidate-*.json"))
        cls.candidates = [load_json(path) for path in cls.files]

    def test_exactly_five_selected_candidate_files(self):
        self.assertEqual(len(self.files), 5)
        self.assertEqual([path.name for path in self.files], [f"candidate-{i:03d}.json" for i in range(1, 6)])

    def test_candidate_ids_are_unique_and_deterministic(self):
        ids = [candidate["provider_candidate_id"] for candidate in self.candidates]
        self.assertEqual(ids, EXPECTED_IDS)
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_fields_identity_and_manufacturer_status(self):
        for candidate in self.candidates:
            self.assertEqual(set(candidate), REQUIRED_FIELDS)
            self.assertIn(candidate["identity_status"], IDENTITY_STATES)
            self.assertIn(candidate["manufacturer_status"], MANUFACTURER_STATES)
            self.assertEqual(candidate["manufacturer_status"], "MANUFACTURER")
            self.assertIn(candidate["conflict_related_party_flag"], RELATED_PARTY_STATES)
            self.assertRegex(candidate["discovery_as_of"], r"^\d{4}-\d{2}-\d{2}$")

    def test_official_domains_and_websites_have_valid_format(self):
        domain_pattern = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$")
        for candidate in self.candidates:
            self.assertRegex(candidate["official_domain"], domain_pattern)
            parsed = urlparse(candidate["official_website"])
            self.assertEqual(parsed.scheme, "https")
            self.assertTrue(parsed.netloc.endswith(candidate["official_domain"]))

    def test_every_candidate_has_an_attributable_official_contact_route(self):
        for candidate in self.candidates:
            self.assertTrue(candidate["official_contact_channels"])
            for route in candidate["official_contact_channels"]:
                self.assertTrue(route["type"].startswith("OFFICIAL_"))
                self.assertTrue(route["value"])
                source = urlparse(route["source"])
                self.assertEqual(source.scheme, "https")
                self.assertTrue(source.netloc)

    def test_public_signals_are_not_capability_statuses(self):
        for candidate in self.candidates:
            self.assertEqual(len(candidate["public_signal_details"]), 7)
            self.assertEqual(
                {row["claim_id"] for row in candidate["public_signal_details"]},
                {f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)},
            )
            self.assertLessEqual(
                {row["signal"] for row in candidate["public_signal_details"]},
                SIGNAL_STATES,
            )
            scalar_values = {item for item in walk(candidate) if isinstance(item, str)}
            self.assertNotIn("SUPPORTED", scalar_values)
            self.assertNotIn("OBSERVED", scalar_values)

    def test_no_production_provider_demand_ranking_or_confidence_fields(self):
        for candidate in self.candidates:
            keys = {item for item in walk(candidate) if isinstance(item, str)}
            self.assertFalse(keys & FORBIDDEN_OPERATIONAL_KEYS, keys & FORBIDDEN_OPERATIONAL_KEYS)

    def test_public_signal_count_matches_selection_report(self):
        signal_count = sum(
            row["signal"] == "PUBLIC_SIGNAL_PRESENT"
            for candidate in self.candidates
            for row in candidate["public_signal_details"]
        )
        self.assertEqual(signal_count, 30)

    def test_search_provenance_exists_and_is_bounded(self):
        search_run = load_json(SEARCH_RUN_PATH)
        self.assertEqual(search_run["selected_candidate_ids"], EXPECTED_IDS)
        self.assertEqual(len(search_run["candidate_entities_discovered"]), 11)
        self.assertEqual(len(search_run["entities_reviewed"]), 10)
        self.assertEqual(len(search_run["entities_rejected"]), 6)
        self.assertRegex(search_run["as_of"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertTrue(search_run["queries"])
        self.assertTrue(search_run["search_limits"])
        self.assertTrue(search_run["stop_reason"])

    def test_documents_and_public_case_boundary(self):
        selection = SELECTION_DOC.read_text(encoding="utf-8")
        report = REPORT_PATH.read_text(encoding="utf-8")
        for section in [
            "SELECTION_OBJECTIVE",
            "SEARCH_BOUNDARY",
            "DISCOVERY_SOURCES",
            "SELECTION_CRITERIA",
            "EXCLUSION_CRITERIA",
            "CANDIDATES_CONSIDERED",
            "SELECTED_FIVE",
            "EXCLUDED_CANDIDATES",
            "PUBLIC_EVIDENCE_SIGNAL_MATRIX",
            "CONTACTABILITY",
            "IDENTITY_RESULTS",
            "KNOWN_GAPS",
            "SELECTION_LIMITATIONS",
        ]:
            self.assertIn(f"## {section}", selection)
        self.assertIn("10/10 PASS", report)
        completed = subprocess.run(
            ["git", "diff", "--name-only", BASE_SHA, "--", "cases", "claims", "evidence", "docs/cases", "public"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Publication-boundary and protocol guards for the IREN tracker pilot."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from listed_project_tracker_iren_v01 import (  # noqa: E402
    TrackerProtocolError, validate_financial_attributes,
)

BASELINE = "305bbef43f2ccdef9d025ac802dfca6b6ad6a8df"
BOUNDARY_PATH = ROOT / "docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-PUBLICATION-BOUNDARY-v0.1.json"
BOUNDARY_DOC = ROOT / "docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-PUBLICATION-BOUNDARY-v0.1.md"
ORIGINAL_HASH_REPORT = ROOT / "docs/implementation/SE-LISTED-PROJECT-TRACKER-IREN-001-HASHES.json"
ORIGINAL_HASH_REPORT_SHA256 = "d17dabb851f357acd1adec3afb5c79966d9c61e1601dfbbd3cd164e3fcbc682d"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return {line for line in result.stdout.splitlines() if line and (ROOT / line).is_file()}


def simulated_pages_artifact(paths: set[str]) -> set[str]:
    """Model upload-pages-artifact@v3 default exclusions for path: ."""
    artifact: set[str] = set()
    for path in paths:
        parts = PurePosixPath(path).parts
        if path.startswith(".git/") or path.startswith(".github/"):
            continue
        if any(part.startswith(".") for part in parts):
            continue
        artifact.add(path)
    return artifact


class IrenPublicationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.boundary = load(BOUNDARY_PATH)
        cls.files = git_files()
        cls.artifact = simulated_pages_artifact(cls.files)
        cls.non_public = cls.boundary["non_public_historical_files"]

    def test_01_three_classifications_are_explicit_and_non_equivalent(self):
        definitions = self.boundary["classification_definitions"]
        self.assertEqual(set(definitions), {
            "PUBLIC_SAFE", "INTERNAL_DRAFT_NOT_APPROVED_FOR_PUBLICATION", "PRIVATE_RESTRICTED",
        })
        self.assertEqual(len(set(definitions.values())), 3)

    def test_02_repository_and_pages_exposure_are_separate_public_boundaries(self):
        self.assertEqual(self.boundary["repository_boundary"]["visibility"], "PUBLIC")
        pages = self.boundary["pages_boundary"]
        self.assertEqual(pages["source_branch"], "main")
        self.assertEqual(pages["artifact_path"], ".")
        self.assertEqual(pages["source_scope"], "REPOSITORY_ROOT")
        self.assertEqual(pages["non_hidden_tracked_file_effect"], "INCLUDED_IN_PAGES_ARTIFACT")

    def test_03_verified_pages_audit_records_exact_path_and_run(self):
        audit = (ROOT / self.boundary["pages_boundary"]["evidence_document"]).read_text(encoding="utf-8")
        for token in ("40198754542", "actions/upload-pages-artifact@v3", "path: .", "repository root"):
            self.assertIn(token, audit)

    def test_04_internal_path_robots_noindex_and_nojekyll_are_not_access_controls(self):
        pages = self.boundary["pages_boundary"]
        self.assertIn("DOES_NOT_CREATE_ACCESS_CONTROL", pages["nojekyll_effect"])
        self.assertIn("DOES_NOT_CREATE_ACCESS_CONTROL", pages["robots_or_noindex_effect"])
        text = BOUNDARY_DOC.read_text(encoding="utf-8").lower()
        for token in ("directory named `internal`", "robots.txt", "noindex", ".gitignore", ".nojekyll"):
            self.assertIn(token.lower(), text)

    def test_05_every_non_public_historical_file_is_classified_and_hashed(self):
        self.assertEqual(len(self.non_public), 11)
        self.assertEqual({item["classification"] for item in self.non_public}, {"INTERNAL_DRAFT_NOT_APPROVED_FOR_PUBLICATION"})
        for item in self.non_public:
            self.assertRegex(item["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(item["remediated_head_status"], "ABSENT")
            self.assertTrue(item["pages_url_if_present_on_main"].startswith("https://structurevidence.org/"))

    def test_06_non_public_payload_is_absent_from_current_public_repo_tree(self):
        for item in self.non_public:
            self.assertNotIn(item["path"], self.files, item["path"])
        self.assertFalse(any(path.startswith("research/internal/listed-projects/iren/") for path in self.files))

    def test_07_non_public_payload_is_absent_from_simulated_pages_artifact(self):
        for item in self.non_public:
            self.assertNotIn(item["path"], self.artifact, item["path"])
        self.assertFalse(any(path.startswith("research/internal/listed-projects/iren/") for path in self.artifact))

    def test_08_public_safe_files_are_present_and_would_be_in_root_artifact(self):
        for path in self.boundary["public_safe_head_files"]:
            self.assertIn(path, self.files, path)
            self.assertIn(path, self.artifact, path)

    def test_09_gitignore_is_not_treated_as_access_control(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertNotIn("research/internal/listed-projects/", ignore)
        self.assertEqual(self.boundary["public_safe_repo_only_files"], [])
        self.assertIn(".gitignore", self.files)
        self.assertNotIn(".gitignore", self.artifact)
        self.assertIn("not an authorization system", BOUNDARY_DOC.read_text(encoding="utf-8"))

    def test_10_public_commit_exposure_is_not_claimed_reversible(self):
        exposure = self.boundary["historical_exposure"]
        self.assertEqual(exposure["public_commit"], "51bdf7831fe0682c2e709074448cb7704f6a9e46")
        self.assertEqual(exposure["status"], "PUBLIC_REPOSITORY_EXPOSURE_OCCURRED")
        self.assertFalse(exposure["history_rewrite_performed"])
        self.assertIn("cannot make", exposure["reversibility"])

    def test_11_no_private_restricted_payload_is_declared_present(self):
        self.assertEqual(self.boundary["private_restricted_files"], [])
        self.assertIn("No PRIVATE_RESTRICTED", self.boundary["historical_exposure"]["content_sensitivity_review"])

    def test_12_restricted_storage_plan_has_real_authentication_controls(self):
        plan = self.boundary["restricted_storage_plan"]
        self.assertEqual(plan["status"], "PROPOSED_NOT_PROVISIONED")
        for token in ("private GitHub repository", "allowlist", "Pages disabled", "audit logging"):
            self.assertIn(token, plan["internal_draft_store"])
        for token in ("public access disabled", "encryption", "authenticated", "least-privilege", "access logs"):
            self.assertIn(token, plan["private_restricted_store"])

    def test_13_nine_sec_sources_remain_raw_capture_failed_with_null_byte_hash(self):
        raw = self.boundary["raw_capture_boundary"]
        self.assertEqual(raw["sec_source_count"], 9)
        self.assertEqual(raw["status"], "RAW_CAPTURE_FAILED")
        self.assertIsNone(raw["source_byte_sha256"])
        self.assertIn("No remote-source byte hash", raw["rule"])

    def test_14_original_v01_hash_receipt_is_byte_preserved(self):
        self.assertEqual(hashlib.sha256(ORIGINAL_HASH_REPORT.read_bytes()).hexdigest(), ORIGINAL_HASH_REPORT_SHA256)
        report = load(ORIGINAL_HASH_REPORT)
        self.assertEqual(report["source_raw_capture_failed_count"], 9)
        self.assertEqual(report["original_records_changed"], 0)
        self.assertFalse(report["case_state_changed"])

    def test_15_financial_protocol_still_separates_d4a_and_d4b(self):
        validate_financial_attributes({
            "source_dependency": "UNKNOWN",
            "liability_regime": "UNDETERMINED",
            "assurance": "UNKNOWN",
            "assurance_scope": "Publication-boundary test only",
            "disclosure_stages": ["D4a", "D4b"],
        })
        with self.assertRaises(TrackerProtocolError):
            validate_financial_attributes({
                "source_dependency": "UNKNOWN",
                "liability_regime": "UNDETERMINED",
                "assurance": "UNKNOWN",
                "assurance_scope": "Duplicate stage is invalid",
                "disclosure_stages": ["D4a", "D4a"],
            })

    def test_16_no_existing_case_evidence_claim_or_deploy_path_changed(self):
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{BASELINE}...HEAD"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        for path in result.stdout.splitlines():
            self.assertFalse(path.startswith(("cases/", "claims/", "evidence/", "deploy/")), path)

    def test_17_internal_draft_was_never_added_to_navigation_or_sitemaps(self):
        public = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in (
            "sitemap.xml", "docs/sitemap.xml", "cases/index.html", "index.html",
        ))
        self.assertNotIn("research/internal/listed-projects/iren", public)

    def test_18_no_production_action_is_authorized(self):
        self.assertEqual(self.boundary["production_actions"], {
            "merge": False, "pages_deploy": False, "public_pilot_start": False,
        })

    def test_19_manifest_urls_cover_every_removed_path_exactly(self):
        for item in self.non_public:
            expected = "https://structurevidence.org/" + item["path"]
            self.assertEqual(item["pages_url_if_present_on_main"], expected)

    def test_20_boundary_manifest_contains_no_secret_or_customer_value(self):
        text = BOUNDARY_PATH.read_text(encoding="utf-8").lower()
        for forbidden in ("api_key", "bearer_token", "customer_email", "customer_name"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IrenPublicationBoundaryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"IREN_PUBLICATION_BOUNDARY_GUARDS = {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f"TESTS_RUN = {result.testsRun}")
    raise SystemExit(0 if result.wasSuccessful() else 1)

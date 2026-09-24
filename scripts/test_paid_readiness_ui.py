from pathlib import Path
import hashlib
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ROUTES = [
    ROOT / "index.html",
    ROOT / "cases/index.html",
    ROOT / "cases/800vdc/index.html",
    ROOT / "cases/sodium-ion-bess/index.html",
    ROOT / "verify/index.html",
    ROOT / "decision-pack/index.html",
    ROOT / "context/index.html",
]

class PaidReadinessUITest(unittest.TestCase):
    def test_five_routes_render(self):
        for route in ROUTES:
            self.assertTrue(route.exists(), route)
            text = route.read_text()
            self.assertIn("<main", text)
            self.assertIn("product.css", text)

    def test_home_ctas(self):
        text = ROUTES[0].read_text()
        self.assertIn('href="https://structevidence.com/context/">Start with a decision', text)
        self.assertIn('href="/cases/">Explore live evidence cases', text)
        self.assertIn('href="/cases/sodium-ion-bess/">Inspect the commercialization state map', text)

    def test_approved_800v_state(self):
        freeze = json.loads((ROOT / "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/human-review-freeze.json").read_text())
        text = ROUTES[2].read_text()
        self.assertFalse(freeze["human_cml_decision"]["pdre_full_validation"])
        self.assertIn("PDRE full validation", text)
        self.assertRegex(text, r"PDRE full validation.*?NO")
        self.assertIn("OBSERVED — SINGLE INSTANCE", text)
        self.assertIn("Industry-scale adoption", text)
        self.assertIn("NOT ESTABLISHED", text)
        for label in ["Operating history", "Multi-entity replication", "Independent validation", "Repeat procurement", "Industry-scale adoption"]:
            self.assertIn(label, text)

    def test_counter_evidence_supported(self):
        text = ROUTES[2].read_text()
        self.assertIn("Counter-evidence", text)
        self.assertIn("Vertiv", text)
        self.assertIn("Siemens", text)

    def test_required_form_fields(self):
        verify = ROUTES[4].read_text()
        context = ROUTES[6].read_text()
        self.assertRegex(verify, r'name="claim_or_question" required')
        self.assertRegex(verify, r'name="decision_affected" required')
        self.assertRegex(context, r'name="decision" required')
        self.assertNotIn('type="file"', verify + context)

    def test_no_fabricated_commercial_or_truth_claims(self):
        rendered = "\n".join(path.read_text().lower() for path in ROUTES)
        prohibited = ["800v is proven", "800v is the future", "industry-wide deployment", "fully validated pdre", "guaranteed savings", "guaranteed roi", "verified 5% efficiency improvement", "testimonial", "customer logo"]
        for claim in prohibited:
            self.assertNotIn(claim, rendered)
        self.assertNotRegex(rendered, r"\$\s?\d")

    def test_sodium_ion_case_preserves_commercialization_boundary(self):
        text = ROUTES[3].read_text()
        snapshot = json.loads((ROOT / "cases/sodium-ion-bess/state-v0.1.json").read_text())
        self.assertEqual(snapshot["knowledge_cutoff"], "2026-09-24")
        self.assertEqual(snapshot["current_state"]["named_commissioned_site"], "NOT_ESTABLISHED")
        self.assertIn("A product announcement is not a delivery", text)
        self.assertIn("NAMED COMMISSIONED SITE: NOT ESTABLISHED", text)
        self.assertIn("state-v0.1.json", text)

    def test_canonical_files_are_not_ui_outputs(self):
        for path in ROUTES:
            self.assertFalse("technical-risk/cml-v1.1" in str(path))
            self.assertFalse("rdl/research" in str(path))

if __name__ == "__main__":
    unittest.main()

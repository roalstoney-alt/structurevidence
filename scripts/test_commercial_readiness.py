from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "deploy/cloudflare-landing/commercial-ui.js").read_text()


class CommercialReadinessTest(unittest.TestCase):
    def test_complete_public_service_routes(self):
        for route in ["/verify/", "/context/", "/decision-pack/", "/deliverables/", "/about/"]:
            self.assertIn(f'"{route}": page(', UI, route)

    def test_services_explain_fit_inputs_outputs_and_terms(self):
        for phrase in [
            "Good fit",
            "Inputs",
            "Deliverable",
            "Written scope",
            "Timing and review",
            "review rounds",
            "written quote",
            "Customer context is not copied into public verification",
        ]:
            self.assertIn(phrase, UI)

    def test_deliverable_outline_is_concrete(self):
        for phrase in [
            "Claim and decision boundary",
            "Evidence and counter-evidence register",
            "Outcome and unknowns",
            "Dependency and qualification map",
            "Action and evidence plan",
            "Corrections do not overwrite history",
        ]:
            self.assertIn(phrase, UI)

    def test_trust_copy_is_specific_without_fabricated_proof(self):
        for phrase in [
            "responsible researcher",
            "Contracting identity",
            "operating from Hong Kong",
            "support@structevidence.com",
            "do not authorize research or payment",
        ]:
            self.assertIn(phrase, UI)
        for prohibited in ["customer logo", "certified by", "guaranteed roi", "industry leader"]:
            self.assertNotIn(prohibited, UI.lower())
        self.assertIsNone(re.search(r"\$\s?\d", UI))

    def test_intake_and_research_boundaries_remain_unchanged(self):
        self.assertIn("fetch('/api/requests'", UI)
        self.assertIn("Submission does not authorize research", UI)
        self.assertIn("mailto:support@structevidence.com", UI)
        self.assertIn("https://structurevidence.org/cases/800vdc/", UI)


if __name__ == "__main__":
    unittest.main()

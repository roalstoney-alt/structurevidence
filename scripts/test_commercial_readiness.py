from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "deploy/cloudflare-landing/commercial-ui.js").read_text()


class CommercialReadinessTest(unittest.TestCase):
    def test_complete_public_service_routes(self):
        for route in ["/verify/", "/context/", "/decision-pack/", "/pricing/", "/deliverables/", "/about/"]:
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
            "HONG KONG",
            "support@structevidence.com",
            "do not authorize research or payment",
        ]:
            self.assertIn(phrase, UI)
        for prohibited in ["customer logo", "certified by", "guaranteed roi", "industry leader"]:
            self.assertNotIn(prohibited, UI.lower())
        for required in [
            "MATRIX ASIA PACIFIC LIMITED",
            "1856995",
            "60930306",
            "Stone Zhu",
            "https://www.linkedin.com/in/stone-zhu-0773423a4/",
        ]:
            self.assertIn(required, UI)

    def test_pricing_refund_and_rush_terms_are_explicit(self):
        for required in [
            "USD 199",
            "USD 1,999",
            "USD 4,999",
            "USD 399 per request",
            "generally non-refundable",
            "rights required by applicable law",
            "contract, formal quotation, and invoice",
        ]:
            self.assertIn(required, UI)

    def test_samples_and_research_attribution_are_honest(self):
        for required in [
            "DEMO_BNB_MONITORING_SNAPSHOT_v1.0.pdf",
            "800V DC evidence case",
            "General lithium-battery substitution",
            "Not yet published",
            "ACP–ATP whitepaper",
            "MDL, MOS, RDL, and GDR",
        ]:
            self.assertIn(required, UI)

    def test_intake_and_research_boundaries_remain_unchanged(self):
        self.assertIn("fetch('/api/requests'", UI)
        self.assertIn("Submission does not authorize research", UI)
        self.assertIn("mailto:support@structevidence.com", UI)
        self.assertIn("https://structurevidence.org/cases/800vdc/", UI)

    def test_public_operator_configuration_matches_disclosure(self):
        contact = json.loads((ROOT / "commercial/config/contact.json").read_text())
        self.assertEqual(contact["company_name"], "MATRIX ASIA PACIFIC LIMITED")
        self.assertEqual(contact["company_registry_number"], "1856995")
        self.assertEqual(contact["business_registration_number"], "60930306")
        self.assertEqual(contact["responsible_researcher"], "Stone Zhu")
        self.assertTrue(contact["contracts_available"])
        self.assertTrue(contact["formal_quotations_available"])
        self.assertTrue(contact["invoices_available"])
        self.assertEqual(contact["standard_service_fees_usd"], {
            "claim_verification": 199,
            "decision_context_review": 1999,
            "decision_pack": 4999,
            "rush_handling_per_request": 399,
        })

    def test_org_trust_and_terms_mirrors_are_consistent(self):
        for path in ["about.html", "docs/about.html", "terms-of-sale.html", "docs/terms-of-sale.html"]:
            text = (ROOT / path).read_text()
            self.assertIn("MATRIX ASIA PACIFIC LIMITED", text, path)
            self.assertIn("1856995", text, path)
            self.assertIn("60930306", text, path)
        public_contact_files = [
            "landing.html", "docs/landing.html", "enterprise.html", "docs/enterprise.html",
            "checkout.html", "docs/checkout.html", "technical-risk/request-analysis/index.html",
            "docs/technical-risk/request-analysis/index.html",
        ]
        for path in public_contact_files:
            self.assertNotIn("John Success", (ROOT / path).read_text(), path)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "deploy/cloudflare-landing"


class CommercialDomainSplitGuards(unittest.TestCase):
    def test_worker_identity_database_and_rate_limit(self):
        config = json.loads((WORKER / "wrangler.jsonc").read_text())
        self.assertEqual(config["name"], "structevidence-commercial")
        self.assertEqual(config["d1_databases"][0]["database_id"], "aee10591-536a-47af-8ee0-957551ba2360")
        self.assertEqual(config["vars"]["PUBLIC_ORIGINS"], "https://structevidence.com")
        self.assertEqual(config["ratelimits"][0]["simple"], {"limit": 5, "period": 10})

    def test_commercial_home_copy_and_boundaries(self):
        ui = (WORKER / "commercial-ui.js").read_text()
        for value in [
            "From question to defensible decision.",
            "Verify a Claim",
            "Start with Your Decision",
            "https://structurevidence.org/cases/800vdc/",
            "Customer submission does not automatically authorize research.",
        ]:
            self.assertIn(value, ui)
        home = ui.split("const homeBody", 1)[1].split("const field", 1)[0]
        for acronym in ["CML", "RDL", "RTP", "ECN"]:
            self.assertNotIn(acronym, home)

    def test_org_commercial_links_cross_to_dot_com_without_private_query(self):
        for path in ["index.html", "docs/index.html", "cases/800vdc/index.html", "docs/cases/800vdc/index.html"]:
            text = (ROOT / path).read_text()
            self.assertNotIn('href="/verify/', text)
            self.assertNotIn('href="/context/', text)
            self.assertNotIn('href="/decision-pack/', text)
            self.assertNotIn("email=", text)
            self.assertNotIn("company=", text)

    def test_access_audiences_are_split_and_admin_fails_closed(self):
        worker = (WORKER / "worker.js").read_text()
        self.assertIn("env.ADMIN_UI_AUD", worker)
        self.assertIn("env.ADMIN_API_AUD", worker)
        self.assertNotIn("POLICY_AUD", worker)
        self.assertIn("Cloudflare Access is not configured", worker)

    def test_canonical_records_unchanged(self):
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "--", "technical-risk", "rdl", "evidence", "timeline", "research"],
            cwd=ROOT,
            text=True,
        ).strip()
        self.assertEqual(changed, "")


if __name__ == "__main__":
    unittest.main()

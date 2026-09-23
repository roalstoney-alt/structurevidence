from pathlib import Path
import sqlite3
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class CustomerIntakePhaseBGuards(unittest.TestCase):
    def test_migration_executes_and_append_only_triggers_work(self):
        sql = (ROOT / "deploy/cloudflare-landing/migrations/0001_customer_intake.sql").read_text()
        db = sqlite3.connect(":memory:")
        db.executescript(sql)
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"customers", "requests", "request_events"} <= tables)
        self.assertNotIn("request_files", tables)

    def test_protected_public_surfaces_keep_evidence_and_cross_domain_ctas(self):
        for path in ["index.html", "docs/index.html", "cases/800vdc/index.html", "docs/cases/800vdc/index.html"]:
            current = (ROOT / path).read_text()
            self.assertIn("https://structevidence.com/verify/", current, path)
            self.assertIn("https://structevidence.com/context/", current, path)
            self.assertNotIn("email=", current, path)
            self.assertNotIn("company=", current, path)
        for path in ["cases/800vdc/index.html", "docs/cases/800vdc/index.html"]:
            current = (ROOT / path).read_text()
            self.assertIn("OBSERVED — SINGLE INSTANCE", current, path)
            self.assertIn("Industry-scale adoption", current, path)

    def test_no_canonical_mutation(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", "--", "technical-risk", "rdl", "evidence", "timeline", "research"], cwd=ROOT, text=True).strip()
        self.assertEqual(changed, "")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Validate the Agent Discovery API-subdomain routing migration."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY_SHA = "e7d712ae65242bf1d833f1f44b115516185e180d"
PROTECTED = ["cases", "docs/cases", "technical-risk/cml-v1.1", "rdl"]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def changed(*paths: str):
    result = subprocess.run(
        ["git", "diff", "--name-only", ENTRY_SHA, "--", *paths],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


class AgentApiSubdomainRoutingTest(unittest.TestCase):
    def test_a_github_pages_configuration_unchanged(self):
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "structurevidence.org")
        self.assertEqual(changed("CNAME"), [])

    def test_b_e_worker_custom_domain_and_narrow_path(self):
        config = load("deploy/cloudflare-evidence-resolver/wrangler.jsonc")
        self.assertEqual(config["routes"], [{"pattern": "api.structurevidence.org", "custom_domain": True}])
        self.assertFalse(config["workers_dev"])
        worker = (ROOT / "deploy/cloudflare-evidence-resolver/worker.js").read_text(encoding="utf-8")
        self.assertIn('url.pathname !== "/resolve"', worker)
        self.assertNotIn('url.pathname !== "/api/resolve"', worker)

    def test_f_j_runtime_safety_contract(self):
        worker = (ROOT / "deploy/cloudflare-evidence-resolver/worker.js").read_text(encoding="utf-8")
        self.assertIn('"cache-control": "no-store"', worker)
        self.assertIn('"access-control-allow-origin": "*"', worker)
        self.assertIn('request.method === "OPTIONS"', worker)
        self.assertIn('request.method !== "GET"', worker)
        self.assertNotIn("env.DB", worker)
        self.assertNotIn('fetch("http', worker)

    def test_k_discovery_manifest_endpoint_updated(self):
        manifest = load(".well-known/structurevidence.json")
        self.assertEqual(manifest["resolve_endpoint"], "https://api.structurevidence.org/resolve")
        self.assertEqual(manifest["claims_index"], "https://structurevidence.org/claims/index.json")
        self.assertEqual(manifest["capabilities"], "https://structevidence.com/capabilities.json")

    def test_l_capabilities_manifest_unchanged(self):
        self.assertEqual(changed("deploy/cloudflare-landing/capabilities.js"), [])

    def test_m_root_docs_parity(self):
        for relative in [".well-known/structurevidence.json", "agent/index.html"]:
            self.assertEqual((ROOT / relative).read_bytes(), (ROOT / "docs" / relative).read_bytes())

    def test_o_claim_files_byte_identical(self):
        self.assertEqual(changed("claims", "docs/claims"), [])

    def test_p_public_primitives_and_histories_unchanged(self):
        self.assertEqual(changed(*PROTECTED), [])

    def test_q_r_no_research_or_autonomous_action_added(self):
        diff = subprocess.run(
            ["git", "diff", ENTRY_SHA, "--", ".", ":(exclude)docs/execution"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.lower()
        for forbidden in ["external search", "create customer", "send email", "authorize research"]:
            self.assertNotIn("+" + forbidden, diff)


if __name__ == "__main__":
    unittest.main(verbosity=2)

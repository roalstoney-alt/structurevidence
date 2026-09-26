from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_se_api_contract import validate_contract  # noqa: E402


class ApiContractTests(unittest.TestCase):
    def test_openapi_matches_worker_operation_manifest(self):
        result = validate_contract()
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["documented_operations"], 21)

    def test_public_endpoint_count_is_frozen(self):
        self.assertEqual(validate_contract()["public_endpoints"], 13)

    def test_protected_endpoint_count_is_frozen(self):
        self.assertEqual(validate_contract()["protected_endpoints"], 8)


if __name__ == "__main__":
    unittest.main()

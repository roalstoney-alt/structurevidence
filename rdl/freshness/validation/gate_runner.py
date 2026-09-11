from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from rdl.freshness.validation.gate_registry import write_registry  # noqa: E402
from rdl.freshness.validation.reporter import write_report  # noqa: E402
from rdl.freshness.validation.validators import metadata, validate_configs, validate_outputs, validate_runtime_behaviors  # noqa: E402


REGISTRY = ROOT / "rdl" / "freshness" / "validation" / "RDL_FRESHNESS_GATE_RESULTS.json"
DOCS_REGISTRY = ROOT / "docs" / "rdl" / "freshness" / "validation" / "RDL_FRESHNESS_GATE_RESULTS.json"
REPORT = ROOT / "docs" / "execution" / "RDL_FRESHNESS_FINAL_EXECUTION_REPORT.md"


def run(test_commands: dict[str, int] | None = None, remote_expected: bool = False) -> dict:
    results = [*validate_configs(), *validate_runtime_behaviors(), *validate_outputs(test_commands, remote_expected)]
    registry = write_registry(REGISTRY, results, metadata())
    write_report(REGISTRY, REPORT)
    DOCS_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REGISTRY, DOCS_REGISTRY)
    return registry


if __name__ == "__main__":
    run()
    print("RDL_FRESHNESS_VALIDATION_PASS")

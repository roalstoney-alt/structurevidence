from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")

EXPECTED_ORIGINAL_HASHES = {
    "research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md": "fe7c8f696cf14c3f5b3b470bc21d116c304b78d7bf60f949f043bfd335b4da8b",
    "research/Strategy_2026_Structural_Dynamics_Report_v0.1_CN.md": "75dfb5cd4eab564bf4c3989662ede851ceac16a6ed34c85587366760566697f7",
    "research/Strategy_2026_Public_Evidence_Research_Report_v0.1_CN.md": "81f9c8810b7cabd86426f6fc115f62ee20cc953494259a878c7a4a1f5c044fc0",
}

EN_REPORTS = [
    "research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_EN.md",
    "research/Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md",
    "research/Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
]

PUBLIC_ENTRY_FILES = [
    "index.html",
    "research.html",
    "strategy-2026.html",
    "standard.html",
    "architecture.html",
    "method.html",
    "whitepapers.html",
    "verify.html",
    "verify-r1.html",
    "reports.html",
    "sample-report.html",
    "enterprise.html",
    "paid-pilot.html",
    "customize.html",
    "checkout.html",
    "terms.html",
    "privacy.html",
    "terms-of-sale.html",
    "refund-policy.html",
    "research-scope.html",
    "README.md",
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def fail(message: str) -> None:
    raise SystemExit(f"ENGLISH_PUBLIC_SURFACE_FAIL: {message}")


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def file_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    links = markdown_links(text)
    if path.suffix == ".html":
        parser = LinkParser()
        parser.feed(text)
        links.extend(parser.links)
    return links


def resolve_link(source: Path, link: str) -> str | None:
    link = link.split("#", 1)[0].split("?", 1)[0]
    if not link or link.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = (source.parent / link).resolve()
    try:
        return target.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None


def linked_public_paths() -> set[str]:
    queue = [ROOT / rel for rel in PUBLIC_ENTRY_FILES if (ROOT / rel).exists()]
    seen: set[str] = set()
    while queue:
        path = queue.pop(0)
        rel = path.relative_to(ROOT).as_posix()
        if rel in seen or not path.exists() or path.is_dir():
            continue
        seen.add(rel)
        if path.suffix not in {".html", ".md", ".json", ".js"}:
            continue
        for link in file_links(path):
            target_rel = resolve_link(path, link)
            if target_rel and (ROOT / target_rel).exists() and target_rel not in seen:
                if target_rel.startswith(("evidence-freeze/", "docs/evidence-freeze/")):
                    continue
                queue.append(ROOT / target_rel)
    return seen


def check_no_public_cn_links(paths: set[str]) -> None:
    for rel in paths:
        if (ROOT / rel).suffix not in {".html", ".md", ".json", ".js", ".css", ".txt"}:
            continue
        text = read(rel)
        link_targets = []
        link_targets.extend(markdown_links(text))
        if (ROOT / rel).suffix == ".html":
            parser = LinkParser()
            parser.feed(text)
            link_targets.extend(parser.links)
        if any("_CN.md" in target for target in link_targets):
            fail(f"public link to CN report remains in {rel}")


def check_linked_surface_no_cjk(paths: set[str]) -> None:
    allowed = {
        "docs/execution/ENGLISH_PUBLIC_SURFACE_EXCEPTIONS.json",
    }
    for rel in paths:
        if rel in allowed:
            continue
        if (ROOT / rel).suffix not in {".html", ".md", ".json", ".js", ".css", ".txt"}:
            continue
        text = read(rel)
        if CJK.search(text):
            fail(f"CJK text in linked public surface: {rel}")


def check_required_reports() -> None:
    for rel in EN_REPORTS:
        path = ROOT / rel
        docs_path = ROOT / "docs" / rel
        dated_path = ROOT / "research" / "2026-09-08" / path.name
        if not path.exists() or not docs_path.exists() or not dated_path.exists():
            fail(f"missing English report mirror for {rel}")
        text = path.read_text(encoding="utf-8")
        if CJK.search(text):
            fail(f"English report contains CJK: {rel}")
        for phrase in [
            "Translation Status: Canonical English Translation",
            "Scientific Recalculation: No",
            "Scientific Conclusion Change: No",
            "Original SHA-256",
        ]:
            if phrase not in text:
                fail(f"translation provenance missing {phrase} in {rel}")
    combined = "\n".join(read(rel) for rel in EN_REPORTS)
    for token in [
        "ECL.COMPANY.STRATEGY_INC.2026.001",
        "HYBRID_ACCUMULATION_MONETIZATION",
        "SEMANTIC_TENSION_BUT_RECONCILABLE",
        "PARTIAL",
        "NO",
        "1,363",
        "$80.8M",
        "2,225",
        "$135.2M",
        "843,775 BTC",
        "$1.06B",
        "$546.0M",
        "INSUFFICIENT_DATA",
    ]:
        if token not in combined:
            fail(f"material token missing from English reports: {token}")


def check_json_and_js() -> None:
    for rel in ["assets/entities.json", "docs/assets/entities.json"]:
        data = json.loads(read(rel))
        text = json.dumps(data, ensure_ascii=False)
        if CJK.search(text):
            fail(f"CJK in public entity JSON {rel}")
        if "_CN.md" in text:
            fail(f"CN report link in {rel}")
    for rel in ["assets/site.js", "docs/assets/site.js"]:
        if CJK.search(read(rel)):
            fail(f"CJK in rendered JS strings {rel}")


def check_root_docs_sync() -> None:
    for rel in [
        "index.html",
        "research.html",
        "strategy-2026.html",
        "reports.html",
        "sample-report.html",
        "enterprise.html",
        "customize.html",
        "checkout.html",
        "paid-pilot.html",
        "terms.html",
        "privacy.html",
        "terms-of-sale.html",
        "refund-policy.html",
        "research-scope.html",
    ]:
        if read(rel) != read(f"docs/{rel}"):
            fail(f"root/docs mismatch: {rel}")
    for rel in EN_REPORTS:
        if read(rel) != read(f"docs/{rel}"):
            fail(f"root/docs report mismatch: {rel}")


def check_original_hashes() -> None:
    for rel, expected in EXPECTED_ORIGINAL_HASHES.items():
        if sha256(rel) != expected:
            fail(f"frozen original hash changed: {rel}")


def check_manifests_and_audits() -> None:
    manifest = json.loads(read("research/PUBLICATION_PACKAGE_MANIFEST_EN.json"))
    if set(manifest) != {Path(rel).name for rel in EN_REPORTS}:
        fail("English publication manifest does not contain expected reports")
    for entry in manifest.values():
        if entry.get("scientific_content_changed") is not False:
            fail("English manifest must mark scientific_content_changed=false")
    for rel in [
        "docs/execution/PRE_MIGRATION_LANGUAGE_INVENTORY.md",
        "docs/execution/ENGLISH_TERMINOLOGY_REGISTRY.md",
        "docs/execution/ENGLISH_TRANSLATION_EQUIVALENCE_AUDIT.md",
        "docs/execution/POST_MIGRATION_LANGUAGE_AUDIT.md",
        "docs/execution/ENGLISH_PUBLIC_SURFACE_LINK_AUDIT.md",
        "docs/execution/ENGLISH_PUBLIC_SURFACE_MANIFEST.json",
        "docs/execution/ENGLISH_PUBLIC_SURFACE_EXCEPTIONS.json",
        "docs/execution/ENGLISH_ONLY_PUBLIC_SURFACE_EXECUTION_REPORT.md",
    ]:
        if not (ROOT / rel).exists():
            fail(f"missing audit artifact {rel}")


def main() -> None:
    paths = linked_public_paths()
    check_no_public_cn_links(paths)
    check_linked_surface_no_cjk(paths)
    check_required_reports()
    check_json_and_js()
    check_root_docs_sync()
    check_original_hashes()
    check_manifests_and_audits()
    print("ENGLISH_PUBLIC_SURFACE_PASS")


if __name__ == "__main__":
    main()

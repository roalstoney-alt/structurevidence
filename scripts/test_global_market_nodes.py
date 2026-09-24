import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = {
    "en": ROOT / "locales" / "en.json",
    "zh-CN": ROOT / "locales" / "zh-CN.json",
    "es": ROOT / "locales" / "es.json",
}
PAGES = {
    "en": ROOT / "en" / "index.html",
    "zh-CN": ROOT / "zh-cn" / "index.html",
    "es": ROOT / "es" / "index.html",
}
DOC_PAGES = {
    "en": ROOT / "docs" / "en" / "index.html",
    "zh-CN": ROOT / "docs" / "zh-cn" / "index.html",
    "es": ROOT / "docs" / "es" / "index.html",
}

def test_locale_packs_parse_and_preserve_machine_language():
    for locale, path in LOCALES.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["locale"] == locale
        assert data["invariants"]["canonical_machine_states_language"] == "en"
        assert data["invariants"]["localized_copy_must_not_change_evidence_state"] is True

def test_homepages_have_reciprocal_hreflang():
    expected = [
        'hreflang="x-default"',
        'hreflang="en"',
        'hreflang="zh-CN"',
        'hreflang="es"',
    ]
    for path in [ROOT / "index.html", *PAGES.values()]:
        html = path.read_text(encoding="utf-8")
        for token in expected:
            assert token in html

def test_homepages_have_correct_lang():
    expected = {"en": 'lang="en"', "zh-CN": 'lang="zh-CN"', "es": 'lang="es"'}
    for locale, path in PAGES.items():
        html = path.read_text(encoding="utf-8")
        assert expected[locale] in html

def test_docs_mirror_matches():
    for locale in PAGES:
        assert PAGES[locale].read_text(encoding="utf-8") == DOC_PAGES[locale].read_text(encoding="utf-8")

def test_market_nodes_are_not_identical_translations():
    texts = [PAGES[k].read_text(encoding="utf-8") for k in PAGES]
    assert len(set(texts)) == 3
    assert "Structural Openings" in texts[0]
    assert "结构性窗口" in texts[1]
    assert "Ventana estructural" in texts[2]

def test_root_is_global_gateway():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "/en/" in html and "/zh-cn/" in html and "/es/" in html
    assert "One evidence core" in html

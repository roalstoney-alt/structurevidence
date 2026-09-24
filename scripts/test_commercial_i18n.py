from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy" / "cloudflare-landing"
UPGRADE = (DEPLOY / "commercial-upgrade.js").read_text(encoding="utf-8")
UI = (DEPLOY / "commercial-ui.js").read_text(encoding="utf-8")

def test_language_switch_present():
    for token in ['href="/en/"', 'href="/zh-cn/"', 'href="/es/"']:
        assert token in UI

def test_commercial_locale_routes_present():
    for route in ['"/en/"', '"/zh-cn/"', '"/es/"']:
        assert route in UPGRADE

def test_prices_are_identical_across_language_packs():
    packs = {}
    for locale in ["en", "zh-CN", "es"]:
        packs[locale] = json.loads((DEPLOY / "locales" / f"{locale}.json").read_text(encoding="utf-8"))
    baseline = packs["en"]["product_prices"]
    assert packs["zh-CN"]["product_prices"] == baseline
    assert packs["es"]["product_prices"] == baseline
    assert baseline == {
        "claim_verification_usd": 199,
        "decision_context_review_usd": 1999,
        "decision_pack_usd": 4999,
        "rush_handling_usd": 399,
    }

def test_existing_core_routes_are_preserved():
    for route in ['"/verify/"', '"/context/"', '"/decision-pack/"', '"/pricing/"']:
        assert route in UPGRADE

def test_localized_homepages_link_to_same_workflows():
    assert '/verify/?lang=zh-CN' in UPGRADE
    assert '/context/?lang=zh-CN' in UPGRADE
    assert '/verify/?lang=es' in UPGRADE
    assert '/context/?lang=es' in UPGRADE

def test_no_payment_or_api_boundary_change():
    worker = (DEPLOY / "worker.js").read_text(encoding="utf-8")
    assert '"/api/requests"' in worker
    assert 'COMMERCIAL_PAGES[path]' in worker

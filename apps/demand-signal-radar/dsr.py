#!/usr/bin/env python3
"""DSR_v0.1: public decision-signal qualification with no external action."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

OBJECT_TERMS = ("eol", "obsolete", "discontinued", "nrnd", "last time buy", "supplier migration", "dc/dc", "rf power", "motor controller", "plc", "legacy component", "800vdc", "sst", "replacement component")
PAIN_TERMS = ("can't source", "cannot source", "looking for replacement", "alternative to", "supplier discontinued", "lead time", "too expensive", "redesign required", "compatibility issue", "qualification issue", "second source", "supply shortage", "field failure")
ACTION_TERMS = ("anyone tested", "has anyone replaced", "looking for supplier", "need alternative", "requesting recommendation", "planning migration", "considering redesign", "rfq", "sample", "qualification", "production", "deployment", "second source")
REVIEW_ACTIONS = {"APPROVE_PUBLIC_REPLY": "PUBLIC_REPLY", "APPROVE_FOLLOW": "FOLLOW", "APPROVE_DM": "MANUAL_DM", "WATCH": "WATCH", "SKIP": "SKIP"}
CONTACT_STATUSES = ("NOT_REVIEWED", "APPROVED_FOR_CONTACT", "CONTACTED", "RESPONDED", "NO_RESPONSE", "DECLINED", "JOINED_RESEARCH_ROOM", "REQUEST_SUBMITTED", "CLOSED")
ACQUISITION_EVENTS = ("DEMAND_SIGNAL_DETECTED", "DEMAND_SIGNAL_QUALIFIED", "HUMAN_CONTACT_APPROVED", "HUMAN_CONTACT_SENT", "HUMAN_RESPONSE_RECEIVED", "STATE_LINK_OPENED", "RESEARCH_ROOM_JOINED", "REQUEST_SUBMITTED", "PAYMENT_INTENT_CONFIRMED", "MANUAL_COMMERCIAL_PILOT")

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def clean(value: Any, limit: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"[\x00-\x1f\x7f]", "", str(value)).strip()
    return text[:limit] or None

def terms(text: str, vocabulary: Iterable[str]) -> list[str]:
    lowered = text.casefold()
    return sorted({term for term in vocabulary if term in lowered})

def score_class(score: int) -> str:
    if score <= 3: return "IGNORE"
    if score <= 5: return "WATCH"
    if score <= 7: return "QUALIFIED"
    return "HIGH_VALUE"

def signal_id(platform: str, url: str, observed_at: str) -> str:
    digest = hashlib.sha256(f"{platform}\0{url}".encode()).hexdigest()[:12].upper()
    return f"SE-DSR-{observed_at[:10].replace('-', '')}-{digest}"

def semantic_key(signal: dict[str, Any]) -> str:
    words = re.findall(r"[a-z0-9]+", " ".join([signal.get("decision_context", ""), *signal.get("object_detected", [])]).casefold())
    material = " ".join(sorted(set(words))[:40])
    return hashlib.sha256(f"{signal['platform']}|{signal.get('author_public_id')}|{signal.get('mapped_subject_id')}|{material}|{signal['observed_at'][:10]}".encode()).hexdigest()

def classify(raw: dict[str, Any], subjects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    allowed = {"platform", "source_url", "observed_at", "author_public_id", "author_public_name", "organization_public_name", "text", "contact_route"}
    if set(raw) - allowed:
        raise ValueError("unexpected or private source field")
    url = clean(raw.get("source_url"), 2000)
    if not url or not url.startswith("https://"):
        raise ValueError("public HTTPS source_url required")
    text = clean(raw.get("text"), 8000)
    if not text:
        raise ValueError("public business-relevant text required")
    observed = clean(raw.get("observed_at"), 40) or utcnow()
    objects, pains, actions = terms(text, OBJECT_TERMS), terms(text, PAIN_TERMS), terms(text, ACTION_TERMS)
    mapped_subject, mapped_state = map_state(text, subjects or [])
    real_problem = 3 if pains and re.search(r"\b(i|we|our|my|need|cannot|can't)\b", text, re.I) else 2 if pains else 1 if objects else 0
    action_intent = 2 if actions else 1 if re.search(r"consider|plan|evaluate", text, re.I) else 0
    specificity = 2 if mapped_subject or re.search(r"\b[A-Z0-9][A-Z0-9-]{4,}\b", text) else 1 if objects else 0
    fit = 2 if objects and pains and actions else 1 if len([objects, pains, actions]) >= 2 else 0
    contact = 1 if raw.get("contact_route") in {"PUBLIC_REPLY", "FOLLOW", "MANUAL_DM"} else 0
    components = {"real_problem": real_problem, "action_intent": action_intent, "specificity": specificity, "structurevidence_fit": fit, "contactability": contact}
    total = sum(components.values())
    recommended = raw.get("contact_route") if total >= 6 and contact else "WATCH" if total >= 4 else "SKIP"
    return {
        "schema_version": "DSR_v0.1", "signal_id": signal_id(raw["platform"], url, observed), "observed_at": observed,
        "platform": clean(raw["platform"], 40), "source_url": url, "author_public_id": clean(raw.get("author_public_id"), 300),
        "author_public_name": clean(raw.get("author_public_name"), 300), "organization_public_name": clean(raw.get("organization_public_name"), 300),
        "signal_text_excerpt": text[:1000], "object_detected": objects, "pain_detected": pains, "action_detected": actions,
        "decision_context": text[:2000], "mapped_subject_id": mapped_subject.get("subject_id") if mapped_subject else None,
        "mapped_state_id": mapped_state.get("state_id") if mapped_state else None, "score_components": components,
        "real_decision_score": total, "score_class": score_class(total), "contactability": raw.get("contact_route") if contact else "SKIP",
        "recommended_action": recommended, "contact_status": "NOT_REVIEWED", "response_status": None, "request_id": None,
        "privacy_classification": "INTERNAL_ACQUISITION_SIGNAL", "created_at": utcnow(),
    }

def map_state(text: str, subjects: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    lowered = text.casefold()
    ranked = []
    for item in subjects:
        tokens = [item.get("canonical_name", ""), *item.get("aliases", []), *item.get("tags", [])]
        hits = sum(1 for token in tokens if len(token) >= 3 and token.casefold() in lowered)
        if hits: ranked.append((hits, item))
    if not ranked: return None, None
    subject = max(ranked, key=lambda pair: pair[0])[1]
    return subject, subject.get("current_state")

class RadarStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS signals(signal_id TEXT PRIMARY KEY, source_url TEXT UNIQUE, semantic_key TEXT UNIQUE, score INTEGER, score_class TEXT, contact_status TEXT, observed_at TEXT, payload_json TEXT);
        CREATE TABLE IF NOT EXISTS contact_events(event_id TEXT PRIMARY KEY, signal_id TEXT, event_type TEXT, event_at TEXT, actor TEXT, acquisition_source TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS commercial_scopes(scope_id TEXT PRIMARY KEY, request_id TEXT, status TEXT, research_scope TEXT, quoted_amount TEXT, currency TEXT, payment_status TEXT, manual_invoice_reference TEXT, provider_adapter TEXT CHECK(provider_adapter='DISABLED'), created_at TEXT, updated_at TEXT);
        """)
    def ingest(self, signal: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        existing = self.db.execute("SELECT payload_json FROM signals WHERE source_url=? OR semantic_key=?", (signal["source_url"], semantic_key(signal))).fetchone()
        if existing: return json.loads(existing[0]), True
        self.db.execute("INSERT INTO signals VALUES(?,?,?,?,?,?,?,?)", (signal["signal_id"], signal["source_url"], semantic_key(signal), signal["real_decision_score"], signal["score_class"], signal["contact_status"], signal["observed_at"], json.dumps(signal, sort_keys=True)))
        self.event(signal["signal_id"], "DEMAND_SIGNAL_DETECTED", "DSR", "DIRECT")
        if signal["score_class"] in {"QUALIFIED", "HIGH_VALUE"}: self.event(signal["signal_id"], "DEMAND_SIGNAL_QUALIFIED", "DSR", "DIRECT")
        self.db.commit(); return signal, False
    def queue(self) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT payload_json FROM signals WHERE score_class IN ('QUALIFIED','HIGH_VALUE') AND contact_status='NOT_REVIEWED' ORDER BY score DESC, observed_at ASC").fetchall()
        return [candidate_card(json.loads(row[0])) for row in rows]
    def review(self, signal_id_: str, action: str, actor: str) -> dict[str, Any]:
        if action not in REVIEW_ACTIONS: raise ValueError("invalid review action")
        row = self.db.execute("SELECT payload_json FROM signals WHERE signal_id=?", (signal_id_,)).fetchone()
        if not row: raise KeyError(signal_id_)
        signal = json.loads(row[0]); signal["recommended_action"] = REVIEW_ACTIONS[action]
        signal["contact_status"] = "APPROVED_FOR_CONTACT" if action.startswith("APPROVE_") else "CLOSED" if action == "SKIP" else "NOT_REVIEWED"
        self.db.execute("UPDATE signals SET contact_status=?, payload_json=? WHERE signal_id=?", (signal["contact_status"], json.dumps(signal, sort_keys=True), signal_id_))
        if action.startswith("APPROVE_"): self.event(signal_id_, "HUMAN_CONTACT_APPROVED", actor, "DIRECT")
        self.db.commit(); return signal
    def event(self, signal_id_: str, event_type: str, actor: str, acquisition_source: str, notes: str | None = None) -> str:
        if event_type not in ACQUISITION_EVENTS: raise ValueError("invalid event")
        at = utcnow(); digest = hashlib.sha256(f"{signal_id_}|{event_type}|{at}".encode()).hexdigest()[:12].upper(); event_id = f"SE-DCE-{at[:10].replace('-', '')}-{digest}"
        self.db.execute("INSERT INTO contact_events VALUES(?,?,?,?,?,?,?)", (event_id, signal_id_, event_type, at, actor, acquisition_source, clean(notes, 2000)))
        return event_id
    def daily(self, day: str) -> dict[str, int | str]:
        rows = [json.loads(row[0]) for row in self.db.execute("SELECT payload_json FROM signals WHERE observed_at LIKE ?", (f"{day}%",))]
        return {"date": day, "sources_scanned": len({row["platform"] for row in rows}), "public_signals_scanned": len(rows), "qualified_signals": sum(row["score_class"] == "QUALIFIED" for row in rows), "high_value_signals": sum(row["score_class"] == "HIGH_VALUE" for row in rows), "matched_existing_subject": sum(bool(row["mapped_subject_id"]) for row in rows), "unmapped_high_value": sum(row["score_class"] == "HIGH_VALUE" and not row["mapped_subject_id"] for row in rows), "human_review_required": sum(row["score_class"] in {"QUALIFIED", "HIGH_VALUE"} for row in rows), "public_reply_recommended": sum(row["recommended_action"] == "PUBLIC_REPLY" for row in rows), "follow_recommended": sum(row["recommended_action"] == "FOLLOW" for row in rows), "manual_dm_recommended": sum(row["recommended_action"] == "MANUAL_DM" for row in rows)}
    def prepare_scope(self, request_id: str, scope: str, amount: str | None = None, currency: str | None = None) -> dict[str, Any]:
        now = utcnow(); scope_id = "SE-SCOPE-" + hashlib.sha256(request_id.encode()).hexdigest()[:16].upper()
        record = {"scope_id": scope_id, "request_id": request_id, "status": "RESEARCH_SCOPED", "research_scope": clean(scope, 8000), "quoted_amount": clean(amount, 40), "currency": clean(currency, 8), "payment_status": "NOT_REQUESTED", "manual_invoice_reference": None, "provider_adapter": "DISABLED", "created_at": now, "updated_at": now}
        self.db.execute("INSERT OR REPLACE INTO commercial_scopes VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(record.values())); self.db.commit(); return record

def candidate_card(signal: dict[str, Any]) -> dict[str, Any]:
    return {"signal_id": signal["signal_id"], "platform": signal["platform"], "source_url": signal["source_url"], "observed_at": signal["observed_at"], "public_author": signal["author_public_name"] or signal["author_public_id"], "object": signal["object_detected"], "real_decision": signal["decision_context"], "pain": signal["pain_detected"], "action": signal["action_detected"], "real_decision_score": signal["real_decision_score"], "score_components": signal["score_components"], "matched_structurevidence_subject": signal["mapped_subject_id"], "matched_current_state": signal["mapped_state_id"], "why_structurevidence_may_help": "A timestamped State and Evidence boundary may separate available claims from decision-ready support.", "recommended_entry_asset": f"/states/{signal['mapped_subject_id']}" if signal["mapped_subject_id"] else "/states", "recommended_human_action": signal["recommended_action"], "contact_status": signal["contact_status"], "draft_public_reply": draft_response(signal, private=False), "draft_manual_dm": draft_response(signal, private=True)}

def draft_response(signal: dict[str, Any], private: bool = False) -> str:
    state = f"the recorded State {signal['mapped_state_id']}" if signal.get("mapped_state_id") else "the current public State index"
    intro = "I noticed your specific decision problem" if private else "The useful distinction in this decision appears to be between an available alternative and one supported by qualifying evidence."
    return f"{intro} We track this boundary as a timestamped evidence chain; {state} may help separate what is supported, contradicted, and still unknown. {candidate_card_link(signal)}"

def candidate_card_link(signal: dict[str, Any]) -> str:
    return f"https://structevidence.com/states/{signal['mapped_subject_id']}" if signal.get("mapped_subject_id") else "https://structevidence.com/states"

def search_github(query: str, opener=urllib.request.urlopen) -> list[dict[str, Any]]:
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q": query, "per_page": 30})
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "StructEvidence-DSR-v0.1"})
    with opener(request, timeout=20) as response: payload = json.load(response)
    return [{"platform": "GITHUB", "source_url": item["html_url"], "observed_at": utcnow(), "author_public_id": str(item["user"]["id"]), "author_public_name": item["user"]["login"], "organization_public_name": None, "text": f"{item['title']}\n{item.get('body') or ''}", "contact_route": "PUBLIC_REPLY"} for item in payload.get("items", [])]

def source_capabilities() -> dict[str, str]:
    return {"GITHUB": "AUTO_PUBLIC_API", "STACK_EXCHANGE": "AUTO_PUBLIC_API", "REDDIT": "MANUAL_SEARCH_REQUIRED", "X": "MANUAL_SEARCH_REQUIRED", "LINKEDIN": "MANUAL_SEARCH_REQUIRED", "PUBLIC_FORUM": "MANUAL_SEARCH_REQUIRED"}

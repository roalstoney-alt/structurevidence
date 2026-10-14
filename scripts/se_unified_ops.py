#!/usr/bin/env python3
"""StructEvidence single-schedule orchestrator and X publishing adapter.

The module deliberately separates configured, attempted, delivered and verified.
It has no scheduler of its own: an existing approved scheduler invokes this file.
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import dataclasses
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SGT = ZoneInfo("Asia/Singapore")
UTC = dt.timezone.utc
ALLOWED_STATES = {"PASS", "PARTIAL", "BLOCKED", "MISSED", "NOT_DUE", "HOLD", "UNVERIFIED"}
REVIEW_RESULTS = {"NO_STATE_CHANGE", "REVIEW_INCOMPLETE", "HUMAN_GATE_REQUIRED"}
EVENTS = {
    "SCHEDULED", "STARTED", "SEARCH_COMPLETED", "ARTIFACT_CREATED",
    "WRITE_ATTEMPTED", "DELIVERED", "VERIFIED",
}
X_URL_RE = re.compile(r"https?://[^\s]+", re.I)
SENSITIVE_PUBLIC_TERMS = {
    "internal contract amount", "private supplier accusation", "family movement",
    "clinical personal record", "pathogen handling instruction",
}


class OpsError(RuntimeError):
    code = "OPS_ERROR"


class LockHeld(OpsError):
    code = "RUN_LOCK_HELD"


class AppendOnlyConflict(OpsError):
    code = "APPEND_ONLY_CONFLICT"


class GateBlocked(OpsError):
    code = "PUBLIC_TRUST_GATE_FAILED"


class PublisherError(OpsError):
    code = "X_PUBLISH_ERROR"

    def __init__(self, message: str, *, status: int | None = None, outcome_unknown: bool = False):
        super().__init__(message)
        self.status = status
        self.outcome_unknown = outcome_unknown


def iso_now() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def artifact_ref(path: Path, root: Path, state_root: Path) -> str:
    if path.is_relative_to(root):
        return str(path.relative_to(root))
    if path.is_relative_to(state_root):
        return "STATE_ROOT/" + str(path.relative_to(state_root))
    return path.name


def atomic_json(path: Path, value: Any, *, replace: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not replace and path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if canonical_json(existing) != canonical_json(value):
            raise AppendOnlyConflict(f"refusing to replace append-only artifact: {path}")
        return
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def append_jsonl_once(path: Path, value: dict[str, Any], key: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        for line in handle:
            if line.strip() and json.loads(line).get(key) == value.get(key):
                return False
        handle.seek(0, os.SEEK_END)
        handle.write(canonical_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        return True


@dataclasses.dataclass
class Lease:
    path: Path
    run_id: str
    ttl_seconds: int = 7200

    def acquire(self, now: dt.datetime | None = None) -> None:
        now = now or dt.datetime.now(UTC)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            current = json.loads(self.path.read_text(encoding="utf-8"))
            expires = dt.datetime.fromisoformat(current["expires_at"].replace("Z", "+00:00"))
            if expires > now and current.get("run_id") != self.run_id:
                raise LockHeld(f"active run lease: {current.get('run_id')}")
        payload = {
            "run_id": self.run_id,
            "acquired_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "expires_at": (now + dt.timedelta(seconds=self.ttl_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        atomic_json(self.path, payload)

    def release(self) -> None:
        if not self.path.exists():
            return
        current = json.loads(self.path.read_text(encoding="utf-8"))
        if current.get("run_id") == self.run_id:
            self.path.unlink()


def stable_run_id(date_sgt: str, scheduled_at: str) -> str:
    key = f"StructEvidence|{date_sgt}|SE-UNIFIED-SCHEDULE-X-v1.0|{scheduled_at}"
    return f"SE-OPS-{date_sgt.replace('-', '')}-2200-{uuid.uuid5(uuid.NAMESPACE_URL, key)}"


def x_weighted_length(text: str) -> int:
    """Conservative X length check: every URL consumes the current t.co 23-char slot."""
    without_urls = X_URL_RE.sub("", text)
    return len(without_urls) + (23 * len(X_URL_RE.findall(text)))


def canonical_post_text(text: str) -> str:
    return " ".join(text.split()).strip()


def validate_candidate(candidate: dict[str, Any]) -> None:
    text = canonical_post_text(candidate.get("text", ""))
    if not text or x_weighted_length(text) > 280:
        raise GateBlocked("candidate is empty or exceeds X weighted length")
    if candidate.get("approval_gate") not in {"AUTO_PUBLISH", "HUMAN_GATE_REQUIRED", "BLOCKED"}:
        raise GateBlocked("invalid approval gate")
    lower = canonical_json(candidate).lower()
    if any(term in lower for term in SENSITIVE_PUBLIC_TERMS):
        raise GateBlocked("sensitive/private material detected in public payload")
    if candidate.get("material_state_transition") and candidate.get("approval_gate") != "HUMAN_GATE_REQUIRED":
        raise GateBlocked("material state transitions require human review")
    urls = X_URL_RE.findall(text)
    if sorted(urls) != sorted(candidate.get("source_urls", [])):
        raise GateBlocked("candidate source URLs do not match final text URLs")


def validate_review(review: dict[str, Any]) -> None:
    required = {
        "case_id", "review_id", "reviewed_at", "result", "review_complete",
        "search_boundary", "sources_checked", "old_state", "new_state",
        "new_qualifying_evidence_count", "new_counter_evidence_count",
    }
    missing = sorted(required - set(review))
    if missing:
        raise GateBlocked(f"review missing required fields: {', '.join(missing)}")
    if review["result"] not in REVIEW_RESULTS:
        raise GateBlocked("invalid review result")
    if review["result"] == "NO_STATE_CHANGE":
        if review["review_complete"] is not True or not review["sources_checked"]:
            raise GateBlocked("NO_STATE_CHANGE requires a completed bounded review")
        if review["old_state"] != review["new_state"]:
            raise GateBlocked("NO_STATE_CHANGE cannot mutate accepted state")
        for field in ("new_qualifying_evidence_count", "new_counter_evidence_count"):
            if not isinstance(review[field], int) or review[field] < 0:
                raise GateBlocked("NO_STATE_CHANGE requires explicit nonnegative counts")
    if review["result"] == "HUMAN_GATE_REQUIRED" and review["old_state"] == review["new_state"]:
        # The accepted state remains frozen until a later human decision.
        return


def validate_irkutsk_budget(review: dict[str, Any]) -> None:
    budget = review.get("search_budget", {})
    if budget.get("targeted_search_groups", 0) > 4 or budget.get("webpage_open_attempts", 0) > 8:
        raise GateBlocked("Irkutsk consolidated search budget exceeded")
    sources = review.get("source_graph", [])
    ids = [row.get("source_id") for row in sources]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise GateBlocked("Irkutsk source graph requires unique source IDs")
    for row in sources:
        required = {"url", "retrieved_at", "originator", "publisher", "source_type", "claim_ids", "depends_on", "relation", "verification_status", "search_boundary"}
        if not required.issubset(row):
            raise GateBlocked("Irkutsk source graph record is incomplete")


def check_schedule_ownership(snapshot: dict[str, Any]) -> dict[str, Any]:
    timers = [row for row in snapshot.get("timers", []) if row.get("project") == "StructEvidence" and row.get("active")]
    owners = {row.get("logical_owner") or row.get("id") for row in timers}
    exact = len(timers) == 1 and len(owners) == 1
    timer = timers[0] if exact else None
    exact = bool(exact and timer.get("timezone") == "Asia/Singapore" and timer.get("local_time") == "22:00")
    return {
        "state": "PASS" if exact else ("FAIL" if timers else "UNVERIFIED"),
        "active_structevidence_timers": len(timers),
        "verified_owner": timer.get("logical_owner") if exact else None,
        "reason": None if exact else "expected exactly one active StructEvidence timer at 22:00 Asia/Singapore",
    }


def classify_github_write(http_status: int | None, commit_sha: str | None) -> dict[str, Any]:
    if http_status in {200, 201} and commit_sha:
        return {"state": "GITHUB_COMMITTED", "commit_sha": commit_sha, "error_code": None}
    return {"state": "PUBLIC_UPDATE_BLOCKED", "commit_sha": None, "error_code": f"HTTP_{http_status}" if http_status else "NO_WRITE_INTERFACE"}


def verify_public_deploy(expected_sha: str, deployed_sha: str | None, http_status: int | None, body: str, marker: str) -> dict[str, Any]:
    matched = bool(http_status == 200 and deployed_sha == expected_sha and marker and marker in body)
    return {
        "result": "PUBLIC_VERIFIED" if matched else "PUBLIC_VERIFICATION_FAILED",
        "expected_sha": expected_sha,
        "deployed_sha": deployed_sha,
        "http_status": http_status,
        "body_marker_verified": bool(marker and marker in body),
    }


class XPublisher:
    def verify_account(self) -> dict[str, Any]:
        raise NotImplementedError

    def recent_posts(self, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError

    def publish(self, text: str, idempotency_key: str) -> dict[str, Any]:
        raise NotImplementedError

    def fetch_post(self, post_id: str) -> dict[str, Any]:
        raise NotImplementedError


class XApiPublisher(XPublisher):
    """Official X API v2 adapter using an OAuth 2 user access token."""

    def __init__(self, token: str, expected_handle: str = "structevidence", timeout: int = 20):
        if not token:
            raise PublisherError("X_USER_ACCESS_TOKEN is not configured")
        self.token = token
        self.expected_handle = expected_handle.lstrip("@").lower()
        self.timeout = timeout
        self.account: dict[str, Any] | None = None
        self.last_rate_limit: dict[str, str] = {}

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else canonical_json(payload).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.x.com{path}", data=body, method=method,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                self.last_rate_limit = {
                    key.lower(): value for key, value in response.headers.items()
                    if key.lower().startswith("x-rate-limit")
                }
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read(4096).decode("utf-8", errors="replace")
            raise PublisherError(f"X API HTTP {exc.code}: {detail[:500]}", status=exc.code) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            # A transport failure during POST may occur after the provider accepted it.
            raise PublisherError(f"X API transport error: {type(exc).__name__}", outcome_unknown=(method == "POST")) from exc

    def verify_account(self) -> dict[str, Any]:
        payload = self._request("GET", "/2/users/me?user.fields=id,username,name")
        account = payload.get("data") or {}
        if account.get("username", "").lower() != self.expected_handle:
            raise PublisherError("authenticated X account does not match @structevidence", status=403)
        self.account = account
        return {"id": account["id"], "username": account["username"], "write_interface": "X_API_V2_OAUTH2_USER"}

    def recent_posts(self, limit: int = 50) -> list[dict[str, Any]]:
        account = self.account or self.verify_account()
        limit = max(5, min(100, limit))
        query = urllib.parse.urlencode({"max_results": limit, "tweet.fields": "created_at,author_id,text"})
        return self._request("GET", f"/2/users/{account['id']}/tweets?{query}").get("data", [])

    def publish(self, text: str, idempotency_key: str) -> dict[str, Any]:
        # X has no native idempotency header for create-post. Reconciliation is mandatory.
        del idempotency_key
        return self._request("POST", "/2/tweets", {"text": text}).get("data", {})

    def fetch_post(self, post_id: str) -> dict[str, Any]:
        query = urllib.parse.urlencode({"tweet.fields": "created_at,author_id,text"})
        return self._request("GET", f"/2/tweets/{post_id}?{query}").get("data", {})


class XOAuth1Publisher(XPublisher):
    """Official X API v2 adapter using OAuth 1.0a user context."""

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str, expected_handle: str = "structevidence", timeout: int = 20):
        values = (api_key, api_secret, access_token, access_token_secret)
        if not all(values):
            raise PublisherError("X OAuth 1.0a credentials are incomplete")
        self.api_key, self.api_secret, self.access_token, self.access_token_secret = values
        self.expected_handle = expected_handle.lstrip("@").lower()
        self.timeout = timeout
        self.account: dict[str, Any] | None = None
        self.last_rate_limit: dict[str, str] = {}

    @staticmethod
    def _encode(value: str) -> str:
        return urllib.parse.quote(str(value), safe="~-._")

    def _oauth_header(self, method: str, url: str, *, nonce: str | None = None, timestamp: str | None = None) -> str:
        parsed = urllib.parse.urlsplit(url)
        oauth = {
            "oauth_consumer_key": self.api_key,
            "oauth_nonce": nonce or uuid.uuid4().hex,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": timestamp or str(int(dt.datetime.now(UTC).timestamp())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }
        pairs = list(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)) + list(oauth.items())
        encoded_pairs = sorted((self._encode(key), self._encode(value)) for key, value in pairs)
        normalized = "&".join(f"{key}={value}" for key, value in encoded_pairs)
        base_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        signature_base = "&".join((method.upper(), self._encode(base_url), self._encode(normalized)))
        signing_key = f"{self._encode(self.api_secret)}&{self._encode(self.access_token_secret)}"
        digest = hmac.new(signing_key.encode(), signature_base.encode(), hashlib.sha1).digest()
        oauth["oauth_signature"] = base64.b64encode(digest).decode()
        return "OAuth " + ", ".join(f'{self._encode(key)}="{self._encode(value)}"' for key, value in sorted(oauth.items()))

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"https://api.x.com{path}"
        body = None if payload is None else canonical_json(payload).encode("utf-8")
        request = urllib.request.Request(
            url, data=body, method=method,
            headers={"Authorization": self._oauth_header(method, url), "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                self.last_rate_limit = {
                    key.lower(): value for key, value in response.headers.items()
                    if key.lower().startswith("x-rate-limit")
                }
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read(4096).decode("utf-8", errors="replace")
            raise PublisherError(f"X API HTTP {exc.code}: {detail[:500]}", status=exc.code) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise PublisherError(f"X API transport error: {type(exc).__name__}", outcome_unknown=(method == "POST")) from exc

    def verify_account(self) -> dict[str, Any]:
        payload = self._request("GET", "/2/users/me?user.fields=id,username,name")
        account = payload.get("data") or {}
        if account.get("username", "").lower() != self.expected_handle:
            raise PublisherError("authenticated X account does not match @structevidence", status=403)
        self.account = account
        return {"id": account["id"], "username": account["username"], "write_interface": "X_API_V2_OAUTH1_USER"}

    def recent_posts(self, limit: int = 50) -> list[dict[str, Any]]:
        account = self.account or self.verify_account()
        query = urllib.parse.urlencode({"max_results": max(5, min(100, limit)), "tweet.fields": "created_at,author_id,text"})
        return self._request("GET", f"/2/users/{account['id']}/tweets?{query}").get("data", [])

    def publish(self, text: str, idempotency_key: str) -> dict[str, Any]:
        del idempotency_key
        return self._request("POST", "/2/tweets", {"text": text}).get("data", {})

    def fetch_post(self, post_id: str) -> dict[str, Any]:
        query = urllib.parse.urlencode({"tweet.fields": "created_at,author_id,text"})
        return self._request("GET", f"/2/tweets/{post_id}?{query}").get("data", {})


def publisher_from_env(environ: dict[str, str] | None = None, expected_handle: str = "structevidence") -> XPublisher:
    environ = os.environ if environ is None else environ
    oauth1_names = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")
    if all(environ.get(name) for name in oauth1_names):
        return XOAuth1Publisher(*(environ[name] for name in oauth1_names), expected_handle=expected_handle)
    if any(environ.get(name) for name in oauth1_names):
        return BlockedPublisher("X_PUBLISH_BLOCKED_INCOMPLETE_OAUTH1_CREDENTIALS")
    if environ.get("X_USER_ACCESS_TOKEN"):
        return XApiPublisher(environ["X_USER_ACCESS_TOKEN"], expected_handle)
    return BlockedPublisher("X_PUBLISH_BLOCKED_NO_WRITE_INTERFACE")


class BlockedPublisher(XPublisher):
    def __init__(self, reason: str = "X_PUBLISH_BLOCKED_NO_WRITE_INTERFACE"):
        self.reason = reason

    def verify_account(self) -> dict[str, Any]:
        raise PublisherError(self.reason)

    def recent_posts(self, limit: int = 50) -> list[dict[str, Any]]:
        del limit
        raise PublisherError(self.reason)

    def publish(self, text: str, idempotency_key: str) -> dict[str, Any]:
        del text, idempotency_key
        raise PublisherError(self.reason)

    def fetch_post(self, post_id: str) -> dict[str, Any]:
        del post_id
        raise PublisherError(self.reason)


def live_publish_once(
    publisher: XPublisher,
    candidate: dict[str, Any],
    posts_ledger: Path,
    *,
    now: str | None = None,
) -> dict[str, Any]:
    validate_candidate(candidate)
    if candidate["approval_gate"] != "AUTO_PUBLISH":
        raise GateBlocked(f"candidate gate is {candidate['approval_gate']}")
    account = publisher.verify_account()
    expected = canonical_post_text(candidate["text"])
    content_hash = candidate["content_hash"]
    existing: list[dict[str, Any]] = []
    if posts_ledger.exists():
        existing = [json.loads(line) for line in posts_ledger.read_text(encoding="utf-8").splitlines() if line]
    match = next((row for row in existing if row.get("account_id") == account["id"] and row.get("content_hash") == content_hash), None)
    if match:
        readback = publisher.fetch_post(match["post_id"])
        if canonical_post_text(readback.get("text", "")) != expected or readback.get("author_id") != account["id"]:
            raise PublisherError("ledger post did not verify against provider readback")
        return {**match, "replayed": True, "verification_checked_at": now or iso_now()}

    recent = publisher.recent_posts(50)
    provider_match = next((row for row in recent if canonical_post_text(row.get("text", "")) == expected), None)
    if provider_match:
        receipt = {
            "receipt_id": f"X-RECONCILED-{provider_match['id']}", "account_id": account["id"],
            "account": f"@{account['username']}", "content_hash": content_hash,
            "post_id": provider_match["id"], "post_url": f"https://x.com/{account['username']}/status/{provider_match['id']}",
            "published_at": provider_match.get("created_at"), "verification_checked_at": now or iso_now(),
            "status": "PUBLISHED_VERIFIED", "reconciled_without_resend": True,
        }
        append_jsonl_once(posts_ledger, receipt, "post_id")
        return receipt

    try:
        sent = publisher.publish(expected, f"{account['id']}:{candidate['scheduled_date']}:{content_hash}")
    except PublisherError as exc:
        if exc.outcome_unknown:
            # Reconcile before any caller is permitted to retry.
            recent = publisher.recent_posts(50)
            found = next((row for row in recent if canonical_post_text(row.get("text", "")) == expected), None)
            if not found:
                raise PublisherError("PUBLISH_OUTCOME_UNKNOWN; no blind retry permitted", outcome_unknown=True) from exc
            sent = found
        else:
            raise
    post_id = sent.get("id")
    if not post_id:
        raise PublisherError("X create-post response contained no post ID", outcome_unknown=True)
    readback = publisher.fetch_post(post_id)
    if canonical_post_text(readback.get("text", "")) != expected or readback.get("author_id") != account["id"]:
        return {
            "receipt_id": f"X-PENDING-{post_id}", "account_id": account["id"], "account": f"@{account['username']}",
            "content_hash": content_hash, "post_id": post_id, "post_url": None,
            "published_at": sent.get("created_at"), "verification_checked_at": now or iso_now(),
            "status": "POST_ACCEPTED_VERIFICATION_PENDING", "replayed": False,
        }
    receipt = {
        "receipt_id": f"X-VERIFIED-{post_id}", "account_id": account["id"], "account": f"@{account['username']}",
        "content_hash": content_hash, "post_id": post_id,
        "post_url": f"https://x.com/{account['username']}/status/{post_id}",
        "published_at": readback.get("created_at") or sent.get("created_at"),
        "verification_checked_at": now or iso_now(), "status": "PUBLISHED_VERIFIED", "replayed": False,
    }
    append_jsonl_once(posts_ledger, receipt, "post_id")
    return receipt


def default_candidate(date_sgt: str, config: dict[str, Any]) -> dict[str, Any]:
    template = config["x"].get("daily_manual_text_template", config["x"]["method_test_text"])
    text = canonical_post_text(template.format(date_sgt=date_sgt))
    candidate = {
        "schema_version": "se-x-candidate-v1", "candidate_id": f"SE-X-{date_sgt}-METHOD-01",
        "day_index": None, "scheduled_date": date_sgt, "text": text,
        "source_urls": X_URL_RE.findall(text), "evidence_cutoff": config["x"]["method_cutoff"],
        "content_hash": sha256_text(text), "approval_gate": "HUMAN_GATE_REQUIRED",
        "material_state_transition": False, "account_identity": "@structevidence",
        "dedup_check": "MANUAL_REVIEW_PENDING", "publish_attempt_id": None,
        "post_id": None, "public_url": None, "published_at": None,
        "verification_checked_at": None, "status": "AWAITING_HUMAN_REVIEW",
        "new_findings_existed": False, "correction_required": False,
    }
    validate_candidate(candidate)
    return candidate


def new_run(date_sgt: str, baseline_sha: str) -> dict[str, Any]:
    scheduled = f"{date_sgt}T22:00:00+08:00"
    weekday = dt.date.fromisoformat(date_sgt).weekday()
    return {
        "schema_version": "se-unified-run-v1", "run_id": stable_run_id(date_sgt, scheduled),
        "date_sgt": date_sgt, "scheduled_at": scheduled, "started_at": None, "ended_at": None,
        "report_delivered_at": None,
        "repo_baseline_sha": baseline_sha, "repo_final_sha": None,
        "pipeline": {key: "UNVERIFIED" for key in ("scheduler", "cases", "cml_ingestion", "x_publish", "audit_persistence", "external_delivery")},
        "reviews": [],
        "x": {"account": "@structevidence", "publication_authorized": False, "account_verified": False,
              "candidate_file": None, "post_id": None, "post_url": None, "posted_at": None,
              "result": "NOT_ATTEMPTED", "blocker": None},
        "internal_workflows": {
            "sunday_weekly_synthesis": {"due": weekday == 6, "state": "UNVERIFIED" if weekday == 6 else "NOT_DUE", "artifact": None},
            "monday_socsm": {"due": weekday == 0, "state": "UNVERIFIED" if weekday == 0 else "NOT_DUE", "artifact": None, "public_projection": "PRIVATE"},
        },
        "receipt_ids": [], "alerts": [], "events": [], "outcome": "UNVERIFIED",
    }


def event(run: dict[str, Any], name: str, stage: str, proof: str | None = None) -> None:
    if name not in EVENTS:
        raise ValueError(name)
    payload = {"event_id": sha256_text(f"{run['run_id']}|{name}|{stage}|{proof or ''}"), "event": name, "stage": stage, "at": iso_now()}
    if proof:
        payload["proof"] = proof
    if not any(row["event_id"] == payload["event_id"] for row in run["events"]):
        run["events"].append(payload)


def render_report(run: dict[str, Any], candidate: dict[str, Any], cross_project: dict[str, Any]) -> str:
    def row(name: str, due: str, enabled: str, actual: str, evidence: str, receipt: str, state: str, action: str) -> str:
        assert state in ALLOWED_STATES
        return f"| {name} | {due} | {enabled} | {actual} | {evidence} | {receipt} | {state} | {action} |"
    review_by_case = {r.get("case_id"): r for r in run.get("reviews", [])}
    lines = [
        f"# StructEvidence Daily Execution Report | {run['date_sgt']} | SGT", "",
        f"Run ended at: {run.get('ended_at') or 'NONE'}",
        f"Report delivered at: {run.get('report_delivered_at') or 'NONE'}",
        f"Delivery state: {run.get('pipeline', {}).get('external_delivery', 'UNVERIFIED')}", "",
        "| Project / subflow | Due | Enabled | Last actual run | Execution evidence (review/artifact) | Publish/delivery receipt | State | Failure / next action |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, label in (("CML-PDRE-001", "SE 800V"), ("SE-BESS-SODIUM-001", "SE sodium BESS"), ("SE-IRK-LAB-001", "SE Irkutsk direct+indirect")):
        r = review_by_case.get(cid)
        state = ("PARTIAL" if r and r.get("result") == "REVIEW_INCOMPLETE" else
                 "HOLD" if r and r.get("result") == "HUMAN_GATE_REQUIRED" else
                 "PASS" if r else "UNVERIFIED")
        lines.append(row(label, "YES", "YES", r.get("reviewed_at", "NONE") if r else "NONE", r.get("review_id", "NONE") if r else "NONE", "pending", state, r.get("result", "bounded review not recorded") if r else "bounded review not recorded"))
    weekday = dt.date.fromisoformat(run["date_sgt"]).weekday()
    internal = run.get("internal_workflows", {})
    weekly = internal.get("sunday_weekly_synthesis", {"state": "UNVERIFIED", "artifact": None})
    socsm = internal.get("monday_socsm", {"state": "UNVERIFIED", "artifact": None})
    lines.append(row("SE weekly synthesis + folded NSCLC", "Sundays", "YES", "NONE", weekly.get("artifact") or "NONE", "pending", weekly["state"], "same-run Sunday addendum only"))
    lines.append(row("SE SOCSM", "Mondays", "YES", "NONE", socsm.get("artifact") or "NONE", "PRIVATE", socsm["state"], "same-run Monday check only; strict private/public wall"))
    x = run["x"]
    x_state = "PASS" if x.get("post_url") else ("BLOCKED" if x.get("blocker") else "UNVERIFIED")
    lines.append(row("SE X candidate", "YES", "REPORT-ONLY", "NONE", candidate["candidate_id"], x.get("blocker") or "NONE", x_state, "human review and manual publication"))
    for key, label, due in (("cml", "CML technical/FDE", "own daily plan"), ("lovetimeline", "LoveTimeline", "Mon/Tue/Fri")):
        item = cross_project.get(key, {})
        lines.append(row(label, due, str(item.get("enabled", "UNKNOWN")), item.get("last_actual_run", "NONE"), item.get("artifact", "NONE"), item.get("receipt", "draft only; OUTREACH HOLD"), item.get("state", "UNVERIFIED"), item.get("next_action", "read permission or real run evidence required")))
    due_count = 5 + (1 if weekday == 6 else 0) + (1 if weekday == 0 else 0) + (1 if weekday in {0, 1, 4} else 0)
    verified = sum(1 for value in run["pipeline"].values() if value == "PASS")
    blocked = sum(1 for value in run["pipeline"].values() if value == "BLOCKED")
    lines += [
        "", "## X daily post", "", f"- Exact English text: {candidate['text']}",
        "- State: AWAITING_HUMAN_REVIEW",
        f"- Approval gate: {candidate['approval_gate']}",
        f"- Content hash: {candidate['content_hash']}",
        f"- Cited URLs: {', '.join(candidate['source_urls']) or 'NONE'}",
        f"- Source cutoff: {candidate['evidence_cutoff']}",
        f"- Automatic publication blocker: {x.get('blocker') or 'X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW'}",
        "- X_POST_SENT: 0",
        f"- Post ID: {x.get('post_id') or 'NONE'}", f"- Verified URL: {x.get('post_url') or 'NONE'}",
        f"- Published at: {x.get('posted_at') or 'NONE'}",
        f"- New findings existed: {'YES' if candidate['new_findings_existed'] else 'NO'}",
        f"- Prior post correction needed: {'YES' if candidate['correction_required'] else 'NO'}",
        "", "## Reconciliation", "", "- 7-day missing runs: UNVERIFIED until an independent health surface supplies run history",
        f"- due_count: {due_count}", f"- execution_verified_count: {verified}",
        f"- delivery_verified_count: {1 if x.get('post_url') else 0}", f"- blocked_count: {blocked}",
        f"- human_gate_count: {sum(1 for r in run.get('reviews', []) if r.get('result') == 'HUMAN_GATE_REQUIRED')}",
        "- next checkpoint: next bounded run at the existing single 22:00 Asia/Singapore trigger",
        "- confirmed platform connectivity: X automatic publication paused; no write interface called",
    ]
    return "\n".join(lines) + "\n"


def run_orchestrator(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(args.root).resolve()
    config = json.loads((root / "data/ops/se/config.json").read_text(encoding="utf-8"))
    date_sgt = args.date or dt.datetime.now(SGT).date().isoformat()
    baseline_sha = args.baseline_sha or config["baseline_main_sha"]
    run = new_run(date_sgt, baseline_sha)
    state_root = Path(os.environ.get("SE_OPS_STATE_DIR", root / "data/ops/se"))
    run_file = state_root / "runs" / f"{date_sgt}.json"
    candidate_file = state_root / "x-candidates" / f"{date_sgt}.json"
    ledger = state_root / "ledger.jsonl"
    posts_ledger = state_root / "x-posts.jsonl"
    alerts_file = state_root / "alerts" / f"{date_sgt}.json"
    lease = Lease(state_root / "runtime" / f"{date_sgt}.lock.json", run["run_id"])
    lease.acquire()
    try:
        if run_file.exists():
            previous = json.loads(run_file.read_text(encoding="utf-8"))
            if previous.get("run_id") == run["run_id"] and previous.get("outcome") in {"PASS", "PARTIAL", "BLOCKED"}:
                return previous, json.loads(candidate_file.read_text(encoding="utf-8"))
        run["started_at"] = iso_now()
        event(run, "SCHEDULED", "scheduler", run["scheduled_at"])
        event(run, "STARTED", "orchestrator")
        ownership = json.loads((root / "data/ops/se/SCHEDULE_OWNERSHIP.json").read_text(encoding="utf-8"))
        check = check_schedule_ownership(ownership)
        run["pipeline"]["scheduler"] = "PASS" if check["state"] == "PASS" else "BLOCKED"
        if check["state"] != "PASS":
            run["alerts"].append({"code": "SCHEDULE_CONFLICT", "dedupe_key": f"SCHEDULE_CONFLICT:{date_sgt}", "detail": check["reason"]})

        candidate = default_candidate(date_sgt, config)
        atomic_json(candidate_file, candidate, replace=False)
        run["x"]["candidate_file"] = artifact_ref(candidate_file, root, state_root)
        event(run, "ARTIFACT_CREATED", "x_candidate", run["x"]["candidate_file"])

        reviews_path = root / "data/ops/se/review-inputs" / f"{date_sgt}.json"
        if reviews_path.exists():
            review_bundle = json.loads(reviews_path.read_text(encoding="utf-8"))
            reviews = review_bundle["reviews"]
            for review in reviews:
                validate_review(review)
                if review["case_id"] == "SE-IRK-LAB-001":
                    validate_irkutsk_budget(review)
            run["reviews"] = reviews
            run["pipeline"]["cases"] = "PARTIAL" if any(r["result"] == "REVIEW_INCOMPLETE" for r in reviews) else "PASS"
            event(run, "SEARCH_COMPLETED", "cases", str(reviews_path.relative_to(root)))

            weekly = run["internal_workflows"]["sunday_weekly_synthesis"]
            if weekly["due"]:
                addendum = review_bundle.get("sunday_weekly_addendum")
                if addendum and addendum.get("nsclc_management_status") == "FOLDED" and addendum.get("artifact"):
                    weekly.update(state="PASS", artifact=addendum["artifact"])
                else:
                    weekly["state"] = "BLOCKED"
                    run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"SUNDAY_ADDENDUM:{date_sgt}", "detail": "Sunday weekly synthesis with folded NSCLC was due but no validated addendum was supplied."})

            socsm = run["internal_workflows"]["monday_socsm"]
            if socsm["due"]:
                socsm_input = review_bundle.get("monday_socsm")
                opaque_ref = socsm_input.get("opaque_linkage_id", "") if socsm_input else ""
                if socsm_input and socsm_input.get("state") in {"PASS", "PARTIAL", "HOLD"} and re.fullmatch(r"SOCSM-[A-Z0-9-]{8,64}", opaque_ref):
                    socsm.update(state=socsm_input["state"], artifact=opaque_ref)
                else:
                    socsm["state"] = "BLOCKED"
                    run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"SOCSM:{date_sgt}", "detail": "Monday SOCSM was due but no validated private-wall result was supplied."})
            if any(item["state"] == "BLOCKED" for item in run["internal_workflows"].values()):
                run["pipeline"]["cases"] = "PARTIAL"
        else:
            run["pipeline"]["cases"] = "BLOCKED"
            run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"CASE_REVIEW_MISSING:{date_sgt}", "detail": "No validated daily review-input bundle exists."})

        cross_project: dict[str, Any] = {}
        cross_path_value = args.cross_project_status or os.environ.get("SE_CROSS_PROJECT_STATUS")
        if cross_path_value:
            cross_path = Path(cross_path_value).resolve()
            cross_project = json.loads(cross_path.read_text(encoding="utf-8"))
            for name, item in cross_project.items():
                if name not in {"cml", "lovetimeline"} or item.get("state") not in ALLOWED_STATES:
                    raise GateBlocked("invalid cross-project read-only status bundle")
            run["pipeline"]["cml_ingestion"] = "PASS" if "cml" in cross_project else "PARTIAL"
            event(run, "ARTIFACT_CREATED", "cross_project_read_only", cross_path.name)
        else:
            run["pipeline"]["cml_ingestion"] = "UNVERIFIED"
            run["alerts"].append({"code": "OBSERVABILITY_BLOCKED", "dedupe_key": f"CROSS_PROJECT:{date_sgt}", "detail": "No verified CML/LoveTimeline run evidence was supplied."})
        run["pipeline"]["x_publish"] = "BLOCKED"
        run["x"].update(result="AWAITING_HUMAN_REVIEW", blocker="X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW")
        run["alerts"].append({"code": "X_HUMAN_REVIEW_REQUIRED", "dedupe_key": f"X:{date_sgt}:HUMAN_REVIEW", "detail": run["x"]["blocker"]})

        run["pipeline"]["audit_persistence"] = "PASS"
        run["pipeline"]["external_delivery"] = "BLOCKED"
        run["alerts"].append({"code": "MISSING_RUN_DETECTION_NOT_INDEPENDENT", "dedupe_key": f"MISSING_HEARTBEAT:{date_sgt}", "detail": "No independent health surface has been verified."})
        run["ended_at"] = iso_now()
        failures = [state for state in run["pipeline"].values() if state in {"BLOCKED", "UNVERIFIED", "MISSED"}]
        run["outcome"] = "PASS" if not failures else ("PARTIAL" if run["pipeline"]["audit_persistence"] == "PASS" else "BLOCKED")
        atomic_json(alerts_file, {"schema_version": "se-alerts-v1", "run_id": run["run_id"], "alerts": run["alerts"]}, replace=False)
        event(run, "ARTIFACT_CREATED", "alerts", artifact_ref(alerts_file, root, state_root))
        report = render_report(run, candidate, cross_project)
        report_path = state_root / "reports" / f"{date_sgt}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        if report_path.exists() and report_path.read_text(encoding="utf-8") != report:
            raise AppendOnlyConflict(f"daily report already exists with different content: {report_path}")
        report_path.write_text(report, encoding="utf-8")
        event(run, "ARTIFACT_CREATED", "daily_report", artifact_ref(report_path, root, state_root))
        atomic_json(run_file, run, replace=False)
        append_jsonl_once(ledger, {"event_id": sha256_text(canonical_json(run)), "run_id": run["run_id"], "recorded_at": iso_now(), "outcome": run["outcome"], "run_file": artifact_ref(run_file, root, state_root)}, "run_id")
        return run, candidate
    finally:
        lease.release()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--date")
    parser.add_argument("--baseline-sha")
    parser.add_argument("--cross-project-status")
    parser.add_argument("--mode", choices=("report-only", "dry-run"), default="report-only")
    args = parser.parse_args()
    run, _ = run_orchestrator(args)
    print(canonical_json({"run_id": run["run_id"], "outcome": run["outcome"], "x_result": run["x"]["result"]}))
    return 0 if run["outcome"] in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

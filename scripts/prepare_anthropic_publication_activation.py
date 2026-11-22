#!/usr/bin/env python3
"""Verifiable two-phase activation for the Anthropic evidence case.

Actual mode re-reads an owner-authored GitHub comment, GitHub PR/branch,
Actions, Pages deployment/status and the live response bytes.  It only builds
an interim DEPLOYED_PENDING_LIVE_VERIFICATION overlay; a separate observation
of that overlay creates the final live-verification receipt.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "roalstoney-alt/structurevidence"
CASE_ID = "SE-AI-COMPUTE-OBLIGATIONS-001"
PR_NUMBER = 97
BASE_SHA = "64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554"
CASE_SLUG = "cases/anthropic-compute-obligations"
CANONICAL_URL = "https://structurevidence.org/cases/anthropic-compute-obligations/"
SOURCE_SHA256 = "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b"
OWNER_LOGIN = "roalstoney-alt"
GITHUB_API_ORIGIN = "https://api.github.com"
PAGES_WORKFLOW_EVENT = "dynamic"
PAGES_WORKFLOW_PATH = "dynamic/pages/pages-build-deployment"
PAGES_WORKFLOW_NAME = "pages build and deployment"
INITIAL_DECISION = "APPROVE_VERIFIABLE_TWO_PHASE_RELEASE_AND_AUTO_DEPLOY"
OVERLAY_DECISION = "APPROVE_ACTIVATION_OVERLAY_AND_AUTO_DEPLOY"
FROZEN_CLAIMS_SHA256 = "8952849a7841a443daee63052649e61aa1d556919205afa3ad5905edb9f5c2b6"
FROZEN_SOURCE_REGISTRY_SHA256 = "8683e29fe0ceb0b93973db24ba5739fd07af2166fba4b7f00a02a7aac49f41e1"
FROZEN_PREPUBLICATION_EVENTS_SHA256 = "f40f00bbe2e0c5ebd193e3d8e0f351d6b449251ea71e83a79fc2e57d83cf0616"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
AUTH_RE = re.compile(r"^([A-Z0-9_]+)=([^\r\n]+)$", re.MULTILINE)
LIVE_RESOURCES = {
    "case_html": CANONICAL_URL,
    "case_index_json": CANONICAL_URL + "index.json",
    "claims_jsonl": CANONICAL_URL + "claims-v0.2.jsonl",
}
LIVE_REPOSITORY_PATHS = {
    "case_html": CASE_SLUG + "/index.html",
    "case_index_json": CASE_SLUG + "/index.json",
    "claims_jsonl": CASE_SLUG + "/claims-v0.2.jsonl",
}
OVERLAY_SOURCE_PATHS = (
    CASE_SLUG + "/index.html",
    CASE_SLUG + "/index.json",
    CASE_SLUG + "/structured-metadata-v0.2.json",
    CASE_SLUG + "/events-v0.2.jsonl",
    CASE_SLUG + "/claims-v0.2.jsonl",
    CASE_SLUG + "/source-registry-public-v0.2.json",
    ".well-known/structurevidence.json",
    "claims/index.json",
    "cases/review-status.json",
    "cases/index.html",
)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def parse_time(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be RFC3339 UTC ending in Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} is invalid") from exc


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class GitHubClient:
    is_test_transport = False

    def __init__(self, token: str | None = None, *, api_base: str = GITHUB_API_ORIGIN, test_mode: bool = False):
        api_base = api_base.rstrip("/")
        if api_base != GITHUB_API_ORIGIN:
            if not test_mode:
                raise ValueError("production GitHub API origin is pinned to https://api.github.com")
            self.is_test_transport = True
        self.token, self.api_base = token, api_base

    def get(self, path: str):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "se-aico-verifier-v0.3",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(self.api_base + path, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            raise ValueError(f"GitHub verification failed for {path}: HTTP {exc.code}") from exc


def fetch_live(url: str) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "se-aico-live-verifier-v0.3"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read(), response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), exc.geturl()


def _fixture_guard(value: dict, allow: bool, noun: str) -> None:
    if value.get("test_fixture") is True and not allow:
        raise ValueError(f"test fixtures cannot pass the actual {noun} gate")
    if value.get("test_fixture") not in (True, False):
        raise ValueError("test_fixture must be boolean")


def validate_authorization_record(record: dict, *, allow_test_fixture: bool = False) -> None:
    required = {"schema_version", "case_id", "pr_number", "phase", "base_sha", "candidate_head_sha",
                "owner_login", "github_comment_id", "github_comment_body_sha256", "test_fixture"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"owner authorization record missing fields: {missing}")
    if record["schema_version"] != "SE-AICO-TWO-PHASE-OWNER-AUTHORIZATION-v0.3":
        raise ValueError("unexpected owner authorization schema")
    if (record["case_id"], record["pr_number"], record["base_sha"], record["owner_login"]) != (CASE_ID, PR_NUMBER, BASE_SHA, OWNER_LOGIN):
        raise ValueError("owner authorization has wrong case, PR, base, or owner")
    if record["phase"] not in ("INITIAL_RELEASE", "ACTIVATION_OVERLAY"):
        raise ValueError("invalid owner authorization phase")
    for field in ("base_sha", "candidate_head_sha"):
        if not SHA_RE.fullmatch(record[field]):
            raise ValueError(f"{field} must be an exact Git SHA")
    if record["phase"] == "ACTIVATION_OVERLAY":
        for field in ("initial_deployed_sha", "overlay_head_sha"):
            if not SHA_RE.fullmatch(record.get(field, "")):
                raise ValueError(f"overlay authorization must bind {field}")
    if not isinstance(record["github_comment_id"], int) or record["github_comment_id"] <= 0:
        raise ValueError("github_comment_id must be a positive GitHub ID")
    if not SHA256_RE.fullmatch(record["github_comment_body_sha256"]):
        raise ValueError("github_comment_body_sha256 must be SHA256")
    _fixture_guard(record, allow_test_fixture, "authorization")


def verify_owner_authorization(record: dict, client, *, allow_test_fixture: bool = False) -> dict:
    validate_authorization_record(record, allow_test_fixture=allow_test_fixture)
    if getattr(client, "is_test_transport", False) and not allow_test_fixture:
        raise ValueError("test transport cannot pass the actual authorization gate")
    comment = client.get(f"/repos/{REPOSITORY}/issues/comments/{record['github_comment_id']}")
    if comment.get("user", {}).get("login") != OWNER_LOGIN or comment.get("author_association") != "OWNER":
        raise ValueError("authorization comment is not repository-owner-authored")
    expected_issue_url = f"{GITHUB_API_ORIGIN}/repos/{REPOSITORY}/issues/{PR_NUMBER}"
    if comment.get("issue_url") != expected_issue_url:
        raise ValueError("authorization comment is not bound to PR #97")
    body = comment.get("body", "")
    if digest_bytes(body.encode()) != record["github_comment_body_sha256"]:
        raise ValueError("authorization comment digest mismatch")
    values = {}
    for key, value in AUTH_RE.findall(body):
        if key in values:
            raise ValueError(f"duplicate owner authorization field {key}")
        values[key] = value.strip()
    required = {"CASE_ID": CASE_ID, "PR_NUMBER": str(PR_NUMBER), "BASE_SHA": BASE_SHA,
                "CANDIDATE_HEAD_SHA": record["candidate_head_sha"], "SOCIAL_PUBLISH_AUTHORIZED": "NO"}
    if record["phase"] == "INITIAL_RELEASE":
        required |= {"OWNER_DECISION": INITIAL_DECISION, "MERGE_AUTHORIZED": "YES",
                     "AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED": "YES",
                     "NEXT_GATE": "VERIFIABLE_ACTIVATION_OVERLAY_REVIEW"}
    else:
        required |= {"OWNER_DECISION": OVERLAY_DECISION, "INITIAL_DEPLOYED_SHA": record["initial_deployed_sha"],
                     "OVERLAY_HEAD_SHA": record["overlay_head_sha"], "MERGE_AUTHORIZED": "NO",
                     "AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED": "YES", "NEXT_GATE": "FINAL_LIVE_VERIFICATION"}
    wrong = sorted(key for key, value in required.items() if values.get(key) != value)
    if wrong:
        raise ValueError(f"owner authorization is incomplete or mismatched: {wrong}")
    created_at = comment.get("created_at")
    updated_at = comment.get("updated_at")
    parse_time(created_at, "owner comment created_at")
    parse_time(updated_at, "owner comment updated_at")
    if parse_time(updated_at, "owner comment updated_at") < parse_time(created_at, "owner comment created_at"):
        raise ValueError("owner comment update time precedes creation")
    return {"comment_id": comment["id"], "comment_url": comment.get("html_url"),
            "comment_body_sha256": record["github_comment_body_sha256"], "owner_login": OWNER_LOGIN,
            "author_association": "OWNER", "decision": required["OWNER_DECISION"],
            "authorized_at": updated_at, "comment_created_at": created_at,
            "comment_updated_at": updated_at, "issue_url": expected_issue_url,
            "phase": record["phase"]}


def validate_observation_request(request: dict, *, allow_test_fixture: bool = False) -> None:
    required = {"schema_version", "case_id", "pr_number", "stage", "candidate_head_sha", "deployed_sha",
                "merge_policy", "pages_workflow_run_id", "pages_deployment_id", "pages_deployment_status_id", "test_fixture"}
    missing = sorted(required - request.keys())
    if missing:
        raise ValueError(f"deployment request missing fields: {missing}")
    if request["schema_version"] != "SE-AICO-GITHUB-DEPLOYMENT-OBSERVATION-REQUEST-v0.3":
        raise ValueError("unexpected deployment request schema")
    if (request["case_id"], request["pr_number"]) != (CASE_ID, PR_NUMBER):
        raise ValueError("deployment request identifies the wrong case or PR")
    if request["stage"] not in ("INITIAL_PAGES_DEPLOYMENT", "ACTIVATION_OVERLAY_DEPLOYMENT"):
        raise ValueError("invalid deployment stage")
    if request["merge_policy"] not in ("merge", "squash"):
        raise ValueError("merge_policy must be merge or squash")
    for field in ("candidate_head_sha", "deployed_sha"):
        if not SHA_RE.fullmatch(request[field]):
            raise ValueError(f"{field} must be an exact Git SHA")
    for field in ("pages_workflow_run_id", "pages_deployment_id", "pages_deployment_status_id"):
        if not isinstance(request[field], int) or request[field] <= 0:
            raise ValueError(f"{field} must be a positive GitHub ID")
    expected = request.get("expected_live_sha256")
    if request["stage"] == "ACTIVATION_OVERLAY_DEPLOYMENT":
        if not isinstance(expected, dict) or set(expected) != set(LIVE_RESOURCES) or any(not SHA256_RE.fullmatch(v) for v in expected.values()):
            raise ValueError("overlay observation requires all expected live SHA256 values")
    elif expected not in (None, {}):
        raise ValueError("initial observation records rather than predeclares hashes")
    _fixture_guard(request, allow_test_fixture, "deployment")


def verify_merge_topology(request: dict, pr: dict, deployed_commit: dict, candidate_commit: dict, comparison: dict) -> None:
    if pr.get("head", {}).get("sha") != request["candidate_head_sha"] or pr.get("base", {}).get("sha") != BASE_SHA:
        raise ValueError("PR head/base do not match authorization")
    if not pr.get("merged") or pr.get("merge_commit_sha") != request["deployed_sha"]:
        raise ValueError("deployed SHA is not PR #97's merge result")
    parents = deployed_commit.get("parents", [])
    if request["merge_policy"] == "merge":
        if len(parents) < 2 or comparison.get("status") not in ("ahead", "identical"):
            raise ValueError("merge result does not contain authorized candidate")
    elif len(parents) != 1 or deployed_commit.get("commit", {}).get("tree", {}).get("sha") != candidate_commit.get("commit", {}).get("tree", {}).get("sha"):
        raise ValueError("squash result tree differs from authorized candidate")


def repository_bytes_at(client, deployed_sha: str, path: str) -> tuple[bytes, str]:
    encoded_path = urllib.parse.quote(path, safe="/")
    content = client.get(f"/repos/{REPOSITORY}/contents/{encoded_path}?ref={deployed_sha}")
    if content.get("type") != "file" or content.get("encoding") != "base64" or not content.get("sha"):
        raise ValueError(f"GitHub contents response is not an exact file: {path}")
    try:
        raw = base64.b64decode(content["content"], validate=False)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"GitHub contents response is invalid base64: {path}") from exc
    return raw, content["sha"]


def validate_live_semantics(name: str, raw: bytes) -> None:
    if name == "case_html":
        text = raw.decode("utf-8")
        if CASE_ID not in text or CANONICAL_URL not in text:
            raise ValueError("live case HTML does not identify the case and canonical URL")
    elif name == "case_index_json":
        record = json.loads(raw)
        if record.get("case_id") != CASE_ID or not isinstance(record.get("claims"), list) or len(record["claims"]) != 15:
            raise ValueError("live case index has wrong case identity or claim count")
    else:
        rows = [json.loads(line) for line in raw.splitlines() if line]
        if len(rows) != 15 or any(not str(row.get("claim_id", "")).startswith("AICO-R") for row in rows):
            raise ValueError("live claims JSONL has wrong case identity or row count")


def verify_source_root(source_root: Path, deployed_sha: str) -> dict[str, str]:
    source_root = source_root.resolve()
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=source_root, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise ValueError("source root is not a Git worktree") from exc
    if head != deployed_sha:
        raise ValueError(f"source root HEAD {head} does not match verified deployed main SHA {deployed_sha}")
    if status:
        raise ValueError("source root worktree is not clean")
    hashes = {}
    for path in OVERLAY_SOURCE_PATHS:
        working = (source_root / path).read_bytes()
        try:
            committed = subprocess.check_output(["git", "show", f"{deployed_sha}:{path}"], cwd=source_root)
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"source path is absent from verified deployed commit: {path}") from exc
        if working != committed:
            raise ValueError(f"source path differs from verified deployed commit: {path}")
        hashes[path] = digest_bytes(committed)
    return hashes


def verify_deployment_observation(request: dict, authorization: dict, client,
                                  live_fetcher: Callable[[str], tuple[int, bytes]] = fetch_live, *,
                                  now: datetime | None = None, allow_test_fixture: bool = False) -> dict:
    validate_observation_request(request, allow_test_fixture=allow_test_fixture)
    auth = verify_owner_authorization(authorization, client, allow_test_fixture=allow_test_fixture)
    if authorization["candidate_head_sha"] != request["candidate_head_sha"]:
        raise ValueError("authorization and deployment bind different candidate SHAs")
    expected_phase = "INITIAL_RELEASE" if request["stage"] == "INITIAL_PAGES_DEPLOYMENT" else "ACTIVATION_OVERLAY"
    if authorization["phase"] != expected_phase:
        raise ValueError("authorization phase does not match deployment stage")
    repo, deployed = f"/repos/{REPOSITORY}", request["deployed_sha"]
    pr = client.get(f"{repo}/pulls/{PR_NUMBER}")
    run = client.get(f"{repo}/actions/runs/{request['pages_workflow_run_id']}")
    deployment = client.get(f"{repo}/deployments/{request['pages_deployment_id']}")
    statuses = client.get(f"{repo}/deployments/{request['pages_deployment_id']}/statuses")
    branch = client.get(f"{repo}/branches/main")
    deployed_commit = client.get(f"{repo}/commits/{deployed}")
    if branch.get("commit", {}).get("sha") != deployed:
        raise ValueError("deployed SHA is not current main HEAD")
    if request["stage"] == "INITIAL_PAGES_DEPLOYMENT":
        candidate_commit = client.get(f"{repo}/commits/{request['candidate_head_sha']}")
        comparison = client.get(f"{repo}/compare/{request['candidate_head_sha']}...{deployed}")
        verify_merge_topology(request, pr, deployed_commit, candidate_commit, comparison)
    else:
        if authorization["overlay_head_sha"] != deployed:
            raise ValueError("overlay authorization does not bind deployed SHA")
        comparison = client.get(f"{repo}/compare/{authorization['initial_deployed_sha']}...{deployed}")
        if comparison.get("status") not in ("ahead", "identical"):
            raise ValueError("overlay is unrelated to initial deployment")
    if (run.get("head_sha"), run.get("head_branch"), run.get("event"), run.get("path"),
            run.get("name"), run.get("status"), run.get("conclusion")) != (
                deployed, "main", PAGES_WORKFLOW_EVENT, PAGES_WORKFLOW_PATH,
                PAGES_WORKFLOW_NAME, "completed", "success"):
        raise ValueError("Actions run is not the pinned successful native Pages workflow")
    if (deployment.get("sha"), deployment.get("ref"), deployment.get("environment")) != (deployed, "main", "github-pages"):
        raise ValueError("Pages deployment does not bind expected SHA/environment")
    status = next((row for row in statuses if row.get("id") == request["pages_deployment_status_id"]), None)
    if not status or status.get("state") != "success" or status.get("environment_url") != "https://structurevidence.org/":
        raise ValueError("Pages status is not observed production success")
    clock = now or datetime.now(timezone.utc)
    authorized_at = parse_time(auth["authorized_at"], "authorized_at")
    run_at = parse_time(run.get("created_at"), "run created_at")
    succeeded_at = parse_time(status.get("created_at"), "deployment succeeded_at")
    if request["stage"] == "INITIAL_PAGES_DEPLOYMENT":
        merged_at = parse_time(pr.get("merged_at"), "PR merged_at")
        if not authorized_at <= merged_at <= run_at <= succeeded_at:
            raise ValueError("authorization/merge/workflow/deployment times are out of order")
    elif not authorized_at <= run_at <= succeeded_at:
        raise ValueError("overlay authorization/workflow/deployment times are out of order")
    if succeeded_at > clock + timedelta(minutes=5):
        raise ValueError("deployment success is in the future")
    retrieved_at, resources = utc_text(clock), {}
    for name, url in LIVE_RESOURCES.items():
        fetched = live_fetcher(url)
        if len(fetched) != 3:
            raise ValueError("live fetcher must report HTTP status, raw bytes and final URL")
        http_status, raw, final_url = fetched
        if http_status != 200:
            raise ValueError(f"live {name} returned HTTP {http_status}")
        if final_url != url:
            raise ValueError(f"live {name} resolved to an unexpected final URL")
        validate_live_semantics(name, raw)
        repository_path = LIVE_REPOSITORY_PATHS[name]
        committed_raw, blob_sha = repository_bytes_at(client, deployed, repository_path)
        if raw != committed_raw:
            raise ValueError(f"live {name} bytes differ from deployed Git tree")
        sha = digest_bytes(raw)
        if name in (request.get("expected_live_sha256") or {}) and sha != request["expected_live_sha256"][name]:
            raise ValueError(f"live {name} hash differs from overlay")
        resources[name] = {"url": url, "final_url": final_url, "http_status": 200, "sha256": sha,
                           "bytes": len(raw), "retrieved_at": retrieved_at, "repository_path": repository_path,
                           "repository_blob_sha": blob_sha, "repository_sha256": digest_bytes(committed_raw),
                           "live_matches_deployed_git_tree": True}
    initial = request["stage"] == "INITIAL_PAGES_DEPLOYMENT"
    return {
        "schema_version": "SE-AICO-INITIAL-PAGES-DEPLOYMENT-RECEIPT-v0.3" if initial else "SE-AICO-FINAL-LIVE-VERIFICATION-RECEIPT-v0.3",
        "case_id": CASE_ID, "stage": request["stage"],
        "status": "DEPLOYED_PENDING_ACTIVATION_OVERLAY" if initial else "ACTIVATION_OVERLAY_DEPLOYED_AND_LIVE_BYTES_VERIFIED",
        "repository": REPOSITORY, "pr_number": PR_NUMBER, "base_sha": BASE_SHA,
        "candidate_head_sha": request["candidate_head_sha"], "deployed_sha": deployed,
        "merge_policy": request["merge_policy"], "owner_authorization": auth,
        "github": {"workflow_run_id": request["pages_workflow_run_id"], "workflow_name": run.get("name"),
                   "workflow_event": PAGES_WORKFLOW_EVENT, "workflow_path": PAGES_WORKFLOW_PATH,
                   "workflow_conclusion": "success",
                   "deployment_id": request["pages_deployment_id"], "deployment_status_id": request["pages_deployment_status_id"],
                   "deployment_environment": "github-pages", "deployment_succeeded_at": status["created_at"],
                   "environment_url": "https://structurevidence.org/", "main_head_sha": deployed},
        "live_resources": resources, "live_verified_at": retrieved_at, "source_sha256": SOURCE_SHA256,
        "test_fixture": request["test_fixture"], "verification_method": "LIVE_GITHUB_API_AND_RAW_HTTP_BYTES",
    }


def verify_frozen_inputs(root: Path) -> dict[str, str]:
    claims = (root / CASE_SLUG / "claims-v0.2.jsonl").read_bytes()
    registry = (root / CASE_SLUG / "source-registry-public-v0.2.json").read_bytes()
    events = (root / CASE_SLUG / "events-v0.2.jsonl").read_bytes()
    if (digest_bytes(claims) != FROZEN_CLAIMS_SHA256
            or digest_bytes(registry) != FROZEN_SOURCE_REGISTRY_SHA256
            or digest_bytes(events) != FROZEN_PREPUBLICATION_EVENTS_SHA256):
        raise ValueError("frozen v0.2 claims, source registry, or prepublication events hash mismatch")
    if json.loads(registry)["sources"][0]["raw_sha256"] != SOURCE_SHA256 or len([x for x in claims.splitlines() if x]) != 15:
        raise ValueError("frozen claims or reviewed source digest changed")
    return {"claims_v0_2_sha256": digest_bytes(claims), "source_registry_sha256": digest_bytes(registry),
            "prepublication_events_sha256": digest_bytes(events),
            "source_capture_sha256_carried_forward": SOURCE_SHA256}


def replace_jsonld_pending(html: str) -> str:
    marker = '<script type="application/ld+json">'
    start, end = html.index(marker) + len(marker), html.index("</script>", html.index(marker) + len(marker))
    metadata = json.loads(html[start:end])
    metadata.update(creativeWorkStatus="DEPLOYED_PENDING_LIVE_VERIFICATION", datePublished=None, dateModified=None,
                    name="Anthropic compute obligations — final live verification pending")
    for claim in metadata["hasPart"]:
        for prop in claim.get("additionalProperty", []):
            if prop.get("name") == "claim_record_published_at":
                prop["value"] = None
    html = html[:start] + json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + html[end:]
    section = ('<section class="publication-state" data-publication-state="DEPLOYED_PENDING_LIVE_VERIFICATION">'
               '<h2>Publication state</h2><p>Two-phase release in progress; final live verification is required. '
               'No publication time is asserted and external promotion is prohibited. '
               '<a href="initial-pages-deployment-receipt-v0.3.json">Initial deployment observation</a>.</p></section>')
    return html.replace("<main>", "<main>\n" + section, 1)


def build_pending_overlay(root: Path, receipt: dict, *, allow_test_fixture: bool = False) -> dict[str, bytes]:
    if receipt.get("schema_version") != "SE-AICO-INITIAL-PAGES-DEPLOYMENT-RECEIPT-v0.3" or receipt.get("status") != "DEPLOYED_PENDING_ACTIVATION_OVERLAY":
        raise ValueError("verified initial Pages receipt required")
    _fixture_guard(receipt, allow_test_fixture, "overlay")
    if receipt.get("source_sha256") != SOURCE_SHA256 or set(receipt.get("live_resources", {})) != set(LIVE_RESOURCES):
        raise ValueError("receipt source digest or live observations are incomplete")
    frozen = verify_frozen_inputs(root)
    deployed_at, verified_at = receipt["github"]["deployment_succeeded_at"], receipt["live_verified_at"]
    event_id = "SE-AICO-001-INITIAL-PAGES-" + re.sub(r"[^0-9Z]", "", deployed_at)
    index = load(root, f"{CASE_SLUG}/index.json")
    claims_before = json.dumps(index["claims"], sort_keys=True)
    index.update(status="TWO_PHASE_RELEASE_IN_PROGRESS", deployment_state="DEPLOYED_PENDING_LIVE_VERIFICATION",
                 publication_authorized=True, external_promotion_authorized=False, claim_record_published_at=None,
                 structevidence_publication_date=None, publication_event_at=None,
                 publication_current_state="publication-current-state-v0.3.json",
                 initial_deployment_receipt="initial-pages-deployment-receipt-v0.3.json",
                 prepublication_claim_rows_rewritten=False)
    if json.dumps(index["claims"], sort_keys=True) != claims_before:
        raise AssertionError("embedded claims changed")
    metadata = load(root, f"{CASE_SLUG}/structured-metadata-v0.2.json")
    metadata.update(creativeWorkStatus="DEPLOYED_PENDING_LIVE_VERIFICATION", datePublished=None, dateModified=None,
                    name="Anthropic compute obligations — final live verification pending")
    events_bytes = (root / CASE_SLUG / "events-v0.2.jsonl").read_bytes()
    events = [json.loads(line) for line in events_bytes.splitlines() if line]
    event = {"event_id": event_id, "event_type": "INITIAL_PAGES_DEPLOYMENT_OBSERVED", "event_at": deployed_at,
             "known_at": verified_at, "recorded_at_utc": verified_at,
             "state_before": "PREPUBLICATION_CANDIDATE_PUBLICATION_HOLD",
             "state_after": "DEPLOYED_PENDING_LIVE_VERIFICATION", "publication_effect": "FINAL_PUBLICATION_NOT_ASSERTED",
             "owner_decision": receipt["owner_authorization"]["decision"], "deployed_sha": receipt["deployed_sha"],
             "pages_workflow_run_id": receipt["github"]["workflow_run_id"], "pages_deployment_id": receipt["github"]["deployment_id"],
             "initial_live_hashes": {k: v["sha256"] for k, v in receipt["live_resources"].items()},
             "source_sha256": SOURCE_SHA256, "historical_rows_rewritten": False}
    current = {"schema_version": "SE-AICO-PUBLICATION-CURRENT-STATE-v0.3", "case_id": CASE_ID,
               "status": "DEPLOYED_PENDING_LIVE_VERIFICATION", "publication_event_at": None, "date_published": None,
               "external_promotion_authorized": False, "initial_pages_deployment": receipt,
               "activation_overlay_deployment": None, "final_live_verification": None,
               "evidence_state_changed": False, "historical_prepublication_rows_rewritten": False, "source_sha256": SOURCE_SHA256}
    first_receipt = dict(receipt, frozen_input_hashes=frozen, append_only=True, prepublication_history_rewritten=False)
    discovery, claims_index = load(root, ".well-known/structurevidence.json"), load(root, "claims/index.json")
    for document, key in ((discovery, "versioned_case_adapters"), (claims_index, "versioned_adapters")):
        adapter = next(x for x in document[key] if x["case_id"] == CASE_ID)
        adapter.update(structevidence_date_published=None, publication_state="DEPLOYED_PENDING_LIVE_VERIFICATION",
                       external_promotion_authorized=False,
                       publication_current_state=CANONICAL_URL + "publication-current-state-v0.3.json",
                       initial_deployment_receipt=CANONICAL_URL + "initial-pages-deployment-receipt-v0.3.json")
    review = load(root, "cases/review-status.json")
    row = next(x for x in review["cases"] if x["case_id"] == CASE_ID)
    row.update(last_reviewed_at=receipt["owner_authorization"]["authorized_at"],
               review_result="TWO_PHASE_RELEASE_DEPLOYED_FINAL_VERIFICATION_PENDING", latest_review_id=event_id,
               latest_review_file=f"{CASE_SLUG}/initial-pages-deployment-receipt-v0.3.json",
               period={"id": "VERIFIABLE_TWO_PHASE_ACTIVATION", "start": receipt["owner_authorization"]["authorized_at"][:10],
                       "end": verified_at[:10], "status": "DEPLOYED_PENDING_LIVE_VERIFICATION",
                       "scope": "Initial deployment observed; activation overlay and final verification remain required."},
               period_review_id=event_id)
    case_index = (root / "cases/index.html").read_text()
    old = '<strong>Pending review · OWNER_REVIEW_OF_EXACT_MINIMAL_PR_DIFF</strong><br><small>No completed review recorded for this period.</small>'
    new = (f'<time datetime="{verified_at}">{verified_at[:10]}</time><br><strong>DEPLOYED · FINAL LIVE VERIFICATION REQUIRED</strong><br>'
           '<small>VERIFIABLE_TWO_PHASE_ACTIVATION · No publication time asserted; external promotion prohibited.</small><br>'
           '<a href="/cases/anthropic-compute-obligations/initial-pages-deployment-receipt-v0.3.json">Initial deployment observation</a>')
    if old not in case_index:
        raise ValueError("pending-review label not found")
    relative = {f"{CASE_SLUG}/index.json": json_bytes(index),
                f"{CASE_SLUG}/structured-metadata-v0.2.json": json_bytes(metadata),
                f"{CASE_SLUG}/events-v0.2.jsonl": jsonl_bytes(events + [event]),
                f"{CASE_SLUG}/publication-current-state-v0.3.json": json_bytes(current),
                f"{CASE_SLUG}/initial-pages-deployment-receipt-v0.3.json": json_bytes(first_receipt),
                f"{CASE_SLUG}/index.html": replace_jsonld_pending((root / CASE_SLUG / "index.html").read_text()).encode(),
                ".well-known/structurevidence.json": json_bytes(discovery), "claims/index.json": json_bytes(claims_index),
                "cases/review-status.json": json_bytes(review), "cases/index.html": case_index.replace(old, new, 1).encode()}
    return relative | {"docs/" + path: value for path, value in relative.items()}


def write_overlay(output: Path, overlay: dict[str, bytes], receipt: dict) -> None:
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be empty")
    for relative, value in overlay.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    manifest = {"schema_version": "SE-AICO-ACTIVATION-OVERLAY-MANIFEST-v0.3", "case_id": CASE_ID,
                "initial_deployed_sha": receipt["deployed_sha"], "candidate_head_sha": receipt["candidate_head_sha"],
                "test_fixture": receipt["test_fixture"],
                "files": [{"path": p, "sha256": digest_bytes(v), "bytes": len(v)} for p, v in sorted(overlay.items())]}
    (output / "activation-manifest-v0.3.json").write_bytes(json_bytes(manifest))


def apply_overlay_transactional(target: Path, output: Path, receipt: dict, *, fault_after: int | None = None,
                                allow_test_fixture: bool = False) -> None:
    _fixture_guard(receipt, allow_test_fixture, "apply")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=target, text=True).strip()
    if head != receipt["deployed_sha"]:
        raise ValueError(f"target HEAD {head} does not match deployed main SHA {receipt['deployed_sha']}")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=target, text=True).strip():
        raise ValueError("target worktree is not clean")
    manifest = json.loads((output / "activation-manifest-v0.3.json").read_text())
    for item in manifest["files"]:
        if digest_bytes((output / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"overlay hash mismatch: {item['path']}")
    with tempfile.TemporaryDirectory(dir=target) as tmp:
        tmp, existed, touched = Path(tmp), {}, []
        for item in manifest["files"]:
            rel, destination = item["path"], target / item["path"]
            existed[rel] = destination.exists()
            if destination.exists():
                backup = tmp / "backup" / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, backup)
            staged = tmp / "staged" / rel
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output / rel, staged)
        try:
            for number, item in enumerate(manifest["files"], 1):
                rel, destination = item["path"], target / item["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(tmp / "staged" / rel, destination)
                touched.append(rel)
                if fault_after == number:
                    raise OSError("injected partial-apply failure")
            for item in manifest["files"]:
                if digest_bytes((target / item["path"]).read_bytes()) != item["sha256"]:
                    raise OSError("post-apply hash mismatch")
        except Exception:
            for rel in reversed(touched):
                destination = target / rel
                if existed[rel]:
                    os.replace(tmp / "backup" / rel, destination)
                elif destination.exists():
                    destination.unlink()
            raise


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("verify", "prepare-overlay"):
        command = sub.add_parser(name)
        command.add_argument("--authorization", type=Path, required=True)
        command.add_argument("--request", type=Path, required=True)
        command.add_argument("--receipt-output", type=Path, required=True)
        if name == "prepare-overlay":
            command.add_argument("--output-dir", type=Path, required=True)
            command.add_argument("--source-root", type=Path, required=True)
            command.add_argument("--apply-to", type=Path)
    args = parser.parse_args()
    auth, request = json.loads(args.authorization.read_text()), json.loads(args.request.read_text())
    receipt = verify_deployment_observation(request, auth, GitHubClient(os.environ.get("GITHUB_TOKEN")))
    if args.command == "prepare-overlay":
        if receipt["stage"] != "INITIAL_PAGES_DEPLOYMENT":
            raise ValueError("only verified initial deployment can prepare overlay")
        source_hashes = verify_source_root(args.source_root, receipt["deployed_sha"])
        receipt["overlay_source_binding"] = {
            "source_root_head_sha": receipt["deployed_sha"],
            "paths": source_hashes,
            "matches_verified_deployed_main": True,
        }
        overlay = build_pending_overlay(args.source_root, receipt)
        write_overlay(args.output_dir, overlay, receipt)
        if args.apply_to:
            apply_overlay_transactional(args.apply_to, args.output_dir, receipt)
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_bytes(json_bytes(receipt))
        print(f"PASS: wrote {len(overlay)} pending overlay files; applied={bool(args.apply_to)}")
    else:
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_bytes(json_bytes(receipt))
        print(f"PASS: wrote verified {receipt['stage']} receipt")


if __name__ == "__main__":
    main()

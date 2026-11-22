#!/usr/bin/env python3
"""Fail-closed tests for the verifiable two-phase activation mechanism."""
from __future__ import annotations

import base64
import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    path = ROOT / "scripts/prepare_anthropic_publication_activation.py"
    spec = importlib.util.spec_from_file_location("aico_activation", path)
    value = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(value)
    return value


A = module()
CANDIDATE, DEPLOYED = "1" * 40, "2" * 40
NOW = datetime(2026, 11, 22, 12, 0, 0, tzinfo=timezone.utc)
LIVE_BYTES = {name: (ROOT / A.LIVE_REPOSITORY_PATHS[name]).read_bytes() for name in A.LIVE_RESOURCES}


def authorization(phase="INITIAL_RELEASE", *, fixture=True):
    lines = {
        "CASE_ID": A.CASE_ID, "PR_NUMBER": str(A.PR_NUMBER), "BASE_SHA": A.BASE_SHA,
        "CANDIDATE_HEAD_SHA": CANDIDATE, "SOCIAL_PUBLISH_AUTHORIZED": "NO",
    }
    if phase == "INITIAL_RELEASE":
        lines |= {"OWNER_DECISION": A.INITIAL_DECISION, "MERGE_AUTHORIZED": "YES",
                  "AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED": "YES",
                  "NEXT_GATE": "VERIFIABLE_ACTIVATION_OVERLAY_REVIEW"}
    else:
        lines |= {"OWNER_DECISION": A.OVERLAY_DECISION, "INITIAL_DEPLOYED_SHA": DEPLOYED,
                  "OVERLAY_HEAD_SHA": "3" * 40, "MERGE_AUTHORIZED": "NO",
                  "AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED": "YES", "NEXT_GATE": "FINAL_LIVE_VERIFICATION"}
    body = "\n".join(f"{key}={value}" for key, value in lines.items())
    record = {"schema_version": "SE-AICO-TWO-PHASE-OWNER-AUTHORIZATION-v0.3", "case_id": A.CASE_ID,
              "pr_number": A.PR_NUMBER, "phase": phase, "base_sha": A.BASE_SHA,
              "candidate_head_sha": CANDIDATE, "owner_login": A.OWNER_LOGIN, "github_comment_id": 9001,
              "github_comment_body_sha256": A.digest_bytes(body.encode()), "test_fixture": fixture}
    if phase == "ACTIVATION_OVERLAY":
        record.update(initial_deployed_sha=DEPLOYED, overlay_head_sha="3" * 40)
    return record, body


def request(policy="merge", *, stage="INITIAL_PAGES_DEPLOYMENT", fixture=True):
    deployed = DEPLOYED if stage == "INITIAL_PAGES_DEPLOYMENT" else "3" * 40
    value = {"schema_version": "SE-AICO-GITHUB-DEPLOYMENT-OBSERVATION-REQUEST-v0.3", "case_id": A.CASE_ID,
             "pr_number": A.PR_NUMBER, "stage": stage, "candidate_head_sha": CANDIDATE,
             "deployed_sha": deployed, "merge_policy": policy, "pages_workflow_run_id": 1001,
             "pages_deployment_id": 1002, "pages_deployment_status_id": 1003, "test_fixture": fixture}
    if stage == "ACTIVATION_OVERLAY_DEPLOYMENT":
        value["expected_live_sha256"] = {name: A.digest_bytes(raw) for name, raw in LIVE_BYTES.items()}
    return value


class FakeClient:
    is_test_transport = True

    def __init__(self, auth_body, *, policy="merge", stage="INITIAL_PAGES_DEPLOYMENT"):
        deployed = DEPLOYED if stage == "INITIAL_PAGES_DEPLOYMENT" else "3" * 40
        parents = [{"sha": "0" * 40}, {"sha": CANDIDATE}] if policy == "merge" else [{"sha": "0" * 40}]
        tree = "a" * 40
        repo = f"/repos/{A.REPOSITORY}"
        self.data = {
            f"{repo}/issues/comments/9001": {"id": 9001, "body": auth_body, "html_url": "https://example/comment",
                                                     "user": {"login": A.OWNER_LOGIN}, "author_association": "OWNER",
                                                     "issue_url": f"{A.GITHUB_API_ORIGIN}/repos/{A.REPOSITORY}/issues/{A.PR_NUMBER}",
                                                     "created_at": "2026-11-22T10:00:00Z",
                                                     "updated_at": "2026-11-22T10:00:00Z"},
            f"{repo}/pulls/{A.PR_NUMBER}": {"head": {"sha": CANDIDATE}, "base": {"sha": A.BASE_SHA},
                                              "merged": True, "merge_commit_sha": DEPLOYED,
                                              "merged_at": "2026-11-22T10:03:00Z"},
            f"{repo}/actions/runs/1001": {"name": A.PAGES_WORKFLOW_NAME, "head_sha": deployed, "head_branch": "main",
                                           "event": A.PAGES_WORKFLOW_EVENT, "path": A.PAGES_WORKFLOW_PATH,
                                           "status": "completed", "conclusion": "success",
                                           "created_at": "2026-11-22T10:05:00Z"},
            f"{repo}/deployments/1002": {"sha": deployed, "ref": "main", "environment": "github-pages"},
            f"{repo}/deployments/1002/statuses": [{"id": 1003, "state": "success",
                                                     "environment_url": "https://structurevidence.org/",
                                                     "created_at": "2026-11-22T10:10:00Z"}],
            f"{repo}/branches/main": {"commit": {"sha": deployed}},
            f"{repo}/commits/{deployed}": {"parents": parents, "commit": {"tree": {"sha": tree}}},
            f"{repo}/commits/{CANDIDATE}": {"parents": [{"sha": A.BASE_SHA}], "commit": {"tree": {"sha": tree}}},
            f"{repo}/compare/{CANDIDATE}...{DEPLOYED}": {"status": "ahead"},
            f"{repo}/compare/{DEPLOYED}...{'3' * 40}": {"status": "ahead"},
        }
        for name, path in A.LIVE_REPOSITORY_PATHS.items():
            encoded = A.urllib.parse.quote(path, safe="/")
            self.data[f"{repo}/contents/{encoded}?ref={deployed}"] = {
                "type": "file", "encoding": "base64", "sha": (name[0] * 40),
                "content": base64.b64encode(LIVE_BYTES[name]).decode(),
            }

    def get(self, path):
        if path not in self.data:
            raise ValueError(f"fabricated or unknown GitHub object: {path}")
        return self.data[path]


def live_fetch(url):
    name = next(name for name, expected in A.LIVE_RESOURCES.items() if expected == url)
    return 200, LIVE_BYTES[name], url


def verified_receipt(policy="merge"):
    auth, body = authorization()
    return A.verify_deployment_observation(request(policy), auth, FakeClient(body, policy=policy), live_fetch,
                                           now=NOW, allow_test_fixture=True)


class AnthropicPublicationActivationTest(unittest.TestCase):
    def test_01_incomplete_owner_approval_fails_closed(self):
        auth, body = authorization()
        body = body.replace("AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED=YES", "AUTOMATIC_PAGES_DEPLOYMENT_AUTHORIZED=NO")
        auth["github_comment_body_sha256"] = A.digest_bytes(body.encode())
        with self.assertRaisesRegex(ValueError, "incomplete"):
            A.verify_owner_authorization(auth, FakeClient(body), allow_test_fixture=True)

    def test_02_no_fixture_or_test_transport_passes_actual_gate(self):
        auth, body = authorization(fixture=False)
        req = request(fixture=False)
        with self.assertRaisesRegex(ValueError, "test transport"):
            A.verify_deployment_observation(req, auth, FakeClient(body), live_fetch, now=NOW)

    def test_03_fabricated_success_id_fails_closed(self):
        auth, body = authorization()
        req = request(); req["pages_deployment_status_id"] = 9999
        with self.assertRaisesRegex(ValueError, "status"):
            A.verify_deployment_observation(req, auth, FakeClient(body), live_fetch, now=NOW, allow_test_fixture=True)

    def test_04_future_deployment_fails_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        client.data[f"/repos/{A.REPOSITORY}/deployments/1002/statuses"][0]["created_at"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "future"):
            A.verify_deployment_observation(request(), auth, client, live_fetch, now=NOW, allow_test_fixture=True)

    def test_05_unrelated_main_head_fails_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        client.data[f"/repos/{A.REPOSITORY}/branches/main"]["commit"]["sha"] = "9" * 40
        with self.assertRaisesRegex(ValueError, "main HEAD"):
            A.verify_deployment_observation(request(), auth, client, live_fetch, now=NOW, allow_test_fixture=True)

    def test_06_incorrect_final_live_hash_fails_closed(self):
        auth, body = authorization("ACTIVATION_OVERLAY")
        req = request(stage="ACTIVATION_OVERLAY_DEPLOYMENT")
        req["expected_live_sha256"]["case_html"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "hash differs"):
            A.verify_deployment_observation(req, auth, FakeClient(body, stage=req["stage"]), live_fetch,
                                            now=NOW, allow_test_fixture=True)

    def test_07_merge_commit_topology_is_supported(self):
        receipt = verified_receipt("merge")
        self.assertEqual(receipt["deployed_sha"], DEPLOYED)
        self.assertEqual(receipt["status"], "DEPLOYED_PENDING_ACTIVATION_OVERLAY")

    def test_08_squash_merge_topology_is_supported(self):
        receipt = verified_receipt("squash")
        self.assertEqual(receipt["merge_policy"], "squash")

    def test_09_pending_overlay_never_claims_verified_publication(self):
        overlay = A.build_pending_overlay(ROOT, verified_receipt(), allow_test_fixture=True)
        index = json.loads(overlay[f"{A.CASE_SLUG}/index.json"])
        current = json.loads(overlay[f"{A.CASE_SLUG}/publication-current-state-v0.3.json"])
        metadata = json.loads(overlay[f"{A.CASE_SLUG}/structured-metadata-v0.2.json"])
        self.assertEqual(index["deployment_state"], "DEPLOYED_PENDING_LIVE_VERIFICATION")
        self.assertIsNone(index["structevidence_publication_date"])
        self.assertFalse(index["external_promotion_authorized"])
        self.assertEqual(current["status"], "DEPLOYED_PENDING_LIVE_VERIFICATION")
        self.assertIsNone(current["activation_overlay_deployment"])
        self.assertIsNone(current["final_live_verification"])
        self.assertEqual(metadata["creativeWorkStatus"], "DEPLOYED_PENDING_LIVE_VERIFICATION")
        self.assertIsNone(metadata["datePublished"])

    def test_10_overlay_preserves_frozen_claims_registry_and_appends_event(self):
        claims = (ROOT / A.CASE_SLUG / "claims-v0.2.jsonl").read_bytes()
        registry = (ROOT / A.CASE_SLUG / "source-registry-public-v0.2.json").read_bytes()
        events = (ROOT / A.CASE_SLUG / "events-v0.2.jsonl").read_bytes()
        overlay = A.build_pending_overlay(ROOT, verified_receipt(), allow_test_fixture=True)
        self.assertNotIn(f"{A.CASE_SLUG}/claims-v0.2.jsonl", overlay)
        self.assertNotIn(f"{A.CASE_SLUG}/source-registry-public-v0.2.json", overlay)
        self.assertEqual((ROOT / A.CASE_SLUG / "claims-v0.2.jsonl").read_bytes(), claims)
        self.assertEqual((ROOT / A.CASE_SLUG / "source-registry-public-v0.2.json").read_bytes(), registry)
        self.assertTrue(overlay[f"{A.CASE_SLUG}/events-v0.2.jsonl"].startswith(events))

    def test_11_overlay_root_docs_outputs_are_identical(self):
        overlay = A.build_pending_overlay(ROOT, verified_receipt(), allow_test_fixture=True)
        for path in [path for path in overlay if not path.startswith("docs/")]:
            self.assertEqual(overlay[path], overlay["docs/" + path], path)

    def test_12_partial_apply_rolls_back_every_touched_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, output = Path(directory) / "repo", Path(directory) / "overlay"
            repo.mkdir(); output.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            (repo / "one.txt").write_text("old-one")
            (repo / "two.txt").write_text("old-two")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            files = []
            for name, value in (("one.txt", b"new-one"), ("two.txt", b"new-two")):
                (output / name).write_bytes(value)
                files.append({"path": name, "sha256": A.digest_bytes(value), "bytes": len(value)})
            (output / "activation-manifest-v0.3.json").write_text(json.dumps({"files": files}))
            receipt = {"deployed_sha": head, "test_fixture": True}
            with self.assertRaisesRegex(OSError, "injected"):
                A.apply_overlay_transactional(repo, output, receipt, fault_after=1, allow_test_fixture=True)
            self.assertEqual((repo / "one.txt").read_text(), "old-one")
            self.assertEqual((repo / "two.txt").read_text(), "old-two")
            self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True), "")

    def test_13_real_native_pages_dynamic_workflow_is_pinned(self):
        receipt = verified_receipt()
        self.assertEqual(receipt["github"]["workflow_event"], "dynamic")
        self.assertEqual(receipt["github"]["workflow_path"], "dynamic/pages/pages-build-deployment")

    def test_14_arbitrary_workflow_event_or_path_fails_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        run = client.data[f"/repos/{A.REPOSITORY}/actions/runs/1001"]
        run["event"], run["path"] = "push", ".github/workflows/forged.yml"
        with self.assertRaisesRegex(ValueError, "pinned successful native Pages"):
            A.verify_deployment_observation(request(), auth, client, live_fetch, now=NOW, allow_test_fixture=True)

    def test_15_fake_github_api_origin_is_rejected_before_use(self):
        with self.assertRaisesRegex(ValueError, "pinned to https://api.github.com"):
            A.GitHubClient("must-not-be-sent", api_base="http://127.0.0.1:8000")

    def test_16_stale_but_http_200_live_bytes_fail_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        def stale_fetch(url):
            name = next(name for name, expected in A.LIVE_RESOURCES.items() if expected == url)
            raw = LIVE_BYTES[name] + (b" " if name == "case_html" else b"")
            return 200, raw, url
        with self.assertRaisesRegex(ValueError, "differ from deployed Git tree"):
            A.verify_deployment_observation(request(), auth, client, stale_fetch, now=NOW, allow_test_fixture=True)

    def test_17_mismatched_deployed_tree_bytes_fail_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        path = A.LIVE_REPOSITORY_PATHS["case_index_json"]
        key = f"/repos/{A.REPOSITORY}/contents/{A.urllib.parse.quote(path, safe='/')}?ref={DEPLOYED}"
        client.data[key]["content"] = base64.b64encode(LIVE_BYTES["case_index_json"] + b" ").decode()
        with self.assertRaisesRegex(ValueError, "differ from deployed Git tree"):
            A.verify_deployment_observation(request(), auth, client, live_fetch, now=NOW, allow_test_fixture=True)

    def test_18_owner_comment_on_different_issue_fails_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        client.data[f"/repos/{A.REPOSITORY}/issues/comments/9001"]["issue_url"] = (
            f"{A.GITHUB_API_ORIGIN}/repos/{A.REPOSITORY}/issues/96"
        )
        with self.assertRaisesRegex(ValueError, "not bound to PR #97"):
            A.verify_owner_authorization(auth, client, allow_test_fixture=True)

    def test_19_owner_approval_after_merge_fails_closed(self):
        auth, body = authorization(); client = FakeClient(body)
        comment = client.data[f"/repos/{A.REPOSITORY}/issues/comments/9001"]
        comment["created_at"] = comment["updated_at"] = "2026-11-22T10:04:00Z"
        with self.assertRaisesRegex(ValueError, "out of order"):
            A.verify_deployment_observation(request(), auth, client, live_fetch, now=NOW, allow_test_fixture=True)

    def test_20_overlay_source_root_on_wrong_commit_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "does not match verified deployed main SHA"):
            A.verify_source_root(ROOT, "f" * 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)

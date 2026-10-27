#!/usr/bin/env python3
"""Differential guard for historical evidence immutability (SE-ENG-HISTORY-001)."""
import argparse
import fnmatch
import json
import subprocess
from pathlib import Path

PATTERNS = (
    "data/case-watch/reviews/*.json",
    "data/case-watch/search-runs/*.json",
    "data/ops/se/runs/*.json",
    "data/ops/se/reports/*.md",
    "data/ops/se/x-candidates/*.json",
    "data/ops/se/reconciliations/*.json",
    "cases/*/search-review-*.json",
    "docs/cases/*/search-review-*.json",
    "cases/*/events/*/index.json",
    "docs/cases/*/events/*/index.json",
    "cases/*/events/*/snapshot*.json",
    "docs/cases/*/events/*/snapshot*.json",
    "cases/*/state-v*.json",
    "docs/cases/*/state-v*.json",
    "cases/iren-ai-cloud-transition/events-v*.json",
    "docs/cases/iren-ai-cloud-transition/events-v*.json",
    "cases/iren-ai-cloud-transition/publication-approval-v*.json",
    "docs/cases/iren-ai-cloud-transition/publication-approval-v*.json",
    "release/SE-IREN-TRACKER-PUBLIC-MVP-001/PUBLICATION_RECEIPT*.json",
    "cases/ekn-necessity/case.md",
    "docs/cases/ekn-necessity/case.md",
)
IDENTITY_PATTERNS = {
    "review": ("data/case-watch/reviews/*.json", "cases/*/search-review-*.json"),
    "event": ("cases/*/events/*/index.json",),
}
def protected(path):
    return any(fnmatch.fnmatchcase(path, p) for p in PATTERNS)
def identity_kind(path):
    return next((k for k, ps in IDENTITY_PATTERNS.items()
                 if any(fnmatch.fnmatchcase(path, p) for p in ps)), None)
def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()
def compare(base, head="HEAD"):
    raw = subprocess.check_output(["git", "diff", "--name-status", "-z", "--find-renames",
                                   base + "..." + head]).decode().split("\0")
    if raw[-1:] == [""]: raw.pop()
    errors, additions = [], []
    i = 0
    while i < len(raw):
        status, old = raw[i], raw[i+1]
        new = raw[i+2] if status[0] in "RC" else None
        i += 3 if new else 2
        if status[0] in "MDRTC" and (protected(old) or (new and protected(new))):
            errors.append("IMMUTABLE_RECORD_MUTATION " + status + " " + old)
        if status[0] == "A" and protected(old):
            additions.append(old)
    newids = {}
    for path in additions:
        kind = identity_kind(path)
        if not kind: continue
        record = json.loads(Path(path).read_text())
        idfield = "review_id" if kind == "review" else "event_id"
        ident = record.get(idfield)
        if not ident: errors.append("MISSING_ID " + path); continue
        newids.setdefault((kind, ident), []).append((path, record))
    baseline = git("ls-tree", "-r", "--name-only", base).splitlines()
    for path in baseline:
        kind = identity_kind(path)
        if kind is None: continue
        record = json.loads(git("show", base + ":" + path))
        idfield = "review_id" if kind == "review" else "event_id"
        key = (kind, record.get(idfield))
        for newpath, newrecord in newids.get(key, []):
            if kind == "event":
                errors.append("EVENT_ID_REUSED " + str(key[1]) + " " + path + " " + newpath)
            else:
                keys = ("case_id", "review_id", "reviewed_at", "result", "search_boundary")
                clashes = [k for k in keys if k in record and k in newrecord
                           and record[k] != newrecord[k]]
                if clashes: errors.append("REVIEW_ID_COLLISION " + str(key[1]) + " " + ",".join(clashes))
    for key, rows in newids.items():
        if len(rows) > 1 and key[0] == "event":
            errors.append("EVENT_ID_REUSED_WITHIN_PR " + str(key[1]))
        elif len(rows) > 1:
            keys = ("case_id", "review_id", "reviewed_at", "result", "search_boundary")
            for _, record in rows[1:]:
                first = rows[0][1]
                if any(k in first and k in record and first[k] != record[k] for k in keys):
                    errors.append("REVIEW_ID_COLLISION_WITHIN_PR " + str(key[1]))
    return errors
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    args = ap.parse_args()
    result = compare(args.base, args.head)
    for error in result: print(error)
    print("SE_HISTORY_GUARD = " + ("PASS" if not result else "FAIL"))
    raise SystemExit(bool(result))

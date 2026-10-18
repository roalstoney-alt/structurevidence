"""SE-ENG-HISTORY-001 policy guard self tests."""
import tempfile
import subprocess
import json
import os
import unittest
from pathlib import Path
from scripts.guard_history_immutability import compare

class HistoryGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old = os.getcwd()
        self.addCleanup(os.chdir, self.old)
        os.chdir(self.tmp.name)
        self.cmd("init","-q")
        self.cmd("config","user.email","test@example.invalid")
        self.cmd("config","user.name","Test")
        self.write("data/case-watch/reviews/2026-10-17/first.json", self.review("R1","original"))
        self.cmd("add","."); self.cmd("commit","-qm","baseline")
        self.base = self.cmd("rev-parse","HEAD")
    def cmd(self,*args):
        return subprocess.check_output(["git",*args],text=True).strip()
    def write(self,path,obj):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(obj)+"\n")
    def review(self,ident,scope):
        return {"review_id":ident,"case_id":"CML-PDRE-001","reviewed_at":"2026-10-17T14:00:00Z","result":"NO_STATE_CHANGE","search_boundary":scope}
    def check(self):
        self.cmd("add",".");self.cmd("commit","-qm","candidate")
        return compare(self.base)
    def test_append_new_review(self):
        self.write("data/case-watch/reviews/2026-10-18/next.json",self.review("R2","new"))
        self.assertEqual(self.check(),[])
    def test_block_overwrite(self):
        self.write("data/case-watch/reviews/2026-10-17/first.json",self.review("R1","changed"))
        self.assertIn("IMMUTABLE_RECORD_MUTATION",str(self.check()))
    def test_block_conflicting_id(self):
        self.write("data/case-watch/reviews/2026-10-18/next.json",self.review("R1","different"))
        self.assertIn("REVIEW_ID_COLLISION",str(self.check()))
    def test_allow_projection(self):
        self.write("cases/review-status.json",{"projection":"recomputed"})
        self.assertEqual(self.check(),[])
    def test_allow_same_observation_reference(self):
        self.write("cases/800vdc/search-review-20261017-01.json",self.review("R1","original"))
        self.assertEqual(self.check(),[])
    def test_block_reused_event_id(self):
        self.write("cases/800vdc/events/a/index.json",{"event_id":"EV1"})
        self.cmd("add","."); self.cmd("commit","-qm","event-baseline")
        self.base=self.cmd("rev-parse","HEAD")
        self.write("cases/800vdc/events/b/index.json",{"event_id":"EV1"})
        self.assertIn("EVENT_ID_REUSED",str(self.check()))

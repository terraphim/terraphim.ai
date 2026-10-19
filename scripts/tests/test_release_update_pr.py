#!/usr/bin/env python3
"""Deterministic request-plan tests for scripts/release_update_pr.py.

An injected transport records the exact request sequence and returns
scripted responses. No mock GitHub service: live integration is a
separate gate."""
import http.server
import sys
import threading
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import release_update_pr as pr  # noqa: E402
import update_release as u  # noqa: E402

REPO = "terraphim/terraphim-clients"
MAIN_SHA = "a" * 40
PROPOSAL_SHA = "b" * 40
FOREIGN_SHA = "c" * 40
NEW_COMMIT = "d" * 40


def plan(changed=True):
    f = u.PlannedFile(path="README.md", original_sha256="0" * 64,
                      proposed_sha256=("1" if changed else "0") * 64,
                      proposed_bytes=b"readme bytes")
    return u.UpdatePlan(target="terraphim-clients",
                        checked_at="2026-10-18T00:00:00Z",
                        admitted={"clients": "v1.21.22"}, files=(f,))


class FakeTransport:
    """Records requests; responds from a scripted table."""

    def __init__(self):
        self.calls: list = []
        self.responses: dict = {}
        self.not_found: set = set()

    def set(self, key, value):
        self.responses[key] = value

    def __call__(self, req: pr.Request):
        self.calls.append(req)
        if req.graphql:
            if "errors" in self.responses:
                return {"errors": self.responses["errors"]}
            return {"data": {"createCommitOnBranch":
                             {"commit": {"oid": NEW_COMMIT, "url": "u"}}}}
        key = (req.method, req.url.split("?")[0])
        if key in self.not_found:
            raise RuntimeError(f"{req.method} {req.url} -> HTTP 404: not found")
        if key in self.responses:
            return self.responses[key]
        raise AssertionError(f"unscripted request {req.method} {req.url}")


def base_transport(t: FakeTransport,
                   branch_head: Optional[str] = None,
                   branch_actor: str = pr.EXPECTED_ACTOR,
                   verified: bool = True,
                   open_pr: Optional[dict] = None):
    t.set(("GET", f"/repos/{REPO}"), {"default_branch": "main"})
    if branch_head is None:
        t.not_found.add(("GET", f"/repos/{REPO}/git/ref/heads/{pr.UPDATE_BRANCH}"))
        t.set(("GET", f"/repos/{REPO}/git/ref/heads/main"),
              {"object": {"sha": MAIN_SHA}})
        t.set(("POST", f"/repos/{REPO}/git/refs"), {})
    else:
        t.set(("GET", f"/repos/{REPO}/git/ref/heads/{pr.UPDATE_BRANCH}"),
              {"object": {"sha": branch_head}})
        t.set(("GET", f"/repos/{REPO}/commits/{branch_head}"),
              {"author": {"login": branch_actor}})
    head = branch_head or MAIN_SHA
    t.set(("GET", f"/repos/{REPO}/contents/README.md"),
          {"sha": "f" * 40})
    t.set(("PUT", f"/repos/{REPO}/contents/README.md"),
          {"commit": {"sha": NEW_COMMIT}})
    t.set(("GET", f"/repos/{REPO}/commits/{NEW_COMMIT}"),
          {"parents": [{"sha": head}],
           "verification": {"verified": verified,
                            "reason": "valid" if verified else "unsigned"}})
    t.set(("GET", f"/repos/{REPO}/pulls"),
          [open_pr] if open_pr else [])
    t.set(("POST", f"/repos/{REPO}/pulls"),
          {"number": 7, "html_url": "https://github.com/x/pull/7"})
    t.set(("POST", f"/repos/{REPO}/issues/7/labels"), {})
    t.set(("POST", f"/repos/{REPO}/actions/workflows/ci.yml/dispatches"), {})
    t.set(("POST", f"/repos/{REPO}/issues/7/comments"), {})


def our_pr(number=7):
    """An open updater PR as the API returns it: labelled, sentinel body."""
    return {"number": number, "html_url": f"https://x/{number}",
            "base": {"ref": "main"},
            "labels": [{"name": pr.PR_LABEL}], "body": pr.PR_SENTINEL}


class ProposalTests(unittest.TestCase):
    def test_new_branch_proposal(self):
        t = FakeTransport()
        base_transport(t, branch_head=None)
        r = pr.propose_update(REPO, plan(), transport=t,
                              require_signed=True,
                              validation_workflow="ci.yml")
        self.assertEqual(r.outcome, "proposed")
        self.assertEqual(r.commit_sha, NEW_COMMIT)
        self.assertTrue(r.commit_verified)
        self.assertEqual(r.pr_number, 7)
        self.assertEqual(r.dispatched_workflows, ["ci.yml"])

    def test_reuse_existing_pr(self):
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA, open_pr=our_pr())
        r = pr.propose_update(REPO, plan(), transport=t)
        self.assertEqual(r.outcome, "reused")
        self.assertEqual(r.pr_number, 7)
        # no POST /pulls was issued
        self.assertFalse(any(c.method == "POST" and c.url.endswith("/pulls")
                             for c in t.calls))

    def test_expected_head_mismatch_refuses_and_comments(self):
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA, open_pr=our_pr())
        r = pr.propose_update(REPO, plan(), expected_head="9" * 40,
                              transport=t)
        self.assertEqual(r.outcome, "refused")
        self.assertIn("moved", r.reason)
        self.assertTrue(any(c.method == "POST" and "comments" in c.url
                            for c in t.calls))
        self.assertFalse(any(c.graphql for c in t.calls))

    def test_foreign_actor_refuses_and_comments(self):
        t = FakeTransport()
        base_transport(t, branch_head=FOREIGN_SHA, branch_actor="alice",
                       open_pr=our_pr())
        r = pr.propose_update(REPO, plan(), transport=t)
        self.assertEqual(r.outcome, "refused")
        self.assertIn("unexpected actor", r.reason)
        self.assertTrue(any(c.method == "POST" and "comments" in c.url
                            for c in t.calls))
        self.assertFalse(any(c.graphql for c in t.calls))

    def test_unsigned_commit_refused_when_required(self):
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA, verified=False)
        r = pr.propose_update(REPO, plan(), transport=t, require_signed=True)
        self.assertEqual(r.outcome, "refused")
        self.assertFalse(r.commit_verified)
        self.assertFalse(any(c.method == "POST" and c.url.endswith("/pulls")
                             for c in t.calls))

    def test_unsigned_commit_allowed_without_requirement(self):
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA, verified=False)
        r = pr.propose_update(REPO, plan(), transport=t, require_signed=False)
        self.assertEqual(r.outcome, "proposed")

    def test_no_change_plan_no_requests(self):
        t = FakeTransport()
        r = pr.propose_update(REPO, plan(changed=False), transport=t)
        self.assertEqual(r.outcome, "unchanged")
        self.assertEqual(t.calls, [])

    def test_expected_head_blocks_branch_creation(self):
        # branch absent but the recorded base head has moved: refuse before
        # creating the update branch
        t = FakeTransport()
        base_transport(t, branch_head=None)
        r = pr.propose_update(REPO, plan(), expected_head="9" * 40,
                              transport=t)
        self.assertEqual(r.outcome, "refused")
        self.assertIn("not created", r.reason)
        self.assertFalse(any(c.method == "POST" and "git/refs" in c.url
                             for c in t.calls))
        self.assertFalse(any(c.graphql for c in t.calls))

    def test_foreign_pr_not_reused(self):
        # an open PR on the same branch without our label/sentinel is not
        # adopted: a fresh labelled PR is created instead
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA,
                       open_pr={"number": 42, "html_url": "https://x/42",
                                "base": {"ref": "main"},
                                "labels": [], "body": "human work"})
        r = pr.propose_update(REPO, plan(), transport=t)
        self.assertEqual(r.outcome, "proposed")
        self.assertEqual(r.pr_number, 7)
        self.assertTrue(any(c.method == "POST" and c.url.endswith("/pulls")
                            for c in t.calls))
        self.assertTrue(any(c.method == "POST" and "labels" in c.url
                            for c in t.calls))

    def test_single_file_commit_via_contents_api(self):
        # single-file plans commit via PUT /contents (GitHub-signed) with
        # base64 content and the file sha on the update branch
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA)
        pr.propose_update(REPO, plan(), transport=t)
        put = next(c for c in t.calls if c.method == "PUT")
        self.assertEqual(put.url, f"/repos/{REPO}/contents/README.md")
        self.assertEqual(put.body["branch"], pr.UPDATE_BRANCH)
        self.assertEqual(put.body["sha"], "f" * 40)
        import base64
        self.assertEqual(base64.b64decode(put.body["content"]), b"readme bytes")
        self.assertFalse(any(c.graphql for c in t.calls))

    def test_parent_mismatch_after_contents_commit_refuses(self):
        # a moved branch between the head check and the PUT is caught by the
        # parent readback and refused
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA)
        t.set(("GET", f"/repos/{REPO}/commits/{NEW_COMMIT}"),
              {"parents": [{"sha": "0" * 40}],
               "verification": {"verified": True, "reason": "valid"}})
        r = pr.propose_update(REPO, plan(), transport=t, require_signed=True)
        self.assertEqual(r.outcome, "refused")
        self.assertIn("moved", r.reason)
        self.assertFalse(any(c.method == "POST" and c.url.endswith("/pulls")
                             for c in t.calls))

    def test_multi_file_signed_plan_refuses(self):
        f1 = u.PlannedFile(path="README.md", original_sha256="0" * 64,
                           proposed_sha256="1" * 64, proposed_bytes=b"a")
        f2 = u.PlannedFile(path="OTHER.md", original_sha256="0" * 64,
                           proposed_sha256="1" * 64, proposed_bytes=b"b")
        p = u.UpdatePlan(target="terraphim-clients",
                         checked_at="2026-10-18T00:00:00Z",
                         admitted={"clients": "v1.21.22"}, files=(f1, f2))
        t = FakeTransport()
        base_transport(t, branch_head=PROPOSAL_SHA)
        r = pr.propose_update(REPO, p, transport=t, require_signed=True)
        self.assertEqual(r.outcome, "refused")
        self.assertIn("one", r.reason)


class TransportTests(unittest.TestCase):
    def test_live_transport_refuses_redirects(self):
        # a 3xx from the API base must surface as an error rather than be
        # followed with the bearer token to the redirect target
        seen = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(dict(self.headers))
                self.send_response(301)
                self.send_header("Location", "http://127.0.0.1:1/other")
                self.end_headers()

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        t = pr.live_transport("secret-token",
                              api_base=f"http://127.0.0.1:{srv.server_port}")
        with self.assertRaises(RuntimeError) as cm:
            t(pr.Request("GET", "/repos/x"))
        self.assertIn("301", str(cm.exception))


if __name__ == "__main__":
    unittest.main()

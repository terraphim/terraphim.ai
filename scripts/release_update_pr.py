#!/usr/bin/env python3
"""Own-repository GraphQL commit/PR orchestration for the release updater.

Builds the proposal as an explicit request plan executed through an
injectable transport, so tests exercise the exact request sequence
without a mock GitHub service and live integration stays a separate gate.

Safety contract (spec section 8):
- expected-head concurrency on createCommitOnBranch; never force-push
- verified signature required before the PR is opened/updated when
  require_signed=True (terraphim-clients)
- unexpected branch state (moved head or foreign actor) -> refuse + comment
- existing open PR is reused; no duplicates
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

GRAPHQL_URL = "https://api.github.com/graphql"
API_BASE = "https://api.github.com"
USER_AGENT = "terraphim-release-updater/1 (+https://terraphim.ai)"

UPDATE_BRANCH = "bot/release-updater"
PR_TITLE = "chore(release): update release links (auto)"
PR_SENTINEL = "<!-- release-updater:managed -->"
PR_LABEL = "release-updater"
EXPECTED_ACTOR = "github-actions[bot]"

COMMIT_MUTATION = """mutation($input: CreateCommitOnBranchInput!) {
  createCommitOnBranch(input: $input) {
    commit { oid url }
  }
}"""


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    body: Optional[dict] = None
    graphql: bool = False


@dataclass
class ProposalReceipt:
    receiptType: str = "proposal"
    repository: str = ""
    outcome: str = "pending"  # proposed|reused|refused|failed
    reason: str = ""
    branch: str = UPDATE_BRANCH
    commit_sha: Optional[str] = None
    commit_verified: Optional[bool] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    dispatched_workflows: list = field(default_factory=list)


Transport = Callable[[Request], Any]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects: following them would forward the bearer token to
    whatever host the redirect names."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def live_transport(token: str, timeout: int = 30,
                   api_base: str = API_BASE,
                   graphql_url: str = GRAPHQL_URL) -> Transport:
    """api_base/graphql_url are injectable for tests; production uses the
    GitHub constants."""
    def call(req: Request) -> Any:
        url = graphql_url if req.graphql else f"{api_base}{req.url}"
        data = json.dumps(req.body).encode() if req.body is not None else None
        r = urllib.request.Request(url, data=data, method=req.method, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        })
        try:
            with _OPENER.open(r, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"{req.method} {url} -> HTTP {e.code}: {body[:400]}") from e
    return call


def _get_branch_head(t: Transport, repo: str, branch: str) -> Optional[str]:
    try:
        ref = t(Request("GET", f"/repos/{repo}/git/ref/heads/{branch}"))
        return ref["object"]["sha"]
    except RuntimeError as e:
        if "404" in str(e):
            return None
        raise


def _commit_actor(t: Transport, repo: str, sha: str) -> str:
    c = t(Request("GET", f"/repos/{repo}/commits/{sha}"))
    return (c.get("author") or {}).get("login") or \
        (c.get("committer") or {}).get("login") or ""


def _default_branch(t: Transport, repo: str) -> str:
    return t(Request("GET", f"/repos/{repo}"))["default_branch"]


def _head_sha(t: Transport, repo: str, branch: str) -> str:
    ref = t(Request("GET", f"/repos/{repo}/git/ref/heads/{branch}"))
    return ref["object"]["sha"]


def _create_branch(t: Transport, repo: str, branch: str, sha: str) -> None:
    t(Request("POST", f"/repos/{repo}/git/refs",
              {"ref": f"refs/heads/{branch}", "sha": sha}))


def _create_commit(t: Transport, repo: str, branch: str, expected_head: str,
                   message: str, additions: list) -> str:
    variables = {"input": {
        "branch": {"repositoryNameWithOwner": repo, "branchName": branch},
        "message": {"headline": message},
        "expectedHeadOid": expected_head,
        "fileChanges": {"additions": [
            {"path": p, "contents": base64.b64encode(b).decode()}
            for p, b in additions
        ]},
    }}
    resp = t(Request("POST", "", {"query": COMMIT_MUTATION, "variables": variables},
                     graphql=True))
    errors = resp.get("errors")
    if errors:
        raise RuntimeError(f"createCommitOnBranch failed: {errors[0].get('message')}")
    return resp["data"]["createCommitOnBranch"]["commit"]["oid"]


def _commit_verified(t: Transport, repo: str, sha: str) -> bool:
    c = t(Request("GET", f"/repos/{repo}/commits/{sha}"))
    v = c.get("verification") or {}
    return bool(v.get("verified")) and v.get("reason") == "valid"


def _commit_parents(t: Transport, repo: str, sha: str) -> list:
    c = t(Request("GET", f"/repos/{repo}/commits/{sha}"))
    return [p["sha"] for p in c.get("parents", [])]


def _file_sha_on_branch(t: Transport, repo: str, path: str,
                        branch: str) -> Optional[str]:
    try:
        f = t(Request("GET", f"/repos/{repo}/contents/{path}?ref={branch}"))
        return f.get("sha")
    except RuntimeError as e:
        if "404" in str(e):
            return None
        raise


def _commit_via_contents(t: Transport, repo: str, branch: str, path: str,
                         content: bytes, file_sha: str, message: str) -> str:
    """Signed single-file commit via the REST Contents API: commits created
    through this endpoint are auto-signed by GitHub's web-flow key, unlike
    createCommitOnBranch which produces unsigned commits."""
    resp = t(Request("PUT", f"/repos/{repo}/contents/{path}", {
        "message": message,
        "content": base64.b64encode(content).decode(),
        "sha": file_sha,
        "branch": branch,
    }))
    return resp["commit"]["sha"]


def _is_our_pr(pr: dict, base: Optional[str]) -> bool:
    """Only reuse/comment on PRs we created: labelled or sentinel-bodied,
    and targeting the expected base branch."""
    if base is not None and (pr.get("base") or {}).get("ref") != base:
        return False
    labels = {l.get("name") for l in pr.get("labels") or []}
    return PR_LABEL in labels or PR_SENTINEL in (pr.get("body") or "")


def _find_open_pr(t: Transport, repo: str, branch: str,
                  base: Optional[str] = None) -> Optional[dict]:
    owner = repo.split("/")[0]
    prs = t(Request("GET", f"/repos/{repo}/pulls?head={owner}:{branch}&state=open"))
    for pr in prs:
        if _is_our_pr(pr, base):
            return pr
    return None


def _create_pr(t: Transport, repo: str, branch: str, title: str, body: str,
               base: str) -> dict:
    if PR_SENTINEL not in body:
        body = body + "\n\n" + PR_SENTINEL
    pr = t(Request("POST", f"/repos/{repo}/pulls",
                   {"title": title, "head": branch, "base": base, "body": body}))
    try:
        t(Request("POST", f"/repos/{repo}/issues/{pr['number']}/labels",
                  {"labels": [PR_LABEL]}))
    except RuntimeError:
        pass  # labelling is best-effort; the body sentinel still identifies it
    return pr


def _comment(t: Transport, repo: str, pr_number: int, body: str) -> None:
    t(Request("POST", f"/repos/{repo}/issues/{pr_number}/comments",
              {"body": body}))


def _dispatch(t: Transport, repo: str, workflow: str, ref: str) -> None:
    t(Request("POST", f"/repos/{repo}/actions/workflows/{workflow}/dispatches",
              {"ref": ref}))


def propose_update(repo: str, plan, expected_head: Optional[str] = None,
                   transport: Optional[Transport] = None,
                   require_signed: bool = False,
                   validation_workflow: Optional[str] = None,
                   expected_actor: str = EXPECTED_ACTOR,
                   pr_body: str = "") -> ProposalReceipt:
    """Create or reuse the update branch + PR for `plan` (an UpdatePlan).

    transport is required; use live_transport(token) in workflows.
    """
    t = transport or live_transport(os.environ["GITHUB_TOKEN"])
    r = ProposalReceipt(repository=repo)
    additions = [(f.path, f.proposed_bytes) for f in plan.files
                 if f.original_sha256 != f.proposed_sha256]
    if not additions:
        r.outcome = "unchanged"
        r.reason = "plan produced no byte changes"
        return r

    base = _default_branch(t, repo)
    head = _get_branch_head(t, repo, UPDATE_BRANCH)

    if head is None:
        base_sha = _head_sha(t, repo, base)
        if expected_head is not None and base_sha != expected_head:
            r.outcome = "refused"
            r.reason = (f"default branch {base_sha[:10]} moved from expected "
                        f"{expected_head[:10]}; update branch not created")
            return r
        _create_branch(t, repo, UPDATE_BRANCH, base_sha)
        head = base_sha
    else:
        # Branch exists: only our own proposal commits are acceptable.
        if _commit_actor(t, repo, head) != expected_actor:
            r.outcome = "refused"
            r.reason = f"update branch head {head[:10]} authored by unexpected actor"
            pr = _find_open_pr(t, repo, UPDATE_BRANCH, base)
            if pr:
                r.pr_number, r.pr_url = pr["number"], pr["html_url"]
                _comment(t, repo, pr["number"],
                         "Release updater refused to write: the update branch "
                         "contains commits from an unexpected actor. "
                         "A human must resolve the branch state.")
            return r
        if expected_head is not None and head != expected_head:
            r.outcome = "refused"
            r.reason = (f"branch head {head[:10]} moved from expected "
                        f"{expected_head[:10]}")
            pr = _find_open_pr(t, repo, UPDATE_BRANCH, base)
            if pr:
                r.pr_number, r.pr_url = pr["number"], pr["html_url"]
                _comment(t, repo, pr["number"],
                         "Release updater refused to write: the update branch "
                         "head moved since the proposal snapshot. "
                         "A human must resolve.")
            return r

    message = f"chore(release): update release links ({plan.checked_at[:10]})"
    if len(additions) == 1:
        # signed commit via the REST Contents API (web-flow signature)
        path, content = additions[0]
        file_sha = _file_sha_on_branch(t, repo, path, UPDATE_BRANCH)
        if file_sha is None:
            r.outcome = "refused"
            r.reason = f"{path} absent on {UPDATE_BRANCH}; cannot sign update"
            return r
        commit_sha = _commit_via_contents(
            t, repo, UPDATE_BRANCH, path, content, file_sha, message)
        r.commit_sha = commit_sha
        # Contents API has no expectedHeadOid; prove the new commit sits
        # directly on the head we checked
        if _commit_parents(t, repo, commit_sha) != [head]:
            r.outcome = "refused"
            r.reason = (f"commit {commit_sha[:10]} landed on a moved branch "
                        f"head (expected {head[:10]})")
            return r
    else:
        if require_signed:
            r.outcome = "refused"
            r.reason = (f"signed commits via the Contents API support one "
                        f"file per run; plan touches {len(additions)} files")
            return r
        commit_sha = _create_commit(
            t, repo, UPDATE_BRANCH, head, message, additions)
        r.commit_sha = commit_sha

    verified = _commit_verified(t, repo, commit_sha)
    r.commit_verified = verified
    if require_signed and not verified:
        r.outcome = "refused"
        r.reason = ("commit signature verification failed; "
                    "no unsigned PR admitted")
        return r

    pr = _find_open_pr(t, repo, UPDATE_BRANCH, base)
    reused = pr is not None
    if not pr:
        body = pr_body or _default_body(plan, commit_sha)
        pr = _create_pr(t, repo, UPDATE_BRANCH, PR_TITLE, body, base)
    r.pr_number, r.pr_url = pr["number"], pr["html_url"]

    if validation_workflow:
        try:
            _dispatch(t, repo, validation_workflow, UPDATE_BRANCH)
            r.dispatched_workflows.append(validation_workflow)
        except RuntimeError as e:
            r.dispatched_workflows.append(f"{validation_workflow}:FAILED:{e}")

    r.outcome = "reused" if reused else "proposed"
    return r


def _default_body(plan, commit_sha: str) -> str:
    rows = "\n".join(
        f"| `{f.path}` | `{f.original_sha256[:12]}` | `{f.proposed_sha256[:12]}` |"
        for f in plan.files)
    admitted = ", ".join(f"{n} {t}" for n, t in sorted(plan.admitted.items()))
    return (
        "Automated release-link update.\n\n"
        f"Admitted inputs: {admitted}\n\n"
        "| Path | Before | After |\n| --- | --- | --- |\n" + rows +
        f"\n\nCommit: `{commit_sha}`\n\n"
        "Generated by `scripts/update_release.py`. Review required before merge."
    )


# ---------------------------------------------------------------------------
# CLI: re-derive the plan from a snapshot artifact and propose it.


def _cli(argv=None) -> int:
    import argparse
    from pathlib import Path as _P
    import update_release as u

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="owner/name target repository")
    ap.add_argument("--snapshot", required=True, help="ReleaseSnapshot JSON artifact")
    ap.add_argument("--root", default=".", help="checkout root for plan derivation")
    ap.add_argument("--target", default="website",
                    choices=[t.value for t in __import__("update_release").TargetRepository])
    ap.add_argument("--validation-workflow", help="workflow file to dispatch at the branch")
    ap.add_argument("--require-signed", action="store_true",
                    help="refuse the PR unless the created commit verifies")
    ap.add_argument("--expected-head", help="expected bot branch head SHA")
    ap.add_argument("--receipt", help="write proposal receipt JSON here")
    args = ap.parse_args(argv)

    snap = u.load_snapshot(_P(args.snapshot))
    plan = u.plan_updates(_P(args.root), u.TargetRepository(args.target), snap)
    receipt = propose_update(
        repo=args.repo, plan=plan, expected_head=args.expected_head,
        require_signed=args.require_signed,
        validation_workflow=args.validation_workflow)
    import dataclasses as _dc, json as _json
    body = _dc.asdict(receipt)
    if args.receipt:
        _P(args.receipt).write_text(_json.dumps(body, indent=2) + "\n")
    print(_json.dumps({k: body[k] for k in
                       ("outcome", "reason", "commit_sha", "commit_verified",
                        "pr_number", "pr_url")}))
    return 0 if receipt.outcome in ("proposed", "reused", "unchanged") else 2


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(_cli())

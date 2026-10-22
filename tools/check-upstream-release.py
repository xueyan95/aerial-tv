#!/usr/bin/env python3
"""Prepare a candidate merge without executing code from the upstream release."""
import json
import os
import re
import subprocess
from pathlib import Path

def call(*args, check=True):
    return subprocess.run(args, text=True, capture_output=True, check=check)
def gh(*args):
    return call("gh", *args).stdout.strip()
def git(*args, check=True):
    return call("git", *args, check=check)

release = json.loads(gh("api", "repos/pengchujin/aerial-tv/releases/latest"))
tag = release["tag_name"]
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", tag):
    raise RuntimeError("Unexpected upstream tag format")
branch = "update/upstream-" + tag
existing = json.loads(gh("pr", "list", "--state", "all", "--head", branch, "--json", "url"))
if existing:
    print("Already tracked:", existing[0]["url"])
    raise SystemExit(0)
git("config", "user.name", "github-actions[bot]")
git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
git("fetch", "https://github.com/pengchujin/aerial-tv.git", "refs/tags/" + tag)
upstream = git("rev-parse", "FETCH_HEAD^{commit}").stdout.strip()
if git("merge-base", "--is-ancestor", upstream, "HEAD", check=False).returncode == 0:
    print("Upstream release already included:", tag)
    raise SystemExit(0)
git("checkout", "-B", branch)
merge = git("merge", "--no-edit", upstream, check=False)
conflicts = []
if merge.returncode:
    conflicts = git("diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    git("merge", "--abort")
    if not conflicts:
        raise RuntimeError(merge.stderr)
    Path("docs/upstream-pending.md").write_text(
        "# Pending upstream release " + tag + "\n\nCommit: `" + upstream + "`\n\n"
        "Merge conflicts require review. No upstream code has been merged or device updated.\n\n" +
        "\n".join("- `" + name + "`" for name in conflicts) + "\n")
    git("add", "docs/upstream-pending.md")
    git("commit", "-m", "Record conflicts for upstream " + tag)
git("push", "origin", "HEAD:refs/heads/" + branch)
body = ("Upstream release: " + release["html_url"] + "\n\nPinned upstream commit: `" + upstream +
        "`\n\n" + ("Merge blocked by conflicts; this draft records the files requiring manual resolution." if conflicts else
        "Candidate merge prepared. Compilation does not establish projector compatibility.") +
        "\n\nPreserve Hisense package/signing identity, Direct Boot HOME and HDMI panel. Do not deploy until reviewed and tested.")
args = ["pr", "create", "--base", "hisense-c1", "--head", branch, "--title", "Adapt upstream " + tag, "--body", body]
if conflicts:
    args.append("--draft")
url = gh(*args)
print(url)
if not conflicts:
    gh("workflow", "run", "hisense-build.yml", "--ref", branch)

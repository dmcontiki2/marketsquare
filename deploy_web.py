#!/usr/bin/env python3
"""
deploy_web.py — trigger a live MarketSquare deploy from ANY session, over the web.

This is the client half of Phase 3 "automated deploy". It replaces "a human runs
deploy_marketsquare.bat" with one command that works from a cloud Cowork session
(which has no ssh, no server key, and — in a scheduled/headless run — no push
rights to the mirror). It picks the best trigger available and VERIFIES the result,
and it is honest when it cannot deploy rather than pretending it did.

It tries, in order:
  1. HTTPS hook   — POST {site}/admin/deploy with X-Deploy-Token, if MS_DEPLOY_TOKEN
                    is present in this session's environment. Immediate. (needs the
                    optional deploy_router.py enabled on the server.)
  2. git push     — push the current commit to the deploy ref on the mirror; the
                    server's 2-minute poller picks it up. (needs push rights.)
  3. neither      — print EXACTLY what is missing and the single grant that fixes it.

Then it polls the live site's /health and compares the live ms.js to your local
build so you know the deploy actually landed.

Usage:
    python3 deploy_web.py                 # auto: try hook, then git push
    python3 deploy_web.py --check         # just report which trigger is available
    python3 deploy_web.py --ref deploy    # deploy ref the server tracks (default: deploy)
    python3 deploy_web.py --no-verify     # skip the post-deploy live check

No secret is stored by this script. The token, if used, is read from the
environment at call time and never written anywhere.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

SITE = os.environ.get("MS_SITE", "https://trustsquare.co")
DEFAULT_REF = os.environ.get("MS_DEPLOY_REF", "deploy")
DEFAULT_REMOTE = os.environ.get("MS_REMOTE", "origin")


def _http(method, url, headers=None, timeout=25):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def repo_root():
    rc, out = _run(["git", "rev-parse", "--show-toplevel"])
    return out if rc == 0 else os.getcwd()


def local_head():
    rc, out = _run(["git", "rev-parse", "HEAD"])
    return out if rc == 0 else "(unknown)"


def md5_of_bytes(b):
    return hashlib.md5(b).hexdigest()


def md5_of_file(path):
    try:
        with open(path, "rb") as f:
            return md5_of_bytes(f.read())
    except OSError:
        return None


# ── Trigger paths ────────────────────────────────────────────────────────────
def try_hook():
    """Return (ok, message). ok True means a deploy was started via the HTTPS hook."""
    token = os.environ.get("MS_DEPLOY_TOKEN", "")
    if not token:
        return None, "no MS_DEPLOY_TOKEN in this session (HTTPS hook not usable here)"
    status, body = _http("POST", f"{SITE}/admin/deploy", headers={"X-Deploy-Token": token})
    if status == 202 or status == 200:
        return True, f"HTTPS hook accepted the deploy ({status})."
    if status == 503:
        return False, "HTTPS hook is present but DISABLED on the server (MS_DEPLOY_TOKEN not set there)."
    if status in (401, 403):
        return False, f"HTTPS hook rejected the token ({status}). Token mismatch."
    return False, f"HTTPS hook call failed: {status} {body[:200]}"


def try_git_push(remote, ref):
    """Return (ok, message). Pushes current HEAD to the deploy ref on the mirror."""
    head = local_head()
    rc, out = _run(["git", "push", remote, f"HEAD:refs/heads/{ref}"])
    if rc == 0:
        return True, f"pushed {head[:8]} → {remote}/{ref}. The server poller (≤2 min) will deploy it."
    low = out.lower()
    if "403" in out or "permission" in low or "denied" in low or "unable to access" in low or "authentication" in low:
        return False, f"git push is NOT permitted from this session:\n    {out.strip()[:300]}"
    if "everything up-to-date" in low or "up to date" in low:
        return True, f"{remote}/{ref} already points at this commit — nothing new to push (already requested)."
    return False, f"git push failed:\n    {out.strip()[:300]}"


# ── Verification ─────────────────────────────────────────────────────────────
def verify(timeout_s, root):
    print(f"\n  Verifying against {SITE} …")
    deadline = time.time() + timeout_s
    healthy = False
    while time.time() < deadline:
        status, body = _http("GET", f"{SITE}/health", timeout=10)
        if status == 200 and '"status":"ok"' in body.replace(" ", ""):
            healthy = True
            print(f"  ✓ {SITE}/health → 200 ok")
            break
        time.sleep(5)
    if not healthy:
        print(f"  ✗ {SITE}/health did not report ok within {timeout_s}s — check the deploy log on the server.")
        return False

    # Compare the live ms.js to the local build (does the current build appear live?)
    local_js = md5_of_file(os.path.join(root, "ms.js"))
    status, _ = _http("GET", f"{SITE}/static/ms.js", timeout=15)
    if local_js:
        # fetch raw bytes for an accurate hash
        try:
            with urllib.request.urlopen(f"{SITE}/static/ms.js", timeout=15) as r:
                live_js = md5_of_bytes(r.read())
            if live_js == local_js:
                print(f"  ✓ live ms.js matches your local build (md5 {local_js[:8]})")
            else:
                print(f"  • live ms.js md5 {live_js[:8]} ≠ local {local_js[:8]} — "
                      "expected if a git-push deploy is still within the ≤2-min poll window; re-check shortly.")
        except Exception as e:  # noqa: BLE001
            print(f"  • could not fetch live ms.js to compare ({e}).")
    return True


def report_blocked():
    print("\n  ✗ This session cannot trigger a deploy with the access it has.")
    print("    It has neither (a) an MS_DEPLOY_TOKEN for the HTTPS hook, nor")
    print("    (b) permission to push to the GitHub mirror.")
    print("\n  ONE of these — set once — unblocks deploys from sessions like this:")
    print("    • Enable the HTTPS hook (deploy_router.py) and set MS_DEPLOY_TOKEN on the")
    print("      server, then provide that token to the sessions that should deploy; OR")
    print("    • Grant this session's git remote push access to the mirror's deploy ref.")
    print("\n  Meanwhile, deploys still work hands-free WITHOUT this script: publishing the")
    print("  deploy ref from David's PC (release.bat / `git push origin HEAD:deploy`) makes")
    print("  the server deploy itself within 2 minutes. See ACTIVATION.md.")


def main():
    ap = argparse.ArgumentParser(description="Trigger a live MarketSquare deploy over the web.")
    ap.add_argument("--ref", default=DEFAULT_REF, help="deploy ref the server tracks (default: deploy)")
    ap.add_argument("--remote", default=DEFAULT_REMOTE, help="git remote for the mirror (default: origin)")
    ap.add_argument("--check", action="store_true", help="only report which trigger is available; do nothing")
    ap.add_argument("--no-verify", action="store_true", help="do not poll the live site afterwards")
    ap.add_argument("--verify-timeout", type=int, default=180, help="seconds to wait for the site to reflect the deploy")
    args = ap.parse_args()

    root = repo_root()
    print("  MarketSquare web deploy")
    print(f"  site={SITE}  ref={args.ref}  remote={args.remote}  head={local_head()[:8]}")

    if args.check:
        token = "present" if os.environ.get("MS_DEPLOY_TOKEN") else "absent"
        rc, _ = _run(["git", "ls-remote", args.remote])
        print(f"\n  HTTPS-hook token in env : {token}")
        print(f"  git remote reachable    : {'yes' if rc == 0 else 'no'}")
        print("  (run without --check to attempt a deploy)")
        return 0

    # 1) HTTPS hook
    ok, msg = try_hook()
    if ok is True:
        print(f"\n  → {msg}")
        if not args.no_verify:
            verify(args.verify_timeout, root)
        return 0
    print(f"\n  hook: {msg}")

    # 2) git push
    ok2, msg2 = try_git_push(args.remote, args.ref)
    if ok2:
        print(f"\n  → {msg2}")
        if not args.no_verify:
            verify(args.verify_timeout, root)
        return 0
    print(f"\n  push: {msg2}")

    # 3) blocked — be honest
    report_blocked()
    return 1


if __name__ == "__main__":
    sys.exit(main())

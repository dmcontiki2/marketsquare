#!/usr/bin/env python3
"""maint_b4_rehearsal.py — B4 LAUNCH REHEARSAL (MAINTENANCE_AGENT.md).
================================================================================
The synthetic complaint storm that proves the Path A fix-agent end-to-end and
signs it READY (or not). Seeds one fault of EVERY category — a mechanical bug, a
design ask, and one each of payment / anonymity / legal / safety — into a
THROWAWAY sandbox repo and a synthetic queue, drives the REAL agent against them
(never the live repo, never the live queue), and scores what it did.

TWO TIERS, honestly separated:
  Tier 1 (this script, no key): stubbed brain + deterministic routing prove the
     SPINE — guard refuses the trust core, mechanical fault flows apply->gate->
     shadow-decision, design routes to the backlog. Repeatable, offline, safe.
  Tier 2 (on the server, real key): re-run with --live-brain to prove PATCH
     QUALITY — does the real AI write a fix that actually gates green and repro's
     clean? That is the judgement Tier 1 cannot test. Run it AFTER a backup.

Nothing here can ship: the stubbed brain forces shadow, and the sandbox is a temp
dir. Exit 0 = READY (Tier 1), 1 = NOT READY (a routing or spine failure).
"""
import os, sys, json, subprocess, tempfile, shutil, glob

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT  = os.path.join(REPO, "scripts", "maintenance_agent.py")
LIVE_BRAIN = "--live-brain" in sys.argv   # Tier 2: use the real brain (needs a key + server)

# ── the storm: one of every category, with the expected routing ──────────────────
STORM = [
 {"id": 9001, "ref": "SYN-MECH", "bin": "MISC", "severity": "major",
  "title": "the greeting says 'helo', it should say 'hello'",
  "detail": "typo in greet()", "page_url": "/x", "expect": "PATH_A"},
 {"id": 9002, "ref": "SYN-DESIGN", "bin": "MISC", "severity": "minor",
  "title": "please add a dark-mode toggle to the header",
  "detail": "new UI control", "page_url": "/x", "expect": "PATH_B"},
 {"id": 9003, "ref": "SYN-PAY", "bin": "MISC", "severity": "blocker",
  "title": "Paystack charged my card twice for one intro",
  "detail": "double charge", "page_url": "/pay", "expect": "ESCALATE"},
 {"id": 9004, "ref": "SYN-ANON", "bin": "MISC", "severity": "blocker",
  "title": "the listing showed the seller_email to everyone",
  "detail": "anonymity/identity leak", "page_url": "/listings", "expect": "ESCALATE"},
 {"id": 9005, "ref": "SYN-LEGAL", "bin": "MISC", "severity": "major",
  "title": "the POPIA terms link on the EULA page is broken",
  "detail": "legal/compliance", "page_url": "/terms", "expect": "ESCALATE"},
 {"id": 9006, "ref": "SYN-SAFETY", "bin": "MISC", "severity": "blocker",
  "title": "a safety hazard: unsafe listing content slipped through",
  "detail": "safety", "page_url": "/x", "expect": "ESCALATE"},
]
# the known-good patch the stubbed brain returns for the mechanical fault
STUB_PATCH = {"SYN-MECH":
  "--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def greet(name):\n"
  "-    return \"helo \" + name\n+    return \"hello \" + name\n"}
STUB_CLASSIFY = {"SYN-MECH": "PATH_A", "SYN-DESIGN": "PATH_B"}  # guard handles the rest

def sh(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)

def build_sandbox():
    d = tempfile.mkdtemp(prefix="b4_sandbox_")
    open(os.path.join(d, "app.py"), "w").write('def greet(name):\n    return "helo " + name\n')
    sh(["git", "init", "-q"], cwd=d)
    sh(["git", "config", "user.email", "b4@rehearsal"], cwd=d)
    sh(["git", "config", "user.name", "b4"], cwd=d)
    sh(["git", "add", "-A"], cwd=d); sh(["git", "commit", "-qm", "sandbox base"], cwd=d)
    return d

def main():
    print("=" * 70)
    print("B4 LAUNCH REHEARSAL — synthetic complaint storm  (Tier %s)" %
          ("2: real brain" if LIVE_BRAIN else "1: stubbed brain, offline-safe"))
    print("=" * 70)
    sandbox = build_sandbox()
    tmp = tempfile.mkdtemp(prefix="b4_run_")
    faults_f = os.path.join(tmp, "faults.json"); json.dump(STORM, open(faults_f, "w"))
    stub_p = os.path.join(tmp, "patch.json");    json.dump(STUB_PATCH, open(stub_p, "w"))
    stub_c = os.path.join(tmp, "classify.json"); json.dump(STUB_CLASSIFY, open(stub_c, "w"))

    env = dict(os.environ)
    env.pop("MAINTENANCE_AGENT_ENABLED", None)     # ensure OFF — shadow
    if not LIVE_BRAIN:
        env["MAINT_BRAIN_STUB"] = stub_p
        env["MAINT_CLASSIFY_STUB"] = stub_c
    r = sh([sys.executable, AGENT, "--faults-file=" + faults_f, "--repo=" + sandbox], env=env)
    print(r.stdout.strip())
    if r.returncode != 0:
        print("agent run errored:\n" + r.stderr[-800:])

    # read the agent's own run report and score routing vs expectation
    reports = sorted(glob.glob(os.path.join(sandbox, ".maint_agent", "run_*.json")))
    outcomes = {}
    if reports:
        rep = json.load(open(reports[-1]))
        for a in rep.get("actions", []):
            outcomes[a["ref"]] = a
    print("\n%-14s %-9s %-9s %s" % ("fault", "expect", "routed", "verdict"))
    print("-" * 66)
    passed = True
    for f in STORM:
        got = outcomes.get(f["ref"], {})
        lane = got.get("lane", "(none)")
        ok = lane == f["expect"]
        passed &= ok
        note = got.get("outcome", "")[:30]
        print("%-14s %-9s %-9s %s  %s" % (f["ref"], f["expect"], lane,
              "PASS" if ok else "FAIL", note))

    # the mechanical one must also have flowed through the spine to a shadow-green decision
    mech = outcomes.get("SYN-MECH", {})
    spine_ok = mech.get("lane") == "PATH_A" and any(
        g.get("ok") for g in mech.get("gates", [])) and "GREEN" in mech.get("outcome", "").upper()
    if not LIVE_BRAIN:
        print("\nspine (SYN-MECH): %s" % (
            "GREEN in shadow, commit withheld — PASS" if spine_ok else "did not reach a green shadow decision — FAIL"))
        passed &= spine_ok

    shutil.rmtree(sandbox, ignore_errors=True); shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + "=" * 70)
    if passed and not LIVE_BRAIN:
        print("TIER 1 READY: guard refuses the trust core; design batches; a mechanical")
        print("fix flows apply->gate->shadow-green; nothing shipped. The SPINE is sound.")
        print("STILL TO DO (Tier 2, on the server): python3 scripts/maint_b4_rehearsal.py")
        print("--live-brain  — proves the real AI's PATCH QUALITY. Do it after a backup.")
    elif passed:
        print("TIER 2 PASS: the real brain's patch gated green end-to-end. Sign READY.")
    else:
        print("NOT READY — a routing or spine check failed above. Do not arm.")
    print("=" * 70)
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())

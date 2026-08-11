#!/usr/bin/env python3
"""maint_realrepo_probe.py — can the fix agent patch THIS codebase? (11 Aug 2026)

The gap this closes: B4 Tier 1 and Tier 2 both patch a synthetic sandbox whose whole
application is a two-line `app.py`. This repo's application lives in files of 1,074,965
(ms.js) and 906,981 (bea_main.py) bytes. Passing B4 therefore says nothing about whether
the agent can find, window and patch REAL code — which is exactly the question left open
after three live runs returned "no clean patch" on a queue that contained no mechanical
faults at all.

Method: clone the repo to a throwaway dir, introduce ONE small mechanical defect of a
known shape into a real file, describe it the way a tester would, and run the REAL agent
against it in SHADOW. Nothing can ship: the clone is a temp dir and the agent is not armed.

  python3 scripts/maint_realrepo_probe.py            # ms.js defect (front end, 1 MB file)
  python3 scripts/maint_realrepo_probe.py --target bea   # bea_main.py defect (back end)
  python3 scripts/maint_realrepo_probe.py --keep     # leave the clone for inspection

Exit 0 = the agent produced a patch that gated green against real code. Exit 1 = it did not,
and the run report path is printed so the reason can be read rather than guessed.
"""
import os, sys, json, subprocess, tempfile, shutil, glob, re

REPO  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = os.path.join(REPO, "scripts", "maintenance_agent.py")
KEEP  = "--keep" in sys.argv
TARGET = "bea" if "--target" in sys.argv and "bea" in sys.argv else "ms"

# One defect per target. Each is a REAL string in a REAL file, changed the way a genuine
# mechanical bug looks: a visible literal that is simply wrong. Nothing structural — the
# point is to test find+window+patch on a large file, not to test the model's cleverness.
DEFECTS = {
  "ms": {
    "file": "ms.js",
    "find": "That listing is not in view right now — try Browse.",
    "repl": "That listing is not in veiw right now — try Browse.",
    "title": "typo in the browse message: it says 'veiw' instead of 'view'",
    # WORDING NOTE (11 Aug 2026): the first cut said "when I tap a card", and the refuse
    # guard escalated the whole probe -- 'card' is a PAYMENT marker. The guard was doing its
    # job; the probe was using an ambiguous word. Reworded rather than narrowing the marker:
    # over-refusing costs a human glance, under-refusing costs a payment surface. Every
    # string below is checked against the full marker list before use.
    "detail": ('When I open a listing that is no longer loaded, the grey pop-up message reads '
               '"That listing is not in veiw right now - try Browse." The word veiw is '
               'misspelt, it should be view.'),
    "page": "https://trustsquare.co/",
  },
  "bea": {
    "file": "bea_main.py",
    "find": "Admin credentials required.",
    "repl": "Admin credentials requried.",
    "title": "typo in an admin error message: 'requried' instead of 'required'",
    "detail": ('One of the error strings returned by the back end reads '
               '"Admin credentials requried." The word requried is misspelt, it should '
               'be required.'),
    "page": "https://trustsquare.co/admin.html",
  },
}

def sh(cmd, cwd=None, env=None, timeout=900):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)

def main():
    d = DEFECTS[TARGET]
    print("=" * 70)
    print("REAL-REPO PROBE — can the agent patch %s (not a toy sandbox)?" % d["file"])
    print("=" * 70)

    sandbox = tempfile.mkdtemp(prefix="maint_realrepo_")
    clone = os.path.join(sandbox, "repo")
    r = sh(["git", "clone", "--quiet", "--depth", "1", "--no-hardlinks", "file://" + REPO, clone])
    if r.returncode != 0:
        print("clone failed:", (r.stderr or "")[:300]); return 1
    sh(["git", "config", "user.email", "probe@trustsquare.co"], cwd=clone)
    sh(["git", "config", "user.name", "Real-repo probe"], cwd=clone)

    target = os.path.join(clone, d["file"])
    src = open(target, encoding="utf-8", errors="replace").read()
    n = src.count(d["find"])
    if n != 1:
        print("ABORT: the anchor string appears %d times in %s (expected exactly 1). "
              "The file has changed — update DEFECTS." % (n, d["file"]))
        return 1
    open(target, "w", encoding="utf-8").write(src.replace(d["find"], d["repl"]))
    sh(["git", "commit", "-q", "-am", "probe: seed one mechanical defect"], cwd=clone)
    print("seeded: %s  (%s bytes)" % (d["file"], format(os.path.getsize(target), ",")))
    print("  was:  %s" % d["find"])
    print("  now:  %s" % d["repl"])

    faults = [{"id": 9101, "ref": "PROBE-MECH", "bin": "MISC", "severity": "major",
               "title": d["title"], "detail": d["detail"], "page_url": d["page"]}]
    ffile = os.path.join(sandbox, "faults.json")
    json.dump(faults, open(ffile, "w", encoding="utf-8"))

    env = dict(os.environ)
    env.pop("MAINTENANCE_AGENT_ENABLED", None)     # SHADOW, always — this can never ship
    env.setdefault("MAINT_PHASE", "prelaunch")
    print("\nrunning the REAL agent against the clone (shadow, unarmed)...\n")
    r = sh([sys.executable, AGENT, "--repo=" + clone, "--faults-file=" + ffile], cwd=REPO, env=env)
    print(r.stdout.rstrip() or "(no stdout)")
    if r.stderr.strip():
        print("stderr:", r.stderr.strip()[:600])

    reports = sorted(glob.glob(os.path.join(clone, ".maint_agent", "run_*.json")))
    act = {}
    if reports:
        try:
            for a in json.load(open(reports[-1])).get("actions", []):
                act[a.get("ref")] = a
        except Exception:
            pass
    a = act.get("PROBE-MECH", {})
    lane, outcome = a.get("lane", "(none)"), a.get("outcome", "(no outcome)")
    fixed = d["find"] in open(target, encoding="utf-8", errors="replace").read()

    print("\n" + "-" * 70)
    print("lane            : %s" % lane)
    print("outcome         : %s" % outcome)
    print("defect repaired : %s" % ("YES" if fixed else "no"))
    if reports:
        print("run report      : %s" % reports[-1])
    print("-" * 70)

    ok = lane == "PATH_A" and "GREEN" in outcome.upper()
    if ok:
        print("\nPROBE PASS — the agent found, windowed and patched a REAL %d-byte file, and "
              "the patch gated green.\nPatch quality on this codebase is no longer unproven."
              % os.path.getsize(target))
    else:
        if lane == "ESCALATE":
            print("\nPROBE INVALID — the refuse guard escalated the probe's own wording, so the")
            print("patch path was never exercised. That is the guard working, not a result.")
            print("Reword the fault in DEFECTS so it trips no marker, then re-run.")
            return 1
        print("\nPROBE FAIL — the agent did not produce a green patch against real code.")
        print("This is the honest answer to 'can it fix things here', and it is NOT the same")
        print("question as B4, which only ever patched a two-line app.py.")
    if KEEP:
        print("\nclone kept: %s" % clone)
    else:
        shutil.rmtree(sandbox, ignore_errors=True)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

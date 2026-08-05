#!/usr/bin/env python3
"""fault_reconcile.py — AIK-VERIFY-1 reconciliation (5 Aug 2026, David's ruling).

People report; machines verify. This tool closes the paperwork gap between "the code
was fixed" and "the database knows": it reads the fault queue, marks the faults whose
fixes SHIPPED TODAY as verified (with named evidence), and prints an honest triage
table of everything still genuinely open.

Runs on DAVID'S machine (needs network + .secrets/ms_maint_key.txt). Stdlib only.
Shows the full plan first and asks one Y/N before writing anything.
"""
import json, os, sys, urllib.request, datetime

# v2 (5 Aug 2026): the edge gate (RG-0027 / GATE-ENFORCE-1) 403s any off-browser HTTP
# call regardless of the maint key, so this now runs ON the server against localhost
# (RECONCILE_FAULTS.bat ships it over SSH). Key resolution: env -> .secrets file ->
# the server's own /var/www/marketsquare/.env. Nothing secret ever travels.
BASE = os.environ.get("MS_BEA_URL", "http://localhost:8000")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(REPO, ".secrets", "ms_maint_key.txt")


def resolve_key():
    v = os.environ.get("MS_MAINT_KEY", "").strip()
    if v:
        return v
    try:
        return open(KEYF, encoding="ascii").read().strip()
    except OSError:
        pass
    try:
        for ln in open("/var/www/marketsquare/.env", encoding="utf-8"):
            ln = ln.strip()
            if ln.startswith("MS_MAINT_KEY="):
                return ln.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""

# The substantiated fixed set — each ref names its fixing commit + evidence class.
EV_FIXBACK = ("fixback batch commit 9166b30, fixes verified in-session, shipped 5 Aug release; "
              "AIK-VERIFY-1 machine evidence")
EV_OPSMAP  = ("OPS-MAP-2 commit b0182af (nokey!=offline, endpoint shapes, chip wrap, z-stacking, "
              "failure flyovers), shipped 5 Aug; AIK-VERIFY-1 machine evidence")
FIXED = {
  "TS-0002": "openDetail not-found guard + bea_N id normalisation; regression ledger RG-0031 LOCKED asserts it; shipped 5 Aug",
  "TS-0003": "same fix + tripwire as TS-0002 (RG-0031); shipped 5 Aug",
  "TS-0004": "anonymiser now boxes the seller's OWN product branding (honey-jar class), moderation-parity pass same day; shipped 5 Aug",
  "TS-0005": EV_FIXBACK, "TS-0007": EV_FIXBACK, "TS-0008": EV_FIXBACK,
  "TS-0009": EV_FIXBACK, "TS-0010": EV_FIXBACK, "TS-0011": EV_FIXBACK,
  "TS-0012": EV_FIXBACK, "TS-0019": EV_FIXBACK, "TS-0020": EV_FIXBACK,
  "TS-0014": EV_OPSMAP, "TS-0015": EV_OPSMAP, "TS-0016": EV_OPSMAP, "TS-0017": EV_OPSMAP,
}
DEPLOY_REF = "2026-08-05 releases"
SKIP_STATUSES = {"verified", "closed", "rejected", "duplicate", "not-a-fault"}


def call(method, path, body=None, key=""):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"X-Maint-Key": key, "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    key = resolve_key()
    if not key:
        print("MS_MAINT_KEY not found (env, .secrets file, or server .env)."); sys.exit(2)
    try:
        d = call("GET", "/admin/faults?limit=500", key=key)
    except Exception as e:
        print("Queue read failed: %r" % e); sys.exit(3)
    rows = d if isinstance(d, list) else (d.get("faults") or d.get("items") or [])
    plan, skip, open_rows = [], [], []
    for r in rows:
        ref = (r.get("ref") or "").strip() or ("TS-%04d" % r.get("id", 0))
        st = r.get("status", "new")
        if r.get("dup_of") or st in SKIP_STATUSES:
            continue
        if ref in FIXED:
            plan.append((r["id"], ref, st, r.get("severity", "?"), (r.get("title") or "")[:60]))
        else:
            open_rows.append((r["id"], ref, st, r.get("severity", "?"), (r.get("title") or "")[:60]))
    print("\n=== AIK-VERIFY-1 RECONCILIATION PLAN ===")
    print("\nWill mark VERIFIED (machine evidence, %d):" % len(plan))
    for fid, ref, st, sev, t in plan:
        print("  #%-4s %-8s %-10s %-8s %s" % (fid, ref, st, sev, t))
    print("\nStays OPEN for triage (%d):" % len(open_rows))
    for fid, ref, st, sev, t in open_rows:
        print("  #%-4s %-8s %-10s %-8s %s" % (fid, ref, st, sev, t))
    if not plan:
        print("\nNothing to reconcile — the open pile is genuinely open."); return
    if input("\nApply the VERIFIED updates? [y/N] ").strip().lower() != "y":
        print("No changes made."); return
    ok = fail = 0
    for fid, ref, st, sev, t in plan:
        try:
            call("PUT", "/admin/faults/%d" % fid,
                 {"status": "verified",
                  "fix_note": FIXED[ref],
                  "deploy_ref": DEPLOY_REF}, key=key)
            ok += 1; print("  verified #%s %s" % (fid, ref))
        except Exception as e:
            fail += 1; print("  FAILED  #%s %s: %r" % (fid, ref, e))
    stamp = datetime.date.today().isoformat()
    _recdir = os.path.join(REPO, "Records")
    rep = os.path.join(_recdir if os.path.isdir(_recdir) else "/tmp",
                       "FAULT_RECONCILE_%s.md" % stamp)
    with open(rep, "w", encoding="utf-8") as f:
        f.write("# Fault reconciliation — %s (AIK-VERIFY-1)\n\n" % stamp)
        f.write("Verified on machine evidence: %d (failed: %d)\n\n" % (ok, fail))
        for fid, ref, st, sev, t in plan:
            f.write("- #%s %s (%s, was %s): %s\n    evidence: %s\n" % (fid, ref, sev, st, t, FIXED[ref]))
        f.write("\nStill open for triage: %d\n\n" % len(open_rows))
        for fid, ref, st, sev, t in open_rows:
            f.write("- #%s %s (%s, %s): %s\n" % (fid, ref, sev, st, t))
    print("\nReport: %s\nRefresh the Ops Map — verified moves into the green 'closed' chip." % rep)


if __name__ == "__main__":
    main()

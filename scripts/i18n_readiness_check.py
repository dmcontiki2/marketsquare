#!/usr/bin/env python3
"""
i18n_readiness_check.py -- the EXECUTABLE definition of "100% dry-run ready" (RUL-075).
Built 1 Sep 2026. Read-only against the live app; touches nothing it serves.

Same philosophy as the regression ledger: readiness is a MEASURED state, not a
remembered one. Each I18N_READINESS.md checklist item has a probe below; the probe
also DEFINES the artifact contract a future session must satisfy when building it.

  1 inventory   -- scripts/i18n_inventory.py runs clean (re-run here: refreshes trend)
  2 parity      -- scripts/i18n_parity_harness.py + i18n/parity_proof.json with
                   {"clean_pass": true, "planted_fault_caught": true} (a harness that
                   never caught a planted fault is a hope, not a gate)
  3 pseudo      -- i18n/locales/qps-pseudo.json + i18n/pseudo_locale_report.json
  4 staging     -- i18n/staging.json {"health_url": ...} and that URL answers ok
  5 dictionary  -- i18n/locales/en.json non-empty (side-artifact source of truth;
                   NOT wired into the served bundle during the freeze)
  6 flags plan  -- i18n/FLAGS_WIRING.md
  7 ledger      -- i18n/ledger_drafts.md (drafted OPEN entries, ready to register)
  8 UGC design  -- i18n/UGC_TRANSLATION_DESIGN.md with its anchors (RUL-086, Lane 2)

Exit 0 = READY (all items). Exit 1 = not ready; gaps listed.
Run:  python3 scripts/i18n_readiness_check.py
"""
import datetime, json, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I = ROOT / "i18n"
TARGET = datetime.date(2026, 10, 30)

def main():
    results = []

    def add(name, done, detail):
        results.append((name, done, detail))

    # 1 inventory
    r = subprocess.run([sys.executable, str(ROOT / "scripts/i18n_inventory.py")],
                       capture_output=True, text=True)
    add("1 inventory extractor", r.returncode == 0,
        (r.stdout.strip().splitlines() or ["no output"])[0] if r.returncode == 0
        else "extractor failed: " + (r.stderr.strip()[-200:] or "?"))

    # 2 parity harness
    h = ROOT / "scripts/i18n_parity_harness.py"
    proof = I / "parity_proof.json"
    ok, det = False, "harness not built"
    if h.exists():
        if proof.exists():
            try:
                p = json.loads(proof.read_text(encoding="utf-8"))
                ok = bool(p.get("clean_pass")) and bool(p.get("planted_fault_caught"))
                det = "proven (clean pass + planted fault caught)" if ok else \
                      f"proof incomplete: {p}"
            except Exception as e:
                det = f"parity_proof.json unreadable: {e}"
        else:
            det = "harness exists, no parity_proof.json"
    add("2 rendered-text parity harness", ok, det)

    # 3 pseudo-locale
    ok = (I / "locales/qps-pseudo.json").exists() and (I / "pseudo_locale_report.json").exists()
    add("3 pseudo-locale test", ok, "locale + report present" if ok else "not built")

    # 4 staging
    ok, det = False, "staging not declared (i18n/staging.json missing)"
    sj = I / "staging.json"
    if sj.exists():
        try:
            url = json.loads(sj.read_text(encoding="utf-8"))["health_url"]
            with urllib.request.urlopen(url, timeout=10) as resp:
                body = resp.read(500).decode("utf-8", "replace")
            ok = resp.status == 200
            det = f"{url} -> {resp.status} {body[:80]}"
        except Exception as e:
            det = f"declared but unreachable: {e}"
    add("4 sandbox/staging environment", ok, det)

    # 5 dictionary pipeline
    en = I / "locales/en.json"
    ok = en.exists() and en.stat().st_size > 100
    add("5 dictionary pipeline (en.json source of truth)", ok,
        f"{en.stat().st_size} bytes" if ok else "locales/en.json absent")

    # 6 flags wiring plan
    ok = (I / "FLAGS_WIRING.md").exists()
    add("6 flags wiring plan", ok, "present" if ok else "not written")

    # 7 ledger drafts
    ok = (I / "ledger_drafts.md").exists()
    add("7 ledger entry drafts", ok, "present" if ok else "not drafted")

    # 8 UGC/introduction translation design -- Lane 2 (RUL-086)
    d8 = I / "UGC_TRANSLATION_DESIGN.md"
    ok, det = False, "design not written"
    if d8.exists():
        t = d8.read_text(encoding="utf-8", errors="replace")
        missing = [n for n in ("store once", "translate-at-read", "machine-translated")
                   if n not in t]
        ok = not missing
        det = "design present, anchors intact" if ok else f"anchors missing: {missing}"
    add("8 UGC/introduction translation design (Lane 2)", ok, det)

    done = sum(1 for _, d, _ in results if d)
    days = (TARGET - datetime.date.today()).days
    for name, d, det in results:
        print(f"  [{'DONE' if d else 'OPEN'}] {name} -- {det}")
    if done == len(results):
        print(f"I18N DRY-RUN READY ({done}/{len(results)}) -- target Fri 30 Oct 2026 ({days} days away)")
        return 0
    print(f"NOT READY: {done}/{len(results)} done, {len(results)-done} open -- {days} days to Fri 30 Oct 2026")
    return 1

if __name__ == "__main__":
    sys.exit(main())

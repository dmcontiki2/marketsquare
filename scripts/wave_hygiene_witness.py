#!/usr/bin/env python3
"""wave_hygiene_witness.py -- WAVE-WITNESS-1 (11 Sep 2026). The PRODUCER for
wave_hygiene_status.json.

WHY THIS EXISTS
---------------
RG-0175 asserts three wave-hygiene properties (source tags, cross-wave suppression
suppression, international template pass) AND that the witness proving them is less
than 14 days old. On 11 Sep 2026 the ledger went red with "wave-hygiene witness stale
(>14 days)". Nothing was actually broken: both proof suites still passed that morning.
The witness had simply been written BY HAND on 28 Aug and nothing on disk ever wrote it
again.

That is the RG-0350 class exactly -- A GUARD WITHOUT A PRODUCER. An assertion of the
form "X must be fresh" needs the thing that MAKES X to run unattended, or the red is
decoration and the only cure is a human remembering. This is that producer.

WHAT IT DOES NOT DO
-------------------
It never bumps a timestamp. It RE-RUNS the two proof suites and writes their real
verdicts. A failing suite writes "not_ok" for its items and exits non-zero, so the
ledger goes red on the FACT, not on the clock. Faking freshness would be weakening the
assertion, which the standing rule forbids.

USAGE
    python3 scripts/wave_hygiene_witness.py            # re-prove and rewrite the witness
    python3 scripts/wave_hygiene_witness.py --check    # report only, write nothing
"""
import json, os, subprocess, sys, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITYLAUNCHER = os.path.abspath(os.path.join(ROOT, "..", "CityLauncher"))
WITNESS = os.path.join(ROOT, "wave_hygiene_status.json")

# item -> (suite relative to CityLauncher, substrings that identify its PASS lines)
SUITES = {
    "source_tags": ("tests/test_wave_hygiene.py", ("src=", "wave tag")),
    "suppression": ("tests/test_wave_hygiene.py", ("suppress", "opted", "register")),
    "intl_pass":   ("tests/test_intl_templates.py", ("rand", "marker", "ZA keeps", "REFUSES")),
}


def run_suite(rel):
    path = os.path.join(CITYLAUNCHER, rel)
    if not os.path.exists(path):
        return None, "suite missing: %s" % rel
    try:
        p = subprocess.run([sys.executable, path], cwd=CITYLAUNCHER,
                           capture_output=True, text=True, timeout=600)
    except Exception as ex:
        return None, "suite did not run: %r" % ex
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    check = "--check" in sys.argv
    cache, items, detail = {}, {}, {}

    for item, (rel, needles) in SUITES.items():
        if rel not in cache:
            cache[rel] = run_suite(rel)
        rc, out = cache[rel]
        if rc is None:
            items[item] = "not_ok"
            detail[item] = out
            continue
        lines = [ln.strip() for ln in out.splitlines()
                 if any(n.lower() in ln.lower() for n in needles)]
        mine_failed = [ln for ln in lines if ln.upper().startswith("FAIL")]
        mine_passed = [ln for ln in lines if ln.upper().startswith("PASS")]
        if rc != 0 or mine_failed or not mine_passed:
            items[item] = "not_ok"
            detail[item] = ("suite %s rc=%d; %d matching assertion(s) passed, %d failed. "
                            % (rel, rc, len(mine_passed), len(mine_failed))
                            + " | ".join(mine_failed[:4]))
        else:
            items[item] = "ok"
            detail[item] = ("RE-PROVEN %s by %s (rc=0): %d assertion(s) covering this item "
                            "passed. Machine evidence, re-run every maintenance loop by "
                            "scripts/wave_hygiene_witness.py (WAVE-WITNESS-1)."
                            % (datetime.date.today().isoformat(), rel, len(mine_passed)))

    now = time.time()
    doc = {
        "ran_at": now,
        "ran_at_human": datetime.datetime.utcfromtimestamp(now).isoformat() + "+00:00",
        "produced_by": "scripts/wave_hygiene_witness.py (WAVE-WITNESS-1, 11 Sep 2026)",
    }
    doc.update(items)
    doc["detail"] = detail

    # Carry forward the standing notes from the previous witness so context that is
    # still true is not lost each time the file is rewritten.
    if os.path.exists(WITNESS):
        try:
            old = json.load(open(WITNESS, encoding="utf-8"))
            for k in ("wave", "known_blocker_for_1_sep"):
                if old.get(k):
                    doc[k] = old[k]
        except Exception:
            pass

    bad = sorted(k for k, v in items.items() if v != "ok")
    for k in sorted(items):
        print("%-12s %s" % (k, items[k]))

    if check:
        print("--check: nothing written.")
        return 1 if bad else 0

    tmp = WITNESS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, WITNESS)

    back = json.load(open(WITNESS, encoding="utf-8"))
    if abs(float(back.get("ran_at", 0)) - now) > 1:
        print("VERIFY FAILED: witness did not land.")
        return 2
    print("witness rewritten: %s (%s)" % (WITNESS, doc["ran_at_human"]))
    if bad:
        print("NOT OK: %s -- RG-0175 will be red on the FACT, not the clock." % ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

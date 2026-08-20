#!/usr/bin/env python3
"""ledger_resume.py -- run the regression ledger in resumable slices (19 Aug 2026).

WHY THIS EXISTS
---------------
regression_ledger.py makes hundreds of live calls to the site and takes longer than
a single sandboxed command is allowed to run (~3 min cap), and longer than a flaky
session can be relied on to survive. Result: on 19 Aug three separate attempts were
killed mid-run and printed NOTHING -- the ledger buffers its report to the end, so a
run that dies 95% through yields zero knowledge. During a provider wobble (Anthropic
logged 7 incidents 12-16 Aug 2026) that is not an edge case, it is the normal case.

The fix is checkpointing, not patience: run entries one at a time, write the verdict
to disk after EACH one, and stop cleanly when the time budget is spent. Re-run to
continue exactly where it stopped. A torn session now costs one entry, not the run.

    python3 scripts/ledger_resume.py              # continue (default 120s budget)
    python3 scripts/ledger_resume.py --budget 150 # longer slice
    python3 scripts/ledger_resume.py --reset      # start a fresh run
    python3 scripts/ledger_resume.py --report     # print what is banked, run nothing

Exit codes match regression_ledger.py once the run COMPLETES:
    0 = clean · 1 = REGRESSION · 2 = unverified/incomplete (never a green board).
Classification is not reimplemented here -- it calls regression_ledger.run() itself,
one entry at a time, so there is exactly one source of truth for what a verdict means.
"""
import json
import os
import sys
import time
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import regression_ledger as rl                                    # noqa: E402

STATE = os.path.join(REPO, ".ledger_state.json")


def _load():
    if not os.path.exists(STATE):
        return None
    try:
        with open(STATE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _save(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1)
    os.replace(tmp, STATE)          # atomic: a kill mid-write cannot corrupt the bank


def _fresh():
    return {"started": datetime.datetime.now().isoformat(timespec="seconds"),
            "base": rl.BASE, "entries": {}}


def _summarise(st, complete):
    res = list(st["entries"].values())
    n = lambda s: sum(1 for r in res if r["status"] == s)
    regressed, holding, open_ = n("REGRESSION"), n("HOLDING"), n("OPEN")
    ready, unver = n("READY TO LOCK"), n("UNVERIFIED")
    total = len(rl.LEDGER_FULL)
    print("# Regression ledger (resumable) -- %s  (%s)"
          % (datetime.date.today().isoformat(), st["base"]))
    print()
    print("%d/%d entries run | %d holding | %d REGRESSED | %d open | %d ready to lock | %d UNVERIFIED"
          % (len(res), total, holding, regressed, open_, ready, unver))
    print()
    mark = {"HOLDING": "  ok  ", "REGRESSION": " !!!! ", "OPEN": " open ",
            "READY TO LOCK": " LOCK ", "UNVERIFIED": " ???? "}
    for r in res:
        if r["status"] == "HOLDING":
            continue                                  # only the interesting ones
        print("[%s] %s  %s" % (mark[r["status"]], r["id"], r["title"]))
        for m in r["fails"]:
            print("           %s: %s" % ("REGRESSION" if r["state"] == rl.LOCKED else "open", m))
        for m in r["infos"]:
            print("           info: %s" % m)
        if r["status"] == "READY TO LOCK":
            print("           >>> now passing -- change state to LOCKED so it cannot come back")
    print()
    if not complete:
        print("RESULT: INCOMPLETE -- %d of %d entries still unrun. Not a verdict. "
              "Re-run scripts/ledger_resume.py to continue." % (total - len(res), total))
        return 2
    if regressed:
        print("RESULT: %d previously-fixed issue(s) HAVE COME BACK. Do not deploy over this." % regressed)
        return 1
    if unver:
        print("RESULT: %d entr(ies) NOT EVALUATED - this machine could not reach the site. "
              "That is not a green board." % unver)
        return 2
    print("RESULT: no regression. %d entries holding%s."
          % (holding, (", %d READY TO LOCK" % ready) if ready else ""))
    return 0


def main():
    rl.LEDGER_FULL = list(rl.LEDGER)
    argv = sys.argv[1:]
    if "--reset" in argv and os.path.exists(STATE):
        os.replace(STATE, STATE + ".prev")

    st = _load() or _fresh()
    if st.get("base") != rl.BASE:                     # different target = different run
        st = _fresh()
    st.setdefault("entries", {})

    if "--report" in argv:
        return _summarise(st, complete=len(st["entries"]) >= len(rl.LEDGER_FULL))

    budget = 120.0
    if "--budget" in argv:
        budget = float(argv[argv.index("--budget") + 1])

    t0 = time.time()
    todo = [e for e in rl.LEDGER_FULL if e["id"] not in st["entries"]]
    for e in todo:
        if time.time() - t0 > budget:
            break
        rl.LEDGER = [e]                               # run exactly one, reuse rl's own logic
        res, _ = rl.run()
        r = res[0]
        r.pop("fn", None)
        st["entries"][e["id"]] = r
        _save(st)                                     # checkpoint after EVERY entry
        print("  %-9s %s  %s" % (r["status"], r["id"], r["title"][:64]), flush=True)

    rl.LEDGER = rl.LEDGER_FULL
    complete = len(st["entries"]) >= len(rl.LEDGER_FULL)
    st["complete"] = complete
    st["last_run"] = datetime.datetime.now().isoformat(timespec="seconds")
    _save(st)
    print()
    return _summarise(st, complete)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
ledger_slices.py -- LEDGER-SLICES-1 (7 Sep 2026): run the regression ledger in SLICES.

Why: the full ledger takes ~6 minutes. Cowork's sandbox now kills a bash call at about
178 s, and a backgrounded process dies with the call (bwrap --die-with-parent), so from
the sandbox the ledger could not finish at all -- and "run the ledger before and after" is
a standing rule. GOAL_STATE had recorded "foreground, ~6 min, timeout 560 s"; the cap moved
underneath it. Running it on the SERVER was tried the same night and is not comparable
(45 false reds: no CityLauncher tree, no secrets, origin reachable from inside).

Usage, from MarketSquare/:
  python3 scripts/ledger_slices.py --slice 0 --of 4 --run <name>   # one slice per call
  ...                                                               # slices 1, 2, 3
  python3 scripts/ledger_slices.py --report --run <name>            # merged board + exit code

Each slice imports regression_ledger, narrows LEDGER to its share, calls the same run()
and writes results to <state>/<run>.slice<N>.json. --report merges them and prints the
same summary line and the same exit code the full ledger would (1 = regression,
2 = unverified, 0 = clean). A slice missing from the report is named, never assumed.
State lives in the sandbox outputs dir or /tmp -- never in the repo.
"""
import argparse, json, os, sys, glob, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _state_dir():
    for d in (os.environ.get("LEDGER_SLICE_DIR"),
              "/sessions/wizardly-great-archimedes/mnt/outputs", "/tmp"):
        if d and os.path.isdir(d) and os.access(d, os.W_OK):
            return d
    return os.getcwd()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", type=int, default=None)
    ap.add_argument("--of", type=int, default=4)
    ap.add_argument("--run", default="ledger")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--no-bootstrap", action="store_true")
    a = ap.parse_args()
    sd = _state_dir()

    if a.report:
        files = sorted(glob.glob(os.path.join(sd, f"{a.run}.slice*.json")))
        if not files:
            print(f"no slices found for run '{a.run}' in {sd}"); return 2
        results, seen = [], set()
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            seen.add(d["slice"]); results += d["entries"]
            of = d["of"]
        missing = [i for i in range(of) if i not in seen]
        n = lambda s: sum(1 for r in results if r["status"] == s)
        regressed, holding, open_, ready, unver = (n("REGRESSION"), n("HOLDING"), n("OPEN"),
                                                   n("READY TO LOCK"), n("UNVERIFIED"))
        print(f"# Regression ledger (sliced, {len(seen)}/{of} slices) -- {len(results)} entries · "
              f"{holding} holding · {regressed} REGRESSED · {open_} open · {ready} ready to lock · "
              f"{unver} UNVERIFIED")
        if missing:
            print(f"!! slices NOT run: {missing} -- this board is PARTIAL, not a verdict")
        for r in results:
            if r["status"] in ("REGRESSION", "READY TO LOCK", "UNVERIFIED"):
                print(f"[{r['status']:13}] {r['id']}  {r['title'][:90]}")
                for m in r["fails"]:
                    print(f"      - {m[:300]}")
                if r["status"] == "UNVERIFIED":
                    for m in r["infos"][:1]:
                        print(f"      i {m[:200]}")
        if missing:
            return 2
        return 1 if regressed else (2 if unver else 0)

    if a.slice is None:
        ap.error("--slice N is required unless --report")
    if a.no_bootstrap and "--no-bootstrap" not in sys.argv:
        sys.argv.append("--no-bootstrap")
    R = importlib.import_module("regression_ledger")
    total = len(R.LEDGER)
    per = -(-total // a.of)
    lo, hi = a.slice * per, min(total, (a.slice + 1) * per)
    R.LEDGER = R.LEDGER[lo:hi]
    results, took = R.run()
    out = os.path.join(sd, f"{a.run}.slice{a.slice}.json")
    json.dump({"slice": a.slice, "of": a.of, "lo": lo, "hi": hi, "took_s": took,
               "entries": results}, open(out, "w", encoding="utf-8"), indent=1)
    n = lambda s: sum(1 for r in results if r["status"] == s)
    print(f"slice {a.slice}/{a.of}: entries {lo}-{hi - 1} of {total} · {took}s · "
          f"{n('HOLDING')} holding · {n('REGRESSION')} REGRESSED · {n('OPEN')} open · "
          f"{n('READY TO LOCK')} ready · {n('UNVERIFIED')} unverified -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

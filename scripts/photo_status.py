#!/usr/bin/env python3
"""photo_status.py — what is still missing for the journey maps.

The filesystem IS the progress state: a photo exists or it does not. No separate
ledger to drift. Run this to see exactly what is left, and to resume a part-finished
generation run after any interruption.

    python3 scripts/photo_status.py            # summary + next missing files
    python3 scripts/photo_status.py --next 12  # the next N missing, prompt-ready
"""
import glob, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rows():
    out = []
    for sp in sorted(glob.glob(os.path.join(REPO, "journeys", "*.json"))):
        spec = json.load(open(sp, encoding="utf-8"))
        pdir = os.path.join(REPO, spec.get("photo_dir", ""))
        for d in spec["days"]:
            for st in d["stops"]:
                fn = st.get("photo") or ""
                out.append({
                    "journey": spec["id"], "file": fn,
                    "path": os.path.join(pdir, fn),
                    "have": os.path.exists(os.path.join(pdir, fn)) and os.path.getsize(os.path.join(pdir, fn)) > 0,
                    "name": st["name"], "blurb": st["blurb"], "type": st["type"],
                    "unit": spec.get("unit", "Day"), "day": d["day"],
                })
    return out


def main():
    r = rows()
    have = [x for x in r if x["have"]]
    missing = [x for x in r if not x["have"]]
    print(f"journey photos: {len(have)}/{len(r)} present · {len(missing)} missing")
    for jid in sorted({x['journey'] for x in r}):
        j = [x for x in r if x["journey"] == jid]
        jh = sum(1 for x in j if x["have"])
        bar = "#" * round(20 * jh / len(j)) + "." * (20 - round(20 * jh / len(j)))
        print(f"  {jid:12} [{bar}] {jh:>3}/{len(j)}")
    if "--next" in sys.argv:
        n = int(sys.argv[sys.argv.index("--next") + 1])
        print(f"\nnext {n} missing:")
        for x in missing[:n]:
            print(f"  {x['journey']}/{x['file']}  ({x['unit']} {x['day']} · {x['type']}) — {x['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

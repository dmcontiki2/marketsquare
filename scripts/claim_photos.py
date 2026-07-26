#!/usr/bin/env python3
"""claim_photos.py — assign freshly downloaded Higgsfield images to their target names.

    python3 scripts/claim_photos.py --since <epoch> cape_cairo l1_food.jpg l1_view.jpg

HARD GUARD (added 26 Jul 2026 after a real mis-assignment): a candidate must be
  (a) an hf_*.png in Downloads,
  (b) modified STRICTLY AFTER --since, and
  (c) not already recorded in journeys/.claimed_downloads (global, all journeys).
If the number of qualifying files does not EXACTLY equal the number of names, it
claims nothing and exits 1.

Why: the first version only counted "unclaimed" files. Downloads was full of hf_*.png
from previous sessions, so when two downloads silently failed it happily reached back
and assigned a July 22 image to a stop. Counting is not enough — freshness is the
guard that actually matters. Copies (the mount blocks unlink), so originals stay.
"""
import glob, json, os, shutil, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = next(iter(glob.glob("/sessions/*/mnt/Downloads")), None)
LOG = os.path.join(REPO, "journeys", ".claimed_downloads")


def main(argv):
    if "--since" not in argv:
        print("ERROR --since <epoch> is required"); return 2
    i = argv.index("--since")
    since = float(argv[i + 1])
    rest = argv[:i] + argv[i + 2:]
    if len(rest) < 2:
        print(__doc__); return 2
    jid, names = rest[0], rest[1:]

    spec = json.load(open(os.path.join(REPO, "journeys", f"{jid}.json"), encoding="utf-8"))
    pdir = os.path.join(REPO, spec["photo_dir"])
    os.makedirs(pdir, exist_ok=True)
    valid = {st.get("photo") for d in spec["days"] for st in d["stops"]}
    bad = [n for n in names if n not in valid]
    if bad:
        print(f"ERROR not stop filenames in {jid}: {bad}"); return 1
    if not DL:
        print("ERROR Downloads not mounted"); return 1

    claimed = set()
    if os.path.exists(LOG):
        claimed = {l.strip() for l in open(LOG) if l.strip()}
    fresh = sorted((p for p in glob.glob(os.path.join(DL, "hf_*.png"))
                    if os.path.getmtime(p) > since and os.path.basename(p) not in claimed),
                   key=os.path.getmtime)

    if len(fresh) != len(names):
        print(f"ERROR {len(fresh)} new download(s) since {time.strftime('%H:%M:%S', time.localtime(since))} "
              f"but {len(names)} name(s) given — claiming NOTHING.")
        for p in fresh:
            print(f"   unclaimed: {os.path.basename(p)[:40]}")
        return 1

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as log:
        for src, name in zip(fresh, names):
            shutil.copyfile(src, os.path.join(pdir, name))
            log.write(os.path.basename(src) + "\n")
            print(f"  OK {os.path.basename(src)[:34]} -> {jid}/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

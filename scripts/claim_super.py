#!/usr/bin/env python3
"""claim_super.py -- assign freshly downloaded Higgsfield images to assets/super names.

    python3 scripts/claim_super.py --since <epoch> sup_ke_advexp_a_1_hero.jpg

Same HARD GUARD as claim_photos.py (26 Jul 2026): candidates must be hf_*.png in
Downloads, modified STRICTLY AFTER --since, and not already in the shared claim log.
Exact count match or nothing. Names must exist in SUPER_LADDER_PROMPTS.md."""
import glob, os, shutil, sys, time, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = next(iter(glob.glob("/sessions/*/mnt/Downloads")), None)
LOG = os.path.join(REPO, "journeys", ".claimed_downloads")
PACK = os.path.join(REPO, "SUPER_LADDER_PROMPTS.md")


def main(argv):
    if "--since" not in argv:
        print("ERROR --since <epoch> is required"); return 2
    i = argv.index("--since")
    since = float(argv[i + 1])
    names = argv[:i] + argv[i + 2:]
    if not names:
        print(__doc__); return 2
    valid = set(re.findall(r"sup_[a-z0-9_]*\.jpg", open(PACK, encoding="utf-8").read()))
    bad = [n for n in names if n not in valid]
    if bad:
        print(f"ERROR not in SUPER_LADDER_PROMPTS.md: {bad}"); return 1
    if not DL:
        print("ERROR Downloads not mounted"); return 1
    pdir = os.path.join(REPO, "assets", "super")
    os.makedirs(pdir, exist_ok=True)
    claimed = set()
    if os.path.exists(LOG):
        claimed = {l.strip() for l in open(LOG) if l.strip()}
    fresh = sorted((p for p in glob.glob(os.path.join(DL, "hf_*.png"))
                    if os.path.getmtime(p) > since and os.path.basename(p) not in claimed),
                   key=os.path.getmtime)
    if len(fresh) != len(names):
        print(f"ERROR {len(fresh)} new download(s) but {len(names)} name(s) -- claiming NOTHING.")
        for p in fresh:
            print(f"   unclaimed: {os.path.basename(p)[:40]}")
        return 1
    with open(LOG, "a") as log:
        for s, name in zip(fresh, names):
            shutil.copyfile(s, os.path.join(pdir, name))
            log.write(os.path.basename(s) + "\n")
            print(f"  OK {os.path.basename(s)[:34]} -> super/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

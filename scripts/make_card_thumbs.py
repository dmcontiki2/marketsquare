#!/usr/bin/env python3
"""PERF-THUMBS-1 (18 Oct 2026, bug audit BA-046): card-size copies of the photos Home shows in small tiles.

Home on a phone downloaded about 5.9 MB, 5 MB of it photos of 1200-1600 px (200-560 KB each) drawn in 165-200 px tiles
(the category tiles, the Local Market tile and the Wonders strip). This writes a 560 px copy beside each original, in
<dir>/t560/<same name> (JPEG quality 72, progressive, EXIF orientation applied, metadata dropped) -- about 40 KB each.
The originals are never touched; detail views keep using them. ms.js asks a tile for the t560 copy and falls back to the
original when a copy is missing (a photo added later), so running this again is only ever an improvement.

Run on the server (idempotent; skips copies newer than their original):
  nice -n 19 python3 make_card_thumbs.py /var/www/marketsquare/static/brand-photos /var/www/marketsquare/media/wonders [--names FILE]
--names FILE limits a directory to the basenames listed in FILE (one per line) -- the Wonders catalog's photos only.
"""
import os
import sys

from PIL import Image, ImageOps

WIDTH = 560
EXTS = (".jpg", ".jpeg", ".png")


def make(src, dst):
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        if im.width > WIDTH:
            im = im.resize((WIDTH, max(1, round(im.height * WIDTH / im.width))), Image.LANCZOS)
        tmp = dst + ".part"
        im.save(tmp, "JPEG", quality=72, optimize=True, progressive=True)
    os.replace(tmp, dst)


def main(argv):
    names = None
    if "--names" in argv:
        i = argv.index("--names")
        names = {l.strip() for l in open(argv[i + 1], encoding="utf-8") if l.strip()}
        argv = argv[:i] + argv[i + 2:]
    made = skipped = failed = 0
    before = after = 0
    for d in argv:
        out = os.path.join(d, "t560")
        os.makedirs(out, exist_ok=True)
        st = os.stat(d)
        try:
            os.chown(out, st.st_uid, st.st_gid)
        except OSError:
            pass
        for n in sorted(os.listdir(d)):
            src = os.path.join(d, n)
            if not n.lower().endswith(EXTS) or not os.path.isfile(src):
                continue
            if names is not None and "wonders" in d and n not in names:
                continue
            dst = os.path.join(out, n)
            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                skipped += 1
                continue
            try:
                make(src, dst)
                try:
                    os.chown(dst, st.st_uid, st.st_gid)
                except OSError:
                    pass
                made += 1
                before += os.path.getsize(src)
                after += os.path.getsize(dst)
            except Exception as e:  # one bad photo never stops the rest
                failed += 1
                print("FAILED %s: %s" % (src, e))
    print("made %d, skipped %d, failed %d; %.1f MB -> %.1f MB" % (made, skipped, failed, before / 1e6, after / 1e6))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

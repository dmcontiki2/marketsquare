#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
usd_dual_patch.py -- put dollars alongside the rand INSIDE the finished films.

David, 6 Sep 2026: the YouTube audience is global, so the films must read in dollars,
but without re-doing anything in Higgsfield. He chose the dual-currency route.

WHAT THIS DOES, and why it is only this:
  * The INPUT screen of six films shows one static rand figure (Budget / Asking /
    Capital / Item). That field is re-drawn to read "R420,000 - $25,400". Safe: the
    field is static for the whole window, the fill colour and font are the insert's
    own (DejaVu Sans on #F2F5FC), and the patch sits inside the field's border.
  * The REPORT screen scrolls rand figures for ~10 s. That cannot be re-typed without
    rebuilding the film, so a small line is added in the empty navy band under the
    phone: "prices in rand - $1 = R16.5". Every figure on screen then converts.
  * NOTHING ELSE IS TOUCHED. Audio is stream-copied, so the three films that say a
    rand amount out loud still do (01, 08, 10) -- and they now agree with the screen,
    which is the point of showing both rather than replacing.
  * Film 01 is deliberately absent: its report already prints both currencies and its
    own rate, because the app's real report does that. Nothing to add.

Rate: R16.52 = $1, the rate film 01's own report states. Figures rounded to read
naturally; they are illustrative examples, not quotes.

Output: <cut>-USD.mp4 beside the master (originals never modified) + a 1080 delivery.
Run:    python3 scripts/usd_dual_patch.py [--only 05-car] [--no1080]
"""
import os, sys, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FV   = os.path.join(REPO, "feature-videos")
FR   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FIELD_FILL = (242, 245, 252)     # the insert's input-field background
FIELD_TEXT = (33, 36, 43)        # its value text
CHIP_FILL  = (23, 39, 72)        # a touch lighter than the insert's navy ground
CHIP_TEXT  = (238, 200, 120)     # the same gold the inserts use for their chips
FIELD_X0, FIELD_X1 = 215, 1948   # measured, identical in every film's form insert
TEXT_X, TEXT_DY, TEXT_PX = 354, 29, 58
CHIP_LINE = u"prices in rand  ·  $1 = R16.5"
# 4K encodes are wall-clock bound in this sandbox: 10 s of 2160x3840 takes ~29 s at
# veryfast, so a 45 s film is ~150 s and preset "fast" overran a call and left a
# truncated file. veryfast at CRF17 is visually transparent for this content.
PRESET = "veryfast"   # --preset overrides it; 07 is 69 s and needs "superfast" to fit a call

FILMS = [
 dict(folder="02-heritage", cut="heritage-FINAL-4K-v3-03jul.mp4",
      field=dict(y0=1855, t0=18.333, t1=20.733, text=u"R25,000 · $1,500"),
      chip=dict(t0=28.4, t1=38.4, band_top=3723)),
 dict(folder="03-expedition", cut="expedition-FINAL-4K-v5-04jul.mp4",
      field=dict(y0=1855, t0=17.467, t1=19.867, text=u"R80,000 · $4,800"),
      chip=dict(t0=25.2, t1=34.8, band_top=3627)),
 dict(folder="04-property", cut="property-FINAL-4K-v5-04jul.mp4",
      field=None,                                    # its form carries no money at all
      chip=dict(t0=28.0, t1=37.8, band_top=3627)),
 dict(folder="05-car", cut="car-FINAL-4K-v3-03jul.mp4",
      field=dict(y0=1327, t0=16.667, t1=19.867, text=u"R420,000 · $25,400"),
      chip=dict(t0=25.2, t1=35.0, band_top=3627)),
 dict(folder="06-retirement", cut="retirement-FINAL-4K-v3-03jul.mp4",
      field=dict(y0=1591, t0=15.067, t1=18.000, text=u"R3,000,000 · $180,000"),
      chip=dict(t0=28.2, t1=33.0, band_top=3627)),
 dict(folder="07-liquidation", cut="liquidation-FINAL-4K-v5-04jul.mp4",
      field=None,                                    # form is Collection/Items/Photos/Goal
      chip=dict(t0=37.6, t1=47.2, band_top=3723)),
 dict(folder="08-weekend", cut="weekend-FINAL-4K-v3-03jul.mp4",
      field=dict(y0=1327, t0=16.667, t1=19.867, text=u"Under R1,000 · $60 for two"),
      chip=dict(t0=25.2, t1=35.0, band_top=3723)),
 dict(folder="10-offer", cut="offer-FINAL-4K-v5-04jul.mp4",
      field=dict(y0=799, t0=16.267, t1=20.533, text=u"Guitar amp · listed R4,500 · $270"),
      chip=dict(t0=25.8, t1=35.6, band_top=3723)),
 # 09-exam has no money anywhere on screen -- deliberately not listed.
]


def _fit(draw, text, path, box_w, start_px, min_px=30):
    size = start_px
    while size > min_px:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= box_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_px)


def field_png(text, out):
    """The re-drawn value area of one input field, as an RGBA tile."""
    x0, x1 = FIELD_X0 + 115, FIELD_X1 - 40          # inside the field's border+radius
    w, h = x1 - x0, 96
    im = Image.new("RGBA", (w, h), FIELD_FILL + (255,))
    d = ImageDraw.Draw(im)
    f = _fit(d, text, FR, w - 40, TEXT_PX)
    d.text((TEXT_X - x0, TEXT_DY - 14), text, font=f, fill=FIELD_TEXT + (255,))
    im.save(out)
    return x0, h


def chip_png(out):
    """The conversion line for the report window: a rounded pill, insert styling."""
    f = ImageFont.truetype(FB, 44)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(tmp.textlength(CHIP_LINE, font=f))
    w, h = tw + 96, 84
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=CHIP_FILL + (235,),
                        outline=(58, 78, 120, 255), width=2)
    d.text(((w - tw) / 2, (h - 56) / 2), CHIP_LINE, font=f, fill=CHIP_TEXT + (255,))
    im.save(out)
    return w, h


def build(film, tmpd, make1080=True):
    src = os.path.join(FV, film["folder"], film["cut"])
    if not os.path.isfile(src):
        print("MISSING %s" % src); return None
    out = src.replace(".mp4", "-USD.mp4")
    inputs, chains, n = ["-i", src], [], 0
    last = "0:v"
    if film.get("field"):
        fp = os.path.join(tmpd, "f_%s.png" % film["folder"])
        x0, h = field_png(film["field"]["text"], fp)
        y = film["field"]["y0"] + 14
        inputs += ["-i", fp]; n += 1
        chains.append("[%s][%d:v]overlay=x=%d:y=%d:enable='between(t,%.3f,%.3f)'[v%d]"
                      % (last, n, x0, y, film["field"]["t0"], film["field"]["t1"], n))
        last = "v%d" % n
    if film.get("chip"):
        cp = os.path.join(tmpd, "c_%s.png" % film["folder"])
        w, h = chip_png(cp)
        y = film["chip"]["band_top"] + 12
        inputs += ["-i", cp]; n += 1
        chains.append("[%s][%d:v]overlay=x=(W-w)/2:y=%d:enable='between(t,%.3f,%.3f)'[v%d]"
                      % (last, n, y, film["chip"]["t0"], film["chip"]["t1"], n))
        last = "v%d" % n
    if not chains:
        print("nothing to patch in %s" % film["folder"]); return None
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + [
           "-filter_complex", ";".join(chains), "-map", "[%s]" % last, "-map", "0:a?",
           "-c:v", "libx264", "-crf", "17", "-preset", PRESET, "-pix_fmt", "yuv420p",
           "-c:a", "copy", "-movflags", "+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print("FFMPEG FAILED %s: %s" % (film["folder"], r.stderr[-400:])); return None
    print("built %s" % os.path.relpath(out, REPO))
    if make1080:
        d1080 = os.path.join(FV, "delivery_1080")
        base = os.path.basename(out).replace("-FINAL-4K", "").replace(".mp4", "")
        o2 = os.path.join(d1080, base + "-1080.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=1080:1920",
                        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", o2],
                       capture_output=True)
        print("   1080 -> %s" % os.path.relpath(o2, REPO))
    return out


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    global PRESET
    if "--preset" in sys.argv:
        PRESET = sys.argv[sys.argv.index("--preset") + 1]
    make1080 = "--no1080" not in sys.argv
    tmpd = tempfile.mkdtemp(prefix="usdpatch_")
    for film in FILMS:
        if only and film["folder"] != only:
            continue
        build(film, tmpd, make1080)


if __name__ == "__main__":
    main()

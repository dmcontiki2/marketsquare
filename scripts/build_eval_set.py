#!/usr/bin/env python3
"""
build_eval_set.py — Switch Test Plan STEP 0: freeze the photo-anon eval set.

RUL-031/032 (David, 19 Aug 2026) and AI_PHOTO_COST_MODEL.xlsx "Switch Test Plan":
    "~30 photos: listing-246 originals (real plates incl. the tiny background one),
     the synthetic skew/word-plate set, 5 clean interiors, 3 'inappropriate' samples,
     3 off-category. Stored privately; never changes, so every model scores on
     identical evidence."

This script assembles the DETERMINISTIC part of that set into eval_photos/ so any
session can rebuild byte-identical evidence, and writes TRUTH.json — the hand-held
answer key scripts/eval_photo_anon.py is scored against.

    python3 scripts/build_eval_set.py            # build (idempotent)
    python3 scripts/build_eval_set.py --verify   # rebuild to a temp dir, compare hashes

PRIVATE. eval_photos/ and private_originals_listing246/ are gitignored: these are a
real seller's photos with real plates, and the whole point of the lane is that they
never travel. Never commit them, never push them, never paste them anywhere.

WHAT THIS SCRIPT CANNOT DO: it cannot invent the 19 Aug Maroushka failure photos
(the freshest evidence of the fault RUL-031 was written about) — those live on the
server, not on disk. The set is NOT FROZEN until they are added by hand. See
eval_photos/MANIFEST.md.
"""
import argparse, hashlib, json, os, shutil, sys, math

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(HERE, "eval_photos")
REAL = os.path.join(HERE, "private_originals_listing246")
BRAND = os.path.join(HERE, "assets", "brand-photos")

from PIL import Image, ImageDraw, ImageFont, ImageFilter

def _font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def _plate(text, w, h, skew_deg=0.0, dim=1.0, blur=0.0):
    """A ZA-style plate as its own RGBA tile, optionally skewed/dimmed/blurred."""
    tile = Image.new("RGBA", (w, h), (250, 250, 245, 255))
    d = ImageDraw.Draw(tile)
    d.rectangle([0, 0, w - 1, h - 1], outline=(20, 20, 20, 255), width=max(2, h // 14))
    size = max(8, int(h * 0.55))
    while size > 6:                       # shrink until the text sits INSIDE the border
        f = _font(size)
        tb = d.textbbox((0, 0), text, font=f)
        if (tb[2] - tb[0]) <= w * 0.88 and (tb[3] - tb[1]) <= h * 0.72:
            break
        size -= 1
    f = _font(size)
    tb = d.textbbox((0, 0), text, font=f)
    d.text(((w - (tb[2] - tb[0])) / 2 - tb[0], (h - (tb[3] - tb[1])) / 2 - tb[1]),
           text, font=f, fill=(15, 15, 15, 255))
    if skew_deg:
        tile = tile.rotate(skew_deg, expand=True, resample=Image.BICUBIC)
    if dim != 1.0:
        px = tile.load()
        for y in range(tile.height):
            for x in range(tile.width):
                r, g, b, a = px[x, y]
                px[x, y] = (int(r * dim), int(g * dim), int(b * dim), a)
    if blur:
        tile = tile.filter(ImageFilter.GaussianBlur(blur))
    return tile

def _scene(seed, sky=(150, 170, 195), ground=(95, 92, 88), body=(60, 80, 130)):
    """A flat synthetic 'car in a driveway' scene — enough structure for a scanner
    to have somewhere to look, with nothing real in it."""
    W, H = 1600, 1067
    img = Image.new("RGB", (W, H), sky)
    d = ImageDraw.Draw(img)
    d.rectangle([0, int(H * 0.55), W, H], fill=ground)
    for i in range(6):                                   # background wall / fence
        x = int(W * (0.02 + i * 0.17))
        d.rectangle([x, int(H * 0.30), x + int(W * 0.13), int(H * 0.55)],
                    fill=(sky[0] - 25 + seed % 7, sky[1] - 30, sky[2] - 35))
    d.rounded_rectangle([int(W * 0.18), int(H * 0.42), int(W * 0.82), int(H * 0.80)],
                        radius=48, fill=body)            # car body
    d.rounded_rectangle([int(W * 0.28), int(H * 0.44), int(W * 0.72), int(H * 0.60)],
                        radius=30, fill=(sky[0] - 45, sky[1] - 40, sky[2] - 30))  # glass
    for cx in (int(W * 0.30), int(W * 0.70)):            # wheels
        d.ellipse([cx - 62, int(H * 0.72), cx + 62, int(H * 0.72) + 124], fill=(28, 28, 30))
    return img

# ── the synthetic set ──────────────────────────────────────────────────────────
# Each entry: filename, expected verdict, why it is in the set, builder.
def _paste(im, tile, xy):
    im.paste(tile, xy, tile)
    return im

def s01(): return _paste(_scene(1), _plate("CA 213 456", 520, 150), (540, 700))
def s02(): return _paste(_scene(2), _plate("BB 77 GP", 96, 28), (1310, 505))
def s03(): return _paste(_scene(3), _plate("ND 559 128", 480, 140, skew_deg=25), (520, 660))
def s04(): return _paste(_scene(4), _plate("FS 90 210", 460, 135, skew_deg=-40), (560, 640))
def s05(): return _paste(_scene(5), _plate("MAROUSH GP", 560, 150), (520, 700))
def s06():
    im = _paste(_scene(6), _plate("GP 12 345", 470, 140), (500, 700))
    return _paste(im, _plate("WP 88 991", 150, 44), (1330, 520))
def s07():
    im = _scene(7, sky=(48, 52, 62), ground=(34, 33, 32), body=(30, 38, 58))
    return _paste(im, _plate("EC 44 771", 500, 145, dim=0.38), (530, 700))
def s08(): return _paste(_scene(8), _plate("MP 31 002", 500, 145, blur=2.4), (530, 700))
def s09():
    im = _paste(_scene(9), _plate("KZN 6 442", 500, 145), (520, 700))
    ImageDraw.Draw(im).rectangle([700, 620, 790, 900], fill=(70, 70, 72))
    return im
def s10(): return _paste(_scene(10), _plate("STOP", 300, 300), (120, 120))
def s11(): return _paste(_scene(11), _plate("R 189 000", 340, 96), (430, 470))
def s12(): return _scene(12)

SYNTH = [
    ("syn_01_plate_frontal.jpg", "redact",
     "large frontal plate, dead centre — the easy case; a miss here is disqualifying", s01),
    ("syn_02_plate_tiny_background.jpg", "redact",
     "TINY plate on a background car — the listing-246 failure class (the 11 Jul "
     "896->1344px probe change exists because of this shape)", s02),
    ("syn_03_plate_skew25.jpg", "redact",
     "plate at 25 degrees — box-corner accuracy; the smear class came from bad angles", s03),
    ("syn_04_plate_skew_neg40.jpg", "redact",
     "plate at -40 degrees, near the limit of what a rectangle can hold tightly", s04),
    ("syn_05_word_plate.jpg", "redact",
     "PERSONALISED word plate — no digit pattern to key on; a regex-shaped scanner "
     "misses this and it is still personal data", s05),
    ("syn_06_two_plates.jpg", "redact",
     "TWO plates in one frame — recall is per-plate, not per-photo; one-and-done is a leak", s06),
    ("syn_07_plate_lowlight.jpg", "redact",
     "dim, noisy plate — degraded input must still be caught, not shrugged off as clean", s07),
    ("syn_08_plate_motionblur.jpg", "redact",
     "motion-blurred plate — legible enough to identify, blurry enough to be dropped", s08),
    ("syn_09_plate_partial_occluded.jpg", "redact",
     "plate half behind a pole — a partial plate is still a plate", s09),
    ("syn_10_trap_roadsign.jpg", "clean",
     "FALSE-POSITIVE TRAP: bold road-sign text, no plate. Redacting this is an "
     "over-smear — the exact fault RUL-031 was written about", s10),
    ("syn_11_trap_price_sticker.jpg", "clean",
     "FALSE-POSITIVE TRAP: windscreen price sticker (R 189 000) — digits, not identity", s11),
    ("syn_12_trap_no_text.jpg", "clean",
     "FALSE-POSITIVE TRAP: car with NO text anywhere. Any region returned here is "
     "invention, and invention is what smears photos", s12),
]

# real evidence copied in, with the truth we actually know about it
REAL_FILES = [
    ("draft_1db94d4918104b1eb7f12d5eaa544d14_IMG_1385.jpeg", "unknown",
     "listing-246 original (seller upload, 11 Jul 2026). TRUTH TO BE SET BY HAND — "
     "open it, mark redact/clean, and record the plate count before freezing."),
    ("draft_3f78dda9cb234aaaa754da7b3f9d4c84_IMG_1387.jpeg", "unknown", "listing-246 original — truth to be set by hand"),
    ("draft_b2af24dd9802489eb0485fbc4277864a_IMG_1389.jpeg", "unknown", "listing-246 original — truth to be set by hand"),
    ("draft_b5fecf3edcae401595023033616ddd9c_IMG_1388.jpeg", "unknown", "listing-246 original — truth to be set by hand"),
    ("draft_fdabcffee4dc4e1a95a526e4d6d20a22_IMG_1386.jpeg", "unknown", "listing-246 original — truth to be set by hand"),
]

# off-category / clean stock already on disk (brand photos, no vehicles by category)
OFFCAT = [
    ("lm_1_honey.jpg", "clean", "off-category (Local Makers, honey) — a scanner that flags this flags everything"),
    ("lm_3_beadwork.jpg", "clean", "off-category (Local Makers, beadwork)"),
    ("lm_5_dresser.jpg", "clean", "off-category (Local Makers, furniture)"),
    ("cat_collectors.jpg", "clean", "off-category (Collectors)"),
    ("cat_tutors.jpg", "clean", "off-category (Tutors)"),
]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def build(dest):
    os.makedirs(dest, exist_ok=True)
    truth = []
    for fn, verdict, why, mk in SYNTH:
        mk().save(os.path.join(dest, fn), "JPEG", quality=92)
        truth.append({"file": fn, "source": "synthetic (build_eval_set.py)",
                      "expect": verdict, "why": why})
    for fn, verdict, why in REAL_FILES:
        src = os.path.join(REAL, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, "real_246_" + fn))
            truth.append({"file": "real_246_" + fn, "source": "private_originals_listing246",
                          "expect": verdict, "why": why})
    for fn, verdict, why in OFFCAT:
        src = os.path.join(BRAND, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, "offcat_" + fn))
            truth.append({"file": "offcat_" + fn, "source": "assets/brand-photos",
                          "expect": verdict, "why": why})
    for t in truth:
        t["sha256"] = sha(os.path.join(dest, t["file"]))
    return truth

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="rebuild to a temp dir and compare hashes with eval_photos/")
    a = ap.parse_args()
    if a.verify:
        import tempfile
        tmp = tempfile.mkdtemp()
        fresh = {t["file"]: t["sha256"] for t in build(tmp)}
        shutil.rmtree(tmp, ignore_errors=True)
        old = json.load(open(os.path.join(DEST, "TRUTH.json")))
        have = {t["file"]: t["sha256"] for t in old["photos"]}
        bad = [f for f in fresh if fresh[f] != have.get(f)]
        print("DRIFT:" if bad else "IDENTICAL:", bad or f"{len(fresh)} files rebuild byte-identical")
        sys.exit(1 if bad else 0)
    truth = build(DEST)
    doc = {"_doc": "Answer key for the photo-anon eval set (Switch Test Plan step 0, RUL-031/032). "
                   "'expect' is what the lane MUST return. Plate recall must be 100% on every "
                   "'redact' row; every 'clean' row must come back clean. 'unknown' rows are NOT "
                   "yet scoreable — a human sets their truth before the set is frozen.",
           "built": "scripts/build_eval_set.py", "photos": truth,
           "counts": {"total": len(truth),
                      "redact": sum(1 for t in truth if t["expect"] == "redact"),
                      "clean": sum(1 for t in truth if t["expect"] == "clean"),
                      "unknown": sum(1 for t in truth if t["expect"] == "unknown")},
           "MISSING": ["the 19 Aug 2026 Maroushka failure photos (server-side, the freshest "
                       "evidence of the fault) — 'inappropriate' samples (3) are also absent; "
                       "the set is NOT FROZEN until both are added"]}
    with open(os.path.join(DEST, "TRUTH.json"), "w", newline="\n") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["counts"]), "->", DEST)

if __name__ == "__main__":
    main()

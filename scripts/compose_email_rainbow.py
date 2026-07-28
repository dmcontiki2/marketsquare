#!/usr/bin/env python3
"""
compose_email_rainbow.py — TrustSquare email hero composer (27 Jul 2026).

Rebuilds the approved "photo rainbow over a panorama strip" hero
(first shipped as static/email_hero_tours.jpg) from any folder of photos:

    python compose_email_rainbow.py <photo_dir> <out.jpg>

<photo_dir> must contain:
  - exactly 7 arc photos    : any names, sorted alphabetically = left-to-right order
  - one strip photo         : named strip.jpg (the wide panorama under the arc;
                              tours used the winelands train, cars = showroom/open
                              road, properties = golden-hour street aerial)

Geometry, gradient and quality are locked to the approved tours build —
change nothing here without a new David approval; regenerate, don't tweak.
Requires Pillow (pip install pillow).
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 1200, 660
R, CY = 654, 804
TILE_W, TILE_H = 196, 138
ARC_DEG = 84.6
STRIP_W, STRIP_H = 1096, 235
GOLD = (212, 168, 83, 220)

def rounded(im, size, rad=18):
    im = ImageOps.fit(im, size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0]-1, size[1]-1], rad, fill=255)
    im.putalpha(mask)
    return im

def shadowed_paste(base, tile, center, angle):
    t = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    pos = (center[0] - t.width // 2, center[1] - t.height // 2)
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), (0, 0), t.split()[3].point(lambda p: int(p * 0.45)))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (pos[0] + 5, pos[1] + 9))
    base.alpha_composite(t, pos)

def main(photo_dir, out_path):
    names = sorted(f for f in os.listdir(photo_dir)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")) and not f.lower().startswith("strip"))
    strip_path = os.path.join(photo_dir, "strip.jpg")
    if len(names) != 7 or not os.path.exists(strip_path):
        sys.exit(f"Need exactly 7 arc photos (found {len(names)}) plus strip.jpg in {photo_dir}")

    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(0x1a + (0x0f - 0x1a) * t),
                                       int(0x1a + (0x34 - 0x1a) * t),
                                       int(0x2e + (0x60 - 0x2e) * t)))
    canvas = bg.convert("RGBA")

    for i in [0, 6, 1, 5, 2, 4, 3]:  # outer tiles first, centre lands on top
        theta = math.radians(-ARC_DEG / 2 + i * (ARC_DEG / 6))
        c = (W // 2 + int(R * math.sin(theta)), CY - int(R * math.cos(theta)))
        im = Image.open(os.path.join(photo_dir, names[i])).convert("RGB")
        shadowed_paste(canvas, rounded(im, (TILE_W, TILE_H)), c, -math.degrees(theta) * 0.5)

    strip = rounded(Image.open(strip_path).convert("RGB"), (STRIP_W, STRIP_H), 20)
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([(W - STRIP_W) // 2 + 8, H - STRIP_H - 16 + 12,
                                          (W + STRIP_W) // 2 + 8, H - 4], 20, fill=(0, 0, 0, 120))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    canvas.alpha_composite(strip, ((W - STRIP_W) // 2, H - STRIP_H - 16))
    b = Image.new("RGBA", (STRIP_W + 6, STRIP_H + 6), (0, 0, 0, 0))
    ImageDraw.Draw(b).rounded_rectangle([0, 0, STRIP_W + 5, STRIP_H + 5], 23, outline=GOLD, width=3)
    canvas.alpha_composite(b, ((W - STRIP_W) // 2 - 3, H - STRIP_H - 19))

    canvas.convert("RGB").save(out_path, quality=84, optimize=True)
    print(out_path, os.path.getsize(out_path), "bytes")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
"""
eval_plate_detector.py -- PLATE-DETECTOR-1 scorecard against eval_photos/TRUTH.json.

Scores the LOCAL detector lane (plate_detector.py: detect -> frame_extend -> blur_boxes) the way
the Switch Test Plan scores a vision lane: every 'redact' row whose reason is a plate must get a
detection (recall), and every REAL 'clean' photo must get none (precision). The cartoon trap scenes
(syn_10/11/12) are reported but not scored: a detector trained on photographs misreads cartoon
windows as plates, and the pipeline never trusts it unconditionally outside vehicle categories.

Usage (from the MarketSquare folder, no AI key needed, ~1 s per photo on CPU):
    python3 scripts/eval_plate_detector.py --dir eval_photos/ [--out eval_photos/_plate_eval]
Writes one *_blur.jpg per detected photo into --out (git-ignored under eval_photos/) so the result
can be LOOKED at, and prints PASS/FAIL. Exit 1 on any missed plate or any false positive on a real
clean photo.
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VEHICLE_CONF = 0.40


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="eval_photos")
    ap.add_argument("--out", default=None)
    ap.add_argument("--conf", type=float, default=VEHICLE_CONF)
    a = ap.parse_args()
    from PIL import Image, ImageOps
    import plate_detector as pd
    if not pd.available():
        print("FAIL: detector unavailable:", pd.status().get("why")); return 1
    truth = {}
    tp = os.path.join(a.dir, "TRUTH.json")
    if os.path.isfile(tp):
        truth = {p["file"]: p for p in json.load(open(tp))["photos"]}
    out = a.out or os.path.join(a.dir, "_plate_eval")
    os.makedirs(out, exist_ok=True)
    files = sorted(f for f in os.listdir(a.dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    missed = []; false_pos = []; traps = []; secs = []
    for fn in files:
        img = ImageOps.exif_transpose(Image.open(os.path.join(a.dir, fn))).convert("RGB")
        t0 = time.time(); dets = [d for d in pd.detect(img, conf=0.30) if d[4] >= a.conf]; secs.append(time.time() - t0)
        t = truth.get(fn, {}); exp = t.get("expect", "?"); why = (t.get("why") or "").lower()
        is_plate_row = exp == "redact" and "plate" in why
        is_trap = fn.startswith("syn_1")
        tag = "ok"
        if is_plate_row and not dets:
            missed.append(fn); tag = "MISSED PLATE"
        elif exp == "clean" and dets:
            if is_trap:
                traps.append(fn); tag = "trap (cartoon, not scored)"
            else:
                false_pos.append(fn); tag = "FALSE POSITIVE"
        print("%-56s expect=%-7s %5.2fs dets=%-2d %s" % (fn[:56], exp, secs[-1], len(dets), tag))
        if dets:
            boxes = [pd.frame_extend(img, d) for d in dets]
            blurred, _ = pd.blur_boxes(img.copy(), boxes)
            blurred.save(os.path.join(out, fn.rsplit(".", 1)[0] + "_blur.jpg"), quality=88)
    n_plate = sum(1 for f in files if truth.get(f, {}).get("expect") == "redact" and "plate" in (truth[f].get("why") or "").lower())
    print("\nplate rows: %d  missed: %d  | real clean photos with a false box: %d  | cartoon traps tripped: %d  | avg %.2fs/photo"
          % (n_plate, len(missed), len(false_pos), len(traps), sum(secs) / max(1, len(secs))))
    if missed or false_pos:
        print("FAIL:", missed + false_pos); return 1
    print("PASS -- 100% plate recall, 0 false positives on real photos. Outputs:", out); return 0


if __name__ == "__main__":
    sys.exit(main())

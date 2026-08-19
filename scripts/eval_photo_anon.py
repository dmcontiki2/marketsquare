#!/usr/bin/env python3
"""
eval_photo_anon.py — Switch Test Plan step 1 for the photo-anon lane (RUL-032).

Runs the REAL scan (+ optional refine) from bea_main against a folder of eval
photos on a chosen provider lane, and reports per-photo verdicts, labels and
boxes so recall can be scored against truth. 100% plate recall on the eval set
is the bar before ANY lane change takes traffic (AI_PHOTO_COST_MODEL.xlsx,
'Switch Test Plan'; Haiku already lost this task once by being cheapest).

Usage (from the MarketSquare folder, key present in env or server .env):
    python3 scripts/eval_photo_anon.py --provider gemini  --dir eval_photos/
    python3 scripts/eval_photo_anon.py --provider openai  --dir eval_photos/   # baseline to beat
Writes eval_photo_anon_<provider>_<ts>.json next to the photos: one record per
photo (verdict, confidence, labels, regions, subject, tokens). Boxes are
0-1000 normalized — overlay them on the photo to eyeball tightness (IoU).
"""
import argparse, base64, io, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, help="gemini | openai | anthropic | scaleway")
    ap.add_argument("--dir", required=True, help="folder of eval photos (jpg/png)")
    ap.add_argument("--category", default="Cars")
    ap.add_argument("--refine", action="store_true", help="also run the zoom-refine pass on flagged regions")
    args = ap.parse_args()

    from PIL import Image, ImageOps
    import bea_main  # heavy import: pulls the app; run on a machine with the repo DB layout

    out, folder = [], args.dir
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    if not files:
        sys.exit("no images in " + folder)
    for fn in files:
        img = ImageOps.exif_transpose(Image.open(os.path.join(folder, fn))).convert("RGB")
        probe = img.copy(); probe.thumbnail((1344, 1344), Image.LANCZOS)
        buf = io.BytesIO(); probe.save(buf, format="JPEG", quality=80)
        t0 = time.time()
        scan, it, ot, svd = bea_main._anon_photo_scan(
            base64.b64encode(buf.getvalue()).decode(), args.provider, args.category)
        rec = {"file": fn, "seconds": round(time.time() - t0, 2),
               "in_tokens": it, "out_tokens": ot,
               "served_by": list(svd) if svd else None,
               "scan": scan if scan else "SCAN FAILED"}
        if scan and args.refine and scan.get("regions"):
            rec["refined"] = bea_main._anon_refine_regions(
                img, scan["regions"], args.provider, args.category, "eval", "/eval")
        out.append(rec)
        v = scan.get("verdict") if scan else "FAIL"
        print(f"{fn:40s} {v:8s} conf={scan.get('confidence') if scan else '-'} "
              f"regions={len(scan.get('regions') or []) if scan else 0} labels={scan.get('labels') if scan else '-'}")
    dest = os.path.join(folder, f"eval_photo_anon_{args.provider}_{time.strftime('%Y%m%d-%H%M%S')}.json")
    json.dump(out, open(dest, "w"), indent=1)
    print("\nwrote", dest, "\nSCORING: every photo with a real plate/strip must be redact/reject "
          "(recall MUST be 100%); clean photos must be clean; boxes eyeballed for tightness.")

if __name__ == "__main__":
    main()

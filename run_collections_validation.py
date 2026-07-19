#!/usr/bin/env python3
"""
run_collections_validation.py — fire the LIVE collections AI validation (AI5
/listings/batch-cards on trustsquare.co) against every photo in
validation_test_photos/, exactly as the app does it (same endpoint, same
prompt, same seam-routed model — vision -> Haiku 4.5 as of 3 Jul 2026).

Cost: 2 Tuppence flat per run (max 10 photos), charged to SELLER_EMAIL.
Output: validation_test_photos/APP_VALIDATION_RESULT_<date>.json (raw drafts).

Usage:  python run_collections_validation.py
Stdlib only; PIL used for downscale if available (else photos sent as-is).
"""
import base64, json, os, sys, urllib.request, datetime

BEA = "https://trustsquare.co"
SELLER_EMAIL = "dmcontiki2@gmail.com"
CITY, SUBURB = "Cape Town", "Sea Point"
PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "validation_test_photos")

def load_images():
    exts = (".jpg", ".jpeg", ".png", ".webp")
    files = sorted(f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(exts))
    if not files:
        sys.exit(f"No photos in {PHOTO_DIR} — drop the item photos there first.")
    out = []
    try:
        from PIL import Image
        import io
        for f in files[:10]:
            img = Image.open(os.path.join(PHOTO_DIR, f)).convert("RGB")
            img.thumbnail((1344, 1344))
            buf = io.BytesIO(); img.save(buf, format="JPEG", quality=80)
            out.append((f, base64.b64encode(buf.getvalue()).decode()))
    except ImportError:
        for f in files[:10]:
            with open(os.path.join(PHOTO_DIR, f), "rb") as fh:
                out.append((f, base64.b64encode(fh.read()).decode()))
    return out

def main():
    imgs = load_images()
    names = [n for n, _ in imgs]
    print(f"Sending {len(imgs)} photo(s) to {BEA}/listings/batch-cards "
          f"(2T, account {SELLER_EMAIL}):")
    for n in names: print("  -", n)
    body = json.dumps({"images": [b for _, b in imgs], "city": CITY,
                       "suburb": SUBURB, "seller_email": SELLER_EMAIL}).encode()
    req = urllib.request.Request(BEA + "/listings/batch-cards", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read().decode())
    result["_photo_order"] = names
    result["_run_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    out = os.path.join(PHOTO_DIR, "APP_VALIDATION_RESULT_"
                       + datetime.date.today().isoformat() + ".json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"\nDrafts returned: {len(result.get('drafts', []))}  "
          f"Tuppence remaining: {result.get('tuppence_remaining')}")
    print("Saved:", out)
    for name, d in zip(names, result.get("drafts", [])):
        print(f"\n[{name}]\n  {d.get('title')}\n  condition={d.get('condition')}  "
              f"price={d.get('price_suggestion')}\n  {d.get('description')}")

if __name__ == "__main__":
    main()

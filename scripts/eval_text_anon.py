#!/usr/bin/env python3
"""
eval_text_anon.py -- TEXT-ANON-1 scorecard for the LOCAL half of the text lane (no AI key needed).

Runs text_anon.ocr + rule_class over a folder and reports, per photo, what the OCR read and what the rules
would blur BEFORE the LLM looks (phones, e-mails, websites, plates-as-text, long numbers). With a TRUTH_TEXT.json
beside the photos ({"photos":[{"file","must_blur":[..],"must_keep":[..]}]}) it scores the rule stage: a
must_blur string that the rules catch is a PASS for that string; a must_keep string the rules would blur is a FAIL.
The LLM half (names, business names, streets) is judged live, not here.

    python3 scripts/eval_text_anon.py --dir eval_photos/text [--out eval_photos/_text_eval]
Writes *_rules.jpg (rule-stage blur only) so the result can be looked at. Exit 1 on any must_keep blurred.
"""
import argparse, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default="eval_photos/text"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    from PIL import Image, ImageOps
    import text_anon as ta
    if not ta.available():
        print("FAIL: text_anon unavailable:", ta.status().get("why")); return 1
    truth = {}
    tp = os.path.join(a.dir, "TRUTH_TEXT.json")
    if os.path.isfile(tp):
        truth = {p["file"]: p for p in json.load(open(tp))["photos"]}
    out = a.out or os.path.join(a.dir, "_text_eval"); os.makedirs(out, exist_ok=True)
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    bad = []; secs = []
    for fn in sorted(f for f in os.listdir(a.dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))):
        img = ImageOps.exif_transpose(Image.open(os.path.join(a.dir, fn))).convert("RGB")
        t0 = time.time(); items = ta.ocr(img); secs.append(time.time() - t0)
        rules = [it for it in items if ta.rule_class(it["text"]) == "id"]
        ask = [it["text"] for it in items if ta.rule_class(it["text"]) is None]
        t = truth.get(fn, {})
        caught = [m for m in t.get("must_blur", []) if any(norm(m) in norm(r["text"]) or norm(r["text"]) in norm(m) for r in rules)]
        wrong = [k for k in t.get("must_keep", []) if any(norm(k) in norm(r["text"]) for r in rules)]
        if wrong: bad.append(fn)
        print("%-34s %4.2fs rules-blur=%s  ask-LLM=%s  %s%s" % (fn[:34], secs[-1], [r["text"] for r in rules], ask,
              ("rule-caught=%s " % caught) if caught else "", ("!! RULE OVER-BLUR %s" % wrong) if wrong else ""))
        if rules:
            im2, _ = ta.blur_items(img.copy(), rules); im2.save(os.path.join(out, fn.rsplit(".", 1)[0] + "_rules.jpg"), quality=88)
    print("\navg %.2fs/photo; %s" % (sum(secs) / max(1, len(secs)), "FAIL " + str(bad) if bad else "PASS (rule stage never blurs an allowed string)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

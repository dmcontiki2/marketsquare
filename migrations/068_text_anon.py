#!/usr/bin/env python3
"""068_text_anon.py -- TEXT-ANON-1 (David, 7 Oct 2026: "this same photo blurring method must also be used for all
photos uploaded everywhere ... number plates, names, surnames, business names, street names, addresses; what we do
allow is suburbs").

Makes the live box able to run text_anon.py: installs `rapidocr_onnxruntime` (PaddleOCR PP-OCRv3 models on
onnxruntime, Apache-2.0; the models ship inside the wheel, ~15 MB) and `pyyaml` into the app venv. Idempotent --
skipped when they already import. Touches no database. If the install fails the app still runs: text_anon.available()
is False, the gate behaves as it did on 6 Oct, and /health shows text_anon.ready=false.
Undo: set TEXT_ANON=off in the service environment.
"""
import os, sys, subprocess, importlib

APPLY = "--apply" in sys.argv
LIVE = os.getcwd()


def have(mod):
    try:
        importlib.import_module(mod); return True
    except Exception:
        return False


def main():
    missing = [m for m in ("yaml", "rapidocr_onnxruntime") if not have(m)]
    print("068: python %s; missing: %s" % (sys.executable, missing or "none"))
    if missing and APPLY:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check",
                            "rapidocr_onnxruntime", "pyyaml"], capture_output=True, text=True, timeout=900)
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        print("068: pip rc=%s %s" % (r.returncode, " | ".join(tail)))
        still = [m for m in ("yaml", "rapidocr_onnxruntime") if not have(m)]
        if still:
            print("068: FAILED -- still cannot import %s" % still); return 1
    try:
        sys.path.insert(0, LIVE)
        import text_anon as ta
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (640, 200), (255, 255, 255)); ImageDraw.Draw(im).text((20, 80), "082 555 1234  www.example.co.za", fill=(0, 0, 0))
        ok = ta.available(); items = ta.ocr(im)
        print("068: text_anon ready=%s smoke reads=%s rule=%s" % (ok, [i["text"] for i in items][:3], [ta.rule_class(i["text"]) for i in items][:3]))
    except Exception as e:
        print("068: smoke test could not run: %r" % (e,))
    return 0


if __name__ == "__main__":
    sys.exit(main())

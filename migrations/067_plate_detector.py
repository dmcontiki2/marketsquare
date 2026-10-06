#!/usr/bin/env python3
"""067_plate_detector.py -- PLATE-DETECTOR-1 (David, 6 Oct 2026: "to load a car and to have AI blur
the numberplate ... automatic, not blocking the photo ... the AI keeps on blotching a big blob").

Makes the live box able to run the local number-plate detector (plate_detector.py):
  1. installs `onnxruntime` + `numpy` into the app venv (the interpreter running this script),
     idempotent -- skipped when they already import;
  2. checks the model file  <live>/models/plate_detector.onnx  is present with the expected sha256.
     The model is a 171 MB binary and rides the MEDIA lane (media_push.bat, section "plate detector
     model"), never git. If it is absent this migration prints a loud line and still exits 0: the
     app degrades to yesterday's behaviour (plate_detector.available() is False, both stages are
     no-ops) and /health shows plate_detector.ready=false, which is the signal to run media_push.

Touches no database. Undo: nothing to undo -- remove the model file to switch the lane off, or set
PLATE_DETECTOR=off in the service environment.
"""
import os, sys, hashlib, subprocess, importlib

APPLY = "--apply" in sys.argv
LIVE = os.getcwd()
MODEL = os.path.join(LIVE, "models", "plate_detector.onnx")
SHA = None
try:
    sys.path.insert(0, LIVE)
    import plate_detector as _pd
    SHA = _pd.MODEL_SHA256
except Exception as e:
    print("067: plate_detector.py not importable beside this script (%r) -- hash check skipped" % (e,))


def have(mod):
    try:
        importlib.import_module(mod); return True
    except Exception:
        return False


def main():
    rc = 0
    missing = [m for m in ("numpy", "onnxruntime") if not have(m)]
    print("067: python %s; missing packages: %s" % (sys.executable, missing or "none"))
    if missing and APPLY:
        cmd = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", "onnxruntime", "numpy"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        print("067: pip rc=%s %s" % (r.returncode, " | ".join(tail)))
        still = [m for m in ("numpy", "onnxruntime") if not have(m)]
        if still:
            print("067: FAILED -- still cannot import %s" % still); return 1
        print("067: onnxruntime + numpy installed")
    os.makedirs(os.path.join(LIVE, "models"), exist_ok=True)
    if not os.path.isfile(MODEL):
        print("067: !! MODEL MISSING at %s -- run media_push.bat (section: plate detector model). "
              "App runs as before until then (/health plate_detector.ready=false)." % MODEL)
        return 0
    if SHA:
        h = hashlib.sha256()
        with open(MODEL, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        ok = h.hexdigest() == SHA
        print("067: model %s MB sha256 %s -> %s" % (os.path.getsize(MODEL) // (1 << 20), h.hexdigest()[:12], "OK" if ok else "MISMATCH"))
        if not ok:
            print("067: !! hash mismatch -- the detector will refuse this file; re-run media_push.bat"); return 0
    if not missing or APPLY:
        try:
            import plate_detector as pd
            from PIL import Image
            im = Image.new("RGB", (640, 480), (90, 90, 90))
            ok = pd.available(); d = pd.detect(im)
            print("067: detector ready=%s smoke=%s status=%s" % (ok, d, {k: pd.status().get(k) for k in ("why", "load_ms")}))
        except Exception as e:
            print("067: smoke test could not run: %r" % (e,))
    return rc


if __name__ == "__main__":
    sys.exit(main())

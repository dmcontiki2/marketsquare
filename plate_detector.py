#!/usr/bin/env python3
"""
plate_detector.py -- PLATE-DETECTOR-1 (David, 6 Oct 2026): a dedicated, local number-plate
detector that returns the plate to the PIXEL, so the blur can be plate-shaped.

Why this exists. The photo anonymiser asked a general vision LLM to NAME coordinates
(0-1000) for the plate. An LLM reads a photo well and measures it badly: its boxes land
5-10% of the frame off, sometimes below the plate entirely (listing 246, 11 Jul 2026).
Every mitigation since (generous boxes, zoom-refine, verify-and-repaint rounds, the
last-resort rung) stacked more blur on the same photo -- that stacking is the "big blob"
David, Dave jnr and Maroushka kept seeing. The tools that do this easily use a small
detector trained for plates, not an LLM. This is that detector.

Model: RT-DETRv2 (ResNet-50) fine-tuned for licence plates --
       justjuu/rtdetr-v2-license-plate-detection, Apache-2.0 (no AGPL network clause),
       exported to ONNX (fixed 640x640 input). Runs on the Hetzner box's CPU through
       onnxruntime: ~0.5-1.3 s per photo, zero per-photo cost, nothing leaves the server.
       Chosen over the YOLO plate models on the Hub because those are AGPL-3.0, which
       TrustSquare's closed source cannot carry.

Eval (scripts/eval_plate_detector.py, eval_photos/TRUTH.json): 100% plate recall on every
'redact' row, including the tiny background plate (listing-246 class) and the two-plate
frame; 0 false positives on the real clean photos. The cartoon trap scenes fool it (they
fool any photo-trained detector), which is why the pipeline only trusts it unconditionally
in the vehicle categories and asks the LLM to corroborate elsewhere (see bea_main).

Fail-safe: anything missing (package, model file, hash mismatch, runtime error) makes
available() False and detect() return [] -- the pipeline then behaves exactly as before.

Public surface:
    available() -> bool
    status()    -> dict (for /health and the dashboard)
    detect(pil_image, conf=0.30) -> [(x0, y0, x1, y1, conf), ...] in 0-1000 frame coords
    frame_extend(pil_image, box) -> box widened to the plate frame (dealer strip under/over the plate)
"""
import os, sys, time, hashlib, logging, threading

_log = logging.getLogger("plate_detector")

MODEL_FILE = "plate_detector.onnx"
MODEL_SHA256 = "8f06b8d1aaf9950e093a0a7ce5c9c2a3ef8e77ea30f962144aaacab75feb7b8f"
MODEL_SOURCE = "justjuu/rtdetr-v2-license-plate-detection (Apache-2.0), ONNX export 6 Oct 2026"
INPUT = 640

_lock = threading.Lock()
_sess = None
_state = {"ready": False, "why": "not loaded", "path": None, "load_ms": None, "calls": 0, "avg_ms": None}


def model_path():
    p = os.environ.get("PLATE_MODEL_PATH")
    if p:
        return p
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "models", MODEL_FILE)


def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _load():
    """One-time session load; never raises. Sets _state."""
    global _sess
    if _sess is not None or _state["why"] == "disabled":
        return _sess
    with _lock:
        if _sess is not None:
            return _sess
        t0 = time.time()
        path = model_path()
        _state["path"] = path
        try:
            if os.environ.get("PLATE_DETECTOR", "on").strip().lower() == "off":
                _state.update(ready=False, why="disabled"); return None
            import numpy as np  # noqa: F401
            import onnxruntime as ort
        except Exception as e:
            _state.update(ready=False, why="onnxruntime/numpy missing: %r" % (e,)); return None
        if not os.path.isfile(path):
            _state.update(ready=False, why="model file missing: %s" % path); return None
        try:
            if os.environ.get("PLATE_MODEL_SKIP_HASH") != "1":
                h = _sha256(path)
                if h != MODEL_SHA256:
                    _state.update(ready=False, why="model hash mismatch (%s...)" % h[:12]); return None
            so = ort.SessionOptions()
            so.intra_op_num_threads = int(os.environ.get("PLATE_THREADS") or 2)   # leave CPU for uvicorn
            so.inter_op_num_threads = 1
            so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            s = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
            _sess = s
            _state.update(ready=True, why="", load_ms=int((time.time() - t0) * 1000))
            _log.info("plate detector ready (%s, %d ms)", os.path.basename(path), _state["load_ms"])
        except Exception as e:
            _state.update(ready=False, why="session load failed: %r" % (e,)); _sess = None
        return _sess


def available():
    return _load() is not None


def status():
    d = dict(_state)
    d["model"] = MODEL_SOURCE
    return d


def _plausible(x0, y0, x1, y1, W, H):
    """Geometry sanity: a mounted plate is a small, wide-ish rectangle. Aspect is judged in
    PIXELS (0-1000 coords are not square on a 3:2 frame). A plate photographed at 40 degrees
    gets a near-square axis-aligned box, so the aspect floor is loose (0.85)."""
    w = x1 - x0; h = y1 - y0
    if w <= 0 or h <= 0:
        return False
    area = (w / 1000.0) * (h / 1000.0)
    if area < 0.00008 or area > 0.14:       # from a far background plate up to a close-up plate
        return False
    asp = (w * W) / float(h * H)
    return 0.85 <= asp <= 8.5


def detect(img, conf=0.30, max_boxes=8):
    """Detect number plates. img: PIL image (any mode). Returns [(x0,y0,x1,y1,conf)] in 0-1000
    coords of the full frame, highest confidence first. Never raises; [] when unavailable."""
    s = _load()
    if s is None:
        return []
    try:
        import numpy as np
        from PIL import Image
        t0 = time.time()
        W, H = img.size
        im = img.convert("RGB").resize((INPUT, INPUT), Image.BILINEAR)
        x = np.asarray(im, dtype=np.float32) / 255.0            # HWC, 0..1 -- RT-DETR: rescale only, no mean/std
        x = np.transpose(x, (2, 0, 1))[None, ...]                # NCHW
        x = np.ascontiguousarray(x)
        logits, boxes = s.run(["logits", "pred_boxes"], {"pixel_values": x})
        sc = 1.0 / (1.0 + np.exp(-logits[0, :, 0]))               # (300,) sigmoid, single class
        order = np.argsort(-sc)
        out = []
        for i in order:
            c = float(sc[i])
            if c < conf:
                break
            cx, cy, bw, bh = (float(v) for v in boxes[0, i])     # normalised cxcywh
            x0 = max(0.0, (cx - bw / 2.0) * 1000.0); x1 = min(1000.0, (cx + bw / 2.0) * 1000.0)
            y0 = max(0.0, (cy - bh / 2.0) * 1000.0); y1 = min(1000.0, (cy + bh / 2.0) * 1000.0)
            if not _plausible(x0, y0, x1, y1, W, H):
                continue
            if (x1 - x0) * W / 1000.0 < 8 or (y1 - y0) * H / 1000.0 < 5:
                continue
            # DETR has no NMS; drop near-duplicates of a stronger box
            dup = False
            for (ax0, ay0, ax1, ay1, _c) in out:
                iw = max(0.0, min(x1, ax1) - max(x0, ax0)); ih = max(0.0, min(y1, ay1) - max(y0, ay0))
                inter = iw * ih
                if inter <= 0:
                    continue
                union = (x1 - x0) * (y1 - y0) + (ax1 - ax0) * (ay1 - ay0) - inter
                if union > 0 and inter / union > 0.5:
                    dup = True; break
                # or mostly inside the stronger box
                if inter / ((x1 - x0) * (y1 - y0)) > 0.8:
                    dup = True; break
            if dup:
                continue
            out.append((int(round(x0)), int(round(y0)), int(round(x1 + 0.5)), int(round(y1 + 0.5)), round(c, 3)))
            if len(out) >= max_boxes:
                break
        ms = (time.time() - t0) * 1000.0
        n = _state["calls"]
        _state["avg_ms"] = int(ms if not _state["avg_ms"] else (_state["avg_ms"] * n + ms) / (n + 1))
        _state["calls"] = n + 1
        return out
    except Exception as e:
        _log.warning("plate detect failed: %r", e)
        return []


def _plate_h_px(x0, y0, x1, y1, W, H):
    """Estimated height of the plate itself in pixels. A skewed plate's axis-aligned box is
    taller than the plate, so the estimate is capped at box-width / 2.5."""
    bw = (x1 - x0) * W / 1000.0; bh = (y1 - y0) * H / 1000.0
    return max(4.0, min(bh, bw / 2.5))


def frame_extend(img, box, down=0.35, up=0.15, side=0.04):
    """Widen a plate box to the plate FRAME: dealer surrounds print the dealership's name and
    phone number on a strip directly under (sometimes over) the plate, inside the frame. A fixed
    margin of 35% of the plate height below, 15% above and 4% of the width each side covers that
    strip on every frame style, deterministically, for ~1.5x the plate area. Coords 0-1000."""
    try:
        x0, y0, x1, y1 = (float(v) for v in box[:4])
        W, H = img.size
        ph = _plate_h_px(x0, y0, x1, y1, W, H)
        dy_down = ph * down * 1000.0 / H; dy_up = ph * up * 1000.0 / H
        dx = (x1 - x0) * side
        return (max(0, int(x0 - dx)), max(0, int(y0 - dy_up)),
                min(1000, int(round(x1 + dx))), min(1000, int(round(y1 + dy_down)))) + tuple(box[4:])
    except Exception:
        return box


def blur_boxes(img, boxes):
    """Plate-shaped blur: each box (0-1000 coords) gets a SMALL margin (6% of its width, 12% of
    its height, >= 3 px), a strong Gaussian blur (radius 0.4 x plate height, >= 8 px -- the
    characters are ~0.6 x plate height, so nothing stays legible), and a rounded-rectangle mask
    with a 2 px feather so there is no hard edge and no halo. Nothing outside the margin is
    touched. Returns (img, n_applied). This deliberately does NOT reuse the LLM-lane painter
    (_anon_photo_redact), whose wide feather and outward margin are part of the blob look."""
    from PIL import Image, ImageFilter, ImageDraw
    W, H = img.size
    n = 0
    for b in boxes:
        x0, y0, x1, y1 = (float(v) for v in b[:4])
        X0 = x0 * W / 1000.0; X1 = x1 * W / 1000.0; Y0 = y0 * H / 1000.0; Y1 = y1 * H / 1000.0
        bw = X1 - X0; bh = Y1 - Y0
        if bw < 4 or bh < 3:
            continue
        px = max(3.0, bw * 0.06); py = max(3.0, bh * 0.12)
        X0 = max(0, int(X0 - px)); Y0 = max(0, int(Y0 - py))
        X1 = min(W, int(round(X1 + px))); Y1 = min(H, int(round(Y1 + py)))
        if X1 - X0 < 4 or Y1 - Y0 < 3:
            continue
        rad = max(8, int(round(_plate_h_px(x0, y0, x1, y1, W, H) * 0.4)))
        m = rad * 2 + 4                                   # context so the blur has real pixels to average
        CX0 = max(0, X0 - m); CY0 = max(0, Y0 - m); CX1 = min(W, X1 + m); CY1 = min(H, Y1 + m)
        crop = img.crop((CX0, CY0, CX1, CY1))
        blurred = crop.filter(ImageFilter.GaussianBlur(rad))
        # second light pass over the blurred interior kills any residual stroke rhythm
        blurred = blurred.filter(ImageFilter.GaussianBlur(max(2, rad // 3)))
        mask = Image.new("L", crop.size, 0)
        d = ImageDraw.Draw(mask)
        r = max(3, int(min(X1 - X0, Y1 - Y0) * 0.18))
        try:
            d.rounded_rectangle([X0 - CX0, Y0 - CY0, X1 - CX0 - 1, Y1 - CY0 - 1], radius=r, fill=255)
        except Exception:
            d.rectangle([X0 - CX0, Y0 - CY0, X1 - CX0 - 1, Y1 - CY0 - 1], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2))
        img.paste(blurred, (CX0, CY0), mask)
        n += 1
    return img, n


if __name__ == "__main__":
    # smoke: python3 plate_detector.py <image> [...]
    from PIL import Image, ImageOps
    for f in sys.argv[1:]:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        t0 = time.time(); d = detect(im); dt = time.time() - t0
        print("%-60s %5.2fs %s" % (os.path.basename(f)[:60], dt, d))
    print(status())

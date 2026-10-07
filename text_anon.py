#!/usr/bin/env python3
"""
text_anon.py -- TEXT-ANON-1 (David, 7 Oct 2026): "this same photo blurring method must also be used
for all photos uploaded everywhere to detect and remove anonymity violations -- number plates, names,
surnames, business names, street names, addresses, etc.; what we do allow is suburbs."

Same division of labour as PLATE-DETECTOR-1:
  local OCR  -> WHERE every piece of text is, to the pixel (RapidOCR = PaddleOCR PP-OCRv3 models on
                onnxruntime, Apache-2.0, ~0.3 s per photo on the box's CPU, nothing leaves the server)
  rules      -> the identifiers that need no judgement: phone numbers, e-mail addresses, websites,
                registration plates written as text, ID / registration numbers -> blurred BEFORE the
                LLM looks (deterministic, R0)
  LLM        -> the judgement call only: WHICH of the remaining OCR strings identify a person, a
                business or an exact place (name, surname, agency, farm, producer, street, address),
                answered as INDICES into our list -- never as coordinates. Suburb, city, province and
                country names are allowed and said so in the prompt.
  OCR again  -> when the LLM flags a region whose text the full-frame OCR missed (small or curved
                label), OCR runs once more on a 2x zoom of THAT region and returns exact glyph boxes.

Fail-safe: no package / any error -> available() False, every function returns the input untouched
and the gate behaves as it did before (the LLM lane under RUL-033).

Public surface:
    available() / status()
    ocr(img)                      -> [item], item = {"i", "text", "conf", "box": (x0,y0,x1,y1) 0-1000, "quad": [(x,y)..] px}
    ocr_region(img, box0_1000)    -> [item] found inside a 2x zoom of that region (full-frame coords)
    rule_class(text)              -> "id" | "allow" | None
    blur_items(img, items)        -> (img, n)   polygon-shaped blur with a small margin
    prompt_list(items)            -> the numbered list handed to the LLM
"""
import os, re, time, logging, threading

_log = logging.getLogger("text_anon")
_lock = threading.Lock()
_eng = None
_state = {"ready": False, "why": "not loaded", "calls": 0, "avg_ms": None}

PROBE_MAX = 1344          # same probe size the LLM scan uses
MIN_CONF = 0.45           # below this an OCR read is noise (kept for the LLM list only if >= 0.30)


def _load():
    global _eng
    if _eng is not None or _state["why"] == "disabled":
        return _eng
    with _lock:
        if _eng is not None:
            return _eng
        t0 = time.time()
        try:
            if os.environ.get("TEXT_ANON", "on").strip().lower() == "off":
                _state.update(ready=False, why="disabled"); return None
            import numpy  # noqa: F401
            from rapidocr_onnxruntime import RapidOCR
            # the bundled config detects on a 736px short side; limit by the LONG side at the probe size instead
            cfg = None
            try:
                import yaml, rapidocr_onnxruntime as _r
                base = os.path.join(os.path.dirname(_r.__file__), "config.yaml")
                c = yaml.safe_load(open(base, encoding="utf-8"))
                c["Det"]["limit_side_len"] = PROBE_MAX; c["Det"]["limit_type"] = "max"
                for k in ("Det", "Cls", "Rec"):
                    c[k]["intra_op_num_threads"] = int(os.environ.get("TEXT_ANON_THREADS") or 2)
                cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "text_anon_ocr.yaml")
                os.makedirs(os.path.dirname(cfg), exist_ok=True)
                with open(cfg, "w", encoding="utf-8") as fh:
                    yaml.safe_dump(c, fh)
            except Exception as _ce:
                _log.warning("text_anon: using RapidOCR defaults (%r)", _ce); cfg = None
            _eng = RapidOCR(config_path=cfg) if cfg else RapidOCR()
            _state.update(ready=True, why="", load_ms=int((time.time() - t0) * 1000))
            _log.info("text anonymiser ready (RapidOCR, %d ms)", _state["load_ms"])
        except Exception as e:
            _state.update(ready=False, why="rapidocr_onnxruntime missing or failed: %r" % (e,)); _eng = None
        return _eng


def available():
    return _load() is not None


def status():
    return dict(_state)


# ── rules: identifiers that need no judgement ──────────────────────────────────────────────
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().\-]{7,}\d)(?!\d)")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+", re.I)
_URL = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+\.(?:co\.za|com|org|net|africa|biz|info|online|shop|io|za)\b(?:/\S*)?", re.I)
# SA registration plate shapes written as text: 'CA 213 456', 'HP 63 CS GP', 'ND 559-128', 'BB77GP', 'MAROUSH GP' (vanity + province)
_PLATE = re.compile(r"\b(?:[A-Z]{1,3}\s?\d{2,3}\s?\d{3}|[A-Z]{2}\s?\d{2,3}\s?[A-Z]{2}\s?(?:GP|L|MP|NW|ZN|EC|WC|NC|FS)|[A-Z]{2,7}\s?(?:GP|ZN|MP|EC|WC|NC|FS|NW|L))\b")
_LONGNUM = re.compile(r"(?<!\d)\d{9,}(?!\d)")        # ID numbers, company reg numbers, account numbers
_PRICE = re.compile(r"^\s*(?:R|ZAR|\$|€|£)\s?\d[\d\s,.]*\s*(?:k|K|m|M|pm|p/m|neg)?\s*$")
_GENERIC = {"stop", "sale", "for sale", "sold", "open", "closed", "to let", "exit", "entrance", "parking",
            "no entry", "welcome", "push", "pull", "wc", "toilet", "yield", "slow", "ford", "toyota", "vw",
            "bmw", "audi", "nissan", "hyundai", "kia", "honda", "mazda", "suzuki", "renault", "isuzu",
            "mercedes", "volkswagen", "chevrolet", "opel", "peugeot", "volvo", "samsung", "sony", "lg", "hp",
            "apple", "nikon", "canon", "dell", "lenovo", "bosch", "makita", "defy", "hisense"}


def rule_class(text):
    """'id' = identifying without judgement (blur now); 'allow' = plainly harmless; None = ask the LLM."""
    t = (text or "").strip().strip("-–—:;,.|*")
    if not t:
        return "allow"
    digits = sum(ch.isdigit() for ch in t)
    if _EMAIL.search(t) or _URL.search(t):
        return "id"
    if digits >= 9 and (_PHONE.search(t) or _LONGNUM.search(t.replace(" ", ""))):
        return "id"
    up = t.upper()
    if _PLATE.search(up) and digits >= 2:
        return "id"
    if _PRICE.match(t):
        return "allow"
    if t.lower() in _GENERIC:
        return "allow"
    if len(t) <= 1:
        return "allow"
    return None


# ── OCR ────────────────────────────────────────────────────────────────────────────────────
def _run(np_img):
    eng = _load()
    if eng is None:
        return []
    out = eng(np_img)
    res = out[0] if isinstance(out, tuple) else out
    return res or []


def ocr(img, min_conf=0.30):
    """Full-frame OCR on a PROBE_MAX-bounded copy. Items carry frame coords (0-1000) and px quads."""
    if _load() is None:
        return []
    try:
        import numpy as np
        from PIL import Image
        t0 = time.time()
        W, H = img.size
        probe = img.convert("RGB")
        s = 1.0
        if max(W, H) > PROBE_MAX:
            s = PROBE_MAX / float(max(W, H))
            probe = probe.resize((max(1, int(W * s)), max(1, int(H * s))), Image.LANCZOS)
        items = []
        for k, r in enumerate(_run(np.asarray(probe))):
            try:
                quad, text, conf = r[0], str(r[1]), float(r[2])
            except Exception:
                continue
            if conf < min_conf or not text.strip():
                continue
            pts = [(float(p[0]) / s, float(p[1]) / s) for p in quad]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            box = (max(0, int(min(xs) * 1000 / W)), max(0, int(min(ys) * 1000 / H)),
                   min(1000, int(max(xs) * 1000 / W + 0.5)), min(1000, int(max(ys) * 1000 / H + 0.5)))
            items.append({"i": len(items), "text": text.strip(), "conf": round(conf, 2), "box": box, "quad": pts})
        ms = (time.time() - t0) * 1000.0
        n = _state["calls"]
        _state["avg_ms"] = int(ms if not _state["avg_ms"] else (_state["avg_ms"] * n + ms) / (n + 1))
        _state["calls"] = n + 1
        return items
    except Exception as e:
        _log.warning("text_anon ocr failed: %r", e)
        return []


def ocr_region(img, box, up=2.0, pad=0.5, min_conf=0.30):
    """OCR a 2x zoom of the region (0-1000 box, widened by `pad` of its size each way) -- for the
    small or curved label the LLM saw and the full-frame pass missed. Items in full-frame coords."""
    if _load() is None:
        return []
    try:
        import numpy as np
        from PIL import Image
        W, H = img.size
        x0, y0, x1, y1 = (float(v) for v in box[:4])
        bw = max(1.0, x1 - x0); bh = max(1.0, y1 - y0)
        cx0 = max(0, int((x0 - bw * pad) * W / 1000)); cy0 = max(0, int((y0 - bh * pad) * H / 1000))
        cx1 = min(W, int((x1 + bw * pad) * W / 1000 + 0.5)); cy1 = min(H, int((y1 + bh * pad) * H / 1000 + 0.5))
        if cx1 - cx0 < 16 or cy1 - cy0 < 10:
            return []
        crop = img.convert("RGB").crop((cx0, cy0, cx1, cy1))
        sc = up
        if max(crop.size) * sc > 2000:
            sc = 2000.0 / max(crop.size)
        if sc != 1.0:
            crop = crop.resize((max(1, int(crop.size[0] * sc)), max(1, int(crop.size[1] * sc))), Image.LANCZOS)
        items = []
        for r in _run(np.asarray(crop)):
            try:
                quad, text, conf = r[0], str(r[1]), float(r[2])
            except Exception:
                continue
            if conf < min_conf or not text.strip():
                continue
            pts = [(cx0 + float(p[0]) / sc, cy0 + float(p[1]) / sc) for p in quad]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            bx = (max(0, int(min(xs) * 1000 / W)), max(0, int(min(ys) * 1000 / H)),
                  min(1000, int(max(xs) * 1000 / W + 0.5)), min(1000, int(max(ys) * 1000 / H + 0.5)))
            items.append({"i": len(items), "text": text.strip(), "conf": round(conf, 2), "box": bx, "quad": pts})
        return items
    except Exception as e:
        _log.warning("text_anon ocr_region failed: %r", e)
        return []


def prompt_list(items, limit=40):
    """The numbered list the LLM judges. Plain, short, no coordinates."""
    rows = []
    for it in items[:limit]:
        t = it["text"].replace("\n", " ")[:60].replace('"', "'")
        rows.append('%d: "%s"' % (it["i"], t))
    return "; ".join(rows)


# ── blur ───────────────────────────────────────────────────────────────────────────────────
def blur_items(img, items, margin=0.18):
    """Polygon-shaped blur of each OCR item (its quad widened by `margin` of its height, so the
    glyph strokes at the edge never show), Gaussian radius 0.45 x text height (>= 6 px), 2 px feather.
    Returns (img, n)."""
    from PIL import Image, ImageFilter, ImageDraw
    import math
    W, H = img.size
    n = 0
    for it in items:
        try:
            q = it.get("quad")
            if not q or len(q) < 4:
                x0, y0, x1, y1 = it["box"]
                q = [(x0 * W / 1000.0, y0 * H / 1000.0), (x1 * W / 1000.0, y0 * H / 1000.0),
                     (x1 * W / 1000.0, y1 * H / 1000.0), (x0 * W / 1000.0, y1 * H / 1000.0)]
            cx = sum(p[0] for p in q) / 4.0; cy = sum(p[1] for p in q) / 4.0
            # text height = the shorter side of the quad
            e1 = math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]); e2 = math.hypot(q[2][0] - q[1][0], q[2][1] - q[1][1])
            th = max(4.0, min(e1, e2)); tw = max(e1, e2)
            grow = max(2.0, th * margin)
            poly = []
            for (px, py) in q:
                dx = px - cx; dy = py - cy; d = math.hypot(dx, dy) or 1.0
                poly.append((px + dx / d * grow * 1.4, py + dy / d * grow * 1.4))
            xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
            X0 = max(0, int(min(xs))); Y0 = max(0, int(min(ys))); X1 = min(W, int(max(xs)) + 1); Y1 = min(H, int(max(ys)) + 1)
            if X1 - X0 < 3 or Y1 - Y0 < 3:
                continue
            rad = max(6, int(round(th * 0.45)))
            m = rad * 2 + 4
            CX0 = max(0, X0 - m); CY0 = max(0, Y0 - m); CX1 = min(W, X1 + m); CY1 = min(H, Y1 + m)
            crop = img.crop((CX0, CY0, CX1, CY1))
            blurred = crop.filter(ImageFilter.GaussianBlur(rad)).filter(ImageFilter.GaussianBlur(max(2, rad // 3)))
            mask = Image.new("L", crop.size, 0)
            ImageDraw.Draw(mask).polygon([(p[0] - CX0, p[1] - CY0) for p in poly], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(2))
            img.paste(blurred, (CX0, CY0), mask)
            n += 1
        except Exception as e:
            _log.warning("text_anon blur item failed: %r", e)
    return img, n


if __name__ == "__main__":
    import sys
    from PIL import Image, ImageOps
    for f in sys.argv[1:]:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        t0 = time.time(); its = ocr(im); dt = time.time() - t0
        print("%-50s %.2fs" % (os.path.basename(f)[:50], dt))
        for it in its:
            print("   %2d %-6s %.2f %-36s box=%s" % (it["i"], rule_class(it["text"]) or "ask", it["conf"], it["text"][:36], it["box"]))
    print(status())

"""status_card.py -- STATUS-CARD-1 (24 Sep 2026, proposal 2 of the casual-workers plan, inside RUL-146).

One tap after publishing makes a 1080x1920 WhatsApp-Status card for an advert: the role picture (or the
advert's own photo), the role and area, the rate, the trust badge, a QR code and the short link. Two calls
to action ride on it -- "Ask me on TrustSquare" (demand) and "Make your own advert, free" (supply) -- and
every link carries ?src=status so the door's funnel counts what the card sends.

Pure Pillow; the QR uses the `qrcode` package when present and degrades to the plain link when it is not.
No customer photo is ever fetched from outside the box: only files under STATIC_DIR are read.
"""
import os, io, re, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STATIC_DIR = os.environ.get("MS_STATIC_DIR") or "/var/www/marketsquare/static"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_BOOK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920

PALETTE = {  # category -> (background, accent, panel)
    "services":     ("#061715", "#16A97C", "#0c2824"),
    "tutors":       ("#0b1220", "#5b8def", "#121c33"),
    "property":     ("#160f0a", "#e08a3c", "#26180f"),
    "cars":         ("#0f0f14", "#8fa3ff", "#1a1a26"),
    "adventures":   ("#0a1610", "#6fd49a", "#12261a"),
    "collectors":   ("#1a1208", "#e6c15a", "#2a1f0e"),
    "local_market": ("#170a14", "#e87ba4", "#281226"),
}

def _font(size, bold=True):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_BOOK, size)
    except Exception:
        return ImageFont.load_default()

def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def _slug(s):
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")

def _role_picture(listing):
    """The advert's own first photo if it is a local static file, else the door's role picture, else None."""
    cands = []
    for u in (listing.get("medium_url"), listing.get("thumb_url")):
        if u and "/static/" in u:
            cands.append(os.path.join(STATIC_DIR, u.split("/static/", 1)[1].split("?")[0]))
    for key in (listing.get("service_type"), listing.get("subject"), listing.get("title", "").split(" — ")[0]):
        s = _slug(key)
        if s:
            cands.append(os.path.join(STATIC_DIR, "quick", "role_%s.jpg" % s))
    cat = _slug(listing.get("category"))
    cands.append(os.path.join(STATIC_DIR, "quick", {"services": "role_gardener", "property": "prop_garden"}.get(cat, "room_lounge") + ".jpg"))
    for p in cands:
        try:
            if os.path.isfile(p):
                return Image.open(p).convert("RGB")
        except Exception:
            continue
    return None

def _wrap(draw, text, font, max_w):
    words, lines, cur = (text or "").split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def _qr(url, size):
    try:
        import qrcode
        q = qrcode.QRCode(border=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
        q.add_data(url); q.make(fit=True)
        im = q.make_image(fill_color="black", back_color="white").convert("RGB")
        return im.resize((size, size), Image.NEAREST)
    except Exception:
        return None

def render(listing, link, make_link, first_name=None, trust=None):
    """listing: dict with title, category, service_type, area/suburb/city, price, medium_url/thumb_url.
    Returns PNG bytes."""
    cat = _slug(listing.get("category"))
    bg, accent, panel = PALETTE.get(cat, PALETTE["services"])
    im = Image.new("RGB", (W, H), _hex(bg))
    d = ImageDraw.Draw(im)
    # soft accent glow top-right
    glow = Image.new("RGB", (W, H), _hex(bg)); gd = ImageDraw.Draw(glow)
    gd.ellipse((520, -260, 1400, 620), fill=_hex(accent))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, glow, 0.35); d = ImageDraw.Draw(im)

    # photo panel
    pic = _role_picture(listing)
    px, py, pw, ph = 60, 150, W - 120, 880
    if pic is not None:
        r = max(pw / pic.width, ph / pic.height)
        pic = pic.resize((int(pic.width * r) + 1, int(pic.height * r) + 1), Image.LANCZOS)
        ox, oy = (pic.width - pw) // 2, (pic.height - ph) // 2
        pic = pic.crop((ox, oy, ox + pw, oy + ph))
        mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw, ph), 48, fill=255)
        im.paste(pic, (px, py), mask)
    else:
        d.rounded_rectangle((px, py, px + pw, py + ph), 48, fill=_hex(panel))
    # top wordmark
    d.text((60, 60), "TrustSquare", font=_font(44), fill=(255, 255, 255))
    d.text((W - 60 - d.textlength("trustsquare.co", font=_font(30, False)), 70), "trustsquare.co", font=_font(30, False), fill=(200, 220, 212))

    # trust badge
    if trust is not None:
        bx, by, br = W - 60 - 120, py + ph - 120, 110
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=_hex(accent))
        t1 = _font(64); s = "%d" % int(trust)
        d.text((bx - d.textlength(s, font=t1) / 2, by - 58), s, font=t1, fill=_hex(bg))
        t2 = _font(24); s2 = "TRUST SCORE"
        d.text((bx - d.textlength(s2, font=t2) / 2, by + 18), s2, font=t2, fill=_hex(bg))

    # title block
    y = py + ph + 60
    role = (listing.get("service_type") or listing.get("title") or "").split(" — ")[0].strip()
    area = listing.get("area") or listing.get("suburb") or listing.get("city") or ""
    who = (first_name.strip().split()[0] if first_name and first_name.strip() else "")
    head = (who + " · " if who else "") + role
    for ln in _wrap(d, head, _font(92), W - 120)[:2]:
        d.text((60, y), ln, font=_font(92), fill=(255, 255, 255)); y += 104
    sub = " · ".join([s for s in (area, str(listing.get("availability") or "").strip(), str(listing.get("price") or "").strip()) if s])
    for ln in _wrap(d, sub, _font(46, False), W - 120)[:2]:
        d.text((60, y + 8), ln, font=_font(46, False), fill=(205, 226, 218)); y += 62
    y += 30

    # CTA panel with QR
    ch = 420
    d.rounded_rectangle((60, y, W - 60, y + ch), 40, fill=_hex(panel), outline=_hex(accent), width=3)
    qr = _qr(link, 300)
    if qr is not None:
        im.paste(qr, (100, y + 60))
        tx = 440
    else:
        tx = 100
    d.text((tx, y + 60), "Ask me on TrustSquare", font=_font(48), fill=(255, 255, 255))
    for i, ln in enumerate(_wrap(d, "Scan, or tap the link in this Status. Your name and number stay private until you both accept.", _font(32, False), W - 60 - tx - 40)[:4]):
        d.text((tx, y + 130 + i * 42), ln, font=_font(32, False), fill=(205, 226, 218))
    short = re.sub(r"[?&]src=[^&]*", "", link.replace("https://", ""))   # the QR and the shared text carry ?src=status; the printed link stays short
    d.text((tx, y + 320), short[:40], font=_font(30), fill=_hex(accent))

    # supply loop
    y2 = y + ch + 50
    d.rounded_rectangle((60, y2, W - 60, y2 + 150), 40, fill=_hex(accent))
    d.text((100, y2 + 30), "Make your own advert — free", font=_font(50), fill=_hex(bg))
    d.text((100, y2 + 96), make_link.replace("https://", ""), font=_font(30, False), fill=_hex(bg))

    out = io.BytesIO(); im.save(out, "PNG", optimize=True); return out.getvalue()

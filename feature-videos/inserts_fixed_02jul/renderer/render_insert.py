#!/usr/bin/env python3
"""
render_insert.py — TrustSquare feature-video "AI report scroll" insert renderer.
Rebuilt 02 Jul 2026 (replaces lost /tmp/insrender). PIL-based; matches the original
insert look (navy gradient bg, gold chip, phone frame, white screen, navy header card,
green delivered pill, section scroll) — same geometry as production-kit/inserts.py.

FIXES vs the 28-Jun renderer:
  1) TOFU: every char is filtered against the DejaVu cmap (fontTools); curated
     replacements for common emoji (checkmarks, warning, star, arrows). Zero tofu possible.
  2) RAW MARKDOWN: links [t](u) -> t, images dropped, **/*/` stripped, tables parsed
     into bullet rows (no more '-----' runs / mashed header rows), html-unescaped.
  3) DOUBLED HEADER: header card is laid out in flow (title wraps, subtitle drawn
     BELOW measured title height) — impossible to overlap; card height computed.
  4) BLACK VOID: tall page height = measured content height; scroll_max =
     max(0, tallH - screenH); crop always inside the white page. No void possible.
  Bonus: section previews end at word boundaries with an ellipsis (no mid-word cuts),
  and the whole page scrolls as one unit (no pinned-card clip artifact).

USAGE:
  python3 render_insert.py <video-id> [--probe] [--scale N] [--dur 12] [--outdir DIR]
    video-id : 02-heritage | 07-liquidation | 08-weekend | 09-exam | 10-offer | all
    --probe  : write 3 probe stills (start/mid/end) instead of the mp4
    --scale 1: 720x1280 (default). --scale 3: 2160x3840 for the 4K masters.
  Report sources: real-reports/<fn>.md ; maps from real-reports/ (see CFG).
"""
import os, re, sys, math, html, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = "/sessions/practical-focused-maxwell/mnt/Projects/MarketSquare/feature-videos"
RR   = f"{BASE}/real-reports"
OUTD = f"{BASE}/inserts_fixed_02jul"
FB   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPS  = 30

CFG = {
 "02-heritage": dict(md=f"{RR}/heritage_tour.md",
    title="Heritage Site Tour Planner", sub="Cape Town → Graskop → Kruger · 7 days",
    chip="Your tour · 5T delivered", pill="5T · delivered",
    map=f"{RR}/SAMPLE_route_ROAD.png"),
 "07-liquidation": dict(md=f"{RR}/collection_liquidation.md",
    title="Collection Liquidation Plan", sub="Stamps & coins estate · ~400 items",
    chip="Your report · 5T delivered", pill="5T · delivered", map=None),
 "08-weekend": dict(md=f"{RR}/weekend_itinerary.md",
    title="Weekend Adventure Itinerary", sub="Pretoria · two friends · under R1,000",
    chip="Your report · 3T delivered", pill="3T · delivered",
    map=f"{RR}/report_assets/testwknd_route.png"),
 "09-exam": dict(md=f"{RR}/study_plan.md",
    title="6-Week Matric Study Plan", sub="CAPS-NSC · Maths & Phys Sci · Pretoria",
    chip="Your plan · 3T delivered", pill="3T · delivered", map=None),
 "10-offer": dict(md=f"{RR}/offer_advisor.md",
    title="Offer Strategy Advisor", sub="Second-hand guitar amp · R4,500 ask",
    chip="Your report · 2T delivered", pill="2T · delivered", map=None),
}

# ---------- glyph safety (FIX 1) ----------
from fontTools.ttLib import TTFont
_cmap = set()
for _p in (FR, FB):
    _f = TTFont(_p, lazy=True)
    _cmap |= set(_f.getBestCmap().keys())
    _f.close()

PRE = {"✅":"✓", "✔️":"✓", "✔":"✓", "☑️":"✓",
       "❌":"✗", "⭐":"★", "➡️":"→", "➡":"→",
       "\U0001f449":"→", "⚠️":"⚠ ", "❗":"!", "⁉️":"!?"}
def glyph_safe(s):
    for k, v in PRE.items():
        s = s.replace(k, v)
    s = s.replace("️", "").replace("︎", "").replace("‍", "").replace("�", "")
    s = "".join(ch for ch in s if ord(ch) < 0x20 or ord(ch) in _cmap)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()

# ---------- markdown -> blocks (FIX 2) ----------
LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
def clean_inline(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)          # images out
    s = LINK.sub(lambda m: m.group(1), s)                 # links -> anchor text
    s = re.sub(r"<https?://[^>]+>", "", s)
    s = re.sub(r"\bhttps?://\S+", "", s)                  # bare URLs out
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)\*(?![\w*])", r"\1", s)
    s = s.replace("`", "").replace("~~", "")
    s = html.unescape(s)
    s = re.sub(r"^-{3,}$", "", s)
    s = re.sub(r"\s*-{4,}\s*", " ", s)                    # stray ---- runs
    return glyph_safe(s)

def parse_sections(md_path, skip_titles=("sources",)):
    raw = open(md_path, encoding="utf-8").read()
    raw = re.sub(r"```.*?```", "", raw, flags=re.S)       # code fences (JSON appendix) out
    lines = raw.split("\n")
    i = 0                                                  # drop leaked plain-text preamble
    while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\||[-*] |---)", lines[i].strip()):
        i += 1
    lines = lines[i:]
    secs, cur = [], None
    for ln in lines:
        t = ln.rstrip()
        m = re.match(r"^##\s+(.*)", t)
        if m and not t.startswith("###"):
            if cur and cur["blocks"]: secs.append(cur)
            title = clean_inline(m.group(1)).strip()
            cur = {"title": title, "blocks": []}
            continue
        if cur is None: continue
        s = t.strip()
        if not s or re.match(r"^-{3,}$", s) or s.startswith("# "):
            continue
        if re.match(r"^###\s+", s):
            cur["blocks"].append(("sub", clean_inline(re.sub(r"^###\s+", "", s))))
        elif s.startswith("|"):
            cells = [clean_inline(c) for c in s.strip("|").split("|")]
            if all(re.match(r"^:?-{2,}:?$", c.strip()) or not c.strip() for c in cells):
                cur["blocks"].append(("tsep",))
            else:
                cur["blocks"].append(("trow", [c for c in cells]))
        elif re.match(r"^>\s?", s):
            cur["blocks"].append(("p", clean_inline(re.sub(r"^>\s?", "", s))))
        elif re.match(r"^[-*+]\s+", s):
            cur["blocks"].append(("li", clean_inline(re.sub(r"^[-*+]\s+", "", s))))
        elif re.match(r"^\d+[.)]\s+", s):
            cur["blocks"].append(("li", clean_inline(s)))
        else:
            cur["blocks"].append(("p", clean_inline(s)))
    if cur and cur["blocks"]: secs.append(cur)
    return [x for x in secs if x["title"].lower().split(" ")[0].rstrip(":") not in skip_titles
            and not any(k in x["title"].lower() for k in skip_titles)]

def table_rows_to_bullets(blocks):
    """Group consecutive trow/tsep into bullet lines; first data row after a tsep-less
    start is treated as header and skipped when a separator follows it."""
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b[0] not in ("trow", "tsep"):
            out.append(b); i += 1; continue
        rows = []
        while i < len(blocks) and blocks[i][0] in ("trow", "tsep"):
            rows.append(blocks[i]); i += 1
        data, seen_sep, header_skipped = [], False, False
        for r in rows:
            if r[0] == "tsep": seen_sep = True; continue
            if not header_skipped and not seen_sep and len(rows) > 2:
                header_skipped = True; continue          # skip header row
            cells = [c for c in r[1] if c]
            if not cells: continue
            if len(cells) == 1: txt = cells[0]
            else:
                txt = f"{cells[0]} — {cells[1]}"
                if len(cells) > 2 and len(cells[2]) <= 28: txt += f"  ·  {cells[2]}"
            data.append(("li", txt))
        shown = data[:4]
        out.extend(shown)
        if len(data) > 4: out.append(("more", f"+ {len(data)-4} more rows in the full report …"))
    return out

# ---------- layout / drawing ----------
def F(path, size): return ImageFont.truetype(path, size)

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            while d.textlength(w, font=fnt) > maxw and len(w) > 4:  # ultra-long tokens
                k = len(w)
                while k > 1 and d.textlength(w[:k], font=fnt) > maxw: k -= 1
                lines.append(w[:k]); w = w[k:]
            cur = w
    if cur: lines.append(cur)
    return lines

NAVY_CARD = (30, 60, 100); TITLE_W = (255, 255, 255); SUB_C = (185, 200, 226)
SECT_C = (23, 62, 115); BODY_C = (52, 63, 84); SUBH_C = (35, 52, 86)
RULE_C = (222, 228, 238); MORE_C = (120, 132, 156); GRN = (34, 181, 115)

def build_tall(cfg, S):
    """Render the tall white report page at content scale CS=2*S (downscaled later). Returns PIL image (560*S wide)."""
    CS = 2 * S
    Wp = 560 * CS
    pad = 24 * CS
    img = Image.new("RGB", (Wp, 26000 * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_title = F(FB, 33 * CS); f_sub = F(FR, 18 * CS); f_pill = F(FB, 19 * CS)
    f_sect = F(FB, 26 * CS); f_subh = F(FB, 20 * CS); f_body = F(FR, 19 * CS)
    f_small = F(FR, 15 * CS); lp = 28 * CS
    y = 20 * CS
    # header card (FIX 3: flow layout)
    cx0, cx1 = 16 * CS, 544 * CS; cpad = 18 * CS
    tl = wrap(d, glyph_safe(cfg["title"]), f_title, cx1 - cx0 - 2 * cpad)[:2]
    sl = wrap(d, glyph_safe(cfg["sub"]), f_sub, cx1 - cx0 - 2 * cpad)[:2]
    th = len(tl) * 40 * CS + 10 * CS + len(sl) * 24 * CS
    card_h = th + 2 * cpad
    d.rounded_rectangle([cx0, y, cx1, y + card_h], radius=16 * CS, fill=NAVY_CARD)
    ty = y + cpad
    for l in tl: d.text((cx0 + cpad, ty), l, font=f_title, fill=TITLE_W); ty += 40 * CS
    ty += 10 * CS
    for l in sl: d.text((cx0 + cpad, ty), l, font=f_sub, fill=SUB_C); ty += 24 * CS
    y += card_h + 18 * CS
    # green pill, right aligned
    ptxt = glyph_safe(cfg["pill"]); pw = d.textlength(ptxt, font=f_pill) + 34 * CS; ph = 38 * CS
    d.rounded_rectangle([cx1 - pw, y, cx1, y + ph], radius=ph // 2, fill=GRN)
    d.text((cx1 - pw / 2, y + ph / 2), ptxt, font=f_pill, fill=TITLE_W, anchor="mm")
    y += ph + 22 * CS
    # map
    if cfg.get("map") and os.path.exists(cfg["map"]):
        m = Image.open(cfg["map"]).convert("RGB")
        mw = 520 * CS; mh = int(m.height * mw / m.width)
        m = m.resize((mw, mh), Image.LANCZOS)
        mask = Image.new("L", (mw, mh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, mw - 1, mh - 1], radius=12 * CS, fill=255)
        img.paste(m, (pad - 4 * CS, y), mask)
        y += mh + 8 * CS
        d.text((pad, y), "Live route map · tap pins to navigate", font=F(FR, 16 * CS), fill=(140, 150, 170))
        y += 30 * CS
    # sections
    secs = parse_sections(cfg["md"])
    max_body_lines = 12
    for si, sec in enumerate(secs):
        if y > (4300 * CS) and si >= 4: break          # height budget (in CS px)
        y += 6 * CS
        d.line([pad, y, Wp - pad, y], fill=RULE_C, width=max(1, CS // 2))
        y += 26 * CS
        for l in wrap(d, sec["title"], f_sect, Wp - 2 * pad)[:2]:
            d.text((pad, y), l, font=f_sect, fill=SECT_C); y += 36 * CS
        y += 6 * CS
        blocks = table_rows_to_bullets(sec["blocks"])
        used = 0
        for b in blocks:
            if used >= max_body_lines:
                break
            if b[0] == "sub":
                for l in wrap(d, b[1], f_subh, Wp - 2 * pad)[:1]:
                    d.text((pad, y), l, font=f_subh, fill=SUBH_C); y += 30 * CS; used += 1
            elif b[0] in ("p", "li"):
                txt = ("•  " + b[1]) if b[0] == "li" else b[1]
                if not txt.strip(): continue
                ls = wrap(d, txt, f_body, Wp - 2 * pad)
                blk_cap = 4 if b[0] == "li" else 6
                take = min(len(ls), max_body_lines - used, blk_cap)
                if take <= 0: break
                if take < len(ls):                       # clean word-boundary ellipsis
                    last = ls[take - 1]
                    while d.textlength(last + " …", font=f_body) > (Wp - 2 * pad) and " " in last:
                        last = last.rsplit(" ", 1)[0]
                    ls[take - 1] = last + " …"
                for l in ls[:take]:
                    d.text((pad, y), l, font=f_body, fill=BODY_C); y += lp; used += 1
            elif b[0] == "more":
                d.text((pad, y), b[1], font=f_small, fill=MORE_C); y += 24 * CS; used += 1
        y += 18 * CS
    y += 30 * CS
    tallH_cs = max(y, 1120 * CS)                        # FIX 4: never shorter than screen
    img = img.crop((0, 0, Wp, tallH_cs))
    return img.resize((560 * S, tallH_cs // 2), Image.LANCZOS)  # CS -> S

def make_base(chip, S):
    W, H = 720 * S, 1280 * S
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for yy in range(H):
        t = yy / H
        d.line([(0, yy), (W, yy)], fill=(int(10 + 8 * t), int(18 + 12 * t), int(38 + 18 * t)))
    ss = 4 if S == 1 else 2
    big = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    bd.rounded_rectangle([60 * S * ss, 80 * S * ss, 660 * S * ss, 1240 * S * ss],
                         radius=64 * S * ss, fill=(16, 22, 38, 255), outline=(70, 86, 120, 255), width=3 * S * ss)
    bd.rounded_rectangle([80 * S * ss, 100 * S * ss, 640 * S * ss, 1220 * S * ss],
                         radius=36 * S * ss, fill=(255, 255, 255, 255))
    frame = big.resize((W, H), Image.LANCZOS)
    im.paste(frame, (0, 0), frame)
    d = ImageDraw.Draw(im)
    f = F(FB, 26 * S)
    chip = glyph_safe(chip)
    tw = d.textlength(chip, font=f); cw = tw + 44 * S
    d.rounded_rectangle([(W - cw) / 2, 24 * S, (W + cw) / 2, 68 * S], radius=14 * S, fill=(13, 26, 56))
    d.text((W / 2, 46 * S), chip, font=f, fill=(238, 200, 120), anchor="mm")
    mask = Image.new("L", (560 * S, 1120 * S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 560 * S - 1, 1120 * S - 1], radius=34 * S, fill=255)
    return im, mask

def easeio(t): return 3 * t * t - 2 * t * t * t

def render(vid, S=1, dur=12.0, probe=False, outdir=OUTD):
    cfg = CFG[vid]
    tall = build_tall(cfg, S)
    base, mask = make_base(cfg["chip"], S)
    SH = 1120 * S
    scroll_max = max(0, tall.height - SH)
    N = int(dur * FPS)
    hold0, hold1 = 0.8, 0.8
    span = dur - hold0 - hold1
    os.makedirs(outdir, exist_ok=True)
    fdir = f"/tmp/frames_{vid}_{S}x"
    os.makedirs(fdir, exist_ok=True)
    print(f"[{vid}] tall={tall.width}x{tall.height} scroll_max={scroll_max} frames={N} scale={S}")
    idxs = [0, N // 2, N - 1] if probe else range(N)
    for f in idxs:
        t = f / FPS
        p = 0.0 if t < hold0 else (1.0 if t > dur - hold1 else easeio((t - hold0) / span))
        yoff = int(round(p * scroll_max))
        fr = base.copy()
        fr.paste(tall.crop((0, yoff, 560 * S, yoff + SH)), (80 * S, 100 * S), mask)
        fr.save(f"{fdir}/{f:04d}.jpg", quality=90)
    if probe:
        for f in idxs:
            os.replace(f"{fdir}/{f:04d}.jpg", f"{outdir}/PROBE_{vid}_{f:04d}.jpg")
        print(f"[{vid}] probes -> {outdir}")
        return
    out = f"{outdir}/{vid}_insert_FIXED.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{fdir}/%04d.jpg",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-an", out], check=True)
    print(f"[{vid}] WROTE {out}")

if __name__ == "__main__":
    args = sys.argv[1:]
    vid = args[0] if args else "10-offer"
    S = int(args[args.index("--scale") + 1]) if "--scale" in args else 1
    dur = float(args[args.index("--dur") + 1]) if "--dur" in args else 12.0
    outdir = args[args.index("--outdir") + 1] if "--outdir" in args else OUTD
    probe = "--probe" in args
    vids = list(CFG.keys()) if vid == "all" else [vid]
    for v in vids:
        render(v, S=S, dur=dur, probe=probe, outdir=outdir)

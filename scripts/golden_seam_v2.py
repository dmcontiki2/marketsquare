#!/usr/bin/env python3
"""GOLDEN_SET_OPENAI_V2_SEAM (15 Aug 2026) — the P2 gate run: the SAME eight production
prompts as GS-OAI-V1, but exercised through the LIVE ai_provider seam instead of a raw
vendor call, with whatever key the seam itself resolves (env, then the server .env at
/var/www/marketsquare/.env). RG-0016/P2 requires the golden set to pass ON THE SEAM WITH
THE SERVER KEY: GS-OAI-V1 proved the models; it did not prove the production path.

What the seam adds that V1 never exercised:
  * _to_openai_messages translation (app sends Anthropic-shaped content blocks)
  * the reasoning_effort="none" production pin (the gate tuple's effort term)
  * max_completion_tokens vs max_tokens handling for gpt-5*
  * AIResult parsing + error classification

Run it ON THE SERVER (or any host holding the production OPENAI_API_KEY):
    python3 scripts/golden_seam_v2.py
probe=True per call: no fallback — every outcome is unambiguously the openai lane's.
Writes Records/GOLDEN_SET_OPENAI_V2_SEAM_results.json. Exit 0 = 8/8 PASS, else 1.
"""
import base64, io, json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
import ai_provider as ap

BEA = open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read()

def extract(name, src=BEA):
    i = src.index(name + " = ")
    for end in range(i + 100, min(i + 20000, len(src)), 50):
        chunk = src[i:end]
        try:
            ns = {}
            exec(chunk, {}, ns)
            if name in ns:
                return ns[name]
        except Exception:
            continue
    raise RuntimeError("extract failed: " + name)

_CURRENCY_MAP = extract("_CURRENCY_MAP")
_VISION_SYSTEM = extract("_VISION_SYSTEM")
_SI_SYSTEM = extract("_SI_SYSTEM")
_ANON_AI_SYSTEM = extract("_ANON_AI_SYSTEM")
i = BEA.index("def _build_vision_prompt")
j = min(x for x in (BEA.find("\ndef ", i + 10), BEA.find("\n@app.", i + 10),
                    BEA.find("\nasync def ", i + 10)) if x != -1)
ns = {"_CURRENCY_MAP": _CURRENCY_MAP}
exec(BEA[i:j], ns)
build_vision_prompt = ns["_build_vision_prompt"]

TRIAGE_SYSTEM = (
    "You are the email triage assistant for TrustSquare, a South African local "
    "marketplace connecting buyers with anonymous, trusted sellers via an "
    "introduction currency called Tuppence. You read one inbound customer email "
    "and return STRICT JSON only — no prose, no markdown fences.\n\n"
    'JSON shape: {"category": one of ["support","billing","legal","compliance","spam","other"], '
    '"urgency": one of ["low","normal","high"], '
    '"bin": the app area, one of ["AUTH","LIST","TRUST","INTRO","BROWSE","ADV","MAIL","PERF","COPY","MISC"], '
    '"draft_reply": a short, warm, professional plain-text reply signed '
    "'The TrustSquare Team', "
    '"auto_safe": boolean — true ONLY if a routine support or billing question '
    "the draft can fully answer with no human judgement.}\n\n"
    "Rules: Never reveal seller identities or internal data. Never promise refunds "
    "(Tuppence is strictly non-refundable). For legal, compliance, disputes, threats, "
    "or anything ambiguous set auto_safe=false. For spam set draft_reply to empty "
    "string and auto_safe=false. Keep replies under 120 words.")

DRAFT_CATS = ["Property", "Tutors", "Services", "Adventures", "Collectors", "Cars", "LocalMarket"]
DRAFT_PROMPT = (
    "A seller on TrustSquare (South African marketplace) wrote ONE sentence about "
    "what they are selling:\n\"%s\"\nCity: %s\n\n"
    "Draft their listing. Reply with ONLY a JSON object, no other text:\n"
    '{"title": "max 80 chars, specific, no hype", '
    '"category": one of ' + str(DRAFT_CATS) + ', '
    '"condition": "short honest read from the sentence, never a certified grade", '
    "\"price\": \"suggested asking price as 'R12 500' (use the seller's number if given; "
    'empty string if you cannot estimate honestly), '
    '"description": "2-3 factual sentences, anonymous seller voice, no contact details"}')

def img_block(path):
    """APP-format image block — the seam's adapters do the vendor translation."""
    from PIL import Image, ImageOps
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = img.size
    if max(w, h) > 1568:
        r = 1568 / max(w, h)
        img = img.resize((int(w * r), int(h * r)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85, optimize=True)
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
            "data": base64.b64encode(buf.getvalue()).decode()}}

PII_RE = re.compile(r"(\+27\s?\d[\d\s\-]{7,}|\b0\d{2}[\s\-]?\d{3}[\s\-]?\d{4}\b|@[\w.]+\.\w{2,}|www\.|http|whatsapp|Olivier Street|Kronborg|ProLux|proluxproperties)", re.I)

def strip_fence(t):
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.lstrip().startswith("json"):
            t = t.lstrip()[4:]
    return t.strip()

results = []

def run(tid, tier, name, system, content, max_out, checks):
    t0 = time.time()
    try:
        r = ap.complete([{"role": "user", "content": content}], task=tier,
                        max_tokens=max_out, system=system, provider="openai",
                        probe=True, timeout=240)
    except Exception as e:
        results.append({"id": tid, "tier": tier, "name": name, "ok": False,
                        "why": "SEAM RAISED: %r" % (e,)})
        print("%s %s: SEAM RAISED %r" % (tid, name, e)); return
    if not r.ok:
        results.append({"id": tid, "tier": tier, "name": name, "ok": False,
                        "provider": r.provider, "model": r.model, "status": r.status,
                        "why": "lane not ok: %s" % (r.error_kind or "unknown")})
        print("%s %s: LANE NOT OK (%s, status %s)" % (tid, name, r.error_kind, r.status)); return
    text = strip_fence(r.text or ""); fails = []
    for label, fn in checks:
        try:
            if not fn(text):
                fails.append(label)
        except Exception as ex:
            fails.append("%s (check error %r)" % (label, ex))
    ok = not fails and bool(text)
    if not text:
        fails.append("EMPTY REPLY")
    results.append({"id": tid, "tier": tier, "name": name, "ok": ok, "fails": fails,
                    "provider": r.provider, "model": r.model,
                    "latency_s": round(time.time() - t0, 1),
                    "in_tok": r.in_tokens, "out_tok": r.out_tokens, "raw": text[:1600]})
    print("%s %s [%s/%s]: %s  (%.1fs, %s+%s tok)"
          % (tid, name, r.provider, r.model, "PASS" if ok else "FAIL " + str(fails),
             time.time() - t0, r.in_tokens, r.out_tokens))

def jchk(*keys):
    def f(t):
        d = json.loads(t); return all(k in d for k in keys)
    return f

def no_pii(t):
    return not PII_RE.search(t)

if not ap.envkey("OPENAI_API_KEY"):
    print("GOLDEN_SEAM_V2: the seam resolves NO OPENAI_API_KEY on this host "
          "(env + /var/www/marketsquare/.env). P2 requires the SERVER key — run this "
          "on the box. Refusing to fake a result.")
    sys.exit(2)

run("T1", "haiku", "draft-from-intent", None,
    DRAFT_PROMPT % ("Selling my 3 seater genuine leather couch, dark brown, 2 years old, small scratch on one arm, want R4500", "Pretoria"),
    350, [("json+schema", jchk("title", "category", "condition", "price", "description")),
          ("no PII", no_pii),
          ("price honest", lambda t: "4" in json.loads(t)["price"] and "500" in json.loads(t)["price"]),
          ("no invention", lambda t: "oak" not in t.lower() and "italian" not in t.lower())])
run("T2", "haiku", "search-interpret", _SI_SYSTEM,
    "im looking for a reliable bakkie under 150k around centurion",
    120, [("json+schema", jchk("terms", "price_min", "price_max", "category")),
          ("price parsed", lambda t: json.loads(t)["price_max"] == 150000),
          ("category", lambda t: json.loads(t)["category"] == "Cars")])
run("T3", "haiku", "anon-rewrite", _ANON_AI_SYSTEM,
    "TITLE: Stunning 3 bed home — ProLux Properties exclusive!\nDESCRIPTION: Lovely family home at 252 Olivier Street, Elarduspark. 3 beds, 2 baths, double garage, R1,450,000. Call Marietta at ProLux Properties on 082 555 1234 or WhatsApp, viewing by appointment through our Lynnwood office. www.proluxproperties.co.za",
    1000, [("format", lambda t: re.search(r"TITLE:.*DESCRIPTION:", t, re.S | re.I) is not None),
           ("PII scrubbed", no_pii),
           ("facts kept", lambda t: "1,450,000" in t or "1 450 000" in t or "R1,450,000" in t or "1450000" in t.replace(" ", "").replace(",", "")),
           ("suburb kept", lambda t: "Elarduspark" in t)])
run("T4", "triage", "email-triage", TRIAGE_SYSTEM,
    "From: piet@example.co.za\nSubject: Tuppence refund\n\nHi, I bought 5 Tuppence yesterday but the seller declined my introduction. Can I get my money back?",
    400, [("json+schema", jchk("category", "urgency", "bin", "draft_reply", "auto_safe")),
          ("no refund promise", lambda t: "refund" not in json.loads(t)["draft_reply"].lower() or "non-refundable" in json.loads(t)["draft_reply"].lower() or "not refundable" in json.loads(t)["draft_reply"].lower()),
          ("reply signed", lambda t: "TrustSquare Team" in json.loads(t)["draft_reply"])])
vp = build_vision_prompt("collectors", "Pretoria", "ZA", 2)
run("T5", "vision", "vision-draft-2-photos", _VISION_SYSTEM,
    [img_block(os.path.join(REPO, "Jewelry", "IMG_8032.JPG")),
     img_block(os.path.join(REPO, "Jewelry", "IMG_8033.JPG")),
     {"type": "text", "text": vp}],
    1200, [("json parses", lambda t: isinstance(json.loads(t), dict)),
           ("core fields", lambda t: all(k in json.loads(t) for k in ("title", "category"))),
           ("no PII", no_pii)])
run("T6", "sonnet", "anon-rewrite-hard", _ANON_AI_SYSTEM,
    "TITLE: Kruger Safari Special — Bushveld Tours & Safaris!\nDESCRIPTION: 3-day Kruger package R8,999pp incl. game drives with ranger Johan. Book via bookings@bushveldtours.co.za or call our Nelspruit office 013 741 9999. Depart from our depot at 17 Impala Road. Follow @bushveldtours for specials!",
    1000, [("format", lambda t: re.search(r"TITLE:.*DESCRIPTION:", t, re.S | re.I) is not None),
           ("PII scrubbed", lambda t: not re.search(r"(bushveld|johan|013\s?741|impala road|@|bookings)", t, re.I)),
           ("facts kept", lambda t: "8,999" in t or "8999" in t.replace(" ", ""))])
run("T7", "sonnet", "price-check-no-invention", None,
    "You assess marketplace prices for TrustSquare (South Africa). Comparable sales provided are the ONLY price evidence — never invent figures. Comps for 2-bed flats, Elarduspark, Pretoria (rent/month): R6,800 · R7,200 · R7,500 · R7,900. Asking price under review: R9,500/month. Reply ONLY JSON: {\"fair\": true|false, \"estimate\": <number from comps range>, \"rationale\": \"<2 sentences citing only the comps>\"}",
    600, [("json+schema", jchk("fair", "estimate", "rationale")),
          ("verdict", lambda t: json.loads(t)["fair"] is False),
          ("estimate in comps range", lambda t: 6800 <= float(json.loads(t)["estimate"]) <= 7900)])
run("T8", "sonnet", "photo-anon-scan",
    "You are the photo anonymiser for TrustSquare, an anonymity-first marketplace. Inspect this photo for ANY identifying content: contact details, logos/watermarks, signage, number plates, house numbers, faces, documents. Reply with ONLY a JSON object: {\"verdict\": \"clean\"|\"redact\"|\"reject\", \"confidence\": 0.0-1.0, \"labels\": []}",
    [img_block(os.path.join(REPO, "Jewelry", "IMG_8033.JPG")),
     {"type": "text", "text": "Scan this seller photo."}],
    400, [("json+schema", jchk("verdict", "confidence")),
          ("verdict sane", lambda t: json.loads(t)["verdict"] in ("clean", "redact", "reject"))])

out = {"eval": "GS-OAI-V2-SEAM", "date": time.strftime("%Y-%m-%d"),
       "path": "ai_provider.complete(provider='openai', probe=True) — live seam",
       "key_source": "env" if os.getenv("OPENAI_API_KEY") else "/var/www/marketsquare/.env",
       "results": results}
os.makedirs(os.path.join(REPO, "Records"), exist_ok=True)
json.dump(out, open(os.path.join(REPO, "Records", "GOLDEN_SET_OPENAI_V2_SEAM_results.json"), "w"), indent=1)
p = sum(1 for r in results if r["ok"]); tot = len(results)
print("\n%d/%d passed via the live seam (key_source=%s)" % (p, tot, out["key_source"]))
sys.exit(0 if p == tot else 1)

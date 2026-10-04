#!/usr/bin/env python3
"""ANON-NAMES-1 (David 4 Oct 2026, testing as a seller): "he had some photos with complex id's which you picked up and
removed, but he also had the complex name 'IQ Rondebosh' in his descriptive title which your AI did not pick up (listing
headline) ... the same is true for the description or anywhere in the advert." Listing 475: title "3 Bed 2 Bath Modern
iQ Rondebosch unit for sale", body "The iQ Rondebosch properties is truly the best choice".
The photo pipeline has asked the AI for complex/building names since July; the TEXT path (E2E-HMI-1 _private_text_scrub)
only ran regexes for phones, emails, links, handles and street addresses -- a name has no shape a regex can see. Now every
private publish and edit (create, edit, guided publish, Local Market, profile) also asks the AI for the NAMES in the
advert -- complexes, estates, buildings, residences, developments, businesses, people -- in the title, the body AND every
photo caption, and replaces them; the area field is checked the same way. Suburbs, towns and public landmarks (malls,
schools, highways) stay. Idempotent; asserts every anchor."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "bea_main.py")
s = io.open(P, encoding="utf-8", newline="").read(); n0 = len(s)
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)

FN = r'''# ── ANON-NAMES-1 (David 4 Oct 2026): names in advert TEXT -- complexes, estates, buildings, businesses, people ──
# The photo scan has looked for complex/building names since July; the text path only had regexes, and a name has no
# shape a regex can see ("3 Bed 2 Bath Modern iQ Rondebosch unit for sale", listing 475). One AI read per changed text
# finds the names; each is replaced in the title, the body and every photo caption. Suburbs, towns and public landmarks
# stay -- they place the advert in an area, not at an address. Fail-open (logged): a lane outage never blocks a seller,
# and the regex strip, the photo pipeline and the introduction gate still stand.
_ANON_NAMES_SYSTEM = (
    "You protect seller anonymity on TrustSquare, a South African marketplace where a buyer must not be able to find "
    "the seller or the exact property before a paid introduction. In the advert text you are given, find every NAME "
    "that identifies one specific place or party: the name of a residential complex, townhouse complex, estate or "
    "security village, block of flats, apartment building, student residence, development or retirement village "
    "(examples: 'iQ Rondebosch', 'Kronborg Luxury Apartments', 'Villa Toscana', 'The Willows Estate'); a named farm or "
    "guest house when it is the seller's own; a business, shop, agency or brand used as the seller's identity; and any "
    "person's name. Do NOT flag: suburbs, towns, cities, provinces or regions (even when they appear inside a complex "
    "name, flag the whole complex name only); public landmarks a buyer uses for orientation (malls, schools, "
    "universities, hospitals, parks, trails, highways, e.g. 'Irene Mall', 'Hoerskool Waterkloof', 'N1'); brands of the "
    "goods or fittings (Toyota, Smeg, Caesarstone); or generic words (complex, estate, townhouse, simplex). "
    "Reply with ONLY JSON: {\"names\":[{\"text\":\"<the name exactly as written>\",\"kind\":\"complex|estate|building|"
    "residence|business|person|other\",\"replace\":\"<neutral words that read naturally in its place, e.g. 'the "
    "complex', or empty>\"}]}. If there are none: {\"names\":[]}."
)
_ANON_NAMES_MEMO = {}   # pure memo of identical text (idempotent) -- not shared state; a cold box just asks again


def _anon_names_find(text, place="", who=""):
    """Returns (ok, [{text, kind, replace}]). Never raises."""
    t = (text or "").strip()
    if len(t) < 3:
        return True, []
    key = hashlib.sha1((place + "\x00" + t).encode("utf-8", "replace")).hexdigest()
    if key in _ANON_NAMES_MEMO:
        return True, _ANON_NAMES_MEMO[key]
    try:
        _check_cost_ceiling(who or "anon-names")
        import ai_provider as _ap
        res = _ap.complete([{"role": "user", "content": ("THE ADVERT'S OWN SUBURB/AREA (never a name to remove): %s\n\n"
                                                         "ADVERT TEXT:\n%s") % (place or "(not given)", t[:6000])}],
                           task="fast", max_tokens=400, system=_ANON_NAMES_SYSTEM, provider=_ts_active_provider(), timeout=20)
        if not res.ok:
            return False, []
        _log_ai_spend(who or "", "/listings#anon-names", "fast", res.in_tokens, res.out_tokens,
                      provider=res.provider, model=res.model)
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", (res.text or "").strip())
        m = re.search(r"\{.*\}", raw, re.S)
        names = (json.loads(m.group(0)).get("names") if m else None) or []
    except Exception as exc:
        _log.warning("ANON-NAMES-1 name read unavailable (%s): %s", who, exc)
        return False, []
    keep_whole = {p.strip().lower() for p in re.split(r"[,/]", place or "") if p.strip()}
    out = []
    for n in names[:12]:
        if not isinstance(n, dict):
            continue
        nt = str(n.get("text") or "").strip()
        if len(nt) < 2 or nt.lower() in keep_whole or nt.lower() not in t.lower():
            continue                      # never the advert's own suburb; never a name the text does not contain
        rp = str(n.get("replace") or "").strip()[:40]
        if nt.lower() in rp.lower():
            rp = ""
        out.append({"text": nt, "kind": str(n.get("kind") or "other")[:12], "replace": rp})
    if len(_ANON_NAMES_MEMO) > 2000:
        _ANON_NAMES_MEMO.clear()
    _ANON_NAMES_MEMO[key] = out
    return True, out


def _anon_names_apply(text, names):
    if not text or not names:
        return text
    out = text
    for n in sorted(names, key=lambda x: -len(x["text"])):
        out = re.sub(r"(?i)(?<![\w])" + re.escape(n["text"]) + r"(?![\w])", n["replace"], out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" +([,.;:!?])", r"\1", out)
    out = re.sub(r"(?im)^[ \t]+|[ \t]+$", "", out)
    return out.strip() if out.strip() else text


_PHOTOS_PREFIX_RX = re.compile(r"^\[photos:([^\]]*)\]\n?")


def _anon_names_scrub(title, desc, place="", who="", where=""):
    """Title, body and photo captions read together (one AI call); names replaced in all three. The [photos:...] URLs
    are never touched. Returns (title, desc, hit_labels)."""
    body, items = (desc or ""), None
    m = _PHOTOS_PREFIX_RX.match(body)
    if m:
        items = [it.split("::", 1) for it in m.group(1).split("|")]
        body = body[m.end():]
    caps = [it[1] for it in (items or []) if len(it) > 1 and it[1].strip()]
    joined = "\n".join([x for x in [title or "", body] + caps if x])
    ok, names = _anon_names_find(joined, place, who)
    if not names:
        return title, desc, []
    t2 = _anon_names_apply(title, names) if title else title
    b2 = _anon_names_apply(body, names)
    if items is not None:
        rebuilt = "|".join(it[0] + ("::" + _anon_names_apply(it[1], names) if len(it) > 1 else "") for it in items)
        d2 = "[photos:" + rebuilt + "]\n" + b2 if b2 else "[photos:" + rebuilt + "]"
    else:
        d2 = b2
    hits = sorted({"name:" + n["kind"] for n in names})
    _log.info("ANON-NAMES-1 (%s) for %s: %s", where, who, [n["text"] for n in names])
    return t2, (d2 if desc is not None else desc), hits


def _anon_names_area(area, suburb="", who="", where=""):
    """The free-text area a seller types (Quick's 'Type your area') is checked the same way; a name falls back to her
    suburb."""
    a = (area or "").strip()
    if not a or a.lower() == (suburb or "").strip().lower():
        return area, []
    ok, names = _anon_names_find(a, suburb, who)
    if not names:
        return area, []
    clean = _anon_names_apply(a, [dict(n, replace="") for n in names]).strip(" ,")
    _log.info("ANON-NAMES-1 area (%s) for %s: %s", where, who, [n["text"] for n in names])
    return (clean or suburb or area), sorted({"name:" + n["kind"] for n in names})


def _private_text_scrub(title, desc, who="", where=""):'''
if "_ANON_NAMES_SYSTEM = (" not in s:
    s = rep(s, "def _private_text_scrub(title, desc, who=\"\", where=\"\"):", FN, "fn")
# _private_text_scrub: run the name pass after the regex pass, with an optional place hint
s = rep(s, "def _private_text_scrub(title, desc, who=\"\", where=\"\"):\n    \"\"\"E2E-HMI-1",
           "def _private_text_scrub(title, desc, who=\"\", where=\"\", place=\"\"):\n    \"\"\"E2E-HMI-1", "sig")
s = rep(s, "    if hits:\n        _log.info(\"E2E-HMI-1 contact scrub (%s) for %s: %s\", where, who, sorted(set(hits)))\n    return out[0], out[1], sorted(set(hits))",
           "    if hits:\n        _log.info(\"E2E-HMI-1 contact scrub (%s) for %s: %s\", where, who, sorted(set(hits)))\n"
           "    # ANON-NAMES-1: then the NAMES -- complexes, estates, buildings, businesses, people -- in title, body and captions\n"
           "    if (out[0] or out[1]):\n"
           "        _t, _d, _nh = _anon_names_scrub(out[0], out[1], place, who, where)\n"
           "        out = [_t, _d]; hits.extend(_nh)\n"
           "    return out[0], out[1], sorted(set(hits))", "scrub body")
# callers: give the place; check the typed area
s = rep(s, "    listing.title, listing.description, _scrubbed = _private_text_scrub(\n        listing.title, listing.description, listing.seller_email or \"\", \"create\")   # E2E-HMI-1\n",
           "    listing.title, listing.description, _scrubbed = _private_text_scrub(\n        listing.title, listing.description, listing.seller_email or \"\", \"create\",\n"
           "        \", \".join(x for x in (listing.suburb, listing.city) if x))   # E2E-HMI-1 + ANON-NAMES-1 (the typed area is checked, not trusted)\n"
           "    listing.area, _an = _anon_names_area(listing.area, listing.suburb or \"\", listing.seller_email or \"\", \"create\")   # ANON-NAMES-1\n",
        "create caller")
s = rep(s, "    update.title, update.description, _scrubbed = _private_text_scrub(\n        update.title, update.description, \"\", \"edit #%s\" % listing_id)   # E2E-HMI-1\n",
           "    update.title, update.description, _scrubbed = _private_text_scrub(\n        update.title, update.description, \"\", \"edit #%s\" % listing_id,\n"
           "        update.suburb or \"\")   # E2E-HMI-1 + ANON-NAMES-1 (the typed area is checked, not trusted)\n"
           "    if update.area:\n        update.area, _an = _anon_names_area(update.area, update.suburb or \"\", \"\", \"edit #%s\" % listing_id)   # ANON-NAMES-1\n",
        "update caller")
s = rep(s, "    title, desc, _scrubbed = _private_text_scrub(title, desc, email, \"aa-publish\")   # E2E-HMI-1\n",
           "    title, desc, _scrubbed = await asyncio.to_thread(_private_text_scrub, title, desc, email, \"aa-publish\")   # E2E-HMI-1 + ANON-NAMES-1 (AI read off the event loop)\n",
        "aa caller")
io.open(P, "w", encoding="utf-8", newline="").write(s)
assert io.open(P, encoding="utf-8", newline="").read() == s
print("ANON-NAMES-1 applied: bea_main.py %d -> %d chars" % (n0, len(s)))

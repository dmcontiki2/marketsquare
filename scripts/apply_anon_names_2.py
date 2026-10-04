#!/usr/bin/env python3
"""ANON-NAMES-1 polish (4 Oct 2026, from the first real run on listing 475): a TITLE drops the name outright ("3 Bed 2 Bath
Modern unit for sale", not "... Modern the complex unit ..."), and a doubled article left by a replacement collapses
("The the complex" -> "The complex"). Run after apply_anon_names.py. Idempotent; asserts its anchors."""
import io, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bea_main.py")
s = io.open(P, encoding="utf-8", newline="").read()
A1 = 'def _anon_names_apply(text, names):\n'
B1 = 'def _anon_names_apply(text, names, title=False):\n'
A2 = '        out = re.sub(r"(?i)(?<![\\w])" + re.escape(n["text"]) + r"(?![\\w])", n["replace"], out)\n    out = re.sub(r"[ \\t]{2,}", " ", out)'
B2 = ('        # a title is a short descriptor: the name simply goes ("3 Bed 2 Bath Modern unit for sale")\n'
      '        out = re.sub(r"(?i)(?<![\\w])" + re.escape(n["text"]) + r"(?![\\w])", "" if title else n["replace"], out)\n'
      '    out = re.sub(r"(?i)\\b(the|a|an)\\s+(the|a|an)\\b", lambda m: m.group(2) if m.group(1)[0].islower() else m.group(2).capitalize(), out)\n'
      '    out = re.sub(r"[ \\t]{2,}", " ", out)')
A3 = '    t2 = _anon_names_apply(title, names) if title else title'
B3 = '    t2 = _anon_names_apply(title, names, title=True) if title else title'
for a, b in ((A1, B1), (A2, B2), (A3, B3)):
    if b in s: continue
    assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("ANON-NAMES-1 polish applied")

# PHOTOS-PREFIX-SAFE-1 (same day): the contact regex must never read the [photos:url|url] prefix -- on a description that
# carries it (the 475 backfill did) the URL pattern stripped every photo address. Prefix set aside, body scrubbed, put back.
s = io.open(P, encoding="utf-8", newline="").read()
A4 = ("    for v in (title, desc):\n        if not v:\n            out.append(v)\n            continue\n"
      "        clean, h = _anon_regex_clean(v)\n        if h:\n            hits.extend(h)\n            out.append(clean)\n"
      "        else:\n            out.append(v)\n    if hits:\n        _log.info(\"E2E-HMI-1 contact scrub (%s) for %s: %s\"")
B4 = ("    _pm = _PHOTOS_PREFIX_RX.match(desc or \"\")   # PHOTOS-PREFIX-SAFE-1: photo addresses are not contact details\n"
      "    _pfx, _body = ((_pm.group(0), (desc or \"\")[_pm.end():]) if _pm else (\"\", desc))\n"
      "    for i, v in enumerate((title, _body)):\n        if not v:\n            out.append((_pfx or v) if i == 1 else v)\n            continue\n"
      "        clean, h = _anon_regex_clean(v)\n        if h:\n            hits.extend(h)\n            out.append(_pfx + clean if i == 1 else clean)\n"
      "        else:\n            out.append(desc if i == 1 else v)\n    if hits:\n        _log.info(\"E2E-HMI-1 contact scrub (%s) for %s: %s\"")
if B4 not in s:
    assert s.count(A4) == 1, "A4 %d" % s.count(A4); s = s.replace(A4, B4)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("PHOTOS-PREFIX-SAFE-1 applied")

# BRANDS-STAY-1 (same day, first real run on 475): the model removed "Smeg" from "quality Smeg appliances". Makers and
# brands of the goods and fittings describe the item; only the seller's OWN business is a name to remove.
s = io.open(P, encoding="utf-8", newline="").read()
for a, b in (('guest house when it is the seller\'s own; a business, shop, agency or brand used as the seller\'s identity; and any "\n    "person\'s name. Do NOT flag:', 'guest house when it is the seller\'s own; the seller\'s OWN business, shop or agency (the one selling, letting or "\n    "managing this advert, e.g. \'Smith Properties\', \'Pam\'s Cleaning\'); and any person\'s name. Do NOT flag:'), ('brands of the "\n    "goods or fittings (Toyota, Smeg, Caesarstone); or generic words', 'makers and brands of "\n    "the goods, appliances, fittings or materials -- they describe the item, not the seller (Toyota, Smeg, Bosch, "\n    "Defy, Caesarstone, Samsung, Weber are NEVER names to remove); or generic words')):
    if b in s: continue
    assert s.count(a) == 1, a[:40]; s = s.replace(a, b)
io.open(P, "w", encoding="utf-8", newline="").write(s); print("BRANDS-STAY-1 applied")

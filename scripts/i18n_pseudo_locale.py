#!/usr/bin/env python3
"""
i18n_pseudo_locale.py -- I18N_READINESS.md item 3 (RUL-075 / RUL-152). Built 1 Oct 2026.

THE PSEUDO-LOCALE TEST. A fake "language" that looks like this -- [Çàţéĝöŕîéš ~~~~] -- is
pushed through the app's REAL paint layer (the one that translates the live app into
Afrikaans, isiZulu, isiXhosa and Sepedi) on a local copy of the app. Every word comes back
accented, bracketed and about 35% longer, so three faults become visible without waiting
for a single real translation:

  1. COVERAGE -- a visible English word with no bracket around it is a word the paint
     layer never reached (hard-coded, composed out of pieces, marked do-not-translate,
     or user content). Words that ARE in the string inventory are app chrome the
     translation will miss; the rest is listing content and data (Lane 2 / RUL-086).
  2. LAYOUT -- text that clips, or runs off a 412-px phone screen, in pseudo but NOT in
     English is a button, chip or label that a longer language (Afrikaans and isiZulu run
     long) will break.
  3. INVENTORY GAPS -- a phrase the paint layer ASKED for that the inventory extractor
     never saw is a string item 1 is blind to.

Runs on the parity harness (scripts/i18n_parity_harness.py): same local serving from the
deploy manifest, same recorded data fixture, same virtual clock. It never calls the live
/i18n/translate (that can spend); the pseudo text is generated here, $0. Touches nothing the
live app serves.

Writes:
  i18n/locales/qps-pseudo.json    -- the pseudo dictionary, same shape as roles/app_i18n_*.json
  i18n/pseudo_locale_report.json  -- the findings (counts + chrome strings + layout breaks;
                                     no listing text is stored)

  python3 scripts/i18n_pseudo_locale.py            # generate + run + report (exit 0 measured, 2 not measured)
  python3 scripts/i18n_pseudo_locale.py --strict   # exit 1 when any NEW layout break is found
  python3 scripts/i18n_pseudo_locale.py --generate # dictionary only, no browser
"""
import json, math, os, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import i18n_parity_harness as H      # noqa: E402

INVENTORY = os.path.join(REPO, "i18n", "inventory.json")
TABLE = os.path.join(REPO, "i18n", "locales", "qps-pseudo.json")
REPORT = os.path.join(REPO, "i18n", "pseudo_locale_report.json")
OPEN, CLOSE = "⟦", "⟧"         # the bracket pair the measurement looks for
# The paint layer is driven through a REAL offered language slot (it only asks for languages
# the country list offers); the answers are pseudo, so which slot is irrelevant to the words.
SLOT = "af"

_UP = "ÀƁÇĐÉƑĜĤÎĴĶĹṀÑÖÞǪŔŠŢÛṼŴẊÝŽ"
_LO = "àƀçđéƒĝĥîĵķĺɱñöþǫŕšţûṽŵẋýž"
assert len(_UP) == 26 and len(_LO) == 26
_MAP = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", _UP + _LO)
_PROTECT = re.compile(r"(\$\{[^}]*\}|\{[^}]*\}|%[sdif]|&[a-zA-Z]+;|https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+)")


def pseudo(s):
    """Accent every letter, keep placeholders/URLs/emails intact, lengthen ~35%, bracket it."""
    parts = _PROTECT.split(s)
    body = "".join(p if i % 2 else p.translate(_MAP) for i, p in enumerate(parts))
    pad = max(2, math.ceil(len(s) * 0.35))
    return OPEN + body + " " + "~" * pad + CLOSE


def generate():
    inv = json.load(open(INVENTORY, encoding="utf-8"))
    strings = [e["text"] for e in inv.get("strings", [])]
    t = {s: pseudo(s) for s in strings}
    os.makedirs(os.path.dirname(TABLE), exist_ok=True)
    with open(TABLE, "w", encoding="utf-8") as fh:
        json.dump({"lang": "qps-pseudo",
                   "note": "Generated pseudo-locale (I18N_READINESS item 3). Accented, bracketed, ~35% longer. "
                           "NEVER served by the live app -- the pseudo-locale test answers the paint layer "
                           "from this table on a local copy only.",
                   "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "source": "i18n/inventory.json (%s)" % inv.get("generated"),
                   "t": t}, fh, ensure_ascii=False, indent=0)
    H.say("pseudo dictionary: %d phrases -> %s" % (len(t), os.path.relpath(TABLE, REPO)))
    return t


MEASURE_JS = r"""(scope) => {
  const OPEN = '⟦', W = window.innerWidth;
  const LETTER = /[A-Za-zÀ-ɏ]/;
  const vis = el => { if (!el || !el.getClientRects || !el.getClientRects().length) return false;
    const cs = getComputedStyle(el); return cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity || '1') > 0; };
  const scopeOf = el => {
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      if (e.classList && e.classList.contains('screen') && !e.classList.contains('active')) return '';
      const t = e.tagName; if (t === 'SCRIPT' || t === 'STYLE' || t === 'NOSCRIPT' || t === 'TEXTAREA' || t === 'OPTION') return '';
      if ((e.getAttribute && e.getAttribute('data-notranslate') !== null) || e.id === 'ts-lang') return 'nt';
    }
    return 'ok'; };
  const sel = el => { const parts = [];
    for (let e = el, i = 0; e && e !== document.body && i < 4; e = e.parentElement, i++) {
      let s = e.tagName.toLowerCase();
      if (e.id) { parts.unshift(s + '#' + e.id); break; }
      if (typeof e.className === 'string' && e.className.trim()) s += '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.');
      parts.unshift(s); }
    return parts.join('>'); };
  const scrollsX = el => { for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) {
      const o = getComputedStyle(e).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
  let total = 0, tr = 0, nt = 0; const untr = [], holders = new Set();
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) {
    const v = (n.nodeValue || '').replace(/\s+/g, ' ').trim();
    if (!v || !LETTER.test(v)) continue;
    const p = n.parentElement; if (!p) continue;
    const sc = scopeOf(p); if (!sc || !vis(p)) continue;
    holders.add(p);
    if (sc === 'nt') { nt++; continue; }
    total++;
    if (v.indexOf(OPEN) >= 0) tr++; else untr.push(v.slice(0, 120));
  }
  const boxes = new Set();
  holders.forEach(h => { boxes.add(h); if (h.parentElement) boxes.add(h.parentElement);
                         if (h.parentElement && h.parentElement.parentElement) boxes.add(h.parentElement.parentElement); });
  const layout = [];
  boxes.forEach(el => {
    if (el === document.body || el === document.documentElement || !vis(el)) return;
    if (el.classList && el.classList.contains('screen')) return;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    const txt = (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
    if (!txt) return;
    const hideX = /^(hidden|clip)$/.test(cs.overflowX) || cs.textOverflow === 'ellipsis';
    const hideY = /^(hidden|clip)$/.test(cs.overflowY);
    if (hideX && el.scrollWidth > el.clientWidth + 2) layout.push({k: 'clipped-x', s: sel(el), t: txt});
    if (hideY && el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 2) layout.push({k: 'clipped-y', s: sel(el), t: txt});
    if (holders.has(el) && r.width > 0 && (r.right > W + 2 || r.left < -2) && !scrollsX(el)) layout.push({k: 'off-screen', s: sel(el), t: txt});
  });
  return {total, tr, nt, untr, layout};
}"""


def _data_strings(fx):
    """Every string value inside the recorded API answers (listings, wonders, geo, flags)."""
    out = set()

    def walk(v):
        if isinstance(v, str):
            v = re.sub(r"\s+", " ", v).strip()
            if v:
                out.add(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    for e in ((fx or {}).get("entries") or {}).values():
        try:
            walk(json.loads(e.get("body") or "null"))
        except Exception:
            pass
    return out


def run(strict=False):
    table = generate()
    fx = H.load_fixture()
    H.say("fixture: %s" % ("%d recorded API answers" % len(fx["entries"]) if fx else
                         "none -- offline wording only (run i18n_parity_harness.py record for listings)"))
    eng = H.Build(label="english", lang="en")
    pse = H.Build(label="pseudo", lang=SLOT, translate=lambda k: table.get(k) or pseudo(k))
    try:
        snaps = H.walk([eng, pse], fixture=fx, extra_js=MEASURE_JS)
    except RuntimeError as e:
        H.say(str(e).replace("NOT_MEASURED", "NOT MEASURED"))
        return 2
    se, sp = snaps[("english", "en")], snaps[("pseudo", SLOT)]
    ee, ep = se.get("extra", {}), sp.get("extra", {})
    inv = set(table)

    # 1. coverage
    total = tr = nt = 0
    chrome_miss = defaultdict(set)      # chrome string -> states where it stayed English
    other_miss = 0
    for key, m in ep.items():
        total += m["total"]; tr += m["tr"]; nt += m["nt"]
        for v in m["untr"]:
            if v in inv:
                chrome_miss[v].add(key)
            else:
                other_miss += 1
    # 2. layout: in pseudo but not in English, same state, same element
    new_breaks = defaultdict(lambda: {"states": [], "text": ""})
    base_issues = 0
    for key, m in ep.items():
        before = Counter((x["k"], x["s"]) for x in (ee.get(key) or {}).get("layout", []))
        base_issues += sum(before.values())
        after = Counter((x["k"], x["s"]) for x in m.get("layout", []))
        sample = {(x["k"], x["s"]): x["t"] for x in m.get("layout", [])}
        for k, c in after.items():
            if c > before.get(k, 0):
                nb = new_breaks["%s  %s" % k]
                nb["states"].append(key)
                nb["text"] = sample[k]
    # 3. inventory gaps -- phrases that come from DATA (listings, wonders, geo) are split off by
    #    looking them up in the recorded API answers, and only their COUNT is kept.
    data_vals = _data_strings(fx)
    blob = "\n".join(data_vals)
    asked_data = {a for a in pse.asked if a in data_vals or a in blob}
    asked_chrome = pse.asked - asked_data
    gaps = sorted(asked_chrome - inv)
    # 5. how much of the chrome the paint layer asks for is in each CHECKED dictionary on disk
    #    (a phrase missing here is painted from the server's machine cache, or stays English)
    dict_cov = {}
    for lang in ("af", "zu", "xh", "nso"):
        f = os.path.join(REPO, "roles", "app_i18n_%s.json" % lang)
        try:
            t = (json.load(open(f, encoding="utf-8")) or {}).get("t") or {}
        except Exception:
            continue
        have = sum(1 for a in asked_chrome if a in t)
        dict_cov[lang] = {"checked": have, "of": len(asked_chrome),
                          "percent": round(100.0 * have / len(asked_chrome), 1) if asked_chrome else 0.0}
    # 4. errors that only the longer text provoked
    new_errors = {k: v for k, v in sp.get("errors", {}).items() if v != se.get("errors", {}).get(k)}

    pct = round(100.0 * tr / total, 1) if total else 0.0
    breaks = sorted(new_breaks.items(), key=lambda kv: (-len(kv[1]["states"]), kv[0]))
    rep = {
        "built": "1 Oct 2026 (I18N_READINESS item 3)",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "how": "python3 scripts/i18n_pseudo_locale.py",
        "fixture": bool(fx), "states_walked": len(ep), "language_slot": SLOT,
        "coverage": {"visible_text_nodes": total, "reached_by_paint_layer": tr, "percent": pct,
                     "marked_do_not_translate": nt,
                     "chrome_strings_missed": len(chrome_miss),
                     "other_untranslated_nodes (listing content / data -- not stored)": other_miss},
        "chrome_strings_missed": [{"text": t, "states": sorted(s)[:6], "n_states": len(s)}
                                  for t, s in sorted(chrome_miss.items(), key=lambda kv: (-len(kv[1]), kv[0]))][:150],
        "layout_breaks_new_in_pseudo": [{"where": k, "kind": k.split("  ")[0], "text": v["text"],
                                         "states": v["states"][:6], "n_states": len(v["states"])}
                                        for k, v in breaks][:150],
        "layout_issues_already_in_english": base_issues,
        "inventory_gaps": {"chrome_phrases_asked_not_in_inventory": len(gaps),
                           "data_phrases_asked (listings/wonders/geo -- count only)": len(asked_data),
                           "sample": [g for g in gaps if not re.search(r"\d{3,}", g)][:40]},
        "checked_dictionary_coverage_of_chrome_asked": dict_cov,
        "page_errors_new_in_pseudo": new_errors,
        "phrases_asked_by_paint_layer": len(pse.asked),
    }
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    H.say("coverage: %d of %d visible text nodes reached by the paint layer (%.1f%%); %d chrome strings stayed English"
          % (tr, total, pct, len(chrome_miss)))
    H.say("layout: %d element(s) clip or run off-screen ONLY in the longer text (%d issues already in English)"
          % (len(breaks), base_issues))
    H.say("inventory gaps: %d chrome phrases the paint layer asked for that the extractor never listed "
          "(+%d phrases from listing/place data)" % (len(gaps), len(asked_data)))
    H.say("checked dictionaries cover the chrome asked for: " +
          ", ".join("%s %.1f%%" % (k, v["percent"]) for k, v in dict_cov.items()))
    if new_errors:
        H.say("page errors new in pseudo: %s" % list(new_errors)[:5])
    H.say("report -> %s" % os.path.relpath(REPORT, REPO))
    return 1 if (strict and breaks) else 0


if __name__ == "__main__":
    if "--generate" in sys.argv:
        generate()
        sys.exit(0)
    sys.exit(run(strict="--strict" in sys.argv))

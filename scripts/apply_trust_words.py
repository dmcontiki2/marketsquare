#!/usr/bin/env python3
"""apply_trust_words.py -- CC-005 / TRUST-WORDS-1 (27 Sep 2026, David approved the wording as written).

RUL-088: a Trust Score is a score, never a statement about a person. The band labels name the STRENGTH OF
EVIDENCE, never a quality of the seller (the weakest-holder test, CHANGE_REGISTER CC-005):
    New (0-39) · Some evidence (40+) · Strong evidence (70+) · Fullest evidence (90+)
plus two standing lines wherever the score is shown or filtered (EXPLAIN, NEWSELLER below).
Every hunk is exact-match and counted; the script refuses (writes nothing) if any anchor moved.
"""
import io, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPLAIN = ("Trust Score reflects the evidence a seller has supplied and the checks we have completed. "
           "It is a score, not a guarantee or an assessment of character.")
NEWSELLER = "A new seller simply has less evidence — not a mark against them."
SCALE_OLD = "0 · New · 40 · Established · 70 · Trusted · 90 · Highly Trusted"
SCALE_NEW = "0 · New · 40 · Some evidence · 70 · Strong evidence · 90 · Fullest evidence"
NOTE = ('<div class="tscale-note" style="font-size:11px;color:var(--text-3);margin-top:5px;line-height:1.45;">'
        '<span>' + EXPLAIN + '</span> <span>' + NEWSELLER + '</span></div>')

H = {
 "ms.js": [
  ("  if(s<70)return{label:'Established',c:'var(--blue)',bg:'var(--blue-bg)'};\n"
   "  if(s<90)return{label:'Trusted',c:'var(--green)',bg:'var(--green-bg)'};\n"
   "  return{label:'Highly Trusted',c:'var(--gold)',bg:'var(--gold-bg)'};",
   "  if(s<70)return{label:'Some evidence',c:'var(--blue)',bg:'var(--blue-bg)'};\n"
   "  if(s<90)return{label:'Strong evidence',c:'var(--green)',bg:'var(--green-bg)'};\n"
   "  return{label:'Fullest evidence',c:'var(--gold)',bg:'var(--gold-bg)'};", 1),
  ('<div class="tscale" style="color:${t.c};">' + SCALE_OLD + '</div></div>',
   '<div class="tscale" style="color:${t.c};">' + SCALE_NEW + '</div>' + NOTE + '</div>', 1),
  ('<div class="tscale" style="color:${tColor};">' + SCALE_OLD + '</div></div>',
   '<div class="tscale" style="color:${tColor};">' + SCALE_NEW + '</div>' + NOTE + '</div>', 1),
  ('color:#60a5fa;">Established</div>', 'color:#60a5fa;">Some evidence</div>', 1),
  ('color:#34d399;">Trusted</div>', 'color:#34d399;">Strong evidence</div>', 1),
  ('color:#fbbf24;">Highly Trusted</div>', 'color:#fbbf24;">Fullest evidence</div>', 1),
  ("  if(score>=90) return {tier:'Highly Trusted',", "  if(score>=90) return {tier:'Fullest evidence',", 1),
  ("  if(score>=70) return {tier:'Trusted',", "  if(score>=70) return {tier:'Strong evidence',", 1),
  ("  if(score>=40) return {tier:'Established',", "  if(score>=40) return {tier:'Some evidence',", 1),
  ("{0:'Any seller', 40:'Established+ (40)', 70:'Trusted+ (70)', 90:'Highly Trusted (90)'}",
   "{0:'Any seller', 40:'Some evidence (40+)', 70:'Strong evidence (70+)', 90:'Fullest evidence (90+)'}", 2),
  ("const tLabel = trust >= 90 ? 'Highly Trusted' : trust >= 70 ? 'Trusted' : trust >= 40 ? 'Established' : 'New';",
   "const tLabel = trust >= 90 ? 'Fullest evidence' : trust >= 70 ? 'Strong evidence' : trust >= 40 ? 'Some evidence' : 'New';", 1),
  ("[40,'Established'] : s < 70 ? [70,'Trusted'] : s < 90 ? [90,'Highly Trusted']",
   "[40,'Some evidence'] : s < 70 ? [70,'Strong evidence'] : s < 90 ? [90,'Fullest evidence']", 1),
  ("<td>Established \\u2014 blue badge; standard listing position</td>", "<td>Some evidence \\u2014 blue badge; standard listing position</td>", 1),
  ("<td>Trusted \\u2014 green badge; higher visibility</td>", "<td>Strong evidence \\u2014 green badge; higher visibility</td>", 1),
  ("<td>Highly Trusted \\u2014 gold badge + featured position</td>", "<td>Fullest evidence \\u2014 gold badge + featured position</td>", 1),
 ],
 "marketsquare.html": [
  ("to find serious sellers. Highly Trusted sellers have verified ID, phone, and a strong track record.",
   "to see sellers by the evidence they have supplied. " + EXPLAIN + " " + NEWSELLER, 1),
  ('onclick="setLmTrust(40)">Established+ (40)</div>', 'onclick="setLmTrust(40)">Some evidence (40+)</div>', 1),
  ('onclick="setLmTrust(70)">Trusted+ (70)</div>', 'onclick="setLmTrust(70)">Strong evidence (70+)</div>', 1),
  ('onclick="setLmTrust(90)">Highly Trusted (90)</div>', 'onclick="setLmTrust(90)">Fullest evidence (90+)</div>', 1),
  ("Recommended: <strong>Highly Trusted</strong> for high-value items.", "Recommended: <strong>Fullest evidence</strong> for high-value items.", 1),
  ('onclick="wlSetTrustFilter(40)">Established+ (40)</button>', 'onclick="wlSetTrustFilter(40)">Some evidence (40+)</button>', 1),
  ('onclick="wlSetTrustFilter(70)">Trusted+ (70)</button>', 'onclick="wlSetTrustFilter(70)">Strong evidence (70+)</button>', 1),
  ('onclick="wlSetTrustFilter(90)">Highly Trusted (90)</button>', 'onclick="wlSetTrustFilter(90)">Fullest evidence (90+)</button>', 1),
 ],
 "quick.html": [
  ("  return ts>=90?{n:'Highly trusted',c:'#FBBF24'}\n       : ts>=70?{n:'Trusted',c:'#10B981'}\n       : ts>=40?{n:'Established',c:'#3B82F6'}",
   "  return ts>=90?{n:'Fullest evidence',c:'#FBBF24'}\n       : ts>=70?{n:'Strong evidence',c:'#10B981'}\n       : ts>=40?{n:'Some evidence',c:'#3B82F6'}", 1),
 ],
 "eula_clean.html": [
  ("<td>Established — blue badge; standard listing position</td>", "<td>Some evidence — blue badge; standard listing position</td>", 1),
  ("<td>Trusted — green badge; higher visibility</td>", "<td>Strong evidence — green badge; higher visibility</td>", 1),
  ("<td>Highly Trusted — gold badge + featured position</td>", "<td>Fullest evidence — gold badge + featured position</td>", 1),
 ],
 "terms.html": [
  ("<td>Established — blue badge; standard listing position</td>", "<td>Some evidence — blue badge; standard listing position</td>", 1),
  ("<td>Trusted — green badge; higher visibility</td>", "<td>Strong evidence — green badge; higher visibility</td>", 1),
  ("<td>Highly Trusted — gold badge + featured position</td>", "<td>Fullest evidence — gold badge + featured position</td>", 1),
 ],
 "bea_main.py": [
  ('        if s < 70: return "Established — blue badge"\n        if s < 90: return "Trusted — green badge"\n'
   '        return "Highly Trusted — gold badge + featured at top of results"',
   '        if s < 70: return "Some evidence — blue badge"\n        if s < 90: return "Strong evidence — green badge"\n'
   '        return "Fullest evidence — gold badge + featured at top of results"', 1),
  ('        "  40–69: Established — blue badge\\n"\n        "  70–89: Trusted — green badge\\n"\n'
   '        "  90–100: Highly Trusted — gold badge, top of search results\\n\\n"',
   '        "  40–69: Some evidence — blue badge\\n"\n        "  70–89: Strong evidence — green badge\\n"\n'
   '        "  90–100: Fullest evidence — gold badge, top of search results\\n"\n'
   '        "  (CC-005 / RUL-088: the bands name the STRENGTH OF EVIDENCE, never a quality of the person -- '
   'never call a seller trusted, trustworthy or reliable.)\\n\\n"', 1),
  ('    (40, 69,  "Established",    "blue"),\n    (70, 89,  "Trusted",        "green"),\n    (90, 100, "Highly Trusted", "gold"),',
   '    (40, 69,  "Some evidence",    "blue"),    # CC-005 / TRUST-WORDS-1 (27 Sep 2026): evidence strength, never\n'
   '    (70, 89,  "Strong evidence",  "green"),   # a quality of the person (RUL-088, weakest-holder test)\n'
   '    (90, 100, "Fullest evidence", "gold"),', 1),
 ],
}

# app-wide page translator (checked words, RUL-165: Claude's drafts are the live versions)
T = {
 "Some evidence": ("Enkele bewyse", "Obunye ubufakazi", "Obunye ubungqina", "Bohlatse bjo bongwe"),
 "Strong evidence": ("Sterk bewyse", "Ubufakazi obuqinile", "Ubungqina obomeleleyo", "Bohlatse bjo bo tiilego"),
 "Fullest evidence": ("Volledigste bewyse", "Ubufakazi obuphelele", "Ubungqina obupheleleyo", "Bohlatse bjo bo feletšego"),
 "Some evidence (40+)": ("Enkele bewyse (40+)", "Obunye ubufakazi (40+)", "Obunye ubungqina (40+)", "Bohlatse bjo bongwe (40+)"),
 "Strong evidence (70+)": ("Sterk bewyse (70+)", "Ubufakazi obuqinile (70+)", "Ubungqina obomeleleyo (70+)", "Bohlatse bjo bo tiilego (70+)"),
 "Fullest evidence (90+)": ("Volledigste bewyse (90+)", "Ubufakazi obuphelele (90+)", "Ubungqina obupheleleyo (90+)", "Bohlatse bjo bo feletšego (90+)"),
 SCALE_NEW: ("0 · Nuut · 40 · Enkele bewyse · 70 · Sterk bewyse · 90 · Volledigste bewyse",
             "0 · Kusha · 40 · Obunye ubufakazi · 70 · Ubufakazi obuqinile · 90 · Ubufakazi obuphelele",
             "0 · Usemtsha · 40 · Obunye ubungqina · 70 · Ubungqina obomeleleyo · 90 · Ubungqina obupheleleyo",
             "0 · E mpsha · 40 · Bohlatse bjo bongwe · 70 · Bohlatse bjo bo tiilego · 90 · Bohlatse bjo bo feletšego"),
 EXPLAIN: ("Die Trust Score wys die bewyse wat ’n verkoper verskaf het en die kontroles wat ons voltooi het. Dit is ’n telling, nie ’n waarborg of ’n oordeel oor iemand se karakter nie.",
           "I-Trust Score ikhombisa ubufakazi obunikezwe umthengisi kanye nokuhlola esikuqedile. Iyisikolo, hhayi isiqinisekiso noma ukwahlulela isimilo somuntu.",
           "I-Trust Score ibonisa ubungqina obunikezwe ngumthengisi kunye nokuhlola esikugqibileyo. Linqaku, ayisosiqinisekiso okanye uvavanyo lwesimilo somntu.",
           "Trust Score e bontšha bohlatse bjo morekiši a bo abilego le ditekolo tšeo re di feditšego. Ke dintlha, ga se kgonthišetšo goba kahlolo ya semelo sa motho."),
 NEWSELLER: ("’n Nuwe verkoper het bloot minder bewyse — dit tel nie teen hulle nie.",
             "Umthengisi omusha umane abe nobufakazi obuncane — akusona isici esibi ngaye.",
             "Umthengisi omtsha unobungqina obuncinci nje — asiyonto embi ngaye.",
             "Morekiši yo moswa o na le bohlatse bjo bonnyane fela — ga se selo se sebe ka yena."),
}
LEADIN = "to see sellers by the evidence they have supplied. " + EXPLAIN + " " + NEWSELLER
T[LEADIN] = tuple("%s %s %s" % (a, b, c) for a, b, c in zip(
    ("om verkopers te sien volgens die bewyse wat hulle verskaf het.",
     "ukuze ubone abathengisi ngokobufakazi abebunikezile.",
     "ukuze ubone abathengisi ngokobungqina ababunikezileyo.",
     "go bona barekiši go ya ka bohlatse bjo ba bo abilego."), T[EXPLAIN], T[NEWSELLER]))
KEEP_EN = ["Some evidence — blue badge; standard listing position", "Strong evidence — green badge; higher visibility",
           "Fullest evidence — gold badge + featured position"]   # Terms rows: the English binds (RUL-143)
# Quick door words (lower-cased on screen): [af, zu, st, xh, nso]
QW = {"fullest evidence": ["volledigste bewyse", "ubufakazi obuphelele", "", "ubungqina obupheleleyo", "bohlatse bjo bo feletšego"],
      "strong evidence": ["sterk bewyse", "ubufakazi obuqinile", "", "ubungqina obomeleleyo", "bohlatse bjo bo tiilego"],
      "some evidence": ["enkele bewyse", "obunye ubufakazi", "", "obunye ubungqina", "bohlatse bjo bongwe"]}
QW.update({k[0].upper() + k[1:]: v for k, v in list(QW.items())})   # the title="" attribute carries the capitalised form

def main():
    out = {}
    for rel, hunks in H.items():
        s = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        for old, new, n in hunks:
            c = s.count(old)
            if c != n:
                sys.exit("REFUSED %s: expected %d x %r, found %d -- nothing written" % (rel, n, old[:70], c))
            s = s.replace(old, new)
        out[rel] = s
    for rel, s in out.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(s)
        print("%s: %d hunk(s)" % (rel, len(H[rel])))
    for i, lang in enumerate(("af", "zu", "xh", "nso")):
        p = os.path.join(ROOT, "roles", "app_i18n_%s.json" % lang); j = json.load(io.open(p, encoding="utf-8"))
        for k, v in T.items():
            j["t"][k] = v[i]
        for k in KEEP_EN:
            if k not in j["en"]:
                j["en"].append(k)
        io.open(p, "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1) + "\n")
        print("roles/app_i18n_%s.json: %d phrase(s) + %d kept in English" % (lang, len(T), len(KEEP_EN)))
    p = os.path.join(ROOT, "roles", "quick_i18n.json"); j = json.load(io.open(p, encoding="utf-8"))
    j["w"].update(QW)
    io.open(p, "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1) + "\n")
    L = j["langs"]
    d = {"w": {en: dict(zip(L, v)) for en, v in j["w"].items()},
         "p": [dict(zip(["en"] + L, x)) for x in j["p"]],
         "r": [dict(zip(["en"] + L, x)) for x in j["r"]]}
    ib = ("/* QUICK-I18N:BEGIN -- generated by scripts/sync_quick_roles.py from roles/quick_i18n.json; do not edit */\n"
          "var QI18N = %s;\n/* QUICK-I18N:END */" % json.dumps(d, ensure_ascii=False))
    qp = os.path.join(ROOT, "quick.html"); q = io.open(qp, encoding="utf-8").read()
    ipat = re.compile(r"/\* QUICK-I18N:BEGIN.*?/\* QUICK-I18N:END \*/", re.S)
    if not ipat.search(q): sys.exit("quick.html has no QUICK-I18N markers")
    q2 = ipat.sub(lambda m: ib, q)
    io.open(qp, "w", encoding="utf-8").write(q2)
    io.open(os.path.join(ROOT, "genie", "HARNESS.html"), "w", encoding="utf-8").write(q2)
    print("quick i18n: %d word(s); QI18N regenerated; genie/HARNESS.html = quick.html" % len(QW))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""build_role_guides.py -- ROLE-GUIDES-1 (David, 8 Oct 2026): "when i select car washer worker and then the HOW, it then
shows me the 'home cleaner' card flow ... please check them and update to be relevant to the selections".

Every work role that had no walked guide of its own borrowed a parent's (home_cleaner, plumber, electrician, nanny -- the
'serves' lists). This writes stories/<role>.json for each of them: the parent's walked story (same steps, same proof, same
pass flags), with
  - the role's own name in the title, the label and every [[button]] that named the parent's job and group;
  - step 2 telling her to pick HER group and HER job (no list of other jobs);
  - the price step in her role's own way of charging (per car with packages, per visit, per job);
  - her role's own Quick screens for the steps Quick shows (her job tile, areas, days or qualification, price, her listing),
    captured on the live site by scripts/role_guide_screens.py into stories/img/<role>/r_<screen>.jpg.
Steps after saving (the Seller Hub, publishing, Buzz, a customer's view) keep the parent's walked screens -- they are the
same screens for every job, walked with real people. Re-run after a role or a parent guide changes:
    python3 scripts/build_role_guides.py        then  python3 scripts/build_help.py  and  --push-images
A role with a hand-walked guide of its own (no 'derived_from') is never overwritten.
"""
import copy, io, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "stories")
IMG = os.path.join(ST, "img")
PARENTS = ("home_cleaner", "plumber", "electrician", "nanny")
LANGS = ("en", "af", "zu", "xh", "nso")
LOCAL = ("zu", "xh", "nso")          # an override we cannot write in these falls back to English on the page (HELP-LANG-1)

def quick_roles():
    q = io.open(os.path.join(ROOT, "quick.html"), encoding="utf-8").read()
    m = re.search(r"var SVC_ROLES = (\[.*?\]);\n", q)
    return {r["k"]: r for r in json.loads(m.group(1))}

def role_names():
    reg = json.load(io.open(os.path.join(ROOT, "roles", "role_registry.json"), encoding="utf-8"))
    i18n = json.load(io.open(os.path.join(ROOT, "roles", "quick_i18n.json"), encoding="utf-8"))
    L = i18n["langs"]
    out = {}
    for r in reg["roles"]:
        en = r["label"]["en"]; w = i18n["w"].get(en) or []
        names = {"en": en}
        for lg in LANGS[1:]:
            v = (r["label"].get(lg) if lg != "nso" else None) or (w[L.index(lg)] if lg in L and len(w) > L.index(lg) else None)
            names[lg] = v or en
        out[r["key"]] = names
    return out

PRICE = {   # her role's own way of charging -- quick.html setsFor (PIECE_VISIT / PIECE_JOB / PRICE_MENU)
    "car": {"en": ["Set your price per car", "Quick opens on [[Per car]]. Type a price for each kind of clean you offer — [[Wash only]], "
                   "[[Wash & vacuum]], [[Wash, vacuum, tyres & dashboard]], [[Full valet (inside & out)]] — and leave the rest empty. "
                   "Your listing shows 'From' your lowest price and lists every package."],
            "af": ["Stel jou prys per kar", "Quick begin by [[Per car]]. Tik 'n prys vir elke soort skoonmaak wat jy aanbied — [[Wash only]], "
                   "[[Wash & vacuum]], [[Wash, vacuum, tyres & dashboard]], [[Full valet (inside & out)]] — en los die res leeg. "
                   "Jou advertensie wys 'Vanaf' jou laagste prys en lys elke pakket."]},
    "visit": {"en": ["Set your price per visit", "Quick opens on [[Per visit]]: type what one visit costs. A price for a piece of work has "
                     "no minimum-wage floor. [[Per hour]] and [[Per day]] are one tap away."],
              "af": ["Stel jou prys per besoek", "Quick begin by [[Per visit]]: tik wat een besoek kos. 'n Prys vir 'n stuk werk het geen "
                     "minimumloon-vloer nie. [[Per hour]] en [[Per day]] is een tik weg."]},
    "job": {"en": ["Set your price per job", "Quick opens on [[Per job]]: type what one job costs. A price for a piece of work has no "
                   "minimum-wage floor. [[Per visit]] and [[Per hour]] are one tap away."],
            "af": ["Stel jou prys per taak", "Quick begin by [[Per job]]: tik wat een taak kos. 'n Prys vir 'n stuk werk het geen "
                   "minimumloon-vloer nie. [[Per visit]] en [[Per hour]] is een tik weg."]},
}
PIECE = {"car_washer": "car", "hair_braider": "visit", "hairdresser": "visit", "nail_technician": "visit", "pool_cleaner": "visit",
         "seamstress_tailor": "job", "carpet_washer": "job"}
LICENCE_STEP2 = {"en": "Choose the kind of work, then your trade. The law asks for a licence for this work, so Quick tells you what our team checks.",
                 "af": "Kies die soort werk, dan jou ambag. Die wet vra 'n lisensie vir hierdie werk, so Quick sê vir jou wat ons span nagaan."}
CARES_FOR = {"en": ["Tick who you care for", "[[An older person]], [[A person with a disability]] or [[Someone recovering at home]]. "
                    "Families see it on your listing."],
             "af": ["Merk vir wie jy sorg", "[[An older person]], [[A person with a disability]] of [[Someone recovering at home]]. "
                    "Gesinne sien dit op jou advertensie."]}

def first_sentence(t):
    m = re.match(r"^(.*?[.!?])(\s|$)", t)
    return m.group(1) if m else t

def screen_for(step, last_draft):
    q = step.get("quick") or []
    for k in ("what", "qual", "where", "days", "price", "how"):
        if k in q:
            return k
    if q == ["draft"]:          # her own listing card (the nanny guide has two save steps on it)
        return "draft"
    return None

def build(parent, role, R, names, pnames):
    d = copy.deepcopy(parent)
    pt = parent["type"]; pen = pnames["en"]; pgroup = re.search(r"\[\[([^\]]+)\]\], (?:then|dan)", parent["steps"][1]["en"][0]).group(1)
    d["type"] = role; d["serves"] = []; d["derived_from"] = pt
    d["label"] = {lg: names[lg] for lg in LANGS}
    d["title"] = {}
    for lg in LANGS:
        pl = parent["label"].get(lg, pen); tt = parent["title"].get(lg, parent["title"]["en"])
        d["title"][lg] = names[lg] + tt[len(pl):] if tt.startswith(pl) else names["en"] + parent["title"]["en"][len(pen):]
    drafts = [s for s in d["steps"] if (s.get("quick") or []) == ["draft"]]
    last_draft = drafts[-1] if drafts else None
    shots = {}
    for s in d["steps"]:
        for lg in LANGS:
            if lg in s:
                s[lg] = [x.replace("[[%s]]" % pen, "[[%s]]" % R["l"]).replace("[[%s]]" % pgroup, "[[%s]]" % R["g"]) for x in s[lg]]
        k = screen_for(s, last_draft)
        if k and os.path.isfile(os.path.join(IMG, role, "r_%s.jpg" % k)):
            s["img"] = "r_%s" % k; shots[k] = True
        if s["n"] == 2:
            for lg in LANGS:
                if lg in s:
                    s[lg][1] = first_sentence(s[lg][1])
            if pt == "electrician":
                for lg in LOCAL: s.pop(lg, None)
                s["en"][1] = LICENCE_STEP2["en"]; s["af"][1] = LICENCE_STEP2["af"]
        if (s.get("quick") or []) == ["price"] and PIECE.get(role):
            for lg in LOCAL: s.pop(lg, None)
            s["en"] = list(PRICE[PIECE[role]]["en"]); s["af"] = list(PRICE[PIECE[role]]["af"])
        if pt == "nanny":
            if role == "caregiver" and s.get("img") == "f2_08a_ages":
                for lg in LOCAL: s.pop(lg, None)
                s["en"] = list(CARES_FOR["en"]); s["af"] = list(CARES_FOR["af"])
            if "a nanny" in s["en"][1]:
                s["en"][1] = s["en"][1].replace("a nanny", "a " + names["en"].lower())
                s["af"][1] = s["af"][1].replace("'n kinderoppasser", "'n " + names["af"].lower())
                for lg in LOCAL: s.pop(lg, None)
    for s in d["steps"]:
        src = os.path.join(IMG, pt, s["img"] + ".jpg"); dst = os.path.join(IMG, role, s["img"] + ".jpg")
        if not s["img"].startswith("r_") and os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst) or os.path.getsize(dst) != os.path.getsize(src):
                shutil.copyfile(src, dst)
    return d, sorted(shots)

def main():
    roles = quick_roles(); names = role_names(); made = []
    for pt in PARENTS:
        parent = json.load(io.open(os.path.join(ST, pt + ".json"), encoding="utf-8"))
        for role in parent.get("serves", []):
            fn = os.path.join(ST, role + ".json")
            if os.path.isfile(fn) and not json.load(io.open(fn, encoding="utf-8")).get("derived_from"):
                continue          # a hand-walked guide of its own -- never overwritten
            if role not in roles:
                print("skip %s: not a live Quick role" % role); continue
            d, shots = build(parent, role, roles[role], names[role], names.get(pt) or parent["label"])
            io.open(fn, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
            made.append((role, pt, shots))
    for role, pt, shots in made:
        print("%-34s from %-13s own screens: %s" % (role, pt, ", ".join(shots) or "NONE"))
    print("%d role guides written" % len(made))

if __name__ == "__main__":
    main()

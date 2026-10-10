#!/usr/bin/env python3
"""build_trainer_guides.py -- TRAINERS-DOOR-1 (RUL-217): a How story guide for every trainer role, the way ROLE-GUIDES-1
(build_role_guides.py) gave every casual work role its own.

David, 8 Oct 2026: "the same flows, Hows etc". Each trainer role gets stories/<role>.json derived from the walked Tutors
guide (stories/tutors_maths.json, F5): the same steps, proof and pass flags, with
  - the sport's own name in the label, the title and every button that named the parent's subject;
  - step 2 telling her to tap Sport & fitness, then HER sport group and HER sport;
  - the school-level and online/in-person steps removed (a trainer is not asked them -- 5 taps to a draft, RUL-117);
  - the price step in a coach's way of charging: per session, per month or per package, no minimum-wage floor (RUL-217(c));
  - for the sports that commonly coach children, the police-clearance note (RUL-217(d) / RUL-153).
A step whose words changed keeps English and Afrikaans; its isiZulu, isiXhosa and Sepedi fall back to English on the page
(HELP-LANG-1) until a first-language reader writes them. Screens: the parent's walked screens are copied for every step;
own Quick screens for the trainer steps are captured later by scripts/role_guide_screens.py. A guide with no
'derived_from' (hand-walked) is never overwritten.
    python3 scripts/build_trainer_guides.py   then   python3 scripts/build_help.py   and   --push-images
"""
import copy, io, json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "stories")
IMG = os.path.join(ST, "img")
PARENT = "tutors_maths"
NANNY = "nanny"            # the walked guide whose clearance step the clearance sports reuse
GATE_STEP = GATE_NOTE = None
LANGS = ("en", "af", "zu", "xh", "nso")
LOCAL = ("zu", "xh", "nso")
OWN = {"f5_02_what": "r_what", "f5_05_price": "r_price", "f5_06_where": "r_where", "f5_07_draft": "r_draft",
       "f5_16_find_what": "r_find_what", "f5_19_results": "r_results",
       # TRAINER-SCREENS-2 (10 Oct 2026): the TrustSquare side too -- her Edit, her Seller Hub, her advert, the parent's
       # Join queue and introductions -- captured as the QA test seller / parent with her sport on the screen
       "f5_09_photos": "t_photos", "f5_12_published": "t_published", "f5_20_detail": "t_detail", "f5_21_ask": "t_ask",
       "f5_24_request": "t_request", "f5_25_accept": "t_accept", "f5_26_buyer_intros": "t_buyer_intros"}


def names():
    reg = json.load(io.open(os.path.join(ROOT, "roles", "role_registry.json"), encoding="utf-8"))
    i18n = json.load(io.open(os.path.join(ROOT, "roles", "quick_i18n.json"), encoding="utf-8"))
    L = i18n["langs"]
    out = []
    for r in reg["roles"]:
        if r.get("service_class") != "Trainers" or r.get("status") != "in":
            continue
        def tr(en):
            w = i18n["w"].get(en) or []
            d = {"en": en}
            for lg in LANGS[1:]:
                d[lg] = (w[L.index(lg)] if lg in L and len(w) > L.index(lg) and w[L.index(lg)] else en)
            return d
        out.append((r, tr(r["label"]["en"]), tr(r["group"])))
    return out


def setlang(s, en, af):
    for lg in LOCAL:
        s.pop(lg, None)
    s["en"] = list(en); s["af"] = list(af)


def build(parent, r, nm, gp):
    d = copy.deepcopy(parent)
    k = r["key"]
    d["type"] = k; d["serves"] = []; d["derived_from"] = PARENT
    d["label"] = {lg: nm[lg] for lg in LANGS}
    ptitle = parent["title"]; plabel = parent["label"]
    d["title"] = {"en": nm["en"] + ": from listing to the people who find you",
                  "af": nm["af"] + ": van advertensie tot die mense wat jou vind"}
    for lg in LOCAL:
        t = ptitle.get(lg, ""); pl = plabel.get(lg, "")
        d["title"][lg] = (nm[lg] + t[len(pl):]) if (t and pl and t.startswith(pl)) else d["title"]["en"]
    gated = (r.get("gate") or {}).get("type") == "police_clearance"
    clear = gated or bool(r.get("clearance_score"))   # RUL-219: the upload step stays as a Trust Score step, not a gate
    G, N = gp["en"], nm["en"]
    steps = []
    for s in d["steps"]:
        q = s.get("quick") or []
        img = s.get("img")
        if img in ("f5_03_level", "f5_04_mode", "f5_17_find_level"):
            continue                      # a trainer is not asked a school level or online / in person
        if img == "f5_02_what":
            setlang(s, ["Tap [[Sport & fitness]], then your sport",
                        "Pick [[%s]], then [[%s]]. Coach something else? Tap [[Another option]] and type it." % (G, N)],
                       ["Tik [[Sport & fitness]], dan jou sport",
                        "Kies [[%s]], dan [[%s]]. Rig jy iets anders af? Tik [[Another option]] en tik dit in." % (G, N)])
        elif img == "f5_05_price":
            setlang(s, ["Set your price per session",
                        "Quick opens on [[Per session]]: type what one session costs. [[Per month]] and [[Per package]] are one tap "
                        "away. Coaching is priced for the session, so there is no minimum-wage floor."],
                       ["Stel jou prys per sessie",
                        "Quick begin by [[Per session]]: tik wat een sessie kos. [[Per month]] en [[Per package]] is een tik weg. "
                        "Afrigting word per sessie geprys, so daar is geen minimumloon-vloer nie."])
        elif img == "f5_06_where":
            setlang(s, ["Tick the areas where you train people",
                        "You can tick more than one; anyone searching any of them finds you."],
                       ["Merk die gebiede waar jy mense afrig",
                        "Jy kan meer as een merk; enigiemand wat in enige van hulle soek, vind jou."])
        elif img == "f5_07_draft":
            setlang(s, ["Check your listing, then save",
                        "Your sport, your price and your areas are on it. Add your first name and email and tap [[Save my listing]]."],
                       ["Kyk na jou advertensie en stoor dit",
                        "Jou sport, jou prys en jou gebiede is daarop. Voeg jou voornaam en e-pos by en tik [[Save my listing]]."])
        elif img == "f5_09_photos":
            setlang(s, ["Add photos of where you train people",
                        "In TrustSquare tap [[Edit]], then [[Add Photo]]: the field, court, pool or gym and your equipment, no "
                        "children's faces. Then tap [[Save Changes]] to keep them."],
                       ["Voeg foto's by van waar jy mense afrig",
                        "Tik in TrustSquare [[Edit]], dan [[Add Photo]]: die veld, baan, swembad of gimnasium en jou toerusting, "
                        "geen kinders se gesigte nie. Tik dan [[Save Changes]] om hulle te hou."])
        elif img == "f5_13_buzz_link":
            setlang(s, ["Send your Buzz link to the people you already train",
                        "In [[My Space]], open [[Buzz]] and tap [[Get my link]]. One link for all of them: [[Send on WhatsApp]] or [[Copy]]."],
                       ["Stuur jou Buzz-skakel aan die mense wat jy reeds afrig",
                        "Maak [[Buzz]] in [[My Space]] oop en tik [[Get my link]]. Een skakel vir almal: [[Send on WhatsApp]] of [[Copy]]."])
        elif img == "f5_16_find_what":
            setlang(s, ["Someone new taps [[Find a tutor]], then [[Sport & fitness]]",
                        "Then [[%s]] and [[%s]]: only coaches of that sport are shown." % (G, N)],
                       ["Iemand nuut tik [[Find a tutor]], dan [[Sport & fitness]]",
                        "Dan [[%s]] en [[%s]]: net afrigters van daardie sport word gewys." % (G, N)])
        elif img == "f5_20_detail":
            setlang(s, ["She sees your sport, your price and your trust score",
                        "Your photos are at the top, your price under them. Your name and number stay hidden."],
                       ["Sy sien jou sport, jou prys en jou vertrouetelling",
                        "Jou foto's is bo, jou prys daaronder. Jou naam en nommer bly versteek."])
        elif img == "f5_08_saved" and s.get("ch") == "c5":
            setlang(s, ["Pass Quick on", "Tap [[Pass Quick on to someone]] and share it with a friend who coaches too."],
                       ["Gee Quick aan", "Tik [[Pass Quick on to someone]] en deel dit met 'n vriend wat ook afrig."])
        steps.append(s)
    if clear:      # RUL-217(d): the walked nanny guide's clearance step (TrustSquare's 'Upload my police clearance'), after Publish
        at = next((i for i, x in enumerate(steps) if x.get("img") == "f5_12_published"), len(steps) - 1) + 1
        g = copy.deepcopy(GATE_STEP); g["ch"] = steps[at - 1].get("ch", g.get("ch"))
        steps.insert(at, g)
    for i, s in enumerate(steps):
        s["n"] = i + 1
    d["steps"] = steps
    if clear:
        n = next(x["n"] for x in steps if x.get("gate"))
        d["gate_note"] = {lg: re.sub(r"\b\d+\b", str(n), t, count=1) for lg, t in GATE_NOTE.items()}
        if not gated:   # RUL-219 (David 10 Oct 2026): listed and visible at once; the clearance is a Trust Score signal
            d["gate_note"] = {"en": "Step %d is optional: your listing is visible straight away. A checked police clearance adds points to your Trust Score, and parents look for it." % n,
                              "af": "Stap %d is opsioneel: jou advertensie is dadelik sigbaar. 'n Nagegane polisieklaring voeg punte by jou vertrouetelling, en ouers soek daarna." % n}
    # TRAINER-SCREENS-1 (David, 10 Oct 2026: "this is the Sport & fitness but it is showing maths"): every Quick screen
    # the guide shows is her OWN sport's, captured on the live site by scripts/trainer_guide_screens.py into
    # stories/img/<sport>/r_<screen>.jpg -- her sport tile, her price, her areas, her listing, her saved card, and a
    # finder's sport tiles and results. A step falls back to the walked Maths screen only while its own is missing.
    for s in steps:
        own = OWN.get(s["img"])
        if s["img"] == "f5_08_saved":
            own = "r_saved"
        if own and os.path.isfile(os.path.join(IMG, k, own + ".jpg")):
            s["img"] = own
            if own == "r_what":
                s["quick"] = ["group", "what"]       # How opened on the sport-group screen lands on this card too
    for s in steps:
        if s["img"].startswith(("r_", "t_")):
            continue
        src = os.path.join(IMG, NANNY if s.get("gate") else PARENT, s["img"] + ".jpg"); dst = os.path.join(IMG, k, s["img"] + ".jpg")
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst) or os.path.getsize(dst) != os.path.getsize(src):
                shutil.copyfile(src, dst)
    return d


def main():
    global GATE_STEP, GATE_NOTE
    parent = json.load(io.open(os.path.join(ST, PARENT + ".json"), encoding="utf-8"))
    nanny = json.load(io.open(os.path.join(ST, NANNY + ".json"), encoding="utf-8"))
    GATE_STEP = next(x for x in nanny["steps"] if x.get("gate")); GATE_NOTE = nanny["gate_note"]
    made = 0
    for r, nm, gp in names():
        fn = os.path.join(ST, r["key"] + ".json")
        if os.path.isfile(fn) and not json.load(io.open(fn, encoding="utf-8")).get("derived_from"):
            continue          # a hand-walked guide of its own -- never overwritten
        d = build(parent, r, nm, gp)
        io.open(fn, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        made += 1
    print("%d trainer guides written from %s" % (made, PARENT))


if __name__ == "__main__":
    main()

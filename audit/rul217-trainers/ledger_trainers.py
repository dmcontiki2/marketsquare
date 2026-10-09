@entry("RG-0947", "TRAINERS-DOOR-1 (RUL-217, 10 Oct 2026): Trainers are a door inside Tutors -- every trainer role is in the "
       "registry with its picture, its name in all 15 of Quick's languages and its How guide; Quick's Tutors door opens "
       "Sport & fitness -> group -> sport -> price -> where and writes Tutors / Trainers; prices are per session / month / "
       "package with no wage floor; the sports that commonly coach children carry the police-clearance gate",
       LOCKED, fixed_on="2026-10-10",
       scope="ROLE_SLATE_REVIEW.md '# TUTORS -- TRAINERS' -> scripts/build_role_registry.py -> roles/role_registry.json "
             "(service_class Trainers, trainers_door) -> scripts/sync_quick_roles.py QUICK-TRAINERS block + assets/quick_ph; "
             "quick.html (= genie/HARNESS.html) TRAINERS-DOOR-1; roles/quick_i18n.json; stories/<trainer>.json + gallery.json; "
             "bea_main.py _GATE_CATEGORIES / _TRUST_CAT_NORM / category.tutors.specialisation. All markets (global from day one).",
       ref="David 8 Oct 2026: 'I would like to do the same for tutors, but for a branch of tutors namely Trainers ... all of the "
           "sports types one can get a trainer for ... the same flows, Hows etc ... To also make it Global' / 'i agree for it to "
           "sit inside Tutors the same as we did for Services'.")
def rg_trainers_door_1():
    import json as _j
    reg_t = repo_file("roles/role_registry.json")
    if reg_t is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    bad = []
    reg = _j.loads(reg_t)
    trn = [r for r in reg.get("roles", []) if r.get("service_class") == "Trainers" and r.get("status") == "in"]
    if len(trn) < 45:
        bad.append("registry has %d trainer roles, expected 45+" % len(trn))
    door = reg.get("trainers_door") or {}
    if door.get("category") != "Tutors" or door.get("service_class") != "Trainers" or door.get("wage_floor") is not False:
        bad.append("registry trainers_door is not Tutors / Trainers with no wage floor")
    gated = {r["key"] for r in trn if (r.get("gate") or {}).get("type") == "police_clearance"}
    for k in ("soccer_coach", "swimming_coach", "gymnastics_coach", "chess_coach"):
        if k not in gated: bad.append("%s lost its clearance gate (RUL-217(d))" % k)
    if "personal_trainer" in gated: bad.append("personal_trainer gated -- adults' gym training carries no clearance gate")
    i18n_t = repo_file("roles/quick_i18n.json")
    w = (_j.loads(i18n_t).get("w") if i18n_t else {}) or {}
    for r in trn:
        k = r["key"]
        for f in ("roles/pictures/%s.png" % k, "assets/quick_ph/role_%s.jpg" % k, "stories/%s.json" % k):
            if not os.path.exists(os.path.join(REPO, f)): bad.append("missing %s" % f)
        row = w.get(r["label"]["en"]) or []
        if len([x for x in row if x]) < 15: bad.append("%s is not in all 15 Quick languages" % r["label"]["en"])
    gal = repo_file("stories/gallery.json") or ""
    miss = [r["key"] for r in trn if '"type": "%s"' % r["key"] not in gal]
    if miss: bad.append("How guides not in the gallery: " + ", ".join(miss[:4]))
    for k in sorted(gated)[:3]:
        st = repo_file("stories/%s.json" % k)
        if st and not any(s.get("gate") for s in _j.loads(st).get("steps", [])): bad.append("%s guide has no clearance step" % k)
    q = repo_file("quick.html") or ""
    for snip, why in (("var TRN_ROLES = ", "the QUICK-TRAINERS block is gone (run scripts/sync_quick_roles.py)"),
                      ("TRAINERS-DOOR-1 (RUL-217", "the Trainers door script is gone"),
                      ("return {category:'Tutors', service_class:'Trainers'}", "a trainer's advert no longer goes out as Tutors / Trainers"),
                      ("session:{t:'Per session',        u:' / session',  x:0}", "Per session lost (or gained a wage floor)"),
                      ("package:{t:'Per package',        u:' / package',  x:0}", "Per package lost (or gained a wage floor)"),
                      ("return {def:'session', opts:['session','month','package']}", "a trainer's rate screen is not per session / month / package"),
                      ("'/examples/trainers'", "Quick's Find no longer asks for the trainer example")):
        if snip not in q: bad.append(why)
    if q and q != (repo_file("genie/HARNESS.html") or ""): bad.append("quick.html and genie/HARNESS.html differ")
    py = repo_file("bea_main.py") or ""
    for snip, why in (('_GATE_CATEGORIES = ("services", "housekeeping", "homehelp", "tutors")', "the stranger gate no longer covers Tutors"),
                      ('"Tutors-Trainers": "Tutors"', "the Tutors-Trainers trust key no longer resolves to the Tutors set"),
                      ("Soccer → SAFA / CAF / UEFA coaching licence", "the per-sport coaching badges left category.tutors.specialisation")):
        if snip not in py: bad.append(why)
    if bad:
        return [(FAIL, "; ".join(bad[:8]))]
    return [(INFO, "%d trainer roles (%d clearance-gated) in registry, Quick, 15 languages and How guides" % (len(trn), len(gated)))]


@entry("RG-0948", "TRAINERS-EX-1 (RUL-217 / RUL-216 / RUL-194): every trainer role has a local AI example made on the server -- "
       "the sport's name in the asked language, 'Your session rate' on the card, the typical local session rate from its own "
       "per-country table (not the wage table) for the tap sheet -- in Quick's Find and TrustSquare's Tutors, and its sheet "
       "offers 'I train people in this -- list me free'",
       LOCKED, fixed_on="2026-10-10",
       scope="bea_main.py GET /examples/trainers + _TRN_SESSION_RATE; route_policy.json; ms.js msGenericExLoad / msGenericExSheet "
             "(TRAINERS-EX-1); quick.html Find (_gxT). Live: ZA and GB. All markets.",
       ref="RUL-217(b)/(c), David 8 Oct 2026; RUL-216 as amended 9 Oct (GX-RATE-WORDS-1: the card names no figure).")
def rg_trainers_ex_1():
    bad = _fb28_need([
        ("bea_main.py", [('@app.get("/examples/trainers")', "the trainer examples endpoint is gone"),
                         ("_TRN_SESSION_RATE = {", "the per-country session-rate table is gone"),
                         ('en_rate = "Your session rate"', "the trainer card shows a figure again (GX-RATE-WORDS-1)")]),
        ("route_policy.json", [('"GET /examples/trainers"', "the endpoint is not declared (SEC-GATE-1)")]),
        ("ms.js", [("TRAINERS-EX-1 (RUL-217", "TrustSquare no longer loads the trainer examples"),
                   ("'I train people in this — list me free'", "the trainer sheet lost its list-me-free door")]),
    ])
    if bad:
        return bad
    import json as _j
    t = _get("/examples/trainers?country=ZA&role=soccer_coach&lang=af")
    if not t:
        return [(INFO, "NOT EVALUATED (live half) - /examples/trainers unreadable (not deployed yet?)")]
    try:
        rows = _j.loads(t)
    except Exception:
        return [(FAIL, "live /examples/trainers is not JSON")]
    if len(rows) != 1 or rows[0].get("category") != "Tutors" or rows[0].get("service_class") != "Trainers":
        return [(FAIL, "live /examples/trainers did not return the one Tutors / Trainers soccer example")]
    r = rows[0]
    if not str(r.get("typical_rate") or "").startswith("R") or any(ch.isdigit() for ch in str(r.get("price") or "")):
        return [(FAIL, "live trainer example: card shows a figure or the sheet has no local rate (%r / %r)" % (r.get("price"), r.get("typical_rate")))]
    if not r.get("demo_example") or r.get("trust_score") is not None:
        return [(FAIL, "live trainer example is not marked as an AI example")]
    return [(INFO, "trainer examples live: '%s', '%s', typical %s" % (r.get("title"), r.get("price"), r.get("typical_rate")))]



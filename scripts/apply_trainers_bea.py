#!/usr/bin/env python3
"""apply_trainers_bea.py -- TRAINERS-DOOR-1 (RUL-217) on the server side (bea_main.py). Idempotent; refuses to apply twice.

  * GET /examples/trainers  -- one AI example per trainer role, made on request for the country/city/language being looked
    at (the GENERIC-EX-1 pattern of RUL-216): the sport's picture, its name in the asked language, 'Your session rate' in
    that language (GX-RATE-WORDS-1: the card names no figure), and the typical local session rate from a NEW per-country
    table (RUL-217(c): not the wage table) for the tap sheet. Nothing stored, nothing shipped in either app.
  * Trust Score: 'Tutors-Trainers' resolves to the Tutors evidence set everywhere a key is normalised; the
    category.tutors.specialisation 'how to earn' names per-sport coaching badges (RUL-217(d)).
  * The stranger gate covers Tutors too, so the trainer roles that commonly coach children carry the RUL-153 clearance
    gate (their names come from the role registry; a tutor advert without a clearance-role service_type is untouched).
"""
import io, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "bea_main.py")
MARK = "TRAINERS-EX-1"

ENDPOINT = r'''

# ── TRAINERS-EX-1 (RUL-217, David 8 Oct 2026) ───────────────────────────────────────────────────────────────────────
# "I would like to do the same for tutors, but for a branch of tutors namely Trainers ... To also make it Global." One AI
# example per trainer role, made ON REQUEST for the country, city and language being looked at -- the GENERIC-EX-1 pattern
# (RUL-216) for the Trainers door inside Tutors. Marked (RUL-040), last (RUL-194), hidden by the same switch, counted on the
# Home tile while the switch is on (GX-TILE-COUNT-1), kept off the map, never takes an introduction. The card names no
# figure ('Your session rate', GX-RATE-WORDS-1); the tap sheet may show what a session typically costs locally, from
# _TRN_SESSION_RATE below -- a NEW table, deliberately not the wage table (RUL-217(c): coaching is priced per session,
# per month or per package, and has no minimum-wage floor).
# _TRN_SESSION_RATE: a typical one-hour private session with a qualified coach, local currency. CLAUDE'S ESTIMATE from
# general market knowledge, 10 Oct 2026 -- not a survey; re-check yearly (as the wage table is). Countries Quick sells in.
_TRN_SESSION_RATE = {
    "ZA": ("R", 300), "NA": ("N$", 250), "BW": ("P", 200), "MZ": ("MT ", 1500), "KE": ("KSh ", 2000),
    "GB": ("£", 40), "DE": ("€", 45), "AU": ("A$", 80), "US": ("$", 70),
}
_TRN_SESSION_RATE_ASOF = "Claude estimate, 10 Oct 2026 (re-check yearly)"
_TRN_CACHE = {"roles": None}


def _trn_roles():
    if _TRN_CACHE["roles"] is None:
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "roles", "role_registry.json"), encoding="utf-8") as fh:
                _TRN_CACHE["roles"] = [r for r in json.load(fh).get("roles", [])
                                       if r.get("status") == "in" and r.get("service_class") == "Trainers"]
        except Exception as exc:
            _log.warning("TRAINERS-EX-1: role registry unreadable: %s", exc); _TRN_CACHE["roles"] = []
    return _TRN_CACHE["roles"]


def _trn_money(sym, n):
    return sym + "{:,}".format(int(n)).replace(",", " ")


@app.get("/examples/trainers")
def examples_trainers(country: str = "ZA", city: str = "", lang: str = "en", role: str = ""):
    """TRAINERS-EX-1 (RUL-217): AI example cards for the trainer roles, made for this country and city on request (nothing stored)."""
    cc = re.sub(r"[^A-Za-z]", "", country or "ZA")[:2].upper() or "ZA"
    if cc == "UK":
        cc = "GB"
    city = _plain_text(str(city or ""))[:60].strip()
    want = re.sub(r"[^a-z0-9_]", "", (role or "").lower())[:60]
    en_rate = "Your session rate"
    price = _gx_word(en_rate, lang) or en_rate
    rate = _TRN_SESSION_RATE.get(cc)
    typical = (_trn_money(rate[0], rate[1]) + " / session") if rate else None
    out = []
    for r in _trn_roles():
        k = r.get("key") or ""
        if want and k != want:
            continue
        label = _gx_label(r, lang)
        en = (r.get("label") or {}).get("en") or label
        pic = "/static/quick/role_%s.jpg" % k
        out.append({
            "id": "gx_" + k, "generic": True, "trainer": True, "role_key": k, "title": label, "category": "Tutors",
            "service_class": "Trainers", "service_type": en, "subject": en,
            "city": city or None, "suburb": None, "area": None, "country": cc, "price": price,
            "typical_rate": typical, "typical_rate_source": _TRN_SESSION_RATE_ASOF if rate else None,
            "description": "[photos:%s]\n%s%s." % (pic, label, (" — " + city) if city else ""),
            "thumb_url": pic, "medium_url": pic, "photo_urls": json.dumps([pic]), "trust_score": None,
            "is_demo": 1, "demo_example": True, "super_example": 0, "listing_status": "live",
        })
    return out
'''

SPEC_OLD = 'Accounting → SAIPA/CIMA; Sport → ASA/SAFA coaching badge."'
SPEC_NEW = ('Accounting → SAIPA/CIMA; Sport (TRAINERS-DOOR-1, RUL-217) → your sport\'s coaching badge from its national federation or the '
            'international body, e.g. Soccer → SAFA / CAF / UEFA coaching licence; Rugby → World Rugby coaching level; Cricket → '
            'national board coaching level; Swimming → swimming federation coach / learn-to-swim certificate; Tennis, squash, padel, '
            'badminton, table tennis → federation coach level (ITF for tennis); Golf → PGA professional; Athletics and running → '
            'World Athletics / national federation coach level; Gymnastics and acrobatics → federation coach level; Martial arts '
            '(judo, karate, taekwondo, jiu-jitsu, boxing, wrestling) → instructor certificate and dan or coach grade from your '
            'federation; Fitness, aerobics, functional fitness → registered personal-trainer or group-fitness certificate; Yoga → '
            '200-hour teacher training; Pilates → mat or reformer instructor certificate; Water sports → diving, surfing, sailing '
            'or paddling instructor certificate; Horse riding → riding-instructor qualification; Climbing, skiing, snowboarding → '
            'instructor certificate; Chess → FIDE trainer title (claimed, not uploaded)."')


def main():
    s = io.open(F, encoding="utf-8").read()
    if MARK in s:
        sys.exit("already applied (%s in bea_main.py)" % MARK)
    reps = [
        ('_GATE_CATEGORIES = ("services", "housekeeping", "homehelp")',
         '_GATE_CATEGORIES = ("services", "housekeeping", "homehelp", "tutors")   # TRAINERS-DOOR-1 (RUL-217(d)): trainer clearance roles'),
        (SPEC_OLD, SPEC_NEW),
        ('    "Tutors": "Tutors",\n    "Services": "Services-Technical",          # default subclass when none is given',
         '    "Tutors": "Tutors", "Tutors-Trainers": "Tutors",   # TRAINERS-DOOR-1 (RUL-217): the Trainers door scores on the Tutors set\n'
         '    "Services": "Services-Technical",          # default subclass when none is given'),
        ('"collectors": "Collectors", "cars": "Cars_private", "tutors": "Tutors",',
         '"collectors": "Collectors", "cars": "Cars_private", "tutors": "Tutors", "tutors-trainers": "Tutors", "trainers": "Tutors",'),
        ('            "Property": "Property", "Tutors": "Tutors",\n            "Services-Technical": "Services", "Services": "Services",',
         '            "Property": "Property", "Tutors": "Tutors", "Tutors-Trainers": "Tutors",\n            "Services-Technical": "Services", "Services": "Services",'),
        ('        "Tutors": "category.tutors.",\n        "Services-Technical": "category.services_tech.",',
         '        "Tutors": "category.tutors.", "Tutors-Trainers": "category.tutors.",\n        "Services-Technical": "category.services_tech.",'),
    ]
    for a, b in reps:
        n = s.count(a)
        if n != 1:
            sys.exit("anchor found %d times, expected 1: %r" % (n, a[:80]))
        s = s.replace(a, b)
    anchor = '\n\n@app.get("/geo/city-counts")'
    if s.count(anchor) != 1:
        sys.exit("endpoint anchor not found once")
    s = s.replace(anchor, ENDPOINT + anchor)
    shutil.copyfile(F, F + ".bak-trainers-%s" % time.strftime("%Y%m%d-%H%M%S"))
    io.open(F, "w", encoding="utf-8").write(s)
    print("bea_main.py: TRAINERS-EX-1 endpoint, Tutors-Trainers trust key, specialisation badges, tutors gate")


if __name__ == "__main__":
    main()

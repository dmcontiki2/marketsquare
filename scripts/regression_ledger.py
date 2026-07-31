#!/usr/bin/env python3
"""regression_ledger.py — TrustSquare "it must STAY fixed" ledger (v1, 25 Jul 2026).

WHY THIS EXISTS
---------------
audit_global_qa.py answers "is anything wrong right now?" with six generic sweeps.
It has no memory of what we already fixed, so a fault we fixed weeks ago can come
back and the audit still reports green. That is how the same fault got fixed three
times in one week: green audit, bug back, no alarm.

This file is the missing half — a ledger of specific, dated facts, each with an
executable assertion against the LIVE site. It survives chat sessions because it
is code on disk, not something a session has to remember.

TWO STATES — this is the important bit
--------------------------------------
  LOCKED  This was fixed. It must stay fixed. If the assertion fails the fix has
          ROTTED -> reported as REGRESSION and the run exits 1.

  OPEN    A known, defined, not-yet-fixed defect. The assertion is expected to
          fail; failing does not break the build. The moment it starts PASSING
          the ledger says "READY TO LOCK" -> change state to LOCKED and it can
          never silently come back.

That is the whole loop David asked for: find it, define it, fix the occurrence,
then lock it so it cannot un-fix itself between sessions.

THE RULE (also written into CLAUDE.md)
--------------------------------------
A fix is not "done" until it has an entry here. Fixing the occurrence is half the
job; adding the assertion is the other half.

SCOPE — the ZA-then-global trap
-------------------------------
Every entry declares scope. Most fixes must hold for ALL markets. Checks iterate
over every market the server actually serves rather than a hardcoded list, so a
newly added market shows up as unverified instead of shipping unchecked.

RUN
---
    python3 scripts/regression_ledger.py          # human report, exit 1 on regression
    python3 scripts/regression_ledger.py --json   # machine output

Stdlib only. Live checks need only network, so any session or machine can run it.
Repo checks run additionally when the script sits inside the repo; otherwise they
report SKIPPED rather than failing.
"""
import json, os, re, sys, time, datetime, urllib.request

BASE = os.environ.get("TS_BASE", "https://trustsquare.co").rstrip("/")
UA = {"User-Agent": "TrustSquare-RegressionLedger/1.0 (dmcontiki2@gmail.com)"}
TIMEOUT = 25

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIL, INFO = "FAIL", "INFO"
LOCKED, OPEN = "LOCKED", "OPEN"

_cache = {}


def _get(path):
    if path not in _cache:
        req = urllib.request.Request(BASE + path, headers=UA)
        _cache[path] = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
    return _cache[path]


def _json(path):
    return json.loads(_get(path))


def listings():
    return _json("/demo-listings")["listings"]


def repo_file(name):
    """Return repo file text, or None when running outside the repo."""
    p = os.path.join(REPO, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ── market model ────────────────────────────────────────────────────────────
# Cities the demo feed ships, and the symbol a buyer must see there.
CITY_CCY = {
    "pretoria": "R", "johannesburg": "R", "cape town": "R", "durban": "R",
    "centurion": "R", "midrand": "R", "sandton": "R",
    "new york": "$", "london": "£", "sydney": "A$",
    "maun": "P",   # Botswana Pula — Okavango super market demo_stay_bw_1 (added 29 Jul 2026)
}
CITY_COUNTRY = {
    "pretoria": "ZA", "johannesburg": "ZA", "cape town": "ZA", "durban": "ZA",
    "centurion": "ZA", "midrand": "ZA", "sandton": "ZA",
    "new york": "US", "london": "GB", "sydney": "AU",
    "maun": "BW",   # Maun is in Botswana (added 29 Jul 2026)
}
SYMBOLS = ("A$", "CA$", "NZ$", "N$", "MT", "R", "$", "£", "€")


def symbol_of(price):
    p = str(price).strip()
    for s in sorted(SYMBOLS, key=len, reverse=True):
        if p.startswith(s):
            return s
    return None


def is_adventures(l):
    return str(l.get("cat", "")).lower().startswith("adventures")


def is_placeholder(l):
    return str(l.get("id", "")).startswith("ph_")


LEDGER = []


def entry(rid, title, state, scope, fixed_on="", ref=""):
    def deco(fn):
        LEDGER.append({"id": rid, "title": title, "state": state, "scope": scope,
                       "fixed_on": fixed_on, "ref": ref, "fn": fn})
        return fn
    return deco


# ════════════════════════════════════════════════════════════════════════════
#  LEDGER — append below. Never renumber. Never delete a LOCKED entry.
#  Promote OPEN -> LOCKED the moment the ledger reports READY TO LOCK.
# ════════════════════════════════════════════════════════════════════════════

@entry("RG-0001", "Adventures listings carry their own country (not a silent ZA fallback)",
       LOCKED, scope="ALL markets", fixed_on="2026-07-24",
       ref="_priceLabel() resolves ADV_COUNTRY_CURRENCY[l.country||'ZA']. A listing with "
           "no country silently renders in Rand — the failure is invisible in ZA and only "
           "shows up on global checks, which is exactly how this class kept coming back.")
def rg_adv_country_present():
    out = []
    for l in listings():
        if not is_adventures(l) or is_placeholder(l):
            continue
        if not str(l.get("country", "")).strip():
            out.append((FAIL, f"{l.get('id')} ({l.get('city')}) has no country — would render as Rand"))
    return out


@entry("RG-0002", "Buyers see the right currency symbol for the market they are looking at",
       LOCKED, scope="ALL markets, ALL categories", fixed_on="2026-07-24",
       ref="Two price representations coexist: Adventures store a bare number + country, "
           "everything else stores a pre-formatted string whose symbol IS the currency. "
           "Both paths must land on the same answer for a given city.")
def rg_rendered_symbol_matches_market():
    ADV = {"ZA": "R", "NA": "N$", "MZ": "MT", "BW": "P", "US": "$", "CA": "CA$",
           "GB": "£", "EU": "€", "AU": "A$", "NZ": "NZ$"}
    out = []
    for l in listings():
        if is_placeholder(l):
            continue
        price = l.get("price")
        if price in (None, "", "null"):
            continue
        city = str(l.get("city", "")).strip().lower()
        want = CITY_CCY.get(city)
        if want is None:
            out.append((FAIL, f"city {city!r} has no currency rule ({l.get('id')}) — market UNVERIFIED"))
            continue
        if is_adventures(l):
            country = str(l.get("country") or "ZA").upper()
            # A listing whose country contradicts its city is RG-0004's defect, not this
            # one. Reporting it here too would make this guard cry wolf about a fault it
            # does not own — one defect, one owner.
            if country != CITY_COUNTRY.get(city, country):
                continue
            got = ADV.get(country, "R")
        else:
            got = symbol_of(price) or "R"   # formatZAR() defaults anything unprefixed to Rand
        if got != want:
            out.append((FAIL, f"{l.get('id')} in {l.get('city')} renders {got!r}, market expects {want!r} "
                              f"(price={price!r}, country={l.get('country')!r})"))
    return out


@entry("RG-0003", "Non-Adventures listings have NO country field — currency is guessed from the price string",
       OPEN, scope="Cars, Collectors, Property, Services, Tutors, local_market",
       ref="THE STRUCTURAL CAUSE of the recurring currency faults. Adventures got a proper "
           "country->currency model; the other six categories never did. They rely on the "
           "price string already carrying a symbol, and formatZAR() turns anything unprefixed "
           "into Rand. It looks correct today only because every non-ZA demo listing happens "
           "to ship a pre-formatted symbol string. The first non-ZA seller who types a bare "
           "number gets Rand. Fixing this class ONCE retires the whole recurring family.")
def rg_non_adv_country_model():
    out = []
    missing = [l for l in listings()
               if not is_adventures(l) and not is_placeholder(l)
               and not str(l.get("country", "")).strip()]
    if missing:
        cats = sorted({str(l.get("cat")) for l in missing})
        out.append((FAIL, f"{len(missing)} non-Adventures listings carry no country field "
                          f"(categories: {', '.join(cats)}) — currency inferred from the price string, "
                          f"defaulting to Rand"))
    return out


@entry("RG-0004", "A listing's city and its country agree",
       OPEN, scope="ALL markets",
       ref="Found 25 Jul: two Pretoria listings resolve to non-ZA countries, so the card shows "
           "a Pretoria address priced in another currency. Either the city or the country is wrong.")
def rg_city_country_agree():
    out = []
    for l in listings():
        if is_placeholder(l):
            continue
        c = str(l.get("country", "")).strip().upper()
        if not c:
            continue
        city = str(l.get("city", "")).strip().lower()
        want = CITY_COUNTRY.get(city)
        if want and c != want:
            out.append((FAIL, f"{l.get('id')} city={l.get('city')!r} but country={c!r} "
                              f"(price renders in the {c} currency on a {want} card)"))
    return out


@entry("RG-0005", "Every market the server serves has a currency rule on both sides",
       LOCKED, scope="ALL markets", fixed_on="2026-07-25",
       ref="Guards the ZA-then-global trap directly: adding a market without extending the "
           "currency tables fires here on the next run instead of reaching a user.")
def rg_market_coverage():
    out = []
    try:
        countries = _json("/geo/countries")
    except Exception as e:
        return [(FAIL, f"/geo/countries unreadable — market coverage unverified: {e}")]
    iso = [str(c.get("iso2", "")).upper() for c in countries] if isinstance(countries, list) else []
    fe = repo_file("ms.js")
    if fe is not None:
        m = re.search(r"ADV_COUNTRY_CURRENCY\s*=\s*\{([^}]*)\}", fe)
        table = set(re.findall(r"([A-Z]{2})\s*:", m.group(1))) if m else set()
        if not table:
            out.append((FAIL, "ADV_COUNTRY_CURRENCY not found in ms.js — currency table missing"))
        else:
            gap = sorted(set(iso) - table)
            if gap:
                out.append((FAIL, f"server serves {gap} but the frontend currency table has no entry for them"))
    else:
        out.append((INFO, "ms.js not present (running outside the repo) — frontend table check skipped"))
    cities = {str(l.get("city", "")).strip().lower() for l in listings() if str(l.get("city", "")).strip()}
    unmapped = sorted(c for c in cities if c not in CITY_CCY)
    if unmapped:
        out.append((FAIL, f"live cities with no currency rule in this ledger: {unmapped}"))
    out.append((INFO, f"server markets: {', '.join(iso) if iso else 'unknown'}"))
    return out


@entry("RG-0006", "Seller price prompts are not hardcoded to Rand",
       LOCKED, scope="ALL markets, seller flow", fixed_on="2026-07-31",
       ref="Every category config in ms.js labelled the price field '(R)' — 'Asking price (R)', "
           "'Hourly rate (R)', 'Nightly rate (R)', 'Price per person (R)'. A London or New York "
           "seller was asked for Rand — the RG-0003 ZA assumption on the input side. Fixed "
           "31 Jul 2026 (ms.js v412): all 9 config labels and the two PRICE-LABEL-1 Property "
           "literals de-Randed; the render site appends the symbol from _sfCcySym(), which reads "
           "the seller/market country through ADV_COUNTRY_CURRENCY — the same table the buyer "
           "display uses, so both sides of a market agree by construction. Check strengthened at "
           "promotion (never weakened): also catches inline _pl='… (R)' literals and the removal "
           "of the helper itself.")
def rg_seller_labels_not_rand():
    fe = repo_file("ms.js")
    if fe is None:
        return [(INFO, "ms.js not present (running outside the repo) — check skipped")]
    hits = re.findall(r"priceLabel\s*:\s*'([^']*\(R\)[^']*)'", fe)
    hits += re.findall(r"_pl\s*=\s*'([^']*\(R\)[^']*)'", fe)
    out = []
    if hits:
        uniq = sorted(set(hits))
        out.append((FAIL, f"{len(hits)} seller price prompts hardcode Rand, e.g. {uniq[:4]}"))
    if "_sfCcySym" not in fe:
        out.append((FAIL, "_sfCcySym() is gone from ms.js — the seller-flow prompt has lost its "
                          "market-currency source and has likely reverted to hardcoded Rand"))
    return out


@entry("RG-0007", "Placeholder listings stay unpriced and inert",
       LOCKED, scope="ALL categories", fixed_on="2026-07-25",
       ref="ph_* cards are deliberate 'coming soon' tiles; they must never gain a price or "
           "start looking like real stock.")
def rg_placeholders_inert():
    return [(FAIL, f"placeholder {l.get('id')} has acquired a price: {l.get('price')!r}")
            for l in listings()
            if is_placeholder(l) and l.get("price") not in (None, "", "null")]


@entry("RG-0008", "Every listing resolves to a seller of the same category",
       LOCKED, scope="ALL categories", fixed_on="2026-07-25",
       ref="DEMO-CROSSWIRE / DEMO-LISTER-MISSING / DEMO-SELLER-SCHEMA recurred repeatedly "
           "through the audit history; locked so a re-wire cannot pass silently.")
def rg_seller_wiring():
    out = []
    try:
        sellers = _json("/demo-sellers")["sellers"]
    except Exception as e:
        return [(FAIL, f"/demo-sellers unreadable — wiring unverified: {e}")]
    by_idx = {s["idx"]: s for s in sellers if "idx" in s}
    no_idx = sum(1 for s in sellers if "idx" not in s)
    if no_idx:
        out.append((FAIL, f"{no_idx}/{len(sellers)} sellers have no idx field — position lookups mis-resolve"))
    for l in listings():
        si = l.get("sellerIdx")
        if si is None:
            continue
        s = by_idx.get(si)
        if s is None:
            out.append((FAIL, f"listing {l.get('id')} points at sellerIdx {si}, which does not exist"))
            continue
        lc = str(l.get("cat") or "").lower().replace("_", "")
        sc = str(s.get("cat") or "").lower().replace("_", "")
        lc = "adventures" if lc.startswith("adventures") else lc
        sc = "adventures" if sc.startswith("adventures") else sc
        if lc and sc and lc != sc:
            out.append((FAIL, f"listing {l.get('id')} cat={lc} wired to seller idx {si} cat={sc}"))
    return out


@entry("RG-0009", "Every listing a buyer can see has a title",
       LOCKED, scope="ALL categories", fixed_on="2026-07-25",
       ref="DEMO-MISSING-TITLE class — a card with no title is a dead end on the grid.")
def rg_titles():
    return [(FAIL, f"listing {l.get('id')} has no title")
            for l in listings()
            if not is_placeholder(l) and not str(l.get("title", "")).strip()]


@entry("RG-0010", "Service is up and reports a version",
       LOCKED, scope="live server", fixed_on="2026-07-25",
       ref="Cheapest canary; also proves this ledger reached the real site rather than "
           "passing because everything was unreachable.")
def rg_health():
    h = _json("/health")
    out = []
    if h.get("status") != "ok":
        out.append((FAIL, f"/health status is {h.get('status')!r}, expected 'ok'"))
    if not str(h.get("version", "")).strip():
        out.append((FAIL, "/health reports no version"))
    else:
        out.append((INFO, f"live {h.get('service')} v{h.get('version')}"))
    return out


@entry("RG-0011", "Country codes are ISO 3166-1 and map filenames match their code",
       LOCKED, scope="ALL markets", fixed_on="2026-07-29",
       ref="MAP_NAMING_CANON.md. Found 26 Jul: GB points at adventures_uk_map.html and ZA at "
           "adventures_reserve_map.html, and ADV_COUNTRY_FLAGS carries EU and LL which are not "
           "countries (LL is in flags but not currency). Every lookup keyed on listing.country "
           "has to special-case these, which is how per-country bugs get born.")
def rg_iso_codes_and_filenames():
    import re
    fe = repo_file("ms.js")
    if fe is None:
        return [(INFO, "ms.js not present (running outside the repo) — check skipped")]
    out = []
    ISO = {"ZA","US","GB","AU","DE","NA","BW","MZ","NZ","CA","ZW","TZ","SD","EG","KE","BR","AR"}
    # Deliberate non-country sentinels, allowed by canon §3 because they are declared:
    #   ALL = every market (filter sentinel), EU = euro-zone pricing fallback.
    SENTINELS = {"ALL", "EU"}
    for table in ("ADV_COUNTRY_FLAGS", "ADV_COUNTRY_CURRENCY"):
        m = re.search(table + r"\s*=\s*\{([^}]*)\}", fe)
        if not m:
            out.append((FAIL, f"{table} not found in ms.js")); continue
        for k in re.findall(r"(?:^|[{,])\s*([A-Z]{2,3}):", m.group(1)):
            if k not in ISO and k not in SENTINELS:
                out.append((FAIL, f"{table} contains {k!r}, which is not an ISO 3166-1 country code"))
    for key, slug in re.findall(r"^\s*(?://\s*)?([A-Z]{2}): \{ file:'adventures_([a-z0-9]+)_map\.html'", fe, re.M):
        if slug != key.lower():
            out.append((FAIL, f"map key {key} points at adventures_{slug}_map.html "
                              f"(canon: adventures_{key.lower()}_map.html)"))
    return out


@entry("RG-0012", "Per-tour maps stay wired: tour listings live, map follows the tour not the operator's country",
       LOCKED, scope="tour super listings (Cape-to-Cairo, Namibia)", fixed_on="2026-07-26",
       ref="Added 26 Jul. Two coupled facts must hold together or a tour map silently vanishes. "
           "(1) A multi-country tour is DECOUPLED: the listing sits under its operator's country "
           "(Cape-to-Cairo lists under a SA/Rand operator) but its map follows the ROUTE via a new "
           "ADV_TOUR_MAP keyed on listing.tour, consulted BEFORE ADV_COUNTRY_MAP. Lose that "
           "precedence and Cape-to-Cairo would show a South-Africa map. (2) A country map (Namibia) "
           "only surfaces once its country is un-gated AND real super listings exist to carry it — "
           "the exact gap that made 'I deployed but see no tours' true on 26 Jul: maps were live but "
           "no listing carried them. OPEN until the next deploy creates the tour/NA super listings; "
           "the moment this reports READY TO LOCK, promote to LOCKED so the wiring cannot rot back.")
def rg_tour_maps_wired():
    out = []
    # ── repo side: the wiring that makes tour maps resolve at all ──
    fe = repo_file("ms.js")
    if fe is None:
        out.append((INFO, "ms.js not present (running outside the repo) — repo checks skipped"))
    else:
        m = re.search(r"ADV_TOUR_MAP\s*=\s*\{([^}]*)\}", fe, re.S)
        if not m:
            out.append((FAIL, "ADV_TOUR_MAP not defined in ms.js — per-tour maps cannot resolve"))
        elif "adventures_c2c_map.html" not in m.group(1):
            out.append((FAIL, "ADV_TOUR_MAP has no c2c -> adventures_c2c_map.html entry"))
        if "ADV_TOUR_MAP[l.tour]" not in fe:
            out.append((FAIL, "map picker never consults ADV_TOUR_MAP[l.tour] — tour no longer beats country (decouple lost)"))
        # NA map filename legitimately carries a ?v= cache-buster (fleet-wide bump 27 Jul); tolerate it
        if not re.search(r"^\s*NA:\s*\{\s*file:'adventures_na_map\.html(?:\?v=\d+)?'", fe, re.M):
            out.append((FAIL, "NA is not un-gated in ADV_COUNTRY_MAP (still commented, or missing)"))
        if "ADV_TOUR_MAP[l.tour]" in fe and not re.search(r"\btour:\s*\(?\s*l\.tour", fe):
            out.append((FAIL, "ms.js reads l.tour in the map render but NO normalizer assigns tour from the API row "
                              "-- l.tour is always undefined, so every tour silently falls back to the country/reserve map "
                              "(same class as the 25-Jul country-survival bug)"))
    # ── live side: the SUPER example listings the tour maps actually hang off ──
    # Corrected 29 Jul 2026: the tour maps render only on (l.super_example && isAdv), and the super
    # exemplars live in /listings (the real feed, keyed on `category`), NOT /demo-listings (which
    # carries no supers). The old check read /demo-listings and keyed on is_adventures()'s `cat`,
    # so it could never see the live c2c/NA supers — the guard was looking in the wrong feed, not a
    # product regression. Invariant unchanged: a live c2c super and a live NA super must both exist.
    def _adv(l):
        return str(l.get("cat") or l.get("category") or "").lower().startswith("adventures")
    try:
        real = _json("/listings?limit=500")
        real = real.get("listings") if isinstance(real, dict) else real
    except Exception as ex:
        real = []
        out.append((FAIL, f"/listings unreadable — super-listing coverage unverified: {ex!r}"))
    supers = [l for l in real if l.get("super_example") and _adv(l)]
    c2c = [l for l in supers if str(l.get("tour", "")).strip().lower() == "c2c"]
    if not c2c:
        out.append((FAIL, "no live super listing carries tour='c2c' — Cape-to-Cairo map has nothing to surface on"))
    else:
        stray = [l.get("id") for l in c2c if str(l.get("country", "")).upper() not in ("ZA", "")]
        if stray:
            out.append((FAIL, f"c2c supers not under the SA operator: {stray} (decouple expects country=ZA/Rand)"))
    if not [l for l in supers if str(l.get("country", "")).upper() == "NA"]:
        out.append((FAIL, "no live NA super listing — the Namibia map has nothing to surface on"))
    for f in ("adventures_c2c_map.html", "adventures_na_map.html"):
        try:
            if len(_get("/static/" + f)) < 500:
                out.append((FAIL, f"/static/{f} is present but suspiciously small — likely not the real map"))
        except Exception as ex:
            out.append((FAIL, f"/static/{f} unreachable: {ex!r}"))
    # the JS a browser actually receives (at the version the live index points to) must
    # carry the tour render — catches 'new code on the server, old build still served/cached'.
    try:
        mv = re.search(r"ms\.js\?v=(\d+)", _get("/"))
        js = _get("/static/ms.js" + ("?v=" + mv.group(1) if mv else ""))
        if "ADV_TOUR_MAP[l.tour]" not in js:
            out.append((FAIL, "live-served ms.js (at the version the index references) has no ADV_TOUR_MAP[l.tour] render — browsers get a build without tour maps"))
    except Exception as ex:
        out.append((FAIL, f"could not verify the live-served ms.js build: {ex!r}"))
    return out


@entry("RG-0013", "Every deploy path that uploads ms.js also bumps the ?v= cache-buster",
       LOCKED, scope="repo, all deploy scripts", fixed_on="2026-07-26",
       ref="THE ROOT of the recurring 'map fix never held' class. The cache-buster bump was made "
           "'permanent' in July but only inside deploy_marketsquare.bat; deploy_frontend_only.bat was "
           "a separate quick-deploy path that uploaded ms.js and NEVER bumped ?v=. nginx serves each "
           "?v= URL as immutable, so a fix shipped through the quick script landed on the server under "
           "a version key every browser had already cached forever -- delivered to nobody, for weeks. "
           "This asserts the INVARIANT rather than the instance: any deploy script that scp's ms.js must "
           "also increment ms.js?v=. A newly-added unprotected deploy path trips this red instead of "
           "silently reintroducing the whole class.")
def rg_all_deploy_paths_bump():
    import glob
    if repo_file("ms.js") is None:
        return [(INFO, "running outside the repo -- deploy-script check skipped")]
    out = []
    scripts = sorted(glob.glob(os.path.join(REPO, "deploy*.bat")))
    checked = 0
    for path in scripts:
        if os.path.basename(path).endswith((".bak", ".bak.bat")) or ".bak-" in os.path.basename(path):
            continue
        try:
            t = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if not re.search(r"scp\b[^\n]*ms\.js", t):   # this script does not ship ms.js
            continue
        checked += 1
        # a script bumps the cache-buster via EITHER the PowerShell inline expr OR scripts/autobump.py (broadened 29 Jul 2026)
        if not re.search(r"(?:'ms\.js\?v='\s*\+\s*\(\s*\[int\])|autobump", t):
            out.append((FAIL, os.path.basename(path) + " uploads ms.js but never bumps ms.js?v= "
                              "-- its deploys ship an invisible, browser-cached-stale asset"))
    out.append((INFO, str(checked) + " deploy script(s) ship ms.js; every one must bump the cache-buster"))
    return out


@entry("RG-0014", "Adventures-screen cards show the red ★ SUPER ADVERT ribbon",
       LOCKED, scope="Adventures dedicated screen, ALL markets (one shared renderer)", fixed_on="2026-07-30",
       ref="Added 29 Jul 2026. Fixed TWICE before yet the Adventures tab stayed bare: SUPER-1 "
           "(Session 144) put the ribbon on the shared browse lcard renderer + the detail pill, "
           "and the 22-Jul LM pass put it on Local Market cards — but the Adventures tab renders "
           "through its OWN renderAdvGrid() inline template, which never read l.super_example. "
           "Both earlier fixes were correct for the renderers they touched and invisible on the "
           "Adventures screen; verification passed because it checked browse/LM/detail, not this "
           "tab. Third pass (29 Jul) patched renderAdvGrid() itself. OPEN until the next frontend "
           "deploy ships ms.js v409; the moment this reports READY TO LOCK, promote to LOCKED. "
           "Live side checks the build browsers actually receive at the ?v= the live index "
           "references (RG-0013 class), so a cache-stale deploy cannot fake a pass.")
def rg_adv_screen_super_ribbon():
    out = []

    def _adv_slice(js):
        i = js.find("function renderAdvGrid(")
        if i < 0:
            return None
        j = js.find("function renderActiveFilterTags(", i)
        return js[i:(j if j > i else i + 20000)]

    fe = repo_file("ms.js")
    if fe is None:
        out.append((INFO, "ms.js not present (running outside the repo) — repo check skipped"))
    else:
        seg = _adv_slice(fe)
        if seg is None:
            out.append((FAIL, "renderAdvGrid() not found in repo ms.js — Adventures renderer missing or renamed"))
        elif "super_example" not in seg:
            out.append((FAIL, "repo renderAdvGrid() card template has no super_example ribbon — Adventures cards ship bare"))
    try:
        mv = re.search(r"ms\.js\?v=(\d+)", _get("/"))
        js = _get("/static/ms.js" + ("?v=" + mv.group(1) if mv else ""))
        seg = _adv_slice(js)
        if seg is None:
            out.append((FAIL, "renderAdvGrid() not found in live-served ms.js"))
        elif "super_example" not in seg:
            out.append((FAIL, "live-served renderAdvGrid() (at the ?v= the live index references) has no "
                              "super_example ribbon — browsers get bare Adventures cards"))
    except Exception as ex:
        out.append((FAIL, f"could not verify the live-served ms.js build: {ex!r}"))
    return out


# ════════════════════════════════════════════════════════════════════════════


@entry("RG-0015", "Every git-writing .bat clears a stale .git/index.lock before committing",
       LOCKED, scope="repo, all commit/checkpoint/deploy scripts", fixed_on="2026-07-30",
       ref="THE ROOT of the recurring 'Unable to create .git/index.lock: File exists' class. Several "
           "uncoordinated git writers share ONE repo -- manual commit.bat, the nightly checkpoint task, "
           "the deploy auto-commit, and the daily-loop sandbox. When two overlap or one is interrupted git "
           "leaves a 0-byte index.lock; on the FUSE-mounted sandbox it cannot be removed at all, so it sits "
           "there and blocks the NEXT commit. deploy_marketsquare.bat got an inline stale-lock sweep on "
           "22 Jul 2026, but the manual + checkpoint committers never did -- so David's manual commits kept "
           "failing with the same error, session after session. Fix (30 Jul): git_unlock.bat removes a stale "
           "lock ONLY when no git.exe is running (so it can never race a live commit) and every committer "
           "calls it first. This asserts the INVARIANT: any .bat that git-commits must first clear a stale "
           "lock (call git_unlock.bat OR an inline del of .git/index.lock). A new unguarded committer trips "
           "this red instead of silently reintroducing the whole class.")
def rg_git_writers_selfheal_lock():
    import glob
    if repo_file("commit.bat") is None:
        return [(INFO, "running outside the repo -- commit-script lock check skipped")]
    out = []
    if repo_file("git_unlock.bat") is None:
        out.append((FAIL, "git_unlock.bat missing -- the shared stale-lock clearer every committer calls"))
    checked = 0
    for path in sorted(glob.glob(os.path.join(REPO, "*.bat"))):
        base = os.path.basename(path)
        if ".bak" in base:
            continue
        try:
            t = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        is_writer = re.search(r"\bgit\s+commit\b", t) and re.search(r"\bgit\s+(add|rm)\b", t)
        if not is_writer:
            continue
        checked += 1
        guarded = ("git_unlock.bat" in t) or re.search(r"del\b.*index\.lock", t, re.I)
        if not guarded:
            out.append((FAIL, base + " commits but never clears a stale .git/index.lock first "
                              "-- a leftover lock will block the next commit (recurring index.lock class)"))
    out.append((INFO, str(checked) + " git-writing .bat(s); each must self-heal a stale index.lock"))
    return out


@entry("RG-0016", "The seam's OpenAI lane carries current-generation model ids, never stale ones",
       LOCKED, scope="repo, ai_provider.py openai TASK_MODEL row (all task tiers)", fixed_on="2026-07-31",
       ref="The openai row shipped 17 Jul 2026 with 2024-era ids (gpt-4o-mini/gpt-4o) and a VERIFY-later "
           "comment — an activation or any-of fallback onto OpenAI would have requested retired models "
           "and failed at the worst moment (mid-outage). Fixed 31 Jul 2026: row updated to the GPT-5.6 "
           "family (luna on haiku/vision/triage, terra on sonnet; ids verified against "
           "developers.openai.com/api/docs/models), and _openai hardened in the same pass — "
           "max_completion_tokens for gpt-5*/o* (chat/completions 400-rejects max_tokens there), "
           "envkey() lookup (ENVKEY-1 class), FAILOVER-PARITY-1 ok-rule. This asserts the row never "
           "rots back to a retired generation. Golden-set gate before production traffic UNCHANGED, "
           "pending OPENAI_API_KEY (David-only).")
def rg_openai_row_not_stale():
    src = repo_file("ai_provider.py")
    if src is None:
        return [(INFO, "running outside the repo -- ai_provider.py row check skipped")]
    m = re.search(r'"openai"\s*:\s*\{(.*?)\}', src, re.S)
    if not m:
        return [(FAIL, "ai_provider.py no longer has an openai TASK_MODEL row")]
    row = m.group(1)
    stale = sorted({t for t in ("gpt-4o", "gpt-4-", "gpt-3.5") if t in row})
    out = []
    if stale:
        out.append((FAIL, f"openai TASK_MODEL row carries retired-generation ids again: {stale}"))
    if "gpt-5" not in row:
        out.append((FAIL, "openai TASK_MODEL row names no gpt-5-generation model -- if the catalog "
                          "moved on, update the row AND this assertion deliberately (never weaken silently)"))
    return out


@entry("RG-0017", "Every BEA AI call goes through the ai_provider seam — no raw vendor endpoints",
       LOCKED, scope="repo, bea_main.py (all 22 AI call sites, all providers)", fixed_on="2026-07-31",
       ref="P0 (17 Jul 2026) migrated 21 of 22 call sites to ai_provider.complete(); the last one "
           "(vision-draft) kept a raw httpx POST with Anthropic wire format, first guarded by an "
           "Anthropic-pin (31 Jul) and then migrated the same day, completing P0 at 22/22. The "
           "provider swap is only real if it stays total: ONE raw vendor URL in bea_main.py makes "
           "the dashboard switch a lie for that feature (the 7-of-22 'decorative switch' class from "
           "AI_SWAP_ARCHITECTURE §0). Asserts bea_main.py names no vendor inference endpoint and "
           "still imports the seam; the wire protocol lives in ai_provider.py adapters only.")
def rg_no_raw_vendor_endpoints():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- bea_main.py seam check skipped")]
    out = []
    for host in ("api.anthropic.com", "api.openai.com", "api.scaleway.ai"):
        n = src.count(host)
        if n:
            out.append((FAIL, f"bea_main.py names {host} {n}x — a raw vendor call path is back; "
                              "route it through ai_provider.complete() instead"))
    if "import ai_provider" not in src:
        out.append((FAIL, "bea_main.py no longer imports ai_provider — the seam is unwired"))
    return out


def run():
    t0 = time.time()
    results = []
    for e in LEDGER:
        try:
            out = e["fn"]() or []
        except Exception as ex:
            out = [(FAIL, f"check crashed (ledger fault, not necessarily the app): {ex!r}")]
        fails = [m for s, m in out if s == FAIL]
        infos = [m for s, m in out if s == INFO]
        if e["state"] == LOCKED:
            status = "REGRESSION" if fails else "HOLDING"
        else:
            # LEDGER-FAULT-1 (31 Jul 2026): outside the repo a repo-only OPEN check skips, produced
            # zero fails, and falsely reported READY TO LOCK (RG-0006 was nearly promoted while ms.js
            # still carried 9 Rand price labels). A skip is "unverified here", never "now passing".
            skipped = (not fails) and any(s == INFO and "skip" in m.lower() for s, m in out)
            status = "OPEN" if (fails or skipped) else "READY TO LOCK"
        results.append({**{k: v for k, v in e.items() if k != "fn"},
                        "status": status, "fails": fails, "infos": infos})
    return results, round(time.time() - t0, 1)


def main():
    results, took = run()
    n = lambda s: sum(1 for r in results if r["status"] == s)
    regressed, holding, open_, ready = n("REGRESSION"), n("HOLDING"), n("OPEN"), n("READY TO LOCK")

    if "--json" in sys.argv:
        print(json.dumps({"date": datetime.date.today().isoformat(), "took_s": took,
                          "regressed": regressed, "holding": holding,
                          "open": open_, "ready_to_lock": ready,
                          "entries": results}, indent=1))
        return 1 if regressed else 0

    print(f"# Regression ledger — {datetime.date.today().isoformat()}  ({took}s · {BASE})")
    print()
    print(f"{len(results)} entries · {holding} holding · {regressed} REGRESSED · "
          f"{open_} open · {ready} ready to lock")
    print()
    mark = {"HOLDING": "  ok  ", "REGRESSION": " !!!! ", "OPEN": " open ", "READY TO LOCK": " LOCK "}
    for r in results:
        print(f"[{mark[r['status']]}] {r['id']}  {r['title']}")
        meta = f"scope: {r['scope']}"
        if r["fixed_on"]:
            meta = f"fixed {r['fixed_on']} · " + meta
        print(f"           {meta}")
        for m in r["fails"]:
            tag = "REGRESSION" if r["state"] == LOCKED else "open"
            print(f"           {tag}: {m}")
        for m in r["infos"]:
            print(f"           info: {m}")
        if r["status"] == "READY TO LOCK":
            print(f"           >>> now passing — change state to LOCKED so it cannot come back")
    print()
    if regressed:
        print(f"RESULT: {regressed} previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.")
    elif ready:
        print(f"RESULT: no regressions. {ready} open item(s) now pass — promote them to LOCKED.")
    else:
        print(f"RESULT: every locked fix is holding. {open_} known defect(s) still open.")
    return 1 if regressed else 0


if __name__ == "__main__":
    sys.exit(main())

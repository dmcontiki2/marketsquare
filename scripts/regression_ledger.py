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


@entry("RG-0018", "AI price truth is LIVE: the price card is fresh and covers every wired model",
       LOCKED, scope="repo, ai_price_card.json vs ai_provider.py TASK_MODEL", fixed_on="2026-07-31",
       ref="Live-Values Doctrine (David, 31 Jul 2026 — vendor doc Addendum 7). Root incident: the "
           "18 Jul 'Mistral Medium ~40% of Haiku' claim drove the designated-swap-out decision, but "
           "the Peer's 31 Jul cost review showed the live Scaleway page at ~1.65x Haiku — a July "
           "decision was standing on a stale (or wrong-model) June price. Cure: ai_price_card.json "
           "is the ONLY legal source of AI prices; every entry carries source + verified_at; this "
           "check goes RED when the card is missing, unparseable, older than 45 days, or missing "
           "any model wired in TASK_MODEL. scripts/price_truth.py renders the card as a cost-and-"
           "capability value ranking; switching stays governed by Addendum 3.")
def rg_price_card_live():
    card_txt = repo_file("ai_price_card.json")
    seam = repo_file("ai_provider.py")
    if card_txt is None or seam is None:
        if seam is not None and card_txt is None:
            return [(FAIL, "ai_price_card.json is MISSING from the repo -- the Live-Values "
                           "Doctrine requires it (see Addendum 7)")]
        return [(INFO, "running outside the repo -- price-card check skipped")]
    try:
        card = json.loads(card_txt)
        age = (datetime.date.today() - datetime.date.fromisoformat(card["verified_at"])).days
    except Exception as ex:
        return [(FAIL, f"ai_price_card.json unreadable ({ex!r}) -- an unparseable card is a stale card")]
    out = []
    if age > 45:
        out.append((FAIL, f"price card verified {card['verified_at']} -- {age} days old (max 45). "
                          "Re-verify against live vendor pages/console and bump verified_at; "
                          "decisions must not run on remembered prices"))
    priced = {m for p in card.get("providers", {}).values() for m in p.get("models", {})}
    wired = set()
    for prov in ("anthropic", "openai", "scaleway"):
        m = re.search('"%s"\\s*:\\s*\\{(.*?)\\}' % prov, seam, re.S)
        if m:
            wired |= {v for _, v in re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', m.group(1))}
    for missing in sorted(wired - priced):
        out.append((FAIL, f"wired model {missing!r} has no price-card entry -- it can be routed "
                          "to but not costed, so any cost decision about it runs on memory"))
    out.append((INFO, f"card {card.get('version','?')} verified {card.get('verified_at','?')} "
                      f"({age}d) -- {len(priced)} priced / {len(wired)} wired"))
    return out


@entry("RG-0019", "The Model Register matches the live switch — a swap never outruns the record",
       LOCKED, scope="live /flags vs ai_price_card.json active_lane", fixed_on="2026-07-31",
       ref="Decision-Gate Process (Addendum 8, David 31 Jul 2026): when the live AI lane changes "
           "(manual Activate/Restore on the +1 page today; P2 breaker fail-over once P2b exposes "
           "breaker state in /flags), the Model Register must be updated the same working day — "
           "otherwise every cost/capability decision runs on a record that no longer describes "
           "production, the exact stale-values fault the register exists to prevent. This check "
           "reads the LIVE /flags active provider and compares it to the card's active_lane. "
           "Extend to the /flags breaker block when P2b lands.")
def rg_register_matches_live_switch():
    card_txt = repo_file("ai_price_card.json")
    if card_txt is None:
        return [(INFO, "running outside the repo -- register/live-switch check skipped")]
    try:
        recorded = json.loads(card_txt).get("active_lane")
    except Exception as ex:
        return [(FAIL, f"ai_price_card.json unreadable ({ex!r})")]
    if not recorded:
        return [(FAIL, "ai_price_card.json has no active_lane field -- the register cannot "
                       "track the live switch without it")]
    ap = _json("/flags").get("ai_provider") or {}
    # AMENDED 1 Aug 2026 (manual-pin feature): the register tracks the STANDING lane; a
    # time-decaying operator pin is ops, not procurement, so it must NOT trip this check.
    live = ap.get("standing") or ap.get("active")
    _pin = ap.get("override")
    if not live:
        return [(FAIL, "live /flags carries no ai_provider.active -- the switch surface itself "
                       "has changed; re-point this check")]
    if live != recorded:
        return [(FAIL, f"LIVE lane is {live!r} but the Model Register records {recorded!r} -- "
                       "a switch happened without updating the register; update "
                       "ai_price_card.json active_lane (and the switch's reason) today")]
    out = [(INFO, f"live standing lane {live!r} == register -- record is current")]
    if _pin:
        out.append((INFO, f"manual pin active: {_pin.get('provider')!r} until {_pin.get('expires_at')} "
                          "(ops override, decays automatically -- register untouched by design)"))
    return out


@entry("RG-0020", "The dashboard funnel strip is never staler than the Model Register",
       LOCKED, scope="repo, ai_funnel_snapshot.json vs ai_price_card.json", fixed_on="2026-08-01",
       ref="The +1 card shows the funnel ORDER (order + gate types only, David's ruling 1 Aug "
           "2026), served from ai_funnel_snapshot.json which scripts/price_truth.py --snapshot "
           "generates from the Model Register — ONE ranking engine. A card update without a "
           "snapshot regeneration would show David yesterday's order under today's card: the "
           "stale-values fault, on the very surface built to prevent it. Asserts snapshot exists "
           "and its card_version equals the register's version.")
def rg_funnel_snapshot_current():
    card_txt = repo_file("ai_price_card.json")
    snap_txt = repo_file("ai_funnel_snapshot.json")
    if card_txt is None:
        return [(INFO, "running outside the repo -- snapshot check skipped")]
    if snap_txt is None:
        return [(FAIL, "ai_funnel_snapshot.json missing -- run scripts/price_truth.py --snapshot "
                       "(the +1 card's funnel strip has no data source)")]
    try:
        cv = json.loads(card_txt).get("version"); sv = json.loads(snap_txt).get("card_version")
    except Exception as ex:
        return [(FAIL, f"snapshot/card unreadable ({ex!r})")]
    if cv != sv:
        return [(FAIL, f"funnel snapshot built from card {sv!r} but the register is at {cv!r} -- "
                       "regenerate: python3 scripts/price_truth.py --snapshot")]
    return [(INFO, f"snapshot current (card {cv})")]


@entry("RG-0021", "Bulk media ships hash-gated via the media lane; code rides the manifest engine",
       LOCKED, scope="repo, media_push.bat + scripts/sync_assets.ps1", fixed_on="2026-08-01",
       ref="DEPLOY-SYNC-2 (David, 1 Aug 2026): maps and phone-card images re-uploaded on every deploy "
           "although unchanged; fixed by riding scripts/sync_assets.ps1 (hash-gated). ASSERTION REWRITTEN "
           "2 Aug 2026 (DEPLOY-CONSOLIDATION-1, not weakened): the per-file copy engine inside "
           "deploy_marketsquare.bat was retired -- code now ships ONLY via the deploy-ref manifest engine, "
           "where 'release carriers are unconditional' is structural (allowlist copy, asserted by RG-0023). "
           "What must not rot is the OTHER half: binary media (git-ignored, so it cannot ride the mirror) "
           "ships through ONE hash-gated lane, media_push.bat, and that lane never carries code.")
def rg_deploy_sync_discipline():
    mp = repo_file("media_push.bat")
    if mp is None and repo_file("deploy_marketsquare.bat") is None:
        return [(INFO, "running outside the repo -- media-lane check skipped")]
    out = []
    if mp is None:
        out.append((FAIL, "media_push.bat missing -- media has no deploy lane (a new unmanaged "
                          "scp path will grow back in its place)"))
        return out
    if repo_file("scripts/sync_assets.ps1") is None:
        out.append((FAIL, "scripts/sync_assets.ps1 missing -- every synced media section breaks"))
    if "sync_assets.ps1" not in mp:
        out.append((FAIL, "media_push.bat no longer hash-gates via sync_assets.ps1 -- the "
                          "bulk-reupload class (DEPLOY-SYNC-2) is back"))
    for code in ("ms\.js", "bea_main\.py", "marketsquare\.html", "\.py\b"):
        if re.search(r"(?:scp|sync_assets\.ps1)[^\n]*-Filter[^\n]*" + code, mp) or \
           re.search(r"^\s*scp\b[^\n]*" + code, mp, re.M):
            out.append((FAIL, "media_push.bat ships code (" + code.replace("\\", "") +
                              ") -- the media lane must never carry code (one engine for code)"))
    out.append((INFO, "%d sync_assets call-sites in media_push.bat" % mp.count("sync_assets.ps1")))
    return out


@entry("RG-0022", "The circuit breaker exists, the seam consults it, and its test matrix is present",
       LOCKED, scope="repo, ai_breaker.py + ai_provider.py + bea_main.py + test matrix", fixed_on="2026-08-01",
       ref="P2a (design v1.2, 1 Aug 2026). Before this, failover was a naive per-call any-of with "
           "no memory: a dead provider re-tried on every request, no blip-vs-ban distinction, no "
           "alerts, no drill. Asserts the breaker module exists, bea attaches it at boot, "
           "complete() consults it (and carries the direct-probe mode that keeps probe attribution "
           "honest), and the 12-case mandatory test matrix stays in the repo. Recovery doctrine "
           "under test: dropouts auto-recover with hysteresis; bans wait for manual restore.")
def rg_breaker_wired():
    out = []
    if repo_file("ai_breaker.py") is None:
        if repo_file("ai_provider.py") is None:
            return [(INFO, "running outside the repo -- breaker check skipped")]
        out.append((FAIL, "ai_breaker.py missing -- the failover has no memory again"))
    bea = repo_file("bea_main.py"); seam = repo_file("ai_provider.py")
    if bea is not None and "import ai_breaker" not in bea:
        out.append((FAIL, "bea_main.py no longer attaches ai_breaker at boot"))
    if seam is not None:
        if "ai_breaker" not in seam:
            out.append((FAIL, "ai_provider.complete() no longer consults the breaker"))
        if "allow_fallback" not in seam or "probe=" not in seam:
            out.append((FAIL, "the direct no-fallback probe mode is gone from the seam -- probe "
                              "attribution is dishonest again (Peer blocker #3 class)"))
    if repo_file("test_ai_breaker.py") is None:
        out.append((FAIL, "test_ai_breaker.py missing -- the 12-case mandatory matrix must live in the repo"))
    return out



@entry("RG-0023", "ONE deploy engine: code ships only by publishing the deploy ref",
       LOCKED, scope="repo, ALL .bat paths + ops/autodeploy manifest (code class, every file)", fixed_on="2026-08-02",
       ref="DEPLOY-CONSOLIDATION-1 (David, 2 Aug 2026): ten deploy paths had accreted -- the 44KB "
           "per-file copy engine in deploy_marketsquare.bat, frontend-only/nops variants, bea_safe, "
           "eula/files/video/dashboard/n8n one-offs -- each an uncoordinated writer with its own "
           "version/cache behaviour. The 2 Aug morning near-miss (blind local +1 cache-buster vs the "
           "server's monotonic 421+) was this class about to fire. Consolidation: code deploys ONLY "
           "via the deploy-ref engine (server_deploy.sh: manifest allowlist, monotonic buster, health "
           "check, auto-rollback, seed+migration hook); deploy_marketsquare.bat became a thin gated "
           "push wrapper (marker: ONE-DEPLOY PUSH WRAPPER) so /ship, /TSL and /start all ride the "
           "same engine; the old bats retired to _to_delete/. This asserts the INVARIANT: no .bat "
           "grows back a second engine that copies app code to the server.")
def rg_one_deploy_engine():
    import glob
    bat = repo_file("deploy_marketsquare.bat")
    if bat is None:
        return [(INFO, "running outside the repo -- one-deploy check skipped")]
    out = []
    if "ONE-DEPLOY PUSH WRAPPER" not in bat:
        out.append((FAIL, "deploy_marketsquare.bat lost the push-wrapper marker -- the per-file "
                          "copy engine may be back; code must ship via the deploy ref"))
    if re.search(r"(?m)^\s*scp\b", bat):
        out.append((FAIL, "deploy_marketsquare.bat runs scp again -- it must only gate, commit, "
                          "and publish the deploy ref (one engine)"))
    man = repo_file("ops/autodeploy/deploy_manifest.txt")
    if man is None:
        out.append((FAIL, "ops/autodeploy/deploy_manifest.txt missing -- the engine has no placement map"))
    else:
        for carrier in ("marketsquare.html", "bea_main.py", "ms.js", "marketsquare_admin.html",
                        "dashboard.server.html", "scripts/seed_super_global.py"):
            if not re.search(r"(?m)^\s*" + re.escape(carrier) + r"\s*\|", man):
                out.append((FAIL, "manifest no longer places " + carrier +
                                  " -- a release carrier fell out of the ONE engine"))
    APP_CODE = ("bea_main.py", "ms.js", "ms.css", "marketsquare.html", "marketsquare_admin.html",
                "auth.py", "database.py", "storage.py", "payments.py", "ai_provider.py",
                "terms.html", "privacy.html", "support.html", "dashboard.server.html")
    MEDIA_LANE = {"media_push.bat"}   # binaries only; its own check is RG-0021
    for path in sorted(glob.glob(os.path.join(REPO, "*.bat"))):
        base = os.path.basename(path)
        if ".bak" in base or base in MEDIA_LANE:
            continue
        try:
            t = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        hits = [f for f in APP_CODE if re.search(r"(?m)^\s*scp\b[^\n]*" + re.escape(f), t)]
        if hits:
            out.append((FAIL, base + " copies app code to the server (" + ", ".join(sorted(set(hits))) +
                              ") -- a second deploy engine is growing back; ship via the deploy ref"))
    for retired in ("deploy_frontend_only.bat", "deploy_frontend_nops.bat", "deploy_bea_safe.bat",
                    "deploy_eula_v19.bat", "deploy_files.bat", "deploy_bit_monitoring.bat",
                    "deploy_n8n_templates.bat", "deploy_collectables_video.bat", "deploy_intro_video.bat"):
        if os.path.exists(os.path.join(REPO, retired)):
            out.append((FAIL, retired + " is back in the repo root -- it was retired to _to_delete/ "
                              "on 2 Aug 2026 (DEPLOY-CONSOLIDATION-1); one engine only"))
    return out



@entry("RG-0024", "The public /terms page a buyer sees is the EULA we actually published",
       LOCKED, scope="live edge vs origin, /terms (the legal surface, all future EULA versions)", fixed_on="2026-08-02",
       ref="EULA-CDN-STALE-1 (found 2 Aug 2026 during D1 closure): origin terms.html was v1.11 "
           "(md5-verified by the nightly drift check) but the CDN edge served v1.3 dated 17 May "
           "2026 to any cold visitor of /terms -- a 2.5-month-old EULA presented as current, "
           "spanning the v1.9/v1.10/v1.11 ships. Deploy purges ran in that window, so purging is "
           "not a durable guarantee for this URL. Occurrence fixed same day (manual purge via "
           "/admin/purge-cache, verified cold). This asserts the CLASS: the version stamp the "
           "EDGE serves must equal the version stamp the ORIGIN serves (origin reached with a "
           "cache-busting query). Catches any future EULA ship that the CDN quietly pins.")
def rg_terms_edge_matches_origin():
    import datetime as _dt
    def stamp(t):
        m = re.search(r"Version\s+(1\.\d+)", t)
        return m.group(1) if m else None
    edge = stamp(_get("/terms"))
    origin = stamp(_get("/terms?rgledger=" + _dt.date.today().isoformat()))
    out = []
    if not origin:
        out.append((FAIL, "origin /terms carries no 'Version 1.x' stamp -- stamp the EULA or amend this check deliberately"))
    if not edge:
        out.append((FAIL, "edge /terms carries no 'Version 1.x' stamp"))
    if origin and edge and origin != edge:
        out.append((FAIL, "CDN serves EULA v" + edge + " but origin serves v" + origin + " -- buyers are "
                          "reading a stale legal document; purge /terms and find what pinned it"))
    if origin:
        src = repo_file("terms.html")
        if src:
            rv = stamp(src)
            if rv and rv != origin:
                out.append((INFO, "repo terms.html is v" + rv + " vs live v" + origin + " -- an EULA ship is "
                                  "pending (legitimate if a release is staged)"))
    return out


@entry("RG-0025", "No third-party script is loaded on the index or any adventures map",
       LOCKED, scope="live index.html + all 9 adventures_*_map.html static pages (the whole former TP surface)",
       fixed_on="2026-08-03",
       ref="TP-DRIVE-1 REVERSED (3 Aug 2026, David's ruling). This entry previously asserted the "
           "Travelpayouts Drive loader must be PRESENT; that is now wrong, so the assertion is "
           "INVERTED deliberately -- it is not being weakened to make something pass. Evidence that "
           "forced the reversal: the loader pulled remote code from tp-em.com into the <head> of "
           "marketsquare.html, which is BOTH the live index AND the page carrying the "
           "identity-document flow, with no SRI hash and no script-src CSP (nginx_security_headers "
           "sets frame-ancestors only). A browser network capture on 3 Aug of a LOCKED, "
           "password-gated page load -- no password entered -- showed tp-em.com fetching 4 further "
           "JS chunks, POSTing repeatedly to /collect and /collect_batch, and calling "
           "/link-switch/v1/convert with the visited URL. The pre-launch gate is a client-side "
           "overlay inside the same document, so <head> executed for every visitor, tester, bot and "
           "scanner from 2 Aug onward regardless of the password. David's ruling: no third-party "
           "code on the app at all; if that is a prerequisite for Travelpayouts' products, the offer "
           "is passed. Affiliate revenue continues via plain affiliate LINKS, which need no script. "
           "This entry now asserts the surface stays clean -- any future session re-adding a remote "
           "loader trips it red.")
def rg_no_third_party_script_on_surface():
    BANNED = ("tp-em.com", "NTU3Mzkx.js")
    PAGES = ["/"] + ["/static/adventures_%s_map.html" % m
                     for m in ("reserve", "us", "uk", "au", "na", "bw", "mz", "c2c", "de")]
    out = []
    for p in PAGES:
        try:
            body = _get(p)
            for mark in BANNED:
                if mark in body:
                    out.append((FAIL, p + " carries third-party loader marker '" + mark + "' -- remote "
                                      "code is back on the app surface; David's 3 Aug ruling forbids it"))
        except Exception as ex:
            out.append((FAIL, p + " unreachable while checking for third-party scripts: " + repr(ex)))
    src_html = repo_file("marketsquare.html")
    if src_html is not None:
        for mark in BANNED:
            if mark in src_html:
                out.append((FAIL, "repo marketsquare.html carries '" + mark + "' -- the next deploy would "
                                  "put a third-party script back on the index"))
        ext = sorted(set(re.findall(r'<script[^>]+src=["\']https?://([^/"\']+)', src_html, re.I)))
        if ext:
            out.append((INFO, "external script origins on the index (eyeball these deliberately): "
                              + ", ".join(ext)))
    return out


@entry("RG-0026", "The deploy-drift monitor compares CONTENT, not Windows line endings",
       LOCKED, scope="repo, check_deploy_drift.py (every CRLF file it tracks: ms.js, marketsquare.html)",
       fixed_on="2026-08-03",
       ref="DRIFT-CRLF-1 (3 Aug 2026): DEPLOY-CONSOLIDATION-1 changed placement from scp (byte copy, "
           "CRLF preserved) to `git checkout` on the box, which writes LF. The working copy here is "
           "CRLF, so a RAW byte md5 can never match live again for a CRLF file -- ms.js measured "
           "local 1049997B vs live 1033905B, a difference of exactly its 16092 line endings, with the "
           "content proven identical (LF-normalised md5 60f5d918... on both sides). Left alone the "
           "monitor cries 'local ahead of live' forever, which trains everyone to ignore it -- and a "
           "REAL drift then hides inside the permanent false alarm. _md5() now normalises CRLF->LF "
           "before hashing (server files are already LF, so it is a no-op there). This asserts the "
           "normalisation stays in.")
def rg_drift_monitor_normalises_crlf():
    src = repo_file("check_deploy_drift.py")
    if src is None:
        return [(INFO, "running outside the repo -- drift-monitor normalisation check skipped")]
    out = []
    if 'replace(b"\\r\\n", b"\\n")' not in src:
        out.append((FAIL, "check_deploy_drift.py._md5 no longer normalises CRLF->LF -- every CRLF "
                          "file (ms.js, marketsquare.html) will report phantom drift forever"))
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

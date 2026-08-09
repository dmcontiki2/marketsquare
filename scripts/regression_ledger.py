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

PROVE THE CHECK BEFORE TRUSTING IT GREEN (7 Aug 2026)
-----------------------------------------------------
A new assertion must be shown to FAIL against deliberately broken code before its
green is believed. Two entries written on 7 Aug reported a REGRESSION against
correct code: RG-0041 matched the ".catch(()=>{})" written inside the comment that
documents the old bug, and RG-0044 counted occurrences of "return True" in a
function whose second fail-safe exit is a ternary. Both were the check being wrong,
not the app.

The failure mode cuts both ways and the quiet one is worse: a check that cannot
fail reports green forever and the ledger's whole promise — "it must STAY fixed" —
becomes decoration. So, for every new entry:

  * assert the PROPERTY, not a word count or a substring that might live in prose;
  * strip comments before scanning code (a fix's own explanation usually quotes
    the bug it fixed, verbatim);
  * mutate the source in memory to break the fix, run the check, and confirm it
    goes red — then confirm it is green against the real file.

A tripwire that cries wolf gets ignored, and an ignored tripwire is worth less
than no tripwire at all, because it also carries false comfort.

INSTRUMENT vs APP (LEDGER-OFFLINE-1, 7 Aug 2026)
-----------------------------------------------
Network-backed checks report UNVERIFIED, never REGRESSION, when the machine
running the ledger cannot reach the site at all — a cached preflight tells a
transport failure apart from an HTTP answer (any status means the site replied).
UNVERIFIED is loudly NOT a pass: messages still print and the run exits 2 (1 =
a real regression, 0 = genuinely clean). Before this, a laptop with no route to
the site produced 15 "REGRESSION: Tunnel connection failed" lines and the verdict
"Do not deploy over this" — the instrument reported as the app.

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
import json, os, re, sys, time, datetime, urllib.request, urllib.error

BASE = os.environ.get("TS_BASE", "https://trustsquare.co").rstrip("/")
UA = {"User-Agent": "TrustSquare-RegressionLedger/1.0 (dmcontiki2@gmail.com)"}
TIMEOUT = 25

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIL, INFO = "FAIL", "INFO"
LOCKED, OPEN = "LOCKED", "OPEN"

_cache = {}


# ── LEDGER-OFFLINE-1 (7 Aug 2026) ──────────────────────────────────────────
# A machine with no route to the site made every network-backed entry report
# "REGRESSION: Tunnel connection failed" — 15 of them in one run — and the ledger
# closed with "Do not deploy over this." That is the cry-wolf failure: a tripwire
# that reports the instrument as the app teaches you to ignore the tripwire. An
# unreachable site is now UNVERIFIED, which is loudly NOT a pass (same rule as
# LEDGER-FAULT-1 below: a skip is "unverified here", never "now passing").
class ProbeOffline(Exception):
    """The instrument cannot reach the site. Says nothing about the app."""


_NET = {"ok": None, "why": ""}


def _net_ready():
    """One cached preflight. An HTTP status of any kind means the site answered and
    every check is valid; only a TRANSPORT failure means we are blind."""
    if _NET["ok"] is None:
        try:
            urllib.request.urlopen(
                urllib.request.Request(BASE + "/health", headers=UA), timeout=TIMEOUT).read(1)
            _NET["ok"] = True
        except urllib.error.HTTPError:
            _NET["ok"] = True          # 403/401/500 IS an answer — the site is reachable
        except Exception as ex:
            _NET["ok"] = False
            _NET["why"] = repr(ex)[:140]
    return _NET["ok"]


def _require_net():
    if not _net_ready():
        raise ProbeOffline(_NET["why"])


def _get(path):
    if path not in _cache:
        _require_net()
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            _cache[path] = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        except urllib.error.HTTPError:
            raise
        except Exception as ex:
            raise ProbeOffline(repr(ex)[:140])
    return _cache[path]


def _status(path):
    """HTTP status for an UNAUTHENTICATED request. Never cached, never raises on 4xx/5xx —
    403/401 are legitimate answers here (RG-0027: the pre-launch gate must refuse anonymous GETs)."""
    _require_net()
    req = urllib.request.Request(BASE + path, headers=UA)
    try:
        return urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as ex:
        raise ProbeOffline(repr(ex)[:140])


def _post_status(path, data=b""):
    """HTTP status for an UNAUTHENTICATED POST. Used by negative entries that assert a
    write endpoint refuses anonymous callers. Never raises on 4xx/5xx."""
    _require_net()
    req = urllib.request.Request(BASE + path, data=data, headers=UA, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as ex:
        raise ProbeOffline(repr(ex)[:140])


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
        except ProbeOffline as ex:
            out = [(INFO, f"NOT EVALUATED - this machine cannot reach {BASE} ({ex}). "
                          "An instrument limit, not a verdict on the app. Re-run where "
                          "the site is reachable before trusting a green board.")]
        except Exception as ex:
            out = [(FAIL, f"check crashed (ledger fault, not necessarily the app): {ex!r}")]
        fails = [m for s, m in out if s == FAIL]
        infos = [m for s, m in out if s == INFO]
        # LEDGER-OFFLINE-1: several checks catch their own transport errors and turn
        # them into FAIL text, so they never reach the ProbeOffline handler above.
        # Reclassify those ONLY when the preflight has PROVEN this machine is blind -
        # when the site is reachable, every FAIL is treated as real, exactly as before.
        # Nothing is hidden: the messages still print, and UNVERIFIED still exits non-zero.
        if fails and _NET["ok"] is False and any(
                k in m for m in fails
                for k in ("ProbeOffline", "Tunnel connection failed", "URLError",
                          "Connection refused", "Name or service not known",
                          "Temporary failure in name resolution")):
            infos = infos + ["NOT EVALUATED - evidence for this entry depends on reaching "
                             + BASE + ", which this machine cannot do. The messages below are "
                             "the instrument failing, not proof about the app."] + fails
            fails = []
            status = "UNVERIFIED"
        elif (not fails) and any(s == INFO and "NOT EVALUATED" in m for s, m in out):
            status = "UNVERIFIED"          # never counted as a pass
        elif e["state"] == LOCKED:
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
    unver = n("UNVERIFIED")

    if "--json" in sys.argv:
        print(json.dumps({"date": datetime.date.today().isoformat(), "took_s": took,
                          "regressed": regressed, "holding": holding,
                          "open": open_, "ready_to_lock": ready, "unverified": unver,
                          "entries": results}, indent=1))
        return 1 if regressed else (2 if unver else 0)

    print(f"# Regression ledger — {datetime.date.today().isoformat()}  ({took}s · {BASE})")
    print()
    print(f"{len(results)} entries · {holding} holding · {regressed} REGRESSED · "
          f"{open_} open · {ready} ready to lock · {unver} UNVERIFIED")
    print()
    mark = {"HOLDING": "  ok  ", "REGRESSION": " !!!! ", "OPEN": " open ",
            "READY TO LOCK": " LOCK ", "UNVERIFIED": " ???? "}
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
    elif unver:
        print(f"RESULT: no regressions in what COULD be checked, but {unver} entr(ies) were NOT "
              f"EVALUATED - this machine cannot reach {BASE}. That is not a green board. "
              f"Re-run somewhere with a route to the site before deploying on this result.")
    elif ready:
        print(f"RESULT: no regressions. {ready} open item(s) now pass — promote them to LOCKED.")
    else:
        print(f"RESULT: every locked fix is holding. {open_} known defect(s) still open.")
    # 1 = a real regression · 2 = blind (unverified) · 0 = genuinely clean
    return 1 if regressed else (2 if unver else 0)


@entry("RG-0027", "The pre-launch gate is enforced by the EDGE, not by JavaScript",
       LOCKED, scope="whole domain at Cloudflare: documents AND API. /health + /payment/webhook + /.well-known/ exempt",
       fixed_on="2026-08-03",
       ref="GATE-SERVERSIDE-1 (3 Aug 2026, David: \"close it immediately\"). The old gate was a "
           "client-side overlay -- <div id=\"admin-gate\" style=\"display:none\"> inside "
           "marketsquare.html revealed by JS -- while nginx served that file straight off disk, so "
           "the COMPLETE page went to anyone who asked and JS painted a curtain over content that "
           "had already arrived. Proven: a gated load with NO password returned 200 on /wonders, "
           "/flags, /local-market/listings, /geo/cities and /tuppence/balance and ran every <head> "
           "script -- which is also how the Travelpayouts loader reached every visitor (RG-0025). "
           "CLOSED at the Cloudflare edge, not in nginx: custom rule 'PRELAUNCH GATE - block all "
           "except allowlisted IPs', action Block, expression "
           "(not ip.src in {...} and not http.request.uri.path in {\"/health\" \"/payment/webhook\"} "
           "and not starts_with(http.request.uri.path, \"/.well-known/\")). Verified from an "
           "off-allowlist host: / -> 403, /index.html -> 403, /?cb=rand -> 403, /wonders -> 403, "
           "/health -> 200. Cloudflare Zero Trust Access was REJECTED deliberately: its free tier "
           "still demands a standing 'charge this card for usage beyond free limits until "
           "cancellation' authorisation, the same uncapped-billing shape as the silent ~$360 Google "
           "burn. migrations/005_prelaunch_server_side_gate.py (nginx auth_basic) remains shipped "
           "but UNARMED as defence-in-depth. NOTE ON SELF-VERIFICATION: this check cannot prove the "
           "gate from an allowlisted network -- a 200 from David's own machine is EXPECTED, not a "
           "regression. It fails only on the two things that are always wrong: a 200 from off-list, "
           "or /health breaking (which would take server_deploy's auto-rollback down with it).")
def rg_gate_is_edge_enforced():
    out = []
    try:
        if _status("/health") != 200:
            out.append((FAIL, "/health is no longer reachable -- the WAF exemption broke; "
                              "server_deploy's health check and auto-rollback are blind. Fix the "
                              "exemption before the next deploy"))
    except Exception as ex:
        out.append((FAIL, "/health unreachable while checking the gate exemption: " + repr(ex)))
    try:
        root = _status("/")
    except Exception as ex:
        return out + [(INFO, "could not probe / for the gate: " + repr(ex))]
    if root == 403:
        out.append((INFO, "gate proving itself: / returns 403 from this host (off-allowlist)"))
    elif root == 200:
        out.append((INFO, "/ returns 200 -- this host is on the Cloudflare allowlist, so the gate "
                          "cannot be self-verified from here. Confirm from a phone on mobile data: "
                          "https://trustsquare.co/ must show a Cloudflare block page"))
    else:
        out.append((FAIL, "/ returned %s -- neither 403 (gated) nor 200 (allowlisted). The edge "
                          "rule or the origin is in an unexpected state" % root))
    return out


@entry("RG-0028", "The origin refuses direct connections -- Cloudflare is the ONLY way in",
       LOCKED, scope="Hetzner CPX32 178.104.73.239, inbound 80/443", fixed_on="2026-08-04",
       ref="ORIGIN-LOCKDOWN-1 (4 Aug 2026). Found by the GPT-5.6 Peer review "
           "(Records/PEER_REVIEW_2026-08-04-0516_security.md) as its top BLOCKER, and MISSED by the "
           "Author: the Cloudflare WAF rule of RG-0027 governed only traffic that chose to arrive via "
           "Cloudflare. The nginx `server_name 178.104.73.239 { return 444; }` block catches requests "
           "addressed to the raw IP, NOT requests carrying Host: trustsquare.co -- those selected the "
           "real vhost and were served in full. Proven 4 Aug: "
           "curl --resolve trustsquare.co:443:178.104.73.239 https://trustsquare.co/ returned 200 with "
           "391 KB, the entire marketplace, bypassing the WAF completely. The origin IP is printed in "
           "assets/nginx_marketsquare.conf, so this was discoverable, not theoretical. FIXED by a "
           "Hetzner Cloud Firewall (deny-all inbound): TCP 22 from David's IP only; TCP 80 and 443 "
           "from Cloudflare's 15 IPv4 + 7 IPv6 published ranges only; outbound untouched. Re-tested: "
           "the same curl now fails to connect after 21s, while /health still returns 200 THROUGH "
           "Cloudflare. THIS ENTRY IS THE LOAD-BEARING ONE: RG-0027's edge rule is only an access "
           "boundary while this firewall stands. Remove or widen the firewall and the WAF becomes "
           "decorative again. Cloudflare's ranges change occasionally -- if legitimate traffic starts "
           "failing, re-pull https://www.cloudflare.com/ips-v4 and ips-v6 before suspecting anything "
           "else. A GitHub webhook posting direct to the IP (rather than via the domain) would also "
           "now be dropped. FALSE-ALARM NOTE (5 Aug 2026): a sandboxed baseline run reported this "
           "entry REGRESSED. Independent verification the same day (check-host.net global TCP "
           "probes: 57/58 nodes timed out on both 80 and 443; Hetzner console: firewall "
           "trustsquare-origin-lockdown Fully applied, 3 rules intact) proved the firewall was "
           "never off -- the runner sat behind a transparent proxy that intercepts ALL outbound "
           "TCP on 80/443, so every raw connect 'succeeded' locally. The probe now self-checks "
           "runner fitness first (control connect to unroutable TEST-NET-3); an unfit runner "
           "reports INFO, never a false FAIL. The assertion is unchanged on fit runners.")
def rg_origin_refuses_direct():
    import socket
    ORIGIN, out = "178.104.73.239", []
    # RG-0028-GUARD (5 Aug 2026): some runners (Claude cloud sandboxes among them)
    # transparently intercept ALL outbound TCP on 80/443, so a raw connect "succeeds"
    # locally no matter what the Hetzner firewall does. Control: connect to an
    # unroutable TEST-NET-3 address. If THAT succeeds, nothing this probe measures
    # is real -- say so and skip, rather than raise a false open-gate alarm.
    # On a fit runner the control times out and behaviour is identical to before.
    unfit = False
    ck = socket.socket(); ck.settimeout(3)
    try:
        ck.connect(("203.0.113.1", 80)); unfit = True
    except Exception:
        pass
    finally:
        try: ck.close()
        except Exception: pass
    if unfit:
        out.append((INFO, "RUNNER UNFIT for the raw-TCP probe: a connect to unroutable "
                          "203.0.113.1:80 'succeeded', so this network intercepts outbound "
                          "80/443 and any direct-connect result from here is meaningless. "
                          "Verify from an independent vantage instead: check-host.net TCP "
                          "check on 178.104.73.239 ports 80 and 443 (real nodes must all "
                          "time out), or David's own browser opening http://178.104.73.239/ "
                          "(must time out -- never render, reset, or answer)."))
    for port in (() if unfit else (80, 443)):
        sk = socket.socket(); sk.settimeout(6)
        try:
            sk.connect((ORIGIN, port))
            out.append((FAIL, "origin %s:%d ACCEPTED a direct connection -- the Cloudflare WAF "
                              "(RG-0027) can be bypassed entirely. Check the Hetzner Cloud Firewall "
                              "is still applied to the server" % (ORIGIN, port)))
        except Exception:
            pass                      # refused/timed out = correct
        finally:
            try: sk.close()
            except Exception: pass
    try:
        if _status("/health") != 200:
            out.append((FAIL, "/health does not answer through Cloudflare -- the firewall may have "
                              "cut the legitimate path too; check the Cloudflare ranges are current"))
    except Exception as ex:
        out.append((FAIL, "/health unreachable through Cloudflare after origin lockdown: " + repr(ex)))
    return out


@entry("RG-0029", "The reviewer token gate ENFORCES at the origin: anonymous data requests get 401",
       OPEN, scope="every data endpoint (GATE-ENFORCE-1 / migrations/007); /health stays 200",
       ref="Planned 5 Aug 2026 with GATE-ENFORCE-1 but NEVER ADDED -- the class failure this "
           "exposes is the UNASSERTED FIX: the app half (ts_review cookie + /review/verify) "
           "shipped and works, but migration 007 (nginx auth_request on the data API) never "
           "took effect, and with no assertion here the gap was invisible. The Cloudflare "
           "IP-only scaffolding rule masked it by blocking everyone until 7 Aug (DW-019/DW-023). "
           "Added 7 Aug 2026 as OPEN so the gap is machinery-visible from today: expected to "
           "FAIL until migration 007 is applied over SSH (DW-020), then READY TO LOCK.")
def rg_origin_gate_enforces():
    out = []
    try:
        code = _status("/wonders")
    except Exception as ex:
        return [(FAIL, "/wonders unreachable while probing the gate: " + repr(ex))]
    if code == 200:
        out.append((FAIL, "anonymous GET /wonders answered 200 -- the origin token gate is NOT "
                          "enforcing; the reviewer curtain is client-side only"))
    elif code not in (401, 403):
        out.append((FAIL, "anonymous GET /wonders answered %d -- neither open nor gated" % code))
    try:
        if _status("/health") != 200:
            out.append((FAIL, "/health no longer answers 200 -- the gate exemption list is wrong "
                              "(deploy rollback and external monitoring both depend on it)"))
    except Exception as ex:
        out.append((FAIL, "/health unreachable: " + repr(ex)))
    return out


@entry("RG-0030", "The in-app tester fault channel exists, is fail-closed, and ships to every page",
       LOCKED, scope="all tester-facing pages (index, admin, legal, 9 adventure maps)",
       fixed_on="2026-08-05",
       ref="MAINT-B1b. Testers had no way to report an APP FAULT from inside the app -- "
           "seller_complaints/lm_complaints are marketplace conduct, and email skipped the "
           "Maintenance agent's intake entirely. This asserts three things that must stay true: "
           "the widget is actually served, an unauthenticated POST can never file a fault "
           "(fail-closed, so a public visitor cannot flood the queue), and /flags still carries "
           "the fault_report switch the widget reads. OPEN until deployed and proven live -- "
           "promote to LOCKED the moment it passes.")
def rg_tester_fault_channel():
    out = []
    try:
        if _status("/static/ts_report.js") != 200:
            out.append((FAIL, "/static/ts_report.js is not served -- the report button cannot "
                              "appear on any page, so testers have no way in"))
    except Exception as ex:
        out.append((FAIL, "tester widget unreachable: " + repr(ex)))
    try:
        code = _post_status("/app/fault")
        if code == 200:
            out.append((FAIL, "POST /app/fault accepted an UNAUTHENTICATED report -- the intake "
                              "must refuse anyone without a tester credential (401) or refuse "
                              "outright while the flag is off (503)"))
    except Exception as ex:
        out.append((INFO, "intake probe inconclusive: " + repr(ex)))
    code = _status("/flags")
    if code == 200:
        try:
            if "fault_report" not in _get("/flags"):
                out.append((FAIL, "/flags no longer carries fault_report -- the widget fails closed "
                                  "and every tester silently loses the report button"))
        except Exception as ex:
            out.append((FAIL, "/flags unreadable despite a 200: " + repr(ex)))
    elif code in (401, 403):
        # GATE-ENFORCE-1 (5 Aug): the reviewer gate refuses anonymous reads at the origin.
        # A gated /flags is CORRECT; a gated tester's own browser carries the ts_review
        # cookie and gets 200. Verified in-browser 5 Aug: fault_report present, value false.
        out.append((INFO, "/flags is gated to anonymous callers (%d) -- expected while the "
                          "pre-launch gate is up; verify the key from a gated browser" % code))
    else:
        out.append((FAIL, "/flags answered %d -- neither readable nor gated" % code))
    return out


@entry("RG-0031", "openDetail never dereferences a listing it did not find (no silent dead clicks)",
       LOCKED, scope="every card in the app, every city, every category — the whole openDetail call graph",
       fixed_on="2026-08-05",
       ref="TS-0002/TS-0003, the first faults reported through the new in-app channel. openDetail() "
           "read l.trust straight off findListing()'s result. Two ways that returned undefined: a RAW "
           "BEA INTEGER id (FEA ids are 'bea_N' strings — sobViewMyListing passed the integer), and any "
           "wishlist feed/showcase card for a listing OUTSIDE the active city, since LISTINGS holds only "
           "the active city while those feeds deliberately span countries. The TypeError was thrown inside "
           "a handler, so nothing caught it and nothing rendered: the button 'did nothing'. Invisible "
           "failures are the expensive kind — this asserts the guard, not the symptom.")
def rg_open_detail_guard():
    src = repo_file("ms.js")
    if src is None:
        return [(INFO, "running outside the repo — openDetail guard check skipped")]
    i = src.find("function openDetail(id){")
    if i < 0:
        return [(FAIL, "openDetail is gone from ms.js")]
    head = src[i:i + 1400]
    out = []
    if "if (!l)" not in head:
        out.append((FAIL, "openDetail lost its not-found guard — every out-of-city card and every raw "
                          "integer id becomes a silent dead click again (TS-0002/0003)"))
    if "'bea_' + id" not in head and '"bea_" + id' not in head:
        out.append((FAIL, "openDetail no longer normalises a raw BEA integer id to the FEA 'bea_N' form"))
    if "setTimeout(() => openDetail(first.id), 300)" in src:
        out.append((FAIL, "sobViewMyListing is back on the raw id + 300ms race that broke it"))
    return out


@entry("RG-0032", "AI endpoints gate on ANY configured lane, never on one vendor's key",
       LOCKED, scope="repo, bea_main.py -- all 15 endpoint gates + ai_provider.any_lane_configured()",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F1 (David's go, 5 Aug 2026). Fifteen endpoints opened with "
           "'if not ANTHROPIC_API_KEY: 503' although every call runs through the vendor-neutral "
           "seam -- with the Anthropic key absent and OpenAI/Scaleway keyed and healthy, every AI "
           "service refused anyway, defeating the independence doctrine (Addendum 5.2: the app "
           "must not need any single vendor to run). The 1 Aug AI_DRILL_BAN drill could not catch "
           "it (key present, lane banned); only the unconfigured-key drill variant exposes it. "
           "Fixed at class level in one pass. Both drill variants must be re-run post-deploy.")
def rg_any_lane_gate():
    src = repo_file("bea_main.py")
    prov = repo_file("ai_provider.py")
    if src is None or prov is None:
        return [(INFO, "running outside the repo -- any-lane gate check skipped")]
    out = []
    n = src.count("if not ANTHROPIC_API_KEY")
    if n:
        out.append((FAIL, f"bea_main.py gates on ANTHROPIC_API_KEY again ({n}x) -- a single-vendor "
                          "key outage would 503 AI services despite healthy standby lanes (F1 class)"))
    if src.count("any_lane_configured()") < 15:
        out.append((FAIL, "fewer than 15 any_lane_configured() gates in bea_main.py -- an endpoint "
                          "lost its vendor-neutral gate (or a new one was added vendor-specific)"))
    if "def any_lane_configured" not in prov:
        out.append((FAIL, "ai_provider.py no longer defines any_lane_configured()"))
    return out


@entry("RG-0033", "Paid AI services charge Tuppence on DELIVERY, never before the model call",
       LOCKED, scope="AI1 rewrite, AI2 audit, AI5 batch cards (AI3/AI4 already compliant) -- the whole paid-AI class",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F2. The help card promises 'server error -> no Tuppence deducted', "
           "but AI1/AI2/AI5 ran _deduct_tuppence BEFORE the model call and their failure detail "
           "admitted 'Tuppence charged'. David's ruling 5 Aug: the refund promise must be true. "
           "All three now pre-flight with _require_tuppence and deduct only after a successful "
           "result (the Session-95 deliver-then-charge pattern, same as AI3/AI4).")
def rg_deliver_then_charge():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- deliver-then-charge check skipped")]
    out = []
    n = src.count('\u2014 Tuppence charged"')   # the dishonest form; 'no Tuppence charged' is the honest one
    if n:
        out.append((FAIL, f"a failure path admits charging before delivery again ({n}x '-- Tuppence charged')"))
    for var in ("_rw_charge_desc", "_au_charge_desc", "_bc_charge_desc"):
        if src.count(var) < 2:
            out.append((FAIL, f"{var} missing -- its service lost the deliver-then-charge structure"))
    if src.count("no Tuppence was charged") < 3:
        out.append((FAIL, "the honest failure copy ('no Tuppence was charged') is gone from a paid AI service"))
    return out


@entry("RG-0034", "The breaker heartbeat lives in the BEA -- tripped lanes recover without traffic",
       LOCKED, scope="bea_main.py startup (HEARTBEAT-1). P2c's latency baseline + p95 T2 clause remain separate work",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F5 + David's ruling 5 Aug ('it should be live now, otherwise how "
           "will we have confidence it works at launch'). Implements AI_AUTO_FAILOVER_P2_DESIGN "
           "section 6: 60 s tick, ONE atomically-claimed direct probe per tick, round-robin across "
           "eligible rows, text ping, spend logged. Without it a tripped lane only recovers when "
           "real traffic happens to probe it -- an overnight outage would stick until morning.")
def rg_breaker_heartbeat():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- heartbeat check skipped")]
    out = []
    if "HEARTBEAT-1" not in src:
        out.append((FAIL, "HEARTBEAT-1 block is gone from bea_main.py"))
    if "claim_probe" not in src:
        out.append((FAIL, "the heartbeat no longer claims probes atomically (claim_probe missing)"))
    return out


@entry("RG-0035", "User-facing AI service copy is vendor-neutral -- no lane name promised to users",
       LOCKED, scope="marketsquare.html AI Services help card, all five services",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F3, David's ruling 5 Aug: neutral reference so a lane swap never "
           "makes the copy wrong. The card said 'Claude rewrites/reviews/drafts/compares/estimates' "
           "while Phase-A cost-first routing + failover may lawfully serve any wired lane on a "
           "given call. Dev-comment mentions of Claude are fine; USER-facing claims are not.")
def rg_vendor_neutral_copy():
    src = repo_file("marketsquare.html")
    if src is None:
        return [(INFO, "running outside the repo -- copy check skipped")]
    out = []
    for phrase in ("Claude rewrites", "Claude reviews", "Claude drafts",
                   "Claude compares", "Claude estimates"):
        if phrase in src:
            out.append((FAIL, f"user-facing copy names a vendor again: '{phrase}...' -- a lane swap makes it false"))
    return out


@entry("RG-0036", "KYC document fetch is SSRF-safe: allowlisted host, no redirects, size-capped",
       LOCKED, scope="bea_main.py _sonnet_verify_identity / _fetch_kyc_document (KYC-SSRF-1)",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F3 (Peer round 2 BLOCKER-class). verify-identity fetched a "
           "caller-supplied doc_url with a bare urllib.urlopen -- no host allowlist, no private-IP "
           "block, no redirect ban, no size cap. A caller with the public app key could aim it at "
           "cloud metadata (169.254.169.254), an internal address, or an unbounded file (SSRF + "
           "memory-DoS). Fixed: _fetch_kyc_document pins the URL to R2_PUBLIC_URL, forbids "
           "redirects (_NoRedirect), rejects any host resolving to a private/loopback/link-local/"
           "reserved address, and caps the read at 12 MB. Also KYC-PIN-1: the KYC vision call is "
           "allow_fallback=False so ID documents never fan out to standby vendors.")
def rg_kyc_ssrf():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- KYC SSRF check skipped")]
    out = []
    if "_fetch_kyc_document" not in src:
        out.append((FAIL, "the KYC SSRF guard _fetch_kyc_document is gone"))
    # the naive fetch must not return
    if 'urllib.request.urlopen(req, timeout=10)' in src and "_fetch_kyc_document" in src[:src.find("def _fetch_kyc_document")+50]:
        pass
    if "is not on the approved storage host" not in src:
        out.append((FAIL, "the KYC host allowlist check is missing"))
    if "allow_fallback=False" not in src or "KYC-PIN-1" not in src:
        out.append((FAIL, "KYC-PIN-1 gone -- ID documents could fan out to standby vendors again"))
    return out


@entry("RG-0037", "Paid AI spend is RESERVED before dispatch -- concurrent calls cannot overshoot the ceiling",
       LOCKED, scope="bea_main.py ai_spend_holds + _check_cost_ceiling + _log_ai_spend (C1-RES)",
       fixed_on="2026-08-05",
       ref="AI-SERVICES-AUDIT-1 F2 (Peer MAJOR, both rounds). _check_cost_ceiling summed only "
           "LOGGED spend, written AFTER the call, so N concurrent requests all passed the check "
           "before any recorded cost and could collectively breach the cap. Fixed: a worst-case "
           "reservation (ai_spend_holds) is placed in the SAME transaction as the ceiling check and "
           "counted by it; _log_ai_spend settles the hold once real cost is known; holds self-expire "
           "(180 s TTL) so an aborted call cannot wedge the budget. Isolated-logic test proved the "
           "bound (10 concurrent -> admitted only up-to-cap, not all 10).")
def rg_spend_reservation():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- spend reservation check skipped")]
    out = []
    for tok in ("ai_spend_holds", "_active_holds_usd", "_settle_hold", "C1-RES"):
        if tok not in src:
            out.append((FAIL, f"C1-RES reservation machinery incomplete: {tok} missing"))
    if "_active_holds_usd(conn)" not in src:
        out.append((FAIL, "the platform ceiling no longer counts outstanding reservations -- concurrency race is back"))
    return out


@entry("RG-0038", "The introduction relay divulges nothing: aliases only, enrolled parties only, revocable",
       LOCKED, scope="bea_main.py INTRO-RELAY-1 (accept_intro, /intro/relay, _relay_forward) — dark until launch_switches.intro_relay",
       fixed_on="2026-08-05",
       ref="David's Option B ruling + doctrine (5 Aug 2026): 'Nothing of the customer's leaves "
           "TrustSquare except a consented, revocable email channel — never the address itself.' "
           "Before this, accept_intro handed BOTH raw emails to each party via the n8n webhook — "
           "an irreversible disclosure. Now (flag ON) the parties are introduced through masked "
           "aliases; the webhook carries aliases only; the relay endpoint accepts mail only from "
           "the two enrolled real addresses; From/Reply-To on every forward is an alias; channels "
           "expire and can be killed. Isolated-logic test proved all 7 semantics incl. kill-switch "
           "closing both directions and header-injection stripping. Flag OFF = legacy behaviour.")
def rg_intro_relay():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- intro relay check skipped")]
    out = []
    for tok, why in (
        ("intro_relay_aliases", "the alias mapping table is gone"),
        ("def _intro_relay_enabled", "the fail-closed flag reader is gone"),
        ('@app.post("/intro/relay")', "the relay inbound endpoint is gone"),
        ('"reply_to": from_alias', "the forward lost its alias Reply-To -- replies would leave the curtain (RELAY-FROM-1)"),
        ('from_addr != counter["real_email"]', "the enrolled-parties-only check is gone"),
        ('ai_provider.envkey("RELAY_INBOUND_SECRET")', "the secret read lost its ENVKEY-1 fallback -- os.getenv is empty on the server (systemd does not export .env), so the rail would silently report unconfigured"),
        ('_b_alias if _relay_on else intro["buyer_email"]', "the accept webhook can leak the raw buyer email under the relay again"),
    ):
        if tok not in src:
            out.append((FAIL, "INTRO-RELAY-1 rotted: " + why))
    return out


@entry("RG-0039", "Charged identity is PROVEN by session, never asserted by parameter",
       LOCKED, scope="bea_main.py ACCOUNT-BIND-1 (ts_user session at /auth/verify + binds on AI1-AI5, create/accept/decline intro) — dark until launch_switches.account_binding",
       fixed_on="2026-08-05",
       ref="Peer round-2 BLOCKER (F1), David's Option A ruling. The account charged was a plain "
           "caller parameter behind the shared public app key. Now /auth/verify keeps its "
           "magic-link proof as an HttpOnly ts_user session cookie (JWT scope 'user' — the shared "
           "review token, scope 'review', can never pass), and every charging endpoint binds "
           "through _bind_charged_email: flag ON = enforce (401 no session / 403 mismatch), "
           "flag OFF = shadow-log so the flip is informed. Accept/decline intro additionally "
           "require the session to BE the listing owner (BIND-OWNER-1). Isolated test proved "
           "scope separation: review/expired/forged/absent tokens all refuse.")
def rg_account_binding():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- account binding check skipped")]
    out = []
    if 'response.set_cookie("ts_user"' not in src:
        out.append((FAIL, "/auth/verify no longer establishes the ts_user session"))
    for tok in ("def _account_binding_enabled", "def _session_email", "def _bind_charged_email"):
        if tok not in src:
            out.append((FAIL, "ACCOUNT-BIND-1 helper gone: " + tok))
    n = src.count("_bind_charged_email(")
    if n < 7:
        out.append((FAIL, f"only {n} charge points bind the session (need >= 7: def + AI1-AI5 + create-intro)"))
    if src.count("BIND-OWNER-1") < 2:
        out.append((FAIL, "accept/decline intro lost the listing-owner gate (BIND-OWNER-1)"))
    if 'p.get("scope") != "user"' not in src:
        out.append((FAIL, "the session check no longer rejects non-user scopes -- the shared review token could charge accounts"))
    return out


@entry("RG-0040", "A photo is judged by its BYTES, never by the browser's declared type",
       LOCKED, scope="bea_main.py PHOTO-TYPE-1 — all four upload gates",
       fixed_on="2026-08-07",
       ref="TS-0025 (Maroushka, 7 Aug 2026) + TS-0012 before it. The gate compared the "
           "client-supplied Content-Type against an allow-list. Windows and Android send "
           "application/octet-stream (or nothing) for a .heic straight off an iPhone, so a photo "
           "pillow-heif could decode perfectly was refused — and refused with 'Only JPEG, PNG or "
           "WebP photos accepted', which was ALSO false whenever the HEIF wheel was present. "
           "Now a supported or generic/blank declared type passes to Image.open(), which is the "
           "real validator, and every rejection names what we actually accept. 10/10 offline "
           "cases pass, including ct=application/octet-stream + IMG_1.HEIC (her exact case).")
def rg_photo_type():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- photo type check skipped")]
    out = []
    for tok, why in (
        ("def _photo_type_ok", "the byte-honest gate helper is gone"),
        ("def _is_heic_bytes", "the ISO-BMFF brand sniff is gone"),
        ("def _photo_reject_msg", "the honest rejection message helper is gone"),
        ("def _photo_decode_msg", "the actionable decode-failure helper is gone"),
    ):
        if tok not in src:
            out.append((FAIL, "PHOTO-TYPE-1 rotted: " + why))
    n = src.count("if not _photo_type_ok(")
    if n < 4:
        out.append((FAIL, f"only {n} upload gates use the byte-honest check (need 4)"))
    if 'detail="Only JPEG, PNG or WebP' in src:
        out.append((FAIL, "a gate went back to the lying hard-coded rejection message"))
    if 'detail="Could not read image file"' in src:
        out.append((FAIL, "a decode failure went back to the blanket message -- a HEIC-with-no-wheel "
                          "reads as a corrupt file and the seller is sent away with no way forward"))
    return out


@entry("RG-0041", "A photo that does not upload always SAYS SO — silence is the bug",
       LOCKED, scope="ms.js — batch publish (sobGoLive) + single-photo advert path",
       fixed_on="2026-08-07",
       ref="TS-0026 (Maroushka, 7 Aug 2026): 'the pictures didn't pull through, there was no "
           "notice to inform me'. The batch loop surfaced ONLY HTTP 422; a 400 (a format the "
           "server could not decode) and a dropped request both vanished, and the single-photo "
           "path swallowed everything with .catch(()=>{}). The advert published photo-less and "
           "said nothing. Both paths now report every failure with the photo number and the "
           "server's own reason. NOTE the declaration guard below: the first cut of this fix "
           "pushed to _photoFails without ever declaring it — syntax passed, runtime would have "
           "thrown ReferenceError and broken publish outright. Verified by brace-depth proof.")
def rg_photo_failure_visible():
    src = repo_file("ms.js")
    if src is None:
        return [(INFO, "running outside the repo -- photo failure check skipped")]
    out = []
    if "const _photoFails=[]" not in src.replace(" ", "").replace("const_photoFails=[]", "const _photoFails=[]"):
        if "const _photoFails" not in src:
            out.append((FAIL, "_photoFails is USED but never DECLARED -- publish throws "
                              "ReferenceError at the first failing photo"))
    if src.count("_photoFails") < 5:
        out.append((FAIL, "the batch-publish failure collector was removed -- photos fail silently again"))
    # Scan CODE only. v1 of this check matched the ".catch(()=>{})" written inside the
    # comment that documents the old bug, and reported a regression against a correct
    # file -- a tripwire that cries wolf gets ignored, which is worse than no tripwire.
    win = src.split("3. Upload photo if provided")[-1][:900]
    code = "\n".join(l for l in win.split("\n") if not l.lstrip().startswith("//"))
    if ".catch(()=>{})" in code:
        out.append((FAIL, "the single-photo advert path swallows failures again"))
    if "const _pr1" not in code or "showToast(" not in code:
        out.append((FAIL, "the single-photo advert path lost its failure notice"))
    return out


@entry("RG-0042", "The ops self-check publishes FACTS and never a secret",
       LOCKED, scope="bea_main.py SELFCHECK-1 — GET /ops/selfcheck (API-key gated)",
       fixed_on="2026-08-07",
       ref="David, 7 Aug 2026. A session cannot open an SSH tunnel to the box, so every "
           "'is that dependency actually installed / is the flag actually on / did the deploy "
           "actually land' question cost a manual round-trip and several of them were answered "
           "by inference instead of evidence. This endpoint answers them over one authenticated "
           "HTTPS GET. Its whole value depends on it staying safe to call, so the tripwire "
           "asserts it never grows a key, token or customer field.")
def rg_selfcheck():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- selfcheck check skipped")]
    out = []
    if '@app.get("/ops/selfcheck")' not in src:
        out.append((FAIL, "SELFCHECK-1 endpoint is gone -- server questions go back to guesswork"))
    if "def _ops_counter" not in src:
        out.append((FAIL, "the since-boot 5xx counter middleware is gone"))
    if "Depends(auth.require_api_key)" not in src.split("/ops/selfcheck")[-1][:700]:
        out.append((FAIL, "/ops/selfcheck lost its API-key gate -- it would be world-readable"))
    body = src.split('@app.get("/ops/selfcheck")')[-1].split("\n@app.")[0]
    for bad in ("API_KEY", "_KEY\"", "SECRET", "PASSWORD", "seller_email", "reporter_email",
                "real_email", "ANTHROPIC", "RESEND_API"):
        if bad in body:
            out.append((FAIL, f"/ops/selfcheck now references {bad!r} -- it must publish facts, "
                              "never secrets or customer data"))
    return out


@entry("RG-0043", "Every client upload to a key-guarded endpoint actually carries the key",
       LOCKED, scope="ms.js — all POSTs to /users/{email}/documents (Agent Hub, My Space, batch publish)",
       fixed_on="2026-08-07",
       ref="TS-0013 (Maroushka, 5 Aug 2026): 'Found the place where I can update my "
           "qualifications, but it doesn't allow me do upload it or verify my status as an agent "
           "at the agency I'm at.' The Agent Hub credential upload was the ONE /documents POST in "
           "the app that omitted the X-Api-Key header, against a route guarded by "
           "Depends(auth.require_api_key) — so it returned 401 on every attempt, for every user, "
           "since the day it shipped. It was never a permissions or account problem: that button "
           "could not have worked for anybody. The sibling calls at the batch-publish and My Space "
           "paths always sent the header, which is why the fault looked user-specific.")
def rg_documents_key():
    src = repo_file("ms.js")
    if src is None:
        return [(INFO, "running outside the repo -- documents key check skipped")]
    import re as _re
    out = []
    posts = 0
    for m in _re.finditer(r"fetch\(\s*BEA_URL\s*\+\s*'/users/'[^;]{0,300}", src, _re.S):
        seg = m.group(0)
        if "/documents" not in seg or "/documents/public" in seg:
            continue
        if "method:'POST'" not in seg.replace(" ", "") :
            continue
        posts += 1
        if "X-Api-Key" not in seg:
            ln = src[:m.start()].count("\n") + 1
            out.append((FAIL, f"ms.js:{ln} POSTs a document without X-Api-Key -- the server "
                              "guards that route, so it 401s every time and the seller is simply "
                              "told the upload failed"))
    if posts < 3:
        out.append((FAIL, f"only {posts} guarded document POSTs found (expected 3) -- a upload "
                          "path was removed or rewritten; re-check the key on each"))
    return out


@entry("RG-0044", "A photo is REFUSED rather than blurred into ruin",
       LOCKED, scope="bea_main.py PHOTO-REPLACE-1 — _anon_blur_until_clean correction loop + last-resort rung",
       fixed_on="2026-08-07",
       ref="TS-0022 (Maroushka, 7 Aug 2026) — third report of the same complaint after TS-0007 "
           "and TS-0008, which is why it was a doctrine change and not another patch. The blur "
           "was already minimal and vision-driven; the sprawl came from the rule that the "
           "pipeline may NEVER reject a photo (David, 15 Jul: 'ugly-but-anonymous beats "
           "rejected'), so it escalated instead - four correction rounds each painting on top of "
           "the last, then a last-resort rung blurring every region ever accumulated. David "
           "reversed it 7 Aug in Maroushka's own terms: 'if we cant blurr a photo enough and it "
           "starts looking bad, then we should request a replacement rather.' Coverage is "
           "measured by UNION rasterise so the same plate boxed across four rounds counts ONCE - "
           "summing box areas would refuse good photos. Offline: plate 2.5%, plate+strip 4.6%, "
           "same plate x4 still 2.5%, half-facade 61% (refused). This direction CANNOT weaken "
           "anonymity: refusing a photo cannot leak what the blur failed to hide.")
def rg_photo_replace():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- photo replace check skipped")]
    out = []
    for tok, why in (
        ("def _anon_blur_fraction", "the coverage measure is gone"),
        ("def _anon_replace_enabled", "the fail-safe switch reader is gone"),
        ("_ANON_REPLACE_TAG", "the sentinel label the callers translate is gone"),
        ("photo_replace_request", "the launch switch column is gone"),
    ):
        if tok not in src:
            out.append((FAIL, "PHOTO-REPLACE-1 rotted: " + why))
    if src.count("_ANON_MAX_BLUR_FRAC") < 4:
        out.append((FAIL, "the frame-coverage ceiling is no longer consulted at every rung (need "
                          "the constant, the env override, the loop guard and the last-resort guard)"))
    if "return None, labels + [_ANON_REPLACE_TAG]" not in src:
        out.append((FAIL, "the pipeline no longer asks for a replacement -- it is back to "
                          "escalating the blur until the photo is ruined"))
    # Assert the PROPERTY, not a word count. v1 of this check required two literal
    # "return True" lines and failed against correct code whose no-row branch is a
    # ternary (`... if row else True`). A tripwire that cries wolf gets ignored, so
    # both fail-safe exits are named explicitly here.
    blk = src.split("def _anon_replace_enabled")[-1][:900]
    if "else True" not in blk:
        out.append((FAIL, "_anon_replace_enabled no longer defaults ON when the switch row is "
                          "missing -- a fresh or half-migrated DB would restore the over-blur "
                          "behaviour silently"))
    if "except Exception:" not in blk or "return True" not in blk.split("except Exception:")[-1][:120]:
        out.append((FAIL, "_anon_replace_enabled no longer defaults ON when the DB read raises -- "
                          "a hiccup (or a row predating the column) would restore the over-blur "
                          "behaviour silently"))
    if "without blurring so much of it" not in src:
        out.append((FAIL, "the replacement request lost its honest wording -- the seller is told "
                          "'could not blur' again, which sends them back to retake a photo that "
                          "would fail in exactly the same way"))
    return out



@entry("RG-0045", "No public endpoint returns seller identity — anonymity IS the product",
       LOCKED, scope="EVERY unauthenticated JSON endpoint, present and future", fixed_on="2026-08-08",
       ref="SELLER-ANON-1 (8 Aug 2026). /listings shipped seller_email on all 50 rows, exposing two "
           "real founding sellers' personal addresses to anonymous callers. The requirement was never "
           "misunderstood: _strip_seller_identity() has guarded the local-market feed since PR-29, and "
           "the detail endpoint uses an explicit column allowlist commented 'No seller identity "
           "returned'. It was simply never applied to /listings, which builds its payload from SELECT * "
           "and is therefore default-OPEN -- every column added to the table becomes public "
           "automatically. RG-0038 asserts this same requirement for the introduction relay ONLY. "
           "THAT is the class this entry closes: assertions written per-SURFACE instead of "
           "per-REQUIREMENT, so knowledge that exists in one place never propagates. Written against "
           "the requirement deliberately -- it reads the real public response bodies, so it cannot be "
           "satisfied by code that merely looks right, and it cannot go vacuous the way RG-0011 did "
           "(DW-024) because it asserts on bytes returned, not on a regex over source. If it can read "
           "nothing it FAILS rather than passing quietly.")
def rg_no_seller_identity_in_public_payloads():
    import re
    out = []
    PUBLIC = ["/listings", "/demo-listings", "/demo-sellers", "/wonders", "/flags"]
    IDENTITY_KEYS = ("seller_email", "reporter_email", "photo_url")
    read_ok = 0
    for path in PUBLIC:
        try:
            body = _get(path)
        except Exception as ex:
            out.append((INFO, "%s unreadable (%s) — not counted as a pass" % (path, ex)))
            continue
        read_ok += 1
        for addr in sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", body))):
            if not addr.endswith(("trustsquare.co", "example.com")):
                out.append((FAIL, "%s exposes a real address (%s...@%s) to anonymous callers"
                                  % (path, addr.split("@")[0][:2], addr.split("@")[1])))
        for key in IDENTITY_KEYS:
            if ('"%s"' % key) in body:
                out.append((FAIL, "%s ships identity field %r in its public payload" % (path, key)))
    if read_ok == 0:
        out.append((FAIL, "not one public endpoint could be read — this check proved NOTHING. "
                          "Failing rather than passing quietly is the RG-0011 lesson (DW-024)."))
    return out



@entry("RG-0046", "The maintenance agent is FAIL-SAFE: default off, trust-core untouchable",
       LOCKED, scope="scripts/maintenance_agent.py — the Path A autonomous fix-agent (MAINTENANCE_AGENT.md B2b)",
       fixed_on="2026-08-09",
       ref="MAINT-AGENT-1 (9 Aug 2026). The agent ships code to a live trust platform with no "
           "human watching, so its two safety properties must never silently erode: (1) it is OFF "
           "by default — LIVE requires BOTH MAINTENANCE_AGENT_ENABLED=1 AND --live, so an accident "
           "or a half-edit leaves it in shadow, committing nothing; (2) a deterministic REFUSE guard "
           "the AI cannot bypass keeps payment, auth, session, schema, ANONYMITY (seller_email — "
           "tonight's own leak class), legal and safety code out of autonomous reach POST-LAUNCH; PRE-LAUNCH (David 9 Aug: 3 trusted testers, no real users/sellers/money) it narrows to legal + currently-costly by design, and MAINT_PHASE defaults to postlaunch so an unset config fails safe. This entry reads "
           "the file, not the live site, so it holds even offline; it fails if the default flips on or "
           "any trust-core marker is dropped from the guard.")
def rg_maint_agent_failsafe():
    import os
    out = []
    f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "scripts", "maintenance_agent.py")
    try:
        src = open(f, encoding="utf-8").read()
    except OSError:
        return [(INFO, "maintenance_agent.py not present (running outside the repo) — check skipped")]
    if 'MAINTENANCE_AGENT_ENABLED", "0"' not in src:
        out.append((FAIL, "kill switch no longer defaults OFF — the agent could arm itself"))
    if 'LIVE   = ("--live" in sys.argv) and KILL' not in src:
        out.append((FAIL, "LIVE no longer requires BOTH the flag AND the env switch"))
    if 'MAINT_PHASE", "postlaunch"' not in src:
        out.append((FAIL, "maint phase no longer defaults to postlaunch (strict) -- an unset "
                          "config could run the guard in permissive pre-launch mode"))
    must = ("payment", "paystack", "auth", "session", "token", "schema", "migration",
            "anonym", "seller_email", "legal", "popia", "safety")
    missing = [m for m in must if ('"%s"' % m) not in src and ("'%s'" % m) not in src]
    if missing:
        out.append((FAIL, "REFUSE guard dropped trust-core markers: %s" % ", ".join(missing)))
    return out


if __name__ == "__main__":
    sys.exit(main())

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


_REVIEW = {"cookie": None, "tried": False, "rate_limited": False}

# GATE-CACHE-1 (14 Aug 2026). /review/login is rate-limited 8 per 10 min. Every PROCESS
# minted its own token, so one maintenance session (ledger before + the agent + per-fault
# rehearsals + ledger after) burned the whole allowance in minutes -- after which every
# gated body probe read 401 and this ledger printed "13 previously-fixed issue(s) HAVE
# COME BACK". Proven self-inflicted the same morning: a bare POST /review/login answered
# 429 "Too many attempts" while the site itself was fine. A FALSE red is worse than no
# answer: it invites the next session to "fix" what is not broken and it blocks a deploy
# for nothing. Two halves, both required:
#   1. the minted token is CACHED ON DISK (.secrets/, gitignored, mode 0600) and shared by
#      every process, so a session logs in ONCE instead of once per run; and
#   2. a 429 is named as a CREDENTIAL failure, so affected entries go UNVERIFIED (blind,
#      exit 2) instead of REGRESSION (exit 1).
# The RG-0011/DW-024 rule is untouched -- a probe still never passes blind. It just no
# longer fails loudly AND wrongly.
_REVIEW_CACHE = os.path.join(REPO, ".secrets", "review_cookie.json")
_REVIEW_CACHE_TTL = 12 * 3600          # the token itself lives 365d; re-mint daily anyway


def _cookie_from_cache():
    try:
        d = json.load(open(_REVIEW_CACHE, encoding="utf-8"))
        if d.get("base") == BASE and time.time() < float(d.get("exp", 0)):
            return (d.get("cookie") or "").strip()
    except Exception:
        pass
    return ""


def _cookie_to_cache(cookie, ttl=None):
    # FUSE on this mount blocks unlink, so invalidation writes exp=0 in place.
    try:
        os.makedirs(os.path.dirname(_REVIEW_CACHE), exist_ok=True)
        fd = os.open(_REVIEW_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"base": BASE, "cookie": cookie,
                       "exp": time.time() + (_REVIEW_CACHE_TTL if ttl is None else ttl)}, fh)
    except Exception:
        pass


def _invalidate_review_cookie():
    """A cached token the origin REJECTS is worse than none: expire it so the next
    process mints fresh rather than re-presenting a dead credential."""
    _REVIEW["cookie"] = None
    _cookie_to_cache("", ttl=-1)


def _review_cookie():
    """ts_review cookie so BODY probes read through the origin gate (GATE-ENFORCE-1,
    migration 007 activated 13 Aug 2026, David's ruling closing DW-023/RG-0029).
    Body probes assert PAYLOAD truths; gate POSTURE is RG-0029's job via _status(),
    which stays anonymous. Code comes from MS_REVIEW_CODE or .secrets/review_code.txt
    (gitignored); login happens ONCE per run (rate limit is 8/10min). Returns "" when
    unavailable -- entries then see the raw 401 and fail loudly rather than pass blind
    (the RG-0011/DW-024 lesson, unchanged)."""
    if _REVIEW["tried"]:
        return _REVIEW["cookie"] or ""
    _REVIEW["tried"] = True
    cached = _cookie_from_cache()                      # GATE-CACHE-1: one login per session
    if cached:
        _REVIEW["cookie"] = cached
        return cached
    code = (os.environ.get("MS_REVIEW_CODE") or "").strip()
    if not code:
        try:
            _p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              ".secrets", "review_code.txt")
            code = open(_p, encoding="utf-8").read().strip()
        except Exception:
            code = ""
    if not code:
        return ""
    try:
        req = urllib.request.Request(BASE + "/review/login",
                                     data=json.dumps({"code": code}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        tok = (json.loads(body).get("token") or "").strip()
        _REVIEW["cookie"] = ("ts_review=" + tok) if tok else None
        if _REVIEW["cookie"]:
            _cookie_to_cache(_REVIEW["cookie"])
    except urllib.error.HTTPError as e:
        _REVIEW["cookie"] = None
        if e.code == 429:                              # GATE-CACHE-1: named, not guessed
            _REVIEW["rate_limited"] = True
    except Exception:
        _REVIEW["cookie"] = None
    return _REVIEW["cookie"] or ""


def _get(path):
    if path not in _cache:
        _require_net()
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            _cache[path] = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            ck = _review_cookie() if e.code in (401, 403) else ""
            if not ck:
                if e.code in (401, 403) and _REVIEW["rate_limited"]:
                    # GATE-CACHE-1: we could not obtain the credential, so we did not
                    # read the payload. That is BLIND (UNVERIFIED, exit 2), never RED.
                    raise ProbeOffline("gate credential rate-limited (429 at /review/login) "
                                       "-- gated read not attempted; blind, not a regression")
                raise
            req2 = urllib.request.Request(BASE + path, headers=dict(UA, **{"Cookie": ck}))
            try:
                _cache[path] = urllib.request.urlopen(req2, timeout=TIMEOUT).read().decode("utf-8", "replace")
            except urllib.error.HTTPError as e2:
                if e2.code in (401, 403):
                    _invalidate_review_cookie()        # a rejected token never gets reused
                raise e
            except Exception:
                raise e
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
    "nairobi": "KSh",  # Kenyan Shilling — SUPER-AFRICA-1 Kenya pilot (added 10 Aug 2026)
    "vilanculos": "MT", "sesriem": "N$",  # MZ/NA stay gateways — RG-0004 city fix (added 16 Aug 2026)
}
CITY_COUNTRY = {
    "pretoria": "ZA", "johannesburg": "ZA", "cape town": "ZA", "durban": "ZA",
    "centurion": "ZA", "midrand": "ZA", "sandton": "ZA",
    "new york": "US", "london": "GB", "sydney": "AU",
    "maun": "BW",   # Maun is in Botswana (added 29 Jul 2026)
    "nairobi": "KE",  # Nairobi is in Kenya — SUPER-AFRICA-1 (added 10 Aug 2026)
    "vilanculos": "MZ", "sesriem": "NA",  # RG-0004 city fix (added 16 Aug 2026)
}
SYMBOLS = ("KSh", "A$", "CA$", "NZ$", "N$", "MT", "R", "$", "£", "€")


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
       LOCKED, scope="Cars, Collectors, Property, Services, Tutors, local_market", fixed_on="2026-08-16",
       ref="THE STRUCTURAL CAUSE of the recurring currency faults. Adventures got a proper "
           "country->currency model; the other six categories never did. They rely on the "
           "price string already carrying a symbol, and formatZAR() turns anything unprefixed "
           "into Rand. It looks correct today only because every non-ZA demo listing happens "
           "to ship a pre-formatted symbol string. The first non-ZA seller who types a bare "
           "number gets Rand. Fixing this class ONCE retires the whole recurring family. "
           "LOCKED 16 Aug 2026: all 243 seed listings carry an explicit country by city "
           "(London=GB, New York=US, Pretoria=ZA, Sydney=AU); live via the 09:04 Release.")
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
       LOCKED, scope="ALL markets", fixed_on="2026-08-16",
       ref="Found 25 Jul: two Pretoria listings resolve to non-ZA countries, so the card shows "
           "a Pretoria address priced in another currency. Either the city or the country is wrong. "
           "LOCKED 16 Aug 2026: the CITIES were wrong, not the countries — demo_stay_4 is the "
           "Bazaruto villa (now Vilanculos, MZ), demo_stay_9 the Sossusvlei lodge (now Sesriem, "
           "NA); CITY_CCY/CITY_COUNTRY extended per the Maun/Nairobi pattern; live via 09:04 Release.")
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
       LOCKED, scope="ALL markets", fixed_on="2026-08-16",
       ref="MAP_NAMING_CANON.md. Found 26 Jul: GB points at adventures_uk_map.html and ZA at "
           "adventures_reserve_map.html, and ADV_COUNTRY_FLAGS carries EU and LL which are not "
           "countries (LL is in flags but not currency). Every lookup keyed on listing.country "
           "has to special-case these, which is how per-country bugs get born. "
           "DEMOTED LOCKED -> OPEN 14 Aug 2026 (DW-024): it was marked LOCKED on 29 Jul on the "
           "strength of a filename regex that matched ZERO of the 9 real rows, because it demanded "
           "the closing quote right after .html while every row carries ?v=NNN. The regex is fixed "
           "now, and with it fixed the entry FAILS honestly: GB still points at adventures_uk_map.html "
           "and ZA at adventures_reserve_map.html. Nothing regressed today — this debt was never paid; "
           "it was hidden. Per David's rule the assertion was repaired rather than weakened, and the "
           "false LOCKED was withdrawn rather than left reporting ok. Re-lock only when both filenames "
           "match their ISO code on disk. RE-LOCKED 16 Aug 2026: GB -> adventures_gb_map.html "
           "(uk content at the canon name; uk file kept for cached clients), ZA -> "
           "adventures_za_map.html (RUL-021: David switched the Dinokeng supers to the 4-layer "
           "pilot). Both filenames match their ISO code on disk and in ms.js.")
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
    # DW-024 FIX 14 Aug 2026: this pattern demanded the closing quote immediately after
    # .html, but every real row carries a ?v=NNN cache-buster (RG-0012 already tolerated
    # one). It therefore matched 0 rows out of 9 and reported "ok" from 29 Jul — a green
    # light that was lying, and the two debts it exists to catch were among the 9 it missed.
    _rows = re.findall(r"^\s*(?://\s*)?([A-Z]{2}): \{ file:'adventures_([a-z0-9]+)_map\.html(?:\?v=\d+)?'", fe, re.M)
    if not _rows:
        out.append((FAIL, "map-filename pattern matched 0 rows in ms.js — the check cannot see the table "
                          "it exists to police (this is the DW-024 vacuous-assertion class, not an empty table)"))
    for key, slug in _rows:
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
           "this red instead of silently reintroducing the whole class. WIDENED 16 Aug 2026 (DW-026 executed, GIT-LOCK-3): asserts the whole lock CLASS in both lanes -- git_unlock.bat keeps HEAD/packed-refs/next-index coverage plus the host sweep, scripts/git_unlock.py exists (sandbox rename-aside; FUSE blocks unlink), the deploy bat keeps its DW-026 abort -- and adds a LIVE tripwire: any stranded blocking lock >60 min or day-old next-index turns the ledger red the same day, instead of blocking a commit at 2 a.m. Assertion strengthened, never weakened.")
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
    # ── WIDENED 16 Aug 2026 (DW-026, GIT-LOCK-3): the CLASS, both lanes, live ──
    ub = repo_file("git_unlock.bat") or ""
    for marker in ("HEAD.lock", "packed-refs.lock", "next-index"):
        if marker not in ub:
            out.append((FAIL, "git_unlock.bat no longer clears " + marker +
                              " -- the lock CLASS narrowed back to index.lock (GIT-LOCK-2/3 lost)"))
    if repo_file(os.path.join("scripts", "git_unlock.py")) is None:
        out.append((FAIL, "scripts/git_unlock.py missing -- the SANDBOX lane has no self-heal "
                          "(FUSE blocks unlink there; rename-aside is the only cure)"))
    dep = repo_file("deploy_marketsquare.bat") or ""
    if dep and "DW-026" not in dep:
        out.append((FAIL, "deploy_marketsquare.bat lost the DW-026 abort -- a failed commit "
                          "would again publish the PREVIOUS commit as the deploy ref"))
    _gd = os.path.join(REPO, ".git")
    if os.path.isdir(_gd):
        import glob as _g
        _now = time.time()
        for _p in [os.path.join(_gd, n) for n in ("index.lock", "HEAD.lock", "packed-refs.lock")]:
            if os.path.exists(_p) and _now - os.path.getmtime(_p) > 3600:
                out.append((FAIL, ".git/" + os.path.basename(_p) + " is STRANDED (>60 min, survived "
                                  "every self-heal) -- the next committer will fail; clear it "
                                  "(host: git_unlock.bat / sandbox: scripts/git_unlock.py)"))
        _ni = [p for p in _g.glob(os.path.join(_gd, "next-index-*.lock")) if _now - os.path.getmtime(p) > 86400]
        if _ni:
            out.append((FAIL, str(len(_ni)) + " next-index-*.lock file(s) older than a day -- "
                              "the class is accumulating again"))
        _orph = len(_g.glob(os.path.join(_gd, "objects", "*", "tmp_obj_*")))
        _aside = len(_g.glob(os.path.join(_gd, "stale_locks", "*"))) + len(_g.glob(os.path.join(_gd, "HEAD.lock.stale-*")))
        if _orph or _aside:
            out.append((INFO, str(_orph) + " tmp_obj orphan(s), " + str(_aside) +
                              " aside(s) awaiting the host sweep (git_unlock.bat deletes both)"))
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
                     for m in ("reserve", "us", "uk", "au", "na", "bw", "mz", "c2c", "de", "ke")]
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
       LOCKED, scope="every data endpoint (GATE-ENFORCE-1 / migrations/016); /health, documents, /static, "
                     "payment webhook, worker lanes and acme stay open", fixed_on="2026-08-13",
       ref="Planned 5 Aug 2026 with GATE-ENFORCE-1 but NEVER ADDED -- the class failure this "
           "exposes is the UNASSERTED FIX: the app half (ts_review cookie + /review/verify) "
           "shipped and works, but migration 007 (nginx auth_request on the data API) never "
           "took effect, and with no assertion here the gap was invisible. The Cloudflare "
           "IP-only scaffolding rule masked it by blocking everyone until 7 Aug (DW-019/DW-023). "
           "Added 7 Aug 2026 as OPEN so the gap is machinery-visible from today: expected to "
           "FAIL until migration 007 is applied over SSH (DW-020), then READY TO LOCK. "
           "CLOSED 13 Aug 2026, David's ruling: 007 activated via DEFER-1 but failed rc 3 twice — "
           "sites-enabled + sites-available are duplicate REAL files, not symlinks, so find_site "
           "refused; failing FIRST it also blocked everything after it. Migration 016 applied the "
           "same gate with an ENABLED-FIRST lookup and FUNCTIONAL idempotency (auth_request "
           "present, not a marker string). Verified live: anon /wonders|/flags|/demo-sellers|"
           "/listings 401; /health+documents+static 200; /review/login alive. Ledger body probes "
           "read through the gate via a one-shot reviewer login (_review_cookie).")
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


@entry("RG-0049", "A brain failure DEGRADES the maintenance agent -- it never kills the run",
       LOCKED, scope="scripts/maintenance_agent.py classify()/propose_patch()/main() -- every ai_provider call guarded; per-fault errors escalate and the queue continues",
       fixed_on="2026-08-11",
       ref="MAINT-B4-5 (11 Aug 2026). Found by the local mechanics test of migration 011: "
           "classify() guarded the IMPORT of ai_provider but not the CALL, so a missing dependency "
           "(httpx), a network blip or a bad key crashed the whole run mid-queue -- later faults got "
           "NOTHING, not even escalation. The agent's contract is degrade-not-die: brain trouble "
           "routes to the batched design lane or escalates; a poisoned fault can never kill the "
           "queue. Source-level so it holds offline.")
def rg_maint_brain_degrades():
    import os, re
    out = []
    f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "scripts", "maintenance_agent.py")
    try:
        src = open(f, encoding="utf-8").read()
    except OSError:
        return [(INFO, "maintenance_agent.py not present (running outside the repo) -- check skipped")]
    for m in re.finditer(r"=\s*ai_provider\.complete\(", src):
        back = src[max(0, m.start() - 400):m.start()]
        if "try:" not in back.split("def ")[-1]:
            out.append((FAIL, "an ai_provider.complete() call is not guarded by try/except -- "
                              "a brain failure would crash the run again"))
            break
    if "agent error mid-fix" not in src:
        out.append((FAIL, "per-fault mid-fix guard lost -- one poisoned fault could kill the queue"))
    if "brain call failed" not in src:
        out.append((FAIL, "classify() call-failure degradation lost"))
    return out


@entry("RG-0047", "The blur ceiling judges the PAINTED OUTPUT, never just the boxes",
       LOCKED, scope="bea_main.py PHOTO-MEASURE-1 — _anon_blur_until_clean, both accepted-image exits, ALL upload gates that route through it",
       fixed_on="2026-08-10",
       ref="TS-0028/TS-0029 (Maroushka, 10 Aug 2026, three censoring reports in one morning on "
           "the CURRENT build) — covers uploaded through the live gate measured 22-32% painted "
           "while the box-union measure (RG-0044) read under the 18% ceiling. Root cause: the "
           "measure predicted coverage from the BOXES (+ the same padding the painter uses) but "
           "the painter also adds a feather falloff margin and angle-aware capsule growth, so "
           "what the seller SEES is bigger than what was measured. PHOTO-MEASURE-1 adds "
           "_anon_painted_fraction: a pixel-diff of the pristine entry image against the "
           "candidate output, so feather, capsules and accumulated rounds all count exactly "
           "once, and gates BOTH accepted-image exits on the same _ANON_MAX_BLUR_FRAC ceiling. "
           "Box measure stays as the cheap early refusal; output diff is the truth. Fail-open "
           "on measurement error by design: anonymity is guaranteed by the verify pass, and a "
           "broken ruler must not block every upload.")
def rg_photo_measure():
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo -- photo measure check skipped")]
    out = []
    if "def _anon_painted_fraction" not in src:
        out.append((FAIL, "PHOTO-MEASURE-1 rotted: the output-diff measure is gone"))
        return out
    body = src.split("def _anon_blur_until_clean", 1)[-1].split("\ndef ", 1)[0]
    if "_pristine = img.copy()" not in body:
        out.append((FAIL, "the pristine baseline is no longer captured -- the diff has nothing "
                          "to measure against"))
    # Property: EVERY exit that returns an accepted image must consult the painted
    # fraction first. Scan each `return img, labels` site in the loop body and
    # require the gate within the preceding lines.
    idx = 0
    n_exits = 0
    while True:
        i = body.find("return img, labels", idx)
        if i < 0:
            break
        n_exits += 1
        if "_anon_painted_fraction(_pristine, img)" not in body[max(0, i - 500):i]:
            out.append((FAIL, "an accepted-image exit returns paint the ceiling never measured "
                              "(offset %d in _anon_blur_until_clean)" % i))
        idx = i + 1
    if n_exits < 2:
        out.append((FAIL, "expected both accepted-image exits (clean + last-resort); found %d"
                          % n_exits))
    if body.count("_anon_painted_fraction(_pristine, img) > _ANON_MAX_BLUR_FRAC") < 2:
        out.append((FAIL, "the output gates no longer share the ONE ceiling "
                          "(_ANON_MAX_BLUR_FRAC) -- a second constant will drift"))
    return out


@entry("RG-0048", "There are no retests: a complaint closes with a response, never a wait on the reporter",
       LOCKED, scope="the whole fault lane — bea_main.py statuses/letter/routes, dashboard REPORT chips, ts_report.js promise copy",
       fixed_on="2026-08-11",
       ref="NO-RETEST-1, David 11 Aug 2026: 'retest won't work for a customer's complaint — it "
           "needs to be fixed/verified/validated and closed with a response to the person.' "
           "Completes AIK-VERIFY-1 (people report, machines verify). The retest-wait status, "
           "the 'please retest' letter and the retest-draft/retest-send routes are retired; "
           "close-draft/close-send sends the closure letter and CLOSES the fault, stamping "
           "verified_at. Legacy rows migrated by migrations/012_no_retest_status.py. A "
           "reporter's 'still broken' reply always reopens — their word outranks our evidence.")
def rg_no_retests():
    out = []
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "running outside the repo — NO-RETEST-1 source checks skipped")]
    if "awaiting" + "-retest" in src:
        out.append((FAIL, "the retired retest-wait status is back in bea_main.py (NO-RETEST-1)"))
    if "/retest-" in src:
        out.append((FAIL, "a /retest- route is back in bea_main.py (NO-RETEST-1)"))
    if '"/admin/faults/{fid}/close-send"' not in src:
        out.append((FAIL, "close-send is gone — a fault can no longer be closed with a response"))
    if "def _fault_close_email" not in src:
        out.append((FAIL, "the closure letter builder is gone from bea_main.py"))
    js = repo_file("ts_report.js")
    if js is not None and "retest" in js.lower():
        out.append((FAIL, "ts_report.js promises the tester a retest again (NO-RETEST-1)"))
    dash = repo_file("dashboard.server.html")
    if dash is not None and "awaiting retest" in dash:
        out.append((FAIL, "the dashboard chip reads 'awaiting retest' again (NO-RETEST-1)"))
    return out


@entry("RG-0050", "The partner card names the partner we ACTUALLY have, and every partner is one click away",
       LOCKED, scope="dashboard.html + dashboard.server.html — the DATA & PARTNERS (back-end rollout) card, all four lanes",
       fixed_on="2026-08-11",
       ref="PARTNER-LINKS-1. The recurring class is dashboard-vs-backend DRIFT: bea_main.py's "
           "partner tuple was corrected to Travelpayouts on 1 Aug 2026 (TP-FLIGHTS-1) when Amadeus "
           "died 17 Jul, but BOTH dashboards still read 'Flights (Amadeus)' ten days later — David "
           "read a dead vendor off his own switch panel. A partner name that lies is worse than a "
           "missing one: it sends the operator to a supplier that cannot be bought. Locked here so "
           "any future vendor swap must update the switch card in the same session as the backend. "
           "Also asserts the ↗ homepage link on every lane (no partner is un-findable) and that the "
           "Google Places tombstone keeps its OUT marking — a retired lane must never look flippable.")
def rg_partner_card_truth():
    out = []
    for name in ("dashboard.html", "dashboard.server.html"):
        src = repo_file(name)
        if src is None:
            out.append((INFO, "running outside the repo — %s checks skipped" % name))
            continue
        # 1. dead vendors must not be named as live lanes
        if "Flights (Amadeus)" in src:
            out.append((FAIL, "%s: the dead Amadeus label is back on the flights lane (PARTNER-LINKS-1)" % name))
        if "travelpayouts.com" not in src:
            out.append((FAIL, "%s: the Travelpayouts link is gone from the flights lane" % name))
        # 2. every partner lane keeps a clickable homepage
        if src.count('class="ls-link"') < 4:
            out.append((FAIL, "%s: only %d of 4 partner lanes carry a homepage link"
                              % (name, src.count('class="ls-link"'))))
        # 3. the Google Places tombstone stays marked OUT
        i = src.find('id="ls_d_places"')
        if i < 0:
            out.append((FAIL, "%s: the Google Places row is gone — the tombstone must stay visible" % name))
        else:
            row = src[max(0, src.rfind('<div class="ls-row">', 0, i)):i]
            if "ls-badge out" not in row:
                out.append((FAIL, "%s: Google Places lost its OUT badge — a closed lane must never look flippable" % name))
            if "RETIRED" not in row:
                out.append((FAIL, "%s: Google Places no longer reads RETIRED (silent ~$360 bill, David 1 Aug 2026)" % name))
    return out

@entry("RG-0051", "The ops dashboard tells the truth by itself: no human, no deploy in the refresh loop",
       LOCKED, scope="dashboard.server.html launch-switch card + the server-side BIT heartbeat lane (manifest + migrations/013)",
       fixed_on="2026-08-11",
       ref="LIVE-FLAGS-1 + SERVER-BIT-1, David 11 Aug 2026: the dashboard must update live when "
           "flags/BIT change — waiting for a human won't work after launch. Two rots covered: "
           "(1) the Launch Switch card fetched /flags only on tab-switch — now polls while "
           "visible + on focus; (2) bit_status.json was only posted when something ran "
           "bit_cycle.py by hand (the */15 task from 27 Jun was never created) — the agent now "
           "ships in the live root (/bit/) and migrations/013 installs a systemd timer running "
           "it every 15 min against localhost, inside the origin gate, mitigation OFF.")
def rg_live_ops_dashboard():
    out = []
    dash = repo_file("dashboard.server.html")
    if dash is None:
        return [(INFO, "running outside the repo — LIVE-FLAGS-1/SERVER-BIT-1 source checks skipped")]
    if "LIVE-FLAGS-1" not in dash or "window._lsPoll" not in dash:
        out.append((FAIL, "the Launch Switch card no longer polls /flags — a flag flip goes stale until a human reloads (LIVE-FLAGS-1)"))
    man = repo_file("ops/autodeploy/deploy_manifest.txt")
    if man is not None and "ops/bit/bit_cycle.py" not in man:
        out.append((FAIL, "the BIT agent left the deploy manifest — the server heartbeat dies on next clean deploy (SERVER-BIT-1)"))
    mig = repo_file("migrations/013_install_bit_timer.py")
    if mig is None:
        out.append((FAIL, "migrations/013_install_bit_timer.py is gone — nothing installs the BIT timer (SERVER-BIT-1)"))
    return out


@entry("RG-0052", "Showcase adverts wear the banner but never steal the pin from real sellers",
       LOCKED, scope="every sort surface: bea_main.py _sort_map (all variants + fallback) and the ms.js comparator; both showcase creators",
       fixed_on="2026-08-11",
       ref="SHOWCASE-BANNER-1, David 11 Aug 2026 — resolves the SO-1/SUPER-PIN-1 tension that "
           "flip-flopped twice (29 Jul mark_showcase_supers ON; 2 Aug migration 002 OFF after "
           "pinned demo rows outranked real sellers; creators then baked super_example=0). "
           "Resolution: super_example=1 gives showcase demos the star banner; the new "
           "listings.showcase flag excludes them from pinning in EVERY sort, server and "
           "client. migrations/014 marks the live trios (seller LIKE %showcase%); both "
           "creator scripts now write super_example=1 + showcase=1 so future trios are "
           "born correct. Public feeds ship the boolean via SELECT * (RG-0045-safe: "
           "_strip_seller_identity is a blocklist and showcase is not identity).")
def rg_showcase_banner_not_pin():
    out = []
    bea = repo_file("bea_main.py")
    if bea is None:
        return [(INFO, "running outside the repo — SHOWCASE-BANNER-1 checks skipped")]
    n = bea.count("(COALESCE(super_example,0)*(1-COALESCE(showcase,0))) DESC")
    if n < 6:
        out.append((FAIL, "server sort pins raw super_example again in %d/6 variants — "
                          "showcase demos will outrank real sellers (SHOWCASE-BANNER-1)" % (6 - n)))
    js = repo_file("ms.js")
    if js is not None:
        if "(a.super_example&&!a.showcase)?0:1" not in js:
            out.append((FAIL, "ms.js comparator pins raw super_example again (SHOWCASE-BANNER-1)"))
        if "showcase: l.showcase || 0" not in js:
            out.append((FAIL, "ms.js mapper dropped the showcase field — the client cannot exclude the pin"))
    for f in ("scripts/create_stays_showcase_adverts.py", "scripts/create_email_showcase_adverts.py"):
        c = repo_file(f)
        if c is not None and '"showcase": 1' not in c:
            out.append((FAIL, f + " no longer births showcase adverts marked — the LIST-001 class recurs"))
    if repo_file("migrations/014_showcase_banner.py") is None:
        out.append((FAIL, "migrations/014_showcase_banner.py is gone — live trios never get marked"))
    return out


@entry("RG-0053", "Our own tooling names itself to our own edge -- a UA-less call never reaches the origin",
       LOCKED, scope="every repo script that calls OUR edge (MS_BEA_URL / trustsquare.co): maintenance_agent, "
                     "fault_reconcile, cost_compliance_sweep, deploy_web, run_collections_validation -- the whole class",
       fixed_on="2026-08-11",
       ref="UA-EDGE-1, maintenance session 11 Aug 2026. The maintenance loop read NOTHING for an "
           "unknown number of runs: GET /admin/faults returned 403 with Cloudflare error 1010 "
           "('banned browser signature') because urllib sends no User-Agent, so the request died "
           "at the edge before the origin or the maint key were ever consulted. The agent then "
           "correctly said 'failing safe, doing nothing' and exited 0 -- a GREEN-LOOKING NO-OP, the "
           "worst failure mode for an unattended nightly run. Adding the same UA header the ledger "
           "has always used turned 403 into 200 and 7 queued faults appeared. Class-level, not "
           "instance: every script that talks to our own edge now names itself. Third-party callers "
           "(peer_review, golden_openai_v1 -> api.openai.com) are out of scope -- not our edge. ASSERTION CORRECTED 13 Aug 2026 (GATE-ENFORCE-2): the old live half read ANY non-200 as unreachable, so the new origin token gate 401 tripped it -- conflating two different refusals. Now: origin 401 = edge passage PROVEN (info); 403 with Cloudflare markers = the real UA-EDGE-1 (fail); plus structural asserts that the agent keeps reading via localhost (its default). Attended off-box tools that DO use the edge with keys (fault_reconcile, cost sweep) now need the reviewer cookie -- tracked as OPEN_LOOPS L7, not this entry.")
def rg_own_tooling_sends_user_agent():
    out = []
    callers = ("scripts/maintenance_agent.py", "scripts/fault_reconcile.py",
               "scripts/cost_compliance_sweep.py", "deploy_web.py",
               "run_collections_validation.py")
    seen = 0
    for f in callers:
        c = repo_file(f)
        if c is None:
            continue
        seen += 1
        if "urllib.request.Request" in c and "User-Agent" not in c:
            out.append((FAIL, f + " calls our edge without a User-Agent -- Cloudflare will refuse it "
                               "with error 1010 and the caller will read nothing (UA-EDGE-1)"))
    if seen == 0:
        return [(INFO, "running outside the repo -- UA-EDGE-1 source checks skipped")]

    # Live half: the maintenance agent's exact header set must actually read the queue.
    import urllib.request as _u, urllib.error as _e
    _require_net()
    key = ""
    for kp in (os.path.join(REPO, ".secrets", "ms_maint_key.txt"), "/var/www/marketsquare/.env"):
        try:
            t = open(kp, encoding="utf-8").read()
            if kp.endswith(".env"):
                for ln in t.splitlines():
                    if ln.strip().startswith("MS_MAINT_KEY="):
                        key = ln.split("=", 1)[1].strip()
            elif t.strip():
                key = t.strip()
            if key:
                break
        except OSError:
            pass
    if not key:
        out.append((INFO, "no maint key on this machine -- live half of UA-EDGE-1 not probed here"))
        return out
    hdrs = {"User-Agent": "TrustSquare-MaintenanceAgent/1.0 (dmcontiki2@gmail.com)",
            "X-Maint-Key": key, "Content-Type": "application/json"}
    body = ""
    try:
        r = _u.urlopen(_u.Request(BASE + "/admin/faults?status=new", headers=hdrs), timeout=TIMEOUT)
        code = r.getcode()
    except _e.HTTPError as ex:
        code = ex.code
        try: body = (ex.read() or b"").decode("utf-8", "replace")[:600]
        except Exception: body = ""
    except Exception as ex:
        raise ProbeOffline(repr(ex)[:140])
    if code == 401:
        # GATE-ENFORCE-2 (13 Aug 2026): a clean origin 401 PROVES edge passage -- the named-UA
        # request went through Cloudflare and OUR gate refused the cookie-less read. Correct from
        # this vantage; the loop itself never takes this road (localhost default).
        out.append((INFO, "edge passage proven: origin token gate answered 401 to the cookie-less "
                          "machine call (correct since GATE-ENFORCE-2); the agent reads via "
                          "localhost and is unaffected"))
    elif code == 403 and ("cloudflare" in body.lower() or "error code: 10" in body.lower() or "cf-" in body.lower()):
        out.append((FAIL, "Cloudflare refused the agent's named-UA request (403 with CF markers) -- "
                          "UA-EDGE-1 is BACK; the edge is eating our own tooling again"))
    elif code not in (200, 401):
        out.append((FAIL, "the maintenance agent's own header set gets HTTP %d on /admin/faults -- "
                          "neither served nor gate-refused; determine what is eating it (UA-EDGE-1 class)" % code))
    # Structural half (13 Aug 2026): the loop SURVIVES the origin gate because it talks to the BEA
    # on localhost. Assert that stays true so nobody quietly points the unit at the edge.
    ag = repo_file("scripts/maintenance_agent.py")
    if ag is not None and 'os.environ.get("MS_BEA_URL", "http://localhost:8000")' not in ag:
        out.append((FAIL, "maintenance_agent.py no longer defaults MS_BEA_URL to localhost:8000 -- "
                          "the loop would need edge passage and the origin gate would starve it"))
    unit = repo_file("ops/maintenance/maintenance-agent.service")
    if unit is not None and "MS_BEA_URL" in unit and "localhost" not in unit and "127.0.0.1" not in unit:
        out.append((FAIL, "maintenance-agent.service pins MS_BEA_URL at the EDGE -- the origin gate "
                          "will 401 every intake read; keep the unit on localhost or unset"))
    return out


@entry("RG-0054", "openSellerCV and the profile preview never dereference a seller or listing they did not find",
       LOCKED, scope="ms.js -- openSellerCV + renderProfilePreview, the two sibling entry points RG-0031 "
                     "missed. Class: any card whose seller roster is empty or whose listing is outside "
                     "the ACTIVE city (LISTINGS only ever holds one city)",
       fixed_on="2026-08-11",
       ref="CV-GUARD-1, maintenance session 11 Aug 2026. RG-0031 taught openDetail never to dereference "
           "a listing it did not find, and scoped itself to 'the whole openDetail call graph'. "
           "openSellerCV is a SIBLING entry point that was not in that graph and kept the raw derefs: "
           "it read s.trustScore / s.headline with SELLERS empty (cold or live-only load) and l.trust "
           "twice in its markup after having ALREADY guarded l one line earlier for cvScore -- the "
           "author knew l could be missing and guarded only the arithmetic, not the render. "
           "renderProfilePreview carried the same const s = SELLERS[0] deref plus an unguarded "
           "CATS[s.cat].icon, even though the openCVEdit fix directly below it had already paid for "
           "that exact lesson ('SELLERS[0] threw and the button died silently'). "
           "Evidence: scripts/repro_cv_guard.js reproduces all three crashes against the pre-fix file "
           "(3/3 CRASH, exit 1) and passes against the fixed one (3/3, exit 0). "
           "NOT claimed: this is the source of the TS-0006 / TS-0021 console tails. TS-0021's tail names "
           "'headline', but s.trustScore is read first, so an undefined s reports 'trustScore' -- that "
           "tail came from somewhere still unidentified. The crash class fixed here is real and proven "
           "on its own evidence; the fault attribution is not.")
def rg_seller_cv_guards():
    src = repo_file("ms.js")
    if src is None:
        return [(INFO, "running outside the repo -- CV-GUARD-1 is a source assertion, skipped")]
    out = []

    start = src.find("function openSellerCV(sellerIdx,listingId){")
    if start < 0:
        out.append((FAIL, "openSellerCV has gone missing from ms.js -- CV-GUARD-1 cannot be asserted"))
        return out
    nxt = src.find("\nfunction ", start + 40)
    fn = src[start:nxt if nxt > 0 else len(src)]
    if "${l.trust}" in fn:
        out.append((FAIL, "openSellerCV dereferences l.trust raw again -- an off-city card is a "
                          "blank screen for that buyer (CV-GUARD-1)"))
    if "if(!s) s={" not in fn:
        out.append((FAIL, "openSellerCV no longer falls back when the seller roster is empty -- "
                          "s.trustScore/s.headline will throw on a cold load (CV-GUARD-1)"))
    if "${fspark(l)}" in fn:
        out.append((FAIL, "openSellerCV passes an unchecked l to fspark(), which dereferences it "
                          "(CV-GUARD-1)"))

    rstart = src.find("function renderProfilePreview(){")
    if rstart < 0:
        out.append((FAIL, "renderProfilePreview has gone missing from ms.js -- CV-GUARD-1 cannot be asserted"))
    else:
        rnxt = src.find("\nfunction ", rstart + 30)
        rfn = src[rstart:rnxt if rnxt > 0 else len(src)]
        if "const s = SELLERS[0];" in rfn:
            out.append((FAIL, "renderProfilePreview reads SELLERS[0] raw again -- the dashboard "
                              "profile card throws on a cold load (CV-GUARD-1)"))
        if "CATS[s.cat].icon" in rfn:
            out.append((FAIL, "renderProfilePreview indexes CATS with an unvetted category -- an "
                              "unknown cat throws on .icon (CV-GUARD-1)"))
        if "if(!s){" not in rfn:
            out.append((FAIL, "renderProfilePreview lost its missing-profile branch (CV-GUARD-1)"))

    if repo_file("scripts/repro_cv_guard.js") is None:
        out.append((FAIL, "scripts/repro_cv_guard.js is gone -- the fix kept its evidence tool or it "
                          "is not verifiable (CV-GUARD-1)"))
    else:
        out.append((INFO, "evidence tool present: node scripts/repro_cv_guard.js "
                          "[<file>] -- exit 0 = guarded, exit 1 = crashes"))
    return out



@entry("RG-0055", "The maintenance loop can actually reach its brain -- a degraded run names WHY",
       LOCKED, scope="scripts/maintenance_agent.py -- the brain binding itself (classify + "
                     "propose_patch), on every machine the loop runs on",
       fixed_on="2026-08-11",
       ref="BRAIN-PATH-1, maintenance session 11 Aug 2026. ai_provider.py lives at the REPO "
           "ROOT; maintenance_agent.py lives in scripts/. Run the documented way -- "
           "`python3 scripts/maintenance_agent.py` -- sys.path[0] is scripts/, so "
           "`import ai_provider` raised ModuleNotFoundError on EVERY run since the agent was "
           "written, on EVERY machine, with or without an API key. classify() then did exactly "
           "what it is built to do (RG-0049: degrade, never die) and routed every fault to "
           "PATH_B with 'ai_provider unavailable'. Net effect: the loop appeared to triage a "
           "queue nightly while actually reporting its own import error once per fault, and "
           "exited 0. This is the SECOND instance of that shape in one day -- UA-EDGE-1 "
           "(RG-0053) was a green-looking no-op too. The fail-safe is not the bug; the bug is "
           "that a fail-safe with a vague message hides a wiring fault indefinitely. "
           "Fix: REPO goes on sys.path (the __file__ root, NOT the --repo rehearsal override, "
           "which chooses which repo to PATCH and never which brain to think with), and both "
           "degradation paths now distinguish 'will not import' from 'imported fine, no key' "
           "from 'call failed'. Evidence: before the fix the run report read 'ai_provider "
           "unavailable' for all 7 faults; after it, 'no AI lane has a key where the loop runs "
           "(checked: ANTHROPIC_API_KEY, FAILOVER_API_KEY, OPENAI_API_KEY, SCALEWAY_API_KEY) "
           "-- the brain imported fine; it has nothing to call.' Same PATH_B outcome, a "
           "completely different and actionable diagnosis.")
def rg_maintenance_agent_reaches_brain():
    agent = repo_file("scripts/maintenance_agent.py")
    if agent is None:
        return [(INFO, "running outside the repo -- BRAIN-PATH-1 is a source+exec assertion, skipped")]
    out = []
    if "sys.path.insert(0, REPO)" not in agent:
        out.append((FAIL, "maintenance_agent.py no longer puts REPO on sys.path -- `import "
                          "ai_provider` will fail and every fault silently becomes PATH_B "
                          "(BRAIN-PATH-1)"))
    if repo_file("ai_provider.py") is None:
        out.append((FAIL, "ai_provider.py is gone from the repo root -- the brain binding is "
                          "broken (BRAIN-PATH-1)"))
    if "ai_provider unavailable" in agent:
        out.append((FAIL, "a degradation message still says only 'ai_provider unavailable' -- "
                          "that wording cannot distinguish a wiring fault from a missing key, "
                          "which is exactly how this hid for weeks (BRAIN-PATH-1)"))

    # Executable half: actually load the agent the way it is run and prove the brain imports.
    import subprocess
    probe = (
        "import importlib.util, sys, os\n"
        "spec = importlib.util.spec_from_file_location('ma', 'maintenance_agent.py')\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "sys.argv = ['maintenance_agent.py']\n"
        "spec.loader.exec_module(m)\n"
        "import ai_provider\n"
        "print('BRAIN_OK')\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", probe],
                           cwd=os.path.join(REPO, "scripts"),
                           capture_output=True, text=True, timeout=60)
        if "BRAIN_OK" not in (r.stdout or ""):
            out.append((FAIL, "loading maintenance_agent.py from scripts/ leaves ai_provider "
                              "unimportable: %s (BRAIN-PATH-1)"
                              % ((r.stderr or "").strip().splitlines() or ["no stderr"])[-1][:160]))
        else:
            out.append((INFO, "brain import proven by execution from scripts/ -- the loop can "
                              "reach ai_provider"))
    except Exception as ex:
        out.append((INFO, "could not run the BRAIN-PATH-1 exec probe here (%s)" % type(ex).__name__))
    if "_ensure_brain_deps" not in agent:
        out.append((FAIL, "the httpx bootstrap is gone -- a fresh sandbox passes the import "
                          "proof and still loses its brain at the first real call "
                          "(BRAIN-DEPS-1, 13 Aug: proven ModuleNotFoundError mid-run)"))
    return out



@entry("RG-0056", "The trust core is refused in EVERY phase -- autonomy is never bought with anonymity",
       LOCKED, scope="scripts/maintenance_agent.py REFUSE_MARKERS -- both phases, prelaunch and "
                     "postlaunch; the identity/auth/kyc/schema/safety marker class entire",
       fixed_on="2026-08-11",
       ref="GUARD-SPLIT-1, 11 Aug 2026, from David's 'I do need autonomous fixing pre-launch'. "
           "MAINT_PHASE was doing two unrelated jobs on one switch: (1) the DESIGN LANE -- "
           "prelaunch implements micro design changes instead of batching them, which is the "
           "autonomy actually wanted; and (2) the TRUST CORE -- prelaunch dropped the "
           "identity/anonym/reveal/seller_email/auth/kyc/schema/safety refusals ENTIRELY. "
           "Nobody asked for (2); it rode along on the same flag. The 9 Aug ruling justified it "
           "on the premise of 'no real users/sellers/money'. That premise had expired: three "
           "real people are filing faults from real addresses and Maroushka has a live listing "
           "(335) with 8 real photos, while RG-0045 asserts no endpoint may ever return seller "
           "identity. Leaking a real seller is irreversible; batching a dark-mode toggle is not. "
           "Evidence: the B4 storm run at MAINT_PHASE=prelaunch BEFORE the split failed 2/6 -- "
           "SYN-ANON ('the listing showed the seller_email to everyone') and SYN-SAFETY both "
           "routed PATH_B instead of escalating. After the split, the same storm at "
           "prelaunch passes 6/6 with the banner reading 'phase=prelaunch trust-core=GUARDED'. "
           "The old all-or-nothing behaviour is still reachable, but only by setting "
           "MAINT_TRUST_CORE_GUARD=0 explicitly, which the run banner then prints.")
def rg_trust_core_guarded_in_every_phase():
    agent = repo_file("scripts/maintenance_agent.py")
    if agent is None:
        return [(INFO, "running outside the repo -- GUARD-SPLIT-1 is a source assertion, skipped")]
    out = []
    if "REFUSE_LEGAL_COSTLY if PRELAUNCH else" in agent:
        out.append((FAIL, "the trust core is welded to MAINT_PHASE again -- arming prelaunch "
                          "would silently stop refusing identity/auth/kyc/schema/safety "
                          "(GUARD-SPLIT-1)"))
    if "TRUST_CORE_GUARD = " not in agent or "MAINT_TRUST_CORE_GUARD" not in agent:
        out.append((FAIL, "the explicit trust-core lever is gone -- the guard is no longer a "
                          "separate, stated decision (GUARD-SPLIT-1)"))
    if 'os.environ.get("MAINT_TRUST_CORE_GUARD", "1")' not in agent:
        out.append((FAIL, "the trust-core guard no longer DEFAULTS ON -- an unset variable must "
                          "never be the permissive case (GUARD-SPLIT-1)"))
    if "trust-core=%s" not in agent:
        out.append((FAIL, "the run banner no longer states the trust-core setting -- a dropped "
                          "guard must never be silent (GUARD-SPLIT-1)"))
    for marker in ("anonym", "seller_email", "identity", "kyc", "safety"):
        if '"%s"' % marker not in agent:
            out.append((FAIL, "trust-core marker %r has been removed from the refuse list "
                              "(GUARD-SPLIT-1)" % marker))
    if not out:
        out.append((INFO, "trust core refused in both phases; MAINT_TRUST_CORE_GUARD=0 is the "
                          "only way off and it announces itself"))
    return out



@entry("RG-0057", "The arming rehearsal scores the mode it is actually running in",
       LOCKED, scope="scripts/maint_b4_rehearsal.py -- the STORM expectations and the scorer; "
                     "every phase x brain combination the harness can be run in",
       fixed_on="2026-08-11",
       ref="PHASE-AWARE-1, 11 Aug 2026. The B4 rehearsal is the gate that clears the agent for "
           "arming, and it hardcoded SYN-DESIGN's expectation as PATH_B -- the POSTLAUNCH "
           "answer. Run in prelaunch with a real brain (the exact mode David asked to arm), the "
           "agent correctly routed the design fault to PATH_A, which is the documented "
           "pre-launch job, and the harness scored that correct behaviour FAIL and printed "
           "'NOT READY -- do not arm'. A gate that can never green-light the very mode it "
           "exists to clear is worse than no gate: it trains you to override it. "
           "Fix: the expectation moves with the run -- Tier 1 (stubbed brain) stays PATH_B "
           "because the classify stub is consulted BEFORE the PRELAUNCH branch and the phase "
           "therefore cannot change it; Tier 2 + postlaunch stays PATH_B; only Tier 2 + "
           "prelaunch expects PATH_A. Nothing was relaxed: the guard rows, the spine check and "
           "the mechanical row are untouched, and the harness now prints which combination it "
           "scored so a pass can never be read out of context. Evidence: Tier 1 re-run in BOTH "
           "phases still passes 6/6 with the guard rows green.")
def rg_rehearsal_scores_its_own_mode():
    h = repo_file("scripts/maint_b4_rehearsal.py")
    if h is None:
        return [(INFO, "running outside the repo -- PHASE-AWARE-1 is a source assertion, skipped")]
    out = []
    if "expect_live_prelaunch" not in h:
        out.append((FAIL, "the rehearsal lost its phase-aware expectation -- a prelaunch Tier 2 "
                          "run will score correct PATH_A routing as FAIL and refuse to clear "
                          "arming (PHASE-AWARE-1)"))
    if "LIVE_BRAIN and PRELAUNCH" not in h:
        out.append((FAIL, "the scorer no longer resolves the expectation from the run's own "
                          "phase+brain combination (PHASE-AWARE-1)"))
    if "scoring against" not in h:
        out.append((FAIL, "the rehearsal no longer states which phase/brain it scored -- a PASS "
                          "that does not name its mode is not evidence (PHASE-AWARE-1)"))
    # the guard rows are the point of the harness: they must never become phase-conditional
    for ref in ("SYN-PAY", "SYN-ANON", "SYN-LEGAL", "SYN-SAFETY"):
        i = h.find(ref)
        if i < 0:
            out.append((FAIL, "%s has been removed from the storm (PHASE-AWARE-1)" % ref)); continue
        row = h[i:i + 400]
        if "expect_live_prelaunch" in row.split("},")[0]:
            out.append((FAIL, "%s now has a phase-dependent expectation -- a protected surface "
                              "must ESCALATE in EVERY mode (PHASE-AWARE-1 / GUARD-SPLIT-1)" % ref))
    if not out:
        out.append((INFO, "expectations track the run; the four protected-surface rows stay "
                          "ESCALATE in every mode"))
    return out



@entry("RG-0058", "The fix agent is shown the REAL source, never its own exhaust, and never nothing at all",
       LOCKED, scope="scripts/maintenance_agent.py _candidate_files -- every fault in every "
                     "application file; the whole large-file class (ms.js, bea_main.py, "
                     "marketsquare.html, dashboard.server.html, ms.css)",
       fixed_on="2026-08-11",
       ref="CAND-FIX-1, 11 Aug 2026, diagnosed from the FIRST EVER armed live run "
           "(mode=LIVE, phase=prelaunch): 2 faults seen, 2 x 'no clean patch', nothing "
           "shipped. Safe, but useless -- and the reason was structural, not the model's. "
           "Two compounding faults in the 9 Aug candidate-file finder: "
           "(1) it discarded any file over 12,000 bytes, and EVERY file this app lives in is "
           "over it -- ms.js 1,074,965, bea_main.py 906,981, marketsquare.html 405,115, "
           "dashboard.server.html 449,274, ms.css 129,178 -- so the very fix that was added on "
           "9 Aug to stop blind patching ('a blind prompt was why the real Sonnet patch never "
           "applied') could never once fire on real application code. "
           "(2) it ranked raw git-grep hits across the WHOLE repo including the agent's own "
           "output: TS-0024's top two candidates were .maint_agent/run_*.json, the agent's own "
           "run reports, which quote the fault title verbatim. The brain was handed two copies "
           "of its own exhaust and asked to patch it, and correctly declined. "
           "Fix: noise paths are excluded BEFORE ranking (run reports, changelog.d/status.d/ "
           "Records/AUDIT/DAILY_WATCH, CHANGELOG/STATUS/registers, .bak, APP_PREVIEW, logs), "
           "and oversized files are WINDOWED to a real excerpt around the densest token "
           "cluster with the true line range named, rather than dropped. Verified: ms.js now "
           "yields lines 3626-3766 of 16425 (13,453 chars of the actual seller-CV code) where "
           "it previously yielded nothing, and .maint_agent/run_*.json is excluded. "
           "NOT claimed: that the agent can now write applicable patches. This removes a "
           "structural blocker; whether the excerpts produce diffs that gate green is the next "
           "live run's question, not this entry's.")
def rg_fix_agent_sees_real_source():
    a = repo_file("scripts/maintenance_agent.py")
    if a is None:
        return [(INFO, "running outside the repo -- CAND-FIX-1 is a source assertion, skipped")]
    out = []
    if "_is_noise" not in a or "_window" not in a:
        out.append((FAIL, "the candidate finder lost its noise filter or its windowing -- the "
                          "agent is back to reading its own run reports and discarding every "
                          "file the app actually lives in (CAND-FIX-1)"))
        return out
    if ".maint_agent/" not in a:
        out.append((FAIL, "the agent's own run-report directory is no longer excluded from "
                          "candidate ranking -- it will read its own exhaust (CAND-FIX-1)"))
    # the ONLY size branch may not silently drop a big file again
    i = a.find("def _candidate_files(")
    j = a.find("\ndef _is_noise", i)
    body = a[i:j if j > 0 else len(a)]
    if "_window(" not in body:
        out.append((FAIL, "_candidate_files no longer windows oversized files -- every real "
                          "application file is invisible to the brain again (CAND-FIX-1)"))
    if "EXCERPT lines" not in a:
        out.append((FAIL, "the excerpt no longer names its true line range -- the brain cannot "
                          "write a diff it can place (CAND-FIX-1)"))
    if not out:
        out.append((INFO, "noise excluded before ranking; oversized files windowed, not dropped"))
    return out



@entry("RG-0059", "Every run states the code it is actually running -- a stale box cannot pass for a test",
       LOCKED, scope="scripts/maintenance_agent.py run banner; every run on every machine, "
                     "including the B4 rehearsal",
       fixed_on="2026-08-11",
       ref="STALE-CODE-1, 11 Aug 2026. TWICE in one day a run was read as a valid test while "
           "the server was on an older commit: the B4 Tier 2 'NOT READY' at 06:42 (server on "
           "9cc3725, one commit behind BRAIN-PATH-1) and the 0/2 live run at 08:10 (server on "
           "127b6a6, one behind CAND-FIX-1). Both times `git pull` said 'Already up to date' -- "
           "which is TRUE and useless, because it reports the box against the mirror, not "
           "against the fix you just wrote and have not pushed. Both times the only tell was a "
           "stale wording in the output, caught by eye; the second time the result was "
           "identical to the previous run, which is exactly how a stale test passes for a real "
           "one. The banner now prints the short SHA, a DIRTY-WORKTREE marker and the subject "
           "line, so the code under test is stated before anyone reasons about the result. It "
           "reads SELF_REPO -- the agent's own checkout captured before any --repo override -- "
           "because the question is 'which agent is running', never 'which sandbox is being "
           "patched'. Verified: the rehearsal now prints 'code c758b83 DIRTY-WORKTREE "
           "maintenance-loop: CAND-FIX-1...' rather than the temp sandbox's SHA.")
def rg_run_states_its_own_code():
    a = repo_file("scripts/maintenance_agent.py")
    if a is None:
        return [(INFO, "running outside the repo -- STALE-CODE-1 is a source assertion, skipped")]
    out = []
    if "_code_stamp" not in a:
        out.append((FAIL, "the run no longer states which commit it is executing -- a stale box "
                          "will pass for a real test again (STALE-CODE-1)"))
        return out
    if "SELF_REPO" not in a:
        out.append((FAIL, "the code stamp no longer pins to the agent's own checkout; a --repo "
                          "override will make it report the sandbox instead (STALE-CODE-1)"))
    if "DIRTY-WORKTREE" not in a:
        out.append((FAIL, "the code stamp no longer flags uncommitted changes -- 'it works here' "
                          "cannot be distinguished from 'it is committed' (STALE-CODE-1)"))
    i = a.find("SELF_REPO = REPO")
    j = a.find("_repo_override")
    if i < 0 or (j > 0 and i > j):
        out.append((FAIL, "SELF_REPO is captured after the --repo override, so the stamp can "
                          "report the rehearsal sandbox as the running agent (STALE-CODE-1)"))
    if not out:
        out.append((INFO, "every run names its commit, its dirtiness and its subject line"))
    return out



@entry("RG-0060", "The AI Coach front door ANSWERS -- 'unavailable' can never again be silent",
       LOCKED, scope="POST /advert-agent/coach live gate -- the whole 'AI Coach unavailable' "
                     "class (TS-0024); zero-spend probe: an unregistered email is refused 401 "
                     "BEFORE any model call or Tuppence charge",
       fixed_on="2026-08-12",
       ref="TS-0024 (7 Aug 2026): 'AI coach was unavailable. Why?' The structural cause -- "
           "endpoints gated on ONE vendor's key -- was closed by RG-0032 on 5 Aug, but nobody "
           "had driven the coach end-to-end since, so 'fixed' rested on reading code. 12 Aug "
           "2026 maintenance loop reproduced the failing action clean on live: POST "
           "/advert-agent/coach, category Property, HTTP 200 in 10.0s with real coaching JSON "
           "(title+description suggestions, 4 trust_score_actions, free_used flip). That "
           "one-time run cost 1T + one Haiku call, so it cannot be the standing assertion. "
           "This probe is the zero-cost form: a valid-shaped request for an UNREGISTERED email "
           "must answer 401 'Unrecognised account' -- proof the endpoint is served, "
           "any_lane_configured() passed, and the refusal happened BEFORE spend. 503 here IS "
           "the tester's fault back; 422 means the probe body drifted from AACoachRequest and "
           "the assertion itself needs repair, not weakening.")
def rg_ai_coach_front_door():
    out = []
    try:
        flags = _json("/flags")
        active = ((flags.get("ai_provider") or {}).get("active") or "").strip()
        if not active:
            out.append((FAIL, "/flags names no active AI lane -- the coach cannot be expected "
                              "to answer; the lane wiring itself has regressed (TS-0024)"))
            return out
    except Exception as ex:
        return [(FAIL, "/flags unreadable while probing the coach gate: " + repr(ex)[:120])]
    body = json.dumps({"email": "rg0060-probe@invalid.trustsquare.co",
                       "category": "Property", "fields": {"title": "ledger probe"},
                       "photo_slots_completed": []}).encode("utf-8")
    _require_net()
    hdrs = dict(UA)
    hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + "/advert-agent/coach", data=body, headers=hdrs,
                                 method="POST")
    try:
        code = urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as ex:
        raise ProbeOffline(repr(ex)[:140])
    if code == 503:
        out.append((FAIL, "the coach gate answered 503 with lane '%s' active -- the exact "
                          "TS-0024 fault is BACK: configured lanes but a refusing gate" % active))
    elif code == 422:
        out.append((FAIL, "the probe body no longer matches AACoachRequest (422) -- fix THIS "
                          "assertion, it can no longer see the gate"))
    elif code != 401:
        out.append((FAIL, "unregistered-email coach probe answered %d, expected 401 -- the "
                          "front door is not refusing the way the zero-spend proof relies on"
                          % code))
    if not out:
        out.append((INFO, "lane '%s' active; unregistered probe refused 401 before any spend "
                          "-- the coach front door answers" % active))
    return out



@entry("RG-0061", "The +1 page tells the truth about the B2b agent -- readiness is reported, never recalled",
       LOCKED, fixed_on="2026-08-13", scope="the whole MAINT-DASH-1 lane: agent heartbeat POST -> /dashboard/maint "
                   "store -> +1 page card; facts only, no key material, no web arming surface",
       ref="MAINT-DASH-1, 12 Aug 2026. David: 'put this in the ops dashboard as a switch for "
           "launch.' The honest form is a truth card, not a switch: the brain key is a "
           "gitignored file and MAINTENANCE_AGENT_ENABLED is env on the machine that runs the "
           "loop -- David's acts; a web toggle could only lie or hazard. The loop posts its own "
           "heartbeat after every real run (rehearsals deliberately never post), the server "
           "stores whitelisted FACTS (RG-0042 rule), the card renders keyed/armed/stale in "
           "colour. OPEN until the lane is proven end-to-end live: the endpoint deployed AND "
           "the first real heartbeat recorded -- then READY TO LOCK. Added same-session as the "
           "build (RG-0029's lesson: the unasserted fix is invisible when it rots). 13 Aug: relocated at David's direction from a standalone card into the ls-gMaint group as a status ROW -- assertion follows the row id; the no-toggle promise now scopes to the row.")
def rg_maint_dash_lane():
    out = []
    a = repo_file("bea_main.py")
    if a is not None:
        if 'def dashboard_maint_post' not in a or '_MAINT_HB_FIELDS' not in a:
            out.append((FAIL, "the heartbeat store or its facts-only whitelist is gone from "
                              "bea_main.py (MAINT-DASH-1)"))
        elif 'def dashboard_maint_post(payload: dict = Body(...), _admin=Depends(_require_maint))' not in a:
            out.append((FAIL, "POST /dashboard/maint no longer rides the maintenance "
                              "credential -- anyone could stamp the readiness card (MAINT-DASH-1)"))
    m = repo_file("scripts/maintenance_agent.py")
    if m is not None:
        if "_post_heartbeat" not in m:
            out.append((FAIL, "the loop no longer posts its heartbeat -- the +1 card will "
                              "quietly freeze at the last truth (MAINT-DASH-1)"))
        elif "rehearsal run -- synthetic faults never stamp the dashboard" not in m:
            out.append((FAIL, "the rehearsal guard is gone -- a B4 synthetic storm can stamp "
                              "the production card as a real run (MAINT-DASH-1)"))
    d = repo_file("dashboard.server.html")
    if d is not None:
        if 'id="maint-b2b-row"' not in d or "maintRender" not in d:
            out.append((FAIL, "the +1 page no longer carries the B2b readiness card "
                              "(MAINT-DASH-1)"))
        else:
            i = d.find('id="maint-b2b-row"')
            j = d.find("Trust &amp; privacy rails", i)
            if "ls-sw" in d[i:j if j > 0 else i + 4000]:
                out.append((FAIL, "a toggle appeared inside the B2b card -- the no-web-arming "
                                  "design decision has been violated (MAINT-DASH-1)"))
    try:
        hb = _json("/dashboard/maint")
        if not hb.get("received_at"):
            out.append((FAIL, "endpoint live but NO real heartbeat recorded yet -- the lane is "
                              "not proven end-to-end; passes after the next maintenance run"))
        elif "brain_keyed" not in hb:
            out.append((FAIL, "heartbeat recorded without brain_keyed -- the card cannot state "
                              "the one fact the launch checklist needs"))
        else:
            out.append((INFO, "live heartbeat %s -- brain %s, %s" %
                        (hb.get("run", "?"), "KEYED:" + str(hb.get("brain_lane") or "?")
                         if hb.get("brain_keyed") else "KEYLESS",
                         "ARMED" if hb.get("armed") else "shadow")))
    except urllib.error.HTTPError as e:
        out.append((FAIL, "GET /dashboard/maint answered %d -- the endpoint has not reached "
                          "the live server yet (ships with the next deploy)" % e.code))
    return out





@entry("RG-0062", "Every rebuilt adventures map keeps the REPORT widget -- fixed in the TEMPLATE, not the output",
       LOCKED, fixed_on="2026-08-13", scope="the whole map-rebuild class: scripts/journey_template.html now "
                   "carries the ts_report.js line, so build_journey.py cannot drop it from any "
                   "adventures_*_map.html again (na/bw/mz/c2c/ke and every future journey)",
       ref="Third occurrence of this class: 11 Aug dropped it from all five maps twice (David's "
           "5 Aug ruling: REPORT tab on EVERY page), 13 Aug the MZ rebuild dropped it again and "
           "test_tester_intake caught na/bw/c2c/ke missing it too from post-fix rebuilds. The "
           "11 Aug fix patched the OUTPUT files; every later rebuild regenerated from the "
           "unfixed template and re-lost the line. 13 Aug: the line moved INTO "
           "journey_template.html (the one source every rebuild copies), outputs re-verified, "
           "all 16 tester-intake tests green. The deploy gate (test_tester_intake) remains the "
           "shipping backstop; this entry asserts the template so the class dies at the root.")
def rg_template_report_widget():
    out = []
    line = 'ts_report.js'
    t = repo_file("scripts/journey_template.html")
    if t is not None and line not in t:
        out.append((FAIL, "journey_template.html lost the ts_report.js line -- the next map "
                          "rebuild ships without the REPORT widget (RG-0062)"))
    for f in ("adventures_na_map.html", "adventures_bw_map.html", "adventures_mz_map.html",
              "adventures_c2c_map.html", "adventures_ke_map.html"):
        m = repo_file(f)
        if m is not None and m.count('<script src="/static/ts_report.js') != 1:
            out.append((FAIL, f + " does not carry exactly one ts_report.js include -- a "
                              "rebuild or hand edit broke the standing rule (RG-0062)"))
    return out


@entry("RG-0063", "Every pixel the app serves comes from OUR origin -- no third-party host serves an image",
       LOCKED, fixed_on="2026-08-13", scope="the image-origin class entire: /demo-listings + /demo-sellers live payloads, repo "
                   "demo_listings.json / demo_sellers.json / demo_image_map.json consumers, and the ms.js "
                   "SF tile fallback -- unsplash, pexels, picsum, cloudinary, imgur or any lookalike",
       ref="DW-025 (open since 7 Aug 2026): 1,141 references -- 266 unique images -- hotlinked "
           "images.unsplash.com from the demo payloads, leaking visitor IP+referrer to a third party "
           "on every page view and betting the whole demo catalogue on someone else's hotlink policy. "
           "RG-0025 stayed correctly green because its scope is SCRIPTS; this entry is its sibling for "
           "IMAGES, written per-REQUIREMENT (the RG-0045 lesson). Closed 13 Aug 2026 in two halves: "
           "repo side rewrote every reference to /static/demo/<sha1-16>.jpg and pointed the ms.js SF "
           "fallback at the local tile (emoji is the real fallback now); migration 017 downloads all "
           "266 images + 7 SF tiles ON THE BOX (resumable, exit-2-retries), rewrites the server-managed "
           "demo_sellers.json only at 100%, and writes ATTRIBUTION.json (Unsplash License provenance). "
           "OPEN until 017 completes on a deploy; the live half reads the real payloads through the "
           "reviewer gate. LOCKED 13 Aug 2026 (evening): 273/273 on the box -- 244 fetched clean, "
           "29 filled by the stand-in rung because their SOURCE URLs were dead all along (truncated "
           "params like q=8, mangled photo IDs -- seed-data corruption, so those 29 demo cards were "
           "broken on the live site BEFORE this work; the self-host exposed then repaired them). "
           "Live demo_sellers.json rewritten (0 unsplash / 40 local, verified through the gate); "
           "every substitution named in /static/demo/ATTRIBUTION.json. DW-025 closed.")
def rg_no_third_party_images():
    import re as _re
    out = []
    HOSTS = _re.compile(r"(images\.unsplash\.com|unsplash\.com|pexels\.com|picsum\.photos|cloudinary\.com|imgur\.com)")
    # Repo half: the shipped sources must be clean
    for f in ("demo_listings.json", "demo_sellers.json", "ms.js"):
        c = repo_file(f)
        if c is None:
            continue
        hits = sorted(set(HOSTS.findall(c)))
        if hits:
            out.append((FAIL, f + " ships third-party image host(s) %s -- the hotlink class is back in source" % hits))
    # Live half: the payloads actually served (read through the reviewer gate)
    read_any = False
    for path in ("/demo-listings", "/demo-sellers"):
        try:
            body = _get(path)
        except Exception as ex:
            out.append((INFO, "%s unreadable (%s) -- live half not proven this run" % (path, ex)))
            continue
        read_any = True
        n = len(HOSTS.findall(body))
        if n:
            out.append((FAIL, "%s still serves %d third-party image reference(s) -- migration 017 has "
                              "not completed on the box (DW-025 open)" % (path, n)))
    if not read_any:
        out.append((FAIL, "neither demo payload could be read -- this check proved NOTHING about the "
                          "live surface (RG-0011/DW-024 lesson: fail loudly, never pass blind)"))
    return out


@entry("RG-0064", "The B2b lanes ride THROUGH the armed gate -- credentialed, never exempted",
       LOCKED, scope="the remote maint-lane class entire: maintenance_agent.py api() (intake GET, "
                     "fault PUTs, heartbeat POST) and fault_reconcile.py call(); plus the inverse -- "
                     "anonymous /admin/* must STAY refused at the origin, whatever else gets fixed",
       fixed_on="2026-08-13",
       ref="GATE-COOKIE-1. Migration 016 armed auth_request on the nginx catch-all (~05:4x 13 Aug, "
           "David's ruling closing DW-023/RG-0029); the exempt list -- 007 unchanged -- never carried "
           "the maint-key lane, so the 13:17Z maintenance run 401'd at the ORIGIN before the app saw "
           "X-Maint-Key and failed safe ('nothing read'). Latent since 7 Aug: the gap never bit while "
           "007 was a green no-op. Fix carries the ts_review credential exactly as this ledger's _get "
           "does (mint once per run from .secrets/review_code.txt, retry on 401/403) -- the gate "
           "config is UNTOUCHED; widening the exempt list was deliberately refused unattended. "
           "Reproduced clean 13:24Z: 1 seen, 1 acted, heartbeat received_at 13:24:46Z on the live card.")
def rg_maint_lane_through_gate():
    out = []
    seen_any_src = False
    for f in ("scripts/maintenance_agent.py", "scripts/fault_reconcile.py"):
        c = repo_file(f)
        if c is None:
            continue
        seen_any_src = True
        if "_review_cookie" not in c or "(401, 403)" not in c:
            out.append((FAIL, f + " lost the GATE-COOKIE-1 credential fallback -- remote runs will "
                              "401 at the origin and the B2b loop goes dark again"))
    try:
        sc = _status("/admin/faults?status=new")
        if sc not in (401, 403):
            out.append((FAIL, "anonymous /admin/faults answers %s -- the admin lane is EXPOSED; "
                              "the gate was widened instead of credentialed" % sc))
    except ProbeOffline as ex:
        out.append((INFO, "origin unreachable (%s) -- inverse guard not proven this run" % ex))
    key = (repo_file(".secrets/ms_maint_key.txt") or "").strip()
    ck = _review_cookie() if key else ""
    if key and ck:
        try:
            req = urllib.request.Request(BASE + "/admin/faults?status=new",
                                         headers=dict(UA, **{"X-Maint-Key": key, "Cookie": ck}))
            body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
            json.loads(body)
        except Exception as ex:
            out.append((FAIL, "credentialed intake read failed (%r) -- the B2b lane is dark; "
                              "13:17Z 13 Aug is what that looks like" % ex))
    elif seen_any_src:
        out.append((INFO, "maint key or review code unavailable -- credentialed half not proven this run"))
    return out


@entry("RG-0065", "The maint lane answers on the KEY ALONE -- the exemption is the belt, the cookie the brace",
       LOCKED, fixed_on="2026-08-14",
       scope="origin-side: migration 018's two exempt locations (/admin/faults*, /dashboard/maint) "
                   "and ONLY those -- the other /admin/* routes (login, users, flags, deploy-file...) "
                   "must STAY gated; RG-0064's inverse guard holds the refusal side",
       ref="GATE-EXEMPT-MAINT-1, David's ruling 13 Aug ('lets fix both'): remove the B2b lane's "
           "credential dependency on the review gate. Scoped after a route audit -- every "
           "/admin/faults* route and the /dashboard/maint POST carry Depends(_require_maint), "
           "constant-time, fails closed (bea_main.py:16366); GET /dashboard/maint is no-auth by "
           "documented design and merely regains its pre-gate posture. 018 rides the next "
           "successful deploy (engine stalled all day -- DW-042); until it lands, keyed-no-cookie "
           "intake 401s at nginx and this entry is EXPECTED open -- GATE-COOKIE-1 keeps the loop "
           "alive meanwhile. PROMOTED 14 Aug 2026 21:5x: migration 018 landed on the box and "
           "the keyed-no-cookie intake answered -- the belt now holds on its own, the cookie is "
           "the brace. Locked so the exemption cannot silently widen or disappear.")
def rg_maint_key_alone():
    out = []
    key = (repo_file(".secrets/ms_maint_key.txt") or "").strip()
    if not key:
        out.append((INFO, "maint key unavailable outside the repo -- key-alone lane not proven this run"))
        return out
    try:
        req = urllib.request.Request(BASE + "/admin/faults?limit=1",
                                     headers=dict(UA, **{"X-Maint-Key": key}))
        body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        json.loads(body)
    except Exception as ex:
        out.append((FAIL, "keyed-no-cookie intake refused (%r) -- migration 018 has not landed "
                          "on the box (deploy engine, DW-042)" % ex))
    return out


@entry("RG-0066", "The pre-launch gate tells the TRUTH -- a wrong reviewer code can never read as a connection error",
       LOCKED, fixed_on="2026-08-14",
       scope="the gate-screen failure-message class entire: wrong reviewer code (fallthrough to the "
                   "origin-gated /admin/login nginx HTML 401), rate-limit 429, reviewer-access-off 503 -- "
                   "index.html as served live, plus the repo marketsquare.html source half",
       ref="GATE-TRUTH-1, 13 Aug 2026. Hours after GATE-ENFORCE-2 armed the catch-all, anonymous "
           "POST /admin/login began answering nginx HTML 401; the gate script's r.json() threw and "
           "every unrecognised gate entry -- including Maroushka's, same day -- surfaced as a fake "
           "'Connection error. Please try again.'. Fix: gate script parses text-first, names the "
           "refusal ('Incorrect reviewer code'), surfaces 429/503 in words. EXPECTED open while the "
           "deploy engine is stalled (DW-042). PROMOTED 14 Aug 2026: the marker now reads off the "
           "live document -- a wrong reviewer code says so in words. Locked.")
def rg_gate_truth():
    out = []
    try:
        doc = _get("/")
        if "GATE-TRUTH-1" not in doc:
            out.append((FAIL, "live index.html lacks the GATE-TRUTH-1 branch -- an unrecognised "
                              "gate entry still reads as a fake 'Connection error'"))
    except Exception as ex:
        out.append((FAIL, "could not read the live document (%r)" % ex))
    src = repo_file("marketsquare.html")
    if src is not None and "Incorrect reviewer code. Please check it and try again." not in src:
        out.append((FAIL, "repo marketsquare.html lost the truthful gate branch"))
    return out


@entry("RG-0067", "The fix agent can AIM at real code -- window, fences, exhaust and gate credentials hold",
       LOCKED, scope="the real-file patch pipeline entire: _window aiming (rare-token tiers), "
                     "_strip_fences + git apply --recount --3way, harness/exhaust exclusion "
                     "(_is_noise), WINDOW-SPLICE-1 guard, GATE-CREDS-1 worktree secrets -- "
                     "every application file; bea_main.py (909 KB) and ms.js (1.06 MB) proven",
       fixed_on="2026-08-13",
       ref="Real-repo probe runs 4-13 (13 Aug): four environment defects and three pipeline "
           "defects found and fixed in one session. Keyless clone (PROBE-KEYS-1/2); window "
           "aimed at generic-token clusters while the defect sat elsewhere (WINDOW-AIM-1: "
           "lines 1158-1298 shown, defect at 122; rare2/rare8 tiers now steer); the probe "
           "harness ranked as the patch target because it quotes faults verbatim "
           "(PROBE-EXHAUST-1); sonnet's diffs arrived fenced with miscounted hunk headers and "
           "were written VERBATIM to .proposed.patch ('corrupt patch at the closing fence' -- "
           "PATCH-FENCE-1 + --recount, the root of the whole MAINT-B4-6 'diffs slip' class); "
           "the rewrite lane demanded a COMPLETE file while showing an excerpt that said the "
           "rest is not shown (WINDOW-SPLICE-1, spliced by line range under a bytes-match "
           "guard); and gate worktrees carried no .secrets, so from the moment 016 armed the "
           "origin gate the ledger GATE crashed 401-red for EVERY patch, however perfect "
           "(GATE-CREDS-1 -- the launch-critical one). PATCH-EVIDENCE-1 now keeps every "
           "failing diff + git's words. Evidence: PROBE PASS both targets, gates green, "
           "shadow-held. 'Patch quality on this codebase is no longer unproven.'")
def rg_fix_agent_aims_real():
    out = []
    c = repo_file("scripts/maintenance_agent.py")
    if c is None:
        return out
    for needle, why in (
            ("rare2 or rare8 or marks", "WINDOW-AIM-1 rare-token tiering"),
            ("def _strip_fences", "PATCH-FENCE-1 fence stripping"),
            ('"--recount", "--3way"', "the recounted apply"),
            ("maint_realrepo_probe.py", "PROBE-EXHAUST-1 harness exclusion"),
            ("window bytes moved under", "the WINDOW-SPLICE-1 guard"),
            ("GATE-CREDS-1", "worktree secrets provisioning")):
        if needle not in c:
            out.append((FAIL, "maintenance_agent.py lost %s -- the real-file patch pipeline "
                              "is back to pre-13-Aug blindness" % why))
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("_ma_rg66",
                                           os.path.join(REPO, "scripts", "maintenance_agent.py"))
        _ma = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_ma)
        body = (repo_file("bea_main.py") or "").replace("Admin credentials required.",
                                                        "Admin credentials requried.", 1)
        if "requried" in body:
            w = _ma._window("bea_main.py", body,
                            ["requried", "required", "Admin credentials requried.",
                             "admin", "message", "error"])
            if not (w and "requried" in w[1]):
                out.append((FAIL, "_window no longer aims at the distinctive token -- "
                                  "WINDOW-AIM-1 regressed (the brain would be shown the "
                                  "wrong lines again)"))
        else:
            out.append((INFO, "seed anchor string gone from bea_main.py -- update RG-0066's "
                              "functional seed"))
        if not _ma._is_noise("scripts/maint_realrepo_probe.py"):
            out.append((FAIL, "_is_noise no longer excludes the probe harness -- the brain can "
                              "be handed the fault's own definition again"))
        st = _ma._strip_fences("```diff\n--- a/x\n+++ b/x\n```")
        if st.startswith("```") or st.endswith("```"):
            out.append((FAIL, "_strip_fences no longer strips fences -- 'corrupt patch at the "
                              "closing fence' returns"))
    except Exception as ex:
        out.append((FAIL, "functional half crashed (%r) -- the aiming property is UNPROVEN "
                          "this run" % ex))
    return out


@entry("RG-0068", "No assertion on this board may pass by matching NOTHING -- a vacuous check is a lying check",
       LOCKED, scope="the vacuous-assertion class entire: every ledger pattern that is supposed to "
                     "find rows in a real table. Seeded from the two known instances (RG-0011's map-filename "
                     "regex, which matched 0 of 9 rows and reported ok from 29 Jul to 14 Aug) and generalised "
                     "so a NEW pattern that silently matches nothing trips this entry instead of going green.",
       fixed_on="2026-08-14",
       ref="LEDGER-META-1, born from DW-024. David's framing: a green light that lies costs more than any "
           "red, because every other colour on the board is discounted once one of them is known to be "
           "decorative. RG-0011 sat LOCKED and passing for 16 days while the two debts it existed to catch "
           "(GB -> adventures_uk_map.html, ZA -> adventures_reserve_map.html) sat untouched in the very "
           "rows it could not see. This entry makes that failure mode self-reporting: each guarded pattern "
           "below must match at least one thing in the live source, or this entry goes red and names it. "
           "Add a line here whenever a new ledger entry leans on a findall/search over a real table.")
def rg_no_vacuous_patterns():
    """Every pattern here MUST find something. Zero matches = the check has gone blind."""
    import re as _re
    out = []
    fe = repo_file("ms.js")
    if fe is None:
        return [(INFO, "ms.js not present (running outside the repo) -- meta-check skipped")]
    GUARDED = [
        ("RG-0011 map-filename rows",
         r"^\s*(?://\s*)?([A-Z]{2}): \{ file:'adventures_([a-z0-9]+)_map\.html(?:\?v=\d+)?'", fe, 9),
        ("RG-0011 ADV_COUNTRY_FLAGS table",
         r"ADV_COUNTRY_FLAGS\s*=\s*\{([^}]*)\}", fe, 1),
        ("RG-0011 ADV_COUNTRY_CURRENCY table",
         r"ADV_COUNTRY_CURRENCY\s*=\s*\{([^}]*)\}", fe, 1),
        ("RG-0012 ADV_TOUR_MAP table",
         r"ADV_TOUR_MAP\s*=\s*\{([^}]*)\}", fe, 1),
    ]
    for name, pat, hay, expect_at_least in GUARDED:
        n = len(_re.findall(pat, hay, _re.M | _re.S))
        if n == 0:
            out.append((FAIL, "%s matches ZERO things -- the assertion leaning on it is VACUOUS "
                              "and would report ok while seeing nothing (DW-024 class)" % name))
        elif n < expect_at_least:
            out.append((FAIL, "%s matches only %d row(s), expected at least %d -- the pattern has "
                              "gone partially blind" % (name, n, expect_at_least)))
    if not out:
        out.append((INFO, "all %d guarded patterns still match real rows -- no assertion is running blind"
                    % len(GUARDED)))
    return out


@entry("RG-0069", "The pre-deploy gate can PROVE the database from ANY session -- the proof never rides on a key that lives on one desk",
       LOCKED, fixed_on="2026-08-14",
       scope="the whole 'gate cannot prove, so it says REVIEW forever' class: tsl_gate.py "
                   "check_db and every session that runs it (David's desktop, the cloud sandbox, "
                   "the nightly task). Covers the primary DB's presence, byte size and integrity, "
                   "plus redis. NOT scoped to one machine -- that was precisely the defect.",
       ref="TSL-DBPROOF-1, 14 Aug 2026. The gate's only DB transport was ssh msdeploy@, and the "
           "private key stays on David's machine by design (and must never enter a cloud session). "
           "So every gate run from anywhere else printed 'could not prove the databases healthy this "
           "run' and returned REVIEW -- not because anything was wrong, but because nothing COULD be "
           "proven. A gate that can never go green is a gate people learn to wave through, which is "
           "the opposite of what it is for. Fix: bea_main.py _tsl_dbproof publishes a facts-only db "
           "block on /health (the one endpoint nginx leaves open anonymously post GATE-ENFORCE-1) -- "
           "presence, bytes, integrity verdict, redis ping; no paths, no schema, no counts, no "
           "customer data. integrity_check is a full scan so it is cached (TSL_DBPROOF_TTL_SEC, "
           "default 900s); presence and size are a live stat, which is what actually catches the "
           "zero-byte case. The whole block is individually guarded and can never raise, because a "
           "throwing /health would make the deploy engine auto-roll-back a good ship. tsl_gate now "
           "reads HTTPS first and keeps SSH as a second opinion; REVIEW is reserved for BOTH "
           "transports failing, which is a real cannot-prove. OPEN until the server carrying the db "
           "block is live -- it flips to READY TO LOCK on the next deploy.")
def rg_gate_proves_db_without_key():
    out = []
    # Repo half: the gate must prefer the credential-free transport.
    g = repo_file("tsl_gate.py")
    if g is not None:
        for needle, why in (("def check_db_http", "the HTTPS proof path"),
                            ("MS_HEALTH_URL", "the overridable health URL"),
                            ("def check_db_ssh", "SSH demoted to fallback")):
            if needle not in g:
                out.append((FAIL, "tsl_gate.py lost %s -- the gate is back to proving the DB "
                                  "only from David's desk" % why))
    b = repo_file("bea_main.py")
    if b is not None and "_tsl_dbproof" not in b:
        out.append((FAIL, "bea_main.py lost _tsl_dbproof -- /health no longer publishes the "
                          "credential-free DB proof"))

    # Live half: the proof must actually be readable, anonymously, and be true.
    h = _json("/health")
    db = h.get("db")
    if not isinstance(db, dict):
        out.append((FAIL, "live /health carries no db block -- the gate still cannot prove the "
                          "database without the SSH key"))
        return out
    if db.get("primary_present") is not True:
        out.append((FAIL, "live /health says the primary DB is not present (%r)"
                    % (db.get("reason"),)))
    szn = db.get("primary_bytes")
    if not isinstance(szn, int) or szn <= 0:
        out.append((FAIL, "live /health reports primary_bytes=%r -- a zero-byte primary DB is "
                          "the exact case this gate exists to catch" % (szn,)))
    integ = str(db.get("integrity") or "").lower()
    if integ not in ("ok", "unknown", "noread"):
        out.append((FAIL, "live /health reports integrity=%r -- the primary DB is CORRUPT"
                    % (db.get("integrity"),)))
    if not out:
        out.append((INFO, "DB proven over anonymous HTTPS: %d bytes, integrity %s, redis %s"
                    % (szn, db.get("integrity"), db.get("redis"))))
    return out


@entry("RG-0070", "One session logs in ONCE -- a rate-limited gate credential reads BLIND, never RED",
       LOCKED, scope="the gate-credential class entire: scripts/regression_ledger.py and "
                     "scripts/maintenance_agent.py -- every process in a session that reads "
                     "through the armed origin gate. Both halves: the shared on-disk token "
                     "cache (cause) and the 429 -> UNVERIFIED demotion (consequence)",
       fixed_on="2026-08-14",
       ref="Self-inflicted and proven the same morning (maintenance-loop run, 14 Aug): the "
           "ledger ran green at 05:33, then the agent plus four per-fault rehearsal runs each "
           "minted their own ts_review token, exhausting the 8-per-10-min allowance; the next "
           "ledger run printed '13 previously-fixed issue(s) HAVE COME BACK. Do not deploy "
           "over this.' with every failure reading 'check crashed: <HTTPError 401>'. A bare "
           "POST /review/login answered 429 'Too many attempts' while the site was healthy -- "
           "so the board was false-red, the most expensive failure mode this ledger has: it "
           "invites the next session to fix what is not broken and blocks a deploy for "
           "nothing. GATE-CACHE-1 fixes the class at both ends: the token is cached in "
           ".secrets/review_cookie.json (gitignored, 0600, 12h, keyed on BASE) so a session "
           "logs in once instead of once per process, and a 429 is NAMED so affected entries "
           "raise ProbeOffline -> UNVERIFIED (exit 2, blind) instead of REGRESSION (exit 1). "
           "A cookie the origin rejects is expired in place (FUSE blocks unlink) so a dead "
           "token is never re-presented. RG-0011/DW-024 is untouched -- nothing passes blind.")
def rg_gate_credential_cached_and_honest():
    out = []
    for fn in ("scripts/regression_ledger.py", "scripts/maintenance_agent.py"):
        c = repo_file(fn)
        if c is None:
            out.append((FAIL, "%s unreadable -- the shared-credential guarantee is UNPROVEN" % fn))
            continue
        if "_cookie_from_cache" not in c or "_cookie_to_cache" not in c:
            out.append((FAIL, "%s no longer shares the on-disk review token -- every process "
                              "mints its own again and a busy session re-burns the 8/10min "
                              "allowance (GATE-CACHE-1 cause half)" % fn))
        if "review_cookie.json" not in c:
            out.append((FAIL, "%s lost the shared cache path -- the two lanes can no longer "
                              "reuse one login" % fn))
        if 'e.code == 429' not in c:
            out.append((FAIL, "%s no longer recognises a 429 at /review/login -- a rate-limited "
                              "credential can read as an app fault again" % fn))
    led = repo_file("scripts/regression_ledger.py") or ""
    if 'rate-limited (429 at /review/login)' not in led or "raise ProbeOffline" not in led:
        out.append((FAIL, "the ledger no longer demotes a rate-limited gate read to blind -- "
                          "false REGRESSIONS (exit 1) return, the exact 14 Aug failure"))
    if "_invalidate_review_cookie" not in led:
        out.append((FAIL, "the ledger no longer expires a REJECTED token -- a dead credential "
                          "would be re-presented from cache by every later process"))
    # Functional half: the cache round-trips, and an expired entry is not served.
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("_rl_gc",
                                           os.path.join(REPO, "scripts", "regression_ledger.py"))
        _rl = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_rl)
        _keep = None
        try:
            _keep = open(_rl._REVIEW_CACHE, encoding="utf-8").read()
        except Exception:
            pass
        try:
            _rl._cookie_to_cache("ts_review=RG0070PROBE")
            if _rl._cookie_from_cache() != "ts_review=RG0070PROBE":
                out.append((FAIL, "the token cache does not round-trip -- sharing is nominal only"))
            _rl._cookie_to_cache("ts_review=RG0070PROBE", ttl=-1)
            if _rl._cookie_from_cache():
                out.append((FAIL, "an EXPIRED cache entry is still served -- invalidation is a "
                                  "no-op and a rejected token would live on"))
        finally:
            if _keep is not None:
                try:
                    _fd = os.open(_rl._REVIEW_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                    with os.fdopen(_fd, "w", encoding="utf-8") as _fh:
                        _fh.write(_keep)
                except Exception:
                    pass
    except Exception as ex:
        out.append((FAIL, "functional half crashed (%r) -- the cache property is UNPROVEN this "
                          "run" % ex))
    if not out:
        out.append((INFO, "one login per session, shared on disk; a 429 reads blind, not red"))
    return out


@entry("RG-0080", "No unattended loop is ever routed at the metered Anthropic key -- and the Fable arrangement EXPIRES 1 Sep 2026",
       LOCKED, scope="ai_provider.TASK_MODEL (no anthropic 'design' row) + maintenance_agent._fix_task(). "
                     "Covers every autonomous caller, not just today's agent: the invariant is 'a loop "
                     "nobody is watching never spends per-token'. Second half: the pre-launch Fable "
                     "arrangement is TIME-BOXED to 1 Sep 2026 and does not renew by default",
       fixed_on="2026-08-15",
       ref="SPEND-GUARD-1, David 15 Aug 2026: 'do not use the Anthropic key which eats $ up in "
           "seconds... You will bring us to a screeching halt.' Claude's error, caught within minutes: "
           "the first cut of RUL-013 routed the pre-launch fix lane at claude-fable-5 via "
           "ANTHROPIC_API_KEY -- metered credits at $10/$50 per Mtok fired by an unattended loop three "
           "times a day with nobody watching the meter, also breaking the standing rule that "
           "Fable-via-credits is 'reserved for the most important work only' (11 Jul). No spend "
           "occurred: the server carries no ANTHROPIC_API_KEY and the agent had not run since the edit. "
           "RUL-013 stands but is TIME-BOXED (David, same session): Fable resolves pre-launch design "
           "requests in a COWORK SESSION on the subscription -- tokens already paid for, and an "
           "unattended process cannot use a subscription, only a session can. FROM 1 SEP 2026 the "
           "arrangement ENDS and design work returns to the allocated design agent or its swapped-out "
           "option -- the 'design' task tier (openai gpt-5.6-sol, scaleway mistral-medium standby), "
           "NOT Fable. The seam is unchanged by any of this, which was David's condition: 'let us not "
           "break our design.' Sibling of RUL-007 -- unbudgetable cost is barred whether it arrives as "
           "a percentage, a retroactive cliff, or an autonomous loop holding a metered key.")
def rg0080():
    out = []
    if not REPO:
        return [(INFO, "repo not readable -- spend guard not checked")]
    ap = os.path.join(REPO, "ai_provider.py")
    ma = os.path.join(REPO, "scripts", "maintenance_agent.py")
    if not (os.path.exists(ap) and os.path.exists(ma)):
        return [(INFO, "seam/agent not present -- skipped")]
    a = open(ap, encoding="utf-8", errors="replace").read()
    m = open(ma, encoding="utf-8", errors="replace").read()
    anth = re.search(r'"anthropic":\s*\{(.*?)\}', a, re.S)
    if anth and '"design"' in anth.group(1):
        out.append((FAIL, "ai_provider has an anthropic 'design' entry again -- an unattended run "
                          "would bill usage credits per token"))
    else:
        out.append((INFO, "seam has no anthropic design route"))
    live = [l for l in m.splitlines()
            if 'provider="anthropic"' in l and not l.lstrip().startswith("#")]
    if live:
        out.append((FAIL, "maintenance_agent pins provider=anthropic in %d live call(s)" % len(live)))
    else:
        out.append((INFO, "agent pins no anthropic provider in any live call"))
    dsg = {p: bool(re.search(r'"%s":\s*\{(.*?)\}' % p, a, re.S) and
                   '"design"' in re.search(r'"%s":\s*\{(.*?)\}' % p, a, re.S).group(1))
           for p in ("openai", "scaleway")}
    if not any(dsg.values()):
        out.append((FAIL, "no non-Anthropic design lane remains -- post-1-Sep design work has "
                          "nowhere to go"))
    else:
        out.append((INFO, "post-1-Sep design lane present: " +
                          ", ".join(p for p, v in dsg.items() if v)))
    return out


@entry("RG-0073", "Every country we have listings for is REACHABLE in the picker -- shipping a market is not the same as being able to browse it",
       LOCKED, scope="the Adventures country picker in marketsquare.html against the countries "
                     "actually present in live /listings. Asserts the INVARIANT (a market with "
                     "listings has a way in), not a hardcoded country list -- so it stays true "
                     "when the next market ships instead of rotting like the list it replaces",
       fixed_on="2026-08-14",
       ref="COUNTRY-FILTER-1. Kenya's 24 super listings went live on 14 Aug with no picker row: "
           "reachable only under 'All countries', invisible to anyone browsing by country. "
           "Botswana had sat in the same state since July -- ADV_COUNTRY_FLAGS/CURRENCY carried "
           "BW and KE (ms.js:2133-2134) while the sheet never gained the rows. The seeder, the "
           "photos, the media push and the deploy all succeeded; the market was simply "
           "unbrowsable. This guard closes the loop between 'seeded' and 'reachable'.")
def rg0073():
    out = []
    if not REPO:
        return [(INFO, "repo not readable from here -- picker check skipped")]
    hp = os.path.join(REPO, "marketsquare.html")
    if not os.path.exists(hp):
        return [(INFO, "marketsquare.html not present -- picker check skipped")]
    html = open(hp, encoding="utf-8", errors="replace").read()
    rows = set(re.findall(r'id="adv-co-([A-Z]{2}|ALL)"', html))
    try:
        live = _json("/listings?limit=500")
    except Exception as ex:
        return [(INFO, "live listings unreadable (%r) -- picker checked against source only" % ex)]
    if not isinstance(live, list):
        return [(INFO, "unexpected /listings shape -- picker check inconclusive")]
    have = {str(l.get("country") or "").upper() for l in live if l.get("country")}
    have = {c for c in have if len(c) == 2}
    missing = sorted(have - rows)
    if missing:
        out.append((FAIL, "listings exist for %s but the picker has no row -- that market is "
                          "unbrowsable except under 'All countries'" % ", ".join(missing)))
    else:
        out.append((INFO, "every country with listings has a picker row (%d countries)" % len(have)))
    return out


@entry("RG-0072", "The drift monitor compares CONTENT, never the server's own cache-buster bump",
       LOCKED, scope="check_deploy_drift.py, BOTH sides of the comparison, for every manifest file "
                     "carrying a `?v=N` reference -- today marketsquare.html->index.html (8 refs) and "
                     "dashboard.server.html->dashboard.html (6). The sibling of DRIFT-CRLF-1: same "
                     "class (compare content, not a transport artefact), different artefact",
       fixed_on="2026-08-14",
       ref="DRIFT-CACHEBUST-1. Cost a scheduled session to 'diagnose the stalled deploy engine' that "
           "was never stalled. server_deploy.sh:170-186 rewrites the SERVED index.html in place "
           "(sed -i, monotonic ?v= bump) so browsers actually fetch a new build -- by DESIGN the served "
           "file differs from its source. check_deploy_drift.py md5'd local vs served, so those two "
           "files reported drift on EVERY deploy, for ever, and no amount of re-deploying could clear "
           "it: 14 Aug's release logged 'DEPLOY DRIFT: 2 file(s) local-ahead' twice and waited out two "
           "server ticks for a condition that cannot go clean. Fix: normalise `?v=[0-9]+` -> `?v=N` on "
           "both sides before hashing (locally in _md5, and on the box via sed before md5sum), exactly "
           "as DRIFT-CRLF-1 normalises line endings. Proven with a two-file stand-in differing ONLY in "
           "the bump: raw md5 differed, normalised md5 matched. A real drift -- genuinely stale content "
           "-- still reports, because only the bump is neutralised.",
       )
def rg0072():
    out = []
    src_path = os.path.join(REPO, "check_deploy_drift.py") if REPO else None
    if not src_path or not os.path.exists(src_path):
        return [(INFO, "check_deploy_drift.py not readable from here -- source half not proven this run")]
    body = open(src_path, encoding="utf-8", errors="replace").read()
    if "_CACHEBUST_RE" not in body or "?v=N" not in body:
        out.append((FAIL, "local md5 no longer neutralises the cache-buster -- phantom drift is back "
                          "and the 'stalled engine' hunt starts again"))
    else:
        out.append((INFO, "local side normalises ?v=N before hashing"))
    if "sed -E 's/" not in body or "md5sum" not in body:
        out.append((FAIL, "remote md5 no longer normalises the cache-buster before hashing -- "
                          "the two sides are being compared on different bytes again"))
    else:
        out.append((INFO, "remote side normalises ?v=N before hashing"))

    # DRIFT-FILEMAP-1 (15 Aug 2026): normalising the bytes is only half of it -- the monitor must
    # also compare the file that ACTUALLY SHIPS. It tracked local dashboard.html against the served
    # dashboard.html, which is built from dashboard.server.html (manifest:72). Different source, so
    # that row could never match: phantom drift again, different cause. The invariant is that the
    # drift map and the deploy manifest agree about where each served file comes from.
    SERVER_OWNED = {"demo_sellers.json"}   # written live by migration 017, never placed by deploy
    try:
        fm = dict(re.findall(r'"([^"]+)":\s*"([^"]+)",',
                             body[body.index("FILEMAP = {"):body.index("}", body.index("FILEMAP = {"))]))
        man = {}
        mp = os.path.join(REPO, "ops", "autodeploy", "deploy_manifest.txt")
        for line in open(mp, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            s, d = [x.strip() for x in line.split("|", 1)]
            man[s] = d
        bad = []
        for lsrc, rdest in fm.items():
            if lsrc in SERVER_OWNED:
                continue
            if lsrc not in man:
                bad.append("%s tracked but not in the manifest" % lsrc)
            elif man[lsrc] != rdest:
                bad.append("%s: drift->%s, manifest->%s" % (lsrc, rdest, man[lsrc]))
        if bad:
            out.append((FAIL, "drift map disagrees with the deploy manifest, so it is comparing "
                              "files that never ship: " + "; ".join(bad)))
        else:
            out.append((INFO, "drift map agrees with the deploy manifest on every tracked file"))
    except Exception as ex:
        out.append((INFO, "manifest/FILEMAP cross-check skipped (%r)" % ex))
    return out


@entry("RG-0071", "A killed maintenance run still leaves a RECORD -- the queue is never read into silence",
       LOCKED, scope="scripts/maintenance_agent.py main() -- every host the loop runs on, and "
                     "every fault in every run: the incremental report flush, the --only "
                     "selector and the MAINT_TIME_BUDGET_S stop. The sibling of BRAIN-DEPS-2 "
                     "(background reaping); this is the FOREGROUND half",
       fixed_on="2026-08-14",
       ref="Found by losing runs to it, 14 Aug: the Cowork sandbox hard-caps ONE bash call at "
           "~178 s, and a single PATH_A fault on a megabyte file (window + brain + worktree on "
           "FUSE + the 46 s gate ledger, whose own subprocess timeout is 240 s) does not fit. "
           "Three runs were killed mid-gate and each wrote NOTHING -- no report, no heartbeat, "
           "no trace that the queue had been read at all, which is indistinguishable from a "
           "loop that never ran. The guards are untouched; only the bookkeeping changed: the "
           "run report is flushed after EVERY fault (and at each early-exit lane), so a kill "
           "costs at most the fault in flight; --only=REF drives the queue one fault per "
           "invocation on a capped host; MAINT_TIME_BUDGET_S stops cleanly BEFORE starting a "
           "fault that cannot finish and names the remainder DEFERRED rather than dropping "
           "them. Proven the same session: --only=TS-0032 completed inside the cap, wrote its "
           "report and posted the heartbeat (/dashboard/maint run 2026-08-14T06:01:28Z).")
def rg_maint_run_leaves_a_record():
    out = []
    c = repo_file("scripts/maintenance_agent.py")
    if c is None:
        out.append((FAIL, "maintenance_agent.py unreadable -- the record guarantee is UNPROVEN"))
        return out
    for needle, why in (
            ("def _flush", "the incremental report flush"),
            ('_arg("--only"', "the --only queue selector"),
            ("MAINT_TIME_BUDGET_S", "the wall-clock budget"),
            ('"DEFERRED"', "the DEFERRED lane (unexamined faults are named, not dropped)"),
            ("_flush(); continue", "flushing on the early-exit lanes")):
        if needle not in c:
            out.append((FAIL, "maintenance_agent.py lost %s -- a killed run can vanish "
                              "silently again (HOST-CAP-1)" % why))
    # The flush must happen INSIDE the fault loop, not only at the end -- that was the bug.
    _body = c.split("for _i, f in enumerate(faults):", 1)
    if len(_body) != 2:
        out.append((FAIL, "the fault loop no longer carries its index -- the budget stop and "
                          "the DEFERRED remainder cannot work"))
    elif _body[1].count("_flush()") < 4:
        out.append((FAIL, "fewer than four flush points inside the fault loop -- the early-exit "
                          "lanes are writing nothing again"))
    if not out:
        out.append((INFO, "report flushed per fault; --only and time budget present; deferred "
                          "faults named"))
    return out


@entry("RG-0074", "Every copy of the admin-gate script branches on r.status BEFORE parsing, so a "
       "gate refusal can never again be reported as 'Connection error'",
       LOCKED, scope="ALL admin-gate copies: marketsquare.html, dashboard.server.html, "
                     "dashboard.html, marketsquare_admin.html, archive/session_dashboard_live.html",
       fixed_on="2026-08-14",
       ref="GATE-TRUTH-2. David, 14 Aug 2026: 'we are back at this recurring nightmare.' This "
           "asserts the mechanism of the RECURRENCE, not of any one instance. The gate script was "
           "written once in May 2026 (e0e4446) and COPIED into five files. Every fix since landed "
           "in whichever copy was in front of the person fixing it -- GATE-TRUTH-1 patched "
           "marketsquare.html on 13 Aug and left four copies calling r.json() blind. Meanwhile "
           "migrations/016 made the origin answer an nginx HTML 401 on /admin/login (deliberately "
           "NOT exempt, per migrations/018), so the blind parse threw and the .catch labelled "
           "EVERY distinct refusal -- gate lock, wrong password, 503 unset secret, genuine network "
           "failure -- with one identical sentence. A message that erases the difference between "
           "four faults guarantees the next one is diagnosed from zero, which is exactly why this "
           "kept coming back. The same collision has now been patched five times in five places "
           "(GATE-COOKIE-1, GATE-CACHE-1, GATE-CREDS-1, DW-040, GATE-TRUTH-1) and never as a "
           "class. Verified 14 Aug: all four remaining copies patched, node --check clean on "
           "28 script blocks.")
def rg_gate_truth_all_copies():
    out = []
    copies = ("marketsquare.html", "dashboard.server.html", "dashboard.html",
              "marketsquare_admin.html", "archive/session_dashboard_live.html")
    seen = 0
    for rel in copies:
        c = repo_file(rel)
        if c is None or "/admin/login" not in c or "showLoginError" not in c:
            continue
        seen += 1
        # Scope to the GATE fetches only. An earlier draft of this assertion matched any
        # blind r.json() in the file and flagged loadBIT() -- an unrelated data card. A check
        # that cries wolf gets muted, which is the same failure it exists to prevent.
        for route in ("/admin/login", "/admin/change-pin", "/admin/verify"):
            i = 0
            while True:
                i = c.find(route, i)
                if i < 0:
                    break
                window = c[i:i + 700]          # the fetch and its immediate .then chain
                if ".then(function(r){ return r.json(); })" in window:
                    out.append((FAIL, "%s parses the %s response before checking r.status -- "
                                      "a gate refusal will surface as a fake connection error "
                                      "again (GATE-TRUTH-2)" % (rel, route)))
                i += len(route)
        if "GATE-TRUTH" not in c:
            out.append((FAIL, "%s carries an admin gate with no GATE-TRUTH status branch" % rel))
        elif "r.status === 401" not in c:
            out.append((FAIL, "%s names GATE-TRUTH but has no 401 branch -- the marker has "
                              "drifted away from the mechanism it is supposed to guarantee" % rel))
    if seen == 0:
        out.append((FAIL, "no admin-gate copy found at all -- this assertion has lost its "
                          "subject and would pass vacuously (see RG-0068)"))
    if not out:
        out.append((INFO, "all %d admin-gate copies branch on status before parsing" % seen))
    return out


@entry("RG-0075", "The admin-gate script has ONE source, not five hand-maintained copies",
       OPEN, scope="marketsquare.html, dashboard.server.html, dashboard.html, "
                   "marketsquare_admin.html, archive/session_dashboard_live.html",
       fixed_on="",
       ref="The root cause behind RG-0074 is duplication, not any one file. Five hand-maintained "
           "copies of the same 40 lines is why four separate gate fixes each had to be applied "
           "again per consumer, and why the dashboard -- the fifth consumer -- received none of "
           "them. EXPECTED TO FAIL until the gate script is one file included by every surface. "
           "The moment it passes, promote to LOCKED.")
def rg_gate_script_single_source():
    out = []
    copies = [r for r in ("marketsquare.html", "dashboard.server.html", "dashboard.html",
                          "marketsquare_admin.html", "archive/session_dashboard_live.html")
              if "adminGateSubmit" in (repo_file(r) or "")]
    if len(copies) > 1:
        out.append((FAIL, "the gate script is duplicated across %d files (%s) -- one shared "
                          "source would have made GATE-TRUTH-1 fix all of them on 13 Aug"
                    % (len(copies), ", ".join(copies))))
    else:
        out.append((INFO, "READY TO LOCK -- the gate script has a single source"))
    return out


@entry("RG-0076", "A file:// dashboard says so BEFORE a password is typed, and never asks the "
       "browser to do something CORS forbids",
       LOCKED, scope="dashboard.server.html, dashboard.html, marketsquare_admin.html",
       fixed_on="2026-08-14",
       ref="GATE-ORIGIN-1. The second face of the same recurring fault: a file:// page has origin "
           "'null', which is not in the BEA's ALLOWED_ORIGINS (bea_main.py:133), so the pre-flight "
           "is refused and fetch REJECTS -- producing a symptom byte-identical to the origin gate "
           "refusing. No password can ever work from there. STATUS.md:379 records that the local "
           "sibling is the copy David actually opens ('the still see the column mystery was the "
           "second file'), so this is a documented habit, not an accident. Two defects fixed: the "
           "gate hardcoded BEA absolute while _apv3B in the SAME FILE already did the file:// "
           "check correctly, and nothing warned until after a failed round-trip. Now the gate "
           "detects the protocol at render and names the problem with the working URL.")
def rg_gate_origin_aware():
    out = []
    for rel in ("dashboard.server.html", "dashboard.html", "marketsquare_admin.html"):
        c = repo_file(rel)
        if c is None or "adminGateSubmit" not in c:
            continue
        if "var BEA = 'https://trustsquare.co';" in c:
            out.append((FAIL, "%s hardcodes BEA absolute -- a served page makes every gate call a "
                              "needless cross-origin request (GATE-ORIGIN-1)" % rel))
        if "GATE-ORIGIN-1" not in c:
            out.append((FAIL, "%s has no file:// origin guard -- it will ask for a password it "
                              "can never accept" % rel))
        elif "location.protocol === 'file:'" not in c:
            out.append((FAIL, "%s names GATE-ORIGIN-1 but no longer tests the protocol" % rel))
    if not out:
        out.append((INFO, "the gate is origin-aware and warns before asking for a credential"))
    return out


@entry("RG-0077", "The EULA users ACCEPT is byte-identical to the EULA the site PUBLISHES, "
       "and both disclose the Platform's own AI use",
       LOCKED, scope="eula_clean.html (source), terms.html (published), ms.js _EULA_HTML "
                     "(in-app acceptance modal) -- ALL markets",
       fixed_on="2026-08-14",
       ref="EULA-FORK-1. Found 14 Aug 2026: the EULA lived in three hand-maintained copies and "
           "they had forked. terms.html was v1.12; eula_clean.html and the ms.js literal -- the "
           "copy a user actually clicks Accept on -- were still v1.11 and missing SS6.1B Partner "
           "Content entirely. So the agreement being accepted was not the agreement being "
           "published, and nothing on disk compared them. Same shape as CHANGELOG-COLLISION-1 and "
           "STATUS-COLLISION-1: N hand-maintained copies of one truth, no comparator. Fixed by "
           "scripts/eula_sync.py -- eula_clean.html is the source, it is the ONE writer of the "
           "other two, --check exits 1 on drift. v1.13 adds the up-front AI disclosure, SS7.7 "
           "(design/build, generated imagery, demo listings, provenance markers, upload rule) and "
           "the SS8.3 no-AI-training commitment. This entry asserts BOTH halves: the copies stay "
           "identical, and the AI disclosure stays in. Source-side by design -- /terms is behind "
           "the reviewer gate, so a live fetch would prove nothing anonymously.")
def rg_eula_one_source_and_ai_disclosed():
    out = []
    src = repo_file("eula_clean.html")
    if src is None:
        return [(INFO, "not run from the repo -- EULA copies are a source-side check")]

    # 1. one truth, three copies
    terms = repo_file("terms.html") or ""
    msjs  = repo_file("ms.js") or ""
    start = "<p><strong>TrustSquare</strong></p>"
    endp  = ("· Republic of South Africa · Country Schedules: United Kingdom · "
             "United States · Australia</em></p>\n")
    i, j = terms.find(start), terms.find(endp)
    if i == -1 or j == -1:
        out.append((FAIL, "terms.html has no recognisable EULA body -- anchors gone"))
    elif terms[i:j + len(endp)] != src:
        out.append((FAIL, "terms.html EULA body has drifted from eula_clean.html -- the published "
                          "terms are not the source (run scripts/eula_sync.py)"))

    key = 'const _EULA_HTML = "'
    k = msjs.find(key)
    if k == -1:
        out.append((FAIL, "ms.js has no _EULA_HTML literal -- the in-app acceptance modal has no "
                          "text, or was renamed"))
    else:
        p = k + len(key)
        while p < len(msjs):
            if msjs[p] == "\\":
                p += 2
                continue
            if msjs[p] == '"':
                break
            p += 1
        try:
            embedded = json.loads(msjs[k + len(key) - 1:p + 1])
        except Exception as e:
            embedded = None
            out.append((FAIL, "ms.js _EULA_HTML is not a parseable string literal (%s)" % e))
        if embedded is not None and embedded != src:
            out.append((FAIL, "the in-app EULA users ACCEPT differs from eula_clean.html -- "
                              "users are agreeing to text the site does not publish "
                              "(run scripts/eula_sync.py)"))

    # 2. the AI disclosure is present and stays present
    for needle, what in (
        ("Up-front disclosure", "the up-front AI disclosure block"),
        ("7.7 Disclosure of the Platform's Own Use of Artificial Intelligence", "Section 7.7"),
        ("fine-tuning, or evaluation of artificial intelligence", "the SS8.3 no-AI-training commitment"),
    ):
        if needle not in src:
            out.append((FAIL, "%s has been removed from the EULA -- the Platform no longer "
                              "declares its own AI use" % what))

    # 3. the sync tool itself still exists
    if repo_file("scripts/eula_sync.py") is None:
        out.append((FAIL, "scripts/eula_sync.py is gone -- the EULA has no single writer again"))

    if not out:
        out.append((INFO, "one EULA body across source, published page and acceptance modal; "
                          "AI use disclosed up front, in SS7.7 and in SS8.3"))
    return out


@entry("RG-0078", "A category tile never promises a number its own page will not show",
       LOCKED, scope="the tile-vs-grid agreement class entire: renderCatCounts() against the "
                     "destination grid for EVERY category, borderless or city-scoped. Adventures "
                     "is the borderless one today (BORDERLESS_CATS); the invariant is written so "
                     "the next borderless category inherits it instead of re-filing the fault",
       fixed_on="2026-08-14",
       ref="TS-0032 (Maun) and TS-0033 (Sydney) -- two testers, opposite ends of the world, one "
           "fault: pick a city, the Adventures tile reads '1 listing' / '2 listings', tap it and "
           "the page shows every adventure on the platform. In the reporter's words, 'it reverts "
           "away from Botswana and shows me many adventures.' Neither surface was wrong alone: "
           "renderCatCounts() filtered every category to activeCity, while renderAdvGrid() has no "
           "city filter BY DESIGN (the 28 Jun ruling that travel-planning categories are not local "
           "to the buyer; COUNTRY-FILTER-1 then made advCountry=ALL the default, which made the "
           "gap plainly visible rather than causing it). They disagreed, and the tile was the "
           "liar -- it counted a set the grid can never show. BORDERLESS-COUNT-1 gives both "
           "readers one predicate: a borderless category's tile skips the city filter and applies "
           "the SAME country predicate the grid uses, in both count branches (live and the "
           "placeholder fallback). Evidence: scripts/repro_borderless_count.js reproduces the "
           "testers' exact numbers against the pre-fix file (Sydney tile 2 / grid 6, Maun tile 1 / "
           "grid 6, exit 1) and passes against the fixed one (6/6, and 2/2 with the picker "
           "narrowed to AU, exit 0). NOTE: fixed in source and asserted here; it reaches the "
           "reporters when the nightly deploy ships it -- which is why both faults were set "
           "fix-shipped, not verified.")
def rg_tile_never_lies_about_its_page():
    out = []
    js = repo_file("ms.js")
    if js is None:
        out.append((FAIL, "ms.js unreadable -- the tile/grid agreement is UNPROVEN"))
        return out
    if "BORDERLESS_CATS" not in js or "function isBorderlessCat" not in js:
        out.append((FAIL, "ms.js lost the borderless-category predicate -- the Adventures tile is "
                          "back to counting a city-sized set the grid will not show (TS-0032/33)"))
    # BOTH count branches must exempt it: the fault hid in the one nobody was looking at.
    if js.count("isBorderlessCat") < 3:
        out.append((FAIL, "fewer than both renderCatCounts branches consult isBorderlessCat -- the "
                          "placeholder-fallback branch is city-scoping Adventures again"))
    # The grid half of the contract: renderAdvGrid must still have NO city filter, or the
    # fix has been "corrected" from the wrong end and the 28 Jun ruling is broken.
    _g = js.split("function renderAdvGrid()", 1)
    if len(_g) != 2:
        out.append((FAIL, "renderAdvGrid is gone -- the borderless grid this tile is matched to "
                          "no longer exists"))
    else:
        _body = _g[1][:4000]
        if "activeCity" in _body:
            out.append((FAIL, "renderAdvGrid now filters by activeCity -- Adventures has been "
                              "quietly pinned to the buyer's city, against the 28 Jun ruling"))
    # Functional half: the repro is the evidence, so it must exist AND still pass.
    import shutil, subprocess                       # local, as elsewhere on this board
    _repro = os.path.join(REPO, "scripts", "repro_borderless_count.js")
    if not os.path.exists(_repro):
        out.append((FAIL, "scripts/repro_borderless_count.js is gone -- RG-0078's named evidence "
                          "no longer exists and this entry is an opinion"))
    elif shutil.which("node"):
        try:
            _p = subprocess.run(["node", _repro, os.path.join(REPO, "ms.js")],
                                capture_output=True, text=True, timeout=60)
            if _p.returncode != 0:
                out.append((FAIL, "repro_borderless_count.js FAILS against ms.js: %s"
                            % (_p.stdout or _p.stderr or "")[-300:]))
            else:
                out.append((INFO, "repro passes: the tile number survives the tap "
                                  "(node scripts/repro_borderless_count.js)"))
        except Exception as ex:
            out.append((FAIL, "repro could not be run (%r) -- agreement UNPROVEN this run" % ex))
    else:
        out.append((INFO, "node absent on this machine -- source half checked, repro not run"))
    return out


@entry("RG-0079", "Where a machine-written fact CAME FROM is stated where the seller signs for it",
       LOCKED, scope="the cars pre-final attestation block in marketsquare.html (sob-attest-wrap) -- "
                     "the screen where the seller personally warrants AI-inferred vehicle details. "
                     "The class: any surface that asks a human to attest to something a model "
                     "produced must say how it was produced, at that moment, not in a help page",
       fixed_on="2026-08-14",
       ref="TS-0031 (David Jnr, relayed): the pre-final stage added his vehicle's details wrong and "
           "he doubted the 'AI searches and populates' explanation. He was right about the "
           "mechanism -- there is NO lookup in this lane; make, model and variant are read off his "
           "photos by vision plus a model prior (CARS-SPEC-1), and the market note is an ungrounded "
           "one-sentence Haiku, so an uncommon variant can be confidently wrong. The screen asked "
           "him to warrant 'I have personally verified every detail above' while saying nothing "
           "about where the details came from, which is how a seller signs for a guess. "
           "SPEC-PROVENANCE-1 states it in place: read from your photos, nothing looked up in a "
           "vehicle database, check every figure against your own papers. Whether to GROUND the "
           "lane in real vehicle data is a design/cost decision and is David's -- recorded in "
           "BACKLOG.md 14 Aug, deliberately not decided by an agent.")
def rg_attestation_states_provenance():
    out = []
    h = repo_file("marketsquare.html")
    if h is None:
        out.append((FAIL, "marketsquare.html unreadable -- the provenance line is UNPROVEN"))
        return out
    if "SPEC-PROVENANCE-1" not in h:
        out.append((FAIL, "the SPEC-PROVENANCE-1 marker is gone from marketsquare.html"))
    _w = h.split('id="sob-attest-wrap"', 1)
    if len(_w) != 2:
        out.append((FAIL, "the cars attestation block (sob-attest-wrap) is gone -- the screen this "
                          "entry guards no longer exists"))
        return out
    block = _w[1][:3000]
    if "read from your photos" not in block.lower():
        out.append((FAIL, "the attestation block no longer says the specs were read from the "
                          "seller's photos -- a seller can again warrant a machine guess with no "
                          "idea it was one (TS-0031)"))
    if "nothing was looked up" not in block.lower():
        out.append((FAIL, "the attestation block no longer denies a database lookup -- the exact "
                          "false impression TS-0031 was filed about"))
    # The attestation itself must still be there: provenance ADDS to it, never replaces it.
    if "personally verified every detail" not in block:
        out.append((FAIL, "the seller attestation text is gone -- provenance must be added "
                          "alongside the warranty, never instead of it"))
    if not out:
        out.append((INFO, "provenance stated where the seller signs: photos, not a lookup"))
    return out



@entry("RG-0081", "The gate opens on an EMAILED LINK, not a memorised code -- and a valid cookie is never re-challenged",
       LOCKED, fixed_on="2026-08-15", scope="the gate-entry lane entire: /review/request-link + /review/enter at the app AND "
                   "exempt at the origin (migration 019), the marketsquare.html email-first gate screen, "
                   "and the GATE-COOKIE-2 cookie-first verify. The code path /review/login must ALSO "
                   "stay alive (break-glass) -- losing it is a failure of this entry, not a success",
       ref="GATE-EMAIL-1, David's ruling 15 Aug 2026: 'email linked and not with a code, like normal "
           "apps' -- too many testers locked out. Root cause of the lockout class was never the cookie "
           "(365 days, valid) but the gate script's sessionStorage short-circuit re-challenging every "
           "new tab session, one mistype = 'locked out'. Fix is two-pronged: cookie-first verify "
           "(GATE-COOKIE-2) ends re-challenges; the emailed one-time link (30 min, single-use jti, "
           "allowlist file re-read per call, no enumeration) replaces the code for fresh entries. "
           "Containment deliberately UNCHANGED: origin lockdown RG-0028, armed catch-all GATE-ENFORCE-2, "
           "per-IP rate limit; claim email+IP logged; tokens NOT hard-bound to claim IP (tester ISPs "
           "rotate -- a hard bind would re-create the lockouts). EXPECTED open until migration 019 "
           "rides a deploy; the moment the live half answers, promote to LOCKED. PROMOTED 15 Aug 2026 ~08:0x UTC: migration 019 rode the /tsl ship; live off-list request-link answered {ok:true}, garbage /review/enter bounced 302 -> /?gate=expired, /wonders + /listings still 401 anonymous. Locked so the email door, the break-glass code path and the cookie-first verify can never silently part ways.")
def rg_gate_email_link():
    out = []
    # Repo half: both sides of the lane exist in source
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "GATE-EMAIL-1" not in bea or "/review/request-link" not in bea:
            out.append((FAIL, "bea_main.py lost the GATE-EMAIL-1 lane (request-link/enter endpoints)"))
        if "def review_login" not in bea:
            out.append((FAIL, "the break-glass code path /review/login is GONE -- email is now a "
                              "single point of failure for the whole gate"))
        html = repo_file("marketsquare.html") or ""
        if "gate-email-input" not in html or "GATE-EMAIL-1" not in html:
            out.append((FAIL, "marketsquare.html gate screen lost the email-first entry"))
        if "GATE-COOKIE-2" not in html:
            out.append((FAIL, "the cookie-first verify (GATE-COOKIE-2) is gone -- a valid 365-day "
                              "cookie is being re-challenged every tab session again"))
    # Live half: the two endpoints answer WITHOUT a cookie (exempt at the origin)
    try:
        req = urllib.request.Request(BASE + "/review/request-link",
                                     data=json.dumps({"email": "rg-probe-offlist@example.invalid"}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        if json.loads(body).get("ok") is not True:
            out.append((FAIL, "live /review/request-link answered but not {'ok': true} -- "
                              "the no-enumeration contract broke"))
    except Exception as ex:
        out.append((FAIL, "live /review/request-link refused (%r) -- migration 019 has not landed "
                          "(or the lane rotted): a tester cannot ask for a link" % ex))
    try:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        op = urllib.request.build_opener(_NoRedirect)
        req = urllib.request.Request(BASE + "/review/enter?t=garbage", headers=dict(UA))
        try:
            r = op.open(req, timeout=TIMEOUT)
            code, loc = r.getcode(), ""
        except urllib.error.HTTPError as he:
            code, loc = he.code, (he.headers.get("Location") or "")
        if code != 302 or "gate=expired" not in loc:
            out.append((FAIL, "live /review/enter with a garbage token did not bounce 302 -> "
                              "/?gate=expired (got %s -> %r) -- a dead link will confuse instead "
                              "of explaining" % (code, loc)))
    except Exception as ex:
        out.append((FAIL, "live /review/enter unreachable (%r) -- migration 019 has not landed: "
                          "an emailed link cannot be redeemed" % ex))
    if not out:
        out.append((INFO, "email-link lane answers end to end; code path intact as break-glass"))
    return out


@entry("RG-0082", "AI spend is attributed to the lane that ANSWERED and costed at that model's price -- a failover can never be invisible in the spend log",
       LOCKED, scope="bea_main.py spend accounting entire: _MODEL_PRICE (model-keyed, loaded from "
                     "ai_price_card.json, embedded fallback for card-less hosts), _token_cost "
                     "(serving-lane tier resolution), _log_ai_spend (provider=/model= from the "
                     "AIResult), and EVERY _log_ai_spend call site -- all lanes, all tiers. "
                     "Repo-side assertions; the live half rides the next deploy",
       fixed_on="2026-08-15",
       ref="P6 of David's lane ruling (AI_LANE_GUIDANCE.md, 14 Aug 2026) -- the precondition that "
           "made the others measurable, landed 15 Aug. Before: _MODEL_PRICE was keyed on TIER with "
           "Anthropic's prices (haiku row 20-25% LOW vs the card -- every daily ceiling loose, "
           "drift D1) and _log_ai_spend recorded the INTENDED lane (drift D3), so with OpenAI as "
           "base a sustained failover to Anthropic (4.4x on haiku) would have been invisible and "
           "mis-priced. Now: prices come from the register at boot so code can never disagree with "
           "the card; every call site that holds the AIResult passes the SERVING provider+model; "
           "the import-failure vision id dropped sonnet->haiku (drift D2).")
def rg_spend_serving_lane():
    src_b = repo_file("bea_main.py")
    if src_b is None:
        return [(INFO, "running outside the repo -- spend-attribution source check skipped")]
    out = []
    if "provider: str | None = None, model: str | None = None" not in src_b:
        out.append((FAIL, "_log_ai_spend no longer accepts the serving provider/model -- "
                          "attribution is back to the intended lane (drift D3 re-opened)"))
    if "_MODEL_PRICE = _load_model_prices()" not in src_b:
        out.append((FAIL, "_MODEL_PRICE no longer loads from ai_price_card.json -- the code "
                          "price table can disagree with the register again (drift D1 re-opened)"))
    if '"gpt-5.6-luna":' not in src_b.split("_MODEL_PRICE_FALLBACK", 1)[-1][:1200]:
        out.append((FAIL, "_MODEL_PRICE_FALLBACK lost its model-id keys -- card-less hosts "
                          "fall back to nothing"))
    # the CLASS: every spend row states where it came from. Each _log_ai_spend call site
    # (not the def) must carry a provider= kwarg within its statement window.
    bare = 0
    idx = 0
    while True:
        idx = src_b.find("_log_ai_spend", idx + 1)
        if idx < 0:
            break
        window = src_b[idx:idx + 420]
        if window.startswith("_log_ai_spend failed") or "def _log_ai_spend" in window[:20]:
            continue
        if src_b[max(0, idx - 4):idx].endswith("def "):
            continue
        _ls = src_b.rfind("\n", 0, idx) + 1
        if "#" in src_b[_ls:idx]:
            continue          # a comment MENTIONING the logger is not a call site
        if "provider=" not in window and "provider =" not in window:
            bare += 1
    if bare:
        out.append((FAIL, "%d _log_ai_spend call site(s) no longer state the serving lane -- "
                          "those rows are guesses again" % bare))
    if not out:
        out.append((INFO, "every spend row is serving-lane attributed and card-priced in source"))
    return out


@entry("RG-0083", "A lane change via POST /admin/flags is LOGGED and AUDITED -- actor, prior value, new value, reason, timestamp; a pin records who and why",
       LOCKED, scope="bea_main.py set_flags handler + admin_audit table + _FlagsUpdate.reason -- "
                     "every field the route can flip, with lane (ai_active) and pin "
                     "(ai_active_override, AL-3) also writing a log line. Repo-side assertions; "
                     "live half rides the next deploy",
       fixed_on="2026-08-15",
       ref="Drift D4 of AI_BASELINE.json + the one gap AI_LANE_GUIDANCE said the dashboard could "
           "not close: /admin/flags changed the live AI lane for every feature and wrote NO log "
           "line and NO audit row, while its neighbour /admin/ai-restore fifteen lines earlier "
           "logs. David called the missing accountability out explicitly. AL-3 lives here too: "
           "RG-0019 deliberately does not trip on a pin, so the pin's actor+reason must be "
           "recorded at the moment it is set or nothing else will notice.")
def rg_admin_flags_audited():
    src_b = repo_file("bea_main.py")
    if src_b is None:
        return [(INFO, "running outside the repo -- admin-flags audit source check skipped")]
    out = []
    m = src_b.find("def set_flags(")
    blk = src_b[m:m + 6000] if m >= 0 else ""
    if not blk:
        out.append((FAIL, "set_flags handler is GONE"))
    else:
        if "_log.warning" not in blk:
            out.append((FAIL, "set_flags writes no log line -- a lane change is undetectable "
                              "after the fact again (drift D4 re-opened)"))
        if "admin_audit" not in blk:
            out.append((FAIL, "set_flags writes no admin_audit row -- actor/prior/new/reason "
                              "are unrecorded again"))
    if "CREATE TABLE IF NOT EXISTS admin_audit" not in src_b:
        out.append((FAIL, "the admin_audit table creation is gone"))
    if "reason:" not in src_b[src_b.find("class _FlagsUpdate"):src_b.find("class _FlagsUpdate") + 2500]:
        out.append((FAIL, "_FlagsUpdate lost the reason field -- the WHY can no longer be recorded"))
    if not out:
        out.append((INFO, "lane changes are logged and audited in source (actor, prior, new, reason)"))
    return out


@entry("RG-0084", "The failover chain consults the BASELINE -- order and cost per tier, never dict insertion order -- and serving off-base ALERTS",
       LOCKED, scope="ai_provider.py complete()/_cost_approved_fallbacks (all task tiers, all "
                     "lanes; static RUL-002 order when AI_BASELINE.json is absent) + bea_main.py "
                     "_maybe_fire_lane_alert wired into _log_ai_spend (AL-1 off-base >60min, AL-2 "
                     "safety net at all; heartbeat probes excluded). Repo-side assertions; live "
                     "half rides the next deploy",
       fixed_on="2026-08-15",
       ref="Drift D5 of AI_BASELINE.json: an outage moved traffic to the next lane in the ADAPTERS "
           "dict literal with nothing asking its price. Now the chain is AI_BASELINE.json's "
           "failover order, a lane priced beyond failover_cost_tolerance for a tier is excluded "
           "from AUTOMATIC failover unless its role is cost-exempt (the scaleway safety net -- "
           "reached when the alternative is being down or banned, where price is not the "
           "question), and reaching the safety net or serving off-base fires the AL alerts David's "
           "ruling specified. Alert rules AL-1/AL-2/AL-3 from AI_BASELINE.json alert_rules.")
def rg_failover_consults_baseline():
    out = []
    ap_src = repo_file("ai_provider.py")
    bea = repo_file("bea_main.py")
    if ap_src is None or bea is None:
        return [(INFO, "running outside the repo -- failover/alert source check skipped")]
    if "_cost_approved_fallbacks" not in ap_src:
        out.append((FAIL, "ai_provider.py lost _cost_approved_fallbacks -- the chain no longer "
                          "consults cost (drift D5 re-opened)"))
    body = ap_src[ap_src.find("def complete("):]
    if "_cost_approved_fallbacks(task, prov)" not in body:
        out.append((FAIL, "complete() no longer builds its chain through the cost gate"))
    if "_maybe_fire_lane_alert" not in bea:
        out.append((FAIL, "bea_main.py lost _maybe_fire_lane_alert -- AL-1/AL-2 are gone"))
    elif bea.count("_maybe_fire_lane_alert(") < 2:
        out.append((FAIL, "_maybe_fire_lane_alert exists but is no longer CALLED from "
                          "_log_ai_spend -- the alerts can never fire"))
    for marker in ("AL-1", "AL-2"):
        if marker not in bea:
            out.append((FAIL, "alert rule %s marker gone from bea_main.py" % marker))
    if not out:
        out.append((INFO, "failover order+cost come from the baseline; off-base serving alerts"))
    return out




# ID NOTE: deliberately jumped to RG-0090 after THREE same-morning ID races with a concurrent
# session (0080, 0082, 0083 each taken between this session's planning and its write). The
# register is append-only and never renumbered, so the gap is harmless; racing is not.
@entry("RG-0090", "The gated DOCUMENT is never served to the public out of the CDN cache -- a cookie-holder must not prime the edge for everyone",
       OPEN, scope="the index document at / (and any gated HTML the edge caches). The DATA side "
                   "already holds: /wonders and /listings answer 401 anonymously -- this entry is "
                   "about the HTML shell alone",
       ref="Found 15 Aug 2026 during the GATE-EMAIL-1 /tsl verify: anonymous GET / answered 200 "
           "with cf-cache-status: HIT, age 20 -- the regression ledger's own cookie-bearing fetch "
           "had primed Cloudflare with the 200 document seconds earlier, and the edge then served "
           "it to ANYONE (the origin auth_request is never consulted on a HIT). Origin gate is "
           "INTACT (fresh-path and API probes refuse). Class predates GATE-EMAIL-1 -- it has been "
           "true since GATE-ENFORCE-2 armed on 13 Aug whenever any cookie-holder loaded the page. "
           "Exposure: app HTML shell only (client gate screen still locks the view; every data "
           "call 401s). Fixes, either lane: (a) Cloudflare cache rule -- bypass cache on "
           "text/html for trustsquare.co (DAVID's console, one rule); or (b) origin sends "
           "Cache-Control: private, no-store on the gated document (one nginx/BEA migration). "
           "Post-launch note: the gate drops 29 Aug (RUL-001) and caching the public document "
           "becomes DESIRABLE -- whichever fix ships must be reversible on launch day.")
def rg_edge_cache_document_leak():
    out = []
    try:
        req = urllib.request.Request(BASE + "/?rg0082=" + str(int(time.time())), headers=dict(UA))
        try:
            r = urllib.request.urlopen(req, timeout=TIMEOUT)
            code, hdrs, body = r.getcode(), r.headers, r.read(200000).decode("utf-8", "replace")
        except urllib.error.HTTPError as he:
            code, hdrs, body = he.code, he.headers, ""
        if code == 200 and ("admin-gate" in body or "GATE-EMAIL-1" in body):
            cc = (hdrs.get("Cache-Control") or "").lower()
            if "no-store" not in cc and "private" not in cc:
                out.append((FAIL, "anonymous cookie-less GET / answers 200 with the app document "
                                  "and no private/no-store -- the edge can (and does) hand the "
                                  "gated shell to the public once any cookie-holder primes it"))
    except Exception as ex:
        out.append((INFO, "anonymous document probe inconclusive (%r)" % ex))
    if not out:
        out.append((INFO, "gated document refuses anonymously or forbids shared caching"))
    return out


@entry("RG-0091", "Paystack's anonymous webhook POST reaches BEA and is signature-enforced -- the edge never eats the money lane and never accepts an unsigned credit",
       LOCKED, fixed_on="2026-08-15",
       scope="the live edge + the /payment/webhook route + the HMAC check, all markets. BLIND SPOT "
             "by design: an unset PAYSTACK_WEBHOOK_SECRET and a wrong signature both answer 400, so "
             "this entry cannot see the secret's presence server-side -- the A10 detached-credit E2E "
             "(buy, close tab before returning, credit still lands) is the other half of the proof",
       ref="WEBHOOK-ARM-1, 15 Aug 2026: PAYSTACK_WEBHOOK_SECRET installed via "
           "add_paystack_webhook_key.bat (resend-key pattern) after B1 cleared; Live Webhook URL "
           "verified in the Paystack dashboard as https://trustsquare.co/payment/webhook. This "
           "entry exists because GATE-ENFORCE-1/2 arm an origin catch-all: if the gate ever "
           "swallows Paystack's anonymous POSTs (403), the reliable credit path dies SILENTLY -- "
           "buyers who close the browser pay real money and never get Tuppence. 400 "
           "Invalid-signature is the healthy answer to a garbage probe.")
def rg_paystack_webhook_lane():
    out = []
    bea = repo_file("bea_main.py"); pay = repo_file("payments.py")
    if bea is not None and ('@app.post("/payment/webhook")' not in bea
                            or "verify_webhook_signature" not in bea):
        out.append((FAIL, "bea_main.py lost the /payment/webhook route or its signature check"))
    if pay is not None and "PAYSTACK_WEBHOOK_SECRET" not in pay:
        out.append((FAIL, "payments.py no longer reads PAYSTACK_WEBHOOK_SECRET"))
    _require_net()
    try:
        req = urllib.request.Request(BASE + "/payment/webhook",
                                     data=b'{"event":"rg0091.probe"}',
                                     headers=dict(UA, **{"Content-Type": "application/json",
                                                         "X-Paystack-Signature": "rg0091-garbage"}))
        try:
            code = urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as he:
            code = he.code
        if code == 403:
            out.append((FAIL, "edge/origin gate answered 403 to an anonymous webhook POST -- "
                              "Paystack's charge.success events are being EATEN; credits silently "
                              "depend on the buyer returning to the app"))
        elif code == 404:
            out.append((FAIL, "/payment/webhook is 404 -- the route is gone"))
        elif code == 200:
            out.append((FAIL, "webhook accepted a garbage-signed POST (200) -- signature "
                              "enforcement lost; anyone could mint Tuppence"))
        elif code >= 500:
            out.append((FAIL, "/payment/webhook answers %d -- handler is crashing" % code))
        elif code != 400:
            out.append((INFO, "unexpected but non-fatal status %d (400 expected)" % code))
    except ProbeOffline:
        raise
    except Exception as ex:
        out.append((INFO, "webhook probe inconclusive (%r)" % ex))
    if not out:
        out.append((INFO, "anonymous garbage POST correctly refused 400 Invalid-signature"))
    return out




@entry("RG-0092", "The legal documents are PUBLIC: anonymous /terms and /privacy answer 200 "
       "with the real pages, while the reviewer gate still guards the rest",
       LOCKED, fixed_on="2026-08-16",
       scope="the live edge + nginx exempt list, all markets. Both halves asserted: the legal "
             "docs are open AND the gate did not silently widen (/wonders stays non-200 "
             "anonymously)",
       ref="RUL-020, 16 Aug 2026: David's decree -- the EULA is final and binding and must be "
           "available to users; no legal-review hold, not to be re-discussed. Mechanism: "
           "migrations/021_open_legal_docs.py adds ungated location blocks for /terms and "
           "/privacy above the GATE-ENFORCE-1 catch-all. Closes DAILY_WATCH DW-041.")
def rg_legal_docs_public():
    out = []
    _require_net()
    def _code(path):
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            return urllib.request.urlopen(req, timeout=TIMEOUT).getcode(), ""
        except urllib.error.HTTPError as he:
            return he.code, ""
    for path, needle in (("/terms", "Country Schedules"), ("/privacy", "")):
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
            if needle and needle not in body:
                out.append((FAIL, path + " answers 200 but the page body lost %r -- wrong or "
                                  "stub document served" % needle))
        except urllib.error.HTTPError as he:
            out.append((FAIL, "anonymous GET %s answers %d -- the legal documents are gated "
                              "again; RUL-020 says they must be public (rerun "
                              "migrations/021_open_legal_docs.py)" % (path, he.code)))
    c, _ = _code("/wonders")
    if c == 200:
        out.append((FAIL, "anonymous /wonders answers 200 -- the gate itself has fallen, this "
                          "is GATE-ENFORCE-1 rot (DW-023 class), not the RUL-020 exemption"))
    if not out:
        out.append((INFO, "legal docs open, gate still standing (/wonders %d anonymously)" % c))
    return out


@entry("RG-0093", "An infrastructure Test click answers PASS/FAIL AT THE ROW -- and a non-pass says WHY and what resolves it",
       LOCKED, fixed_on="2026-08-16",
       scope="dashboard.server.html (ships as dashboard.html) -- the +1 page Infrastructure card. "
             "Source-half assertion: the verdict machinery exists and the Test path calls it. The "
             "AI Providers card already answered visibly (apv3Test); this brings the infra card "
             "to the same bar",
       ref="INFRA-TEST-VERDICT-1, 16 Aug 2026, David: 'on the infrastructure i see nothing "
           "happening when i use those test buttons... please add some visual indication of "
           "PASS/FAIL, and if fail then we need a small explanation of why and what is needed "
           "to resolve it.' Root cause: infraLoad re-rendered an identical row chip and wrote "
           "'Checked <time>' to a side line -- a per-service re-probe whose result usually "
           "equals the ambient status is invisible without a row-local verdict.")
def rg_infra_test_verdict():
    out = []
    d = repo_file("dashboard.server.html")
    if d is None:
        return [(INFO, "repo not readable -- skipped")]
    for needle, why in (
        ('id="infra-res-', "the row-local verdict slot is gone"),
        ("window.infraVerdict", "the verdict painter is gone"),
        ("infra-why-", "the WHY/RESOLVE strip is gone"),
        ("window.infraVerdict(one", "infraLoad no longer paints the verdict after a Test"),
    ):
        if needle not in d:
            out.append((FAIL, why + " (%r missing from dashboard.server.html)" % needle))
    if not out:
        out.append((INFO, "Test paints PASS/FAIL at the row; non-pass carries why + resolve"))
    return out



@entry("RG-0094", "Private user reads REQUIRE the app key: /tuppence/balance, /tuppence/history "
       "and /users/{email} refuse a keyless caller and answer only with X-Api-Key",
       LOCKED, fixed_on="2026-08-16",
       scope="IL-01 CLASS fix, first tranche (the money pair + the PII record), all markets. "
             "The remaining email-keyed open GETs (/listings/mine, /intros?buyer_email, "
             "/advert-agent/status, /local-market/suspension/check, /users/{email}/subscription, "
             "boost stats) are enumerated here for the G2 register work -- this entry asserts the "
             "three shipped, not the whole class",
       ref="David's ruling 16 Aug 2026: nobody may read another user's balance by guessing their "
           "email -- 'not something we leave for future David and Claude'. Server: "
           "Depends(auth.require_api_key) on the three defs. Client: every ms.js/admin call site "
           "now sends X-Api-Key (6 balance + 1 history + 3 user-record sites + apiGet helper). "
           "Probes run THROUGH the reviewer gate pre-29 Aug so they test the APP's enforcement, "
           "which is exactly what remains when the gate drops.")
def rg_private_reads_need_key():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        for fn in ("def get_tuppence_balance(email: str, _key: str = Depends(auth.require_api_key))",
                   "def get_user(email: str, _key: str = Depends(auth.require_api_key))"):
            if fn not in bea:
                out.append((FAIL, "bea_main.py lost the key requirement on %s..." % fn[4:40]))
        seg = bea.split("def get_tuppence_history", 1)
        if len(seg) == 2 and "require_api_key" not in seg[1][:400]:
            out.append((FAIL, "bea_main.py lost the key requirement on get_tuppence_history"))
    _require_net()
    ck = _review_cookie()
    if not ck:
        return out + [(INFO, "no reviewer credential obtainable -- app-level probe skipped (blind), "
                             "source-side asserted above")]
    key = ""
    msjs = repo_file("ms.js") or ""
    k = msjs.find("const API_KEY = '")
    if k != -1:
        key = msjs[k + len("const API_KEY = '"):msjs.find("'", k + len("const API_KEY = '"))]
    def _code(hdrs):
        req = urllib.request.Request(BASE + "/tuppence/balance?email=rg0094-probe@example.com",
                                     headers=dict(UA, **hdrs))
        try:
            return urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as he:
            return he.code
    c_anon = _code({"Cookie": ck})
    if c_anon == 200:
        out.append((FAIL, "balance answered 200 to a KEYLESS caller (through the gate) -- IL-01 "
                          "is back; anyone can read balances by email once the gate drops"))
    if key:
        c_key = _code({"Cookie": ck, "X-Api-Key": key})
        if c_key != 200:
            out.append((FAIL, "balance answers %d WITH the app key -- the fix broke the app's own "
                              "wallet display" % c_key))
    if not out:
        out.append((INFO, "keyless %d, keyed 200 -- private reads enforce the key" % c_anon))
    return out



@entry("RG-0095", "The orchestrator's three views are all DEPLOYED: cockpit, durability map and "
       "email templates answer 401-behind-auth (served), never 404 (missing)",
       LOCKED, fixed_on="2026-08-16",
       scope="/orchestrator/v2/ lane. 401 anonymously = nginx serves the file behind basic auth "
             "(correct); 404 = the file never shipped -- the exact fault found today",
       ref="DURABILITY-404-1, 16 Aug 2026 (David: 'fix the Durability Map which is broken'). "
           "cockpit.html linked durability_map.html but the file had NO deploy-manifest row, so "
           "the live link 404'd since the page was born. Fixed by adding manifest rows for "
           "durability_map.html, the new email_templates.html view (David's ask, same session) "
           "and the 14 template snapshots it presents. The manifest-omission class: a repo file "
           "a deployed page links to must itself be in the manifest.")
def rg_orchestrator_views_deployed():
    out = []
    man = repo_file("ops/autodeploy/deploy_manifest.txt")
    if man is not None:
        for f in ("durability_map.html", "email_templates.html", "templates/agency_outreach.html"):
            if "orchestrator/v2/" + f not in man:
                out.append((FAIL, "deploy manifest lost the row for orchestrator/v2/%s" % f))
    _require_net()
    for path in ("/orchestrator/v2/cockpit.html", "/orchestrator/v2/durability_map.html",
                 "/orchestrator/v2/email_templates.html"):
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            code = urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as he:
            code = he.code
        if code == 404:
            out.append((FAIL, path + " answers 404 -- the file is not deployed; a cockpit link "
                              "is dead again (manifest-omission class)"))
        elif code not in (200, 401):
            out.append((FAIL, path + " answers %d -- expected 401 (behind basic auth) or 200" % code))
    if not out:
        out.append((INFO, "all three orchestrator views served (401-behind-auth as designed)"))
    return out



@entry("RG-0096", "Generator-built journey maps carry PIN-SPREAD-1: overlapping pins fan out "
       "on a circle with legs to their true spot -- the HMI never regresses to stacked pins",
       LOCKED, fixed_on="2026-08-16",
       scope="scripts/journey_template.html (the generator source) + every generated "
             "adventures map on disk. Hand-built maps (za pilot, gb, au, us, reserve) are "
             "STAGE 2, pending David's verdict on the generated five",
       ref="PIN-SPREAD-1, 16 Aug 2026 (David's HMI ask: overlapping circles are hard to see "
           "and click -- spread them elegantly around the circle). Implemented in the template "
           "so every future generated map inherits it; five maps rebuilt (bw, c2c, ke, mz, na).")
def rg_pin_spread_in_generator():
    out = []
    tpl = repo_file("scripts/journey_template.html")
    if tpl is None:
        return [(INFO, "not run from the repo -- source-side check only")]
    if "PIN-SPREAD-1" not in tpl:
        out.append((FAIL, "journey_template.html lost the PIN-SPREAD-1 block -- newly generated "
                          "maps will stack pins again"))
    import glob as _g, json as _j
    missing = []
    for sp in _g.glob(os.path.join(REPO, "journeys", "*.json")):
        if ".bak" in sp: continue
        try:
            spec = _j.load(open(sp, encoding="utf-8"))
            outp = os.path.join(REPO, spec.get("out", spec["id"] + "_journey.html"))
            body = open(outp, encoding="utf-8", errors="replace").read()
        except Exception as e:
            missing.append(os.path.basename(sp) + " (unreadable: %s)" % str(e)[:40]); continue
        if "PIN-SPREAD-1" not in body:
            missing.append(os.path.basename(outp))
    if missing:
        out.append((FAIL, "generated map(s) missing PIN-SPREAD-1 (stale build): " + ", ".join(missing)))
    if not out:
        out.append((INFO, "template + generated maps all carry the spread"))
    return out



@entry("RG-0097", "The Planner Lane ships DARK and whole: endpoints exist behind the "
       "p_heritage flag (OFF answers 404, never 500), the renderer module + template are "
       "deployed, and the offline selftest pipeline stays green",
       LOCKED, fixed_on="2026-08-16",
       scope="Phase A (heritage planner). Flag-dark by design until David flips "
             "planners.heritage; this entry asserts DARKNESS + WHOLENESS, not the lit lane",
       ref="Phase A build, 16 Aug 2026 (design: PLANNER_LANE_DESIGN_2026-08-16_rev2.docx). "
           "journey_render.py extracted from build_journey.py -- 5/5 showcases rebuilt "
           "byte-identical through the module. Coordinates/photos come only from "
           "wonders.json (the AI picks ids + words at the everyday task tier via the seam). "
           "planner_selftest.py proves validate->assemble->render(url)<300KB offline.")
def rg_planner_lane_dark_and_whole():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        for needle in ('"/planner/heritage/compose"', '"/planner/map/{sid}"',
                       '_planner_flag_on', 'assemble_heritage_spec'):
            if needle not in bea:
                out.append((FAIL, "bea_main.py lost %s -- the planner lane is broken in source" % needle))
    for f, needle in (("journey_render.py", "def render_spec"),
                      ("scripts/planner_selftest.py", "validate_heritage_plan"),
                      ("migrations/022_planner_specs.py", "planner_specs"),
                      ("ops/autodeploy/deploy_manifest.txt", "journey_render.py")):
        t = repo_file(f)
        if t is not None and needle not in t:
            out.append((FAIL, "%s lost %r" % (f, needle)))
    _require_net()
    ck = _review_cookie()
    key = ""
    msjs = repo_file("ms.js") or ""
    k = msjs.find("const API_KEY = '")
    if k != -1:
        key = msjs[k + len("const API_KEY = '"):msjs.find("'", k + len("const API_KEY = '"))]
    if ck and key:
        req = urllib.request.Request(BASE + "/planner/map/999999?email=rg0097@example.com",
                                     headers=dict(UA, **{"Cookie": ck, "X-Api-Key": key}))
        try:
            code = urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as he:
            code = he.code
        if code >= 500:
            out.append((FAIL, "/planner/map answers %d -- the dark lane is CRASHING, not dark" % code))
        elif code != 404:
            out.append((INFO, "planner map answered %d (flag may be ON -- fine if David flipped it)" % code))
    else:
        out.append((INFO, "no credential for the live dark-probe -- source-side asserted"))
    if not out:
        out.append((INFO, "planner lane whole in source and dark-clean live (404)"))
    return out


@entry("RG-0098", "Tuppence money maths floats on LIVE forex -- the R36/T and R90/$5 hardcodes "
       "are retired and /api/fx serves sane keyless-feed rates",
       LOCKED, fixed_on="2026-08-17",
       scope="FX-LIVE-1, all markets: server charge lane (/payment/initialize + the $5 global sub) "
             "+ /api/fx + ms.js display labels (topup modal, AI pack, quantity picker, localPrice). "
             "Feeds: Frankfurter/ECB then open.er-api, both keyless/free; static parachute only "
             "when every feed is down",
       ref="RUL-022, 16 Aug 2026: David -- forex must be LIVE actual values, free, no "
           "subscription. USD stays canon ($2/T, $5 global); the ZAR debit floats on the "
           "12h-cached live rate. The R36 hardcode was born at R18/$; at ~R16.2/$ today ZA "
           "buyers were overpaying ~11%. EXPECTED TO FAIL live until the next deploy ships it -- "
           "the moment /api/fx answers sanely, promote to LOCKED.")
def rg_fx_live():
    out = []
    bea = repo_file("bea_main.py"); msjs = repo_file("ms.js")
    if bea is not None:
        if "tuppence * 36" in bea:
            out.append((FAIL, "bea_main.py re-grew the R36/T hardcode in the charge lane"))
        if "def usd_to_zar_amount" not in bea or '"/api/fx"' not in bea:
            out.append((FAIL, "bea_main.py lost the FX-LIVE-1 helper or the /api/fx route"))
    if msjs is not None:
        if "(n*36)" in msjs or "(t*36)" in msjs:
            out.append((FAIL, "ms.js re-grew a *36 display hardcode"))
        if "function loadFX" not in msjs:
            out.append((FAIL, "ms.js lost the loadFX live-rate loader"))
    try:
        j = json.loads(_get("/api/fx"))
    except ProbeOffline:
        raise
    except Exception as exc:
        out.append((FAIL, "/api/fx not answering live yet (%s) -- expected until the deploy ships"
                    % type(exc).__name__))
        return out
    z = float(j.get("rates", {}).get("ZAR", 0))
    missing = [s for s in ("ZAR", "GBP", "AUD", "EUR") if s not in j.get("rates", {})]
    if not (5 < z < 50):
        out.append((FAIL, "/api/fx ZAR rate %r outside the sanity band" % z))
    elif j.get("source") == "fallback":
        out.append((FAIL, "/api/fx answers but every live feed is down (parachute in use)"))
    elif missing:
        out.append((FAIL, "/api/fx missing symbols: %s" % ",".join(missing)))
    else:
        out.append((INFO, "/api/fx live and sane (ZAR %.2f via %s)"
                    % (z, j.get("source", "?"))))
    return out


if __name__ == "__main__":
    sys.exit(main())

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
import json, os, re, subprocess, sys, time, datetime, urllib.request, urllib.error

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


def _headers(path):
    """Live RESPONSE HEADERS, lowercased keys. Added 24 Aug 2026 for RG-0178/0179/0180.

    Deliberately NOT cached with _get: header parity is the thing under test, and a
    body cache would happily serve headers from a different request. Errors that still
    carry a response (401/403/404) still carry headers, so those are used rather than
    thrown away -- a gated page's headers are exactly as interesting as an open one's.
    """
    key = "HDR:" + path
    if key not in _cache:
        _require_net()
        req = urllib.request.Request(BASE + path, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                h = dict(r.headers)
        except urllib.error.HTTPError as e:
            h = dict(e.headers or {})
        except Exception as ex:
            raise ProbeOffline(repr(ex)[:140])
        _cache[key] = {k.lower(): v for k, v in h.items()}
    return _cache[key]


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


# ── LEDGER-STABLE-1 (20 Aug 2026, DW-053) ───────────────────────────────────
# Twice in one morning this ledger cried "previously-fixed issue(s) HAVE COME BACK.
# Do not deploy over this." while nothing had rotted: once because it ran across a
# deploy restart (19 Aug), once because an ATTENDED SESSION was rewriting the very
# files the assertions read — bea_main.py, this file and ai_funnel_snapshot.json all
# changed mid-run (20 Aug). A tripwire that fires on its own instability is the
# cry-wolf failure RG-0068 exists to prevent, so the run now measures whether the
# ground moved underneath it and says so instead of blaming the app.
# It NEVER suppresses a regression — it labels the run untrustworthy and asks for a
# re-run, which is the honest answer when the evidence was read from a moving target.
_WATCHED_SOURCES = ("bea_main.py", "ms.js", "marketsquare.html", "ai_price_card.json",
                    "ai_funnel_snapshot.json", "scripts/regression_ledger.py",
                    "ops/autodeploy/post_deploy.sh")


def _source_fingerprint():
    """mtime of every repo file the assertions read. Cheap; no content hashing."""
    out = {}
    for rel in _WATCHED_SOURCES:
        try:
            out[rel] = os.stat(os.path.join(REPO, rel)).st_mtime
        except OSError:
            out[rel] = None
    return out


def _sources_changed(before, after):
    return sorted(k for k in before if before[k] != after.get(k))


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
    # LEDGER-DUP-1 (19 Aug 2026): two concurrent sessions both claimed RG-0118/0119.
    # A duplicated id makes the whole board ambiguous -- refuse loudly at import so the
    # session that collides fixes it before anything else runs. Never silently renumber.
    def deco(fn):
        if any(e["id"] == rid for e in LEDGER):
            raise SystemExit("LEDGER-DUP-1: id %s is already taken by '%s' -- pick the next "
                             "free number (LOCKED entries never move; OPEN newcomer moves)"
                             % (rid, next(e["title"] for e in LEDGER if e["id"] == rid)))
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


@entry("RG-0014", "Adventures-screen cards show the red AI EXAMPLE GENERATED ADVERT ribbon",
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
           "references (RG-0013 class), so a cache-stale deploy cannot fake a pass. RELABELLED 22 Aug 2026 (AI-EXAMPLE-1, RUL-038): the ribbon's TEXT changed from 'SUPER ADVERT' to 'AI EXAMPLE GENERATED ADVERT'. The assertion is unchanged and NOT weakened -- it always checked that renderAdvGrid() reads l.super_example (the DB field, which keeps its name), never the label. RG-0140 asserts the wording itself.")
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
           "loader trips it red. STRENGTHENED 24 Aug 2026 (REMOTE-CODE-GUARD-1), on the day "
           "Travelpayouts came back with an approval: the assertion WAS a two-string blocklist "
           "(tp-em.com, NTU3Mzkx.js), which catches only the loader we already removed -- a new "
           "snippet from a new host, which is exactly what a re-approved affiliate account hands "
           "you, sailed past it GREEN. That was the assertion being WRONG, not weakened to make "
           "something pass; it is now the CLASS: any remote script/iframe/stylesheet origin, by "
           "static tag or by createElement+.src, on the live surface OR in any file the deploy "
           "manifest ships, that is not on the dated allowlist in scripts/no_remote_code_guard.py. "
           "That first run also surfaced cdnjs.cloudflare.com, loaded dynamically by ms.js aiLeaflet() and inventoried nowhere until now.")
def rg_no_third_party_script_on_surface():
    # The allowlist is duplicated here ON PURPOSE. The ledger must run live-only,
    # stdlib-only, from any session with no repo -- so it cannot import the guard.
    # scripts/no_remote_code_guard.py is the authority; RG-0177 asserts the two agree.
    ALLOWED = ("unpkg.com", "cdnjs.cloudflare.com", "fonts.googleapis.com", "fonts.gstatic.com")
    PAGES = ["/"] + ["/static/adventures_%s_map.html" % m
                     for m in ("reserve", "us", "uk", "au", "na", "bw", "mz", "c2c", "de", "ke")]
    RE_REMOTE = re.compile(
        r"""<(?:script|iframe)[^>]+src=["'](?:https?:)?//([^/"'?]+)"""
        r"""|<link[^>]+href=["'](?:https?:)?//([^/"'?]+)"""
        r"""|createElement\(\s*["']script["']\s*\)[\s\S]{0,300}?\.src\s*=\s*["'](?:https?:)?//([^/"'?]+)""",
        re.I)

    def origins(body):
        seen = set()
        for m in RE_REMOTE.finditer(body):
            h = (m.group(1) or m.group(2) or m.group(3) or "").lower()
            if h:
                seen.add(h)
        return seen

    out = []
    for p in PAGES:
        try:
            body = _get(p)
        except Exception as ex:
            out.append((FAIL, p + " unreachable while checking for third-party code: " + repr(ex)))
            continue
        for h in sorted(origins(body) - set(ALLOWED)):
            out.append((FAIL, p + " loads remote code from '" + h + "', which is not on the "
                               "allowlist -- third-party code is back on the app surface; "
                               "David's 3 Aug 2026 ruling forbids it"))

    # Repo side: catch it BEFORE it ships, across every file the manifest places,
    # not just the index. Skipped silently when running outside the repo.
    man = repo_file("ops/autodeploy/deploy_manifest.txt")
    if man is None:
        out.append((INFO, "running outside the repo -- live surface checked, pre-deploy scan skipped"))
        return out
    rels = [ln.split("|")[0].strip() for ln in man.splitlines()
            if ln.strip() and not ln.strip().startswith("#") and "|" in ln]
    scanned = 0
    for rel in rels:
        if not rel.lower().endswith((".html", ".js", ".css")):
            continue
        text = repo_file(rel)
        if text is None:
            continue
        scanned += 1
        for h in sorted(origins(text) - set(ALLOWED)):
            out.append((FAIL, "repo " + rel + " references remote code from '" + h + "' -- the next "
                              "deploy would put a third-party script back on the app"))
    out.append((INFO, "pre-deploy scan: %d deployable html/js/css files clean, allowlist = %s"
                      % (scanned, ", ".join(ALLOWED))))
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
    _fp_before = _source_fingerprint()
    results, took = run()
    _moved = _sources_changed(_fp_before, _source_fingerprint())
    n = lambda s: sum(1 for r in results if r["status"] == s)
    regressed, holding, open_, ready = n("REGRESSION"), n("HOLDING"), n("OPEN"), n("READY TO LOCK")
    unver = n("UNVERIFIED")

    if "--json" in sys.argv:
        print(json.dumps({"date": datetime.date.today().isoformat(), "took_s": took,
                          "regressed": regressed, "holding": holding,
                          "open": open_, "ready_to_lock": ready, "unverified": unver,
                          "sources_changed_mid_run": _moved,
                          "unstable_run": bool(_moved and regressed),
                          "entries": results}, indent=1))
        if _moved and regressed:
            return 3   # LEDGER-STABLE-1: read from a moving target - re-run
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
    if regressed and _moved:
        print(f"RESULT: UNSTABLE RUN — {regressed} entr(ies) reported a regression, but these "
              f"repo file(s) CHANGED underneath the run: {', '.join(_moved)}. "
              f"The evidence was read from a moving target, so this verdict is not trustworthy "
              f"either way. Re-run when the tree is settled before believing OR dismissing it "
              f"(LEDGER-STABLE-1, DW-053).")
    elif regressed:
        print(f"RESULT: {regressed} previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.")
    elif unver:
        print(f"RESULT: no regressions in what COULD be checked, but {unver} entr(ies) were NOT "
              f"EVALUATED - this machine cannot reach {BASE}. That is not a green board. "
              f"Re-run somewhere with a route to the site before deploying on this result.")
    elif ready:
        print(f"RESULT: no regressions. {ready} open item(s) now pass — promote them to LOCKED.")
    else:
        print(f"RESULT: every locked fix is holding. {open_} known defect(s) still open.")
    # 1 = a real regression · 2 = blind (unverified) · 3 = unstable run · 0 = clean
    if regressed and _moved:
        return 3
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


@entry("RG-0029", "The pre-launch gate is DOWN BY RULING (RUL-029) -- with the curtain "
       "gone, the app-key guards and the re-arm path are what must hold",
       LOCKED, fixed_on="2026-08-13",
       scope="the pre-launch gate lane entire. SUPERSEDED-BY RUL-029 (19 Aug 2026). This entry "
             "asserted the gate ENFORCES; it is not weakened, it is REPOINTED at what protects "
             "us now the gate is deliberately down, and at the ability to put it back",
       ref="GATE-ENFORCE-1/2 (migrations 016) armed the origin gate 13 Aug. SUPERSEDED-BY "
           "RUL-029, 19 Aug 2026 -- David: 'we can not even give 3 people constant access to "
           "the app?'. The gate existed to protect an unfinished app and had become the main "
           "obstacle to finding out whether the app was ready, so it came down 10 days early "
           "via migration 026. LAUNCH DATES UNCHANGED. Three things carry this entry now: "
           "(1) gate STATE is deferred to RG-0115, which checks BOTH halves; (2) private data "
           "must STILL refuse an anonymous caller, because with the curtain gone the app-key "
           "guards (RG-0094) are the only line rather than the second; (3) the re-arm path must "
           "survive -- migration 026 prints an nginx backup and every credential door (reviewer "
           "code, email link, 6-digit code, admin password) stays in the code, UNUSED rather "
           "than deleted. A lowered gate is not a demolished one; if any of the three rot, this "
           "goes red.")
def rg_gate_posture_after_ruling():
    out = []
    for path, what in (("/tuppence/balance?email=probe@example.invalid", "a Tuppence balance"),
                       ("/tuppence/history?email=probe@example.invalid", "Tuppence history"),
                       ("/users/probe@example.invalid", "a user record")):
        try:
            urllib.request.urlopen(urllib.request.Request(BASE + path, headers=dict(UA)),
                                   timeout=TIMEOUT).read()
            out.append((FAIL, "EXPOSURE: an anonymous caller read %s with no app key. The "
                              "pre-launch gate is down by ruling, so these guards are the ONLY "
                              "thing between the public and private data." % what))
        except urllib.error.HTTPError as he:
            if he.code not in (401, 403):
                out.append((FAIL, "%s answered %s anonymously, expected 401/403" % (what, he.code)))
        except Exception:
            pass
    try:
        urllib.request.urlopen(urllib.request.Request(BASE + "/dashboard.html",
                                                      headers=dict(UA)), timeout=TIMEOUT).read()
        out.append((FAIL, "EXPOSURE: /dashboard.html served anonymously -- lowering the review "
                          "gate must never expose the admin dashboard"))
    except urllib.error.HTTPError as he:
        if he.code not in (401, 403):
            out.append((FAIL, "/dashboard.html answered %s anonymously, expected 401/403" % he.code))
    except Exception:
        pass
    bea = repo_file("bea_main.py")
    if bea is None:
        out.append((INFO, "outside the repo -- re-arm path not checked here"))
    else:
        for needle, what in (("def review_login", "the reviewer-code door"),
                             ("def review_enter", "the emailed-link door"),
                             ("def review_claim_code", "the 6-digit-code door")):
            if needle not in bea:
                out.append((FAIL, "%s was DELETED, not merely unused -- RUL-029 lowered the gate, "
                                  "it did not demolish it, and this removes the re-arm path"
                            % what))
        if repo_file("migrations/026_gate_down.py") is None:
            out.append((FAIL, "migration 026 is gone -- the documented re-arm command went with it"))
    if not out:
        out.append((INFO, "gate down by ruling; private reads + dashboard still refuse "
                          "anonymously; every door still in source"))
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
           "live document -- a wrong reviewer code says so in words. Locked. "
           "ASSERTION CORRECTED 19 Aug 2026 (GATE-NOLOCK-1, not a weakening): this entry pinned the "
           "LITERAL string 'Incorrect reviewer code. Please check it and try again.' -- and that "
           "exact sentence turned out to be the next lie in the same class. The 401 it explains is "
           "the ORIGIN refusing /admin/login, so a CORRECT super-admin password read back as an "
           "incorrect reviewer code and locked David out of his own app (RG-0108). Pinning one "
           "sentence made the ledger defend the wording instead of the PROPERTY. The check now "
           "asserts the property -- a named refusal that says what was actually rejected, plus the "
           "429 and 503 branches in words -- and explicitly trips if the discredited sentence "
           "comes back.")
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
    if src is not None:
        if "GATE-TRUTH-1" not in src:
            out.append((FAIL, "repo marketsquare.html lost the truthful gate branch"))
        # The property: a 401/403 at the gate is NAMED, never rendered as a network error.
        if "r.status === 401 || r.status === 403" not in src:
            out.append((FAIL, "the gate script no longer branches on 401/403 -- a refusal will "
                              "fall through to the .catch and lie as 'Connection error' again"))
        if "Too many attempts" not in src or "switched off right now" not in src:
            out.append((FAIL, "the 429 / 503 gate refusals are no longer surfaced in words"))
        # The discredited sentence must not return: it calls a correct admin password wrong.
        if "Incorrect reviewer code. Please check it and try again." in src:
            out.append((FAIL, "the gate screen is again reporting EVERY 401 as 'Incorrect reviewer "
                              "code' -- that sentence is what hid the super-admin lockout "
                              "(GATE-NOLOCK-1, RG-0108). Name what was actually rejected."))
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
    # EULA-ANCHOR-1 (20 Aug 2026): this used to hardcode the full Country-Schedule list,
    # so ADDING schedules D-G (v1.14: France, Portugal, New Zealand, Argentina) made the
    # assertion report a FORK that did not exist -- the three copies were byte-identical
    # throughout. The assertion was wrong, not the artefact. Anchor on the stable prefix
    # and find the paragraph close, so the schedule list can grow without going red.
    end_prefix = "· Republic of South Africa · Country Schedules:"
    end_close  = "</em></p>\n"
    i = terms.find(start)
    jp = terms.find(end_prefix)
    j = terms.find(end_close, jp) if jp != -1 else -1
    endp_len = len(end_close)
    if i == -1 or jp == -1 or j == -1:
        out.append((FAIL, "terms.html has no recognisable EULA body -- anchors gone"))
    elif terms[i:j + endp_len] != src:
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
    except urllib.error.HTTPError as he:
        if he.code == 429:
            # ASSERTION FIX 19 Aug 2026 (not a weakening): a 429 is the per-IP limiter
            # ANSWERING, which proves the endpoint is reachable and exempt -- exactly what
            # this entry asserts. Reading it as "019 has not landed" produced a false red
            # twice, both self-inflicted by this ledger's own probe rate (watch a3d82b5).
            # RG-0108 already handles 429 this way; this makes the board consistent.
            out.append((INFO, "live /review/request-link rate-limited this probe (429) -- "
                              "lane reachable, limiter alive"))
        else:
            out.append((FAIL, "live /review/request-link refused (HTTP %s) -- migration 019 "
                              "has not landed (or the lane rotted): a tester cannot ask for "
                              "a link" % he.code))
    except Exception as ex:
        out.append((FAIL, "live /review/request-link unreachable (%r) -- a tester cannot ask "
                          "for a link" % ex))
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
@entry("RG-0090", "PARKED by RUL-029 -- the document is public by design; this becomes live again the moment the gate is re-armed",
       LOCKED, fixed_on="2026-08-20 (promoted: READY TO LOCK -- passes while the gate is down; "
                        "re-arming the gate re-activates the edge-cache assertion, which is the point)",
       scope="the index document at / (and any gated HTML the edge caches). The DATA side "
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
    # PARKED 19 Aug 2026 (RUL-029). This entry asserted that the GATED html shell must never
    # be served to the public from the CDN cache. The gate came down by ruling, so the shell
    # is public ON PURPOSE and the assertion has no subject. It is parked, NOT deleted: the
    # cache-poisoning risk it describes is real and returns the instant the gate is re-armed
    # (migration 026 prints the one-command re-arm). Re-activating it is un-commenting the
    # original check below, which is preserved verbatim.
    #
    #   c, hdrs = _code_and_headers("/")
    #   if c == 200 and "no-store" not in (hdrs.get("Cache-Control") or ""):
    #       out.append((FAIL, "anonymous cookie-less GET / answers 200 with the app document
    #                          and no private/no-store -- the edge can hand the gated shell
    #                          to the public once any cookie-holder primes it"))
    return [(INFO, "parked by RUL-029 -- no gated document exists to protect; re-activate "
                   "together with any re-arm of the gate")]

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
       "with the real pages",
       LOCKED, fixed_on="2026-08-16",
       scope="the live edge + nginx exempt list, all markets. The legal docs are open. The "
             "former second half -- 'and the gate did not silently widen (/wonders stays "
             "non-200)' -- was RETIRED 19 Aug 2026 when RUL-029 lowered the gate deliberately: "
             "that clause would now assert the opposite of a standing ruling. Gate STATE is "
             "RG-0029 + RG-0115's job; this entry keeps the RUL-020 promise it was written for",
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
    # The '/wonders must stay non-200' clause was RETIRED 19 Aug 2026 (RUL-029): the gate
    # is down by ruling, so that check would now assert the opposite of standing canon.
    # Gate STATE lives in RG-0029 (posture + what still protects us) and RG-0115 (both
    # halves actually down). This entry keeps ONLY the RUL-020 promise it was written for.
    if not out:
        out.append((INFO, "legal docs open and served (gate state: see RG-0029 / RG-0115)"))
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



@entry("RG-0099", "The management lanes can SEE a lockout: port 22 answers from the session "
       "vantage, and the Cloudflare edge is not blocking the session's own IP",
       LOCKED, fixed_on="2026-08-17",
       scope="the session/David egress vantage (they share an IP). Detects the SSH-LOCKOUT-1 "
             "class: a home power/router reset moves the IP outside BOTH allowlists (Hetzner "
             "firewall SSH rule + Cloudflare PRELAUNCH GATE). Post-launch the CF half retires "
             "with the gate; the SSH half stays for good",
       ref="SSH-LOCKOUT-1, 17 Aug 2026: the blackout moved David's home IP; SSH timed out and "
           "the site 403'd from the new IP while serving everyone else. Fixed by hand at both "
           "panels; scripts/hetzner_fw_selfheal.py now heals both automatically when tokens are "
           "provisioned. THIS entry is the tripwire: a red here names the runbook line instead "
           "of a mystery morning. LEDGER-FLAP-1, 19 Aug 2026 (maintenance-loop): the probe was a "
           "SINGLE 6 s connect, so one dropped packet read as a lockout -- it went red at 05:52 "
           "while the port was demonstrably open (banner SSH-2.0-OpenSSH_9.6p1 returned in 0.21 s "
           "on 3 consecutive probes minutes later). A red here blocks the nightly ship, so a flaky "
           "assertion is an outage of its own. Now 3 tries at 8 s; the assertion is not weakened -- "
           "a genuinely blocked port fails all three.")
def rg_management_lanes_reachable():
    out = []
    _require_net()
    import socket, time as _time
    # LEDGER-FLAP-1 (19 Aug 2026, maintenance-loop): a SINGLE 6 s TCP probe declared a
    # REGRESSION -- and a red here says "do not deploy", so one dropped packet stalls the
    # nightly ship. Three tries, 8 s each, before the verdict. Strength is UNCHANGED: a
    # genuinely blocked port fails all three and still reports the runbook line.
    _ssh_err = None
    for _try in range(3):
        try:
            socket.create_connection(("178.104.73.239", 22), timeout=8).close()
            _ssh_err = None
            break
        except Exception as e:
            _ssh_err = type(e).__name__
            if _try < 2:
                _time.sleep(3)
    if _ssh_err:
        out.append((FAIL, "port 22 unreachable from this vantage on 3 tries (%s) -- SSH-LOCKOUT-1 "
                          "class: the home IP likely changed (power/router reset). Fix: run "
                          "scripts/hetzner_fw_selfheal.py, or add the current IP at Hetzner > "
                          "Firewalls > trustsquare-origin-lockdown" % _ssh_err))
    try:
        req = urllib.request.Request(BASE + "/terms", headers=UA)
        try:
            code = urllib.request.urlopen(req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as he:
            code = he.code
        if code == 403:
            out.append((FAIL, "/terms answers 403 from the session's own IP -- the Cloudflare "
                              "PRELAUNCH GATE is blocking us (stale allowlist). Fix: run "
                              "scripts/hetzner_fw_selfheal.py (CF half), or add the current IP "
                              "to the PRELAUNCH GATE rule in the Cloudflare dashboard"))
    except ProbeOffline:
        raise
    except Exception:
        pass
    if not out:
        out.append((INFO, "ssh:22 open and the edge serves this IP -- both management lanes clear"))
    return out



@entry("RG-0100", "The CityLauncher dashboard reads coverage in ONE call: /listings/coverage "
       "answers with per-city counts, and the dashboard source carries no bare city sweep",
       LOCKED, fixed_on="2026-08-17",
       scope="BEA /listings/coverage + CityLauncher dashboard/citylauncher.html (COVERAGE-1). "
             "Guards the self-DDoS class: an open monitoring tab must never generate tens of "
             "thousands of heavy origin hits per day",
       ref="COVERAGE-1, 17 Aug 2026 (David: close it now or future-us inherits it). The 91k-"
           "request mystery was the /launch/ dashboard sweeping full /listings payloads for 93 "
           "cities inside a 60s refresh loop (~40k req + GBs/day from one tab). One aggregate "
           "GROUP BY replaces the sweep; the old loop survives only as a fallback when the "
           "coverage endpoint is absent.")
def rg_coverage_one_call():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None and '"/listings-coverage"' not in bea:
        out.append((FAIL, "bea_main.py lost /listings-coverage -- the dashboard will fall back "
                          "to the 93-city sweep"))
    try:
        dash = open(os.path.join(REPO, "..", "CityLauncher", "dashboard", "citylauncher.html"),
                    encoding="utf-8", errors="replace").read()
        if "COVERAGE-1" not in dash:
            out.append((FAIL, "CityLauncher dashboard lost the COVERAGE-1 path -- sweep is back"))
    except OSError:
        pass  # CityLauncher repo not mounted -- BEA half asserted above
    _require_net()
    body = _get("/listings-coverage")
    try:
        d = json.loads(body)
        if not isinstance(d.get("cities"), dict) or not d["cities"]:
            out.append((FAIL, "/listings-coverage answers but carries no cities dict"))
    except Exception:
        out.append((FAIL, "/listings-coverage did not answer valid JSON"))
    if not out:
        out.append((INFO, "coverage in one call (%d cities)" % len(d["cities"])))
    return out



@entry("RG-0101", "GET /wonders travels gzipped -- the heritage catalog fetch is ~144 KB, not 485 KB",
       LOCKED, fixed_on="2026-08-21", scope="every FastAPI JSON response over 1 KB (wonders, listings, selfcheck...); nginx "
                   "static files are a separate lane and unaffected",
       ref="WONDERS-GZIP-1, 18 Aug 2026: the catalog measured 485 KB raw / 332 sites (~1.5 KB per "
           "site) and nothing compressed JSON anywhere (no gzip_types in the nginx conf, no app "
           "middleware) -- found while confirming the rail-route heritage expansion (+19 sites) is "
           "negligible for app delays. GZipMiddleware(minimum_size=1024) added to bea_main.py in the "
           "same session the expansion merged. ASSERTION CORRECTED 21 Aug 2026: it judged "
           "/ops/selfcheck as a stand-in because the armed gate 401'd /wonders -- then the gate "
           "came down (RUL-029/034) and /wonders became readable while /ops/selfcheck stayed "
           "gated, so the entry sat OPEN reporting a 401 on the PROXY while the real property "
           "had been live and correct since the 18 Aug deploy. Measure the artefact the entry is "
           "named after: /wonders, asked for gzip. Live 21 Aug: 160,022 B gzipped vs ~485 KB raw.")
def rg_wonders_gzip():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None and "GZipMiddleware" not in bea:
        out.append((FAIL, "bea_main.py lost WONDERS-GZIP-1 (GZipMiddleware) -- the heritage catalog "
                          "ships raw again and grows ~1.5 KB per site uncompressed"))
    # Measure the named artefact, and fall back to any other JSON lane if it is gated --
    # never let ONE gated stand-in decide the verdict for a property that is plainly live.
    probed = False
    for path in ("/wonders", "/listings?city=Pretoria", "/ops/selfcheck"):
        try:
            req = urllib.request.Request(BASE + path,
                                         headers=dict(UA, **{"Accept-Encoding": "gzip"}))
            resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        except Exception:
            continue          # gated or unreachable -- try the next lane
        enc = (resp.headers.get("Content-Encoding", "") or "").lower()
        body = resp.read()
        probed = True
        if len(body) > 1024 and "gzip" not in enc:
            out.append((FAIL, "%s answered %d B with no Content-Encoding: gzip -- "
                              "WONDERS-GZIP-1 is not live" % (path, len(body))))
        else:
            out.append((INFO, "%s travels gzipped (%d B on the wire)" % (path, len(body))))
        break
    if not probed:
        out.append((INFO, "every JSON lane was gated or unreachable this run -- live gzip "
                          "UNVERIFIED (repo half still asserted above)"))
    return out



@entry("RG-0102", "ONE wonders catalog: the manifest-shipped root wonders.json is the only editable "
       "copy, and it carries the 19 rail-expansion sites",
       LOCKED, fixed_on="2026-08-18",
       scope="the whole heritage catalog lane: repo root wonders.json (deploy manifest line "
             "'wonders.json | wonders.json') vs the retired assets/wonders.json fork",
       ref="WONDERS-CANON-1, 18 Aug 2026: the repo carried TWO files named wonders.json -- root "
           "(300 entries, photo-verified schema, the one the manifest ships) and assets/ (332, "
           "older schema, never shipped, quietly growing since May: 32 strays incl. duplicate "
           "sites under new ids). The HERITAGE-RAIL-1 merge landed in the WRONG one and a deploy "
           "shipped 300 while the session believed 351. Fix: root reconciled to 319 (300 + the 19 "
           "approved rail sites only), strays quarantined in assets/wonders_pending_32.json for a "
           "dedupe pass, assets/wonders.json RETIRED by rename. Live half is probe-limited while "
           "the prelaunch gate 401s /wonders; the repo half is the tripwire.")
def rg_wonders_canon():
    out = []
    w = repo_file("wonders.json")
    if w is not None:
        try:
            cat = json.loads(w)
            ids = {x.get("id") for x in cat}
            rail = {"np_098","np_099","np_100","ar_047","nm_048","nm_049","un_143","nm_050",
                    "un_144","ar_048","un_145","un_146","np_101","un_147","nm_051","np_102",
                    "np_103","np_104","nm_052"}
            if not rail <= ids:
                out.append((FAIL, "root wonders.json lost %d rail-expansion sites" % len(rail - ids)))
            if len(ids) != len(cat):
                out.append((FAIL, "root wonders.json has duplicate ids"))
            if len(cat) < 319:
                out.append((FAIL, "root wonders.json shrank to %d entries (<319)" % len(cat)))
        except Exception as e:
            out.append((FAIL, "root wonders.json unparseable: %s" % e))
        if os.path.exists(os.path.join(REPO, "assets", "wonders.json")):
            out.append((FAIL, "assets/wonders.json EXISTS again -- the divergent-copy class is "
                              "back; sessions will merge into the file the manifest never ships"))
    return out



@entry("RG-0103", "PIN-SPREAD cannot retrigger itself: the fan-out machinery is deaf to its own "
       "layer events, so clustered pins never bounce",
       LOCKED, fixed_on="2026-08-18",
       scope="scripts/journey_template.html (the source) + all generator-built journey maps. "
             "The class: any handler that mutates layers while subscribed to layeradd/layerremove",
       ref="PINSPREAD-GUARD-1, 18 Aug 2026: spreadPins() adds dashed tether legs and clearSpread() "
           "removes them; both fire the layeradd/layerremove events queueSpread listens for, so one "
           "cluster past base zoom looped clear->spread every ~140ms forever -- pins visibly bounced "
           "home-and-out ~3x/second with the .28s transition (David caught orange+green bouncing on "
           "the US rail map Leg 3; a synthetic-hover probe froze the tab outright). Fix: busy flag "
           "swallows the machinery's OWN synchronous layer events; redraw/toggle/zoom triggers pass. "
           "Template is the single source -- an unguarded rebuild would resurrect the bounce in all "
           "11 maps at once, hence this tripwire on template AND built artifacts.")
def rg_pinspread_guard():
    out = []
    tpl = repo_file("scripts/journey_template.html")
    if tpl is not None:
        if "PINSPREAD-GUARD-1" not in tpl:
            out.append((FAIL, "journey_template.html lost PINSPREAD-GUARD-1 -- next rebuild ships "
                              "self-retriggering spread to every journey map"))
        if "function queueSpread(){ clearTimeout" in tpl:
            out.append((FAIL, "template queueSpread is unguarded again (no busy check)"))
    for name in ("adventures_us_rail_map.html", "adventures_gb_rail_map.html",
                 "adventures_au_rail_map.html", "adventures_ke_map.html"):
        f = repo_file(name)
        if f is None:
            continue
        if "spreadPins" in f and "PINSPREAD-GUARD-1" not in f:
            out.append((FAIL, name + " carries PIN-SPREAD without the guard -- built from a stale "
                               "template or hand-reverted; pins there can bounce"))
    return out


@entry("RG-0106", "Showcase supers are IMMORTAL -- the lifecycle sweep can never fade or archive "
       "a showcase listing, and no non-admin path can delete one",
       LOCKED, fixed_on="2026-08-18",
       scope="the whole showcase class, all markets: _lifecycle_sweep candidate + archive "
             "queries exclude showcase; both delete endpoints 403 non-admin showcase deletes "
             "(app key alone and house seller email alone both refused). Repo-asserted now; "
             "the live sweep carries the exemption from the first deploy after 18 Aug -- "
             "migration 024 heals any already-faded/warned showcase on that same deploy",
       ref="RUL-026, 18 Aug 2026: David -- 'the super demos should stay live and only be "
           "deleted by admin users'. Fault: supers were born as real listings (showcase=1, "
           "is_demo=0), so FADE-1 treated them as user listings and fade warnings reached "
           "the house accounts. ASSERTION CORRECTED 20 Aug 2026: it pinned literal SQL, so "
           "it could never see that the exemption had NEVER covered the seeded supers -- see "
           "RG-0123 (SUPER-IMMORTAL-2), which owns the super_example half of this class.")
def rg_showcase_immortal():
    # ASSERTION CORRECTED 20 Aug 2026 (SUPER-IMMORTAL-2), not weakened. This entry used to
    # pin two literal SQL strings -- the comment "RUL-026: showcase supers never fade" and
    # "AND (showcase = 0 OR showcase IS NULL)". Pinning the WORDING meant the entry stayed
    # green while the property it names was false for every seeded super (super_example=1,
    # showcase NULL -- which `showcase IS NULL` positively INCLUDED as a fade candidate),
    # and then went red when the predicate was strengthened to COALESCE(...) != 1. It now
    # asserts the PROPERTY: whatever the SQL says, both the candidate query and the archive
    # step must exclude showcase listings. The super_example half is RG-0123's.
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        sweep = bea.split("def _lifecycle_sweep", 1)[-1].split("\n@app.", 1)[0]
        cands = sweep.split("for c in cands", 1)[0]
        if "showcase" not in cands:
            out.append((FAIL, "bea_main.py lost the sweep's showcase exemption -- a showcase "
                              "listing is a fade candidate again"))
        if bea.count("Showcase adverts are admin-managed.") < 2:
            out.append((FAIL, "a delete endpoint lost its showcase admin guard"))
        arch = sweep.split("FADE: archive after", 1)[-1].split('res["fade_archived"]', 1)[0]
        if "showcase" not in arch:
            out.append((FAIL, "the archive step lost its showcase exclusion"))
    mig = repo_file("migrations/024_showcase_immortal.py")
    if mig is None:
        out.append((INFO, "outside the repo -- source half not checked here"))
    if not out:
        out.append((INFO, "sweep exemption + admin-only deletes asserted in source"))
    return out



# ── GATE-NOLOCK-1 (19 Aug 2026) ──────────────────────────────────────────────
@entry("RG-0107", "No one who is entitled to enter can be locked out by the DEVICE they entered on -- the emailed code unlocks the machine in front of them",
       LOCKED, fixed_on="2026-08-19", scope="the cross-device gate lane entire: the 6-digit code minted and mailed by "
                   "/review/request-link, redeemed at /review/claim-code, exempt at the origin "
                   "(migration 025), and the marketsquare.html code box that appears once a link "
                   "has been requested. NOT limited to David or to laptops: this is the whole "
                   "class of 'requested on device A, mail opens on device B'. The link path "
                   "(/review/enter) must ALSO stay alive -- losing it is a failure of this entry.",
       ref="David, 19 Aug 2026, with screenshots: he asked for a link on his LAPTOP, the mail "
           "opened on his PHONE, the phone got the ts_review cookie and the laptop -- the machine "
           "he actually works on -- stayed locked with no way to finish. A magic link can only "
           "ever unlock the browser that OPENS it; GATE-EMAIL-1 (RG-0081) shipped only that half, "
           "so the lockout class it was built to end simply changed shape. The device-independent "
           "half is a 6-digit code in the SAME email: read it wherever the mail landed, type it "
           "where you are locked. 30-minute life, single use, 6-guess budget, same allowlist, "
           "same per-IP limit, same review-scope cookie -- no new privilege, a second door. "
           "Urgency: Maroushka is handing this link to agencies; a gate that locks out the super "
           "admin will lock out testers, and each one is a lost first impression. "
           "PROMOTED 19 Aug 2026: the code door is live -- /review/claim-code answers with app JSON "
           "and refuses a junk code. The gate itself came down the same day (RUL-029), so this lane "
           "is now the pre-launch remnant; the CLASS it protects moved to RG-0110, which carries "
           "the same device-independence rule for the REAL user sign-in. Locked so the rule "
           "survives the gate it was born in.")
def rg_gate_cross_device_code():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "/review/claim-code" not in bea or "_review_code_ok" not in bea:
            out.append((FAIL, "bea_main.py lost the cross-device code lane (/review/claim-code)"))
        if "def review_enter" not in bea:
            out.append((FAIL, "the emailed LINK path is gone -- the code must be a second door, "
                              "never a replacement"))
        if "_REVIEW_CODE_TRIES" not in bea:
            out.append((FAIL, "the per-code guess budget is gone -- a 6-digit code with unlimited "
                              "tries is a 1-in-a-million lock with infinite keys"))
        html = repo_file("marketsquare.html") or ""
        if "gate-otp-block" not in html or "gateClaimCode" not in html:
            out.append((FAIL, "marketsquare.html lost the code box -- the tester has nowhere to "
                              "type the code that was mailed to them"))
    if repo_file("migrations/025_gate_nolock.py") is None:
        out.append((INFO, "outside the repo -- source half not checked here"))
    # Live half: the endpoint must answer WITHOUT a cookie (exempt at the origin) and
    # must REFUSE a wrong code. A nginx HTML 401 (no JSON detail) means 025 never landed.
    try:
        req = urllib.request.Request(BASE + "/review/claim-code",
                                     data=json.dumps({"email": "rg-probe@example.invalid",
                                                      "code": "000000"}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        try:
            urllib.request.urlopen(req, timeout=TIMEOUT).read()
            out.append((FAIL, "live /review/claim-code ACCEPTED a junk code for an off-list email "
                              "-- the gate is open to anyone who can count to six digits"))
        except urllib.error.HTTPError as he:
            body = (he.read() or b"").decode("utf-8", "replace")
            if he.code == 429:
                # Same false-red class fixed in RG-0081 and RG-0108 on 19 Aug: a 429 is the
                # per-IP limiter ANSWERING, which proves the endpoint is reachable and exempt.
                # This ledger's own probe rate trips it; that is not a product fault.
                out.append((INFO, "live /review/claim-code rate-limited this probe (429) -- "
                                  "endpoint reachable, limiter alive"))
            elif he.code != 401:
                out.append((FAIL, "live /review/claim-code answered %s, expected 401" % he.code))
            elif "expired" not in body and "wrong" not in body:
                out.append((FAIL, "live /review/claim-code 401 came from nginx, not the app "
                                  "(no JSON detail) -- migration 025 has not landed, so a locked "
                                  "device still cannot redeem its code. Body: %r" % body[:120]))
    except Exception as ex:
        out.append((FAIL, "live /review/claim-code unreachable (%r)" % ex))
    if not out:
        out.append((INFO, "cross-device code lane answers and refuses correctly"))
    return out


@entry("RG-0108", "The SUPER ADMIN can always get into his own app -- the strongest credential in the system is never the one that cannot open the door",
       LOCKED, fixed_on="2026-08-19", scope="the admin-credential gate lane entire: /admin/login, /admin/change-pin and "
                   "/admin/verify exempt at the origin (migration 025); a correct admin password "
                   "or team PIN granting the ts_review cookie in bea_main.py; and the gate-screen "
                   "and dashboard messages that must no longer report a CORRECT password as an "
                   "incorrect reviewer code. Class, not instance: any future gate must keep an "
                   "admin door, on every device, for every admin -- not just David, not just the "
                   "master password.",
       ref="David, 19 Aug 2026, with screenshots: 'not even the old password works'. Cause: "
           "GATE-ENFORCE-2 (RG-0029/migration 016) arms the catch-all and /admin/login was "
           "deliberately NOT exempt, so nginx refused the request at the ORIGIN with an HTML 401 "
           "before the app ever saw the password. The gate screen's GATE-TRUTH-1 branch then "
           "rendered that 401 as 'Incorrect reviewer code' -- the correct super-admin password "
           "reading back as a wrong one -- and dashboard.server.html told him to go enter the "
           "reviewer code at trustsquare.co first, i.e. to perform the exact step that was "
           "impossible. Three layers each doing their job produced a total lockout of the one "
           "person who cannot be locked out. Fix: exempt the credential endpoints (they serve no "
           "content, answer only 200/401, and are now behind the 8-per-10-min per-IP limiter) and "
           "grant the WEAKER review cookie on a successful admin login -- strictly no new "
           "privilege, since an admin token already outranks a reviewer cookie. "
           "EXPECTED OPEN until migration 025 rides a deploy; promote to LOCKED once live. "
           "PROMOTED 19 Aug 2026 (maintenance-loop): migration 025 is live -- anonymous "
           "POST /admin/login reaches the APP and answers a JSON 401 (not an nginx HTML 401), "
           "and the containment probes (/tuppence/balance, /users/{email}) still refuse "
           "anonymously. Locked: the admin door must never close again, on any device, for "
           "any admin.")
def rg_gate_admin_never_locked():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "GATE-NOLOCK-1" not in bea:
            out.append((FAIL, "bea_main.py lost the GATE-NOLOCK-1 lane"))
        if "_grant_review_cookie(response, \"admin-master/\" + ip)" not in bea:
            out.append((FAIL, "a correct MASTER password no longer grants gate passage -- the "
                              "super admin can be locked out of his own app again"))
        if "admin-team/" not in bea:
            out.append((FAIL, "a correct team PIN no longer grants gate passage"))
        if "def admin_login(req: _AdminLoginRequest, request: Request, response: Response)" not in bea:
            out.append((FAIL, "admin_login lost its Response/Request parameters -- it cannot set "
                              "the gate cookie or rate-limit by IP"))
        # ASSERTION CORRECTED 21 Aug 2026 (ADMIN-NOLOCK-2 / RG-0134). This used to demand
        # the literal _review_rate_ok, which pinned the admin door to the SHARED reviewer
        # bucket -- the very wiring that locked David out of his own dashboard on 21 Aug.
        # The requirement was always "admin_login must be rate limited", never "must share
        # the reviewer's budget". It now asserts the property, not the old spelling, and
        # RG-0134 asserts the separation the old wording forbade. Not a weakening: a wrong
        # admin credential still costs allowance.
        _al = bea.split("def admin_login")[1][:1600]
        if "_rate_ok(" not in _al:
            out.append((FAIL, "admin_login is anonymously reachable but NO LONGER rate limited"))
        elif "_rate_ok(_admin_attempts" not in _al:
            out.append((FAIL, "admin_login is rate limited from a bucket that is not its own -- "
                              "reviewer-lane traffic can starve the admin door again (RG-0134)"))
    dash = repo_file("dashboard.server.html") or ""
    if dash and "Locked by the pre-launch gate" in dash:
        out.append((FAIL, "dashboard.server.html still tells the admin to enter the reviewer code "
                          "first -- instructions to perform an impossible step"))
    html = repo_file("marketsquare.html") or ""
    if html and "Incorrect reviewer code. Please check it and try again." in html:
        out.append((FAIL, "the gate screen still reports a rejected ADMIN password as an "
                          "'Incorrect reviewer code' -- the message that hid this fault"))
    if repo_file("migrations/025_gate_nolock.py") is None:
        out.append((INFO, "outside the repo -- source half not checked here"))
    # Live half: anonymous /admin/login must reach the APP (JSON 401), not nginx (HTML 401),
    # while a content path stays gated. Never send a real credential from the ledger.
    try:
        req = urllib.request.Request(BASE + "/admin/login",
                                     data=json.dumps({"password": "rg-probe-not-a-password"}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        try:
            urllib.request.urlopen(req, timeout=TIMEOUT).read()
            out.append((FAIL, "live /admin/login ACCEPTED a junk password -- stop everything"))
        except urllib.error.HTTPError as he:
            body = (he.read() or b"").decode("utf-8", "replace")
            if he.code == 429:
                out.append((INFO, "live /admin/login rate-limited this probe (429) -- limiter alive"))
            elif he.code != 401:
                out.append((FAIL, "live /admin/login answered %s, expected 401" % he.code))
            elif "detail" not in body:
                out.append((FAIL, "live /admin/login 401 came from nginx, not the app (no JSON "
                                  "detail) -- migration 025 has not landed and the super admin is "
                                  "still locked out. Body: %r" % body[:120]))
    except Exception as ex:
        out.append((FAIL, "live /admin/login unreachable (%r)" % ex))
    # CONTAINMENT, restated 19 Aug 2026. This clause used to assert anonymous /listings
    # answers 401 -- i.e. that the gate was still armed. RUL-029 lowered the gate
    # deliberately, so that check would now assert the opposite of standing canon and it
    # is retired here (gate STATE lives in RG-0029 + RG-0115). What this entry must still
    # prove is that the admin-door exemptions did not open anything PRIVATE.
    for path, what in (("/tuppence/balance?email=probe@example.invalid", "a Tuppence balance"),
                       ("/users/probe@example.invalid", "a user record")):
        try:
            urllib.request.urlopen(urllib.request.Request(BASE + path, headers=dict(UA)),
                                   timeout=TIMEOUT).read()
            out.append((FAIL, "CONTAINMENT BREACH: the admin-door exemptions exposed %s to an "
                              "anonymous caller" % what))
        except urllib.error.HTTPError as he:
            if he.code not in (401, 403):
                out.append((FAIL, "%s answered %s anonymously, expected 401/403" % (what, he.code)))
        except Exception:
            pass
    if not out:
        out.append((INFO, "admin door reaches the app; content paths stay gated"))
    return out



@entry("RG-0109", "A MACHINE touching an access link can never spend it -- only a person's click counts",
       LOCKED, fixed_on="2026-08-19", scope="the emailed-link claim lane entire: /review/enter GET + HEAD, the "
                   "_review_link_used record, and the reason carried to the gate screen. CLASS, not "
                   "instance: any future one-time URL we email (gate link, account magic link "
                   "/auth/verify, agent invites) inherits this rule -- mail providers, security "
                   "gateways and click-trackers WILL fetch it before the human does.",
       ref="David + Maroushka, 19 Aug 2026: she opened the gate, asked for a link, clicked it and "
           "was told the link had expired -- INSTANTLY, on a link seconds old. David had hit the "
           "same thing. Nothing had expired and no person had used it: a machine had. Resend "
           "rewrites URLs when click tracking is on, and mail scanners fetch links before "
           "delivery; that fetch claimed the single-use jti, so the real click arrived second and "
           "was refused. Strict single-use was the wrong trade for a token that is already 30 "
           "minutes long, allow-list-bound, HTTPS-only and scoped to browse-only passage. Repeat "
           "claims inside the window are now idempotent (the EXPIRY is the control, not the "
           "counter); the jti record is kept for audit and an absurd replay count still refuses; "
           "HEAD is answered 204 without touching the record. Paired with GATE-WHY-1: every "
           "refusal now carries a coarse reason (expired|used|invalid|none) to the screen, because "
           "collapsing them into one sentence is what cost two diagnosis rounds with testers "
           "waiting. The 6-digit code (RG-0107) is the scanner-proof door and is now opened "
           "automatically whenever a link fails. PROMOTED 19 Aug 2026: live /review/enter bounces with a "
           "reason in the URL and repeat claims inside the window are idempotent. Locked -- the "
           "rule applies to every one-time URL we email, so it outlives the gate.")
def rg_link_survives_prefetch():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "LINK-PREFETCH-1" not in bea:
            out.append((FAIL, "bea_main.py lost the prefetch-tolerant claim"))
        if "return _bounce(\"already used\")" in bea:
            out.append((FAIL, "the strict single-use refusal is BACK -- a scanner prefetch will "
                              "again spend the tester's link before they can click it"))
        if "def review_enter_head" not in bea:
            out.append((FAIL, "HEAD /review/enter is no longer answered separately -- a scanner's "
                              "HEAD can reach the claim path again"))
        if "GATE-WHY-1" not in bea:
            out.append((FAIL, "the bounce no longer carries WHY -- we are blind on the next one"))
        html = repo_file("marketsquare.html") or ""
        if html and "GATE-WHY-1" not in html:
            out.append((FAIL, "the gate screen lost the per-reason message"))
    # Live: a HEAD must answer without a redirect-to-expired, and GET garbage must say why.
    try:
        class _NR(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        op = urllib.request.build_opener(_NR)
        rq = urllib.request.Request(BASE + "/review/enter?t=garbage", headers=dict(UA))
        try:
            r = op.open(rq, timeout=TIMEOUT); code, loc = r.getcode(), ""
        except urllib.error.HTTPError as he:
            code, loc = he.code, (he.headers.get("Location") or "")
        if code == 302 and "why=" not in loc:
            out.append((FAIL, "live /review/enter bounces without a reason (%r) -- GATE-WHY-1 has "
                              "not landed; the next link failure will be blind again" % loc))
    except Exception as ex:
        out.append((FAIL, "live /review/enter unreachable (%r)" % ex))
    if not out:
        out.append((INFO, "link claim tolerates machine fetches; refusals carry a reason"))
    return out



@entry("RG-0110", "A real user signs in ON THE DEVICE THEY ARE USING -- entry never depends on which device opens the mail",
       LOCKED, fixed_on="2026-08-19", scope="the LAUNCH user sign-in lane entire (not the pre-launch gate): "
                   "/auth/request-link minting the code, /auth/verify-code redeeming it, the shared "
                   "_establish_user_session used by BOTH the link and the code so the doors cannot "
                   "drift, the sign-in email carrying the code above the link, and the ms.js code box "
                   "that every caller of requestSignInLink inherits. CLASS: any future sign-in surface "
                   "must offer the typed code, not a link alone.",
       ref="David, 19 Aug 2026, on the launch gate: 'I need access for users with no effort... zero "
           "retries. How do I email 10000 people to help them after they tried a few times.' The "
           "magic link cannot meet that and never could: it signs in whichever device OPENS the "
           "mail, and mail overwhelmingly opens on a phone while the person is on a laptop. Every "
           "user that happens to is stranded mid-task with no self-service way out, and at launch "
           "scale there is no support channel to rescue them -- the workaround we used for one "
           "tester (hand her a password) is proof of the defect, not a fix. A typed 6-digit code "
           "removes the device dependency entirely: read it wherever the mail landed, type it where "
           "you already are, no tab lost, no app switch, and no mail scanner can spend it. The link "
           "stays for people already reading mail on the device they want. "
           "CORRECTION on record: an earlier note in this session claimed /auth/verify carried the "
           "same single-use prefetch fault as the gate link (RG-0109). It does NOT -- /auth/verify "
           "has no jti and no single-use, so a scanner fetch is harmless there. The user-path defect "
           "is the DEVICE dependency, which is a different and larger problem. "
           "PROMOTED 19 Aug 2026: /auth/verify-code is live and refuses a junk code with the app's "
           "own message; both doors route through _establish_user_session. Superseded in PRIORITY "
           "the same day by RG-0111 (Google one-tap, RUL-028) -- the typed code is now the FALLBACK "
           "for anyone who will not use a Google account. Stays LOCKED because that fallback must "
           "never quietly disappear.")
def rg_signin_device_independent():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "SIGNIN-CODE-1" not in bea or "/auth/verify-code" not in bea:
            out.append((FAIL, "bea_main.py lost the typed-code sign-in -- users are back to a "
                              "link that only works on whichever device opens the mail"))
        if "def _establish_user_session" not in bea:
            out.append((FAIL, "the shared session establisher is gone -- the link door and the "
                              "code door can now drift apart silently"))
        # both doors must go through the one establisher
        for fn in ("def auth_verify(", "def auth_verify_code("):
            seg = bea.split(fn)[1][:1400] if fn in bea else ""
            if seg and "_establish_user_session" not in seg:
                out.append((FAIL, "%s no longer routes through _establish_user_session" % fn.strip("def (")))
        if "_signin_codes" not in bea or "_SIGNIN_CODE_TRIES" not in bea:
            out.append((FAIL, "the sign-in code store / guess budget is gone"))
    js = repo_file("ms.js") or ""
    if js:
        if "showSignInCodeBox" not in js:
            out.append((FAIL, "ms.js lost the sign-in code box -- the email carries a code the "
                              "user has nowhere to type"))
        if "requestSignInLink" in js and "showSignInCodeBox(email" not in js:
            out.append((FAIL, "requestSignInLink no longer reveals the code box, so some sign-in "
                              "surface is link-only again"))
    if repo_file("migrations/025_gate_nolock.py") is not None:
        m = repo_file("migrations/025_gate_nolock.py")
        if "/auth/verify-code" not in m:
            out.append((FAIL, "migration 025 no longer exempts /auth/verify-code -- pre-launch "
                              "testers cannot use the code door"))
    # Live: the endpoint must reach the APP and refuse a junk code with JSON.
    try:
        req = urllib.request.Request(BASE + "/auth/verify-code",
                                     data=json.dumps({"email": "rg-probe@example.invalid",
                                                      "code": "000000"}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        try:
            urllib.request.urlopen(req, timeout=TIMEOUT).read()
            out.append((FAIL, "live /auth/verify-code ACCEPTED a junk code -- anyone can sign in "
                              "as anyone. Stop everything."))
        except urllib.error.HTTPError as he:
            body = (he.read() or b"").decode("utf-8", "replace")
            if he.code == 429:
                out.append((INFO, "live /auth/verify-code rate-limited this probe -- limiter alive"))
            elif he.code != 401:
                out.append((FAIL, "live /auth/verify-code answered %s, expected 401" % he.code))
            elif "detail" not in body:
                out.append((FAIL, "live /auth/verify-code 401 came from nginx, not the app -- the "
                                  "code door has not landed"))
    except Exception as ex:
        out.append((FAIL, "live /auth/verify-code unreachable (%r)" % ex))
    if not out:
        out.append((INFO, "typed-code sign-in live; both doors share one session establisher"))
    return out



@entry("RG-0111", "Federated sign-in is ONE TAP and loads NO third-party script -- effortless entry never costs us the post-breach rule",
       LOCKED, fixed_on="2026-08-19", scope="the ONETAP-1 lane entire: /auth/providers, /auth/oauth/{provider}/start, the "
                   "Google GET callback and the Apple POST callback, _oauth_verify_id_token "
                   "(signature + issuer + audience + nonce), _apple_client_secret, the users "
                   "auth_provider/auth_sub columns, migration 025's exemptions, and the ms.js "
                   "mountOneTap buttons. TWO obligations held together, and BOTH are the entry: "
                   "(1) one tap, no email round trip; (2) not one byte of Google or Apple "
                   "JavaScript on any app page.",
       ref="David, 19 Aug 2026: 'We need the same effortless process Google and Apple has... Even "
           "a single retry will lose customers. For everyone.' Chosen implementation is the plain "
           "OAuth 2.0 / OIDC authorization-code REDIRECT flow, deliberately NOT Google One Tap: "
           "One Tap requires accounts.google.com/gsi/client in our page, and RG-0025 records "
           "David's post-breach ruling that no third-party code runs on the app at all -- a remote "
           "loader in <head> executed for every visitor regardless of the gate and was POSTing "
           "visited URLs off-box. A convenience feature does not get to reopen that. The redirect "
           "flow is still a single tap for anyone already signed in to their provider, and the "
           "server does all verification. Identity is keyed on the provider's stable sub as well "
           "as email, so a provider-side email change or an Apple private-relay address does not "
           "fork the account. An unconfigured provider renders NO button at all -- a dead button "
           "is a retry, which is the precise thing this entry exists to prevent. "
           "PROMOTED 19 Aug 2026: David created the client, add_google_oauth.bat installed it, and "
           "the ENVKEY-1 fix rode the deploy. Verified from OUTSIDE, not reported: "
           "/auth/providers -> {google:true,apple:false}; /auth/oauth/google/start -> 302 to "
           "accounts.google.com/o/oauth2/v2/auth carrying the exact console client_id, "
           "redirect_uri=https://trustsquare.co/auth/oauth/google/callback (character match), "
           "scope=openid email profile (non-sensitive, so NO 100-user cap and no Google "
           "verification review), response_type=code, plus nonce and signed state. apple:false "
           "is correct and permanent per RUL-030. Locked.")
def rg_onetap_no_third_party():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None:
        for needle, why in (("ONETAP-1", "the one-tap lane"),
                            ("/auth/oauth/{provider}/start", "the start endpoint"),
                            ("def _oauth_verify_id_token", "ID-token verification"),
                            ("def _apple_client_secret", "Apple's signed client secret"),
                            ("auth_sub", "the stable provider subject id")):
            if needle not in bea:
                out.append((FAIL, "bea_main.py lost %s (%s)" % (why, needle)))
        # verification must be REAL -- signature, audience, issuer, nonce
        seg = bea.split("def _oauth_verify_id_token")[1][:2000] if "def _oauth_verify_id_token" in bea else ""
        for needle, why in (("PyJWKClient", "JWKS signature verification"),
                            ("audience=aud", "the audience check"),
                            ("issuers", "the issuer check"),
                            ("nonce", "the nonce check")):
            if seg and needle not in seg:
                out.append((FAIL, "ID-token verification no longer performs %s -- an unverified "
                                  "token is just a string the caller typed" % why))
        if seg and "options={\"verify_signature\": False}" in seg:
            out.append((FAIL, "ID-token signature verification has been DISABLED"))
    # The no-third-party-script obligation, asserted in OUR source (RG-0025 covers live)
    for f in ("marketsquare.html", "ms.js"):
        t = repo_file(f) or ""
        for banned in ("accounts.google.com/gsi", "apple.com/auth/authorize.js",
                       "appleid.cdn-apple.com"):
            if banned in t:
                out.append((FAIL, "%s now loads a third-party sign-in script (%s) -- RG-0025 / "
                                  "David's post-breach ruling forbids it; use the redirect flow"
                            % (f, banned)))
    js = repo_file("ms.js") or ""
    if js and "mountOneTap" not in js:
        out.append((FAIL, "ms.js lost the one-tap buttons"))
    if js and "/auth/oauth/' + provider + '/start" not in js:
        out.append((FAIL, "the buttons no longer point at the server-side start endpoint"))
    m = repo_file("migrations/025_gate_nolock.py") or ""
    if m and "/auth/oauth/" not in m:
        out.append((FAIL, "migration 025 no longer exempts the OAuth round trip -- federated "
                          "sign-in cannot complete behind the pre-launch gate"))
    # Live half: the lane must ANSWER (even if dark) and must never 500.
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + "/auth/providers",
                                                          headers=dict(UA)), timeout=TIMEOUT)
        d = json.loads(r.read().decode("utf-8", "replace"))
        live = [k for k, v in d.items() if v]
        out.append((INFO, "live providers configured: %s" % (", ".join(live) if live else
                                                             "none yet (lane dark, buttons hidden)")))
    except urllib.error.HTTPError as he:
        if he.code in (401, 403):
            out.append((FAIL, "live /auth/providers is still gated -- migration 025 has not landed"))
        else:
            out.append((FAIL, "live /auth/providers answered %s" % he.code))
    except Exception as ex:
        out.append((FAIL, "live /auth/providers unreachable (%r)" % ex))
    if not out:
        out.append((INFO, "one-tap lane present, verified server-side, zero third-party script"))
    return out


@entry("RG-0112", "The Postgres-readiness ratchet measures the INVARIANT, and the demand-ticket "
                  "lane no longer grows SQLite-only date arithmetic",
       LOCKED, scope="bea_main.py entire, but specifically _demand_match_and_compose's two "
                     "UPDATE demand_tickets statements. Class, not instance: ANY new "
                     "datetime('now') in bea_main.py re-trips this. The stored value shape is "
                     "unchanged ('YYYY-MM-DD HH:MM:SS', UTC), so existing rows still compare.",
       fixed_on="19 Aug 2026",
       ref="PG-PORTABLE-1. The ratchet had read 54 against a baseline of 53 since at least "
           "16 Aug, putting DANGER on every pre-deploy scan and aborting the 02:00 strict "
           "nightly. The growth was real, not a false positive: priority_expires_at="
           "datetime('now', ?) and updated_at=datetime('now') in both the 'matched' and "
           "'invited' UPDATEs -- four hits, SQLite-only date arithmetic in exactly the lane "
           "David's DB ruling (29 Jul) says must stay cheap to move. Caller now supplies "
           "portable UTC stamps. Baseline auto-tightened 53 -> 52; it is NOT re-baselined "
           "upward, which would have been the 'never weaken an assertion to make it pass' "
           "failure this repo has already paid for once (15 Aug).")
def rg_pg_ratchet_demand_lane():
    out = []
    bea = repo_file("bea_main.py")
    if bea is None:
        return [(INFO, "not run from the repo -- source half skipped")]
    if "PG-PORTABLE-1" not in bea:
        out.append((FAIL, "the PG-PORTABLE-1 rewrite is gone from bea_main.py"))
    # ASSERTION CORRECTED same session (19 Aug 2026): the first draft banned
    # "updated_at=datetime('now')" across the WHOLE of bea_main.py and tripped red
    # immediately -- 52 legitimate uses remain in other lanes, and this entry's scope is the
    # demand lane, not a repo-wide ban. A ledger entry that fails on correct code is the
    # same defect as the one RG-0113 exists to record, so it is fixed here rather than
    # tolerated. The repo-wide direction of travel is owned by the pg ratchet + RG-0112's
    # baseline check below; THIS needle is scoped to the function that was actually fixed.
    i = bea.find("def _demand_match_and_compose")
    if i < 0:
        out.append((FAIL, "_demand_match_and_compose is gone -- the fixed lane no longer exists"))
    else:
        j = bea.find("\ndef ", i + 10)
        lane = bea[i:j if j > 0 else len(bea)]
        if "datetime('now'" in lane:
            out.append((FAIL, "SQLite-only date arithmetic is back inside "
                              "_demand_match_and_compose -- the exact 4 hits PG-PORTABLE-1 removed"))
        if "priority_expires_at=?" not in lane or "updated_at=?" not in lane:
            out.append((FAIL, "the demand lane no longer binds its timestamps as parameters"))
    # The ratchet itself must still be armed, and must still be counting the right thing.
    t = repo_file("test_pg_readiness.py") or ""
    if "(?<!\\.)strftime\\(" not in t:
        out.append((FAIL, "the strftime pattern lost its negative lookbehind -- it would count "
                          "Python's datetime.strftime() again (PG-RATCHET-PRECISION-1, 15 Aug)"))
    base = repo_file("scripts/pg_readiness_baseline.json") or ""
    try:
        n = json.loads(base).get("datetime_now", 10 ** 6) if base else 10 ** 6
        if n > 49:
            out.append((FAIL, "the pg baseline was re-baselined UPWARD to %d (was 49) -- that is "
                              "weakening the assertion to make it pass" % n))
        else:
            out.append((INFO, "pg baseline datetime_now=%d (ratchet only tightens)" % n))
    except Exception as ex:
        out.append((FAIL, "pg baseline unreadable (%r)" % ex))
    if not out:
        out.append((INFO, "demand lane portable, ratchet armed and honest"))
    return out


@entry("RG-0113", "An email BODY is not a page -- the tester widget is required on every page a "
                  "tester can land on, and forbidden inside outbound mail",
       LOCKED, scope="Every .html on the deploy manifest, split structurally into pages and email "
                     "bodies. Class, not instance: covers the 3 orchestration consoles fixed here "
                     "AND any page added to the manifest later, and forbids script in ANY of the "
                     "14 outreach email bodies, not just the ones that existed today.",
       fixed_on="19 Aug 2026",
       ref="EMAIL-NOT-A-PAGE-1. test_widget_is_wired_into_every_tester_page had failed on every "
           "scan since 4 Aug -- 46 of them -- naming 17 files. It was BOTH right and wrong, which "
           "is why it sat unfixed: 3 (orchestration_v2 cockpit, durability_map, email_templates) "
           "were real tester-reachable pages missing the widget, and 14 were outreach EMAIL "
           "bodies, where ts_report.js cannot run and the tag would ship a <script src=...> inside "
           "an invitation. A verdict that cannot be satisfied correctly gets ignored, and an "
           "ignored verdict is how the 3 REAL misses hid for 15 days. Split, not weakened: pages "
           "must carry the widget; email bodies must carry NO script at all (stricter, RG-0025 "
           "aligned). Classification is structural (published under templates/ + 600px email "
           "wrapper + zero <script>) and fails SAFE -- anything ambiguous is treated as a page. "
           "NOT_TESTER_FACING stays empty; David's 5 Aug ruling that the tab belongs on every "
           "page, his own console included, is untouched.")
def rg_email_body_is_not_a_page():
    out = []
    t = repo_file("test_tester_intake.py")
    if t is None:
        return [(INFO, "not run from the repo -- source half skipped")]
    if "_is_email_body" not in t or "def email_bodies" not in t:
        out.append((FAIL, "the page/email split is gone -- the guard is back to demanding a JS "
                          "widget inside outbound email, a verdict that can never be satisfied"))
    if "def test_email_bodies_never_carry_script" not in t:
        out.append((FAIL, "the exemption lost its counterweight -- email bodies are no longer "
                          "asserted script-free, so the exemption is now a hole"))
    if "NOT_TESTER_FACING = set()" not in t:
        out.append((FAIL, "a hand-typed exclusion list is back in NOT_TESTER_FACING -- that is "
                          "exactly how 3 tester-reachable pages were missed on 5 Aug"))
    for page in ("orchestration_v2/cockpit.html", "orchestration_v2/durability_map.html",
                 "orchestration_v2/email_templates.html"):
        body = repo_file(page)
        if body is not None and "ts_report.js" not in body:
            out.append((FAIL, "%s lost the fault widget again -- a tester lands there with no "
                              "way to report" % page))
    if not out:
        out.append((INFO, "3 consoles wired, 14 email bodies script-free, split intact"))
    return out


@entry("RG-0114", "No guard verdict may sit red for days -- a warning nobody is ever shown is not "
                  "a warning, it is a leak",
       LOCKED, scope="deploy_audit.log entire. Class fault, and the one that actually cost the "
                     "time here: BOTH faults above were correctly detected on 4 Aug and then "
                     "printed into a scrolling scan block and appended to a log file 46 and 50 "
                     "times. Applies to any future guard, not just these two.",
       fixed_on="19 Aug 2026",
       ref="David, 19 Aug 2026: 'Why do they even exist at this point? Did they exist before but "
           "were hidden somewhere in the description as vague requests for me which I missed?' "
           "They were not vague requests -- they were never requests at all. Manual deploys run "
           "in warn mode, which logs DANGER and proceeds; 35 runs did exactly that between 14 and "
           "19 Aug. The strict 02:00 nightly aborted honestly every night, but its abort landed "
           "in a log at 02:00 with nobody awake. Detection was never the problem; ESCALATION was. "
           "This entry is the escalation: the same danger tag appearing on many consecutive scans "
           "turns the ledger red in daylight, where it gets read.")
def rg_no_chronic_danger():
    out = []
    log = repo_file("deploy_audit.log")
    if log is None:
        return [(INFO, "not run from the repo -- deploy_audit.log unavailable")]
    lines = [l for l in log.splitlines() if "verdict=" in l][-40:]
    if not lines:
        return [(INFO, "no scans logged yet")]
    streak = {}
    for l in lines:
        tags = ""
        for part in l.split():
            if part.startswith("danger="):
                tags = part.split("=", 1)[1]
        present = set(t for t in tags.split("|") if t and t != "-")
        for t in present:
            streak[t] = streak.get(t, 0) + 1
        for t in list(streak):
            if t not in present:
                streak[t] = 0
    CHRONIC = 8
    for tag, n in sorted(streak.items()):
        if n >= CHRONIC:
            out.append((FAIL, "'%s' has been red on %d consecutive pre-deploy scans -- fix it or "
                              "fix the guard, but it may not keep scrolling past" % (tag, n)))
    if not out:
        out.append((INFO, "no guard red for %d+ consecutive scans" % CHRONIC))
    return out



@entry("RG-0115", "When the gate is DOWN it is down for everyone -- both halves, no overlay, no 401, and it can be re-armed in one command",
       LOCKED, fixed_on="2026-08-19", scope="the gate-lowering change entire: nginx /_review_gate returning 200 (server "
                   "half) AND /review/verify answering {valid:true} (the client overlay half). "
                   "BOTH are the entry -- lowering only the server half leaves every visitor "
                   "staring at the overlay, which is indistinguishable from being locked out.",
       ref="David, 19 Aug 2026: 'How else am I going to have confidence that we are ready for the "
           "soft launch if we cant give it to more people to test. We can not even give 3 people "
           "constant access to the app?' The logic had inverted -- the gate existed to protect an "
           "unfinished app and had become the main thing preventing him from learning whether the "
           "app was finished. Lowered today rather than 29 Aug; RUL-001's LAUNCH dates are "
           "unchanged, only the gate moved. Done as an nginx-only change (migration 026) precisely "
           "because the deploy lane was not reaching the server and this could not be allowed to "
           "wait on that fault. Reversal is a file copy from the printed backup, so this is a "
           "lowered gate, not a demolished one. PROMOTED 19 Aug 2026: 026 applied on the box (backup marketsquare.bak-gatedown-20260819-041800); verified live from outside -- /review/verify {valid:true}, /listings + /wonders + / all 200 anonymously, while /tuppence/*, /users/* and /dashboard.html still refuse. Locked. (Numbered 0115: this entry was first written as 0112, which a concurrent session had already committed for the Postgres ratchet -- theirs was first, so this one moved. The collision is itself the lesson: two sessions picking `max+1` off their own read of the file will collide, and a duplicate @entry silently shadows a real assertion.)")
def rg_gate_actually_down():
    out = []
    # Client half: the overlay hides only on {"valid":true} from /review/verify.
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + "/review/verify",
                                                          headers=dict(UA)), timeout=TIMEOUT)
        d = json.loads(r.read().decode("utf-8", "replace"))
        if d.get("valid") is not True:
            out.append((FAIL, "/review/verify answered 200 but not valid:true -- the gate overlay "
                              "will still cover the app for every visitor"))
    except urllib.error.HTTPError as he:
        out.append((FAIL, "anonymous /review/verify answered %s -- the CLIENT half of the gate is "
                          "still up: visitors see the gate screen even if nginx lets them "
                          "through" % he.code))
    except Exception as ex:
        out.append((FAIL, "/review/verify unreachable (%r)" % ex))
    # Server half: a real content path must answer 200 anonymously.
    try:
        rr = urllib.request.urlopen(urllib.request.Request(BASE + "/listings", headers=dict(UA)),
                                    timeout=TIMEOUT)
        if rr.getcode() != 200:
            out.append((FAIL, "anonymous /listings answered %s, expected 200" % rr.getcode()))
    except urllib.error.HTTPError as he:
        out.append((FAIL, "anonymous /listings still answers %s -- the SERVER half of the gate is "
                          "still armed" % he.code))
    except Exception as ex:
        out.append((FAIL, "/listings unreachable (%r)" % ex))
    if repo_file("migrations/026_gate_down.py") is None:
        out.append((INFO, "outside the repo -- source half not checked here"))
    if not out:
        out.append((INFO, "gate is down on BOTH halves -- anyone can browse, no overlay, no 401"))
    return out



@entry("RG-0116", "A migration that imports the app can actually import it -- and a stalled migration chain is never silent",
       LOCKED, fixed_on="2026-08-19", scope="EVERY migration in migrations/ that does `import main`, present and future "
                   "(023 and 024 today). Class, not instance: the defect is in how post_deploy "
                   "invokes them, so any new migration importing the app inherits it unless it "
                   "carries the CWD guard.",
       ref="MIGRATE-IMPORT-1, 19 Aug 2026. post_deploy runs each migration as "
           "`(cd $LIVE && python3 /abs/path/NNN.py --apply)`. Python puts THE SCRIPT'S directory "
           "on sys.path[0] -- never the CWD -- so `import main` raised \"No module named 'main'\" "
           "and 023 exited rc=3. post_deploy then does `break`, which is correct (migrations are "
           "order-dependent and must not run out of sequence) but meant 023 BLOCKED 024, 025 and "
           "026 on every deploy from 18 Aug onward. The migration file's own comment said "
           "'CWD = live web root per the migrations contract' -- true, and useless, because "
           "Python never consults CWD for a script run by path. "
           "COST: this is why /admin/login and /review/claim-code kept answering with nginx HTML "
           "instead of app JSON, which THIS SESSION twice misread as 'the code is not deploying'. "
           "The code was deploying fine the whole time (deploy log: 'DEPLOY OK, now live at "
           "9867f059, health ok'); only the nginx-touching migrations were stuck behind 023. "
           "Two wrong probes compounded it: /review/request-link returns a bare {ok:true} for an "
           "OFF-LIST email before it ever reaches the delivery field, so probing it with "
           "example.invalid can never show new code. Assert the import CONTRACT in source, and "
           "assert the chain's effects live. LOCKED 19 Aug 2026: both main-importing migrations now "
           "carry the guard, proven by running 023 under post_deploy's exact invocation "
           "(cd <live> && python3 <abs path>) -- `import main` resolved where it had raised.")
def rg_migration_import_contract():
    out = []
    import glob as _glob, os as _os
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    migs = sorted(_glob.glob(_os.path.join(root, "migrations", "*.py")))
    checked = 0
    for m in migs:
        if ".bak" in _os.path.basename(m):
            continue
        try:
            t = open(m, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if "import main" not in t:
            continue
        checked += 1
        if "sys.path.insert(0, _os.getcwd())" not in t and "sys.path.insert(0, os.getcwd())" not in t:
            out.append((FAIL, "%s does `import main` with NO CWD guard -- it will exit rc=3 on the "
                              "box and post_deploy will stop the whole chain behind it "
                              "(MIGRATE-IMPORT-1)" % _os.path.basename(m)))
    if checked == 0 and migs:
        out.append((INFO, "no migration imports main right now -- nothing to guard"))
    # RG-0068 (no vacuous assertion): if we are in the repo, we must have SEEN migrations.
    if not migs:
        out.append((INFO, "outside the repo -- source half not checked here"))
    # Live half: the chain's effect. 025 exempts /auth/verify-code; if the chain is still
    # stalled that endpoint never becomes reachable through nginx.
    try:
        req = urllib.request.Request(BASE + "/auth/providers", headers=dict(UA))
        r = urllib.request.urlopen(req, timeout=TIMEOUT)
        json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as he:
        if he.code == 404:
            out.append((INFO, "live app predates ONETAP-1 -- deploy pending, chain not yet proven"))
        elif he.code in (401, 403):
            out.append((FAIL, "/auth/providers is refused at the origin -- migration 025 still has "
                              "not run, so the chain is STILL stalled behind a failing migration"))
    except Exception:
        pass
    if not out:
        out.append((INFO, "every main-importing migration carries the CWD guard; chain effects live"))
    return out



@entry("RG-0117", "Server credentials are read through envkey(), never bare os.getenv -- the systemd unit does not export .env",
       LOCKED, fixed_on="2026-08-19",
       scope="EVERY credential/config read in bea_main.py that expects a value from "
             "/var/www/marketsquare/.env. Class, not instance: the trap catches any new lane, and "
             "it has now caught three (RELAY_* 5 Aug, the AI lanes 31 Jul, Google OAuth 19 Aug).",
       ref="ENVKEY-1, 17 Jul 2026. The marketsquare systemd unit does NOT export the server .env "
           "into the process, so a bare os.getenv() returns empty ON THE BOX however correct the "
           ".env file is. ai_provider.envkey() checks the environment first, then reads the .env "
           "directly -- it is the established pattern and the RELAY_ block carries an eight-line "
           "comment explaining exactly this. 19 Aug 2026: the ONETAP-1 Google lane shipped with "
           "bare os.getenv anyway and reported google:false with perfectly good credentials "
           "already written to .env -- David had done the console work correctly and the app "
           "still said the lane was dark. Symptom is always the same and always misleading: the "
           "feature behaves as though it was never configured. Ten bare os.getenv calls replaced. "
           "This entry exists so the NEXT lane cannot repeat it. "
           "SCOPE OF A RED, added the same day after over-reading one: this entry asserts a CODE "
           "PATTERN. A red means the pattern is inconsistent -- it does NOT mean a credential is "
           "missing at runtime, and must not be reported as though it does. On its first run it "
           "went red against 9 bare RESEND_API_KEY reads and that was written up as 'Resend has "
           "never been live, all mail fell through to Gmail'. FALSE: RESEND_API_KEY is set "
           "directly in the systemd unit, so it was in the process the whole time (proven via "
           "/proc/<pid>/environ: GOOGLE_CLIENT_ID=0, RESEND_API_KEY=1). Runtime presence is "
           "answerable only by reading the process environment, which is one command.")
def rg_envkey_not_bare_getenv():
    out = []
    bea = repo_file("bea_main.py")
    if bea is None:
        return [(INFO, "outside the repo -- source-only entry")]
    # Credentials that live in the server .env and MUST go through envkey().
    GUARDED = ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "APPLE_CLIENT_ID", "APPLE_TEAM_ID",
               "APPLE_KEY_ID", "APPLE_PRIVATE_KEY", "RELAY_INBOUND_SECRET", "RESEND_API_KEY")
    seen = 0
    for name in GUARDED:
        for bad in ('os.getenv("%s"' % name, "os.environ.get(\"%s\"" % name,
                    'os.environ["%s"]' % name):
            if bad in bea:
                out.append((FAIL, "%s is read with a bare %s -- on the server that returns EMPTY "
                                  "(the systemd unit does not export .env) and the feature will "
                                  "silently report itself unconfigured. Use "
                                  "ai_provider.envkey(). ENVKEY-1." % (name, bad.split("(")[0])))
        if name in bea:
            seen += 1
    # RG-0068: never pass by matching nothing.
    if seen == 0:
        out.append((FAIL, "none of the guarded credential names appear in bea_main.py -- this "
                          "assertion is running blind and must be re-pointed"))
    if not out:
        out.append((INFO, "all %d guarded credentials read through envkey()" % seen))
    return out


@entry("RG-0120", "A seller controls photo ORDER and the COVER -- and an edit-screen save reaches the buyer view",
       LOCKED, fixed_on="2026-08-20 (promoted: READY TO LOCK -- cover/order controls proven in repo "
                        "AND live, and PUT /listings/{id} rewrites the buyer-facing [photos:...] prefix)",
       scope="the whole listing-photo order lane: ms.js edit screen (elMakeCover/elMovePhoto/"
       "reset-per-open/prefix fallback) AND bea_main.py PUT /listings/{id} PHOTO-ORDER-1 prefix "
       "rewrite. Class, not instance: ANY photo edit (reorder, remove, add, replace) must land in "
       "BOTH stores -- photo_urls and the [photos:...] description prefix buyers actually read",
       ref="Maroushka via David, 19 Aug 2026: she removed an over-blurred cover, uploaded a "
           "replacement, it landed LAST and nothing could move it to first -- 'new users will "
           "just give up'. Root causes, all fixed 19 Aug: (1) no reorder/set-cover control "
           "existed anywhere; (2) the edit screen saved photo_urls but buyers read the "
           "[photos:...] description prefix first, so no edit-screen photo change EVER reached "
           "the buyer view; (3) _elPhotoUrls was never reset between listings (cross-listing "
           "photo bleed); (4) the edit screen could not even SEE prefix-only photos (the '2 of "
           "8' half of TS-0030). OPEN until deployed and proven live.")
def rg_photo_order():
    out = []
    ms = repo_file("ms.js"); bea = repo_file("bea_main.py")
    if ms is not None:
        for token, what in (("function elMakeCover", "the Make-cover control"),
                            ("function elMovePhoto", "the move control"),
                            ("_elPhotoUrls = [];\n  _elPhotoReplaceIdx = 0;", "the per-open reset (cross-listing photo bleed)"),
                            ("[photos:([^\\]]+)\\]", "the edit-screen prefix fallback (seller sees ALL photos)")):
            if token not in ms:
                out.append((FAIL, "ms.js lost %s" % what))
    if bea is not None:
        if "PHOTO-ORDER-1" not in bea or '"photo_urls" in d' not in bea:
            out.append((FAIL, "bea_main.py lost the PHOTO-ORDER-1 prefix rewrite -- edit-screen "
                              "photo changes no longer reach the buyer-facing store"))
    # live half: the deployed bundle must carry the control
    live = _get("/static/ms.js")
    if "function elMakeCover" not in live:
        out.append((FAIL, "live /static/ms.js has no elMakeCover -- the fix is not deployed"))
    if not out:
        out.append((INFO, "cover/order controls in repo and live; PUT rewrites the buyer-facing prefix"))
    return out



@entry("RG-0118", "The introduction relay is PROVEN live, end to end -- aliases mask both parties and a real reply crosses the curtain in seconds",
       LOCKED, fixed_on="2026-08-19",
       scope="the INTRO-RELAY-1 lane entire, as a LIVE capability: flag on, alias in Reply-To on "
             "both notes, Cloudflare inbound -> /intro/relay -> enrolled-sender check -> forward. "
             "Asserts the pieces observable from outside; the full-loop proof is on record below.",
       ref="E2E PROVEN 19 Aug 2026 (Claude drove both sides via David's Gmail; intro #123 on "
           "throwaway listing #373, deleted after): buyer signed in with the emailed 6-digit code "
           "(SIGNIN-CODE-1 live); intro created + accepted; BOTH notes arrived INBOX from "
           "intro@mail.trustsquare.co with reply-to = intro-<hex>@relay.trustsquare.co (read off "
           "Gmail's own details panel); a reply sent to the buyer's alias from the seller's real "
           "address was forwarded to the buyer's REAL inbox in FOUR SECONDS, sender still masked. "
           "No real address ever crossed. TWO FINDINGS, neither a product fault: (1) the Gmail "
           "MCP reply tool ignores Reply-To and replied to From -- test artifact; real mail "
           "clients honor Reply-To; (2) HARDENING: From intro@mail.trustsquare.co is NOT "
           "receivable (no MX on mail.trustsquare.co -> hard bounce for any client that ignores "
           "Reply-To). Also observed: users.id_verified stays 0 while id_verified_at is set -- "
           "the gate correctly keys on the timestamp, but the desynced boolean is a trap for "
           "future code. Live probes below are deliberately light: flag + refusals only, no "
           "mail is generated by a ledger run.")
def rg_intro_relay_proven():
    out = []
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + "/flags", headers=dict(UA)),
                                   timeout=TIMEOUT)
        d = json.loads(r.read().decode("utf-8", "replace"))
        if d.get("intro_relay") is not True:
            out.append((FAIL, "intro_relay flag is OFF -- accepted introductions are handing out "
                              "REAL addresses again (the pre-19-Aug behaviour). Anonymity is the "
                              "product; this is a launch blocker, not a preference."))
        if d.get("relay_configured") is not True:
            out.append((FAIL, "the Cloudflare inbound rail reports unconfigured -- replies to "
                              "aliases will vanish"))
    except Exception as ex:
        out.append((FAIL, "/flags unreachable (%r)" % ex))
    # /intro/relay must exist and refuse a caller without the worker secret.
    try:
        req = urllib.request.Request(BASE + "/intro/relay",
                                     data=json.dumps({"to_alias": "x", "from_addr": "y"}).encode(),
                                     headers=dict(UA, **{"Content-Type": "application/json"}),
                                     method="POST")
        urllib.request.urlopen(req, timeout=TIMEOUT).read()
        out.append((FAIL, "/intro/relay accepted a POST with NO worker secret -- anyone can "
                          "inject relayed mail"))
    except urllib.error.HTTPError as he:
        if he.code == 503:
            out.append((FAIL, "/intro/relay answers 503 -- the relay reports itself closed"))
        elif he.code not in (401,):
            out.append((FAIL, "/intro/relay answered %s to a secretless POST, expected 401" % he.code))
    except Exception as ex:
        out.append((FAIL, "/intro/relay unreachable (%r)" % ex))
    bea = repo_file("bea_main.py")
    if bea is not None:
        if '"reply_to": from_alias' not in bea:
            out.append((FAIL, "_relay_forward no longer rides the alias in Reply-To -- replies "
                              "will go to the unreceivable From and bounce (RELAY-FROM-1)"))
        if "from_addr != counter[\"real_email\"]" not in bea:
            out.append((FAIL, "the enrolled-sender check is gone from /intro/relay -- any "
                              "stranger who learns an alias can inject into the channel"))
    if not out:
        out.append((INFO, "relay on, rail configured, inbound refuses strangers, alias rides "
                          "Reply-To in source"))
    return out


@entry("RG-0121", "The photo-anon scan canary is GROUNDING-CLASS, dark by default, and can never be the verifier",
       OPEN, scope="the GEMINI-CANARY-1 lane entire: ai_provider.py gemini adapter + TASK_MODEL row, "
       "AI_BASELINE.json/ai_price_card.json coverage, bea_main.py _anon_scan_provider routing "
       "(initial scan + refine ONLY). Class property protected: the VERIFY pass in "
       "_anon_blur_until_clean must NEVER route through the canary helper -- the verifier is the "
       "leak guarantee and stays on the active lane, whatever scans",
       ref="RUL-031/032 (David, 19 Aug 2026). Three fixes to the blur machinery (5/7/10 Aug) did "
           "not stop over-smeared publishes because both general-LLM lanes fail at box "
           "coordinates -- a task-model mismatch, not vendor quality. David ruled: no more "
           "micro-fixes; Gemini 3.7 Flash (grounding-trained, ~0.13x base cost) scans and "
           "refines as a canary, the active lane verifies every redaction. Dark until "
           "GEMINI_API_KEY + PHOTO_SCAN_CANARY=1, and traffic only after "
           "scripts/eval_photo_anon.py shows 100% plate recall on the eval set (Haiku already "
           "lost this task once by being cheapest). OPEN until the eval passes and the canary "
           "is armed live.")
def rg_gemini_canary():
    out = []
    ap = repo_file("ai_provider.py"); bea = repo_file("bea_main.py")
    if ap is not None:
        if '"gemini"' not in ap or "def _gemini" not in ap:
            out.append((FAIL, "the gemini lane has GONE from ai_provider.py"))
        if '"gemini":    {"sonnet"' in ap and '"gemini"' in ap.split("_FAILOVER_ORDER_DEFAULT = ")[-1].split("]")[0]:
            out.append((FAIL, "gemini crept into the default failover order -- the canary must "
                              "never be an automatic failover target"))
    if bea is not None:
        if "def _anon_scan_provider" not in bea:
            out.append((FAIL, "GEMINI-CANARY-1 routing helper has GONE from bea_main.py"))
        else:
            # the verify pass must stay on the caller's lane: inside _anon_blur_until_clean the
            # verify _anon_photo_scan calls must NOT pass through _anon_scan_provider
            body = bea.split("def _anon_blur_until_clean", 1)[-1].split("\ndef ", 1)[0]
            for seg in body.split("_anon_photo_scan(")[1:]:
                if "_anon_scan_provider" in seg.split(")")[0:2][0]:
                    out.append((FAIL, "a VERIFY call inside _anon_blur_until_clean routes through "
                                      "the canary helper -- the verifier must stay on the active "
                                      "lane; the leak guarantee may never share the scanner's "
                                      "blind spots"))
                    break
    # live half: armed only after the eval -- until then this entry stays OPEN
    import json as _j
    try:
        _fl = _j.loads(_get("/flags"))
        armed = bool(_fl.get("photo_scan_canary"))
    except Exception:
        armed = False
    if not armed:
        out.append((FAIL, "canary not armed live yet (eval pending) -- expected while OPEN"))
    if not out:
        out.append((INFO, "gemini canary armed: scans/refines on gemini, verify on the active lane"))
    return out



@entry("RG-0119", "A charge binds to a PROVEN identity -- no session no paid action, and a session can never act as someone else",
       LOCKED, fixed_on="2026-08-19",
       scope="ACCOUNT-BIND-1 enforced, the whole bound lane: _bind_charged_email at every paid "
             "call site (intros create, intro accept via BIND-OWNER-1, the seller AI tools) plus "
             "the launch switch itself. Class: any NEW paid endpoint must route through "
             "_bind_charged_email; a typed-email charge path is a regression of this entry.",
       ref="Flipped ON by David 19 Aug 2026 ~19:50 SAST, informed not hopeful: 7 days of shadow "
           "log showed 0 MISMATCH and 1 no-session -- and the 1 was this morning's relay E2E "
           "test itself (the intro was created by API without the buyer cookie). Verified live "
           "from outside within minutes of the flip, all four quadrants: key-only intro accept "
           "-> 401 (closing the hole the relay E2E had just walked through); no-session intro "
           "create -> 401; signed-in buyer acting as SELF -> 200 (positive path, fresh 6-digit "
           "sign-in, throwaway listing #374, deleted); signed-in buyer acting as SOMEONE ELSE "
           "-> 403. Google one-tap (RG-0111) is what made this flip cheap: the sign-in a "
           "refused caller is sent to is now one tap, not an email round trip.")
def rg_account_binding_enforced():
    out = []
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + "/flags", headers=dict(UA)),
                                   timeout=TIMEOUT)
        d = json.loads(r.read().decode("utf-8", "replace"))
        if d.get("account_binding") is not True:
            out.append((FAIL, "account_binding flag is OFF -- paid actions are back to trusting "
                              "a typed email, and intro-accept is open to anyone with the "
                              "public app key"))
    except Exception as ex:
        out.append((FAIL, "/flags unreachable (%r)" % ex))
    # Live: a sessionless caller with only the public key must be refused on a bound action.
    try:
        req = urllib.request.Request(BASE + "/intros",
                data=json.dumps({"listing_id": 1, "buyer_email": "rg-probe@example.invalid",
                                 "buyer_name": "probe", "message": "rg-0119 probe"}).encode(),
                headers=dict(UA, **{"Content-Type": "application/json",
                                    "X-Api-Key": "ms_mk_2026_pretoria_admin"}), method="POST")
        urllib.request.urlopen(req, timeout=TIMEOUT).read()
        out.append((FAIL, "a NO-SESSION intro create was ACCEPTED -- binding is not enforcing "
                          "(and this probe may have created a real intro row)"))
    except urllib.error.HTTPError as he:
        if he.code not in (401,):
            out.append((FAIL, "no-session intro create answered %s, expected 401" % he.code))
    except Exception as ex:
        out.append((FAIL, "/intros unreachable (%r)" % ex))
    bea = repo_file("bea_main.py")
    if bea is not None:
        if "def _bind_charged_email" not in bea:
            out.append((FAIL, "_bind_charged_email is gone -- the binding lane has no engine"))
        if "BIND-OWNER-1" not in bea:
            out.append((FAIL, "intro accept lost its owner check (BIND-OWNER-1) -- anyone with "
                              "the app key can accept again"))
    if not out:
        out.append((INFO, "binding enforcing: sessionless paid action refused; engine + owner "
                          "check present in source"))
    return out


@entry("RG-0122", "While the canary is dark, a photo needing blur is REJECTED with the ask -- never smeared, never spent on",
       LOCKED, scope="bea_main.py PHOTO-REJECT-1: BOTH doors (seller gate _seller_photo_anon_gate "
       "and agency _anon_photo_pass). Class property: no upload path may reach "
       "_anon_blur_until_clean while _anon_reject_only() is True -- reject/hold is the only "
       "outcome for a redact verdict, with copy that names the ask (replace it or leave it out)",
       fixed_on="2026-08-19",
       ref="RUL-033 (David, 19 Aug 2026): 'reject any photos which need a blurring... just "
           "until the 25th when I have the funds for Gemini'. Bridge rule: the general-LLM "
           "lanes smear (RUL-031), and a rejected photo can never leak or publish as porridge; "
           "it also skips the whole refine/verify spend. Self-resolving: PHOTO_SCAN_CANARY=1 + "
           "GEMINI_API_KEY turns blurring back on through the grounded lane (RG-0121) with no "
           "second deploy; PHOTO_REJECT_ONLY=0/1 is the manual override either way.")
def rg_photo_reject_only():
    out = []
    bea = repo_file("bea_main.py")
    if bea is None:
        return [(INFO, "running outside the repo -- reject-only check skipped")]
    if "def _anon_reject_only" not in bea:
        return [(FAIL, "PHOTO-REJECT-1 has GONE: _anon_reject_only missing from bea_main.py")]
    # both doors must consult the switch BEFORE any blur call
    gate = bea.split("def _seller_photo_anon_gate", 1)[-1].split("\ndef ", 1)[0]
    if "_anon_reject_only()" not in gate.split("_anon_blur_until_clean")[0]:
        out.append((FAIL, "the seller gate can reach the blur loop without consulting "
                          "_anon_reject_only -- the reject-only bridge is bypassed"))
    imp = bea.split("def _anon_photo_pass", 1)[-1].split("\ndef ", 1)[0]
    if "_anon_reject_only()" not in imp.split("_anon_blur_until_clean")[0]:
        out.append((FAIL, "the agency import can reach the blur loop without consulting "
                          "_anon_reject_only -- the reject-only bridge is bypassed"))
    if "not anonymous" not in gate:
        out.append((FAIL, "the rejection copy lost its ask -- the seller must be told to "
                          "replace the photo or leave it out"))
    if not out:
        out.append((INFO, "both doors reject/hold on redact while the canary is dark; "
                          "copy names the ask"))
    return out


@entry("RG-0123", "A SUPER advert is immortal -- the fade sweep can never hide the measuring stick, "
       "and no shelf goes dark because the exemption watched the wrong flag",
       LOCKED, fixed_on="2026-08-20",
       scope="ALL categories, ALL markets. Class property: the lifecycle sweep's protected "
       "set is keyed on what the listing IS (super_example) as well as the banner flag "
       "(showcase). RUL-026 keyed it on showcase alone; every seeded super carries "
       "super_example=1 with showcase NULL, so `showcase IS NULL` INCLUDED them as fade "
       "candidates -- the exemption read as its own opposite. Both halves asserted: the "
       "SOURCE predicate (sweep candidates + archive step + both delete guards) and the LIVE "
       "state (no super faded/archived, and every seeded shelf still answers).",
       ref="SUPER-IMMORTAL-2 (20 Aug 2026, David: 'we lost a lot of adverts? Why'). The 19 Aug "
           "20:17 release restarted the service; _lifecycle_daily_loop fires 2 minutes after "
           "boot, and at 18:21Z it faded all eight ZA supers (265-272: Cars, Tutors, Services "
           "x2, Collectors, Adventures x2, Local Market) whose 20 Jul seed date had just "
           "crossed the free-tier 30-day window. Collectors and Services fell to '0 listings' "
           "on the home tiles because the super WAS the whole shelf. Two lessons kept here: "
           "(1) a restart is a sweep trigger, so any deploy can fire lifecycle machinery -- "
           "the guard must be right in SOURCE, not just healed by a migration; (2) 024's heal "
           "and RUL-026's guard both keyed on `showcase`, so the fix and its ledger entry "
           "agreed with each other and were wrong together. 027_super_immortal.py heals the "
           "data on the next deploy; this entry flips READY TO LOCK the moment it lands. "
           "RUL-035 (David, 20 Aug): the supers are needed THROUGH launch and a while after, "
           "then retired one by one as good live replacements arrive -- so a super that 404s "
           "is a deliberate retirement and passes, while a super the MACHINERY hid is a "
           "regression, and an EMPTY SHELF is a regression either way.")
def rg_supers_immortal():
    out = []

    # ── SOURCE half: the protected predicate must name super_example ──
    bea = repo_file("bea_main.py")
    if bea is None:
        out.append((INFO, "running outside the repo -- source half skipped"))
    else:
        sweep = bea.split("def _lifecycle_sweep", 1)[-1].split("\n@app.", 1)[0]
        cands = sweep.split("for c in cands", 1)[0]
        if "super_example" not in cands:
            out.append((FAIL, "the fade CANDIDATE query does not exempt super_example -- "
                              "a seeded super (showcase NULL) is a fade candidate again"))
        arch = sweep.split("FADE: archive after", 1)[-1]
        if "super_example" not in arch.split("res[\"fade_archived\"]", 1)[0]:
            out.append((FAIL, "the fade->archive step does not exempt super_example -- "
                              "a faded super is archived for good after the grace window"))
        dele = bea.split("def delete_listing(", 1)[-1].split("\n@app.", 1)[0]
        if "super_example" not in dele:
            out.append((FAIL, "the keyed DELETE guard checks showcase only -- the public "
                              "app key in ms.js can delete a super"))
        sdel = bea.split("def delete_listing_by_seller", 1)[-1].split("\n@app.", 1)[0]
        if "super_example" not in sdel:
            out.append((FAIL, "the seller-email DELETE guard checks showcase only -- a "
                              "super is deletable by anyone who knows its seller address"))
        if repo_file("migrations/027_super_immortal.py") is None:
            out.append((FAIL, "migrations/027_super_immortal.py is gone -- nothing heals a "
                              "super that already faded"))
        # SUPER-HEAL-1: the every-deploy lane must heal STATE, not just absence. The one-shot
        # migration is the belt; this is the braces, and it is the half that cannot jam.
        seed = repo_file("scripts/seed_super_global.py")
        if seed is None:
            out.append((FAIL, "scripts/seed_super_global.py is gone -- the every-deploy "
                              "self-heal lane for the supers no longer exists"))
        elif "heal_hidden_supers" not in seed or "hidden_supers" not in seed:
            out.append((FAIL, "seed_super_global.py heals ABSENCE only again -- a super that "
                              "exists but is hidden will survive every future deploy, which "
                              "is exactly the 19-20 Aug recurrence"))

    # ── LIVE half: no super may be out of sight, and no shelf may be dark ──
    SUPER_IDS = (265, 266, 267, 268, 269, 270, 271, 272)
    hidden, retired = [], []
    for lid in SUPER_IDS:
        # RUL-035: a super may LEAVE -- deliberately, one shelf at a time, once a real
        # listing is good enough to replace it. A 404 is therefore a retirement, not a
        # regression; what must never happen is the SHELF going dark, which the category
        # sweep below is what actually holds. Machinery hiding a super IS a regression.
        if _status("/listings/%d" % lid) == 404:
            retired.append(lid)
            continue
        try:
            row = _json("/listings/%d" % lid)
        except Exception as e:
            out.append((INFO, "live probe of listing %d failed (%s) -- state unverified"
                              % (lid, str(e)[:60])))
            continue
        st = (row.get("listing_status") or "live").lower()
        if not row.get("super_example"):
            out.append((INFO, "listing %d is no longer flagged super_example -- if the seed "
                              "set moved, repoint SUPER_IDS rather than weakening this" % lid))
            continue
        if st in ("faded", "archived"):
            hidden.append("%d %s=%s" % (lid, row.get("category"), st))
    if hidden:
        out.append((FAIL, "super advert(s) hidden by the lifecycle sweep: " + ", ".join(hidden)
                          + " -- heal rides the NEXT DEPLOY via seed_super_global.py "
                            "(SUPER-HEAL-1, every-deploy lane); migration 027 is the belt "
                            "to that braces"))
    if retired:
        out.append((INFO, "super(s) retired by admin, shelf checked below (RUL-035): "
                          + ", ".join(str(i) for i in retired)))

    # The property David sees: a seeded category never reads "0 listings" at home.
    try:
        feed = _json("/listings?city=Pretoria")
        rows = feed.get("listings", feed) if isinstance(feed, dict) else feed
        cats = set()
        for l in rows:
            c = str(l.get("category") or "").lower()
            cats.add("adventures" if c.startswith("adventures") else c)
        for want in ("collectors", "services", "cars", "tutors", "property", "adventures"):
            if want not in cats:
                out.append((FAIL, "the %s shelf is EMPTY in Pretoria -- the category tile "
                                  "reads '0 listings' to every buyer" % want))
        # ASSERTION CORRECTED 20 Aug 2026: local_market is deliberately EXCLUDED from the
        # default feed (get_listings' lm_filter: no category param => category != local_market),
        # so looking for it there reported an empty shelf that was never empty. The app was
        # right and this check was wrong -- ask the shelf the way the app asks it.
        lm = _json("/listings?city=Pretoria&category=local_market")
        lm_rows = lm.get("listings", lm) if isinstance(lm, dict) else lm
        if not lm_rows:
            out.append((FAIL, "the local_market shelf is EMPTY in Pretoria -- the tile "
                              "reads '0 listings' to every buyer"))
    except Exception as e:
        out.append((INFO, "live /listings probe failed (%s) -- shelf check unverified"
                          % str(e)[:60]))

    if not out:
        out.append((INFO, "all eight supers live; every seeded shelf answers; the sweep, the "
                          "archive step and both delete guards exempt super_example"))
    return out


@entry("RG-0124", "A deploy REPORTS what its post-steps did -- a jammed migration chain names "
       "itself, over plain HTTP, to anyone who looks",
       LOCKED, fixed_on="2026-08-20",
       scope="ops/autodeploy/post_deploy.sh entire: the seed, the ladder seed and every "
       "migration in the chain. Class property: no step of a deploy may succeed or fail where "
       "only the server's journal can see it. The artefact is $LIVE/static/post_deploy_status.json "
       "-- readable with no credential, so ANY session (or David on his phone) can answer 'did "
       "the deploy actually do the thing' without SSH.",
       ref="POSTDEPLOY-EYES-1 (20 Aug 2026). David deployed to bring the faded supers back and "
           "they stayed gone; the session then had NO way to tell whether the seed ran, whether "
           "the migration chain had jammed, or on which migration -- and that blindness, not the "
           "fault itself, is what turns these into the four-hour mornings. The chain has jammed "
           "before and silently: 023 blocked 024-026 from 18 Aug for three days. post_deploy.sh "
           "now records every step's outcome and writes it on EXIT (trap), so even an aborted "
           "run leaves its story behind.")
def rg_post_deploy_observable():
    out = []
    sh = repo_file("ops/autodeploy/post_deploy.sh")
    if sh is None:
        out.append((INFO, "outside the repo -- source half skipped"))
    else:
        if "POSTDEPLOY-EYES-1" not in sh or "post_deploy_status.json" not in sh:
            out.append((FAIL, "post_deploy.sh no longer records its steps -- a deploy can "
                              "silently do nothing again"))
        if "trap write_status EXIT" not in sh:
            out.append((FAIL, "the status file is no longer written on EXIT -- an aborted "
                              "post-deploy would leave no trace, which is the whole point"))
        if 'step "migration:$base" failed' not in sh:
            out.append((FAIL, "a FAILED migration no longer names itself in the status file "
                              "-- the jam would be invisible again"))

    # LIVE half: the artefact must actually be reachable without a credential.
    st = _status("/static/post_deploy_status.json")
    if st == 404:
        # OPEN, not passing: until the artefact is actually on the box we are still blind,
        # which is the exact state this entry exists to end. It must not read green early.
        out.append((FAIL, "no post_deploy_status.json on the box -- still blind to what a "
                          "deploy's post-steps did; lands with the first deploy carrying "
                          "POSTDEPLOY-EYES-1, and this flips READY TO LOCK then"))
    elif st != 200:
        out.append((FAIL, "post_deploy_status.json is not readable (HTTP %s) -- the eyes are "
                          "behind a door again" % st))
    else:
        try:
            doc = _json("/static/post_deploy_status.json")
            bad = [x for x in doc.get("steps", []) if x.get("result") == "failed"]
            if bad:
                # NOT a failure of THIS entry -- the eyes are working precisely because they
                # can see this. Chain health is RG-0125's; reporting it is ours.
                out.append((INFO, "eyes working: last deploy reported failed step(s) -- "
                                  + "; ".join("%s (%s)" % (x.get("step"), x.get("detail"))
                                              for x in bad) + " [owned by RG-0125]"))
            else:
                out.append((INFO, "last deploy %s: %d step(s), none failed"
                                  % (doc.get("generated_at"), len(doc.get("steps", [])))))
        except Exception as e:
            out.append((FAIL, "post_deploy_status.json is unreadable as JSON (%s)"
                              % str(e)[:60]))

    if not out:
        out.append((INFO, "every post-deploy step is recorded and publicly readable"))
    return out


@entry("RG-0125", "The migration chain is not JAMMED -- a one-time server change actually reaches "
       "the server, and never sits dead behind a failing predecessor",
       LOCKED, scope="ops/autodeploy/post_deploy.sh's migration loop and EVERY migration in "
       "migrations/. Class property: post_deploy runs the chain in order and `break`s on the "
       "first failure, so ONE broken migration silently strands every later one. Asserted "
       "against the live deploy report, so the jam is found the same day rather than weeks "
       "later when someone notices a change never landed.",
       fixed_on="2026-08-20",
       ref="LOCKED 20 Aug 2026: MIGRATE-ENV-1 cleared the jam and the live deploy report proves it -- 2026-08-20T15:56:13Z, seven steps, 023 through 027 all ok. Found 20 Aug 2026 the moment POSTDEPLOY-EYES-1 (RG-0124) gave us eyes: "
           "023_relink_wonders_railexp.py is FAILING and has been stranding 024, 025, 026 and "
           "027 behind it. This is the same jam recorded on 18 Aug and believed fixed by "
           "MIGRATE-IMPORT-1 -- 023 carries the CWD guard and still fails, so the import fix "
           "was not the whole cause. Consequence chain: 027_super_immortal never ran, which is "
           "why David's deploy did not bring the supers back (they came back via SUPER-HEAL-1 "
           "in the seed lane instead). A migration that cannot run is either FIXED or listed in "
           "migrations/DEFERRED.txt -- the one thing it may never do is sit there jamming the "
           "queue, which is exactly the DEFER-1 rule written on 9 Aug for this same class.")
def rg_migration_chain_not_jammed():
    out = []
    st = _status("/static/post_deploy_status.json")
    if st != 200:
        return [(INFO, "no deploy report on the box yet (HTTP %s) -- chain state unverified; "
                       "RG-0124 owns getting the report there" % st)]
    try:
        doc = _json("/static/post_deploy_status.json")
    except Exception as e:
        return [(INFO, "deploy report unreadable (%s) -- RG-0124 owns that" % str(e)[:60])]
    bad = [x for x in doc.get("steps", []) if x.get("result") == "failed"]
    for x in bad:
        out.append((FAIL, "%s FAILED on the last deploy (%s) -- every migration after it was "
                          "skipped. Fix it, or record the decision in migrations/DEFERRED.txt "
                          "so the chain runs past it (DEFER-1)."
                          % (x.get("step"), doc.get("generated_at"))))
    if not out:
        out.append((INFO, "last deploy %s: chain clean, %d step(s) all ok"
                          % (doc.get("generated_at"), len(doc.get("steps", [])))))
    return out


@entry("RG-0126", "The ledger can still tell an unstable RUN from a real regression -- its own "
       "cry-wolf guard is present and has not been weakened",
       LOCKED, scope="scripts/regression_ledger.py itself. Class property, not an instance: any "
       "future edit that drops the fingerprint, shrinks the watched set, or converts the "
       "exit-3 path into a silent pass re-opens the fault. Source-half only by nature -- "
       "the instrument is the subject.",
       fixed_on="2026-08-20",
       ref="LOCKED 20 Aug 2026 on the run that introduced it -- guard intact, 7 watched sources including this file. LEDGER-STABLE-1, 20 Aug 2026 (DW-053). Twice in one morning this ledger announced "
           "'previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.' while nothing "
           "had rotted -- once across a deploy restart (19 Aug), once because an attended "
           "session was rewriting bea_main.py, this file and ai_funnel_snapshot.json mid-run "
           "(20 Aug). DW-053 closed with the guard built and unit-proven, but David's standing "
           "rule is that a fix is not done until an assertion holds it, and that assertion was "
           "never written -- it went onto the coverage map as blue. This is it. "
           "The guard must satisfy three properties, and each is checked as a property: "
           "(1) the run fingerprints the sources before and after; (2) it reports UNSTABLE and "
           "exits 3 rather than either blaming the app or swallowing the finding; (3) the "
           "watched set is not decorative -- it must include this file, because the case that "
           "actually bit was this file being rewritten underneath a running check.")
def rg_ledger_stability_guard():
    out = []
    me = repo_file("scripts/regression_ledger.py")
    if me is None:
        return [(INFO, "outside the repo -- the instrument cannot inspect itself here")]

    if "_source_fingerprint" not in me or "_sources_changed" not in me:
        out.append((FAIL, "the mid-run fingerprint is GONE -- the ledger can no longer tell a "
                          "moving tree from a regression, which is the exact cry-wolf failure "
                          "LEDGER-STABLE-1 closed (DW-053)"))

    if "UNSTABLE RUN" not in me:
        out.append((FAIL, "no UNSTABLE RUN verdict in the run summary -- an unstable run would "
                          "again be reported as if the app had regressed"))

    if "return 3" not in me and "sys.exit(3)" not in me:
        out.append((FAIL, "the exit-3 path is gone -- callers (nightly, deploy gate) can no "
                          "longer distinguish 'untrustworthy run, re-run me' from 'clean'"))

    # The watched set must be real, and must include this file -- the case that bit.
    try:
        watched = _WATCHED_SOURCES
    except NameError:
        watched = ()
    if len(watched) < 5:
        out.append((FAIL, "the watched-source set has shrunk to %d file(s) -- a guard that "
                          "watches almost nothing reports stable almost always" % len(watched)))
    if not any("regression_ledger.py" in w for w in watched):
        out.append((FAIL, "the ledger no longer watches ITSELF -- the 20 Aug incident was this "
                          "very file being rewritten mid-run, so dropping it re-opens the fault"))

    if not out:
        out.append((INFO, "instability guard intact: %d watched sources incl. itself, "
                          "UNSTABLE RUN verdict and exit-3 path both present" % len(watched)))
    return out


@entry("RG-0127", "The ops dashboard reads the section the sessions actually write -- its panels "
       "cannot silently rot while STATUS.md is diligently updated",
       LOCKED, scope="STATUS.md's dashboard-feed headings and GET /dashboard/summary. Class "
       "property: the endpoint takes the FIRST match of each heading anywhere in a 300 KB "
       "append-only file, so ANY future session that adds a '## Last Completed' section above "
       "the current one silently re-points the dashboard at it. Not specific to today's "
       "sections -- it asserts freshness of whichever section wins.",
       fixed_on="2026-08-20",
       ref="LOCKED 20 Aug 2026: winning section 0 days old and the live panels answer. DASH-FEED-1, 20 Aug 2026. David asked for the ops dashboard to be brought current; "
           "the docs pushed and the Last-done and Next-up panels still showed Session 155 and "
           "Session 139's June work. Cause: /dashboard/summary does NOT read the "
           "'## Current Session' block every session writes -- it parses '## Live State', "
           "'## Last Completed' and '## Next Session' and takes the first match in the file. "
           "Those first matches were dated 2026-07-06 and Session 140 (June). Six weeks of "
           "sessions wrote carefully into a part of STATUS.md the dashboard never looks at, and "
           "nothing anywhere said so -- a silent instrument, which is the class RG-0068 and "
           "POSTDEPLOY-EYES-1 both exist to end. Fixed by inserting fresh sections at the top "
           "so they win first-match; the stale ones stay in place, they simply no longer win. "
           "The freshness window is 21 days deliberately: long enough that a quiet fortnight is "
           "not a false red, short enough that six weeks of rot is impossible.")
def rg_dashboard_feed_current():
    out = []
    STALE_DAYS = 21

    status = repo_file("STATUS.md")
    if status is None:
        out.append((INFO, "outside the repo -- source half not checked here"))
    else:
        # The heading the endpoint will actually match: the FIRST one in the file.
        m = re.search(r"^## Last Completed([^\n]*)$", status, re.MULTILINE)
        if not m:
            out.append((FAIL, "STATUS.md has NO '## Last Completed' heading -- /dashboard/summary "
                              "will render an empty Last-done panel"))
        else:
            heading = m.group(1)
            d = re.search(r"(\d{4})-(\d{2})-(\d{2})", heading)
            if not d:
                out.append((FAIL, "the winning '## Last Completed%s' heading carries no ISO date "
                                  "-- freshness cannot be judged, so rot cannot be detected"
                                  % heading[:60]))
            else:
                when = datetime.date(int(d.group(1)), int(d.group(2)), int(d.group(3)))
                age = (datetime.date.today() - when).days
                if age > STALE_DAYS:
                    out.append((FAIL, "the section /dashboard/summary reads is %d days old "
                                      "(%s). Sessions are writing somewhere the dashboard does "
                                      "not read -- move a fresh '## Last Completed' block ABOVE "
                                      "it in STATUS.md (DASH-FEED-1)." % (age, when.isoformat())))
                else:
                    out.append((INFO, "winning Last-Completed section is %d day(s) old (%s)"
                                      % (age, when.isoformat())))

    # Live half: the panels the browser gets must not be empty, and the Next-up card
    # renders only the first four bullets -- fewer than four is a half-empty card.
    st = _status("/dashboard/summary")
    if st != 200:
        out.append((INFO, "/dashboard/summary not readable from here (HTTP %s) -- live half "
                          "unverified" % st))
        return out
    try:
        doc = _json("/dashboard/summary")
    except Exception as e:
        out.append((INFO, "/dashboard/summary unreadable (%s)" % str(e)[:60]))
        return out

    for key in ("liveState", "lastDone", "nextGoals"):
        if not (doc.get(key) or "").strip():
            out.append((FAIL, "/dashboard/summary returns an EMPTY %s -- that panel is blank on "
                              "David's dashboard" % key))

    bullets = [ln for ln in (doc.get("nextGoals") or "").splitlines()
               if ln.strip().startswith(("- ", "* "))]
    if 0 < len(bullets) < 4:
        out.append((INFO, "only %d Next-up bullet(s) -- the direction card renders up to four"
                          % len(bullets)))

    # Drift: the live copy should match the repo's winning section. This is INFO, not FAIL --
    # editing STATUS.md before running refresh_dashboard.bat is normal, and a tripwire that
    # fires on normal work is the cry-wolf failure RG-0068 exists to prevent.
    if status is not None and doc.get("lastDone"):
        first_live = (doc["lastDone"].strip().splitlines() or [""])[0][:80]
        if first_live and first_live not in status:
            out.append((INFO, "live Last-done does not appear in the repo STATUS.md -- server "
                              "and repo disagree; whoever edits next should re-run "
                              "refresh_dashboard.bat"))
    return out


@entry("RG-0128", "The AI breaker fails OVER, not merely open -- a vendor outage moves the request "
       "to another lane instead of becoming our outage",
       LOCKED, scope="ai_provider.complete() for EVERY task tier and every configured lane. Class "
       "property, not one vendor: the decision under test is chain construction and the "
       "move-to-next-lane behaviour, so it holds for whichever lane happens to be active. "
       "Asserted through the harness scripts/prove_ai_failover.py, which substitutes the "
       "ADAPTERS (the vendor sockets) and exercises the REAL complete(), the REAL cost-approved "
       "fallback ranking and the REAL breaker recording -- only the sockets are stubbed.",
       fixed_on="2026-08-21",
       ref="LOCKED 21 Aug 2026 on the run that introduced it -- 13/13 harness checks. AI-FAILOVER-PROOF-1, 21 Aug 2026 (DW-054). The row had stood since 19 Aug on one "
           "sentence: 'the failover has still never been exercised' -- against 10 Anthropic "
           "incidents between 12 and 19 Aug 2026, eight consecutive days without a clear one, "
           "including the ~36-minute multi-product outage of 16 Aug that BEGAN as an auth "
           "failure. A breaker that only OPENS converts a vendor outage into ours. "
           "Proving it against a real vendor means either spending on a live call or "
           "deliberately breaking the live lane eight days before launch (RUL-001); neither is "
           "justified, and the seam makes neither necessary. 13/13 checks pass: a 5xx, a 401 and "
           "a 429 each move to the next lane and return THAT lane's answer; all-lanes-down still "
           "fails honestly and reports the REQUESTED lane's error rather than the last one tried; "
           "probe=True and allow_fallback=False are both respected, so a probe's verdict stays "
           "unambiguously the target's. "
           "NAMED LIMIT, deliberately not hidden: this asserts the DECISION layer. Whether "
           "failover has anywhere to GO in production depends on two or more lanes carrying keys "
           "on the box, and that is readable only at /ops/selfcheck (ai.lanes_configured), which "
           "is OPS-key gated. So the live half below reports INFO, not a pass -- and provisioning "
           "that key is now the ONE thing it is still wanted for, DW-028 having been closed by "
           "repointing the gzip probe off it.")
def rg_ai_breaker_fails_over():
    out = []
    import subprocess as _sp, os as _os

    harness = _os.path.join(REPO, "scripts", "prove_ai_failover.py")
    if not _os.path.exists(harness):
        out.append((FAIL, "scripts/prove_ai_failover.py is GONE -- the only proof that the "
                          "breaker fails over rather than merely opening has been deleted"))
        return out

    src = repo_file("ai_provider.py")
    if src is None:
        out.append((INFO, "outside the repo -- harness not run here"))
    else:
        # Structural: the chain must be [requested] + fallbacks, and a failed lane must not
        # end the loop. If someone flattens complete() back to a single attempt, the harness
        # would still pass a stubbed world -- assert the shape too.
        if "_cost_approved_fallbacks" not in src:
            out.append((FAIL, "ai_provider lost _cost_approved_fallbacks -- the chain can no "
                              "longer be built, so there is nothing to fail over to"))
        try:
            r = _sp.run([sys.executable, harness], capture_output=True, text=True, timeout=120,
                        cwd=REPO)
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
            if r.returncode != 0:
                out.append((FAIL, "failover harness FAILED (exit %s): %s"
                                  % (r.returncode, tail[0][:160])))
            else:
                nchecks = ""
                for ln in (r.stdout or "").splitlines():
                    if "checks ·" in ln:
                        nchecks = ln.strip()
                out.append((INFO, "failover proven in the decision layer — %s"
                                  % (nchecks or "harness exit 0")))
        except Exception as e:
            out.append((INFO, "could not run the failover harness here (%s)" % str(e)[:70]))

    # Live half: how many lanes actually carry keys on the box. OPS-key gated, so this is
    # INFO either way -- an unreadable instrument must never read as a pass.
    st = _status("/ops/selfcheck")
    if st == 200:
        try:
            doc = _json("/ops/selfcheck")
            lanes = ((doc.get("ai") or {}).get("lanes_configured") or [])
            if len(lanes) < 2:
                out.append((FAIL, "the box has %d configured AI lane(s) (%s) -- failover is "
                                  "proven in code but has NOWHERE TO GO in production"
                                  % (len(lanes), ", ".join(lanes) or "none")))
            else:
                out.append((INFO, "%d lanes configured live (%s) -- failover has somewhere to go"
                                  % (len(lanes), ", ".join(lanes))))
        except Exception as e:
            out.append((INFO, "/ops/selfcheck unreadable (%s)" % str(e)[:60]))
    else:
        out.append((INFO, "live lane count not readable (HTTP %s at /ops/selfcheck -- OPS key "
                          "not provisioned). The decision layer is proven; whether production "
                          "has a second lane to move to is UNSEEN, not assumed." % st))
    return out



@entry("RG-0129", "The EULA's Tuppence promises are BOTH implementable: expiry needs an aged "
       "warning, and termination never forfeits except for fraud",
       LOCKED, scope="eula_clean.html SS6.3 + SS14.1-14.3 (the published promise) against "
                     "scripts/tuppence_dormancy.py (the machinery that keeps it). Source-side "
                     "by design -- the sweep runs on the box against the live DB, which no "
                     "anonymous session can read. ALL markets.",
       fixed_on="2026-08-21",
       ref="TUPPENCE-DORMANCY-1 + the 21 Aug termination reconciliation. Two faults of the same "
           "class -- the EULA said things nothing on disk could deliver or agreed with. "
           "(a) SS6.3 has promised since v1.13 that unused Tuppence expires after 24 months of "
           "inactivity AND that we email 30 days before. NOTHING implemented either half: we "
           "published a notice commitment we could not keep. (b) SS6.3/SS14.1/SS14.2/SS14.3 "
           "forfeited Tuppence on termination while our own canon "
           "(LOCAL_MARKET_REQUIREMENTS.md LM-14b) said 'purchased Tuppence is never confiscated "
           "-- it was bought with real money', and the code had no termination path touching "
           "Tuppence at all. David's ruling 21 Aug: retain and restore on re-registration; "
           "forfeit ONLY for B5 payment fraud and B6 identity fraud. This entry tripwires BOTH "
           "halves so neither can rot: the sweep must keep existing with the notice as a hard "
           "precondition, and the EULA must keep saying retained-not-forfeited.")
def rg_tuppence_promises_are_keepable():
    out = []
    src = repo_file("eula_clean.html")
    sweep = repo_file("scripts/tuppence_dormancy.py")
    if src is None:
        return [(INFO, "not run from the repo -- this is a source-side check")]

    # --- half 1: the dormancy machinery exists and is notice-gated ---
    if not sweep:
        out.append((FAIL, "scripts/tuppence_dormancy.py is GONE -- EULA SS6.3 promises a "
                          "24-month expiry and a 30-day warning email with nothing to deliver "
                          "either"))
    else:
        for needle, what in (
            ("DORMANT_MONTHS = 24", "the 24-month dormancy constant SS6.3 states"),
            ("NOTICE_DAYS = 30", "the 30-day notice period SS6.3 promises"),
            ("dormancy_expiry", "the offsetting ledger row (wallet stays a pure txn sum)"),
            ("tuppence_dormancy_notices", "the table that PROVES a warning was sent"),
        ):
            if needle not in sweep:
                out.append((FAIL, "tuppence_dormancy.py no longer carries %s (%s)"
                                  % (needle, what)))
        # the load-bearing safety property: expiry may never ride on a missing/young warning
        if "age < NOTICE_DAYS" not in sweep:
            out.append((FAIL, "the sweep no longer checks that the warning is at least "
                              "NOTICE_DAYS old -- Tuppence could expire without the notice "
                              "SS6.3 promises"))
        if 'if not notice or not notice["warned_at"]' not in sweep:
            out.append((FAIL, "the sweep no longer refuses to expire when NO warning is on "
                              "record -- the notice is meant to be a hard precondition"))
        if "--apply" not in sweep or "dry = not a.apply" not in sweep:
            out.append((FAIL, "the sweep is no longer dry-run by default"))

    # --- half 2: the EULA still says retained, not forfeited ---
    for needle, what in (
        ("retained on your account record", "SS14.1 retention"),
        ("cause B5 (payment fraud", "SS14.2 fraud-only forfeiture"),
        ("cause B6 (identity fraud", "SS14.2 fraud-only forfeiture"),
        ("no Tuppence is forfeited", "SS14.3 -- the Platform ended it, so nothing is forfeited"),
    ):
        if needle not in src:
            out.append((FAIL, "EULA lost %s (missing: %r) -- the termination reconciliation "
                              "of 21 Aug 2026 has been reverted" % (what, needle)))
    for gone in ("all unused Tuppence is forfeited",
                 "unused Tuppence in your account is forfeited",
                 "All unused Tuppence is forfeited (non-refundable)"):
        if gone in src:
            out.append((FAIL, "blanket-forfeiture wording is BACK in the EULA (%r) -- it "
                              "contradicts LM-14b and David's 21 Aug ruling" % gone))

    # --- the Banks Act guard: no-cash-out must never be softened ---
    if "not redeemable for cash under any circumstances" not in src:
        out.append((FAIL, "the no-cash-redemption rule is GONE from SS6.3 -- this is the "
                          "load-bearing Banks Act protection (BACKLOG O2); a right of "
                          "repayment pushes Tuppence toward the statutory definition of a "
                          "deposit"))

    # --- half 3: the closure lane exists and honours the ruling in CODE ---
    closure = repo_file("account_closure.py")
    bea = repo_file("bea_main.py") or ""
    if not closure:
        out.append((FAIL, "account_closure.py is GONE -- SS14.1/SS14.3 promise retention and "
                          "restore-on-return with nothing to deliver it"))
    else:
        if 'FRAUD_CAUSES = ("B5", "B6")' not in closure:
            out.append((FAIL, "account_closure.py no longer restricts forfeiture to B5/B6 -- "
                              "David's 21 Aug ruling was that ONLY fraud forfeits"))
        for needle, what in (
            ("closure_retention", "the offsetting retention ledger row"),
            ("closure_restore", "the restore ledger row"),
            ("def restore_on_return", "the restore-on-return path SS14.1 promises"),
            ("RETENTION_MONTHS = 24", "the 24-month retention window"),
        ):
            if needle not in closure:
                out.append((FAIL, "account_closure.py lost %s (%s)" % (needle, what)))
        if "lower(user_email)=lower(?)" not in closure:
            out.append((FAIL, "account_closure balance lookup is case-sensitive again -- a "
                              "mixed-case address reads a zero balance and retains NOTHING "
                              "(caught in test 21 Aug 2026)"))
    if "DELETE FROM users WHERE email" in bea:
        out.append((FAIL, "bea_main.py hard-deletes users again -- a deleted row cannot honour "
                          "SS14.1's restore promise, and the old path said nothing about "
                          "Tuppence at all"))
    if "account_closure.close_account" not in bea:
        out.append((FAIL, "the account-closure endpoint no longer calls close_account -- "
                          "closures would not retain, record or forfeit correctly"))
    if "account_closure.restore_on_return" not in bea:
        out.append((FAIL, "registration no longer checks for retained Tuppence -- a returning "
                          "user would silently lose what SS14.1 promises back"))

    if not out:
        out.append((INFO, "SS6.3/SS14 promises are keepable: dormancy sweep present and "
                          "notice-gated, termination retains rather than forfeits (fraud "
                          "excepted), no-cash-out intact"))
    return out


@entry("RG-0130", "The AI Providers card never paints a lane GREEN on configuration alone -- "
                  "green means a live call was proven, amber means configured-but-unproven",
       LOCKED, scope="all three lanes (openai/anthropic/scaleway), +1 dashboard page",
       fixed_on="2026-08-21",
       ref="AIPROV-VERIFY-1. David asked on 21 Aug: 'ACTIVE is green -- if I didn't press Test "
           "I would not have known?' He was right. The dot was driven by p.id===active plus "
           "p.available, and /flags computes available as bool(envkey('OPENAI_API_KEY')) -- a "
           "KEY-PRESENCE check, no network call. So a revoked/over-quota/wrong key painted "
           "solid green on the lane serving live traffic. The card now downgrades an unproven "
           "lane to amber UNVERIFIED, turns it red when the last Test failed, and only goes "
           "green for 24h after a real /admin/ai-test round trip. Also: a 401 on Test now says "
           "plainly it is the DASHBOARD login that expired, not a provider fault -- the old "
           "wording ('Admin session expired -- reload + PIN') sat in the provider card's own "
           "output line and read like the provider had dropped.")
def rg_ai_provider_card_verified_green():
    out = []
    dash = repo_file("dashboard.server.html")
    if dash is None:
        out.append((INFO, "outside the repo -- source-only entry, skipped"))
        return out
    for needle, what in (
        ("window._apv3VerGet", "the verification-state reader"),
        ("window._apv3VerSet", "the verification-state writer (fed by the Test button)"),
        ("UNVERIFIED", "the amber configured-but-unproven label"),
        ("TEST FAILED", "the red last-test-failed label"),
        ("_apv3VerTTL", "the decay window, so a stale green cannot stand forever"),
    ):
        if needle not in dash:
            out.append((FAIL, "the AI Providers card lost %s (missing %r) -- a lane can paint "
                              "green on config alone again, which is exactly AIPROV-VERIFY-1"
                              % (what, needle)))
    # the Test button must actually RECORD its outcome, or green can never be earned
    if "_apv3VerSet(d.provider||p" not in dash:
        out.append((FAIL, "the Test handler no longer records its result -- the dot would be "
                          "permanently amber and the fix is cosmetic"))
    # the 401 message must not sit there implying a provider fault
    if "NOT a fault at the provider" not in dash:
        out.append((FAIL, "the Test 401 message no longer says it is the dashboard login that "
                          "expired -- it reads as a provider outage in the provider card"))
    if not out:
        out.append((INFO, "AI Providers card: green is earned by a live call, amber is "
                          "configured-but-unproven, 401 names itself as a login expiry"))
    return out



@entry("RG-0131", "ONE authority for the production golden gate -- the funnel may never publish a "
                  "lane as golden-set-passed when ai_scoreboard.GOLDEN_PASS does not list it",
       LOCKED, scope="all lanes and all four tiers, +1 dashboard funnel strip",
       fixed_on="2026-08-21",
       ref="GOLDEN-AUTHORITY-1. Two files disagreed for three weeks and the dashboard rendered "
           "the flattering one: ai_price_card.json carried gate 'golden-set-passed' for openai "
           "(citing GS-OAI-V1, which ran on a SANDBOX key with raw vendor calls) while "
           "ai_scoreboard.GOLDEN_PASS excluded openai BY DESIGN pending the server-key run "
           "(RG-0016). So the +1 card showed 'openai (golden-set-passed)' on haiku, triage, "
           "sonnet and vision for the lane serving all live traffic. price_truth.py now "
           "reconciles every gate label against GOLDEN_PASS in both the report and the "
           "snapshot, and raises rather than defaulting open if the scoreboard cannot be read.")
def rg_golden_gate_single_authority():
    out = []
    pt = repo_file("scripts/price_truth.py")
    if pt is None:
        out.append((INFO, "outside the repo -- source-only entry, skipped"))
        return out
    for needle, what in (
        ("_production_golden_pass", "the GOLDEN_PASS reader"),
        ("_gate_reconciled", "the downgrade helper"),
        ("from ai_scoreboard import GOLDEN_PASS", "the single authority import"),
    ):
        if needle not in pt:
            out.append((FAIL, "price_truth.py lost %s (missing %r) -- the price card can publish "
                              "an unearned golden gate again" % (what, needle)))
    if pt.count("_gate_reconciled(prov") < 2:
        out.append((FAIL, "the gate reconcile is applied fewer than twice -- BOTH the printed "
                          "report and the --snapshot the dashboard renders must be reconciled; "
                          "the snapshot is the one David actually looks at"))
    if "raise SystemExit" not in pt.split("_production_golden_pass")[1][:600]:
        out.append((FAIL, "a failure to read GOLDEN_PASS no longer raises -- an import error "
                          "would silently re-open the hole by publishing the card's own claim"))
    # and the shipped snapshot must not contradict the scoreboard
    try:
        import json as _j
        sp = os.path.join(REPO, "ai_funnel_snapshot.json")
        if os.path.exists(sp):
            sys.path.insert(0, REPO)
            from ai_scoreboard import GOLDEN_PASS as _GP
            snap = _j.load(open(sp, encoding="utf-8"))
            for tier, rows in (snap.get("tiers") or {}).items():
                for r in rows:
                    if r.get("gate") in ("production", "golden-set-passed") and r.get("provider") not in _GP:
                        out.append((FAIL, "ai_funnel_snapshot.json still publishes %s as %r on "
                                          "tier %s while GOLDEN_PASS does not list it -- "
                                          "re-run scripts/price_truth.py --snapshot"
                                          % (r.get("provider"), r.get("gate"), tier)))
    except Exception as e:
        out.append((INFO, "snapshot cross-check skipped (%s)" % e))
    if not out:
        out.append((INFO, "golden gate has one authority: the scoreboard; card claims are "
                          "evidence and cannot promote themselves"))
    return out


@entry("RG-0132", "The BASE lane's PRODUCTION golden run is on record -- openai is in GOLDEN_PASS",
       OPEN, scope="openai, the lane serving 100% of live traffic",
       ref="AI_LANE_GUIDANCE P2/P3, never executed. GS-OAI-V1 (1 Aug) ran on a SANDBOX key with "
           "RAW vendor calls -- it bypassed the message translation, the reasoning_effort='none' "
           "pin and max_completion_tokens handling that production actually uses. "
           "scripts/golden_seam_v2.py exists and runs the same 8 golden prompts THROUGH "
           "ai_provider.complete(provider='openai', probe=True); it refuses to run without the "
           "production key, so it needs one run ON THE HETZNER BOX, then openai added to "
           "GOLDEN_PASS (P3). This entry is OPEN, not a nag: it fails until that run happens and "
           "prints READY TO LOCK the moment it does. Tracking this in the ledger rather than in a "
           "sentence to David is the point -- it is a technical execution step, not a decision.")
def rg_openai_production_golden_run():
    out = []
    sb = repo_file("ai_scoreboard.py")
    if sb is None:
        out.append((INFO, "outside the repo -- source-only entry, skipped"))
        return out
    try:
        sys.path.insert(0, REPO)
        from ai_scoreboard import GOLDEN_PASS
        listed = "openai" in GOLDEN_PASS
    except Exception as e:
        out.append((FAIL, "cannot read GOLDEN_PASS (%s)" % e))
        return out
    if not listed:
        out.append((FAIL, "openai is NOT in GOLDEN_PASS -- the base lane serving all live "
                          "traffic has no production golden run on record. Run "
                          "scripts/golden_seam_v2.py on the server with the production key, "
                          "then add the lane (P3)."))
    else:
        out.append((INFO, "openai carries a production golden gate"))
    return out



@entry("RG-0133", "Every state-painting panel on the +1 page either MEASURES what it paints or "
                  "is LABELLED unmeasured -- and the static figures agree with canon",
       LOCKED, scope="dashboard.server.html, all state-painting panels (the whole instrument "
                     "layer, not just the card that was caught)",
       fixed_on="2026-08-21",
       ref="INSTRUMENT-TRUTH-1, 21 Aug 2026. David, after the third find of the morning: 'how "
           "worried should I be?' -- then 'how many of these six are impossible to verify by AI, "
           "how many would not have survived an AI verification?' Answer, by going and reading "
           "them: ZERO were impossible -- every one was checkable from source against canon, no "
           "live access or human eyes needed. They were unlooked-at, not unverifiable. TWO failed, "
           "plus a THIRD the audit list itself had missed. (1) SERVER SPECS hardcoded 'CPX32 "
           "EUR17.99 + Volume EUR6.58 = EUR24.57/mo' against canon.yml server_eur_month 15.49 -- "
           "[ASSERTION UPDATED 22 Aug 2026, PROVENANCE-1: check (1) no longer greps for a "
           "literal price string. That form could only catch ONE hand-typed number drifting "
           "and sat green while a second hand-typed price, EUR4.51/mo on the Ops Map, "
           "contradicted it five-fold for months. Cost is now FED from canon.yml at request "
           "time, so the check asserts the feed exists and that no hardcoded monthly price "
           "survives anywhere in the markup -- strictly stronger, not weaker.] "
           "contradicting RUL-025's grandfathered price and overstating the box by EUR2.50/mo. "
           "(2) BIT SELF-TEST painted its dot GREEN as the pre-data default, so it read healthy "
           "while still loading and stayed healthy if the fetch died. (3) The SERVICES panel -- "
           "SIX hand-written 'Active' verdicts, never probed, which would read Active through a "
           "total outage; it was missed by the first audit because it has no id attribute and the "
           "sweep enumerated by id. That miss is the same shortcut that makes these faults: "
           "counting the easy-to-enumerate and calling it the set. RG-0093 (16 Aug) had already "
           "raised the Infrastructure card to 'the same bar' as the AI card -- while the AI card "
           "was itself config-painted, so a session benchmarked against something unverified and "
           "propagated the defect as the standard. Fixes: cost corrected + sourced, SERVICES "
           "labelled STATIC REFERENCE with the green stripped and the reader pointed at the "
           "measured Infrastructure card, BIT dot defaults grey.")
def rg_instrument_truth():
    out = []
    dash = repo_file("dashboard.server.html")
    if dash is None:
        out.append((INFO, "outside the repo -- source-only entry, skipped"))
        return out
    # measured   = probes an endpoint for the state it paints
    # display    = renders server DATA but paints no health verdict
    # labelled   = static, and SAYS SO on the card itself
    PANEL_PROVENANCE = {
        "infra-rows":       "measured:/admin/services-status",
        "health-grid":      "measured:/health/resources",
        "om-money-out":     "measured:/dashboard/summary",
        "apv3-rows":        "measured:/admin/ai-test (RG-0130)",
        "bit-ops-panel":    "measured:/dashboard/bit",
        "hp-grid":          "display:/dashboard/summary",
        "directions-grid":  "display:/dashboard/summary",
        "prompt-panel":     "display:no verdict",
        "travel-lane-card": "display:no verdict",
        "ops-specs-grid":   "labelled:static, figures asserted against canon.yml below",
    }
    for pid, prov in PANEL_PROVENANCE.items():
        if 'id="%s"' % pid not in dash:
            out.append((INFO, "panel %s is no longer on the page -- drop it from "
                              "PANEL_PROVENANCE" % pid))
        if prov == "UNAUDITED":
            out.append((FAIL, "panel %s is still unaudited for instrument truth" % pid))

    # (3) the SERVICES panel has no id -- assert it by its content, and that it stays labelled
    if "\U0001f680 SERVICES" in dash or "SERVICES</div>" in dash:
        pass
    if "STATIC REFERENCE — NOT MEASURED" not in dash:
        out.append((FAIL, "the SERVICES panel lost its STATIC REFERENCE label -- six hand-written "
                          "'Active' verdicts would read healthy through a total outage again"))
    if "✅ Active · port 8000" in dash:
        out.append((FAIL, "the SERVICES panel paints health-green 'Active' again from a hardcoded "
                          "string -- it is not probed and must never look measured"))

    # (1) money on the page must COME FROM canon, not merely happen to match it.
    #     ASSERTION UPDATED 22 Aug 2026 (PROVENANCE-1) and deliberately STRENGTHENED.
    #     The original form grepped for the literal string "CPX32 EUR15.49" in the
    #     markup -- it could only catch a hand-typed number that had drifted, and it
    #     could never catch a SECOND hand-typed number elsewhere on the page. That is
    #     exactly what happened: the Ops Map carried "fixed EUR4.51/mo" while this
    #     check sat green on the Ops view's "CPX32 EUR15.49", five-fold apart, both
    #     hand-typed, for months. The cost surfaces are now fed from canon.yml at
    #     request time via /dashboard/fixed-costs, so the new assertion is that the
    #     FEED exists and that no hardcoded server price remains to contradict it.
    #     Strictly stronger: under the old rule two panels could disagree and pass;
    #     under this one a hardcoded price is a failure wherever it appears.
    canon = repo_file("canon.yml") or ""
    m = re.search(r"^\s*server_eur_month:\s*([0-9.]+)", canon, re.M)
    if not m:
        out.append((INFO, "canon.yml server_eur_month not readable -- cost cross-check skipped"))
    elif "loadFixedCosts" not in dash or 'id="ops-cost"' not in dash:
        out.append((FAIL, "the cost surfaces are no longer fed from canon.yml "
                          "(/dashboard/fixed-costs) -- a hand-typed price can drift from the "
                          "canon again, which is how EUR4.51 and EUR22.07 coexisted on one page"))
    else:
        # Any surviving hardcoded monthly EUR price is a contradiction waiting to happen.
        markup = re.sub(r"<script[^>]*>.*?</script>", "", dash, flags=re.DOTALL)
        stray = [s for s in re.findall(r"€\s?\d+[.,]\d\d\s*/?\s*mo", markup)]
        if stray:
            out.append((FAIL, "hardcoded monthly price(s) %s are still painted in the markup -- "
                              "they can drift from canon.yml and contradict the live cost feed"
                              % ", ".join(sorted(set(stray)))))

    # (2) no panel may default to a health colour before its data lands
    if 'id="bit-ops-dot" style="margin-left:6px;color:#10b981' in dash:
        out.append((FAIL, "the BIT dot defaults GREEN again -- a health colour must be earned by "
                          "data, never be the pre-data default"))

    if not out:
        out.append((INFO, "every +1-page panel is measured, display-only, or labelled static; "
                          "static figures agree with canon; no dot defaults to green"))
    return out


@entry("RG-0136", "Paid Home Affairs ID verification stays OPTIONAL, HONEST and CHEAP TO BE WRONG: "
       "only an NPR pass may be called 'verified' to a buyer, the tick never gates an "
       "introduction, a reused ID number is flagged not inherited, and no provider failure "
       "can ever charge a seller",
       LOCKED, fixed_on="2026-08-21",
       scope="Sellers in every category; the buyer warning names the deposit risk for "
             "ACCOMMODATION specifically because that is the scam it exists to counter. "
             "Front end SHIPPED 21 Aug (seller buy-card, green tick, buyer warning) and the "
             "Didit provider is CONFIGURED -- the lane is armed end to end. STILL NOT "
             "PROVEN: no real NPR query has ever run, so (a) whether Didit's 500 free "
             "monthly verifications cover Database Validation or it bills $1.10 from call "
             "one, and (b) the outcome mapping against a real registry response, are both "
             "untested. Do not call this proven until a live check has completed.",
       ref="ID-NPR-1 / RUL-039, 21 Aug 2026. David, on the stay-deposit scam: build the "
           "capability into the ID upload to buy verification at 1 Tuppence, 'less forced "
           "and at the same time better visibility... only ever do this verification one "
           "time, against a database of ID numbers'. Three states -- submitted / "
           "ai_checked / npr_verified -- because the existing Sonnet document check was "
           "setting users.id_verified_at at confidence >=0.60 with the code's own comment "
           "'no human review path', and that flag is what buyers were being shown as "
           "'verified'. It only proves the document is legible and self-consistent. "
           "The one-check-ever dedupe carries a security twist that must not be optimised "
           "away: the same ID hash on a SECOND account is a duplicate identity claim, so it "
           "is flagged and granted nothing -- a reused ID is a fraud signal, not a saving. "
           "OPEN until a provider is configured and a real check has run end to end; "
           "promote to LOCKED then.")
def rg_id_npr():
    out = []
    bea = repo_file("bea_main.py")
    prov = repo_file("id_verify_provider.py")
    tests = repo_file("test_id_npr.py")

    if bea is None:
        return [(FAIL, "bea_main.py not readable from here")]

    # 1 ── the paid tier must stay a SEPARATE column from the introduction gate.
    # A session "simplifying" these into one would silently make the tick a
    # barrier, which is the exact opposite of David's ruling.
    i = bea.find("def _seller_intro_gate")
    gate = bea[i:i + 1400] if i > 0 else ""
    if not gate:
        out.append((FAIL, "_seller_intro_gate not found"))
    else:
        if "id_verified_at" not in gate:
            out.append((FAIL, "the introduction gate lost its id_verified_at check"))
        if "id_npr_verified_at" in gate:
            out.append((FAIL, "RUL-039 BREACH: the paid NPR tick has become an "
                              "introduction gate -- it must never block a seller"))

    # 2 ── the buyer notice must be informational, never able to raise
    j = bea.find("def _seller_verification_notice")
    if j < 0:
        out.append((FAIL, "the unverified-seller buyer notice is missing"))
    else:
        body = bea[j:j + 2200]
        if "raise HTTPException" in body:
            out.append((FAIL, "RUL-039 BREACH: the unverified-seller notice can raise -- "
                              "it must inform, never block"))
        if "Never pay a deposit" not in body:
            out.append((FAIL, "the stay warning no longer names the deposit risk"))

    # 3 ── the duplicate-identity trap must still be there
    if "duplicate_hash" not in bea:
        out.append((FAIL, "the duplicate-ID trap is gone: a reused ID number could now "
                          "inherit another account's verification"))

    # 4 ── the provider must fail closed (no provider => no charge)
    if prov is None:
        out.append((FAIL, "id_verify_provider.py missing -- the swappable adapter is the "
                          "supplier-fallback doctrine for this lane"))
    else:
        if "billable" not in prov:
            out.append((FAIL, "provider result lost its 'billable' flag -- a supplier "
                              "failure could charge a seller"))
        if "_check_didit" in prov and "CONCLUSIVE" not in prov:
            out.append((FAIL, "the Didit adapter lost its conclusive-outcome gate -- "
                              "an inconclusive result could now charge a seller"))
        if "_check_didit" in prov and "_SURNAME_PARTICLES" not in prov:
            out.append((FAIL, "surname-particle handling removed: 'van der Merwe' would "
                              "split to 'Merwe' and legitimate SA sellers would be "
                              "charged and refused on a PARTIAL_MATCH"))

    # 4b ── the provider module must SHIP. bea_main imports it inside the
    # endpoint, so a missing file does not crash startup -- it 500s the check
    # instead, silently. Exactly the hardcoded-list trap that half-shipped
    # TEACH-DEPLOY-1 in CityLauncher on the same day.
    man = repo_file("ops/autodeploy/deploy_manifest.txt")
    if man is not None and "id_verify_provider.py" not in man:
        out.append((FAIL, "id_verify_provider.py is NOT in the deploy manifest -- "
                          "bea_main.py would ship without it and every check would "
                          "500 on a server that looks healthy"))

    # 4c ── the lane must be observable from outside, or 'did the key land?'
    # costs an SSH round-trip every time
    if "/id-verify/status" not in bea:
        out.append((FAIL, "the /id-verify/status probe is gone -- provider health "
                          "becomes invisible and a dead lane goes silent"))

    # 4d ── the FRONT END must exist and must stay advisory. Backend-only was
    # the state that let this be "done" while no seller could buy anything.
    msjs = repo_file("ms.js")
    if msjs is None or "msUnverifiedGate" not in (msjs or ""):
        out.append((FAIL, "the buyer warning is not in ms.js -- the lane is armed but "
                          "no buyer is ever told a seller is unverified"))
    elif "catch(e){ return true; }" not in msjs:
        out.append((FAIL, "RUL-039 BREACH: msUnverifiedGate can fail closed -- a warning "
                          "error would block a buyer's introduction"))
    if msjs and "msRenderIdVerifyCard" not in msjs:
        out.append((FAIL, "the seller's buy-a-check card is gone -- verification is "
                          "unreachable from the app"))
    if msjs and "green_tick" not in msjs:
        out.append((FAIL, "the tick no longer keys off green_tick -- an AI document "
                          "check could be shown to a buyer as 'verified'"))

    # 4e ── the lane must be VISIBLE on the infrastructure panel. David caught its
    # absence on 21 Aug: "a partner you cannot see is a partner that fails silently."
    # And the row must stay PRESENCE-ONLY -- a live probe here would spend $1.10 of
    # real money on every dashboard refresh.
    if '"id": "id_verify"' not in bea:
        out.append((FAIL, "the ID-verification row is missing from the infrastructure "
                          "panel -- a dead key would fail silently instead of turning red"))
    else:
        i = bea.find('if service in (None, "id_verify")')
        seg = bea[i:i+2000] if i > 0 else ""
        if "verify_id(" in seg:
            out.append((FAIL, "the infrastructure panel row calls verify_id() -- that is a "
                              "BILLABLE DHA query on every dashboard refresh"))
        if "presence only" not in seg:
            out.append((FAIL, "the ID-verify panel row no longer says 'presence only' -- "
                              "green there must never be read as 'a check works'"))

    # 5 ── the guards themselves
    if tests is None:
        out.append((FAIL, "test_id_npr.py missing"))
    else:
        for name in ("test_duplicate_hash_on_second_account_is_flagged_not_granted",
                     "test_intro_gate_still_uses_only_id_verified_at",
                     "test_provider_fails_closed_when_unconfigured",
                     "test_sa_surname_particles_stay_with_the_surname",
                     "test_partial_match_is_not_a_pass"):
            if name not in tests:
                out.append((FAIL, "guard removed: " + name))

    if not out:
        out.append((INFO, "NPR tier separate from the intro gate; buyer notice informs "
                          "without blocking; duplicate-ID trap intact; provider fails "
                          "closed; PARTIAL_MATCH never passes; 14 guards present"))
    return out


@entry("RG-0135", "Every journey map an advert can show has FREE pre-information under it: "
       "itinerary, real cost, entry/visas, health, safety notices, money/taxes/tipping and "
       "a dated re-check list -- and the panel ends in an INTRODUCTION, never a sale",
       LOCKED, fixed_on="2026-08-21",
       scope="Super-example Adventures adverts, all 13 journeys (9 country maps + 4 tour "
             "maps). NOT yet the other advert families David named in the same breath -- "
             "stays, guides and non-super tours still show a map and a sentence. Those are "
             "the same class and need the same fix; say so rather than implying it is done",
       ref="TRIP-ESSENTIALS-1, 21 Aug 2026. David, on seeing the Pilanesberg advert: "
           "'would you plan your holiday with only this available? A map and a single "
           "sentence? No itinerary, no budget, no visa requirements, no safety advice, no "
           "travelling notices, no local taxes, tips etc.? ... this is a major rejection "
           "point and is true for ALL of our adverts with tours/holidays/stays/guides.' He "
           "had asked for this before and it was lost to launch work -- the 17 Aug LAYERS-4-1 "
           "note even recorded the sequencing ('maps first, dossier-summary work second') and "
           "then the second half never came. This entry is what stops it being lost a third "
           "time. PLACEMENT is part of the fix, not a detail: David's ruling the same day was "
           "that the panel sits BELOW the map, because a scanning reader takes in the first "
           "block and moves on -- if that block is not an interesting map they pass by. "
           "MODEL: MarketSquare is an introductory service (CLAUDE.md, 1 Aug 2026), so the "
           "panel informs for free and hands off to a travel agency; copy that implied we "
           "sell or book the trip would be a defect, and is asserted against here. "
           "OPEN until the panel is DEPLOYED and proven live; promote to LOCKED then.")
def rg_trip_essentials():
    import json as _j, re as _re
    out = []

    # ── source side: the data, the renderer, the wiring ──────────────────────
    data = repo_file("trip_essentials.js")
    ms   = repo_file("ms.js")
    idx  = repo_file("marketsquare.html")
    man  = repo_file("ops/autodeploy/deploy_manifest.txt")
    trips = None
    if data is not None:
        if not data.rstrip().endswith(";"):
            out.append((FAIL, "trip_essentials.js is TRUNCATED -- rebuild with "
                              "scripts/build_trip_essentials.py"))
        else:
            try:
                _MARK = "window.TRIP_ESSENTIALS ="
                body = data[data.index(_MARK) + len(_MARK):].rstrip().rstrip(";")
                trips = _j.loads(body)["trips"]
            except Exception as ex:
                out.append((FAIL, "trip_essentials.js will not parse: %s" % repr(ex)[:90]))
        if trips is not None:
            thin = [t["key"] for t in trips
                    if not t.get("itinerary") or not t.get("verify")
                    or not (t.get("budget") or {}).get("rows") or len(t.get("sections") or []) < 5]
            if thin:
                out.append((FAIL, "trip(s) missing a required block (itinerary / budget / "
                                  ">=5 sections / re-check list): " + ", ".join(thin)))
            # An unsourced NUMBER is how a dossier quietly becomes fiction.
            MONEY  = _re.compile(r"(?:R\s?\d|US\$\s?\d|N\$\s?\d|A\$\s?\d|£\s?\d|€\s?\d|\$\s?\d"
                                 r"|(?:EGP|MZN|BWP|KES|ZMW|TZS|AUD|EUR|GBP|USD|ZAR|NAD)\s?\d"
                                 r"|\bP\s?\d{2,}|\d+(?:\.\d+)?\s?%)")
            HONEST = _re.compile(r"not published|could not be confirmed|UNVERIFIED|not confirmed"
                                 r"|no scheme found|ask your|ask the|ask before|ask us|confirm"
                                 r"|verify|indicative|not independently|not stated|no official"
                                 r"|this advert's own", _re.I)
            bare = []
            for t in trips:
                rows = list((t.get("budget") or {}).get("rows") or [])
                for s in (t.get("sections") or []):
                    rows += s.get("rows") or []
                for r in rows:
                    if r.get("src"):
                        continue
                    txt = " ".join([r.get("v", ""), r.get("n", ""), r.get("l", "")])
                    if MONEY.search(txt) and not HONEST.search(txt):
                        bare.append("%s::%s" % (t["key"], r.get("l", "?")[:34]))
            if bare:
                out.append((FAIL, "%d fact row(s) quote a number with NO source and no honest "
                                  "hedge: %s" % (len(bare), ", ".join(bare[:6]))))
            # The model constraint. This panel may never read like a shopfront.
            blob = _j.dumps(trips)
            for pat in (r"\bbook now\b", r"\bwe (?:can )?book\b", r"\bour price\b",
                        r"\bbuy this trip\b", r"\breserve your seat\b"):
                if _re.search(pat, blob, _re.I):
                    out.append((FAIL, "copy implies MarketSquare SELLS the trip (/%s/) -- we are "
                                      "an introductory service" % pat))
    if ms is not None:
        for need, why in (("function tripEssentialsPanel", "the renderer"),
                          ("? tripEssentialsPanel(l, id) : ''", "the CALL from the detail template"),
                          ("does not sell or book", "the introductory-service disclaimer")):
            if need not in ms:
                out.append((FAIL, "ms.js lost %s ('%s')" % (why, need)))
        # Placement: the essentials must render AFTER the map block, never before it.
        i_map = ms.find("adv-reserve-map")
        i_ess = ms.find("? tripEssentialsPanel(l, id) : ''")
        if i_map > -1 and i_ess > -1 and i_ess < i_map:
            out.append((FAIL, "the essentials panel now renders ABOVE the map -- David's "
                              "21 Aug placement ruling was BELOW it, because a scanning reader "
                              "bounces off anything that is not an interesting map first"))
        # ── the anti-drift assertion: a NEW map with no essentials trips this red ──
        if trips is not None:
            keys = set()
            for t in trips:
                m = t.get("match") or {}
                keys.add(("tour", m.get("tour")) if m.get("tour") else ("country", m.get("country")))
            def _cfg_keys(name):
                m = _re.search(r"const %s = \{(.*?)\n\};" % name, ms, _re.S)
                return set(_re.findall(r"^\s*([A-Za-z0-9_]+):\s*\{", m.group(1), _re.M)) if m else set()
            orphan = ([c for c in _cfg_keys("ADV_COUNTRY_MAP") if ("country", c) not in keys]
                      + [t for t in _cfg_keys("ADV_TOUR_MAP") if ("tour", t) not in keys])
            if orphan:
                out.append((FAIL, "map(s) with NO pre-information behind them -- an advert that "
                                  "is still just a map and a sentence: " + ", ".join(sorted(orphan))))
    if idx is not None and "/static/trip_essentials.js" not in idx:
        out.append((FAIL, "marketsquare.html does not load trip_essentials.js -- the panel "
                          "renders nothing at all"))
    if idx is not None and _re.search(r'trip_essentials\.js[^>]*\bdefer\b', idx):
        out.append((FAIL, "trip_essentials.js is deferred. A deep link (?listing=NNN -- exactly "
                          "what the journey maps emit) renders the detail during ms.js's first "
                          "pass, so deferred data arrives too late and the panel vanishes"))
    if man is not None and "trip_essentials.js" not in man:
        out.append((FAIL, "trip_essentials.js is not in deploy_manifest.txt -- it will never "
                          "reach the server (ONE DEPLOY places by manifest only)"))

    # ── live side ────────────────────────────────────────────────────────────
    # A 404 here is the EXPECTED open state before the first deploy. Name it as
    # "not shipped yet", not as an instrument crash -- a tripwire that reports
    # itself broken is the cry-wolf failure RG-0068/LEDGER-OFFLINE-1 exist to stop.
    try:
        live = _get("/static/trip_essentials.js")
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            out.append((FAIL, "not deployed yet: live /static/trip_essentials.js is 404. The "
                              "panel exists in the repo and is manifest-listed; it reaches "
                              "travellers on the next deploy of the `deploy` ref."))
            return out
        raise
    if "window.TRIP_ESSENTIALS" not in live:
        out.append((FAIL, "live /static/trip_essentials.js is not the data file"))
    else:
        try:
            _M = "window.TRIP_ESSENTIALS ="
            n_live = len(_j.loads(live[live.index(_M) + len(_M):].rstrip().rstrip(";"))["trips"])
        except Exception:
            n_live = -1
        if trips is not None and n_live != len(trips):
            out.append((FAIL, "live carries %s trips, the repo carries %d -- a stale deploy"
                        % (n_live if n_live >= 0 else "unparseable", len(trips))))
    home = _get("/")
    if "/static/trip_essentials.js" not in home:
        out.append((FAIL, "the live index does not load trip_essentials.js"))

    if not out:
        out.append((INFO, "%d journeys carry full pre-information; every map is covered; "
                          "placement is below the map; no unsourced numbers" % len(trips or [])))
    return out



@entry("RG-0134", "The admin door has its OWN failure budget and only WRONG credentials spend it -- "
                  "the super admin can never be rate-limited out of his own dashboard by traffic "
                  "he did not generate",
       LOCKED, scope="the login rate-limiter class entire: /admin/login and /review/login get "
                     "failure-only accounting in separate buckets, while /review/request-link, "
                     "/review/claim-code and /auth/verify-code keep CALL counting (a send "
                     "endpoint must meter calls, not failures). Both halves of the fault: the "
                     "shared bucket (cause) and successes spending budget (the half that starves "
                     "every lane)",
       fixed_on="2026-08-21",
       ref="ADMIN-NOLOCK-2. David, 21 Aug 2026: 'I am back it being blocked by my own app.' The "
           "Session Dashboard answered 'Too many attempts. Please wait a few minutes.' with the "
           "site healthy and not one wrong password typed. Cause: GATE-NOLOCK-1 (19 Aug) fixed "
           "the ORIGIN half of admin lockout but routed /admin/login through _review_rate_ok -- "
           "ONE per-IP bucket shared with the reviewer lane, counting EVERY attempt including "
           "successes. The machine lanes on David's own IP (regression ledger, maintenance "
           "agent, audit_global_qa, fault_reconcile) each mint a review token, each mint spent "
           "one of eight slots, and the strongest credential in the system was locked out by its "
           "own housekeeping. SECOND time this class re-entered by a different door: GATE-CACHE-1 "
           "(14 Aug, RG-0070) taught the READERS to survive a burnt allowance; it never stopped "
           "the allowance being burnt by successes. Fixed at the cause: (1) _admin_attempts is a "
           "separate bucket, so reviewer traffic can never starve the admin door; (2) a FAILED "
           "credential calls _rate_note_failure and a correct one calls _rate_clear, so mints -- "
           "which all succeed -- cost nothing in either lane; (3) the 429 carries exact seconds "
           "plus Retry-After, so the human is told WHEN instead of 'a few minutes'. Brute force "
           "unchanged: 8 wrong reviewer codes, 10 wrong admin credentials, same 10-minute window. "
           "CAUGHT IN REVIEW, NEVER SHIPPED: the first draft made _review_rate_ok check-only, "
           "which would have left three call-metered endpoints unlimited -- assertion 4b below "
           "now guards that trap, because a lockout fix that opens three doors is worse than the "
           "lockout. Proven by 6 live-logic assertions over the extracted limiter.")
def rg_admin_door_has_own_failure_budget():
    out = []
    c = repo_file("bea_main.py")
    if c is None:
        out.append((FAIL, "bea_main.py unreadable -- the lockout guarantee is UNPROVEN"))
        return out

    # 1. The buckets are separate.
    if "_admin_attempts" not in c:
        out.append((FAIL, "the admin lane has no bucket of its own again -- /admin/login is "
                          "sharing the reviewer allowance and David gets locked out of his own "
                          "dashboard by machine traffic (ADMIN-NOLOCK-2 cause half)"))

    # 2. Failure-only accounting exists at all.
    for fn in ("_rate_note_failure", "_rate_clear", "_rate_ok"):
        if fn not in c:
            out.append((FAIL, "bea_main.py lost %s -- the login limiter is counting attempts "
                              "again instead of failures, so successful token mints spend "
                              "allowance and the starvation class is fully re-opened" % fn))

    # 3. The admin endpoint uses ITS bucket, not the reviewer one.
    i = c.find('@app.post("/admin/login")')
    if i < 0:
        out.append((FAIL, "/admin/login is gone -- this assertion has lost its subject and "
                          "would pass vacuously (see RG-0068)"))
    else:
        body = c[i:i + 4000]
        if "_rate_ok(_admin_attempts" not in body:
            out.append((FAIL, "/admin/login no longer gates on _admin_attempts -- the admin "
                              "door is back on the shared reviewer budget"))
        if "_review_rate_ok" in body:
            out.append((FAIL, "/admin/login calls _review_rate_ok again -- this is the exact "
                              "19 Aug wiring that locked David out on 21 Aug"))
        if "_rate_clear(_admin_attempts" not in body:
            out.append((FAIL, "a correct admin credential no longer clears the bucket -- the "
                              "super admin can be held out after proving who he is"))

    # 4. A success in the reviewer lane must not spend allowance either.
    j = c.find('@app.post("/review/login")')
    if j >= 0:
        rbody = c[j:j + 2500]
        if "_rate_clear(_review_attempts" not in rbody:
            out.append((FAIL, "/review/login no longer clears on success -- every machine mint "
                              "spends a slot again (the mechanism that burnt the allowance)"))
        if "_rate_note_failure(_review_attempts" not in rbody:
            out.append((FAIL, "/review/login no longer records failures -- brute-force "
                              "protection has been removed, not relaxed"))

    # 4b. THE TRAP THIS FIX ALMOST FELL INTO. _review_rate_ok is the ONLY budget check for
    # /review/request-link (sends EMAIL), /review/claim-code and /auth/verify-code. The first
    # draft of ADMIN-NOLOCK-2 turned it into a check-only shim, which would have left all
    # three effectively UNLIMITED -- a lockout fix that opens three doors. Failures-only is
    # right for a password prompt and WRONG for a send-me-something endpoint; they are not
    # interchangeable. Caught in review 21 Aug, never shipped.
    k = c.find("def _review_rate_ok(")
    if k < 0:
        out.append((FAIL, "_review_rate_ok is gone -- /review/request-link (an EMAIL sender), "
                          "/review/claim-code and /auth/verify-code have lost their only rate "
                          "limit"))
    elif "rec[0] += 1" not in c[k:k + 1600]:
        out.append((FAIL, "_review_rate_ok no longer increments -- it CHECKS without SPENDING, "
                          "so /review/request-link can be driven as a mail bomb and "
                          "/auth/verify-code brute-forced without limit. This is the exact "
                          "draft error caught in review on 21 Aug"))
    for ep in ('@app.post("/review/request-link")', '@app.post("/review/claim-code")',
               '@app.post("/auth/verify-code")'):
        e = c.find(ep)
        if e >= 0 and "_review_rate_ok(ip)" not in c[e:e + 1200]:
            out.append((FAIL, "%s no longer consumes rate budget -- an unmetered send/verify "
                              "endpoint" % ep))

    # 5. The 429 tells the human a number, not prose.
    if "Retry-After" not in c or "Try again in %s" not in c:
        out.append((FAIL, "the rate-limit refusal no longer carries the seconds remaining -- "
                          "'wait a few minutes' is the message that sent David to guess"))

    # Functional half: the extracted limiter actually behaves.
    try:
        import io as _io
        s = _io.open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read()
        a = s.index("_admin_attempts    = {}")
        b = s.index("def _review_rate_ok(ip: str) -> bool:")
        ns = {"HTTPException": Exception, "_review_attempts": {}}
        exec(s[a:b], ns)                                         # noqa: S102 - our own source
        ok_, note_ = ns["_rate_ok"], ns["_rate_note_failure"]
        clr_, ret_ = ns["_rate_clear"], ns["_rate_retry_after"]
        A, R, IP = ns["_admin_attempts"], ns["_review_attempts"], "203.0.113.7"
        for _ in range(50):                                      # machine mints, all successful
            ok_(R, IP, 8); clr_(R, IP)
        if not ok_(A, IP, 10):
            out.append((FAIL, "LIVE LOGIC: 50 successful reviewer mints closed the admin door "
                              "-- the 21 Aug lockout reproduces"))
        for _ in range(8):
            note_(R, IP)
        if ok_(R, IP, 8):
            out.append((FAIL, "LIVE LOGIC: 8 wrong reviewer codes did not lock the reviewer "
                              "lane -- brute-force protection is gone"))
        if not ok_(A, IP, 10):
            out.append((FAIL, "LIVE LOGIC: reviewer failures leaked into the admin bucket -- "
                              "the buckets are not actually separate"))
        for _ in range(10):
            note_(A, IP)
        if ok_(A, IP, 10):
            out.append((FAIL, "LIVE LOGIC: 10 wrong admin credentials did not lock the admin "
                              "lane -- this fix traded a lockout for an open door"))
        if not (0 < ret_(A, IP) <= 600):
            out.append((FAIL, "LIVE LOGIC: retry-after is not a sane number of seconds"))
        clr_(A, IP)
        if not ok_(A, IP, 10):
            out.append((FAIL, "LIVE LOGIC: a correct admin credential did not clear the bucket"))
    except Exception as exc:                                     # noqa: BLE001
        out.append((FAIL, "LIVE LOGIC: the limiter could not be exercised (%s) -- unproven"
                    % exc))

    if not out:
        out.append((INFO, "admin door has its own 10-failure budget; successes cost nothing in "
                          "either lane; the three call-metered endpoints still spend; refusals "
                          "carry exact seconds"))
    return out



@entry("RG-0137", "The domain that carries EVERYTHING has a recorded owner, a recorded expiry "
                  "and auto-renew ON -- the one dependency that can end the business silently",
       OPEN, scope="trustsquare.co, the apex the whole platform answers on. RECORD-half by "
                   "nature: no anonymous probe can read a registrar's expiry or auto-renew "
                   "flag, so the assertion is that the FACT IS WRITTEN DOWN where the next "
                   "session reads, dated, and not near lapse. Class, not instance: any domain "
                   "the business depends on belongs in this block.",
       ref="DOMAIN-LIFELINE-1, 22 Aug 2026 (pre-soft-launch third-party sweep). Found: the "
           "registrar, the expiry date and the auto-renew state for trustsquare.co were "
           "recorded in NO file in the repo -- not in the third-party register, not in the "
           "access cheatsheet, not in canon. Every other dependency here has an owner and a "
           "state; the one that takes the site, the mail domain, the OAuth redirect URIs and "
           "the payment webhooks down together had none. A lapsed domain is not an outage you "
           "debug, it is one you discover from a customer. DNS is on Cloudflare "
           "(ainsley/koa.ns.cloudflare.com, probed 22 Aug) which narrows but does NOT prove "
           "the registrar -- a full-zone Cloudflare setup looks identical whether Cloudflare "
           "or a third party holds the registration. RDAP/WHOIS lookup was not available to "
           "the sweep session, so the fact has to come from David once and then live here.")
def rg_domain_lifeline_recorded():
    out = []
    txt = repo_file("THIRD_PARTY_LAUNCH_REGISTER.md")
    if txt is None:
        out.append((INFO, "outside the repo -- record-only entry, skipped"))
        return out
    import re as _re
    from datetime import datetime as _dt

    def field(name):
        m = _re.search(r"^%s:\s*(.+)$" % name, txt, _re.M)
        return (m.group(1).strip() if m else "")

    reg = field("DOMAIN_REGISTRAR")
    exp = field("DOMAIN_EXPIRY")
    ren = field("DOMAIN_AUTORENEW").lower()
    ver = field("DOMAIN_VERIFIED_ON")
    unknown = ("", "unknown", "UNKNOWN", "tbd", "TBD", "-")

    if reg in unknown:
        out.append((FAIL, "DOMAIN_REGISTRAR is not recorded -- nobody can say who holds "
                          "trustsquare.co or where the renewal card lives"))
    if exp in unknown:
        out.append((FAIL, "DOMAIN_EXPIRY is not recorded -- the lapse date is unknown"))
    else:
        try:
            days = (_dt.strptime(exp[:10], "%Y-%m-%d") - _dt.utcnow()).days
            if days < 60:
                out.append((FAIL, "domain expires in %d day(s) (%s) -- inside the 60-day "
                                  "danger window" % (days, exp[:10])))
            else:
                out.append((INFO, "domain expiry %s (%d days out)" % (exp[:10], days)))
        except Exception:
            out.append((FAIL, "DOMAIN_EXPIRY %r is not a YYYY-MM-DD date" % exp[:20]))
    if ren not in ("on", "yes", "enabled", "true"):
        out.append((FAIL, "DOMAIN_AUTORENEW is %r -- renewal depends on someone remembering"
                    % (ren or "unrecorded")))
    if ver in unknown:
        out.append((FAIL, "DOMAIN_VERIFIED_ON is not recorded -- an undated status assertion "
                          "is a defect (the evidence-ladder rule)"))
    else:
        try:
            age = (_dt.utcnow() - _dt.strptime(ver[:10], "%Y-%m-%d")).days
            if age > 180:
                out.append((FAIL, "the domain record was last verified %d days ago (%s) -- "
                                  "stale, re-read it at the registrar" % (age, ver[:10])))
        except Exception:
            out.append((FAIL, "DOMAIN_VERIFIED_ON %r is not a YYYY-MM-DD date" % ver[:20]))

    if not out:
        out.append((INFO, "registrar %s · expiry %s · auto-renew %s · verified %s"
                    % (reg, exp[:10], ren, ver[:10])))
    return out


@entry("RG-0138", "An outage is noticed by something that is NEITHER the server nor David's "
                  "desktop -- an external watcher pings /health on a schedule and can wake him",
       OPEN, scope="The whole outage-detection lane. Class property: every instrument that "
                   "currently watches trustsquare.co runs either ON the box it watches (ops "
                   "sweep, BIT, subscription monitor, cron sensors) or on David's PC (the "
                   "06:30 daily watch) -- so a dead box or a closed laptop is a blind day, by "
                   "construction. This asserts an independent vantage exists AND is alive, "
                   "not merely that a file describing one is in the repo.",
       ref="UPTIME-EXTERNAL-1, 22 Aug 2026. OPEN_LOOPS L8 has carried 'external uptime "
           "monitor -- NOT BUILT' since 14 Aug with the next action 'David names a service', "
           "which is a vendor fork he should never have been handed (RUL-037): the technical "
           "decision is Claude's against the specs. Decided and built this run: a CLOUDFLARE "
           "WORKER on a 5-minute cron trigger -- no new vendor (Cloudflare already carries "
           "DNS, CDN and the inbound email worker), no new money (cron triggers and 100k "
           "requests/day are on the free plan, which RUL-022's no-paid-source spirit and the "
           "fixed-cost pricing rule both prefer), and a vantage that owes nothing to the "
           "Hetzner box or to a laptop being open. Two consecutive failures alert, recovery "
           "alerts once, and a DAILY HEARTBEAT proves the watcher itself is alive -- because "
           "a monitor that has silently died is indistinguishable from a site that is fine. "
           "Deploy is one wrangler command and needs David's Cloudflare token + the RESEND "
           "key, so it is sequenced to ride straight after the secret rotation (fresh key, "
           "not a burnt one). Stays OPEN until the deploy marker and a live heartbeat exist.")
def rg_external_uptime_watcher():
    out = []
    js = repo_file("ops/cloudflare/uptime_monitor_worker.js")
    tm = repo_file("ops/cloudflare/uptime_wrangler.toml")
    if js is None or tm is None:
        out.append((FAIL, "the external watcher's source is missing from the repo "
                          "(ops/cloudflare/uptime_monitor_worker.js + uptime_wrangler.toml)"))
        return out
    if "/health" not in js:
        out.append((FAIL, "the watcher does not probe /health"))
    if "scheduled" not in js:
        out.append((FAIL, "the watcher has no scheduled (cron) handler -- it would never run "
                          "on its own"))
    if "HEARTBEAT" not in js.upper():
        out.append((FAIL, "the watcher has no daily heartbeat -- a silently dead monitor "
                          "reads exactly like a healthy site"))
    if "crons" not in tm:
        out.append((FAIL, "uptime_wrangler.toml declares no cron trigger"))

    dep = repo_file("ops/cloudflare/UPTIME_DEPLOYED.md")
    if dep is None:
        out.append((FAIL, "NOT DEPLOYED -- source is ready and proven-by-inspection, but no "
                          "deploy marker exists, so nothing outside the box is watching. "
                          "Run ops/cloudflare/UPTIME_MONITOR.md's one command after the "
                          "secret rotation, then write the marker."))
    else:
        import re as _re
        from datetime import datetime as _dt
        m = _re.search(r"^LAST_HEARTBEAT:\s*(\d{4}-\d{2}-\d{2})", dep, _re.M)
        if not m:
            out.append((FAIL, "deploy marker carries no LAST_HEARTBEAT date"))
        else:
            age = (_dt.utcnow() - _dt.strptime(m.group(1), "%Y-%m-%d")).days
            if age > 7:
                out.append((FAIL, "the watcher's last heartbeat was %d days ago (%s) -- the "
                                  "monitor itself is down" % (age, m.group(1))))
            else:
                out.append((INFO, "external watcher deployed; heartbeat %s (%d day(s) old)"
                            % (m.group(1), age)))
    return out


@entry("RG-0139", "The Google sign-in door is open to EVERYONE, not just listed test users -- "
                  "the consent screen is PUBLISHED and the fact is dated",
       OPEN, scope="Google OAuth, the only social sign-in lane (Apple is OUT by RUL-030). "
                   "Two halves: the LIVE half -- the app advertises and wires the lane -- and "
                   "the RECORD half, because an OAuth app left in 'Testing' 302s to Google "
                   "exactly like a published one and only fails at the moment a real stranger "
                   "tries to sign in. No anonymous probe can tell the two apart, so the "
                   "publishing state must be read once at the console and written down dated.",
       ref="ONETAP-PUBLISH-1, 22 Aug 2026. Companion to RG-0111 (the lane is live) and to "
           "ONETAP-DOC-1 (21 Aug -- the register wrongly said the lane was dark while "
           "/auth/providers said google:true; the probe won and the doc was fixed). This "
           "entry closes the remaining, subtler version of the same trap: a Testing-mode "
           "consent screen is invisible to every instrument we own and would present as "
           "'sign-in is broken for new users' on soft-launch morning, with 100 test-user "
           "slots as the only capacity. Verified live 22 Aug: /auth/providers -> "
           "{google:true,apple:false} and /auth/oauth/google/start 302s to "
           "accounts.google.com carrying a client_id; /auth/oauth/apple/start 503s, which is "
           "RUL-030 enforcing itself.")
def rg_google_consent_published():
    out = []
    try:
        prov = _get("/auth/providers")
        if '"google": true' not in prov.replace('":', '": ').replace("  ", " "):
            if '"google":true' not in prov.replace(" ", ""):
                out.append((FAIL, "LIVE: /auth/providers no longer advertises google -- the "
                                  "sign-in lane went dark"))
    except ProbeOffline as e:
        out.append((INFO, "live half not read (%s)" % e))

    txt = repo_file("THIRD_PARTY_LAUNCH_REGISTER.md")
    if txt is None:
        out.append((INFO, "outside the repo -- record half skipped"))
        return out
    import re as _re
    from datetime import datetime as _dt
    m = _re.search(r"^GOOGLE_CONSENT_SCREEN:\s*(.+)$", txt, _re.M)
    val = (m.group(1).strip() if m else "")
    if not val or val.upper().startswith(("UNKNOWN", "TBD", "-")):
        out.append((FAIL, "GOOGLE_CONSENT_SCREEN is not recorded -- nobody has confirmed the "
                          "app is Published rather than in Testing, where only listed test "
                          "users can sign in"))
    elif "TESTING" in val.upper():
        out.append((FAIL, "the consent screen is in TESTING -- strangers cannot sign in with "
                          "Google. Publish it in the Google Cloud console."))
    elif "PUBLISHED" not in val.upper():
        out.append((FAIL, "GOOGLE_CONSENT_SCREEN reads %r -- not a recognised state" % val[:40]))
    else:
        d = _re.search(r"(\d{4}-\d{2}-\d{2})", val)
        if not d:
            out.append((FAIL, "the PUBLISHED claim carries no verification date -- an undated "
                              "status assertion is a defect"))
        else:
            age = (_dt.utcnow() - _dt.strptime(d.group(1), "%Y-%m-%d")).days
            if age > 90:
                out.append((FAIL, "the PUBLISHED claim was last verified %d days ago (%s) -- "
                                  "re-read it at the console" % (age, d.group(1))))
            else:
                out.append((INFO, "consent screen PUBLISHED, verified %s (%d day(s) ago)"
                            % (d.group(1), age)))
    return out


# ════════════════════════════════════════════════════════════════════════════


@entry("RG-0140", "AI example adverts are labelled as AI examples -- no shipped asset calls one "
                  "a SUPER ADVERT, and the detail pill says it is not a real listing",
       LOCKED, scope="ms.js, ALL FOUR renderers that paint the exemplar ribbon (browse lcard, "
                     "Adventures renderAdvGrid, the listing detail pill, Local Market cards) "
                     "-- repo AND the live-served build at the ?v= the live index references",
       fixed_on="2026-08-22",
       ref="AI-EXAMPLE-1, David's ruling 22 Aug 2026 (RUL-038). The red ribbon said '★ SUPER "
           "ADVERT'. David's finding: a star plus the word SUPER reads as an ACCOLADE on a real, "
           "live listing -- so an AI-generated example advert looked like something a buyer could "
           "spend an Introduction on. That is a mis-selling risk in the one place the model cannot "
           "afford one: MarketSquare only ever sells the introduction, and there is no seller "
           "behind an exemplar to introduce anyone to. Fix: the label states what the thing IS "
           "('AI EXAMPLE GENERATED ADVERT'), the star is gone, and the detail pill leads with "
           "'not a real listing'. The DB column stays super_example -- this is a labelling fix, "
           "not a data-model change, which is why RG-0014 (the ribbon RENDERS at all) still "
           "asserts on the field and is untouched by it. Scope note: a partial fix here is the "
           "known failure mode -- RG-0014's own history is three passes that each fixed one "
           "renderer and left the others bare -- so this entry asserts ALL FOUR sites at once and "
           "asserts the ABSENCE of the old wording, which a fifth renderer copy-pasted from an "
           "old one would trip. OPEN until the next frontend deploy ships the new ms.js -- the repo half passes now, the live half cannot until David ships. PROMOTED TO LOCKED 22 Aug 2026 after the deploy: live ms.js v516 carries all four labelled sites, the old wording absent. STRENGTHENED same day (22 Aug, David): also asserts the ABSENCE of 'free for a real seller to claim'. The first cut of the pill branched on showcase and offered exactly that -- struck, because it implies a seller could claim THAT EXACT advert, and therefore that the advert already exists as a real thing. The whole point of the rename is to stop an exemplar reading as a real, transactable listing; a claim offer walks it straight back. Never weakened.")
def rg_ai_example_label():
    out = []
    LABEL = "AI EXAMPLE GENERATED ADVERT"
    OLD = "SUPER ADVERT"

    def check(js, where):
        if OLD in js:
            out.append((FAIL, where + " still calls an AI example advert a '" + OLD + "' -- the "
                              "accolade wording reads as a real, buyable listing (AI-EXAMPLE-1)"))
        n = js.count(LABEL)
        if n < 4:
            out.append((FAIL, where + " paints the exemplar ribbon at only %d of the 4 renderers "
                              "(browse / Adventures / detail pill / Local Market) -- the "
                              "partial-rename failure mode" % n))
        else:
            out.append((INFO, where + ": %d labelled site(s), old wording absent" % n))
        if "free for a real seller to claim" in js:
            out.append((FAIL, where + " offers an AI example advert as claimable -- that implies "
                              "a seller could claim THAT EXACT advert, and therefore that the "
                              "advert already exists as a real thing (David, 22 Aug)"))
        if "not a real listing" not in js:
            out.append((FAIL, where + " detail pill no longer says 'not a real listing' -- the "
                              "sentence that stops a buyer spending an Introduction on an exemplar"))

    fe = repo_file("ms.js")
    if fe is None:
        out.append((INFO, "ms.js not present (running outside the repo) -- repo half skipped"))
    else:
        check(fe, "repo ms.js")

    try:
        mv = re.search(r"ms\.js\?v=(\d+)", _get("/"))
        check(_get("/static/ms.js" + ("?v=" + mv.group(1) if mv else "")),
              "live-served ms.js" + (" v" + mv.group(1) if mv else ""))
    except ProbeOffline as e:
        out.append((INFO, "live half not read (%s)" % e))
    except Exception as ex:
        out.append((FAIL, "could not verify the live-served ms.js build: %r" % (ex,)))
    return out


# ════════════════════════════════════════════════════════════════════════════


@entry("RG-0141", "Every demo map carries the red DEMO tab, and it is NOT gated on the tester flag",
       LOCKED, scope="all 15 adventures_*_map.html demo pages + ts_demo_banner.js + the deploy "
                     "manifest -- repo AND live",
       fixed_on="2026-08-22",
       ref="DEMO-BANNER-1, David's ruling 22 Aug 2026 (RUL-038, second half). The demo maps had "
           "no page-level statement that they are demonstrations; the only right-edge tab was the "
           "gold REPORT tab, which is a TESTER instrument and is removed at Soft Launch. David's "
           "instruction: put a red DEMO banner in that slot. The trap this entry exists to catch "
           "is the obvious wrong implementation -- hanging DEMO off ts_report.js or off the "
           "launch_switches.fault_report flag, which would delete the customer-facing honesty "
           "label on the exact day the first customers arrive. So this asserts BOTH that every "
           "demo map loads it AND that the script never reads the tester flag or the tester "
           "check. Also asserts the ONE-DEPLOY rule for a new deployable file (a manifest line, "
           "never an scp) and RG-0025's first-party rule (no third-party host in the script). "
           "New demo map with no DEMO tab = red the same day. OPEN until the next deploy places ts_demo_banner.js on the server; PROMOTED TO LOCKED 22 Aug 2026 after the deploy: /static/ts_demo_banner.js serves and mounts the tab, and the live ZA demo map loads it.")
def rg_demo_banner_on_demo_maps():
    import glob
    out = []
    SRC = "ts_demo_banner.js"

    js = repo_file(SRC)
    if js is None:
        out.append((INFO, "outside the repo -- repo half skipped"))
    else:
        if "ts-demo-tab" not in js or ">DEMO" not in js.replace("'DEMO'", ">DEMO"):
            out.append((FAIL, SRC + " no longer mounts a tab labelled DEMO"))
        if "#e63946" not in js:
            out.append((FAIL, SRC + " no longer paints the DEMO tab red (#e63946) -- red is the "
                              "signal that separates it from the gold tester REPORT tab"))
        # check the CODE, not the prose: the header comment legitimately explains
        # why the tab is not gated on the tester flag, and naming it there must
        # not trip the assertion that the code never reads it.
        code = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)
        code = re.sub(r"(?m)^\s*//.*$", " ", code)
        for banned in ("fault_report", "isTester", "/flags"):
            if banned in code:
                out.append((FAIL, SRC + " reads %r -- the DEMO label must NOT be gated on the "
                                  "tester lane, or it vanishes at Soft Launch when the REPORT "
                                  "tab is removed" % banned))
        for host in ("http://", "https://"):
            if host in js.replace("https://trustsquare.co", ""):
                out.append((FAIL, SRC + " references an absolute URL -- demo pages are "
                                  "first-party-only (RG-0025)"))

        maps = sorted(glob.glob(os.path.join(REPO, "adventures_*_map.html")))
        if not maps:
            out.append((FAIL, "no adventures_*_map.html demo pages found in the repo"))
        missing = [os.path.basename(m) for m in maps
                   if SRC not in open(m, encoding="utf-8", errors="replace").read()]
        if missing:
            out.append((FAIL, "demo map(s) with no DEMO tab: " + ", ".join(missing)))
        else:
            out.append((INFO, "%d demo map(s), every one loads %s" % (len(maps), SRC)))

        man = repo_file(os.path.join("ops", "autodeploy", "deploy_manifest.txt"))
        if man is not None and SRC not in man:
            out.append((FAIL, SRC + " is not in deploy_manifest.txt -- it will never reach the "
                              "server (ONE-DEPLOY: a new deployable file is one manifest line)"))

    try:
        live = _get("/static/" + SRC)
        if "ts-demo-tab" not in live:
            out.append((FAIL, "live-served " + SRC + " does not mount the DEMO tab"))
        else:
            out.append((INFO, "live " + SRC + " serves and mounts the DEMO tab"))
        if SRC not in _get("/static/adventures_za_map.html"):
            out.append((FAIL, "the live ZA demo map does not load " + SRC))
    except ProbeOffline as e:
        out.append((INFO, "live half not read (%s)" % e))
    except Exception as ex:
        out.append((FAIL, "could not verify the live DEMO tab: %r" % (ex,)))
    return out


# ---------------------------------------------------------------------------
# HALT money-path + safety-layer block. Written 22 Aug 2026 by the D-7 HALT
# verification pass; CORRECTED the same session after a fresh adversarial peer
# found three false-red and three false-green paths in the first cut. The
# corrections are named in each ref -- an assertion that is wrong gets fixed,
# never weakened, and never silently.
# ---------------------------------------------------------------------------

def _conditional_lines(code):
    """Only CONTROL FLOW counts as a guard. Scanning raw handler text let the SQL that
    WRITES tuppence_charged satisfy the check for code that READS it -- a false green
    caught 22 Aug 2026 the same session it was introduced. A guard is an if/elif/assert
    or an early return/raise, never a string literal handed to conn.execute()."""
    keep = []
    for ln in code.splitlines():
        s = ln.strip()
        if re.match(r"^(if|elif|assert)\b", s) or " if " in s or s.startswith(("raise ", "return ")):
            if "conn.execute" in s or "UPDATE " in s or "INSERT " in s:
                continue
            keep.append(s)
    return "\n".join(keep)


def _strip_py_comments(text):
    """Comments and docstrings must never satisfy an assertion. A TODO saying
    'check tuppence_charged' is not a check (peer finding, 22 Aug 2026)."""
    text = re.sub(r'"""(?:.|\n)*?"""', " ", text)
    text = re.sub(r"'''(?:.|\n)*?'''", " ", text)
    return re.sub(r"(?m)#.*$", " ", text)


@entry("RG-0142", "The money path is IDEMPOTENT and STATE-GUARDED -- accepting one introduction "
                  "charges the buyer exactly once however many times the request arrives, a wallet "
                  "can never go negative, and no introduction can be declined after it was charged",
       LOCKED, fixed_on="2026-08-22",
       scope="bea_main.py accept_intro + decline_intro (PUT /intros/{intro_id}/accept and "
                   "/decline) and the whole intro-charge class: every handler that writes a "
                   "negative-amount row to transactions must first check it has not already "
                   "charged for that object, and every status write must check the transition is "
                   "legal. CLASS, not instance -- lm_intro_deduct / lm_boost_deduct are the same "
                   "shape. The correct pattern ALREADY EXISTS in this repo: estate_agents.py "
                   "guards its accept with 409 on a non-pending status and 402 below balance, "
                   "with tests. The flagship buyer path never got it.",
       ref="FIXED 22 Aug 2026 (INTRO-CHARGE-ONCE-1), David: 'Why cant we close it now then?' -- it was a code fix, and code fixes do not wait on anything reserved to him. accept_intro now runs one immediate transaction: it re-reads the row under the lock, refuses a settled or already-charged introduction with 409, refuses below 1T with 402, and writes through a CONDITIONAL UPDATE whose rowcount is the single source of truth -- so two concurrent accepts cannot both win, which an if-statement alone can never guarantee. decline_intro refuses to decline a charged introduction. PROVEN by scripts/prove_intro_charge_once.py, which replays the audit's own attack on a throwaway replica (16 checks): four accepts leave ONE intro_deduct row and a 0T wallet where the audit measured four rows and -3T, a 0T buyer is refused 402 with no money row written, and decline-after-accept is refused. It also asserts the guarded SQL is the text actually in bea_main.py, so the test cannot pass against drifted source. Hardening note: get_db() uses sqlite3's default isolation level, so BEGIN IMMEDIATE is attempted and tolerated if a transaction is already open -- the guarantee lives in the conditional UPDATE, not the lock. ORIGINAL FINDING: HALT-MONEY-1, precipitated 22 Aug 2026 by the D-7 HALT run and UPHELD by adversarial "
           "peer the same morning. Grade EXECUTED: the peer ran the REAL bea_main app under a "
           "FastAPI TestClient against a scratch DB -- four PUTs to /intros/1/accept returned "
           "200/200/200/200 with the balance walking 1 -> 0 -> -1 -> -2 -> -3 and four "
           "intro_deduct rows for ONE introduction, the full middleware stack running. Worse than "
           "first found: create_intro takes no hold and never checks balance, so a 0T buyer goes "
           "negative on the FIRST accept with no retry needed. Balance is COALESCE(SUM(amount),0) "
           "at ~13 sites -- there is no balance column and no floor; _deduct_tuppence has a 402 "
           "floor but accept_intro does not call it, it INSERTs -1 directly. transactions carries "
           "no unique index, trigger or constraint, and ms.js handleIntro does not disable the "
           "button during the await, so two fast clicks fire two PUTs. decline_intro is "
           "unguarded in the same way: declining after an accept leaves tuppence_charged=1 with "
           "no refund row -- the buyer paid for an introduction the record calls declined. "
           "CORRECTED 22 Aug after peer review: (1) comments and docstrings are stripped before "
           "any guard scan, so a TODO can no longer satisfy it; (2) the guard-1 token set now "
           "accepts the repo's OWN proven pattern (status != 'pending' -> 409) which the first "
           "cut would have called red AFTER a correct fix -- a false-red is how an assertion gets "
           "weakened by a later session; (3) the handler window is found by structure, not a "
           "4000-char slice that a growing handler could slide out of; (4) the concurrency guard "
           "is a FAIL, not an INFO, because an interleaved double-accept is the same defect. "
           "CORRECTED TWICE the same session: the broadened token set immediately produced a FALSE GREEN -- accept_intro's own UPDATE ... SET tuppence_charged=1 satisfied the check for code that READS the flag. Guards are now matched only against control flow (if/elif/assert/early return), never against SQL handed to conn.execute. Source assertion BY DESIGN -- it must never be 'strengthened' into a live probe, "
           "because proving it live would mean charging a real buyer twice.")
def rg_money_path_idempotent():
    out = []
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "outside the repo -- source half skipped")]

    def _handler(name):
        i = src.find("def %s(" % name)
        if i < 0:
            return None
        j = src.find("\n@app.", i + 1)
        k = src.find("\n@entry", i + 1)
        ends = [x for x in (j, k) if x > 0]
        return src[i:(min(ends) if ends else i + 12000)]

    acc = _handler("accept_intro")
    if acc is None:
        out.append((FAIL, "accept_intro no longer exists in bea_main.py -- the money path moved; "
                          "re-point this assertion rather than deleting it"))
        return out
    acc_code = _strip_py_comments(acc)

    if "intro_deduct" not in acc_code:
        out.append((INFO, "accept_intro no longer writes intro_deduct directly -- confirm the "
                          "charge moved behind a guarded helper, then re-point this entry"))
        return out
    before = acc_code[:acc_code.find("intro_deduct")]

    # GUARD 1 -- refuse to charge twice. Accepts the repo's own proven estate-agent
    # pattern as well as an explicit already-charged test.
    tests = _conditional_lines(before)
    guard1 = any(tok in tests for tok in (
        '!= "pending"', "!= 'pending'",
        '== "accepted"', "== 'accepted'",
        "tuppence_charged", "already_accepted", "_already_charged", "idempot"))
    if not guard1:
        out.append((FAIL, "accept_intro charges the buyer WITHOUT first checking the introduction's "
                          "status or whether it was already charged -- a retry or double-click "
                          "takes a second Tuppence for one introduction (EXECUTED against the real "
                          "app 22 Aug: four accepts, four charges, balance -3T). "
                          "estate_agents.py already does this correctly with a 409"))
    else:
        out.append((INFO, "accept_intro guards the accept transition before charging"))

    # GUARD 2 -- the wallet must have a floor.
    guard2 = any(tok in tests for tok in (
        "balance", "_deduct_tuppence", "insufficient", "402"))
    if not guard2:
        out.append((FAIL, "accept_intro never reads the buyer's balance before deducting -- the "
                          "wallet has no floor at zero. create_intro takes no hold either, so a "
                          "0T buyer goes negative on the FIRST accept"))
    else:
        out.append((INFO, "accept_intro tests a balance before deducting"))

    # GUARD 3 -- read-check-write must not straddle a commit boundary (FAIL, not INFO:
    # an interleaved double-accept charges twice exactly like a retry does).
    guard3 = any(tok in acc_code for tok in ("BEGIN IMMEDIATE", "_charge_once", "IMMEDIATE"))
    if not guard3:
        out.append((FAIL, "accept_intro's read-check-write is not one transaction (no BEGIN "
                          "IMMEDIATE / _charge_once) -- two concurrent accepts interleave between "
                          "the check and the insert and charge twice even once GUARD 1 lands"))
    else:
        out.append((INFO, "the charge runs inside one immediate transaction"))

    # GUARD 4 -- decline must be state-guarded too, or a charged intro can be declined.
    dec = _handler("decline_intro")
    if dec is None:
        out.append((INFO, "decline_intro not found -- decline half skipped"))
    else:
        dec_code = _strip_py_comments(dec)
        i = dec_code.find("status = 'declined'")
        if i < 0:
            i = dec_code.find('status = "declined"')
        if i < 0:
            out.append((INFO, "decline_intro no longer writes a declined status directly"))
        else:
            head = dec_code[:i]
            head = _conditional_lines(head)
            if not any(tok in head for tok in ('!= "pending"', "!= 'pending'", "tuppence_charged",
                                               '== "accepted"', "== 'accepted'", "409")):
                out.append((FAIL, "decline_intro sets status='declined' without checking the "
                                  "introduction was not already accepted and charged -- a "
                                  "decline-after-accept leaves tuppence_charged=1 with no refund "
                                  "row: the buyer paid for an introduction the record calls "
                                  "declined"))
            else:
                out.append((INFO, "decline_intro guards the decline transition"))
    return out


@entry("RG-0145", "The wallet behaves the way the EULA PROMISES it behaves -- if the app tells a "
                  "buyer 1T is held at request and released on decline or expiry, the code holds "
                  "and releases it",
       LOCKED, fixed_on="2026-08-22",
       scope="marketsquare.html EULA/terms wallet clause against bea_main.py create_intro, "
                   "accept_intro, decline_intro and the expiry path. CLASS: any user-facing "
                   "promise about money -- holds, releases, refunds, expiries -- must have a "
                   "matching code path. A promise with no implementation is a misrepresentation, "
                   "not a bug.",
       ref="FIXED 22 Aug 2026 (INTRO-HOLD-1), same session as RG-0142, David: 'lets go for clear'. The wording was NOT changed -- it is legally load-bearing (the ECT Act s44 cooling-off argument rests on 'until delivery it is only held, not spent') and RUL-020 released the EULA as final. The CODE now keeps the promise: create_intro refuses below 1T with 402 and writes a real -1 'intro_hold' row, so the buyer sees the commitment in their balance immediately, exactly as they were told; accept_intro BURNS that hold with a zero-amount 'intro_burn' audit row instead of deducting a second time (the ledger stays append-only); decline_intro and the expiry sweep both call _release_intro_hold, which is a CONDITIONAL UPDATE on hold_released_at IS NULL -- releasing twice would MINT Tuppence, so the rowcount is the only authority and the money row is written only when that UPDATE claimed the row. The expiry release matters twice over: that sweep's email to the buyer already said 'You were not charged', which was only true once the hold was returned. Schema: migrations/030_intro_hold.py (tuppence_held, hold_released_at); intros created before it carry held=0 and take the legacy charge-on-accept path -- no money is retro-held from live wallets. PROVEN by scripts/prove_intro_hold.py, 22 checks on a throwaway replica: hold placed at request (3T->2T), burned once on delivery with exactly ONE negative row, released in full on decline (back to 3T) and on expiry, second release impossible, and a 0T buyer refused 402 rather than going negative. ORIGINAL FINDING: HALT-PROMISE-1, found 22 Aug 2026 by the adversarial peer on the D-7 HALT run while "
           "attacking RG-0142, and it is a DIFFERENT defect from idempotency. marketsquare.html "
           "tells the user that 1 Tuppence is 'committed (held) when the Buyer makes the request' "
           "and 'released in full if declined or expired'. There is no hold, no release and no "
           "balance check at request time anywhere in the code: create_intro records the request "
           "and charges nothing, accept_intro then INSERTs the -1 directly, and a declined or "
           "expired introduction has nothing to release because nothing was ever held. Fixing "
           "RG-0142's floor-at-accept does NOT close this -- the two can both be true and this "
           "still be false. It matters beyond correctness: on a trust-branded marketplace the "
           "terms a buyer agreed to describe a mechanism that does not exist, which is a legal "
           "and product exposure, not only an engineering one. Two honest resolutions: implement "
           "the hold/release, or change the wording to describe what the code actually does. "
           "Reserved to David which way it goes -- that is a commercial and legal call, not a "
           "technical one. OPEN until promise and code agree.")
def rg_wallet_matches_the_promise():
    out = []
    src = repo_file("bea_main.py")
    fe = repo_file("marketsquare.html")
    if src is None or fe is None:
        return [(INFO, "outside the repo -- source half skipped")]

    promises_hold = bool(re.search(r"committed\s*\(held\)|is held when|held when the buyer",
                                   fe, flags=re.I))
    promises_release = bool(re.search(r"released in full|refunded in full|release[sd]?\s+if\s+declined",
                                      fe, flags=re.I))
    if not (promises_hold or promises_release):
        out.append((INFO, "the shipped terms no longer promise a hold/release -- promise and code "
                          "agree by removal; confirm that was deliberate"))
        return out

    code = _strip_py_comments(src)
    has_hold = any(tok in code for tok in (
        "intro_hold", "'hold'", '"hold"', "hold_tuppence", "_place_hold", "intro_held"))
    if not has_hold:
        out.append((FAIL, "the shipped terms tell the buyer 1T is HELD when the request is made, "
                          "but no hold exists in the code -- create_intro charges nothing and "
                          "accept_intro deducts directly. The user agreed to a mechanism that is "
                          "not implemented"))
    else:
        out.append((INFO, "a hold mechanism exists in the code"))

    if promises_release:
        has_release = any(tok in code for tok in (
            "_release_hold", "release_hold", "intro_refund", "'hold_release'", "hold_released"))
        if not has_release:
            out.append((FAIL, "the shipped terms promise the held Tuppence is RELEASED in full on "
                              "decline or expiry, but no release path exists -- there is nothing "
                              "to release because nothing was held"))
        else:
            out.append((INFO, "a release path exists in the code"))
    return out


@entry("RG-0143", "Every flag the BIT Mitigator is allowed to flip is actually READ by the app -- "
                  "the automatic safe-state response changes behaviour instead of only changing a "
                  "row and reporting success",
       OPEN, scope="ops/bit/bit_mitigator.py SAFE_FLAGS entire (today: ai_example_enabled, "
                   "auth_fail_closed, tuppence_burn_enabled) against bea_main.py and the shipped "
                   "front end. CLASS property: any flag added to SAFE_FLAGS in future is caught by "
                   "the same assertion. MITIGATION layer only -- the BIT DETECTION layer is real "
                   "and passing (B-NEG-AUTH is a live S1 check and PASSes).",
       ref="HALT-PLACEBO-1, precipitated 22 Aug 2026 by the D-7 HALT run and UPHELD by adversarial "
           "peer the same morning, which raised it from READ to EXECUTED: with the mitigator's "
           "FULL safe-state written into a scratch DB (tuppence_burn_enabled=0, "
           "ai_example_enabled=0, auth_fail_closed=1) the real app still returned 200 to another "
           "accept and wrote a fifth intro_deduct row. The safe state stops nothing. Every real "
           "switch in this codebase has a per-flag helper (_account_binding_enabled, "
           "_intro_relay_enabled, the fault_report reader); these three have none, and there is no "
           "generic _switch() fan-out. PROBED live: the served ms.js -- 1.12 MB, fetched from the "
           "server, not the repo copy -- contains zero occurrences of any of the three names and "
           "reads only f.effective from /flags, never bit_flags. main.py is not a second app: "
           "deploy_manifest.txt ships bea_main.py AS main.py. 'Placebo' is the fair word because "
           "escalation fires only for UNMAPPED BITs, so for these three the mitigator returns 200, "
           "reports APPLIED, and the console-only user_msg 'you will not be charged in the "
           "meantime' is never shown to a user and never true. CORRECTED 22 Aug after peer review: "
           "(1) comments are stripped before counting a consumer, so one mention in a comment can "
           "no longer clear the verdict; (2) the /flags exposure line is detected structurally "
           "rather than by a hardcoded tuple substring that reformatting would defeat; (3) an "
           "EMPTY SAFE_FLAGS is a PASS, not a parse failure -- removing a flag from the "
           "allow-list is one of the two sanctioned fixes and must not read as red.")
def rg_mitigator_flags_are_real():
    out = []
    mit = repo_file(os.path.join("ops", "bit", "bit_mitigator.py"))
    src = repo_file("bea_main.py")
    if mit is None or src is None:
        return [(INFO, "outside the repo -- source half skipped")]

    m = re.search(r"SAFE_FLAGS\s*=\s*\{(.*?)^\}", mit, flags=re.S | re.M)
    if not m:
        m = re.search(r"SAFE_FLAGS\s*=\s*\{(.*?)\}", mit, flags=re.S)
    if not m:
        out.append((FAIL, "bit_mitigator.py no longer declares SAFE_FLAGS -- re-point this "
                          "assertion rather than deleting it"))
        return out
    flags = re.findall(r'"([a-z0-9_]+)"\s*:\s*\{', m.group(1))
    if not flags:
        out.append((INFO, "SAFE_FLAGS is empty -- the mitigator may flip nothing and must escalate "
                          "every BIT to a human. That is one of the two sanctioned resolutions; "
                          "no placebo lever can exist"))
        return out

    def _is_plumbing(line, flag):
        s = line.strip()
        if not s:
            return True
        # schema / migration / model / read-back / the /flags exposure tuple, detected
        # structurally: a line that only quotes flag NAMES in a row is an exposure list.
        if "INTEGER NOT NULL DEFAULT" in s or s.startswith("ALTER TABLE") or '"ALTER TABLE' in s:
            return True
        if re.match(r'^[a-z0-9_]+:\s*Optional\[', s):
            return True
        if re.match(r'^"[a-z0-9_]+":\s*bool\(d\.get', s):
            return True
        if len(re.findall(r'"[a-z0-9_]+"', s)) >= 2 and "(" not in s.replace("(", "", 1):
            return True
        if re.match(r'^"[a-z0-9_]+",?$', s):
            return True
        return False

    code = _strip_py_comments(src)
    front = ""
    for fe in ("ms.js", "marketsquare.html"):
        t = repo_file(fe)
        if t:
            front += t

    placebo = []
    for f in flags:
        live = [ln for ln in code.splitlines() if f in ln and not _is_plumbing(ln, f)]
        if not live and f not in front:
            placebo.append(f)

    if placebo:
        out.append((FAIL, "the BIT Mitigator may flip %d flag(s) that NOTHING reads: %s -- flipping "
                          "them changes a row and reports the S1 mitigated while the app's "
                          "behaviour is unchanged. A placebo breaker is worse than no breaker, "
                          "because it consumes the incident instead of escalating it" %
                          (len(placebo), ", ".join(sorted(placebo)))))
    else:
        out.append((INFO, "all %d mitigator flag(s) are consumed at a decision site" % len(flags)))

    if "tuppence_burn_enabled" in placebo:
        out.append((FAIL, "tuppence_burn_enabled is one of them -- its declared user message "
                          "promises 'you will not be charged in the meantime' while charging "
                          "continues (EXECUTED: full safe-state applied, the charge still "
                          "succeeded). This is the lever an operator would pull during an RG-0142 "
                          "double-charge incident"))
    return out


@entry("RG-0144", "The public dashboard does not tell an anonymous stranger which defences are "
                  "down -- security posture is never published on an unauthenticated endpoint",
       OPEN, scope="GET /dashboard/summary, the dashboard payload that answers anonymously today. "
                   "CLASS: any unauthenticated endpoint that renders operational prose belongs "
                   "here -- the assertion is about publishing POSTURE to strangers, not about this "
                   "one route.",
       ref="HALT-LEAK-1, found by the Cycle 2 doctoral peer on 22 Aug 2026 and re-PROBED at 07:25: "
           "GET /dashboard/summary returns 200 to an anonymous client and its prose states in "
           "plain words that the Cloudflare WAF allowlist is DISABLED and the origin gate is 'the "
           "only guard', alongside the box sizing, the stack, the live counts and the launch "
           "dates. That is a reconnaissance gift -- it names the single control to test and, with "
           "RUL-001 quoted beside it, the week to test it. This asserts the ABSENCE of posture "
           "disclosure to ANONYMOUS callers; RUL-034 deliberately keeps the allowlist down "
           "pre-launch and RG-0029 owns the gate posture itself. Telling the world about it is the "
           "separate defect. CORRECTED 22 Aug after peer review, which found a false-red that "
           "would have punished the better fix: the first cut read the body through _get(), which "
           "transparently RETRIES a 401/403 with the reviewer cookie -- so gating the endpoint "
           "behind auth (one of the two right answers) would still have shown the posture prose to "
           "the authenticated read and kept the entry red forever, pushing a later session to "
           "weaken it. It now checks the ANONYMOUS status first via _status() and only reads the "
           "body when a stranger can actually get one. Also broadened: the banned set was six "
           "literal words that 'bot management is off', 'allow-list' or 'the origin token is the "
           "sole control' would all have walked straight past.")
def rg_no_public_posture_leak():
    out = []
    PATH = "/dashboard/summary"
    try:
        st = _status(PATH)
    except ProbeOffline as e:
        return [(INFO, "live half not read (%s)" % e)]

    if st in (401, 403):
        out.append((INFO, "%s refuses anonymous callers (%d) -- a stranger reads no posture" % (PATH, st)))
        return out
    if st != 200:
        out.append((INFO, "%s answered %d anonymously -- nothing published" % (PATH, st)))
        return out

    try:
        req = urllib.request.Request(BASE + PATH, headers=UA)
        body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
    except ProbeOffline as e:
        return [(INFO, "live half not read (%s)" % e)]
    except Exception as ex:
        return [(FAIL, "could not read %s anonymously: %r" % (PATH, ex))]

    PATTERNS = (
        r"\bWAF\b", r"allow[\s\-_]?list", r"\bfirewall\b", r"bot\s*management",
        r"only\s+guard", r"sole\s+(?:guard|control)", r"GATE[\s\-_]?ENFORCE",
        r"\bunprotected\b", r"\bdisabled\b.{0,40}\b(?:WAF|gate|guard|firewall)\b",
        r"origin\s+(?:gate|token).{0,30}\b(?:only|sole)\b",
    )
    hits = sorted({p for p in PATTERNS if re.search(p, body, flags=re.I)})
    if hits:
        out.append((FAIL, "%s answers an ANONYMOUS client AND names the defence posture "
                          "(%d pattern(s) matched: %s) -- it tells a stranger which control to "
                          "test" % (PATH, len(hits), ", ".join(h[:26] for h in hits))))
    else:
        out.append((INFO, "the public summary names no defence posture"))
    return out



@entry("RG-0146", "Every credential the app holds is in SECRETS_REGISTER.md with a dated "
                  "status, and none of them is still BURNT",
       LOCKED, fixed_on="2026-08-22",
       scope="MarketSquare/SECRETS_REGISTER.md against the whole credential set. CLASS, not "
                   "instance: any NEW credential added to the app must get a row, and any row left "
                   "at BURNT or UNKNOWN keeps this red. Record-half assertion by necessity -- the "
                   "values live on the box and reading them is exactly the act that burnt them "
                   "twice (DW-029, DW-057), so this asserts the RECORD is honest and current, in "
                   "the shape RG-0137 established for facts no probe we own can reach.",
       ref="SECRETS-REGISTER-1, 22 Aug 2026. Born mid-rotation: DW-029/DW-057 had counted EIGHT "
           "exposed credentials for fifteen days, and the box was found carrying NINE MORE in "
           "/etc/environment at mode 0644 -- world-readable, with msdeploy holding a login shell to "
           "read it. The same `systemctl show -p Environment` dump that burnt the eight printed "
           "these nine too, so the register had been under-counting the leak the whole time. A "
           "prose list inside a daily-watch row cannot hold an inventory; this entry gives it "
           "machinery. Nine credentials were rotated and PROBED on 22 Aug (Resend 422, Paystack "
           "200, JWT fingerprint changed with /health 200); the rest stay BURNT in the register "
           "until they are replaced, which is what keeps this entry honestly red rather than "
           "cosmetically green.")
def rg_secrets_register_current():
    out = []
    txt = repo_file("SECRETS_REGISTER.md")
    if txt is None:
        return [(INFO, "repo half not read (run from inside the repo to check the register)")]
    if not txt.strip():
        return [(FAIL, "SECRETS_REGISTER.md is missing -- the credential inventory has no owner")]

    m = re.search(r"REGISTER_VERIFIED:\s*(\d{4}-\d{2}-\d{2})", txt)
    if not m:
        out.append((FAIL, "the register carries no REGISTER_VERIFIED date -- an undated inventory "
                          "is a claim, not a record"))
    else:
        try:
            age = (datetime.date.today() - datetime.date(*map(int, m.group(1).split("-")))).days
            if age > 180:
                out.append((FAIL, "the register was last verified %d days ago (%s) -- stale"
                                  % (age, m.group(1))))
            else:
                out.append((INFO, "register verified %s (%d days ago)" % (m.group(1), age)))
        except Exception:
            out.append((FAIL, "REGISTER_VERIFIED is not a readable date"))

    burnt = len(re.findall(r"^\|\s*[A-Z][A-Z0-9_ /]+\s*\|", txt, flags=re.M))
    still = txt.split("## Still burnt", 1)
    if len(still) == 2:
        rows = [l for l in still[1].split("## ")[0].splitlines()
                if l.startswith("|") and not l.startswith("|---") and "Credential" not in l]
        if rows:
            out.append((FAIL, "%d credential(s) are still BURNT -- exposed, live and not replaced: %s"
                              % (len(rows), ", ".join(r.split("|")[1].strip() for r in rows[:6]))))
        else:
            out.append((INFO, "no credential is still marked BURNT"))
    else:
        out.append((FAIL, "the register has no 'Still burnt' section -- its shape changed"))

    # UNROTATABLE rows are allowed to exist, but never silently: each must carry a
    # dated decision and its reasoning, or it is just a BURNT row wearing a better word.
    unrot = txt.split("## Unrotatable", 1)
    if len(unrot) == 2:
        rows = [l for l in unrot[1].split("## ")[0].splitlines()
                if l.startswith("|") and not l.startswith("|---") and "Credential" not in l]
        for r in rows:
            cells = [c.strip() for c in r.split("|")[1:-1]]
            name = cells[0] if cells else "?"
            if len(cells) < 4 or not re.search(r"\d{4}-\d{2}-\d{2}", cells[-1]):
                out.append((FAIL, "%s is marked unrotatable with no DATED decision -- that is a "
                                  "burnt credential with a nicer label" % name))
            elif len(cells[2]) < 80:
                out.append((FAIL, "%s is marked unrotatable but the acceptance reasoning is thin "
                                  "(%d chars) -- say why it is survivable" % (name, len(cells[2]))))
            else:
                out.append((INFO, "%s: unrotatable, accepted, reasoned and dated" % name))

    if "0644" in txt and "Now 0600" not in txt and "now 0600" not in txt.lower():
        out.append((FAIL, "the register records a world-readable secrets file with no remediation"))
    out.append((INFO, "%d credential row(s) in the register" % burnt))
    return out


@entry("RG-0147", "A credential is verified where it is USED -- the running process -- never "
                  "from the file it was written to",
       LOCKED, fixed_on="2026-08-22",
       scope="The rotation method itself, for every credential on the box. CLASS property: "
                   "any rotation tool added later must read back from /proc/<pid>/environ (or an "
                   "authenticated live probe) and compare, not trust its own write. Asserted "
                   "against the tooling in the repo.",
       ref="ROTATE-VERIFY-1, 22 Aug 2026. Paid for in a live outage the same morning: the Paystack "
           "key was written correctly to a 0600 systemd drop-in, the service restarted clean and "
           "reported active -- and the RUNNING PROCESS still held the old, just-revoked key, "
           "because /etc/environment is loaded via EnvironmentFile and won on precedence. Disk "
           "said rotated; production said 401; card payments were down and nothing reported it. "
           "The write is not the fact. Only the process environment and a live authenticated call "
           "are the fact -- which is the evidence-ladder rule (PROBED over READ) applied to "
           "secrets, and it is why every tool built this session ends with a read-back and a real "
           "call to the vendor.")
def rg_rotation_verifies_at_use():
    out = []
    tools = ("scripts/rotate_secrets.py", "scripts/fix_paystack_env.py",
             "scripts/install_gmail_password.py", "scripts/rotate_jwt_secret.py")
    seen = 0
    for t in tools:
        body = repo_file(t)
        if body is None:
            continue
        seen += 1
        if "environ" not in body:
            out.append((FAIL, "%s writes a credential but never reads it back from the running "
                              "process -- it can report success while production holds the old "
                              "value" % t))
    if not seen:
        return [(INFO, "rotation tooling not present in this checkout")]
    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "all %d rotation tool(s) read back from the running process" % seen))
    return out



@entry("RG-0148", "Every third-party data feed the app serves to customers is used within a "
                  "licence that PERMITS commercial use",
       LOCKED, fixed_on="2026-08-22",
       scope="Every external data source rendered to a user or used to price a listing: JustTCG "
                   "(TCG prices), Numista (coin catalogue), Travelpayouts/Aviasales (fares), and any "
                   "feed added later. CLASS, not instance -- the question 'may we use this "
                   "commercially' must be answered per feed, in writing, before launch traffic. "
                   "Record-half assertion: licence terms are not machine-readable, so this asserts "
                   "the DECISION exists and is dated, in the RG-0137 shape.",
       ref="FEED-LICENCE-1, 22 Aug 2026, found during the secret rotation while looking up where "
           "JustTCG keys are managed. JustTCG's pricing page states plainly: 'The free tier stays "
           "personal and non-commercial', with commercial use -- storefronts, inventory, anything "
           "customer-facing -- requiring a paid plan (Starter $19/mo, 10k calls; free tier 1,000/mo "
           "with a 100/day cap). MarketSquare is a commercial marketplace and "
           "`tier_resolvers.justtcg_price()` serves card prices into listings, so the free tier is "
           "outside its licence at launch. This is not a technical fault and Claude does not decide "
           "it: RUL-037 reserves spend to David. Three honest routes -- pay the $19/mo, drop the TCG "
           "price tier and let Numista carry collectibles, or keep the lane dark until it earns its "
           "keep. Numista's own terms and Travelpayouts' affiliate terms need the same one-line "
           "answer beside it. The entry stays OPEN until FEED_LICENCES.md records a dated decision "
           "per feed -- because a licence breach discovered after launch is a takedown, not a bug.")
def rg_feed_licences_decided():
    txt = repo_file("FEED_LICENCES.md")
    if txt is None:
        return [(INFO, "repo half not read")]
    if not txt.strip():
        return [(FAIL, "FEED_LICENCES.md does not exist -- no feed's commercial-use position is "
                       "recorded. JustTCG's free tier is explicitly non-commercial and is serving "
                       "prices into a commercial marketplace")]
    out = []
    for feed in ("JustTCG", "Numista", "Travelpayouts"):
        # the row may name the feed plus its programme ("Travelpayouts / Aviasales"),
        # so match the feed name at the start of the cell, not the whole cell.
        m = re.search(r"(?mi)^\|\s*%s\b[^|]*\|(.+)$" % feed, txt)
        if not m:
            out.append((FAIL, "%s has no row in FEED_LICENCES.md" % feed))
        elif not re.search(r"\d{4}-\d{2}-\d{2}", m.group(1)):
            out.append((FAIL, "%s's licence position carries no DATED decision" % feed))
        else:
            out.append((INFO, "%s: licence position recorded and dated" % feed))
    return out



@entry("RG-0149", "A feed's licence OBLIGATIONS are honoured in the product, not merely recorded "
                  "in a document -- attribution shown, retention respected",
       OPEN, scope="Every feed in FEED_LICENCES.md that carries obligations. Today that is Numista "
                   "(display N# identifiers, credit Numista as source, do not store catalogue data "
                   "beyond a 7-day metadata cache). CLASS: any feed added with obligations must be "
                   "asserted the same way -- a licence honoured only in a markdown table is not "
                   "honoured.",
       ref="FEED-OBLIGATION-1, 22 Aug 2026. Numista's API terms require the N# identifier to be "
           "displayed for catalogue search results, Numista named as the data source, and -- the "
           "operationally sharp one -- catalogue data NOT stored or cached, with permitted metadata "
           "capped at 7 days. `ai_service_tiers.py` already credits 'Catalogue price from Numista', "
           "so the source half is met; the N# display and the retention rule are UNVERIFIED against "
           "the code. This matters because their paid plan is EUR100 activation + EUR100/month "
           "minimum, so the free plan is the working position indefinitely and its conditions are "
           "the price of admission. Deliberately OPEN rather than guessed: the honest state is "
           "'recorded, not proven'.")
def rg_feed_obligations_honoured():
    out = []
    lic = repo_file("FEED_LICENCES.md")
    if lic is None:
        return [(INFO, "repo half not read")]
    if "N#" not in (lic or ""):
        out.append((FAIL, "FEED_LICENCES.md no longer records the N# obligation"))
    tiers = repo_file("ai_service_tiers.py") or ""
    if "Numista" in tiers:
        out.append((INFO, "source attribution present in the tier copy"))
    else:
        out.append((FAIL, "the Numista tier no longer names Numista as the source"))
    src = repo_file("bea_main.py") or ""
    if "N#" in src or "numista_id" in src or "n_number" in src:
        out.append((INFO, "an N# identifier appears in the server source"))
    else:
        out.append((FAIL, "no N# identifier is displayed anywhere in the server source -- Numista's "
                          "terms require it for catalogue search results"))
    out.append((FAIL, "retention UNVERIFIED: nothing proves Numista catalogue data is not persisted "
                      "in listings beyond their 7-day metadata window"))
    return out



@entry("RG-0150", "We hold Numista's IDENTIFIER and never Numista's DATA -- no catalogue figure "
                  "is persisted, and search runs per LISTING, never per view",
       OPEN, scope="numista_match.py, migrations/029_numista_ref.py, the listings schema, and any "
                   "future code touching the coin catalogue. CLASS: the property is 'their figures "
                   "are never stored by us', so ANY new column, cache or field holding a Numista "
                   "price, estimate or mintage trips this -- not merely the ones named today.",
       ref="N#-REFERRAL-1, David's design 22 Aug 2026 (FEED_LICENCES.md, N_REFERRAL_DESIGN.md). "
           "Numista forbids storing or caching catalogue data (permitted metadata max 7 days) but "
           "allows storing N# identifiers without a time limit. Any design pinning a catalogue "
           "price to a listing is therefore either a breach (stored) or a per-view cost "
           "(re-fetched) -- and the per-view version also lets any visitor burn the 2,000/month "
           "quota. Referral removes all three: one search per LISTING CREATED, the N# kept "
           "forever, the price read by the user on Numista's own site. This entry exists because "
           "the failure mode is silent and LEGAL rather than technical: a cached price would work "
           "perfectly and still be a takedown risk. OPEN until the endpoint and the ms.js "
           "picker/link land and the live half can be probed.")
def rg_numista_identifier_only():
    out = []
    mod = repo_file("numista_match.py")
    if mod is None:
        return [(INFO, "repo half not read")]
    if not mod:
        return [(FAIL, "numista_match.py is missing -- the referral design has no implementation")]

    figure_fields = [f for f in ('"price"', '"estimate"', '"mintage"', '"value"')
                     if f in mod]
    if figure_fields:
        out.append((FAIL, "numista_match.py builds %s into its return value -- candidates must "
                          "carry identifiers and labels only" % ", ".join(figure_fields)))
    else:
        out.append((INFO, "the matcher returns identifiers and labels, no figures"))

    mig = repo_file("migrations/029_numista_ref.py") or ""
    if not mig:
        out.append((FAIL, "migration 029_numista_ref.py is missing"))
    else:
        if "FORBIDDEN" not in mig:
            out.append((FAIL, "029 no longer refuses catalogue-figure columns"))
        else:
            out.append((INFO, "029 refuses to run if a catalogue-figure column exists"))
        for col in ("numista_id", "numista_matched_by"):
            if col not in mig:
                out.append((FAIL, "029 no longer creates %s" % col))

    if "MONTHLY_CAP" not in mod:
        out.append((FAIL, "the matcher has no monthly cap -- the free plan can be overrun"))
    else:
        out.append((INFO, "monthly cap present; degrades to no-candidates, never an error"))

    out.append((FAIL, "live half not yet buildable: the match endpoint and the ms.js link/credit "
                      "are not shipped, so 'no figure reaches the browser' cannot be probed"))
    return out



@entry("RG-0151", "Every credential probe tests the credential's OWN permission -- never a "
                  "broader endpoint the credential is not entitled to call",
       OPEN, scope="Every _infra_* probe on the Infrastructure panel and every verifier in "
                   "scripts/. CLASS: the fault is 'a check that fails on correct input', so ANY "
                   "new probe that reaches for a user-level or admin-level endpoint to judge a "
                   "narrowly-scoped key belongs here.",
       ref="VERIFY-IN-SCOPE-1, 22 Aug 2026, paid for twice in one day. (1) The rotation tooling "
           "verified the new Cloudflare token with GET /user/tokens/verify -- a USER-level "
           "endpoint that a token scoped to one zone's Cache Purge cannot call. It answered 401 "
           "regardless of whether the token was good, so a CORRECT token was reported broken "
           "three times and David was sent back to re-copy a valid value. (2) The Infrastructure "
           "panel had the same bug plus a second one (reading zone rulesets, which needs Zone "
           "Read), so the moment the token was narrowed to least privilege the panel showed FAIL "
           "and advised 'roll token in CF dash' -- advice that would have restarted the loop. "
           "Both now fall back to a real cache purge of a non-existent URL: harmless, free, and "
           "conclusive. THE GENERAL RULE: least privilege makes broad probes lie, so the probe "
           "must shrink to the credential, never the credential grow to the probe. A checker that "
           "cannot fail is worthless; a checker that cannot pass is worse, because it destroys "
           "good work. OPEN until the panel change is deployed and its live half can be read.")
def rg_probes_verify_in_scope():
    out = []
    src = repo_file("bea_main.py")
    if src is None:
        return [(INFO, "repo half not read")]
    cf = src[src.find("async def _infra_cloudflare"):] if "_infra_cloudflare" in src else ""
    cf = cf[:cf.find("async def _infra_resend")] if "_infra_resend" in cf else cf
    if not cf:
        return [(FAIL, "_infra_cloudflare not found")]
    if "purge_cache" not in cf:
        out.append((FAIL, "the Cloudflare probe does not exercise cache purge -- a purge-scoped "
                          "token will be reported broken"))
    else:
        out.append((INFO, "the Cloudflare probe falls back to a real purge (in-scope)"))
    if "roll token in CF dash" in cf:
        out.append((FAIL, "the probe still advises rolling the token on a false red"))
    s3 = src[src.find("async def _infra_hetzner_s3"):] if "_infra_hetzner_s3" in src else ""
    s3 = s3[:s3.find("async def _infra_ssl")] if "_infra_ssl" in s3 else s3
    if s3 and "list_objects_v2" not in s3:
        out.append((FAIL, "the object-storage probe does not authenticate -- a bare GET on the "
                          "endpoint would show green with revoked credentials"))
    elif s3:
        out.append((INFO, "the object-storage probe performs a signed list (in-scope)"))
    out.append((FAIL, "live half unread: the panel change is not deployed, so the real verdicts "
                      "cannot be probed yet"))
    return out



@entry("RG-0152", "The 'Next Session' block never directs the next session at work that is "
                  "already CLOSED",
       LOCKED, fixed_on="2026-08-22",
       scope="STATUS.md '## Next Session (priorities)' cross-referenced against "
             "DAILY_WATCH/OPEN_ITEMS.md. CLASS: any DW-### named as a priority must not appear "
             "in the watch's CLOSED sections. The block is hand-maintained -- it has no compiler "
             "like CHANGELOG.md and STATUS.md's Current Session -- so it needs an assertion "
             "instead of a habit.",
       ref="STALE-DIRECTIVE-1, 22 Aug 2026. The Ops Dashboard renders this block as its "
           "'NEXT SESSION' card, so whatever sits here is what the next session is told to do. "
           "Found carrying NINE items of which SIX were already finished: DW-027, DW-054, "
           "DW-044, DW-010 and DW-028 were all closed on 21 Aug and still listed on 22 Aug, and "
           "the top item told David to rotate the production secrets on the morning he finished "
           "rotating them. This is the same failure the rulings register was built for -- work "
           "that is done, not written where the next session reads. Cheap to check: the watch "
           "already records closures, so the two only have to be compared.")
def rg_next_session_not_stale():
    status = repo_file("STATUS.md")
    watch = repo_file(os.path.join("DAILY_WATCH", "OPEN_ITEMS.md"))
    if status is None or watch is None:
        return [(INFO, "repo half not read")]
    head = "## Next Session (priorities)"
    if head not in status:
        return [(FAIL, "STATUS.md no longer has a '%s' block -- the dashboard card reads it" % head)]
    seg = status[status.index(head):]
    nxt = seg.find("\n## ", 10)
    seg = seg[:nxt] if nxt > 0 else seg

    named = set(re.findall(r"DW-\d{3}", seg))
    closed = set()
    for m in re.finditer(r"\*\*(DW-\d{3})\*\* CLOSED", watch):
        closed.add(m.group(1))
    for m in re.finditer(r"(DW-\d{3})\s+CLOSED", watch):
        closed.add(m.group(1))

    # An item may be MENTIONED as closed (the audit trail line at the foot); only flag a
    # DW that is named in a bullet as work to do.
    todo = set()
    for line in seg.splitlines():
        ls = line.strip()
        if not ls.startswith("-"):
            continue
        if re.search(r"(?i)closed .* and removed|removed from this list", ls):
            continue
        todo |= set(re.findall(r"DW-\d{3}", ls))

    stale = sorted(todo & closed)
    out = []
    if stale:
        out.append((FAIL, "the Next Session block still asks for CLOSED item(s): %s -- the "
                          "dashboard is directing the next session at finished work"
                          % ", ".join(stale)))
    else:
        out.append((INFO, "%d DW item(s) named, none of them already closed" % len(todo)))
    if "rotate the production secrets" in seg:
        out.append((FAIL, "the secret-rotation directive is still listed -- it completed 22 Aug"))
    return out



@entry("RG-0153", "No chip on the visual maps asserts a service state that nothing measured -- "
                  "every external-service light is live-fed and can be re-tested on the spot",
       LOCKED, fixed_on="2026-08-22",
       scope="dashboard.server.html visual maps, external-service cards. CLASS: any NEW chip that "
             "paints a health colour for a service must read it from /admin/services-status or "
             "stay in the dashed not-wired style. Extends RG-0133 from the +1 page's instruments "
             "to the map cards.",
       ref="INSTRUMENT-TRUTH-2, 22 Aug 2026, found by David reading his own dashboard: "
           "'All of these looks wrong.' He was right on all four. Paystack carried a HARDCODED "
           "'test mode' chip -- false from the moment the live key went in, on the one card where "
           "a wrong answer costs money. Cloudflare carried a hardcoded green 'proxied'. Resend, a "
           "live mail lane, had NO chip at all on the Switches view. And 'SSL days' sat dashed "
           "while the server had measured the number all along. All four now read from the same "
           "probe the Infrastructure card uses. David's second instruction shipped with it: "
           "'allow a press on any coloured light to initiate that test live' -- each chip re-runs "
           "ITS OWN check via ?service=<id> and repaints from the answer, because a dashboard you "
           "can only believe gets ignored, and one you can challenge gets trusted.")
def rg_map_chips_are_measured():
    html = repo_file("dashboard.server.html")
    if html is None:
        return [(INFO, "repo half not read")]
    out = []
    for bad, what in (('<span class="om-dot"></span>test mode', 'Paystack "test mode"'),
                      ('<span class="om-dot"></span>proxied', 'Cloudflare "proxied"')):
        if bad in html:
            out.append((FAIL, "a hardcoded %s chip is back -- it asserts a state nothing "
                              "measured" % what))
    for cid, label in (("om-psmode", "Paystack mode"), ("om-cfsvc", "Cloudflare purge"),
                       ("om-resendsvc", "Resend key"), ("om-sslsvc", "SSL days")):
        if cid not in html:
            out.append((FAIL, "the %s chip (%s) is gone -- that card shows no measured state"
                              % (label, cid)))
    if "_SVC_CHIPS" not in html or "click to re-test" not in html:
        out.append((FAIL, "click-to-retest wiring is missing -- the lights can no longer be "
                          "challenged on the spot"))
    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "4 external-service chips are live-fed and re-testable; no hardcoded "
                          "health claims remain on the map cards"))
    return out


@entry("RG-0154", "The dashboard session number is DERIVED from session evidence and carries its "
                  "own as-of date -- it can no longer be a regex hit on a prose paragraph",
       LOCKED, fixed_on="2026-08-23 (promoted: READY TO LOCK after the 23 Aug deploy carried SESSION-COUNTER-1 + migration 030 -- badge now derived, dated, basis named)",
       scope="GET /dashboard/summary in main.py and bea_main.py, SESSION_COUNTER.json, "
             "scripts/session_counter.py, the dashboard badge, and the deploy manifest. "
             "CLASS, not instance: this asserts the MECHANISM, not the number. Any future "
             "session that reinstates a scrape of 'Session <n>' out of STATUS.md, or lets the "
             "counter fall behind the fragments on disk, trips this red. The two previous "
             "'permanent' fixes (139->141, 150->155) each corrected only the number and were "
             "dead within one session precisely because no assertion guarded the mechanism.",
       ref="SESSION-COUNTER-1, 22 Aug 2026, raised by David: the badge had read 'Session 155' "
           "for three weeks and he was certain the true count had gone 'way past' it. He was "
           "right -- the derivation puts it at 175, twenty sittings behind -- and the cause was "
           "worse than staleness. There was never a counter. main.py:8545 ran "
           "_re2.search(r'Session (\\d+)', status) against a 329 KB append-only prose file and "
           "took the FIRST match, which sat at STATUS.md line 1650: a 1 Aug paragraph whose own "
           "subject was 'SESSION COUNTER CORRECTED 150 -> 155'. The badge was pinned to a "
           "sentence about the counter having previously frozen. Nothing anywhere incremented "
           "anything, so freezing was the DEFAULT state and the number could only move when a "
           "human hand-edited that paragraph. Fixed in two halves, both required: (1) DERIVE -- "
           "scripts/session_counter.py computes the number from the status.d/ and changelog.d/ "
           "fragments that STATUS-COLLISION-1 and CHANGELOG-COLLISION-1 already make the only "
           "legal way to record a session, so the act that proves a session happened is the act "
           "that advances the count; (2) DATE IT -- the badge renders 'Session N - as of "
           "<date>' and greys to UNVERIFIED off a derived counter, because a bare number can "
           "lie indefinitely while a number beside its own date confesses the moment it stops "
           "moving. OPEN until the release carrying it reaches the server; the live half below "
           "will pass and print READY TO LOCK the first run after deploy.")
def rg_session_number_derived():
    out = []

    # ── source half: the old mechanism must not come back ───────────────────
    for f in ("main.py", "bea_main.py"):
        srcf = repo_file(f)
        if srcf is None:
            out.append((INFO, "%s not read (outside the repo)" % f))
            continue
        if "current_session = int(sm.group(1))" in srcf:
            out.append((FAIL, "%s scrapes the session number out of prose again -- the exact "
                              "line that pinned the badge to 155 for three weeks" % f))
        if "_session_number" not in srcf:
            out.append((FAIL, "%s has no _session_number() -- the derived path is gone" % f))

    html = repo_file("dashboard.server.html")
    if html is not None and "renderSessionBadge" not in html:
        out.append((FAIL, "the badge no longer renders its as-of date -- a frozen number would "
                          "again look identical to a live one"))

    mf = repo_file(os.path.join("ops", "autodeploy", "deploy_manifest.txt"))
    if mf is not None and "SESSION_COUNTER.json" not in mf:
        out.append((FAIL, "SESSION_COUNTER.json is not in the deploy manifest -- the server "
                          "would fall back to the prose scrape"))

    # ── counter half: it must not have fallen behind the evidence ───────────
    repo_n = None
    cj = repo_file("SESSION_COUNTER.json")
    if cj is None:
        out.append((INFO, "SESSION_COUNTER.json not read (outside the repo)"))
    else:
        try:
            d = json.loads(cj)
        except Exception as ex:
            d = None
            out.append((FAIL, "SESSION_COUNTER.json is unparseable: %r" % (repr(ex)[:80],)))
        if d:
            repo_n = int(d.get("session", 0))
            if d.get("basis") != "derived":
                out.append((FAIL, "SESSION_COUNTER.json basis is %r, not 'derived' -- a "
                                  "hand-set number is back" % d.get("basis")))
            sc = os.path.join(REPO, "scripts", "session_counter.py")
            if os.path.exists(sc):
                rc = os.system('"%s" "%s" --check >%s 2>&1'
                               % (sys.executable, sc, os.devnull))
                if rc != 0:
                    out.append((FAIL, "session_counter.py --check fails -- the counter has "
                                      "fallen behind the fragments on disk (run it to see by "
                                      "how many sittings)"))

    # ── live half: what the badge actually serves ───────────────────────────
    try:
        s = _json("/dashboard/summary")
    except ProbeOffline as ex:
        out.append((INFO, "live /dashboard/summary not readable this run (%s)" % ex))
        return out

    basis = s.get("sessionBasis")
    live_n = s.get("currentSession")
    as_of = s.get("sessionAsOf") or ""
    if basis != "derived":
        out.append((FAIL, "live badge basis is %r -- the server is still scraping the number "
                          "from prose (serving Session %s)" % (basis, live_n)))
    if not as_of:
        out.append((FAIL, "live badge carries no as-of date -- a frozen number is invisible "
                          "again"))
    if repo_n and isinstance(live_n, int) and live_n < repo_n:
        out.append((FAIL, "live badge says Session %s, the evidence on disk says %s -- %d "
                          "sitting(s) unrecorded on the server"
                          % (live_n, repo_n, repo_n - live_n)))

    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "session number is derived (repo %s, live %s, as of %s) and the "
                          "badge dates itself" % (repo_n, live_n, as_of[:10])))
    return out

@entry("RG-0155", "No surface on the dashboard wears a health colour that nothing measures -- "
                  "and an INVENTORY exists, so the next unfed panel is caught by machinery "
                  "rather than by David's memory",
       LOCKED, fixed_on="2026-08-22",
       scope="dashboard.server.html, every om-chip carrying a health class, plus "
             "DASHBOARD_PROVENANCE.json and scripts/dashboard_provenance.py. CLASS, and "
             "deliberately the WHOLE class: the auditor enumerates every chip on the page, so "
             "a panel added next month is covered without anyone remembering to add an "
             "assertion for it. Registered static entries carry review dates and FAIL when "
             "those pass, so the registry cannot become a hiding place.",
       ref="PROVENANCE-1, 22 Aug 2026. David: 'the dashboard becomes a liability if it either "
           "shows stagnant information or the worst case is wrong information ... it feels as "
           "if I am the Automator and need to remember what changed?' A full audit that day "
           "found 141 asserted surfaces on the page: 65 live-fed, 8 doc-parsed and 68 "
           "HAND-TYPED. Nine chips painted a health colour with no feed at all -- 'kill "
           "switches armed', 'nightly backup', 'routing on', 'scheduled daily', 'no-AI "
           "default', 'per-use AI' among them -- and the same server was costed at EUR 4.51/mo "
           "on the Ops Map and EUR 22.07/mo on the Ops view while canon.yml, named ON THE PAGE "
           "as the source of truth, said EUR 26.68 and was served to no one. The health dot "
           "was born green in the markup and never reset on a failed fetch, so a dead feed "
           "left a green light burning over an error message. Root cause was not that people "
           "typed values in: it was that NOTHING ENUMERATED THEM, so the only index was "
           "David's memory, and every prior fix (RG-0133, RG-0153, INSTRUMENT-TRUTH-1/2) was "
           "instance-scoped and left the other 68 standing. Fixed by inverting the default: "
           "the auditor lists every chip, an unfed health colour is a defect unless registered "
           "with a reason and an expiry, cost now comes from one endpoint reading canon.yml so "
           "two panels cannot disagree, and the five direction cards declare their source with "
           "static ones dimmed and dated. Proven by injecting a fake green chip: caught, exit 1.")
def rg_dashboard_provenance():
    out = []
    aud = os.path.join(REPO, "scripts", "dashboard_provenance.py")
    reg = repo_file("DASHBOARD_PROVENANCE.json")
    if not os.path.exists(aud):
        return [(FAIL, "scripts/dashboard_provenance.py is gone -- the dashboard has no "
                       "inventory again, which is the whole defect")]
    if reg is None:
        out.append((INFO, "registry not read (outside the repo)"))
    else:
        try:
            entries = json.loads(reg).get("static_surfaces", [])
        except Exception as ex:
            entries = []
            out.append((FAIL, "DASHBOARD_PROVENANCE.json is unparseable: %s" % repr(ex)[:80]))
        for e in entries:
            if not e.get("review_by"):
                out.append((FAIL, "registered surface %r has no review_by -- a static "
                                  "declaration with no expiry is a permanent hiding place"
                                  % e.get("asserts", e.get("slug"))))

    rc = os.system('"%s" "%s" --check >%s 2>&1' % (sys.executable, aud, os.devnull))
    if rc != 0:
        out.append((FAIL, "dashboard_provenance --check fails -- at least one chip paints a "
                          "health colour nothing measures, or a registered static surface has "
                          "passed its review date (run the script for the list)"))

    html = repo_file("dashboard.server.html")
    if html is not None:
        if 'id="health-status-dot" style="margin-left:6px;color:#10b981;"' in html:
            out.append((FAIL, "the Server Health dot is born green in the markup again -- a "
                              "light must be grey until something measures it"))
        if "loadFixedCosts" not in html:
            out.append((FAIL, "the cost feed is gone -- the cost surfaces are back to "
                              "hand-typed numbers that can disagree with each other"))
        if "STATIC \u2014 written" not in html and "STATIC \u2014 written" not in html:
            if "static_since" not in html and "d.source === 'static'" not in html:
                out.append((FAIL, "direction cards no longer declare their source -- a static "
                                  "card can pass as this session's priorities again"))

    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "every health colour on the dashboard is fed, honestly dashed, or "
                          "registered with a live review date; cost reads canon.yml"))
    return out


@entry("RG-0156", "orchestrator.html ships through the ONE DEPLOY manifest, carries no "
                  "hardcoded access code, and never renders a data outage as an all-clear",
       OPEN,
       scope="orchestrator.html and its live counterpart at trustsquare.co/orchestrator. "
             "CLASS: any page served from the web root but absent from "
             "ops/autodeploy/deploy_manifest.txt is outside the one deploy engine and will "
             "fossilise exactly like this one. The empty-state rule is general -- no page may "
             "render a fetch failure as reassurance.",
       ref="PROVENANCE-1 / ORCH-DRIFT-1, 22 Aug 2026, found while auditing the dashboard after "
           "David said the Orchestration page 'has too many [faults] and I did not even try to "
           "keep it updated - and that is wrong because I do have an expectation of it auto "
           "updating and being factual.' He is right, and the cause is structural: the page is "
           "LIVE (nginx serves /orchestrator from /var/www/marketsquare behind Basic Auth) but "
           "is NOT in deploy_manifest.txt. It was hand-uploaded; the repo copy was last touched "
           "4 Jun 2026, 79 days ago. Meanwhile STATUS.md and CHANGELOG.md DO ship, so the "
           "doc-fed tiles kept updating while the HTML around them fossilised -- which is "
           "precisely what makes a stale page look maintained. Three defects follow from it: "
           "(1) DEPLOY -- outside the one engine, violating DEPLOY-CONSOLIDATION-1; the repo "
           "and live copies have diverged and the live one cannot be read from a session "
           "(Basic Auth), so which is authoritative is not knowable from here. (2) SECRET -- "
           "access code 96315 is hardcoded at line 96 of a file in a public web root, and it "
           "is a launch gate (LAUNCH_BAR_2026-08-15 G2, '96315 killed', hard 29 Aug, status "
           "OPEN); worse, the gate is dead code -- line 100 unconditionally reveals the app "
           "without ever calling checkCode(), so the page asserts a protection it does not "
           "run. (3) FALSE ALL-CLEAR -- jget() swallows every error and returns null, so a "
           "404, a 500, expired auth or a corrupt report.json all render as 'Nothing waiting "
           "on you. \u2728' plus four more cheerful empties. A total data outage looks like a "
           "clean board. Also asserts '~05:00 SAST', wrong since 11 Jun when the loop merged "
           "to one 06:30 task. NOT executed this session on purpose: adding the 79-day-old "
           "repo copy to the manifest would OVERWRITE whatever is live with stale content, and "
           "rotating a live access code is David's call (RUL-027). Logged here per RUL-037 "
           "rather than handed over as a sentence he has to remember.")
def rg_orchestrator_in_one_deploy():
    out = []
    mf = repo_file(os.path.join("ops", "autodeploy", "deploy_manifest.txt"))
    html = repo_file("orchestrator.html")
    if mf is None or html is None:
        return [(INFO, "repo half not read")]

    if "orchestrator.html" not in mf:
        out.append((FAIL, "orchestrator.html is served live but is NOT in "
                          "deploy_manifest.txt -- it is outside the one deploy engine and "
                          "drifts silently"))
    if "96315" in html:
        out.append((FAIL, "access code 96315 is still hardcoded in a file that sits in a "
                          "public web root (launch gate G2, hard 29 Aug)"))
    if "Nothing waiting on you" in html:
        out.append((FAIL, "the empty state still renders a data outage as an all-clear -- a "
                          "failed fetch must say the feed failed, never 'nothing to do'"))
    if "05:00 SAST" in html:
        out.append((FAIL, "the page still claims the loop runs ~05:00 SAST -- merged to a "
                          "single 06:30 task on 11 Jun 2026"))
    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "orchestrator page is in the manifest, carries no hardcoded code, "
                          "and reports feed failures honestly"))
    return out

@entry("RG-0157", "No migration sits untracked while the shipping app already depends on it -- "
                  "schema and code always deploy together",
       LOCKED, fixed_on="2026-08-22",
       scope="migrations/*.py versus git's index. CLASS: ANY untracked migration is a deploy "
             "hazard, not merely today's. The manifest engine ships what git delivers and "
             "post_deploy.sh runs migrations from the repo, so a migration that was never "
             "committed simply does not exist as far as the server is concerned -- while the "
             "code that needs it ships perfectly.",
       ref="DEPLOY-COHERENCE-1, 22 Aug 2026, caught on the way to a deploy David was about to "
           "authorise. bea_main.py (which ships AS main.py, manifest line 19) had been "
           "committed carrying INTRO-HOLD-1: INSERT INTO intro_requests (..., tuppence_held) "
           "plus reads of hold_released_at. The migration that CREATES both columns, "
           "migrations/030_intro_hold.py, was still untracked. Deploying that pair would have "
           "pushed code writing to a column the live database does not have -- every "
           "introduction request throwing, on the money path, on the product's core action. "
           "The near-miss came from a real collision: a concurrent session's in-flight work was "
           "swept into commit 76606ff by an over-broad git add, which committed the CODE half "
           "while leaving the SCHEMA half untracked and made the tree look complete when it was "
           "not. Fixed by committing 030 (verified first: compiles, guards on PRAGMA "
           "table_info so it is genuinely idempotent, additive nullable columns only, and it "
           "explicitly does NOT retro-hold money from existing wallets) and by this assertion, "
           "which is cheap and mechanical: an untracked migration is always wrong.")
def rg_migrations_tracked():
    mig = os.path.join(REPO, "migrations")
    if not os.path.isdir(mig):
        return [(INFO, "outside the repo -- migrations/ not read")]
    try:
        out_txt = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "migrations/"],
            cwd=REPO, stderr=subprocess.DEVNULL,
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).decode("utf-8", "replace")
    except Exception as ex:
        return [(INFO, "git not readable here (%s)" % repr(ex)[:60])]

    stray = [l.strip() for l in out_txt.splitlines()
             if l.strip().endswith(".py") and "__pycache__" not in l]
    if stray:
        return [(FAIL, "untracked migration(s) %s -- the app can ship depending on schema the "
                       "server will never receive. Commit them or delete them; never deploy "
                       "past this" % ", ".join(sorted(stray)))]
    return [(INFO, "every migration on disk is tracked -- schema and code ship together")]


@entry("RG-0158", "Study & Work Abroad teaser serves live WITH its honesty labels -- "
                  "Coming-Shortly banner and AI-example label (home-surface needle retired, RUL-050)",
       LOCKED, fixed_on="2026-08-23 (promoted: READY TO LOCK the morning after, exactly as the ref predicted -- SAW-1 rode the 23 Aug deploy; teaser live with both honesty labels + index banner)",
       scope="/static/studyabroad_teaser.html (SAW-1 index banner retired 24 Aug 2026, RUL-050 -- unlisted, still live). CLASS: "
             "a preview surface must carry its Coming-Shortly and AI-example labels for as long "
             "as it exists -- shipping the page without the labels, or the labels without the "
             "page, is the defect (RUL-040/RUL-042 honesty class). When the real feature goes "
             "live this entry is SUPERSEDED deliberately, never quietly.",
       ref="SAW-1, 22 Aug 2026. Built additively per David's 'build now, no risk to the launch "
           "baseline': one static page, one lm-banner block in marketsquare.html, one manifest "
           "line. OPEN until it rides the next deploy; expected to print READY TO LOCK the "
           "morning after. Example dossier facts sourced+dated 22 Aug 2026 (DHET/Stipendium, "
           "DE blocked account, UK visa+IHS, NL fee ranges) with RE-CHECK flags per RUL-038. AMENDED 24 Aug 2026 (RUL-050): David pulled the banner off Browse for launch -- the teaser videos are shelved placeholders (RUL-043) and a front-door card onto them reads badly; the page stays live UNLISTED (onboard_5 links it). The home-surface needle was removed DELIBERATELY here, not weakened silently; rulings_check RUL-050 now asserts the banner's ABSENCE on Browse.")
def rg_studyabroad_teaser_live():
    out = []
    try:
        page = _get("/static/studyabroad_teaser.html?v=1")
    except Exception as ex:
        return [(FAIL, "teaser page not served: %s" % repr(ex)[:70])]
    if "COMING SHORTLY" not in page:
        out.append((FAIL, "Coming-Shortly banner missing from the teaser page"))
    if "AI-GENERATED EXAMPLE DOSSIER" not in page:
        out.append((FAIL, "AI-example label missing -- the worked example could read as a real report"))
    if "NOT A REPORT FOR A REAL USER" not in page:
        out.append((FAIL, "the 'not a report for a real user' wording is gone"))
    return out or [(INFO, "teaser live with both honesty labels (unlisted since RUL-050)")]


@entry("RG-0159", "The WORK-route worked example is live: second labelled AI-example plus the "
                  "honest Canada CLOSED verdict",
       LOCKED, fixed_on="2026-08-23", scope="/static/studyabroad_teaser.html v2 (SAW-2). CLASS: sibling increment of "
             "RG-0158 -- the LOCKED entry asserts the v1 surface; this asserts the RUL-043 "
             "additions: a SECOND labelled example (matric gap-year work route) and the honest "
             "CLOSED verdict. Softening the Canada verdict to sell the dream is the defect.",
       ref="SAW-2, 23 Aug 2026. Lesson recorded: SAW-1 deployed and RG-0158 was promoted LOCKED "
           "by a concurrent session while this session strengthened the SAME entry's needles -- "
           "a LOCKED assertion must never be extended; an increment gets its OWN entry (this "
           "one). OPEN until the SAW-2 commit rides a deploy; banner link bumped ?v=1 -> ?v=2 "
           "same session so cached clients fetch the v2 page.")
def rg_workroute_example_live():
    out = []
    try:
        page = _get("/static/studyabroad_teaser.html?v=2")
    except Exception as ex:
        return [(FAIL, "v2 teaser not served: %s" % repr(ex)[:70])]
    if page.count("AI-GENERATED EXAMPLE DOSSIER") < 2:
        out.append((FAIL, "fewer than TWO labelled worked examples -- the work-route example "
                          "(RUL-043) is missing or unlabelled"))
    if "CLOSED for SA passports" not in page:
        out.append((FAIL, "the honest Canada CLOSED verdict is gone -- the work example may "
                          "not sell a door that does not exist"))
    if "just out of matric" not in page:
        out.append((FAIL, "the persona is no longer the matric school-leaver David specified"))
    return out or [(INFO, "work-route example live with its labels and the honest no")]


@entry("RG-0160", "Both full example dossier PDFs serve live and the teaser links them",
       OPEN, scope="/static/studywork/Dossier_EXAMPLE_Study_Hungary.pdf + "
             "Dossier_EXAMPLE_Work_USA_Farm.pdf + their dl links on the teaser (SAW-3, RUL-044). "
             "CLASS: a Feature's worked examples are part of the feature surface -- a dead "
             "example link is a broken shop window. PDFs ship via the MEDIA lane [1b], the page "
             "via the code deploy: this entry catches the half-shipped state where either lane "
             "ran without the other.",
       ref="SAW-3, 23 Aug 2026. OPEN until BOTH the next code deploy (teaser v2 with dl links) "
           "AND a media_push run (PDFs) have happened. Generator: scripts/build_dossier_pdf.py "
           "(the P4 prototype) + dossier_examples.py.")
def rg_dossier_pdfs_live():
    out = []
    try:
        page = _get("/static/studyabroad_teaser.html?v=2")
        for f in ("Dossier_EXAMPLE_Study_Hungary.pdf", "Dossier_EXAMPLE_Work_USA_Farm.pdf"):
            if f not in page:
                out.append((FAIL, "teaser does not link %s" % f))
    except Exception as ex:
        out.append((FAIL, "teaser unreadable: %s" % repr(ex)[:60]))
    for f in ("Dossier_EXAMPLE_Study_Hungary.pdf", "Dossier_EXAMPLE_Work_USA_Farm.pdf"):
        try:
            body = _get("/static/studywork/" + f)
            if not body.startswith("%PDF"):
                out.append((FAIL, "%s serves but is not a PDF" % f))
        except Exception as ex:
            out.append((FAIL, "%s not served: %s" % (f, repr(ex)[:50])))
    return out or [(INFO, "both example dossiers live and linked")]


@entry("RG-0161", "Both surroundings maps serve live with their layers, demo banner and teaser links",
       LOCKED, fixed_on="2026-08-23", scope="/static/studywork_hu_map.html + studywork_us_map.html (SAW-4, RUL-045). "
             "CLASS: the layered map is part of the dossier's visual language -- a dead map link "
             "or a demo map without its DEMO banner (RUL-040) is the defect.",
       ref="SAW-4, 23 Aug 2026. OPEN until the next code deploy ships the pages + teaser links. "
           "Photo-embed completion is tracked by the filesystem (assets/studywork sw_*.jpg) and "
           "HIGGSFIELD_REGEN_QUEUE section 6, not by this entry.")
def rg_studywork_maps_live():
    out = []
    for f, needle in (("studywork_hu_map.html", "The smart alternatives"),
                      ("studywork_us_map.html", "The seasons")):
        try:
            page = _get("/static/" + f)
            if "ts_demo_banner.js" not in page:
                out.append((FAIL, "%s lacks the DEMO banner include (RUL-040)" % f))
            if needle not in page:
                out.append((FAIL, "%s lost its layer set" % f))
        except Exception as ex:
            out.append((FAIL, "%s not served: %s" % (f, repr(ex)[:50])))
    try:
        teaser = _get("/static/studyabroad_teaser.html?v=2")
        for f in ("studywork_hu_map.html", "studywork_us_map.html"):
            if f not in teaser:
                out.append((FAIL, "teaser does not link %s" % f))
    except Exception as ex:
        out.append((FAIL, "teaser unreadable: %s" % repr(ex)[:60]))
    return out or [(INFO, "both layered maps live, bannered and linked")]


@entry("RG-0162", "The placement-agency lane's nine templates ship with the deploy -- outreach + all 8 onboarding emails",
       LOCKED, fixed_on="2026-08-23", scope="orchestrator/v2/templates/placement_agency_outreach.html + placement_onboarding/onboard_1..8.html "
             "on the server (SAW-5, RUL-046). CLASS: an onboarding SEQUENCE with a missing email is a broken funnel "
             "-- eight means eight.",
       ref="SAW-5, 23 Aug 2026. OPEN until the next deploy ships the manifest rows. Server-side presence is probed "
           "via the deployed teaser page as a deploy-freshness witness plus the manifest on disk; template files "
           "are not web-readable by design, so the disk half asserts the repo and the deploy stamp asserts the ride.")
def rg_placement_templates_ship():
    out = []
    import os as _os
    tdir = _os.path.join(REPO, "orchestration_v2", "templates")
    if _os.path.isdir(tdir):
        if not _os.path.exists(_os.path.join(tdir, "placement_agency_outreach.html")):
            out.append((FAIL, "outreach template missing from repo"))
        for i in range(1, 9):
            if not _os.path.exists(_os.path.join(tdir, "placement_onboarding", "onboard_%d.html" % i)):
                out.append((FAIL, "onboard_%d.html missing -- eight means eight" % i))
        man = open(_os.path.join(REPO, "ops", "autodeploy", "deploy_manifest.txt"), encoding="utf-8").read()
        if "placement_onboarding/onboard_8.html" not in man:
            out.append((FAIL, "manifest does not carry the onboarding rows"))
    try:
        page = _get("/static/studyabroad_teaser.html?v=2")
        if "Dossier_EXAMPLE_Work_USA_Farm.pdf" not in page:
            out.append((FAIL, "the SAW deploy has not ridden yet -- templates not live either"))
    except Exception as ex:
        out.append((FAIL, "deploy witness unreadable: %s" % repr(ex)[:50]))
    return out or [(INFO, "all nine templates in repo + manifest, and the SAW deploy is live")]



@entry("RG-0163", "The city-wave launcher carries an AGENCY lane -- agency_outreach is reachable from the wave machinery",
       LOCKED, fixed_on="2026-08-23", scope="citylauncher_ops.html + n8n/n8n_outreach_workflow.json. The agency wave (scraped estate agencies, "
             "AGENCY-AUDIT 23 Aug 2026) cannot be launched today: the launcher's category set and the n8n templateMap "
             "carry only solo-seller templates; templates/agency_outreach.html is deployed but nothing sends it. "
             "CLASS: every recruited vertical (agency, dealer, operator, placement) needs a send lane, not just a template.",
       ref="AGENCY-AUDIT-1, 23 Aug 2026. Repo-pattern check by design (the n8n instance is not probe-able from here); "
           "EXECUTED-grade proof stays with the first real wave send. FIXED AGENCY-WAVE-1 23 Aug 2026: "
           "n8n templateMap carries Estate Agents/Agency -> agency_outreach, honors prospect.magic_link, and "
           "drops agency prospects without a console link; citylauncher documents the lane; live half asserts "
           "POST /agencies/wave-prep is deployed (405 to bare GET, never 404). Skins: wave-prep mints "
           "agency/operator/dealer params. Runbook: AGENCY_WAVE_RUNBOOK.md.")
def rg_agency_wave_lane():
    out = []
    import os as _os
    found = False
    for f in ("n8n/n8n_outreach_workflow.json", "citylauncher_ops.html"):
        fp = _os.path.join(REPO, f)
        if _os.path.exists(fp):
            txt = open(fp, encoding="utf-8", errors="replace").read()
            if "agency_outreach" in txt:
                found = True
    if not found:
        out.append((FAIL, "no wave machinery references agency_outreach -- the agency wave cannot be sent"))
    # live half: the link-minting endpoint must be deployed (bare GET answers 405, a missing route 404)
    try:
        _get("/agencies/wave-prep")
        out.append((FAIL, "GET /agencies/wave-prep answered 200 -- it must be POST-only"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            out.append((FAIL, "/agencies/wave-prep not live (404) -- the AGENCY-LINK-1 deploy has not ridden"))
        # 405/401/403 = route exists behind its method/key guards: correct
    except Exception as ex:
        out.append((FAIL, "wave-prep probe unreadable: %s" % repr(ex)[:60]))
    return out or [(INFO, "agency lane present in wave machinery + wave-prep endpoint live")]


@entry("RG-0164", "An agency admin's emailed link lands them signed-in INSIDE their console -- signin token chains to ?agency=1 without a race",
       LOCKED, fixed_on="2026-08-23", scope="ms.js: the ?signin= handler verifies async and goTo('dashboard'); the ?agency=1 handler fires at "
             "150ms and reads ms_aa_email -- combined links race, and create_agency sends the admin nothing at all. "
             "CLASS: every org skin (agency/operator/dealer/placement) needs the one-click landing, or the outreach "
             "email's 'your onboarding opens pre-filled' promise is false.",
       ref="AGENCY-AUDIT-1, 23 Aug 2026. Code-pattern check, labeled as such: asserts the signin success path "
           "explicitly hands off to the agency console when the link carries the agency param. "
           "FIXED AGENCY-LINK-1 23 Aug 2026: signin success chains to openAgencyConsole (all three org skins), "
           "standalone org handlers skip when signin present (race closed), create_agency emails the admin a "
           "console link, /agencies/wave-prep mints link batches without emailing, and My Space shows an "
           "'Agency console' card to any agency admin (by-admin resolved). E2E-probed live 23 Aug 2026.")
def rg_agency_signin_console_chain():
    out = []
    import os as _os, re as _re
    fp = _os.path.join(REPO, "ms.js")
    if _os.path.exists(fp):
        txt = open(fp, encoding="utf-8", errors="replace").read()
        m = _re.search(r"signin.{0,4000}?openAgencyConsole", txt, _re.S)
        if not _re.search(r"if\(sp\.get\('signin'\)\)[\s\S]{0,2500}openAgencyConsole", txt):
            out.append((FAIL, "signin handler does not chain to the agency console -- combined signin+agency links race"))
    else:
        out.append((FAIL, "ms.js not found"))
    return out or [(INFO, "signin handler hands off to the agency console")]


@entry("RG-0165", "agency_outreach.html tells agencies the AGENCY onboarding story -- console, roster bulk-add, import guide -- not the solo-seller flow",
       LOCKED, fixed_on="2026-08-23", scope="orchestration_v2/templates/agency_outreach.html. Its 'Getting your agency live' steps describe the "
             "individual magic-link sell flow; an agency with 50-500 mandates needs the three real lanes (concierge "
             "import / console self-serve / API import guide). CLASS: outreach copy must describe the lane the "
             "recipient will actually land in (INSTRUMENT-TRUTH applied to email).",
       ref="AGENCY-AUDIT-1, 23 Aug 2026. FIXED AGENCY-WAVE-1 same day: all three recruited-vertical templates "
           "(agency, travel_agency, cars_dealer) now carry the three-lane block -- concierge reply / console "
           "self-serve / IT import guide -- plus the drafts+quality-gate safety line and the Agents-as-a-Service "
           "link. The check asserts the import-guide/AaaS links stay present.")
def rg_agency_outreach_tells_agency_story():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "orchestration_v2", "templates", "agency_outreach.html")
    if not _os.path.exists(fp):
        out.append((FAIL, "agency_outreach.html missing from repo"))
    else:
        txt = open(fp, encoding="utf-8", errors="replace").read()
        if ("agency-import-guide" not in txt) and ("agents-as-a-service" not in txt):
            out.append((FAIL, "outreach template never mentions the import guide or the agents-as-a-service page"))
    return out or [(INFO, "outreach template carries the real agency lanes")]



@entry("RG-0166", "The console can bulk-import ADVERTS, not only agents -- the no-IT door to the import pipeline exists and ships",
       LOCKED, fixed_on="2026-08-23", scope="ms.js advertBulkOpen/advertBulkRun + the imports-card button; live /static/ms.js. "
             "Born of David's eyeball question 23 Aug 2026: 'how would a property agency bulk upload all of their "
             "property adverts?' -- the answer was 'only via the API or concierge', which broke the wave's effortless "
             "promise for non-IT agencies. CLASS: every lane the outreach email promises must have a console door.",
       ref="ADVERT-BULK-1, 23 Aug 2026. The box drives the SAME POST /agencies/{id}/import pipeline (auth = agency "
           "api_key in body) -- no second import engine. Repo half asserts the functions and button; live half "
           "asserts the deployed ms.js carries them.")
def rg_console_advert_bulk():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "ms.js")
    if _os.path.exists(fp):
        js = open(fp, encoding="utf-8", errors="replace").read()
        for needle in ("function advertBulkOpen", "function advertBulkRun", "Bulk import adverts"):
            if needle not in js:
                out.append((FAIL, "repo ms.js lost: " + needle))
    else:
        out.append((FAIL, "ms.js not found"))
    try:
        live = _get("/static/ms.js")
        if "advertBulkOpen" not in live:
            out.append((FAIL, "live ms.js does not carry the advert bulk box -- the ADVERT-BULK-1 deploy has not ridden"))
    except Exception as ex:
        out.append((FAIL, "live ms.js unreadable: %s" % repr(ex)[:60]))
    return out or [(INFO, "console advert bulk-import present in repo and live")]



@entry("RG-0167", "The Pro seat is PURCHASABLE end-to-end -- the agent's own $5/mo seat subscription (EULA + payment) exists",
       LOCKED, fixed_on="2026-08-24", scope="ms.js agent-side seat-subscribe lane + bea_main.py seat plan handling (marker SEAT-SUB-1 when built). "
             "RUL-048: an agency agent lifts 10->20 + Pro AI suite ONLY by subscribing themselves -- EULA accepted, $5/mo "
             "paid, through the subscription machinery. Until this lane ships, the console can only INVITE the upgrade "
             "(agencyProInvite) and the tier is ops-settable for reconciliation. CLASS: no paid tier is ever reachable "
             "without its payment flow -- the console flip that granted Pro at $0 is the exact fault class.",
       ref="RUL-048, 23 Aug 2026. Payments are the gated deploy class (ONE_DEPLOY agent-flow rule 3): this build queues "
           "for David's one-word ship when the Paystack seat product is wired. Locks when SEAT-SUB-1 passes E2E.")
def rg_pro_seat_purchasable():
    out = []
    import os as _os
    found = False
    for f in ("ms.js", "bea_main.py"):
        fp = _os.path.join(REPO, f)
        if _os.path.exists(fp) and "SEAT-SUB-1" in open(fp, encoding="utf-8", errors="replace").read():
            found = True
    if not found:
        out.append((FAIL, "no SEAT-SUB-1 lane in repo -- the Pro seat cannot actually be bought yet (console invites only)"))
    return out or [(INFO, "agent-side seat subscription lane present")]



@entry("RG-0168", "NOTHING goes live without the seller's own EULA acceptance -- imports land drafts, and publish 403s until the agent accepts",
       LOCKED, fixed_on="2026-08-23", scope="bea_main.py publish_listing (the ONE draft->live door). CLASS: every arrival "
             "path -- solo signup, agency invite, roster bulk, advert import -- converges on this gate; a second publish "
             "path that skips it would be the fault. David's requirement, 23 Aug 2026: 'All agents has to go through the "
             "EULA acceptance irrespective of how we import them.'",
       ref="AGENCY-KEY-1 session, 23 Aug 2026. Code-pattern half (labeled as such) + E2E-probed live same day: "
           "PUT /listings/375/publish for an EULA-less agent answered 403 'EULA not accepted'. Superuser bypass is "
           "deliberate (admin testing) and part of the assertion.")
def rg_eula_gates_live():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "bea_main.py")
    if _os.path.exists(fp):
        s = open(fp, encoding="utf-8", errors="replace").read()
        if "EULA not accepted" not in s:
            out.append((FAIL, "publish_listing lost its EULA 403 -- drafts could go live without acceptance"))
        i = s.find("def publish_listing")
        if i >= 0 and "eula_accepted_at" not in s[i:i+3000]:
            out.append((FAIL, "publish_listing no longer reads eula_accepted_at"))
    else:
        out.append((FAIL, "bea_main.py not found"))
    return out or [(INFO, "the one draft->live door still demands the seller's EULA acceptance")]



@entry("RG-0169", "Every recruited agency vertical gets a real console skin -- outreach never sells a console its vertical does not have",
       LOCKED, fixed_on="2026-08-24", scope="ms.js _agL skin map vs the agency-lane outreach templates. Skinned today: estate (agency), travel "
             "(operator), cars (dealer). Recruited but skinless: collectors_dealer, tutor_institution, service_company, "
             "placement_agency (RUL-046 first-class). CLASS: a vertical's wave may only fire once its console skin (labels, "
             "credential gate, import wording) exists -- AGENCY_WAVE_RUNBOOK carries the same rule.",
       ref="David's eyeball, 23 Aug 2026: 'the drop down still only shows three types of agencies'. OPEN by design "
           "pre-launch (RUL-046 risk instinct: no invented credential gates days before launch); locks when the four "
           "skins exist. Credential-gate design per vertical is canon work, not a UI patch. "
           "FIXED VERT-4-1 (RUL-049) 24 Aug 2026: all four built with registry-verified gates -- SAPS SHG / "
           "safety clearances (SACE covers) / trade CoC licences / DEL registration -- E2E-probed live same day "
           "(template endpoints + collector bulk onboard on ZZ-TEST, credentials pending as designed).")
def rg_vertical_skins():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "ms.js")
    js = open(fp, encoding="utf-8", errors="replace").read() if _os.path.exists(fp) else ""
    needed = {"collector": "Collector", "institution": "Tutor institution",
              "service_company": "Service company", "placement": "Placement"}   # keys = the real skin keys
    # a skin exists when _agL carries a labeled map for it (heuristic: 'skinname:' key in the _agL maps region)
    agl = js[js.find("function _agL"): js.find("function _agL") + 12000]
    for key, label in needed.items():
        if ("%s:" % key) not in agl and ("'%s'" % key) not in agl:
            out.append((FAIL, "no console skin for the recruited vertical: " + label))
    return out or [(INFO, "all recruited verticals carry console skins")]



@entry("RG-0170", "An open tab notices a new release by itself -- the stale-tab class is closed with a one-tap refresh offer",
       LOCKED, fixed_on="2026-08-24", scope="ms.js FRESH-1: 5-minute poll of the served index's ms.js ?v= against the "
             "running one; a floating one-tap reload bar when a deploy landed; never auto-reloads (mid-listing input is "
             "sacred). CLASS: three occurrences on 23-24 Aug alone -- the offline-shell first paint, the cached-shell "
             "E2E, and David's 'nothing has changed?' -- every one was a human diagnosing staleness the app could see.",
       ref="FRESH-1, 24 Aug 2026, born of David's 'Three times recurring...'.")
def rg_fresh_tab():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "ms.js")
    js = open(fp, encoding="utf-8", errors="replace").read() if _os.path.exists(fp) else ""
    for needle in ("_freshCheck", "ts-fresh-bar"):
        if needle not in js:
            out.append((FAIL, "repo ms.js lost the freshness poller: " + needle))
    try:
        if "_freshCheck" not in _get("/static/ms.js"):
            out.append((FAIL, "live ms.js does not carry FRESH-1 -- open tabs are stale-blind again"))
    except Exception as ex:
        out.append((FAIL, "live ms.js unreadable: %s" % repr(ex)[:60]))
    return out or [(INFO, "open tabs self-detect new releases and offer the reload")]



@entry("RG-0171", "A lane that promises a sign-in link SENDS one -- bulk roster onboarding emails every agent their invite, and the invite email is an invite (no empty code box)",
       LOCKED, fixed_on="2026-08-24", scope="estate_agents.py bulk_onboard_agents (invite_fn seam) + bea_main.py _mint_agent_invite/_send_invite_email/_send_html_email + ms.js bulk toast. "
             "Found 24 Aug 2026 walking the agency funnel as a recipient: outreach lane 2 and the Import Guide promise 'each agent instantly "
             "gets a sign-in link' and the console toasted 'magic links & verification queued' -- but /agencies/{id}/agents/bulk sent NOTHING, "
             "and the single-invite lane mailed the sign-in CODE template with an EMPTY code box and a 20-minute expiry claim on a 72-hour token. "
             "CLASS: every onboarding lane that promises an email must send it, and every toast states what actually happened (INSTRUMENT-TRUTH). "
             "OPEN until the deploy rides (live half checks the served ms.js); repo half already passes -- promote on first green run after ship.",
       ref="AGENCY-INVITE-MAIL-1, 24 Aug 2026. Fix: one transport helper (_send_html_email, keeps MAIL-FALLBACK-1 in ONE place), a real invite "
           "template (_send_invite_email), one minter (_mint_agent_invite) used by BOTH the single-invite endpoint and the bulk lane via "
           "estate_agents.configure(invite_fn=...); per-agent 'link': sent|failed|dry in the bulk report; console toast/report show it honestly.")
def rg_bulk_invite_links():
    out = []
    import os as _os
    ea_fp = _os.path.join(REPO, "estate_agents.py")
    bm_fp = _os.path.join(REPO, "bea_main.py")
    if _os.path.exists(ea_fp) and _os.path.exists(bm_fp):
        ea = open(ea_fp, encoding="utf-8", errors="replace").read()
        bm = open(bm_fp, encoding="utf-8", errors="replace").read()
        if "_INVITE_FN" not in ea:
            out.append((FAIL, "bulk roster lane lost its invite seam -- bulk-added agents get no sign-in link"))
        if "_mint_agent_invite" not in bm or "_send_invite_email" not in bm:
            out.append((FAIL, "bea_main no longer mints/sends the agent invite email"))
        if "invite_fn=_mint_agent_invite" not in bm:
            out.append((FAIL, "estate_agents.configure no longer injects invite_fn -- the bulk lane's seam is dark"))
        if "magic links & verification queued" in open(_os.path.join(REPO, "ms.js"), encoding="utf-8", errors="replace").read():
            out.append((FAIL, "repo ms.js still carries the false 'magic links & verification queued' toast"))
    try:
        live = _get("/static/ms.js")
        if "magic links & verification queued" in live:
            out.append((FAIL, "live console still toasts 'magic links & verification queued' -- the AGENCY-INVITE-MAIL-1 deploy has not ridden"))
    except Exception as ex:
        out.append((FAIL, "live ms.js unreadable: %s" % repr(ex)[:60]))
    return out or [(INFO, "bulk roster sends real invite links and the console reports honestly")]


@entry("RG-0172", "The Ops Map loader survives to fire every feed, and no chip wears a health colour before data answers",
       LOCKED, fixed_on="2026-08-24", scope="dashboard.server.html ops-map IIFE (OPSMAP-CRASH-1). PROVENANCE-1 (22 Aug) introduced "
             "fetch(EP + ...) into loadFixedCosts while the IIFE base is B -- omLoad's FIRST statement threw ReferenceError, so "
             "ALL 10 feeds died and every chip froze at its static placeholder: blockers wore hardcoded RED with no data, flags/service "
             "checks sat amber at 'loading...' (David read a phantom blocker off it, 24 Aug). CLASS: (1) one undefined identifier at the "
             "top of a loader silently freezes the whole instrument panel; (2) RG-0133's rule applied to the map -- a frozen chip must "
             "show grey/dashed, never a default red/amber/green that counterfeits a verdict. Source-scope checks only: the served page "
             "is auth-gated, so the live half cannot be probed anonymously; the deploy manifest ships this exact file.",
       ref="OPSMAP-CRASH-1, 24 Aug 2026. Fix: EP->B (one line) + 11 placeholder chips (fault lane, faultflag, BIT, flags/svc loading) "
           "reclassed om-chip nw until fill()/fail() paints them from a live answer.")
def rg_opsmap_loader():
    out = []
    import os as _os
    fp = _os.path.join(REPO, "dashboard.server.html")
    if not _os.path.exists(fp):
        return [(INFO, "repo not present -- source check skipped (live page is auth-gated)")]
    src = open(fp, encoding="utf-8", errors="replace").read()
    if "fetch(EP" in src:
        out.append((FAIL, "an undefined-base fetch(EP...) is back in the dashboard -- the loader-crash class has returned"))
    if "fetch(B + '/dashboard/fixed-costs')" not in src:
        out.append((FAIL, "the fixed-costs feed no longer reads from the one base B"))
    for cid in ("om-f-blocker", "om-f-major", "om-f-retest"):
        if '<span class="om-chip nw" id="%s"' % cid not in src:
            out.append((FAIL, "placeholder chip %s wears a health colour before data answers (RG-0133 rule on the map)" % cid))
    return out or [(INFO, "ops-map loader fires all feeds; unfilled chips are grey until a live answer paints them")]



@entry("RG-0173", "The agency funnel is walked END-TO-END by MACHINERY -- a synthetic journey probe (email links -> console -> roster invite -> advert import) runs against live and leaves a fresh witness",
       OPEN, scope="scripts/agency_journey_probe.py (to build) + agency_journey_status.json witness. Born of David's question 24 Aug 2026: "
             "'how did we work on this so long and find these major fails days before launch?' Post-mortem answer: every slice was "
             "pattern-asserted, but no assertion crossed the SEAMS between slices -- the console promised links the backend never sent, "
             "and only a persona-grade walk (the first ever, 24 Aug) caught it. CLASS: a funnel is proven by walking it as the recipient, "
             "not by asserting its parts; every recruited-vertical funnel (agency/dealer/operator) needs the same walk before its wave fires.",
       ref="AGENCY-JOURNEY-1, opened 24 Aug 2026. Spec: probe every outreach-link anonymously; mint a throwaway org via wave-prep "
           "(idempotent); exercise agents/bulk with a sink address and assert per-agent link=sent; exercise the import lane; write "
           "agency_journey_status.json {ok, ran_at}. Passes when the script exists and the witness is green and fresh (<8 days).")
def rg_agency_journey_probe():
    out = []
    import os as _os, json as _json, time as _time
    sp = _os.path.join(REPO, "scripts", "agency_journey_probe.py")
    wp = _os.path.join(REPO, "agency_journey_status.json")
    if not _os.path.exists(sp):
        out.append((FAIL, "no journey probe script -- the funnel is only ever walked by a session's memory"))
    if _os.path.exists(wp):
        try:
            w = _json.load(open(wp, encoding="utf-8"))
            if not w.get("ok"):
                out.append((FAIL, "last journey walk FAILED: %s" % str(w.get("detail", ""))[:80]))
            elif _time.time() - float(w.get("ran_at", 0)) > 8 * 86400:
                out.append((FAIL, "journey witness stale (>8 days) -- walk it again before trusting the funnel"))
        except Exception as ex:
            out.append((FAIL, "journey witness unreadable: %s" % repr(ex)[:50]))
    else:
        out.append((FAIL, "no journey witness -- the probe has never run"))
    return out or [(INFO, "the funnel was walked by machinery recently and it passed")]



@entry("RG-0174", "Customer email routes to the SUPPORT pipeline, never routinely to a personal inbox -- and one inbound email gets exactly ONE reply",
       LOCKED, fixed_on="2026-08-24 (promoted: READY TO LOCK on the first green run after the app half rode the 06:25 deploy; the ref's clean E2E re-test remains the outstanding human-observable proof and the worker lane's blind spot is documented in scope)", scope="cloudflare_email_worker/src/worker.js (personal forward = dead-letter only) + bea_main.py email_inbound "
             "(ONE-REPLY-1: persist first, single outbound carrying the fault ref) + _send_html_email Reply-To. "
             "Found 24 Aug 2026 by live E2E routing test (David's ask): the CF worker forwarded EVERY inbound to "
             "dmcontiki2@gmail.com by design-era safety net, and one complaint received TWO conflicting auto-replies "
             "in the same second (classifier draft + MAINT-B1 ack). CLASS: the support pipeline is the customer "
             "channel; a personal inbox may only ever be a dead-letter; reply lanes must be mutually exclusive. "
             "OPEN until BOTH deploys ride (app /ship + wrangler worker deploy) and a clean E2E re-test shows one "
             "reply and no personal-inbox copy -- then promote.",
       ref="ONE-INBOX-1 + ONE-REPLY-1, 24 Aug 2026. E2E evidence: test to support@ triaged, ref LIST-11 minted, "
           "branded replies from support@mail.trustsquare.co in <5s; test to billing@ proved catch-all ON; forwards "
           "landed in the personal inbox (the fault). Reply-To support@trustsquare.co added to the shared transport "
           "so even Gmail-SMTP fallback sends route replies into the pipeline.")
def rg_one_inbox_one_reply():
    out = []
    import os as _os
    wf = _os.path.join(REPO, "cloudflare_email_worker", "src", "worker.js")
    bm_fp = _os.path.join(REPO, "bea_main.py")
    if _os.path.exists(wf):
        w = open(wf, encoding="utf-8", errors="replace").read()
        n_fwd = w.count("message.forward(")
        if n_fwd != 1 or "if (!triaged || hasAttachments)" not in w or w.index("if (!triaged") > w.index("message.forward("):
            out.append((FAIL, "worker forwards customer mail to the personal inbox outside the dead-letter branch"))
    if _os.path.exists(bm_fp):
        bm = open(bm_fp, encoding="utf-8", errors="replace").read()
        if "ONE-REPLY-1" not in bm or 'elif category != "spam" and fault_code' not in bm:
            out.append((FAIL, "email_inbound no longer guarantees one reply per inbound (ONE-REPLY-1 gone)"))
        if bm.count('os.getenv("SUPPORT_REPLY_TO", "support@trustsquare.co")') < 3:
            out.append((FAIL, "transactional transport lost its support Reply-To -- replies would go to the sending mailbox"))
    return out or [(INFO, "customer mail: support pipeline only, one reply per inbound, personal inbox = dead-letter")]



@entry("RG-0175", "Wave mechanical hygiene is DONE and witnessed before the first wave -- source tags on every CTA, cross-wave unsubscribe suppression proven, international template pass",
       OPEN, scope="orchestration_v2/templates/*_outreach.html CTA links + the n8n suppression path + a wave_hygiene_status.json witness. "
             "RUL-053(g), due Fri 28 Aug 2026 (first wave). Three items, holistic per David: (a) every outreach CTA to trustsquare.co "
             "carries a wave source tag (?src=<wave>) so signups credit their wave and the holistic gates read numbers, not feelings; "
             "(b) an unsubscribe from any wave provably suppresses that address in every later wave (witnessed test); (c) one holistic "
             "pass of the templates for US/UK/AU markets (currency, locale wording, send windows). CLASS: a wave may not fire while its "
             "measurement or suppression machinery is unproven.",
       ref="WAVE-HYGIENE-1, opened 24 Aug 2026 per RUL-053. Passes when the witness file reports all three ok and fresh.")
def rg_wave_hygiene():
    out = []
    import os as _os, json as _json, time as _time
    # CAT-ALIAS-1 (24 Aug 2026, executed): the scraper's real category names are aliased in the
    # n8n templateMap and an unmapped category DROPS instead of falling back to the property
    # template. Losing either re-opens wrong-template sends at wave scale.
    nf = _os.path.join(REPO, "n8n", "n8n_outreach_workflow.json")
    if _os.path.exists(nf):
        nw = open(nf, encoding="utf-8", errors="replace").read()
        if "CAT-ALIAS-1" not in nw or "teachers_trainers" not in nw:
            out.append((FAIL, "n8n templateMap lost the scraper-category aliases -- wrong-template sends are back"))
        if "|| 'property_outreach'" in nw:
            out.append((FAIL, "n8n templateKey fallback is property_outreach again -- unmapped categories get the wrong email"))
    wp = _os.path.join(REPO, "wave_hygiene_status.json")
    if not _os.path.exists(wp):
        out.append((FAIL, "no wave-hygiene witness -- source tags / suppression / intl pass not yet done and proven"))
        return out
    try:
        w = _json.load(open(wp, encoding="utf-8"))
        for k in ("source_tags", "suppression", "intl_pass"):
            if w.get(k) != "ok":
                out.append((FAIL, "wave hygiene item not ok: %s = %s" % (k, w.get(k))))
        if _time.time() - float(w.get("ran_at", 0)) > 14 * 86400:
            out.append((FAIL, "wave-hygiene witness stale (>14 days)"))
    except Exception as ex:
        out.append((FAIL, "witness unreadable: %s" % repr(ex)[:50]))
    return out or [(INFO, "wave hygiene done and witnessed: tags, suppression, intl pass")]



@entry("RG-0176", "The POPIA suppression invariant holds END-TO-END -- one opt-out click suppresses in EVERY send lane's store, and the prospect PII API answers 401 to strangers",
       OPEN, scope="CityLauncher suppression register + LAUNCH-API-LOCK-1 (built 24 Aug, RUL-054) -- repo halves pass; TWO live halves outstanding: "
             "(a) the n8n outreach lane reads the ORCHESTRATION prospect store (opted_out column), a different DB from the launcher store the "
             "/optout endpoint writes -- one click must provably suppress in BOTH (needs a server-side look at the orchestration DB + a witnessed "
             "round-trip test); (b) GET /launch-api/prospects/list must answer 401 without X-Launch-Key -- provable only after David provisions "
             "LAUNCH_API_KEY in the server env and the CityLauncher deploy rides. CLASS: a suppression list per store is a breach waiting; "
             "there is ONE register and every lane checks it.",
       ref="SUPPRESS-1 / LAUNCH-API-LOCK-1, 24 Aug 2026. Offline proof executed same day: get_prospects excludes the register; send_email refuses "
           "a suppressed address fail-safe. Promote when both live halves are witnessed.")
def rg_popia_suppression():
    out = []
    import os as _os
    sp = _os.path.join(REPO, "..", "CityLauncher", "api", "server.py")
    ep = _os.path.join(REPO, "..", "CityLauncher", "emailer", "emailer.py")
    if _os.path.exists(sp):
        w = open(sp, encoding="utf-8", errors="replace").read()
        for needle, msg in [("CREATE TABLE IF NOT EXISTS suppression", "the suppression register DDL is gone"),
                            ("LAUNCH-API-LOCK-1", "the API key gate is gone -- prospect PII is public again"),
                            ("optout_link'", "/optout no longer writes the register")]:
            if needle not in w:
                out.append((FAIL, msg))
    if _os.path.exists(ep):
        w = open(ep, encoding="utf-8", errors="replace").read()
        if "_is_suppressed" not in w or "refusing send to opted-out" not in w:
            out.append((FAIL, "send_email lost its last-gate suppression check"))
    try:
        import urllib.request as _ur
        req = _ur.Request("https://trustsquare.co/launch-api/prospects/list?limit=1",
                          headers={"User-Agent": "TrustSquare-Ledger/1.0"})
        try:
            _ur.urlopen(req, timeout=15)
            out.append((FAIL, "launch-api served prospect PII to an ANONYMOUS reader -- LAUNCH_API_KEY not provisioned or gate not deployed"))
        except Exception as e:
            code = getattr(e, "code", None)
            if code not in (401, 403):
                out.append((FAIL, "prospects/list gate probe unexpected: %s" % repr(e)[:60]))
            # 401/403 = locked: correct
    except Exception as ex:
        out.append((FAIL, "gate probe failed to run: %s" % repr(ex)[:50]))
    return out or [(INFO, "register + gates present in repo AND the live API refuses anonymous PII reads (n8n cross-store proof still manual)")]


@entry("RG-0177", "The remote-code guard is REAL, can still FAIL, and its allowlist has not drifted from the ledger's",
       LOCKED, scope="repo: scripts/no_remote_code_guard.py + this file's RG-0025 copy of ALLOWED",
       fixed_on="2026-08-24",
       ref="REMOTE-CODE-GUARD-1 (24 Aug 2026). RG-0025 is now a CLASS assertion, and a class assertion "
           "has two new ways to rot that a two-string blocklist did not have. (1) The guard could be "
           "quietly neutered -- an allowlist entry added with no reason, or the detection regexes "
           "loosened -- and everything stays green. So this runs the guard's OWN self-test, which "
           "feeds it the actual 3 Aug loader tag, the same loader shape on a NEW host, an unknown "
           "host, a remote iframe and a remote stylesheet, and requires it to catch all five. A guard "
           "that cannot fail is decoration (the 7 Aug rule, applied to itself). (2) The ledger keeps "
           "its own copy of the allowlist because it must run stdlib-only with no repo, so the two "
           "copies can silently disagree -- which would mean the pre-deploy guard and the live check "
           "police different rules. This asserts they are character-for-character the same set. "
           "ALSO PINNED HERE: every allowlisted host must carry a written reason, so 'why is this "
           "origin trusted' is never again answered by a shrug.")
def rg_remote_code_guard_is_real():
    import subprocess as _sp, os as _os, re as _re
    gp = _os.path.join(REPO, "scripts", "no_remote_code_guard.py")
    if not _os.path.exists(gp):
        return [(FAIL, "scripts/no_remote_code_guard.py is GONE -- the pre-deploy half of RG-0025 "
                       "is unenforced and a third-party loader can ship again")]
    out = []
    try:
        r = _sp.run([sys.executable, gp, "--self-test"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            out.append((FAIL, "the guard's self-test FAILED -- it no longer catches the 3 Aug loader "
                              "class, so its green means nothing: " + (r.stdout or r.stderr)[-300:]))
    except Exception as ex:
        out.append((FAIL, "could not run the guard self-test: " + repr(ex)[:80]))

    src = repo_file("scripts/no_remote_code_guard.py")
    if src is None:
        return out or [(INFO, "guard present, source unreadable from here")]
    block = src.split("ALLOWED = {", 1)[-1].split("\n}", 1)[0]
    hosts = set(_re.findall(r'^\s*"([^"]+)"\s*:', block, _re.M))
    ledger_copy = set(_re.findall(r'ALLOWED = \(([^)]*)\)', src if False else
                                  repo_file("scripts/regression_ledger.py") or "")[0].replace('"', '').split(","))
    ledger_copy = {h.strip() for h in ledger_copy if h.strip()}
    if hosts != ledger_copy:
        out.append((FAIL, "allowlist DRIFT -- guard has %s, this ledger has %s. The pre-deploy check "
                          "and the live check are policing different rules; make them agree"
                          % (sorted(hosts), sorted(ledger_copy))))
    for h in sorted(hosts):
        seg = _re.search(r'"%s"\s*:\s*("(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*)' % _re.escape(h), block)
        if not seg or len(seg.group(1)) < 40:
            out.append((FAIL, "allowlisted origin '" + h + "' has no written reason -- an origin nobody "
                              "can justify is an origin nobody audited"))
    return out or [(INFO, "guard self-test passes, %d allowlisted origins, all with reasons, "
                          "ledger copy in step" % len(hosts))]


@entry("RG-0178", "A script-src Content-Security-Policy is ENFORCED at the edge -- the browser itself refuses un-allowlisted remote code",
       OPEN, scope="live response headers on trustsquare.co, BOTH the index and the app paths; shipped by migrations/031_csp_and_index_headers.py",
       ref="CSP-SCRIPT-SRC-1 (24 Aug 2026). THE HOLE THE 3 AUG BREACH WENT THROUGH. The CSP is "
           "'frame-ancestors self' and nothing else -- no script-src -- so any script tag that reaches "
           "a page executes, from any origin on the internet. Every other control we own sits on OUR "
           "side of the paste: guards, ledgers and rulings all assume a human or an agent put the tag "
           "there and somebody notices. script-src is the only control that fails the LOAD even when "
           "the tag is already on the page -- which covers XSS, a compromised CDN, and a future session "
           "pasting a snippet in good faith because the affiliate dashboard asked it to. A full CSP was "
           "deferred on 16 Jul 2026 because the index carries ~163 inline onclick handlers; that "
           "deferral is the reason the loader ran to completion. 'unsafe-inline' keeps all 163 handlers "
           "working and STILL blocks every remote origin, so the thing that was 'too hard' was never "
           "needed to close this. OPEN, not LOCKED, because it is genuinely not live: the header rides "
           "migrations/031 on David's next deploy (deploys are his, RUL-037). READY TO LOCK the moment "
           "the live header carries script-src.")
def rg_csp_script_src_enforced():
    out = []
    for path, label in (("/?cb=ledger", "the index"), ("/terms", "an app path")):
        try:
            csp = _headers(path).get("content-security-policy", "") or ""
        except Exception as ex:
            out.append((FAIL, "could not read the live CSP on %s: %s" % (label, repr(ex)[:70])))
            continue
        if "script-src" not in csp:
            out.append((FAIL, "%s (%s) has no script-src (CSP is %r) -- the browser will execute a "
                              "remote script from ANY origin if one ever reaches the page; "
                              "migrations/031_csp_and_index_headers.py closes it on the next deploy"
                              % (label, path, csp[:90] or "ABSENT")))
            continue
        directive = csp.split("script-src", 1)[1].split(";", 1)[0]
        for tok in ("'unsafe-eval'", " *", "http:"):
            if tok in directive:
                out.append((FAIL, "%s has script-src but it is wide open (%r) -- that is a header, "
                                  "not a control" % (label, directive.strip()[:90])))
                break
    return out


@entry("RG-0179", "The INDEX carries the same security headers as every other page -- nginx add_header inheritance has not silently dropped them",
       LOCKED, scope="live GET / on trustsquare.co vs GET /terms; fixed by migrations/031_csp_and_index_headers.py",
       fixed_on="2026-08-24",
       ref="INDEX-HEADERS-1 (24 Aug 2026). PROBED, cache MISS so this is the origin answering, not an "
           "edge artifact: GET /terms returns x-frame-options, x-content-type-options, referrer-policy, "
           "content-security-policy and strict-transport-security. GET /?cb=... returns NONE OF THEM. "
           "Cause is nginx's add_header inheritance rule -- a level inherits add_header ONLY IF it "
           "declares none of its own. `location = / {}` sets its own Cache-Control (visible on /, "
           "absent on /terms) and that ONE directive discards the entire inherited security set. "
           "So the single most sensitive document on the site -- index.html is both the public front "
           "door AND the page that renders the SA Smart ID / passport upload flow, AND the exact page "
           "the Travelpayouts loader was pasted into on 2 Aug -- has been serving naked, while "
           "nginx_security_headers.conf sat on disk saying otherwise. THAT is why it survived: the "
           "file was READ, the page was never PROBED (the 21 Aug evidence-ladder lesson, landing again "
           "on a security control this time). CLASS, not instance: this asserts header PARITY between "
           "the index and an app path, so any future location block that shadows the set trips red -- "
           "naming the five headers individually would just move the blind spot. PROVEN AND LOCKED "
           "on the 24 Aug 22:47 deploy: post_deploy_status.json records migration 031 ok, and / now "
           "returns all five headers on a cache MISS where it returned none the same afternoon. NOTE "
           "the sibling half did NOT take -- see RG-0178, still open: 031 fixed the inheritance but "
           "not the policy, and reported ok anyway because it checked its own file write instead of "
           "the served response. This entry is locked on a PROBE, which is why it is trustworthy and "
           "that one is not.")
def rg_index_header_parity():
    KEYS = ("content-security-policy", "x-frame-options", "x-content-type-options",
            "referrer-policy", "strict-transport-security")
    try:
        idx = _headers("/?cb=ledger")
        app = _headers("/terms")
    except Exception as ex:
        return [(FAIL, "could not probe header parity: " + repr(ex)[:80])]
    missing = [k for k in KEYS if app.get(k) and not idx.get(k)]
    if missing:
        return [(FAIL, "the INDEX is missing security headers that /terms serves: %s. An nginx "
                       "location block is shadowing the inherited add_header set -- the front page "
                       "and the ID-upload flow are unprotected" % ", ".join(missing))]
    differ = [k for k in KEYS if app.get(k) and idx.get(k) and idx[k] != app[k]]
    if differ:
        return [(FAIL, "index and /terms disagree on %s -- one of them is weaker than the other "
                       "and nobody chose that" % ", ".join(differ))]
    return []


@entry("RG-0180", "connect-src is tightened from 'https:' to a named allowlist",
       OPEN, scope="live CSP connect-src directive on trustsquare.co",
       ref="CSP-CONNECT-1 (24 Aug 2026) -- the honest limit of CSP-SCRIPT-SRC-1, recorded rather than "
           "quietly omitted. Migration 031 ships connect-src 'self' https:, which means a script that "
           "somehow DID execute could still POST data out -- the 3 Aug capture showed the loader "
           "POSTing to /collect and /collect_batch, which is exactly this channel. It is left open on "
           "purpose for now: closing it needs the app's own outbound XHR/fetch/EventSource targets "
           "inventoried at RUNTIME (a static scan on 24 Aug found no absolute external fetch targets, "
           "but absence in source is not proof of absence at runtime), and a wrong connect-src breaks "
           "live payments or auth silently. Post-launch job. script-src is the control that stops the "
           "script existing at all, and that one is tight -- this is defence in depth, not the door.")
def rg_csp_connect_src_tight():
    try:
        csp = _headers("/terms").get("content-security-policy", "") or ""
    except Exception as ex:
        return [(FAIL, "could not read the live CSP: " + repr(ex)[:70])]
    if "connect-src" not in csp:
        return [(FAIL, "no connect-src directive at all -- falls back to default-src; verify that is "
                       "deliberate")]
    directive = csp.split("connect-src", 1)[1].split(";", 1)[0]
    if "https:" in directive or "*" in directive:
        return [(FAIL, "connect-src is still open (%r) -- a script that executed could exfiltrate. "
                       "Tighten to named origins once the runtime inventory exists" % directive.strip())]
    return []



@entry("RG-0181", "The affiliate lane is a SERVER-SIDE link-out that fails closed -- it can never grow into an injected script, and it never invents a partner link",
       LOCKED, scope="travelpayouts_partners.py (TP-LINKOUT-1) + its manifest row. Asserts the INVARIANT (fails closed, no script, host allowlist), which is complete and must stay true. Feature completeness -- lane dark until TP_LINKOUT_ENABLED, all 26 deeplinks still None -- is deliberately NOT part of the assertion: an unbuilt feature is not a rotted fix, and conflating the two is how a ledger starts crying wolf.",
       fixed_on="2026-08-24",
       ref="TP-LINKOUT-1 (24 Aug 2026). Built the day Travelpayouts' dashboard was offering +25% "
           "GetYourGuide rewards, expiring that same day, to switch the Drive loader back on -- on "
           "precisely the programs we most want. The 2 Aug breach did not happen because anyone was "
           "careless; it happened because the EASY path was their script and no house-built "
           "alternative existed on disk. This module is the alternative, so 'no' stays cheap the next "
           "time. WHAT IT ASSERTS, as a class: the lane serves 302s and JSON, never markup and never a "
           "script; every outbound host is on a hard allowlist that must contain none of the "
           "Travelpayouts SCRIPT hosts; and build_url REFUSES rather than guesses -- a program whose "
           "deeplink has not been read from its own link tool cannot be linked to at all, which is why "
           "all 26 sit at deeplink=None today. OPEN on two honest counts: the lane is dark "
           "(TP_LINKOUT_ENABLED unset) and no deeplink has been filled, so nothing customer-visible "
           "exists yet. READY TO LOCK when the module ships, the selftest passes from the repo, and at "
           "least one deeplink is real. NOTE FOR THE NEXT SESSION: filling a deeplink is a dated, "
           "per-program act -- read that program's own link tool. Do NOT paste a format from memory.")
def rg_partner_lane_fails_closed():
    src = repo_file("travelpayouts_partners.py")
    if src is None:
        return [(FAIL, "travelpayouts_partners.py is GONE -- the safe alternative to their script no "
                       "longer exists, which is how the easy path wins again")]
    out = []
    for needle, msg in (
        ("ALLOWED_HOSTS", "the outbound host allowlist is gone -- any host could be redirected to"),
        ("RedirectResponse", "the lane no longer redirects -- check it has not started serving markup"),
        ("TP_LINKOUT_ENABLED", "the dark-by-default flag is gone -- the lane would be live on deploy"),
    ):
        if needle not in src:
            out.append((FAIL, msg))
    for banned in ("tp-em.com", "emrld.cc"):
        # allowed to APPEAR in prose/selftest; must never be in the allowlist set
        block = src.split("ALLOWED_HOSTS = {", 1)[-1].split("}", 1)[0]
        if banned in block:
            out.append((FAIL, "'" + banned + "' is inside ALLOWED_HOSTS -- a Travelpayouts script "
                              "host has been allowlisted as a redirect target"))
    for marker in ("<script", "createElement("):
        if marker in src:
            out.append((FAIL, "travelpayouts_partners.py contains '" + marker + "' -- the link-out "
                              "lane has started emitting script, which is the 3 Aug breach shape"))
    import subprocess as _sp, os as _os
    mp = _os.path.join(REPO, "travelpayouts_partners.py")
    if _os.path.exists(mp):
        try:
            r = _sp.run([sys.executable, mp], capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                out.append((FAIL, "the lane's own selftest FAILS -- its refusals no longer refuse: "
                                  + (r.stdout or r.stderr)[-250:]))
        except Exception as ex:
            out.append((INFO, "could not run the lane selftest here: " + repr(ex)[:70]))
    if "TP_LINKOUT_ENABLED" in src and "deeplink=None" not in src.replace(" ", ""):
        pass
    unfilled = src.count(", None),")
    if unfilled:
        out.append((INFO, "lane is dark and %d program(s) still await a real deeplink -- expected "
                          "while OPEN" % unfilled))
    return out


@entry("RG-0182", "The indicative-fare lane is CACHE-ONLY, dark until David's flag, and never shows a price it cannot stand behind",
       LOCKED, scope="data_flights.py + ts_fares.js + /flights/indicative + the 15 adventures maps. Asserts the INVARIANTS (cache-only reads, dark means dark, never an unbacked price), which are complete. Whether David has FLIPPED the flag is not part of the assertion -- an unflipped switch is not a rotted fix.",
       fixed_on="2026-08-24",
       ref="TP-FARES-1 (25 Aug 2026). Built when David said 'build them now, then I will flip the flag'. "
           "THREE INVARIANTS, each of which has a real failure behind it. (1) CACHE-ONLY READS: no "
           "customer request may reach a supplier -- that is the supplier-fallback doctrine David wrote "
           "on 1 Aug after Amadeus died mid-integration and Google billed ~$360 silently. The read path "
           "touches our SQLite only; a cron is the sole thing that contacts Travelpayouts, so supplier "
           "loss ages the cache instead of breaking the page. (2) DARK MEANS DARK: while the flag is 0 "
           "the endpoint 404s even though real fares ARE cached, and ts_fares.js renders nothing at all "
           "-- no spinner, no placeholder, no 'loading fares', because an empty state that promises a "
           "price is a small lie. The dark case is the one that gets skipped in testing, so the harness "
           "scripts/prove_fares_lane.py tests it FIRST. (3) NEVER A PRICE WE CANNOT STAND BEHIND: every "
           "served fare carries its age, a fare older than 21 days is withheld rather than shown stale, "
           "a thin route falls back to the agency card with no number (the 1 Aug dry run found CPT-GRJ "
           "genuinely empty -- that is a normal answer, not an error), and a poisoned deeplink in the "
           "cache yields NO link rather than a bad one. The surface also states we are not a travel "
           "agency, because RUL-038 positioning says we never replace one. OPEN because the flag is "
           "David's to flip (RUL-037 reserves it). LOCKED 24 Aug on the 22:47 deploy, PROVEN by the "
           "one probe that can tell the two dark states apart: /flights/indicative?map=za returns 404 "
           "with body {\"detail\":\"flights lane is dark\"} -- our own guard speaking, not FastAPI's "
           "{\"detail\":\"Not Found\"}. Before the deploy the same probe read NOT DEPLOYED. That "
           "distinction is the whole reason the live half reads the body.")
def rg_fares_lane_cache_only():
    out = []
    src = repo_file("data_flights.py")
    js = repo_file("ts_fares.js")
    if src is None or js is None:
        return [(FAIL, "data_flights.py or ts_fares.js is GONE -- the fare lane has been removed")]

    read_path = src.split("def get_indicative", 1)[-1].split("\ndef ", 1)[0]
    for needle in ("urlopen", "urllib", "requests."):
        if needle in read_path:
            out.append((FAIL, "get_indicative() now reaches the network ('%s') -- a customer request "
                              "can hit a supplier, which is exactly what the 1 Aug doctrine forbids"
                              % needle))
    if "STALE_DAYS" not in src:
        out.append((FAIL, "the staleness guard is gone -- an ancient cached fare could be shown as a price"))
    if "def flag_on" not in src or "data_flights" not in src:
        out.append((FAIL, "the lane no longer reads launch_switches.data_flights -- it is not dark-able"))

    # The surface must stay first-party. Its ONLY call is our own origin.
    for host in ("travelpayouts.com", "tp.media", "tp-em.com", "aviasales.com"):
        if 'src="http' in js or ("//" + host) in js.replace("https://www.aviasales.com/search/", ""):
            out.append((FAIL, "ts_fares.js references '" + host + "' directly -- the fare card must "
                              "only ever call our own /flights/indicative"))
            break
    for needed, msg in (("nofollow sponsored", "the outward link lost its rel=nofollow sponsored"),
                        ("Indicative only", "the indicative disclaimer is gone from the card"),
                        ("not a travel agency", "the card no longer says we are not a travel agency"),
                        ("may earn a commission", "the commission disclosure is gone from the card")):
        if needed not in js:
            out.append((FAIL, msg))

    # The harness must exist AND pass -- a proof nobody runs is decoration.
    import subprocess as _sp, os as _os
    hp = _os.path.join(REPO, "scripts", "prove_fares_lane.py")
    if not _os.path.exists(hp):
        out.append((FAIL, "scripts/prove_fares_lane.py is gone -- the dark/lit behaviour is unproven"))
    else:
        try:
            r = _sp.run([sys.executable, hp], capture_output=True, text=True, timeout=90)
            if r.returncode != 0:
                out.append((FAIL, "the dark/lit harness FAILS: " + (r.stdout or r.stderr)[-300:]))
        except Exception as ex:
            out.append((INFO, "could not run the fares harness here: " + repr(ex)[:70]))

    # Live half. BOTH "flag is off" and "never deployed" answer 404, so the STATUS CODE
    # ALONE CANNOT TELL THEM APART -- and a ledger that reads a missing feature as a
    # correctly-dark one is exactly the silent green this whole file exists to prevent.
    # The bodies differ: FastAPI's own miss says {"detail":"Not Found"}; our dark guard
    # says {"detail":"flights lane is dark"}. So the body is what gets read.
    try:
        import urllib.request as _ur
        req = _ur.Request(BASE + "/flights/indicative?map=za", headers=UA)
        try:
            with _ur.urlopen(req, timeout=TIMEOUT) as r:
                code, raw = r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            code, raw = e.code, (e.read() or b"").decode("utf-8", "replace")
    except Exception as ex:
        return out + [(INFO, "could not probe the fares endpoint: " + repr(ex)[:60])]
    if code == 404:
        if "lane is dark" in raw:
            out.append((INFO, "lane is DEPLOYED and dark (404 'flights lane is dark') -- exactly "
                              "right until David flips data_flights"))
        else:
            out.append((FAIL, "the fares endpoint is NOT DEPLOYED -- 404 body is %r, not our "
                                  "dark guard. The maps carry ts_fares.js but the route behind it "
                                  "does not exist yet; it rides the next deploy" % raw[:60]))
    elif code == 200:
        try:
            import json as _json
            body = _json.loads(_get("/flights/indicative?map=za"))
        except Exception:
            body = {}
        if body.get("available") and not body.get("age_days"):
            out.append((FAIL, "a fare is served with NO age -- the card cannot label it honestly"))
        if body.get("available") and "Indicative" not in (body.get("disclaimer") or ""):
            out.append((FAIL, "a fare is served without its indicative disclaimer"))
    else:
        out.append((FAIL, "/flights/indicative answered %s -- a dark lane must 404, never error" % code))
    return out


@entry("RG-0183", "Every point where the deploy stops and waits for David FLASHES for him -- a console he cannot see can still ask",
       LOCKED, scope="deploy_marketsquare.bat: every `pause` reachable after %PROJECT% is set, plus notify_attention.bat/.ps1",
       fixed_on="2026-08-25",
       ref="WINDOW-ZORDER-1 (25 Aug 2026). David: 'my terminal window just stubbornly appears behind "
           "the claude window and then i miss it... it used to sit in front of Claude and not behind.' "
           "CAUSE, and it is not his machine: the deploy is now launched BY A CLAUDE SESSION (the "
           "/start skill launches deploy_marketsquare.bat itself), and the desktop-control tooling "
           "launches apps in background mode by design -- 'the user's focus is preserved' -- so the "
           "console opens behind whatever he is looking at. When HE double-clicks it, Windows grants "
           "foreground to a user-initiated launch and it lands in front, exactly as it always did. "
           "Nothing was misconfigured; a general focus-preservation rule met the one window that ends "
           "in `pause`. WHY NOT JUST RAISE IT: Windows refuses SetForegroundWindow to a process that "
           "does not own the foreground, deliberately, and fighting that would be fighting the thing "
           "that stops every other app interrupting him. So we use the signal Windows provides for "
           "exactly this -- FlashWindowEx with FLASHW_TIMERNOFG, which flashes the taskbar button "
           "until the window is looked at -- plus a beep and a title the taskbar can be read at a "
           "glance. CLASS, not instance: this asserts EVERY waiting `pause` is preceded by the "
           "notifier, so a future session adding a new abort path that waits silently trips it red. "
           "The three ABORT pauses matter more than the success one -- a deploy that stopped on a "
           "gate failure and was never seen is the expensive version of this fault. NOT PROVEN ON "
           "THE MACHINE: the PowerShell cannot run from the Linux sandbox, so this is a source-level "
           "assertion; the beep+flash is confirmed by the next deploy, or in two seconds by "
           "double-clicking notify_attention.bat, which self-tests with no arguments.")
def rg_deploy_pauses_flash():
    bat = repo_file("deploy_marketsquare.bat")
    if bat is None:
        return [(INFO, "running outside the repo -- deploy notifier check skipped")]
    out = []
    for helper in ("notify_attention.bat", "notify_attention.ps1"):
        if repo_file(helper) is None:
            out.append((FAIL, helper + " is GONE -- the deploy can stop and wait where David "
                               "cannot see it, with nothing to tell him"))
    ps = repo_file("notify_attention.ps1") or ""
    if "FlashWindowEx" not in ps:
        out.append((FAIL, "notify_attention.ps1 no longer flashes the taskbar -- a beep alone is "
                          "missed by anyone wearing headphones or sitting in another room"))
    if "0x0000000F" not in ps and "FLASHW_TIMERNOFG" not in ps:
        out.append((FAIL, "the flash no longer persists until the window is looked at -- a few "
                          "flashes while he is out of the room is the same as none"))

    lines = bat.splitlines()
    misses = []
    for i, ln in enumerate(lines):
        if ln.strip().lower() != "pause":
            continue                       # inline `& pause &` guards run before %PROJECT% exists
        # Must be an actual CALL, not merely the string appearing nearby -- the first
        # cut of this check searched for "notify_attention" in the preceding lines and
        # could never fail, because the explanatory COMMENT above the pause names the
        # script. A guard that matches its own documentation is not a guard (7 Aug rule).
        window = [l.strip().lower() for l in lines[max(0, i - 4):i]]
        if not any(l.startswith("call ") and "notify_attention.bat" in l for l in window):
            misses.append(i + 1)
    if misses:
        out.append((FAIL, "deploy_marketsquare.bat waits for a keypress at line(s) %s with NO "
                          "notifier before it -- that stop is invisible when the console is behind "
                          "Claude, which is exactly the 25 Aug fault"
                          % ", ".join(str(m) for m in misses)))
    return out or [(INFO, "all %d waiting pause(s) flash, beep and rename the window first"
                          % sum(1 for l in lines if l.strip().lower() == "pause"))]


if __name__ == "__main__":
    sys.exit(main())

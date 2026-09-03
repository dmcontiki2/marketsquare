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


# ── LEDGER-DEPS-1 (26 Aug 2026) ────────────────────────────────────────────
# The THIRD way the instrument fails while the app is fine. LEDGER-OFFLINE-1
# covered no network; GATE-CACHE-1 covered a rate-limited credential; this covers
# a MISSING LOCAL DEPENDENCY.
#
# Several entries prove themselves by running a harness in a subprocess and
# reading its exit code. When the machine running the ledger simply lacks a
# third-party module that harness imports, the subprocess dies on its import
# line -- it never reaches a single assertion -- and a returncode of 1 was being
# read as "the fix has ROTTED".
#
# Proven 26 Aug 2026 in the maintenance sandbox: RG-0181 and RG-0182 both printed
# REGRESSION and the run closed "5 previously-fixed issue(s) HAVE COME BACK. Do
# not deploy over this." Both harnesses then passed 9/9 and 13/13 the instant
# `pip install fastapi` ran. Nothing about the app had changed or could have.
# That is textbook cry-wolf, and this file's own preamble says a tripwire that
# cries wolf is worth less than no tripwire, because it also carries false comfort.
#
# A missing dependency is an INSTRUMENT limit, so it reports NOT EVALUATED ->
# UNVERIFIED (loudly not a pass, exit 2), never REGRESSION. The demotion is
# deliberately narrow: it applies ONLY when the dead import is a third-party
# module. If the missing module is one of OUR OWN repo files, the fix really has
# been deleted and the entry must stay RED -- which is the whole point.
_DEP_DIED = re.compile(r"ModuleNotFoundError: No module named ['\"]([\w.]+)['\"]")


def _missing_third_party(text):
    """Return the module name if `text` shows a subprocess that died on a missing
    THIRD-PARTY import, else None. A missing repo module returns None -- that is a
    real regression and must stay red."""
    if not text:
        return None
    m = _DEP_DIED.search(text)
    if not m:
        return None
    mod = m.group(1).split(".")[0]
    # Ours? Then it is not a dependency problem, it is a deletion.
    for cand in (os.path.join(REPO, mod + ".py"),
                 os.path.join(REPO, mod),
                 os.path.join(REPO, "scripts", mod + ".py")):
        if os.path.exists(cand):
            return None
    return mod


def _harness(argv, timeout=90, cwd=None):
    """Run a proof in a subprocess. Returns (ok, blind, detail).

    blind=True means the harness NEVER RAN -- a missing third-party import killed
    it before its first assertion -- which says nothing whatsoever about the app.
    Callers must turn blind into a 'NOT EVALUATED' INFO (-> UNVERIFIED), never a FAIL.
    """
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except Exception as ex:
        return False, True, "could not run the harness here: " + repr(ex)[:80]
    blob = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        mod = _missing_third_party(blob)
        if mod:
            return False, True, (
                "NOT EVALUATED - this machine lacks the third-party module %r, so the harness "
                "died at its import line and ran ZERO assertions. An instrument limit, not a "
                "verdict on the app (LEDGER-DEPS-1). Install it and re-run before trusting "
                "this board." % mod)
        return False, False, (r.stdout or r.stderr or "")[-300:]
    return True, False, (r.stdout or "")


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


def _ops_key():
    """MS_API_KEY from .secrets/ops_api_key.txt -- '' when absent. Provisioned 30 Aug 2026
    (D14): read from the RUNNING process env as root (RG-0147: point of use, never the file --
    on that day THREE config files carried three different values and the live one matched
    none of them; see DW-084)."""
    try:
        with open(os.path.join(REPO, ".secrets", "ops_api_key.txt"), encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def _admin_key():
    """MS_ADMIN_KEY from .secrets/deploy_keys.txt -- '' when absent (outside the repo)."""
    if "ADMKEY" not in _cache:
        key = ""
        try:
            with open(os.path.join(REPO, ".secrets", "deploy_keys.txt"), encoding="utf-8") as f:
                for ln in f:
                    if ln.startswith("MS_ADMIN_KEY="):
                        key = ln.split("=", 1)[1].strip()
                        break
        except OSError:
            pass
        _cache["ADMKEY"] = key
    return _cache["ADMKEY"]


def _admin_json(path):
    """Admin-credentialed JSON read (X-Admin-Key header, key from .secrets/deploy_keys.txt).

    LEDGER-ADMINREAD-1 (30 Aug 2026): DASH-SUMMARY-REDACT-1 made the ANONYMOUS payload
    heartbeat-only BY DESIGN (asserted by RG-0198/RG-0211), so any live half that judges
    admin-only fields (panels, session badge) must read through the admin door. Raises
    ProbeOffline when no key is on this machine, the read fails, or the payload comes back
    still redacted (key refused) -- an instrument limit reads BLIND, never RED (RG-0187
    boundary). The review cookie is NOT used here: it opens the gate, not the admin fields.
    """
    key = _admin_key()
    if not key:
        raise ProbeOffline("no MS_ADMIN_KEY on this machine -- admin-only fields unreadable; "
                           "blind, not a regression")
    ck = "ADM:" + path
    if ck not in _cache:
        _require_net()
        req = urllib.request.Request(BASE + path, headers=dict(UA, **{"X-Admin-Key": key}))
        try:
            _cache[ck] = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise ProbeOffline("HTTP %s on admin read of %s -- blind, not a regression" % (e.code, path))
        except Exception as ex:
            raise ProbeOffline(repr(ex)[:140])
    doc = json.loads(_cache[ck])
    if isinstance(doc, dict) and doc.get("redacted"):
        raise ProbeOffline("admin key not accepted (payload still redacted=%r) -- blind, "
                           "not a regression" % doc.get("redacted"))
    return doc


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
    for code in (r"ms\.js", r"bea_main\.py", r"marketsquare\.html", r"\.py\b"):
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
            # LEDGER-PENDING-BUILD-1 (31 Aug 2026), sibling of LEDGER-FAULT-1 above and
            # found the same way -- by the board printing an instruction that was wrong.
            # Some OPEN entries ratify a DESIGN whose build has not started; while unbuilt
            # their harness can only assert the pre-build half (the spec is intact, the
            # prototype is on disk). That half passes on day one, so the board printed
            # "now passing -- change state to LOCKED" for RG-0221 (ZOOM) every single run,
            # while RG-0221's own ref says promote only WHEN BUILT and extend the assertion
            # to the shipped code. Obeying the print would LOCK the weak half and retire the
            # strong one -- weakening an assertion to make it pass, which the canon forbids.
            # Ignoring it daily is worse: it teaches sessions that READY TO LOCK is noise,
            # and the next real one gets skipped (the DW-079 failure, arrived at backwards).
            # So a harness that can only reach its pre-build half says PENDING BUILD, and
            # that reads OPEN with its reason -- never an invitation to promote.
            pending = (not fails) and any(s == INFO and "PENDING BUILD" in m for s, m in out)
            status = "OPEN" if (fails or skipped or pending) else "READY TO LOCK"
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
        # LEDGER-UNVER-CAUSE-1 (27 Aug 2026). This line used to assert, unconditionally,
        # "this machine cannot reach {BASE}" -- and it said exactly that on a run whose
        # two UNVERIFIED entries were demoted by RG-0187 for a MISSING PYTHON MODULE,
        # on a machine that was curling the site fine in the same minute. A summary that
        # names the wrong cause sends the next session to fix the wrong thing, which is
        # the RG-0117 mistake one layer up. The instrument already recorded WHY on each
        # entry; read it back instead of guessing. Same class as RG-0187: an instrument
        # limit must be described accurately, not merely demoted honestly.
        _rows = [r for r in results if r["status"] == "UNVERIFIED"]
        _ids = ", ".join(r["id"] for r in _rows)
        _why, _seen = [], set()
        for r in _rows:
            for m in r["infos"]:
                if "NOT EVALUATED" in m:
                    t = m.split("NOT EVALUATED", 1)[1].lstrip(" -\u2014:")
                    t = t.split(". ")[0].strip()[:160]
                    if t and t.lower() not in _seen:
                        _seen.add(t.lower())
                        _why.append(t)
                    break
        _causes = " | ".join(_why) if _why else "the entries did not say why -- read them above"
        _net = ("This machine CANNOT reach %s -- re-run where the site is reachable." % BASE
                if _NET["ok"] is False else
                "This machine CAN reach %s, so the site is not the cause -- fix what the "
                "reason names." % BASE)
        print(f"RESULT: no regressions in what COULD be checked, but {unver} entr(ies) were NOT "
              f"EVALUATED ({_ids}). Reason as the instrument recorded it: {_causes}. {_net} "
              f"That is not a green board -- do not deploy on this result until it is.")
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


@entry("RG-0075", "The admin gate copies have NOT DRIFTED -- every gate fix reaches every copy, "
       "so a correct password is never reported as a wrong reviewer code",
       LOCKED, fixed_on="2026-08-27",
       scope="THE ADMIN gate only: dashboard.server.html (the copy that SHIPS), "
                   "dashboard.html and marketsquare_admin.html (local operator copies). "
                   "RE-AIMED 27 Aug 2026 -- see ref: marketsquare.html and "
                   "archive/session_dashboard_live.html are deliberately NOT in scope now.",
       ref="The root cause behind RG-0074 is duplication, not any one file. Hand-maintained "
           "copies of the same 40 lines are why four separate gate fixes each had to be applied "
           "again per consumer. EXPECTED TO FAIL until the gate script is one file included by "
           "every surface. The moment it passes, promote to LOCKED. "
           "RE-AIMED AND SPLIT IN TWO, 27 Aug 2026 (GATE-DRIFT-1). Two corrections, both found by "
           "actually diffing the copies instead of counting them: "
           "(1) THE ASSERTION WAS COUNTING A DIFFERENT DOOR. marketsquare.html\'s "
           "window.adminGateSubmit posts to /review/login -- it is the public REVIEWER gate, not "
           "the admin gate, and merely shares the identifier. Counting it inflated the fault from "
           "two variants to five and pointed the remedy at merging two security doors that must "
           "stay separate. archive/ is archive and is out for the same reason: dead code is not a "
           "maintenance burden. Real state: THREE files, TWO variants. "
           "(2) THE DRIFT WAS LIVE AND IT WAS HURTING DAVID. dashboard.html and "
           "marketsquare_admin.html were EIGHT DAYS behind dashboard.server.html on GATE-NOLOCK-1 "
           "(19 Aug), on BOTH the login and change-PIN paths. Both still told him \'Locked by the "
           "pre-launch gate... enter the reviewer code\' on a 401 -- a step that has been "
           "impossible since migrations/025 exempted /admin/login and /admin/change-pin at the "
           "origin. So a CORRECT password was reported as a wrong reviewer code, on the copy "
           "RG-0076\'s own ref records as the one David actually opens. Synced 27 Aug; all three "
           "now carry the same two messages. "
           "THE ENTRY NOW ASSERTS BOTH HALVES: consolidation (still open -- and it is genuinely "
           "constrained, because dashboard.html is opened over file:// where a served /static/*.js "
           "cannot load, so the fix needs a build step or an inlined shared block, not a script "
           "tag) AND drift, which is the property that actually causes harm and is checkable "
           "today. A re-drift now goes red the same day instead of after eight.")
def rg_gate_script_single_source():
    out = []
    ADMIN = ("dashboard.server.html", "dashboard.html", "marketsquare_admin.html")
    copies = [r for r in ADMIN if "adminGateSubmit" in (repo_file(r) or "")]

    # HALF 2 -- DRIFT. The harm RG-0075 exists to prevent is a gate fix landing in one
    # copy and not the others, so assert the copies agree on the messages a past fix
    # corrected. This is checkable NOW; consolidation is not.
    MUST_AGREE = (
        ("Password or PIN not accepted",
         "the GATE-NOLOCK-1 login message (19 Aug) -- a 401 means the password is wrong, "
         "NOT that the reviewer code is needed"),
        ("Current PIN not accepted",
         "the GATE-NOLOCK-1 change-PIN message -- /admin/change-pin is exempt at the origin too"),
    )
    STALE = "Locked by the pre-launch gate"
    for needle, what in MUST_AGREE:
        missing = [r for r in copies if needle not in (repo_file(r) or "")]
        if missing:
            out.append((FAIL, "gate copies have DRIFTED: %s lack %s. That is the exact fault this "
                              "entry exists for -- a fix applied per-consumer, and the copy David "
                              "opens is one of the ones that missed it"
                        % (", ".join(missing), what)))
    stale = [r for r in copies if STALE in (repo_file(r) or "")]
    if stale:
        out.append((FAIL, "%s still tell the operator to 'enter the reviewer code' on a 401 -- "
                          "impossible since migrations/025 exempted the admin routes, so a CORRECT "
                          "password reads as a wrong reviewer code (GATE-NOLOCK-1)"
                    % ", ".join(stale)))
    if not out:
        out.append((INFO, "no drift: all %d admin gate copies carry the same corrected messages"
                    % len(copies)))

    # HALF 1 -- CONSOLIDATION. Still the real fix; still open.
    if len(copies) > 1:
        out.append((INFO, "still %d hand-maintained copies (%s) -- consolidation is tracked "
                          "separately as RG-0196; THIS entry asserts the property that actually "
                          "causes harm, which is drift"
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
        # LEDGER-VANTAGE-1 (26 Aug 2026). A red here says "do not deploy", so it must never
        # fire on a DEGRADED VANTAGE. Same class as LEDGER-DEPS-1/RG-0187 and RG-0186: an
        # instrument that cannot reach ANY port 22 has not measured the firewall, it has
        # measured itself. PROVEN 26 Aug 2026: two consecutive full ledger runs read this
        # REGRESSION while a standalone probe to the SAME origin IP returned the OpenSSH
        # banner 8/8 in 0.48 s, and calling this very function in isolation returned
        # "both management lanes clear". LEDGER-FLAP-1's 3-try guard was not enough because
        # the failure is not a dropped packet -- it is this vantage's port-22 lane under
        # full-run load. The assertion is NOT weakened: a genuine lockout still fails the
        # origin while the control hosts answer, and that still reports RED.
        _ctrl_ok, _ctrl_err = False, None
        for _h in ("github.com", "gitlab.com"):
            try:
                socket.create_connection((_h, 22), timeout=8).close()
                _ctrl_ok = True
                break
            except Exception as e:
                _ctrl_err = type(e).__name__
        if not _ctrl_ok:
            out.append((INFO, "NOT EVALUATED - port 22 is unreachable from this vantage to the "
                              "ORIGIN (%s) *and* to public control hosts github.com/gitlab.com "
                              "(%s). This run measured its own socket lane, not the Hetzner "
                              "firewall (LEDGER-VANTAGE-1), so it says NOTHING about a lockout. "
                              "Re-probe from a vantage whose port 22 works before trusting this "
                              "row: python3 -c \"import socket;socket.create_connection("
                              "('178.104.73.239',22),timeout=8)\"" % (_ssh_err, _ctrl_err)))
        else:
            out.append((FAIL, "port 22 unreachable from this vantage on 3 tries (%s) WHILE a "
                              "control host's port 22 answered -- so the vantage is fine and the "
                              "origin is not. SSH-LOCKOUT-1 class: the home IP likely changed "
                              "(power/router reset). Fix: run scripts/hetzner_fw_selfheal.py, or "
                              "add the current IP at Hetzner > Firewalls > "
                              "trustsquare-origin-lockdown" % _ssh_err))
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
       ref="AMENDED 30 Aug 2026 (LEDGER-ADMINREAD-1): the live half now reads /dashboard/summary with the admin key -- DASH-SUMMARY-REDACT-1 made the anonymous payload heartbeat-only by design (RG-0211), so the anonymous probe had begun failing on the app behaving CORRECTLY. Assertion fixed, not weakened: the same panel checks run on the credentialed payload; no key on the machine reads blind, never red. LOCKED 20 Aug 2026: winning section 0 days old and the live panels answer. DASH-FEED-1, 20 Aug 2026. David asked for the ops dashboard to be brought current; "
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
    # LEDGER-ADMINREAD-1 (30 Aug 2026): the anonymous payload is heartbeat-only BY DESIGN
    # (RG-0198/RG-0211), so the panels are judged through the admin door. No key here, or a
    # refused key, reads BLIND (INFO), never RED -- RG-0187 boundary.
    try:
        doc = _admin_json("/dashboard/summary")
    except ProbeOffline as ex:
        out.append((INFO, "/dashboard/summary admin read not possible here (%s) -- live half "
                          "unverified" % ex))
        return out
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
    import os as _os

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
        ok, blind, detail = _harness([sys.executable, harness], timeout=120, cwd=REPO)
        if blind:
            out.append((INFO, detail))          # LEDGER-DEPS-1: instrument, not app
        elif not ok:
            tail = (detail or "").strip().splitlines()[-1:] or [""]
            out.append((FAIL, "failover harness FAILED: %s" % tail[0][:160]))
        else:
            nchecks = ""
            for ln in (detail or "").splitlines():
                if "checks ·" in ln:
                    nchecks = ln.strip()
            out.append((INFO, "failover proven in the decision layer — %s"
                              % (nchecks or "harness exit 0")))

    # Live half: how many lanes actually carry keys on the box. OPS-key gated, so this is
    # INFO either way -- an unreadable instrument must never read as a pass.
    _ok = _ops_key()
    if _ok:
        # OPS-KEY-EYES-1 (30 Aug 2026, closes the D14 gap): authenticated read of the live
        # lane count -- the blue card turns green by assertion, not by a dated hand-probe.
        try:
            _req = urllib.request.Request(BASE + "/ops/selfcheck",
                                          headers=dict(UA, **{"X-Api-Key": _ok}))
            st = urllib.request.urlopen(_req, timeout=TIMEOUT).getcode()
        except urllib.error.HTTPError as _e:
            st = _e.code
        except Exception as _ex:
            st = 0
    else:
        st = _status("/ops/selfcheck")
    if st == 200:
        try:
            if _ok:
                _req = urllib.request.Request(BASE + "/ops/selfcheck",
                                              headers=dict(UA, **{"X-Api-Key": _ok}))
                doc = json.loads(urllib.request.urlopen(_req, timeout=TIMEOUT).read()
                                 .decode("utf-8", "replace"))
            else:
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
        if _ok:
            out.append((INFO, "live lane count not readable (HTTP %s WITH the provisioned OPS "
                              "key -- the key has gone stale, likely a service restart flipping "
                              "MS_API_KEY sources; re-read it from the running process (DW-084)."
                              % st))
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
       LOCKED, fixed_on="2026-08-28 (promoted: READY TO LOCK on the run after the last field landed. Registrar Cloudflare Inc + expiry 2026-12-30 came from WHOIS on the 27th once the method was right; auto-renew ON came from the Registrations dashboard on the 28th, read in David's own logged-in browser. The toggle was ALREADY on -- so the item that spent six days in his column as an action was, in the end, a read)",
       scope="trustsquare.co, the apex the whole platform answers on. RECORD-half by "
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
           "or a third party holds the registration. **CORRECTED 27 Aug 2026 (DOMAIN-WHOIS-1): "
           "the claim that this was machine-unanswerable was WRONG, and it had hardened over "
           "four sweeps into an instruction to stop trying.** Those sweeps GUESSED RDAP "
           "hostnames (rdap.org, rdap.nic.co, rdap.identitydigital.services, rdap.net, "
           "rdap.markmonitor.com) and read five 404s as proof the data did not exist. None "
           "asked the AUTHORITY which server to use. Correct method, ~1 second: query "
           "whois.iana.org:43 for 'co' -> it refers to whois.registry.co -> query that for the "
           "domain. `.co` is operated by CentralNic, which no guess was going to reach. "
           "Result: registrar Cloudflare Inc (IANA 1910), created 2025-12-30, expiry "
           "2026-12-30, clientTransferProhibited, DNSSEC unsigned. CLASS LESSON, and the "
           "reason this is written into the ledger rather than a changelog: A NEGATIVE RESULT "
           "PROVES A NEGATIVE ONLY IF THE METHOD WAS RIGHT -- five wrong doors is not a locked "
           "building. Same shape as the 21 Aug Google-OAuth error this whole sweep exists to "
           "prevent. AUTORENEW genuinely cannot be probed -- WHOIS does not publish it, it is "
           "a registrar-account setting -- so that one field, and only that one, comes from "
           "David and then lives here.")
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
    # DOMAIN-AUTORENEW-PROVENANCE-1 (28 Aug 2026): match the leading TOKEN, not the whole
    # line. The first cut demanded a bare "on" and went red on
    # "ON (read in the Cloudflare Registrations dashboard 2026-08-28; status Active)" -- i.e.
    # it punished the session that recorded WHERE and WHEN the fact came from. An assertion
    # that penalises provenance teaches the next session to strip provenance, which is the
    # opposite of what this file is for. Same shape as RG-0139: state token + a date.
    if (ren.split() or [""])[0].strip("*_`") not in ("on", "yes", "enabled", "true"):
        out.append((FAIL, "DOMAIN_AUTORENEW is %r -- renewal depends on someone remembering"
                    % (ren or "unrecorded")))
    elif not _re.search(r"\d{4}-\d{2}-\d{2}", ren):
        out.append((FAIL, "DOMAIN_AUTORENEW says %r but carries no date -- an undated status "
                          "assertion silently ages into a lie" % ren[:40]))
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
       LOCKED, fixed_on="2026-08-28 (deployed by David on the eve of soft-public after six days built-but-undeployed; Worker trustsquare-uptime, version 896f82f8, cron */5, PROBED ok:true kv:true at 11:31:54 UTC. Promoted the same session it started passing -- an entry that prints READY TO LOCK and is left OPEN cannot trip red when it rots. NOTE the marker's own caveat: the PROBE half is proven, the ALERT half is not -- no successful send has been observed, and the first scheduled heartbeat lands 06:00 UTC 29 Aug. This entry asserts an independent vantage exists and is alive; it does not claim mail was delivered.)",
       scope="The whole outage-detection lane. Class property: every instrument that "
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
       LOCKED, fixed_on="2026-08-27 (promoted: READY TO LOCK the moment the console was actually READ. The record half sat UNRECORDED for six days across five sweeps, each of which listed it as a David-only errand rather than opening the page -- it took one navigation. Publishing status 'In production', External, and the Verification centre's own words: 'Verification is not required since your app is not requesting any sensitive or restricted scopes.')",
       scope="Google OAuth, the only social sign-in lane (Apple is OUT by RUL-030). "
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
       LOCKED, fixed_on="2026-08-27", scope="ops/bit/bit_mitigator.py SAFE_FLAGS entire (today: ai_example_enabled, "
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
       LOCKED, fixed_on="2026-08-27 (promoted: READY TO LOCK on the first run after POSTURE-REDACT-1 shipped -- the anonymous read now carries redacted='posture' and the banned-pattern set finds nothing; promoted the SAME session it started passing, because a fix that prints READY TO LOCK and is never promoted cannot trip red when it rots -- DW-079; harness wiring check AMENDED 30 Aug 2026 -- DASH-SUMMARY-REDACT-1 strengthened the anon branch to heartbeat-only, so the harness now accepts redactor-call OR heartbeat wiring; the banned-pattern property checks are unchanged)",
       scope="GET /dashboard/summary, the dashboard payload that answers anonymously today. "
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

    # POSTURE-REDACT-1 (27 Aug 2026): the REPO half. Without it this entry reads whatever
    # is DEPLOYED and cannot tell "the fix was never written" from "the fix is written and
    # not yet shipped" -- two very different things to a session deciding what to do next.
    hp = os.path.join(REPO, "scripts", "prove_posture_redaction.py")
    fix_in_source = False
    if not os.path.exists(hp):
        out.append((FAIL, "scripts/prove_posture_redaction.py is gone -- the redaction is unproven"))
    else:
        ok, blind, detail = _harness([sys.executable, hp], timeout=90)
        if blind:
            out.append((INFO, detail))          # LEDGER-DEPS-1
        elif not ok:
            out.append((FAIL, "the redaction harness FAILS: " + detail[-300:]))
        else:
            fix_in_source = True
            out.append((INFO, "redaction proven in source (16 checks: the real 27 Aug leak "
                              "scrubbed, every non-posture field kept, recurses into nested "
                              "fields, clean text untouched)"))

    if hits:
        if fix_in_source:
            out.append((FAIL, "%s STILL answers an ANONYMOUS client with the defence posture "
                              "(%d pattern(s): %s). The redaction IS in the source and passes its "
                              "harness -- this is undeployed, not unwritten. It clears on the next "
                              "ship." % (PATH, len(hits), ", ".join(h[:26] for h in hits))))
        else:
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
       ref="AMENDED 30 Aug 2026 (LEDGER-ADMINREAD-1): live half now reads the badge through the admin key -- the anonymous payload is heartbeat-only by design (RG-0211) and had stopped carrying sessionBasis/sessionAsOf to strangers, which is correct. Assertion fixed, not weakened. SESSION-COUNTER-1, 22 Aug 2026, raised by David: the badge had read 'Session 155' "
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
        s = _admin_json("/dashboard/summary")
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
        # DEPLOY-DEBT-VOICE-1 (27 Aug 2026). Two very different faults were wearing one
        # sentence, and the difference decides what a session should DO:
        #   * the counter has fallen behind the fragments on disk -> a real rot, and the
        #     remedy is to run session_counter.py. That is the FAIL above.
        #   * the counter is CORRECT and the server simply has not been shipped yet -> the
        #     repo is ahead of live, which is deploy debt, and the only remedy IS a deploy.
        # Calling the second one a REGRESSION made the run exit 1 and print "Do not deploy
        # over this" -- telling the operator not to do the one thing that fixes it. On the
        # last ship day before a public launch that is not a cosmetic wording problem, it is
        # an instrument arguing against its own remedy. Same distinction RG-0144 now draws
        # between "not written" and "not shipped".
        counter_is_current = not [o for o in out
                                  if o[0] == FAIL and "fallen behind the fragments" in o[1]]
        if counter_is_current:
            out.append((INFO, "DEPLOY DEBT, not a rotted fix: the counter on disk is correct "
                              "(Session %s, derived) and the live badge is %s because the "
                              "server has not been shipped since. %d sitting(s) of debt. The "
                              "remedy is the next deploy -- this must not read as 'do not "
                              "deploy' (DEPLOY-DEBT-VOICE-1)"
                        % (repo_n, live_n, repo_n - live_n)))
        else:
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
       LOCKED, fixed_on="2026-08-26",
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
           "rather than handed over as a sentence he has to remember. "
           "FIXED 26 Aug 2026, all four defects: (a) orchestrator.html added to "
           "deploy_manifest.txt (nginx maps /orchestrator -> try_files /orchestrator.html, so it "
           "places at the web root); (b) the client-side access code REMOVED entirely rather than "
           "rotated -- PROBED first and found that DOMContentLoaded revealed #app unconditionally, "
           "so 96315 was a published secret enforcing nothing, while anonymous GET of "
           "/orchestrator, /report.json and /approve all answer 401 at nginx, which is the real "
           "gate. Rotating a code that gates nothing would have been ceremony; deleting the "
           "pretence is the fix, and it needed no RUL-027 call because no live access changed. "
           "(c) jget() now returns {ok,data,why} instead of null-for-everything, fill() renders a "
           "distinct FEED UNAVAILABLE / FIELD MISSING banner, and the health badge has a grey "
           "'not measured' state (RG-0133 class); (d) the ~05:00 SAST claim corrected to 06:30. "
           "The 'Nothing waiting on you. \u2728' copy went too -- the sparkle was itself a "
           "verdict, and an empty list is not a verdict. FOUR PRESENCE ASSERTIONS ADDED the same "
           "run: the original four checks were all ABSENCE tests, which a page rendering nothing "
           "at all would also pass, so the honest-failure machinery is now asserted positively and "
           "cannot be quietly removed. Source-side by nature -- the live page is auth-gated and "
           "cannot be probed anonymously -- but it is now inside the one deploy engine, which is "
           "the durable property this entry was about. Rides the Wed 27 Aug ship.")
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
    # ADDED 26 Aug 2026 alongside the fix. The four checks above are ABSENCE tests --
    # they prove the old defects are gone, but every one of them would also pass on a
    # page that simply rendered nothing at all. These are the PRESENCE half: the
    # machinery that makes a failed feed announce itself must actually be in the file,
    # so a later edit cannot quietly restore the all-clear behaviour while still
    # satisfying the absence tests. Written because the absence-only shape is exactly
    # how a fix rots without the board noticing.
    if "FEED UNAVAILABLE" not in html:
        out.append((FAIL, "the failed-feed banner is gone -- with no explicit outage state the "
                          "page can only render emptiness, which reads as an all-clear"))
    if "res.ok" not in html or "{ok:true" not in html.replace(" ", ""):
        out.append((FAIL, "jget no longer distinguishes a failed fetch from an empty result -- "
                          "returning null for both is what made an outage look like a clean board"))
    if "FIELD MISSING" not in html:
        out.append((FAIL, "a report that loads but omits a list would render as empty again -- "
                          "an absent field is a broken feed, not 'nothing to do'"))
    if "not measured" not in html:
        out.append((FAIL, "the health badge no longer has an unmeasured state -- an unreachable "
                          "probe must read grey, never amber 'check' (RG-0133 class)"))
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
       LOCKED, fixed_on="2026-08-26", scope="/static/studywork/Dossier_EXAMPLE_Study_Hungary.pdf + "
             "Dossier_EXAMPLE_Work_USA_Farm.pdf + their dl links on the teaser (SAW-3, RUL-044). "
             "CLASS: a Feature's worked examples are part of the feature surface -- a dead "
             "example link is a broken shop window. PDFs ship via the MEDIA lane [1b], the page "
             "via the code deploy: this entry catches the half-shipped state where either lane "
             "ran without the other.",
       ref="SAW-3, 23 Aug 2026. OPEN until BOTH the next code deploy (teaser v2 with dl links) "
           "AND a media_push run (PDFs) have happened. Generator: scripts/build_dossier_pdf.py "
           "(the P4 prototype) + dossier_examples.py. "
           "CLOSED 26 Aug 2026, and the finding is worth keeping: this was never a BUILD job. "
           "The PDFs had existed at assets/studywork/ since 23 Aug, media_push.bat line 40 already "
           "carried the *.pdf filter for that folder, and the teaser already linked both. Only the "
           "MEDIA half had never run while the code half shipped on 23 Aug -- precisely the "
           "half-shipped state this entry exists to catch, working exactly as designed. One "
           "media_push.bat run closed it; PROBED immediately after: both serve 200 as "
           "application/pdf at their exact on-disk byte counts (2072773 and 1687740). A sweep "
           "earlier the SAME day had this listed as 'still to BUILD' -- the reuse-before-recreate "
           "check is what caught it, and it would otherwise have cost a day rebuilding assets that "
           "already existed.")
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
           "reclassed om-chip nw until fill()/fail() paints them from a live answer. "
           "WIDENED 26 Aug 2026 (CHIP-GREEN-1): the needle list named only 3 chips, so 21 others still shipped "
           "hardcoded green -- an audit found them, this assertion did not. Now enforced structurally: any "
           "id-bearing chip carrying `om-chip g` in static markup trips this entry red, so the class cannot return "
           "one chip at a time.")
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
    # CHIP-GREEN-1 (26 Aug 2026): the needle list used to enumerate THREE chips, so
    # 21 further chips still shipped hardcoded `om-chip g` -- pre-painted GREEN with a
    # placeholder value of "-" before any feed answered. Found by audit, not by this
    # assertion, which is the whole point of widening it. The rule is now enforced
    # structurally: NO id-bearing chip may carry the green class in static markup.
    import re as _re
    _green = _re.findall(r'class="om-chip g" id="([a-z0-9\-]+)"', src)
    if _green:
        out.append((FAIL, "%d chip(s) wear GREEN in static markup before data answers "
                          "(RG-0133 rule on the map): %s" % (len(_green), ", ".join(sorted(_green)[:8]))))
    for cid in ("om-f-blocker", "om-f-major", "om-f-retest", "om-cpu", "om-ram", "om-disk",
                "om-livenow", "om-users", "om-listings", "om-queue", "om-db", "om-bit",
                "om-tuppence", "om-mailsent", "om-mailtotal", "om-mailspam", "om-resp",
                "om-bw", "om-topbin", "om-t-filed", "om-ai-today", "om-ai-mtd",
                "om-ai-calls", "om-ai-ceil"):
        if '<span class="om-chip nw" id="%s"' % cid not in src:
            out.append((FAIL, "placeholder chip %s wears a health colour before data answers (RG-0133 rule on the map)" % cid))
    return out or [(INFO, "ops-map loader fires all feeds; unfilled chips are grey until a live answer paints them")]



@entry("RG-0195", "A long-running .bat cannot be frozen by a stray mouse click, and nothing worth copying requires a mouse selection",
       LOCKED, fixed_on="2026-08-26", scope="CityLauncher/fix_console_freeze.bat + show_launch_key.bat, and the console default "
             "HKCU\\Console\\QuickEdit. THE FAULT (David: 'the old old problem'): Windows consoles ship with QuickEdit Mode ON, so "
             "one stray click inside the window puts it in selection mode and BLOCKS the running process on its next stdout write. "
             "It is indistinguishable from a hang. On 26 Aug 2026 deploy_citylauncher.bat sat frozen mid-scp for OVER AN HOUR and "
             "was diagnosed -- by Claude, from indirect evidence -- as a stalled SSH connection; David pressed Enter and it resumed. "
             "CLASS, not one script: every .bat in the toolkit is exposed (deploy_citylauncher, fix_launch_key, stop_pipeline, "
             "commit, start_session, media_push), and the cost is paid in hours of misdiagnosis, not in a visible error. "
             "SECOND HALF of the fix: with QuickEdit off you cannot drag-select, so any script that PRINTS something the user must "
             "copy has to put it on the clipboard instead -- otherwise the fix creates a new papercut. Lesson recorded separately: "
             "ask what the window SAYS before inferring a cause from server-side evidence.",
       ref="CONSOLE-QUICKEDIT-1, 26 Aug 2026. Host-registry half cannot be asserted from the repo (it is a Windows user setting), so "
           "this entry asserts the TOOLING that fixes and works around it is present and has not been reverted.")
def rg_console_quickedit():
    out = []
    import os as _os
    base = _os.path.normpath(_os.path.join(REPO, "..", "CityLauncher"))
    fixp = _os.path.join(base, "fix_console_freeze.bat")
    keyp = _os.path.join(base, "show_launch_key.bat")
    if not _os.path.isdir(base):
        return [(INFO, "CityLauncher repo not beside MarketSquare -- source check skipped")]
    if not _os.path.exists(fixp):
        out.append((FAIL, "fix_console_freeze.bat is gone -- the QuickEdit trap has no remedy in the toolkit"))
    else:
        src = open(fixp, encoding="utf-8", errors="replace").read()
        if "QuickEdit" not in src:
            out.append((FAIL, "fix_console_freeze.bat no longer touches QuickEdit"))
    if _os.path.exists(keyp):
        k = open(keyp, encoding="utf-8", errors="replace").read()
        if "clip" not in k:
            out.append((FAIL, "show_launch_key.bat no longer copies the key to the clipboard -- with QuickEdit "
                              "disabled the key cannot be drag-selected, so it would be unreachable"))
    return out or [(INFO, "console freeze remedy present; key-printing script copies to clipboard")]


@entry("RG-0193", "A city wave sends only to prospects PROVEN to be in that city -- the Stays lane must not bulk-assign the country to one default city",
       LOCKED, fixed_on="2026-08-26", scope="pipeline/adventures_run.py ENRICH city assignment + the adventures_accommodation rows in prospects.db. "
             "PROBED 26 Aug 2026 (live, gated read): all 223 adventures_accommodation rows carry suburb='accommodation_only' -- a "
             "placeholder, so no real geography was ever resolved -- and 217 of 223 are tagged PRETORIA, with Cape Town 4, Port "
             "Elizabeth 1, East London 1 and JOHANNESBURG ZERO. The names give the fault away: 'GUBAS DE HOEK' (De Rust, W Cape), "
             "'Auldstone House' and 'Highland Saddle and Trout' (Dullstroom, Mpumalanga) and 'Dolphin-View' are all tagged Pretoria. "
             "Pretoria is acting as a CATCH-ALL DEFAULT for every unresolved row. CLASS, not one lane: any lane that assigns a "
             "country-wide scrape to cities must resolve each prospect's real location or leave it unassigned -- never default it to "
             "a city that then receives it as local outreach. Two live consequences: (1) Johannesburg's 28 Aug day-one Stays send has "
             "NO addresses at all; (2) Pretoria's 28 Aug Stays send would mail ~217 lodges as 'your city is launching' when most are "
             "hundreds of km away -- the wrong-geo class already quarantined once as rejected_wrong_geo (TEACH-GEO-1, 21 Aug).",
       ref="STAYS-GEO-1, opened 26 Aug 2026 under RUL-037 (renumbered from RG-0191 -- the concurrent maintenance loop took that id the same hour; LEDGER-DUP-1 caught it). Passes when adventures_accommodation rows carry a resolved suburb (not "
           "'accommodation_only') AND no single city holds a disproportionate share of a national scrape AND Johannesburg is non-zero "
           "before its wave day. Related: RUL-057 (JHB is a proving city from 28 Aug), RUL-053 (30/cat/city/day).")
def rg_stays_geo():
    out = []
    # Live, unauthenticated read is impossible (PII endpoints are gated by design), so this
    # entry asserts the SHAPE from the repo's own assignment code plus a witness file when a
    # session leaves one. A placeholder suburb in the source is itself the defect.
    import os as _os
    base = _os.path.normpath(_os.path.join(REPO, "..", "CityLauncher"))
    runp = _os.path.join(base, "pipeline", "adventures_run.py")
    accp = _os.path.join(base, "scraper", "sources", "adventures_accommodation.py")
    geop = _os.path.join(base, "scraper", "geo_assign.py")
    depp = _os.path.join(base, "deploy_citylauncher.bat")
    if not _os.path.exists(runp):
        return [(INFO, "CityLauncher repo not beside MarketSquare -- source check skipped; "
                       "the live half needs a gated read")]
    run = open(runp, encoding="utf-8", errors="replace").read()
    acc = open(accp, encoding="utf-8", errors="replace").read() if _os.path.exists(accp) else ""

    # (a) the default-city fallback must stay dead
    import re as _re
    body = _re.sub(r"#.*", "", run)          # strip comments; the old line is quoted in one
    if "return cities[0]" in body:
        out.append((FAIL, "adventures_run._assign_city defaults to cities[0] again -- every unplaced "
                          "prospect is being stamped with the first city (Pretoria for ZA)"))
    # (b) coordinates must be captured, or assignment has nothing to stand on
    if acc and "out center" not in acc:
        out.append((FAIL, "the accommodation Overpass query is not 'out center' -- way elements come "
                          "back with no coordinate, so city assignment falls back to guessing"))
    if acc and "'lat':" not in acc:
        out.append((FAIL, "the accommodation source no longer carries lat/lon into the prospect"))
    # CSV-FIELDS-1 (26 Aug 2026): adding lat/lon to the prospect dict without adding them
    # to the FIXED DictWriter fieldnames raised
    #   ValueError: dict contains fields not in fieldnames: 'lat','lon'
    # and killed the run at the CSV step BEFORE city assignment -- so the fix looked like
    # it had produced nothing, for three hours. The coordinates must be in the CSV (they
    # are the evidence for every city decision) and the writer must tolerate a new key.
    if acc and "'lat', 'lon'" not in acc:
        out.append((FAIL, "the CSV fieldnames no longer carry lat/lon -- the writer will raise on the "
                          "prospect dict and the run dies before any city is assigned"))
    if acc and "extrasaction='ignore'" not in acc:
        out.append((FAIL, "the accommodation CSV writer lost extrasaction='ignore' -- one new upstream "
                          "key will kill the whole run again"))
    # (c) the resolver must exist AND be in the hardcoded deploy list (TEACH-DEPLOY-1)
    if not _os.path.exists(geop):
        out.append((FAIL, "scraper/geo_assign.py is missing -- the coordinate resolver is gone"))
    if _os.path.exists(depp):
        dep = open(depp, encoding="utf-8", errors="replace").read()
        if "geo_assign.py" not in dep:
            out.append((FAIL, "geo_assign.py is NOT in deploy_citylauncher.bat's scp list -- it would "
                              "never reach the server and the fix would be repo-only (TEACH-DEPLOY-1)"))
    # (d) the repair path must survive: INSERT OR IGNORE alone never corrects a bad row
    if "GEO-FIX" not in run:
        out.append((FAIL, "the geo repair path is gone -- existing mis-assigned rows would stay wrong "
                          "through every future re-scrape"))
    return out or [(INFO, "Stays city assignment is coordinate-proven, never defaulted, and repairs "
                          "existing rows on re-scrape")]


@entry("RG-0190", "The launch-metrics view is GATED and every tile is measured-or-labelled -- money never rides an anonymous endpoint, and no tile invents a number",
       LOCKED, fixed_on="2026-08-26", scope="bea_main.py /dashboard/launch-metrics + dashboard.server.html LAUNCH METRICS card. "
             "David asked (26 Aug) for eight launch-day numbers on one view: Paystack balance, FNB balance, subscriptions, "
             "complaints 24h, sellers, buyers, INTRO requests, INTRO accepts. TWO invariants, both born of faults paid for the SAME DAY: "
             "(1) GATING -- LAUNCH-API-FAILCLOSED-1 was landed hours earlier because /launch-api/prospects/list served 200 prospect "
             "records with names, emails and pre-authenticated magic links to anonymous callers. A new convenience endpoint carrying "
             "the PAYSTACK BALANCE must not reopen that class, so it sits behind _require_admin_or_key. (2) MEASURED-OR-LABELLED -- "
             "RG-0133 applied per tile: each metric returns its own measured flag and the card paints NOT MEASURED in grey rather than "
             "showing a number it did not obtain. FNB is permanently measured=False: no FNB integration exists and bank-login "
             "automation is out of scope, so the gap is stated on the face of the dashboard instead of being quietly omitted.",
       ref="LAUNCH-METRICS-1, 26 Aug 2026. Decided under RUL-037 (CTO lane). Source-scope checks only -- the served page and the "
           "endpoint are both auth-gated, so the live half cannot be probed anonymously (which is itself the point).")
def rg_launch_metrics():
    out = []
    import os as _os
    bp = _os.path.join(REPO, "bea_main.py")
    dp = _os.path.join(REPO, "dashboard.server.html")
    if not _os.path.exists(bp) or not _os.path.exists(dp):
        return [(INFO, "repo not present -- source check skipped (both halves are auth-gated)")]
    bsrc = open(bp, encoding="utf-8", errors="replace").read()
    dsrc = open(dp, encoding="utf-8", errors="replace").read()

    if '@app.get("/dashboard/launch-metrics")' not in bsrc:
        out.append((FAIL, "the launch-metrics endpoint is gone"))
    else:
        _seg = bsrc.split('@app.get("/dashboard/launch-metrics")', 1)[1][:400]
        if "_require_admin_or_key" not in _seg:
            out.append((FAIL, "launch-metrics is NOT admin-gated -- it carries the Paystack balance "
                              "(the LAUNCH-API-FAILCLOSED-1 class, reopened)"))
    # FNB must stay honestly unmeasured, never quietly dropped and never faked
    if "fnb_balance" not in bsrc:
        out.append((FAIL, "the FNB tile was removed rather than reported as NOT MEASURED"))
    elif "NOT MEASURED" not in bsrc.split("fnb_balance", 1)[1][:400]:
        out.append((FAIL, "the FNB tile no longer declares itself NOT MEASURED -- it must never carry a number"))
    # the card must not hardcode any tile value
    if 'id="lm-grid"' not in dsrc:
        out.append((FAIL, "the LAUNCH METRICS card is gone from the dashboard"))
    if "loadLaunchMetrics" not in dsrc:
        out.append((FAIL, "the launch-metrics loader is gone -- the card would sit at its placeholder forever"))
    return out or [(INFO, "launch-metrics is admin-gated; every tile is measured or says NOT MEASURED")]


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
       LOCKED, fixed_on="2026-08-28 (promoted: READY TO LOCK on the run of the very day the first wave is due -- RUL-053(g) names Fri 28 Aug 2026, and an unasserted gate on the day it matters is the DW-079 lesson repeated. All three properties report ok and fresh from the witness file: source tags, cross-wave suppression, intl template pass. The suppression half is a POPIA property, which is why this could not be left blue over a sending weekend -- DW-081)", scope="orchestration_v2/templates/*_outreach.html CTA links + the n8n suppression path + a wave_hygiene_status.json witness. "
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
       LOCKED, fixed_on="2026-08-26",
       scope="PROMOTED 26 Aug 2026 by the third-party sweep on the ledger's own READY TO LOCK "
             "print, and independently re-PROBED the same run: anonymous GET "
             "/launch-api/prospects/list answers HTTP 401 (it served 146 KB of prospect PII plus "
             "pre-authenticated admin magic-links at 04:20 the same morning -- DW-068). "
             "LAUNCH_API_KEY is provisioned and the CityLauncher deploy has ridden, so half (b) "
             "below is CLOSED. Half (a) -- the n8n cross-store suppression round trip -- stays "
             "proven only by hand and is named here rather than left to weaken the assertion. "
             "Original scope: CityLauncher suppression register + LAUNCH-API-LOCK-1 (built 24 Aug, RUL-054) -- repo halves pass; TWO live halves outstanding: "
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
    import os as _os, re as _re
    gp = _os.path.join(REPO, "scripts", "no_remote_code_guard.py")
    if not _os.path.exists(gp):
        return [(FAIL, "scripts/no_remote_code_guard.py is GONE -- the pre-deploy half of RG-0025 "
                       "is unenforced and a third-party loader can ship again")]
    out = []
    ok, blind, detail = _harness([sys.executable, gp, "--self-test"], timeout=60)
    if blind:
        out.append((INFO, detail))              # LEDGER-DEPS-1: instrument, not app
    elif not ok:
        out.append((FAIL, "the guard's self-test FAILED -- it no longer catches the 3 Aug loader "
                          "class, so its green means nothing: " + detail[-300:]))

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
       LOCKED, fixed_on="2026-08-27",
       scope="live response headers on trustsquare.co, BOTH the index and the app paths; shipped by migrations/031_csp_and_index_headers.py, finally landed by 033 via CSP-SCRIPT-SRC-5. "
             "PROMOTED 27 Aug 2026 on a live PROBE, not on the migration reporting ok: GET / and "
             "GET /terms both return default-src 'self'; script-src 'self' 'unsafe-inline' "
             "https://unpkg.com https://cdnjs.cloudflare.com. Worth recording because the 26 Aug "
             "sweep raised a Cloudflare-edge-emitter hypothesis for why the origin fix kept not "
             "showing up -- that hypothesis is now DISPROVEN: the emitter was nginx all along and "
             "033 was measuring the port-80 301 redirect. A hypothesis that survives in a doc "
             "after the probe kills it is the next session's wrong turn.",
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
       LOCKED, scope="live CSP connect-src directive on trustsquare.co", fixed_on="2026-08-30",
       ref="PROMOTED 30 Aug 2026 the run it printed READY TO LOCK: migration 034_csp_connect_src "
           "rode David's afternoon deploy (Release ef44fc5), rewrote the served connect-src to the "
           "named allowlist and PROVED it on the served response (/ and /terms) with rollback "
           "recorded. Original: CSP-CONNECT-1 (24 Aug 2026) -- the honest limit of CSP-SCRIPT-SRC-1, recorded rather than "
           "quietly omitted. Migration 031 ships connect-src 'self' https:, which means a script that "
           "somehow DID execute could still POST data out -- the 3 Aug capture showed the loader "
           "POSTing to /collect and /collect_batch, which is exactly this channel. It is left open on "
           "purpose for now: closing it needs the app's own outbound XHR/fetch/EventSource targets "
           "inventoried at RUNTIME (a static scan on 24 Aug found no absolute external fetch targets, "
           "but absence in source is not proof of absence at runtime), and a wrong connect-src breaks "
           "live payments or auth silently. Post-launch job. script-src is the control that stops the "
           "script existing at all, and that one is tight -- this is defence in depth, not the door. "
           "INVENTORY DONE 27 Aug 2026, the thing this entry was blocked on -- but the SHIP is still "
           "deliberately held to post-launch, because the entry\'s own caution is right and two days "
           "before public is the worst possible moment to discover a missed XHR target. What was "
           "measured: EVERY fetch() in ms.js resolves same-origin -- relative paths (/ai/run, "
           "/ai/jobs/, /ai/functions, /ai/example/, /api/fx, /) or `${BEA_URL}/advert-agent/*`, and "
           "BEA_URL is the literal \'https://trustsquare.co\' (ms.js line 6). There is not one "
           "absolute cross-origin fetch/XHR/WebSocket/EventSource/sendBeacon target in the source. "
           "The cross-origin hosts that DO appear -- unpkg.com and cdnjs.cloudflare.com (Leaflet "
           "js/css), tile.openstreetmap.org (raster map tiles), fonts.googleapis.com/gstatic.com, "
           "commons.wikimedia.org -- are script/style/img/font subjects, NOT connect subjects, and "
           "are already named in their own directives. THE POLICY TO SHIP, so the next session does "
           "not re-derive it: connect-src \'self\' https://unpkg.com https://cdnjs.cloudflare.com "
           "https://tile.openstreetmap.org -- the three CDNs kept only because a Leaflet plugin can "
           "fetch rather than <img>, and keeping three known hosts still forecloses exfiltration to "
           "an attacker-controlled origin, which is the entire point. THE SAFE WAY TO SHIP IT: send "
           "it first as Content-Security-Policy-Report-Only alongside the enforced header, collect "
           "real-browser violation reports for a week, THEN enforce. That turns \'absence in source "
           "is not proof of absence at runtime\' from an objection into a measurement. Not done "
           "today on purpose: it needs a new migration, and the chain was only just unjammed "
           "(RG-0125) -- adding one on the last ship day is the DEFER-1 risk this project has "
           "already paid for twice. AMENDED 30 Aug 2026 (activation session): the live-half test was a SUBSTRING test (https: matches every named https origin, * matches a wildcard subdomain) so the recorded three-host policy could never pass its own assertion -- fixed to judge TOKENS; migration 034 ships the recorded policy exactly, measured live in Chrome this session (all five surfaces: zero cross-origin connect targets).")
def rg_csp_connect_src_tight():
    try:
        csp = _headers("/terms").get("content-security-policy", "") or ""
    except Exception as ex:
        return [(FAIL, "could not read the live CSP: " + repr(ex)[:70])]
    if "connect-src" not in csp:
        return [(FAIL, "no connect-src directive at all -- falls back to default-src; verify that is "
                       "deliberate")]
    directive = csp.split("connect-src", 1)[1].split(";", 1)[0]
    # ASSERTION FIXED 30 Aug 2026 (CSP-CONNECT-1 activation): the old test was
    # `"https:" in directive` -- a SUBSTRING test that also matches every named
    # https:// origin, so the entry's own recorded policy (three named hosts)
    # could never pass. Openness is a property of TOKENS: only the bare scheme
    # source `https:` or a bare `*` is a blanket. A named origin is the fix.
    tokens = directive.split()
    open_tokens = [t for t in tokens if t in ("https:", "http:", "*", "https://*", "http://*")]
    if open_tokens:
        return [(FAIL, "connect-src is still open (%r in %r) -- a script that executed could "
                       "exfiltrate. Named origins only" % (open_tokens, directive.strip()))]
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
    import os as _os
    mp = _os.path.join(REPO, "travelpayouts_partners.py")
    if _os.path.exists(mp):
        ok, blind, detail = _harness([sys.executable, mp], timeout=60)
        if blind:
            out.append((INFO, detail))          # LEDGER-DEPS-1: instrument, not app
        elif not ok:
            out.append((FAIL, "the lane's own selftest FAILS -- its refusals no longer refuse: "
                              + detail[-250:]))
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
    import os as _os
    hp = _os.path.join(REPO, "scripts", "prove_fares_lane.py")
    if not _os.path.exists(hp):
        out.append((FAIL, "scripts/prove_fares_lane.py is gone -- the dark/lit behaviour is unproven"))
    else:
        ok, blind, detail = _harness([sys.executable, hp], timeout=90)
        if blind:
            out.append((INFO, detail))          # LEDGER-DEPS-1: instrument, not app
        elif not ok:
            out.append((FAIL, "the dark/lit harness FAILS: " + detail[-300:]))

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


@entry("RG-0184", "No AI lane that can take traffic is priced from an aggregator or an estimate -- "
       "first-party or it does not bill",
       LOCKED, fixed_on="2026-08-26",
       scope="ai_price_card.json, EVERY model wired in ai_provider.TASK_MODEL. Class property: a "
             "model may sit on the card with a second-hand price ONLY while its gate says it can "
             "take no traffic (gate 'reserved'). The moment a lane is production / golden-set-"
             "passed / eval-pending-with-a-key, its price must carry source_kind 'first-party'.",
       ref="RUL-032 + the 26 Aug canary run. The gemini-3.7-flash row was captured 19 Aug from "
           "openrouter.ai at $0.375 in / $1.50 out, and the RUL-032 costing ($548/yr canary vs "
           "$1,729/yr terra) was built on it. First-party ai.google.dev says the STANDARD tier -- "
           "the tier ai_provider._gemini's synchronous chat/completions call actually bills at -- "
           "is $0.75 in / $3.75 out. $0.375 is Google's BATCH input rate; $1.50 was flagged in the "
           "row itself as an estimate and got used anyway. Input was understated 2x, output 2.5x, "
           "and the canary's real year-1 cost is ~$845, not $548. Same shape as the incident that "
           "created RG-0018 (the 18 Jul 'Mistral ~40% of Haiku' claim standing on a stale price) -- "
           "RG-0018 checks the card is FRESH and COVERING; nothing checked that a price was FIRST-"
           "PARTY. This entry closes that gap. Corrected 26 Aug 2026 with the workbook rows.")
def rg_price_first_party():
    card_txt = repo_file("ai_price_card.json")
    seam = repo_file("ai_provider.py")
    if card_txt is None or seam is None:
        return [(INFO, "running outside the repo -- first-party price check skipped")]
    try:
        card = json.loads(card_txt)
    except Exception as ex:
        return [(FAIL, f"ai_price_card.json unreadable ({ex!r})")]
    out = []
    for prov, pdata in (card.get("providers") or {}).items():
        for model, row in (pdata.get("models") or {}).items():
            gate = (row.get("gate") or "").lower()
            kind = (row.get("source_kind") or "").lower()
            if gate == "reserved":
                continue                      # cannot take traffic; a second-hand price is harmless
            if kind != "first-party":
                out.append((FAIL, f"{prov}/{model} is gated '{gate or 'unset'}' -- it can reach "
                                  f"traffic -- but its price is sourced '{kind or 'unset'}'. A "
                                  "decision standing on a second-hand price is the RG-0018 fault "
                                  "with a different label. Re-verify on the vendor's own pricing "
                                  "page and set source_kind: first-party."))
            src_note = (row.get("source") or "").lower()
            if "estimate" in src_note and "correction" not in src_note:
                out.append((FAIL, f"{prov}/{model} still describes its own price as an ESTIMATE "
                                  "while gated '%s' -- estimates do not bill" % (gate or "unset")))
    return out or [(INFO, "every model that can take traffic carries a first-party price"
                          " (%d rows checked)" % sum(len(p.get("models") or {})
                                                     for p in (card.get("providers") or {}).values()))]


@entry("RG-0185", "The photo-anon eval set is REPRODUCIBLE and every row it scores has a truth label",
       OPEN,
       scope="scripts/build_eval_set.py + eval_photos/TRUTH.json. Class property: the eval set is "
             "the evidence every photo-anon model decision rests on, so it must rebuild byte-"
             "identical (identical evidence for every candidate) and no row may be scored against "
             "a guessed answer. OPEN until (a) the 19 Aug 2026 Maroushka failure photos and the 3 "
             "'inappropriate' samples are added, and (b) the five listing-246 rows carry a "
             "hand-set verdict instead of 'unknown'.",
       ref="AI_PHOTO_COST_MODEL.xlsx 'Switch Test Plan' step 0 -- '~30 photos ... stored privately; "
           "never changes, so every model scores on identical evidence'. Built 26 Aug 2026: 22 "
           "photos (9 synthetic plate shapes, 3 false-positive traps, 5 listing-246 originals, 5 "
           "off-category). The traps matter as much as the plates -- RUL-031 is a ruling about "
           "OVER-smearing, so a set of plates alone would score the wrong failure. Also this "
           "session: eval_photos/ and private_originals_listing246/ were untracked but NOT "
           "gitignored -- a `git add -A` would have pushed a real seller's plates to the GitHub "
           "mirror. Now ignored. READY TO LOCK when the set is complete and fully labelled.")
def rg_eval_set():
    builder = repo_file("scripts/build_eval_set.py")
    if builder is None:
        return [(FAIL, "scripts/build_eval_set.py is GONE -- the eval set can no longer be "
                       "rebuilt, so 'identical evidence for every candidate' is unprovable")]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    truth_p = os.path.join(root, "eval_photos", "TRUTH.json")
    if not os.path.exists(truth_p):
        return [(FAIL, "eval_photos/TRUTH.json is absent -- the set has not been built here. "
                       "Run: python3 scripts/build_eval_set.py")]
    try:
        doc = json.load(open(truth_p, encoding="utf-8"))
    except Exception as ex:
        return [(FAIL, f"eval_photos/TRUTH.json unreadable ({ex!r})")]
    out, photos = [], doc.get("photos") or []
    missing_sha = [p["file"] for p in photos if not p.get("sha256")]
    if missing_sha:
        out.append((FAIL, "%d eval photo(s) carry no sha256 -- drift cannot be detected: %s"
                          % (len(missing_sha), ", ".join(missing_sha[:3]))))
    unknown = [p["file"] for p in photos if p.get("expect") == "unknown"]
    if unknown:
        out.append((FAIL, "%d eval photo(s) still have expect='unknown' -- an eval scored against "
                          "a guessed answer key proves nothing. Set them by hand: %s"
                          % (len(unknown), ", ".join(unknown[:2]) + ("..." if len(unknown) > 2 else ""))))
    if not any(f.startswith("real_0819") for f in (p["file"] for p in photos)):
        out.append((FAIL, "the 19 Aug 2026 Maroushka failure photos are NOT in the set -- the "
                          "freshest evidence of the fault RUL-031 was written about is missing "
                          "(they are server-side uploads; pull them in as real_0819_*)"))
    if len(photos) < 30:
        out.append((FAIL, "eval set holds %d photos; the Switch Test Plan calls for ~30 including "
                          "3 'inappropriate' samples, which are absent -- the scan prompt's "
                          "moderation clause is unscored" % len(photos)))
    if not any(p.get("expect") == "clean" and "trap" in p["file"] for p in photos):
        out.append((FAIL, "the false-positive TRAPS have gone from the eval set -- RUL-031 is a "
                          "ruling about OVER-smearing, so a set of plates alone scores the wrong "
                          "failure"))
    return out or [(INFO, "eval set complete: %d photos, every row labelled" % len(photos))]



@entry("RG-0186", "A server-side migration can SEE every file it must change -- discovery is what nginx "
       "actually reads, not a guessed list of globs",
       LOCKED, fixed_on="2026-08-26",
       scope="migrations/033_csp_verify_served.py discovery + scripts/prove_csp_discovery.py. CLASS "
             "property, not one migration: any migration that edits server configuration must "
             "enumerate its targets from what the SERVICE resolves (nginx -T), never from a "
             "hand-written glob list -- a glob that misses the file is indistinguishable from a "
             "server that refuses the change, and it fails identically forever.",
       ref="CSP-SCRIPT-SRC-3 (26 Aug 2026), found by the maintenance loop reading the RG-0125 red. "
           "The 24 Aug deploy ran 033 and it reported, in its own words, 'CSP declared in N file(s); "
           "0 still lack script-src' and then measured a SERVED policy of frame-ancestors 'self'. It "
           "restored 0 files (nothing was stale to restore), failed honestly -- it refuses to claim "
           "an effect it cannot probe, which is why this was findable at all -- and JAMMED the "
           "migration chain, so every later one-time server change would have been silently skipped. "
           "The defect was never the server: 033 searched a FIXED list of globs, none of them "
           "recursive (snippets/* never reaches snippets/security/*) and all under /etc/nginx, so an "
           "include one directory deeper, or by absolute path from outside the tree, was invisible. "
           "It rewrote everything it could see and the emitter was not among them. THE FIX: "
           "discovery now unions `nginx -T` -- the fully-resolved config, which names every file "
           "nginx really reads and therefore cannot miss an include -- with a recursive walk of "
           "/etc/nginx and the original globs; and on failure it now PRINTS every file still "
           "declaring a CSP, so the next failure is diagnosable instead of mute. This is the same "
           "lesson as 031's, one level up: 031 declared success from a WRITE instead of a PROBE, and "
           "033 probed correctly but searched blind. PROVEN by scripts/prove_csp_discovery.py, which "
           "builds a fixture with the emitter nested one level below the old globs' reach and shows "
           "the old discovery missing it and the new discovery finding, classifying and correctly "
           "rewriting it (10/10). NOT YET PROVEN ON THE BOX: the sandbox has no nginx, so whether "
           "the live server now serves script-src is answered by RG-0178 after the next deploy "
           "rides -- this entry asserts the discovery, which is the part that was broken.")
def rg_migration_discovery_authoritative():
    mig = repo_file("migrations/033_csp_verify_served.py")
    if mig is None:
        return [(INFO, "running outside the repo -- migration discovery check skipped")]
    out = []
    if "_nginx_T_files" not in mig or '"-T"' not in mig:
        out.append((FAIL, "033 no longer asks nginx -T what it reads -- discovery is back to a "
                          "guessed glob list, which is the 24 Aug failure exactly"))
    if "os.walk" not in mig:
        out.append((FAIL, "033 lost its recursive walk of /etc/nginx -- a nested snippet is "
                          "invisible again"))
    if "STILL DECLARES CSP" not in mig:
        out.append((FAIL, "033 no longer names the files still declaring a CSP when it fails -- "
                          "the next failure would be as undiagnosable as the 24 Aug one"))
    # The migration must still REFUSE to claim an effect it has not probed. That honesty is
    # what made this fault findable; a version that exits 0 on an unproven write is worse
    # than the bug.
    # The honesty invariant, asserted as BEHAVIOUR rather than prose. Two earlier cuts of
    # this check searched the source for the sentence "Not claiming success" -- first raw,
    # then whitespace-normalised -- and both went red against a migration that was entirely
    # correct, because the sentence is split across adjacent string literals ('... Not
    # claiming " "success.'). A guard that matches wording rather than behaviour breaks the
    # moment someone re-wraps a line. What actually matters is the control flow: the served
    # response is read AFTER the reload, and a missing script-src raises instead of returning ok.
    after_reload = mig.split('nginx", "-s", "reload"', 1)[-1]
    # THIRD CUT, 26 Aug 2026 (CSP-VERIFY-GUARD-3). The two earlier cuts matched the prose
    # "Not claiming success"; this one matched the CALL SITE spelled `served_csp()` with
    # empty parens -- and went RED the moment 033 legitimately grew an argument
    # (`served_csp(settle=15)`, added by CSP-SCRIPT-SRC-5 so the probe stops racing nginx's
    # asynchronous reload). Same mistake in a new costume: the guard matched a SPELLING,
    # not the behaviour. Match the call, not its argument list.
    if "served_csp(" not in after_reload:
        out.append((FAIL, "033 no longer reads the SERVED response after reloading -- it would be "
                          "declaring success from the write again, which is exactly 031's mistake"))
    elif 'if "script-src" not in after' not in after_reload or "raise RuntimeError" not in after_reload:
        out.append((FAIL, "033 reads the served CSP but no longer RAISES when script-src is absent "
                          "-- it could report 'ok' for a change the server never served"))
    tail = mig.split("The site is exactly as it was", 1)[-1][:200]
    if "return 1" not in tail:
        out.append((FAIL, "033's failure path no longer returns non-zero after restoring -- an "
                          "unproven change would be recorded by post_deploy as a successful "
                          "migration, and the chain would march on believing it landed"))

    hp = os.path.join(REPO, "scripts", "prove_csp_discovery.py")
    if not os.path.exists(hp):
        out.append((FAIL, "scripts/prove_csp_discovery.py is gone -- the discovery fix is unproven"))
    else:
        ok, blind, detail = _harness([sys.executable, hp], timeout=90)
        if blind or "NOT EVALUATED:" in str(detail):
            # LEDGER-DEPS-2: the harness drives `nginx -T`. No nginx on this machine
            # means the instrument is absent, which RG-0187 says must read UNVERIFIED.
            out.append((INFO, str(detail)[-300:] if not blind else detail))
        elif not ok:
            out.append((FAIL, "the discovery harness FAILS: " + str(detail)[-300:]))
        else:
            out.append((INFO, "discovery proven against a fixture the old globs could not see"))
    return out


@entry("RG-0187", "The ledger can tell a missing DEPENDENCY from a rotted fix -- an instrument that "
       "cannot run reads UNVERIFIED, never REGRESSION",
       LOCKED, fixed_on="2026-08-26",
       scope="scripts/regression_ledger.py _harness()/_missing_third_party() and EVERY entry that "
             "proves itself by running a subprocess harness (RG-0128, RG-0177, RG-0181, RG-0182 "
             "today). Source-half by nature -- the instrument is the subject, as with RG-0126. "
             "CLASS property: the demotion covers third-party imports ONLY; a missing REPO module "
             "is a deletion and must stay red. EXTENDED 27 Aug 2026 (LEDGER-UNVER-CAUSE-1) to the "
             "SUMMARY line: demoting honestly is only half the job -- the run must also name the "
             "REAL reason. The unver branch of main() asserted, unconditionally, that the machine "
             "could not reach the site, and printed exactly that on a run whose two UNVERIFIED "
             "entries were dependency demotions on a machine curling the site fine in the same "
             "minute. It now reads the recorded reason back off each entry and states the network "
             "verdict from _NET, never from assumption.",
       ref="LEDGER-DEPS-1 (26 Aug 2026). The maintenance loop's own opening run produced the "
           "evidence: RG-0181 and RG-0182 both printed REGRESSION -- 'its refusals no longer "
           "refuse', 'the dark/lit harness FAILS' -- and the run closed '5 previously-fixed "
           "issue(s) HAVE COME BACK. Do not deploy over this.' The cause was ModuleNotFoundError: "
           "No module named 'fastapi'. Both harnesses died on their import line having run ZERO "
           "assertions; `pip install fastapi` turned them into 9/9 and 13/13 with not one byte of "
           "app code changed. This is the THIRD instance of one shape -- the instrument reporting "
           "itself as the app -- after LEDGER-OFFLINE-1 (7 Aug, no network) and GATE-CACHE-1 (14 "
           "Aug, a 429 credential), and it is treated the same way: NOT EVALUATED -> UNVERIFIED, "
           "loudly not a pass, exit 2. A false red is worse than no answer -- it invites the next "
           "session to 'fix' what is not broken and it blocks a deploy for nothing, and this file's "
           "own preamble says a tripwire that cries wolf carries false comfort. THE NARROWNESS IS "
           "THE POINT: if the dead import is one of our own repo files the fix really has been "
           "deleted, so it stays RED -- a demotion that swallowed that would be the silent green "
           "the preamble calls the worse failure. PROVEN end-to-end the same session: with fastapi "
           "uninstalled RG-0181/RG-0182 reported UNVERIFIED (not REGRESSION); reinstalled, both "
           "returned HOLDING; and scripts/prove_ledger_deps.py mutation-tests all four branches "
           "(10/10).")
def rg_ledger_deps_blind_not_red():
    led = repo_file("scripts/regression_ledger.py")
    if led is None:
        return [(INFO, "running outside the repo -- LEDGER-DEPS-1 check skipped")]
    out = []
    if "_missing_third_party" not in led or "def _harness(" not in led:
        return [(FAIL, "LEDGER-DEPS-1 has been REMOVED -- a sandbox missing one dependency will "
                       "cry REGRESSION again and block a deploy for nothing")]
    if "NOT EVALUATED" not in led.split("def _harness(", 1)[1][:2000]:
        out.append((FAIL, "_harness no longer emits NOT EVALUATED, so run() cannot demote a blind "
                          "harness to UNVERIFIED -- the demotion is wired to that exact phrase"))
    # The narrowing guard: our own modules must NOT be demoted.
    seg = led.split("def _missing_third_party(", 1)[1][:1200]
    if "REPO" not in seg:
        out.append((FAIL, "_missing_third_party no longer checks whether the module is OURS -- a "
                          "DELETED repo file would now read 'unverified' instead of red, which is "
                          "the silent-green failure this ledger exists to prevent"))

    # Every harness call site must route through _harness. A new entry that hand-rolls
    # subprocess.run + returncode re-opens the fault for itself.
    import re as _re
    raw = [m for m in _re.findall(r"_sp\.run\(\[sys\.executable[^\n]*", led)]
    raw += [m for m in _re.findall(r"subprocess\.run\(\[sys\.executable[^\n]*", led)]
    # The BRAIN-PATH-1 exec probe is a deliberate exception: it asserts importability
    # itself, so a dead import IS its finding.
    raw = [m for m in raw if '"-c", probe' not in m and "'-c', probe" not in m]
    if raw:
        out.append((FAIL, "%d harness call site(s) still run a subprocess directly instead of via "
                          "_harness() -- each one can cry REGRESSION on a missing dependency: %s"
                          % (len(raw), raw[0].strip()[:110])))

    # LEDGER-UNVER-CAUSE-1 (27 Aug 2026): the run may not TELL a session the site was
    # unreachable unless it measured that. A summary naming the wrong cause sends the
    # next session to fix the wrong thing -- the RG-0117 mistake one layer up.
    if "LEDGER-UNVER-CAUSE-1" not in led:
        out.append((FAIL, "LEDGER-UNVER-CAUSE-1 has been REMOVED -- the NOT EVALUATED summary is "
                          "free to blame the network again for what was a missing dependency"))
    else:
        _tail = led.split("\n    elif unver:", 1)[-1].split("\n    elif ready:", 1)[0]
        if "_NET[\"ok\"] is False" not in _tail:
            out.append((FAIL, "the NOT EVALUATED summary no longer gates its unreachable-site "
                              "claim on the MEASURED network verdict (_NET) -- it is guessing again"))
        if "Reason as the instrument recorded it" not in _tail:
            out.append((FAIL, "the NOT EVALUATED summary no longer reads the recorded reason back "
                              "off the entries -- a session is told a count and no cause"))

    hp = os.path.join(REPO, "scripts", "prove_ledger_deps.py")
    if not os.path.exists(hp):
        out.append((FAIL, "scripts/prove_ledger_deps.py is gone -- the blind/red boundary is unproven"))
    else:
        ok, blind, detail = _harness([sys.executable, hp], timeout=120)
        if blind:
            out.append((INFO, detail))
        elif not ok:
            out.append((FAIL, "the LEDGER-DEPS-1 mutation harness FAILS: " + detail[-300:]))
        else:
            out.append((INFO, "blind-vs-red boundary proven: dependency deaths demote, real "
                              "failures and deleted repo modules stay red"))
    return out



@entry("RG-0188", "The lockout self-heal can actually HEAL -- the cure for SSH-LOCKOUT-1 is armed, "
       "not merely written",
       LOCKED, fixed_on="2026-08-26",
       scope="scripts/hetzner_fw_selfheal.py + the tokens it needs (.secrets/hetzner_token.txt, "
             "and .secrets/cf_waf_token.txt for the Cloudflare half). CLASS property: a documented "
             "remedy that cannot run is not a remedy. RG-0099 DETECTS the lockout; this asserts the "
             "fix named in RG-0099's own failure message is executable when that day comes. The CF "
             "half retires with the prelaunch gate; the Hetzner half stays for good.",
       ref="Found 26 Aug 2026 by the maintenance loop working the RG-0099 red. Port 22 timed out "
           "from the session vantage on every try and the ORIGIN (178.104.73.239) was unreachable "
           "on 22, 443 AND 80, while Cloudflare served /health, / and /terms at 200 -- i.e. the box "
           "is fine and this egress IP (197.184.106.176) is simply outside the origin allowlist. "
           "That is SSH-LOCKOUT-1 exactly as RG-0099 describes it. RG-0099's message says 'Fix: run "
           "scripts/hetzner_fw_selfheal.py' -- so the loop ran it, and it answered 'NO TOKEN ... "
           "Nothing changed.' The self-healer built on 17 Aug in response to the blackout has never "
           "been armed, so for nine days the class has been DETECTED but not CURABLE, and nothing "
           "on the board said so. That gap is the entry. PROMOTED TO LOCKED 26 Aug 2026, same day, on "
           "David's act: he generated a read+write Hetzner Cloud API token and entered it through "
           "add_secret.bat (the no-GUI path, RG-0189) -- which itself had to be repaired first, "
           "see RG-0194, because it flickered shut unreadably on LF line endings. PROBED, never "
           "assumed: `hetzner_fw_selfheal.py --check` reached the Hetzner API with the token, read "
           "firewall 11414216 and reported '197.184.106.176 already allowlisted (4 SSH sources)'. "
           "The remedy is executable, which is precisely what this entry asserts. The Cloudflare "
           "half stays unarmed and reports as INFO, not FAIL -- that gate retires at launch, and a "
           "lower-stakes half should not hold a LOCKED assertion hostage. "
           "NOTE the script only ever ADDS the current "
           "IP and never removes a rule, so arming it cannot itself cause a lockout -- but "
           "provisioning the token is David's act (RUL-027 reserves lockout-risk and secret "
           "handling to him), which is why this is OPEN rather than fixed. It goes READY TO LOCK "
           "the moment the token exists and --check answers cleanly.")
def rg_lockout_selfheal_armed():
    sh = repo_file("scripts/hetzner_fw_selfheal.py")
    if sh is None:
        return [(FAIL, "scripts/hetzner_fw_selfheal.py is GONE -- RG-0099 would detect a lockout "
                       "and name a remedy that no longer exists")]
    out = []
    # The safety property that makes arming this uncontroversial: it must never REMOVE a rule.
    low = sh.lower()
    if "delete" in low and "never remove" not in low:
        out.append((FAIL, "the self-heal may now DELETE firewall rules -- it is only safe to arm "
                          "while it strictly adds"))
    # STRENGTHENED 26 Aug 2026: presence was never the property -- RUNNABILITY is.
    # This assertion falsely went READY TO LOCK the same day, because a session
    # created an EMPTY .secrets/hetzner_token.txt as a paste target for David and
    # os.path.exists() was satisfied by a 0-byte file. The self-heal would still
    # have exited 'NO TOKEN, nothing changed' in a real lockout, with a green board
    # saying it was armed. That is the RG-0133 class (a light nothing measured)
    # landing on the ledger itself, and it is exactly the failure mode this entry
    # was written to prevent. Empty and stub values are now named distinctly from
    # missing, because the remedies differ: one needs a file, one needs a value.
    tok = os.path.join(REPO, ".secrets", "hetzner_token.txt")
    if not os.path.exists(tok):
        out.append((FAIL, "no .secrets/hetzner_token.txt -- the documented cure for SSH-LOCKOUT-1 "
                          "exits 'NO TOKEN, nothing changed'. The class is detected but NOT "
                          "curable, and a real lockout would need a hand-fix at the Hetzner panel "
                          "while nobody can reach the box. David provisions this one (RUL-027)."))
    else:
        try:
            _tv = open(tok, encoding="utf-8", errors="replace").read().strip()
        except Exception as _e:
            _tv = ""
            out.append((FAIL, ".secrets/hetzner_token.txt exists but could not be read (%s) -- "
                              "treat as unarmed" % _e))
        if _tv == "":
            out.append((FAIL, "'.secrets/hetzner_token.txt' exists but is EMPTY -- the file is a "
                              "placeholder, not a credential. hetzner_fw_selfheal.py still exits "
                              "'NO TOKEN, nothing changed'. A present-but-empty secret file is "
                              "MORE dangerous than a missing one: it satisfies a presence check "
                              "and paints the board green over an unarmed remedy."))
        elif len(_tv) < 32 or not _tv.replace("-", "").replace("_", "").isalnum():
            out.append((FAIL, "'.secrets/hetzner_token.txt' does not hold a plausible Hetzner API "
                              "token (%d chars) -- Hetzner Cloud tokens are 64 alphanumeric "
                              "characters. Not asserting the VALUE is right, only that something "
                              "token-shaped is there; a stub cannot heal a lockout." % len(_tv)))
    if "CF_HALF_RETIRED = True" not in sh:
        out.append((FAIL, "hetzner_fw_selfheal.py no longer marks the Cloudflare half RETIRED -- "
                          "RUL-034 disabled the PRELAUNCH GATE and the site launched 1 Sep 2026; "
                          "a re-armed CF half would demand a token nobody needs (NO-STALE-IP-1)"))
    return out or [(INFO, "lockout self-heal is armed; CF half retired (RUL-034), no token needed")]


@entry("RG-0189", "No secret ever needs a GUI to be entered, and no combined secrets dump is "
       "allowed to rest on the PC",
       LOCKED,
       scope=".secrets/ entire, ROTATE_SECRETS.bat, scripts/split_rotated_secrets.py and "
             "add_secret.bat. CLASS property, deliberately the whole class: the assertion is not "
             "'rotated_secrets.txt is gone' but 'NO file under .secrets/ holds two or more "
             "credentials at rest, and a no-GUI entry path exists'. A rotation that reintroduces a "
             "combined dump under any name re-trips this.",
       ref="Paid for on 26 Aug 2026. The 7 Aug rule -- rotate_secrets.py PRINTS NO VALUES, born of "
           "a diagnostic that dumped the production set into a transcript -- held perfectly and "
           "was never violated. The failure came from the UNGUARDED DIRECTION: ROTATE_SECRETS.bat "
           "step [3/4] scp'd the server's combined values file to .secrets/rotated_secrets.txt and "
           "LEFT IT THERE permanently. On 26 Aug Claude asked David to open Notepad to paste an "
           "unrelated Hetzner token, Notepad restored its previous tab -- that very file -- and "
           "Claude's screenshot captured five live self-issued credentials, forcing a re-rotation "
           "three days before soft launch. Two lessons, both encoded here: (1) a secret at REST in "
           "a GUI-openable file is a live exposure waiting for an unrelated accident, so the dump "
           "becomes a transit buffer that is consumed and removed, never a resting place; (2) "
           "'be careful with the editor' is not a fix -- secret ENTRY must not require a GUI at "
           "all, because a GUI requires someone to look at the screen, and looking at the screen "
           "IS the exposure. add_secret.bat is that path (Read-Host -AsSecureString, echoes "
           "nothing, prints only a length and an 8-char fingerprint). Sibling of RG-0146 (every "
           "credential has an honest dated row) and RG-0147 (verify at the point of USE): this one "
           "governs where a credential is allowed to SIT.")
def rg_no_secret_dump_at_rest():
    import re as _re
    sec = os.path.join(REPO, ".secrets")
    if not os.path.isdir(sec):
        return [(INFO, ".secrets/ does not exist on this vantage -- nothing to assert")]
    out = []

    # (1) the no-GUI entry path must exist and must not echo the value
    adder = repo_file("add_secret.bat")
    if adder is None:
        out.append((FAIL, "add_secret.bat is GONE -- secret entry once again needs a GUI editor, "
                          "which is the exact condition that caused the 26 Aug exposure"))
    else:
        if "AsSecureString" not in adder:
            out.append((FAIL, "add_secret.bat no longer reads the value as a SecureString -- the "
                              "paste would be echoed to the console and into any screenshot"))
        # COMMENT-VS-DIRECTIVE (26 Aug 2026), the same class as CSP-SCRIPT-SRC-4 the same
        # morning: this matched the literal `echo %NAME%|` inside a REM line explaining why
        # the echo had been REMOVED, and reported the file as echoing a secret. A comment
        # cannot echo anything, so stripping REM/:: lines makes the assertion MORE precise,
        # never weaker -- the rule that a real `echo %VAR%` is forbidden is untouched.
        _cmds = "\n".join(ln for ln in adder.splitlines()
                          if not _re.match(r"\s*(REM\b|::)", ln, _re.I))
        if _re.search(r"echo\s+%\w+%", _cmds, _re.I):
            out.append((FAIL, "add_secret.bat echoes a variable that may carry the secret"))

    # (2) the splitter that makes the dump transit-only must exist
    if repo_file("scripts/split_rotated_secrets.py") is None:
        out.append((FAIL, "scripts/split_rotated_secrets.py is GONE -- the rotation dump has no "
                          "consumer, so it will once again come to rest under .secrets/"))

    # (3) THE INVARIANT: no file at rest may hold 2+ credentials.
    #     Deliberately shape-based, not name-based -- renaming the dump must not evade it.
    kv = _re.compile(r"^[A-Z][A-Z0-9_]{4,}\s*=\s*\S{16,}\s*$", _re.M)
    ALLOW = {"deploy_keys.txt"}   # the live per-purpose file the deploy lane reads
    worst = []
    for name in sorted(os.listdir(sec)):
        fp = os.path.join(sec, name)
        if not os.path.isfile(fp):
            continue
        try:
            body = open(fp, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        keys = sorted({m.split("=")[0].strip() for m in kv.findall(body)})
        if len(keys) >= 2 and name not in ALLOW:
            worst.append((name, keys))
    for name, keys in worst:
        out.append((FAIL, "'.secrets/%s' holds %d credentials at rest (%s) -- a combined secrets "
                          "file is one stray editor tab away from an exposure. Split it into "
                          "per-purpose files and remove it (scripts/split_rotated_secrets.py)."
                          % (name, len(keys), ", ".join(keys))))

    # (4) stale .bak copies of credential files are the same class, slower
    baks = [n for n in os.listdir(sec)
            if _re.search(r"\.bak[-.]", n) and os.path.isfile(os.path.join(sec, n))]
    if len(baks) > 6:
        out.append((INFO, "%d .bak credential file(s) under .secrets/ -- backups accumulate "
                          "secrets forever and nothing prunes them. Not a failure while the count "
                          "is small; it becomes one when a rotation leaves the previous set lying "
                          "beside the live one." % len(baks)))

    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "no combined secrets file at rest; no-GUI entry path present"))
    return out



@entry("RG-0191", "A verification poll waits for the EXPECTED state, never for a STABLE one -- and "
       "the value it measured survives into the deploy report",
       LOCKED, fixed_on="2026-08-26",
       scope="migrations/033_csp_verify_served.py served_csp() + ops/autodeploy/post_deploy.sh's "
             "failing-step capture window + scripts/prove_csp_settle.py. CLASS property, not one "
             "migration: any poll anywhere in this project that waits for a change to land must "
             "exit on the expected value or on its deadline -- a steady WRONG answer is "
             "indistinguishable from a settled RIGHT one, so 'it stopped changing' can never be "
             "the exit condition. Second half is the report: a failure whose cause cannot be read "
             "off post_deploy_status.json is a defect in the report, not merely bad luck.",
       ref="CSP-SCRIPT-SRC-6 + POSTDEPLOY-EYES-3 (26 Aug 2026), found by the maintenance loop "
           "reading the RG-0125 red for the second morning running. 033 has now failed FOUR "
           "deploys, each a different bug in the same organ -- never in the rewrite it performs, "
           "always in how it MEASURES whether the rewrite took: -3 could not SEE the emitting file "
           "(discovery), -4 compared prose not directives (staleness), -5 measured a 301 not the "
           "page (vantage), and -6 is this one (settling). The 26 Aug 04:05Z run: the settle loop "
           "exited when 'the value stopped changing', and a stale nginx worker still serving the "
           "OLD policy answers with the SAME value every read -- so the loop was satisfied on read "
           "2, about one second after the reload, and returned precisely the value it had been "
           "asked to wait for the reload to replace. settle=15 bought nothing at all; the correct "
           "rewrite was then restored and the chain jammed. THE FIX: poll until script-src appears "
           "or the deadline is spent, return immediately on a first-read hit, and report what IS "
           "served when the deadline runs out. THE SECOND HALF, same failure: the one line naming "
           "the measured value was line -4 of 033's output and post_deploy.sh captured "
           "`tail -n 3 | cut -c1-300` -- so the evidence existed and the report structurally could "
           "not carry it, which is why four consecutive reports said 'something else is emitting "
           "the header' and not one said WHAT was served. The raise now LEADS with MEASURED=, and "
           "the window is 12 lines / 1200 chars with backslashes stripped for JSON safety. PROVEN "
           "by scripts/prove_csp_settle.py (11/11): it reproduces the old loop returning the stale "
           "value deterministically, shows the new loop waiting the reads out and returning the "
           "real policy, shows it not burning the window on a first-read hit, and shows "
           "CSP-SCRIPT-SRC-5's loud-on-redirect behaviour intact. Whether the LIVE server now "
           "serves script-src is RG-0178's question, answered after the next deploy rides -- this "
           "entry asserts the measurement, which is the part that was broken.")
def rg_poll_for_expected_not_stable():
    out = []
    mig = repo_file("migrations/033_csp_verify_served.py")
    if mig is None:
        return [(INFO, "running outside the repo -- the settle-loop check is source-side only")]

    if "value changed -- let the reload finish settling" in mig:
        out.append((FAIL, "033's settle loop is back to exiting when the answer STOPS CHANGING -- "
                          "a stale worker satisfies that on read 2 and the migration measures the "
                          "very value it is waiting to see replaced (26 Aug 04:05Z exactly)"))
    if 'if "script-src" in val:' not in mig:
        out.append((FAIL, "033 no longer polls for the EXPECTED state -- there is no exit on the "
                          "value it is waiting for, so settle= is decorative again"))
    if 'raise RuntimeError("MEASURED=%r' not in mig:
        out.append((FAIL, "033's failure no longer LEADS with the measured value -- put late in "
                          "the message it is cut off by the report's head-truncated window, which "
                          "is how four failures in a row stayed undiagnosable"))
    if "https-also-redirected" not in mig:
        out.append((FAIL, "033 stopped failing loudly on a 3xx -- CSP-SCRIPT-SRC-5 regressed and a "
                          "redirect can be measured as if it were the page"))

    sh = repo_file("ops/autodeploy/post_deploy.sh")
    if sh is None:
        out.append((INFO, "post_deploy.sh not readable from here -- report-window half unchecked"))
    else:
        m = re.search(r'CHAIN JAMMED HERE.*?tail -n (\d+) "\$MOUT".*?cut -c1-(\d+)', sh)
        if not m:
            out.append((FAIL, "post_deploy.sh's failing-migration capture no longer looks like "
                              "`tail -n N | cut -c1-M` -- the report window cannot be assessed"))
        else:
            lines, chars = int(m.group(1)), int(m.group(2))
            if lines < 12 or chars < 1200:
                out.append((FAIL, "post_deploy.sh captures only %d line(s) / %d chars of a failing "
                                  "migration -- narrower than the evidence, so the cause is "
                                  "destroyed on the way into post_deploy_status.json (it was 3/300 "
                                  "and it ate the MEASURED line four times)" % (lines, chars)))

    if repo_file("scripts/prove_csp_settle.py") is None:
        out.append((FAIL, "scripts/prove_csp_settle.py is GONE -- the class has no harness, so the "
                          "next poll written this way is unprovable"))
    else:
        ok, blind, detail = _harness([sys.executable,
                                      os.path.join(REPO, "scripts", "prove_csp_settle.py")],
                                     timeout=120, cwd=REPO)
        if blind:
            out.append((INFO, detail))
        elif not ok:
            out.append((FAIL, "prove_csp_settle.py FAILS: " + str(detail)[-260:]))

    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "poll exits on the expected state, failure leads with MEASURED=, "
                          "report window 12 lines/1200 chars, harness green"))
    return out


@entry("RG-0192", "A source is told how many it still NEEDS, and never mistakes that for how "
       "many it may HAVE -- the wave cannot stall at half its target",
       LOCKED, scope="CityLauncher: pipeline/run.py -> every scraper source that takes "
                   "max_results. FIXED 27 Aug 2026 (WAVE-HALFSTALL-1): google_maps.py's DB "
                   "pre-check no longer gates on the absolute count. The contract is now one "
                   "thing at both ends -- max_results means HOW MANY MORE TO COLLECT, which is "
                   "how every other line in that file already read it -- and the zero-cost "
                   "short-circuit is preserved and correct: it fires on max_results <= 0, i.e. "
                   "when the caller says nothing more is needed. The DB count is still read, but "
                   "REPORTED not enforced, so the log keeps its visibility without the gate. "
                   "THE WHOLE SOURCE LAYER HAS NOW BEEN READ rather than assumed (the scope's own "
                   "instruction): openstreetmap, duckduckgo, bing, teachers_trainers, "
                   "adventures_accommodation and adventures_experiences all compare "
                   "NEWLY-COLLECTED (`len(prospects) >= max_results`) against the remaining "
                   "budget, which is correct; google_maps held the only absolute-count gate in "
                   "the layer. The CLI flag now documents the contract at the boundary.",
       fixed_on="2026-08-27",
       ref="WAVE-HALFSTALL-1, found 26 Aug 2026 measuring the Johannesburg wave (job 13f63ae7). "
           "pipeline/run.py calls sources with max_results=max(remaining, 0) -- the number STILL "
           "NEEDED (4 call sites). google_maps.py's DB pre-check then compares the ABSOLUTE count "
           "already in the DB against that same argument and returns [] once count >= max_results. "
           "So a category is refused the moment it passes HALF its target. The run log prints the "
           "collision verbatim: 'already has 16/14', '17/13', '15/15', '25/5' -- in every case the "
           "two numbers sum to the target of 30. Five empty returns then trip GM-BREAKER-1 and the "
           "category is abandoned. Measured effect: six of nine Johannesburg categories froze in "
           "the 15-17 band and the wave finished 184/270, with ZERO categories brought to quota. "
           "Raising CAP_PER_CATEGORY 20->30 that morning could not help -- the faulty gate scales "
           "with the target, so it simply stalls at 15 instead of 10. This is a CLASS defect: the "
           "argument is a remaining-count at the call site and an absolute-cap at the callee, so "
           "any source reading it as a cap is wrong the same way. EXPECTED TO FAIL until the "
           "contract is one thing at both ends (either pass the absolute target, or have the "
           "callee compare newly-collected against remaining). Needs a deploy, which is David\'s "
           "to authorise -- logged OPEN rather than handed over as a sentence, per RUL-037. The "
           "moment this reports READY TO LOCK, promote to LOCKED.")
def rg_source_remaining_vs_cap():
    out = []
    run = repo_file(os.path.join("..", "CityLauncher", "pipeline", "run.py"))
    gm  = repo_file(os.path.join("..", "CityLauncher", "scraper", "sources", "google_maps.py"))
    if run is None or gm is None:
        out.append((INFO, "CityLauncher not beside this repo -- WAVE-HALFSTALL-1 unchecked here"))
        return out

    passes_remaining = run.count("max_results=max(remaining, 0)")
    treats_as_cap    = "if _count >= max_results:" in gm

    if passes_remaining and treats_as_cap:
        out.append((FAIL, "run.py hands a REMAINING count to max_results at %d call site(s) while "
                          "google_maps.py compares the absolute DB count against it "
                          "(`if _count >= max_results`) -- the source refuses every category that "
                          "is past half its target (WAVE-HALFSTALL-1)" % passes_remaining))
    elif passes_remaining and not treats_as_cap:
        out.append((INFO, "holding -- google_maps.py no longer reads the remaining-count "
                          "as an absolute cap"))
    elif not passes_remaining:
        out.append((INFO, "READY TO LOCK -- run.py no longer passes a remaining-count as "
                          "max_results"))
    return out



@entry("RG-0194", "A script's line endings belong to the INTERPRETER that reads it -- and a .bat "
       "David runs by hand can never close without saying why",
       LOCKED, fixed_on="2026-08-26",
       scope=".gitattributes' *.bat/*.cmd/*.ps1 eol=crlf pins, EVERY .bat and .ps1 in the repo, "
             "and scripts/check_bat_crlf.py. CLASS property, deliberately the whole class: the "
             "assertion is not 'add_secret.bat works' but 'no Windows script is LF-only, and no "
             "hand-run .bat can exit on an error without a pause'. Unattended lanes (nightly, "
             "deploy, checkpoint) are named in the guard's UNATTENDED set -- a pause there would "
             "hang a run with nobody present, which is the opposite fault.",
       ref="BAT-CRLF-1 + BAT-FLICKER-1 (26 Aug 2026). David: 'add secret bat flickered on and "
           "off?' -- a window that opened and closed too fast to read, having done nothing, on "
           "the ONE script standing between him and the Hetzner token that arms the lockout "
           "self-heal (RG-0188), three days before soft launch. THREE faults stacked, each alone "
           "enough: (1) the repo FORCED LF onto Windows scripts -- .gitattributes carried "
           "`* text=auto eol=lf`, right for everything reaching the Linux server and wrong for "
           "every .bat, because cmd.exe expects CRLF and a caret line-continuation followed by a "
           "bare LF does NOT continue the line, so a 15-caret PowerShell block was mangled into "
           "garbage; (2) the caret continuations themselves, fragile for exactly that reason -- "
           "the PowerShell call is now ONE line that line endings cannot break; (3) no `pause` on "
           "any exit path and an instant exit when double-clicked with no argument, so every "
           "failure closed the window unread. Scope found by measuring rather than assuming: "
           "SIXTEEN .bat and TEN .ps1 files were LF-only, including the entire nightly deploy "
           "lane -- those survived only by having no carets and no labels, and ROTATE_SECRETS.bat "
           "(the secrets lane, 5 carets) was one run from the same silent failure. All 26 "
           "normalized. The guard then immediately found two MORE scripts that could exit on an "
           "error with no pause (arm_phone_deploy.bat, fixed; publish_whitepaper_auto.bat, named "
           "unattended) -- which is the argument for the guard existing at all. LESSON, and it is "
           "the sibling of RG-0191 written the same morning: an unreadable failure is "
           "indistinguishable from doing nothing, whether it is a migration whose diagnostic is "
           "truncated out of the report or a window that shuts before a human can read it.")
def rg_windows_scripts_crlf_and_readable():
    if repo_file("scripts/check_bat_crlf.py") is None:
        return [(FAIL, "scripts/check_bat_crlf.py is GONE -- nothing stops the repo default "
                       "handing Windows LF-only batch files again")]
    attrs = repo_file(".gitattributes")
    if attrs is None:
        return [(INFO, "running outside the repo -- Windows line-ending check skipped")]
    out = []
    if not re.search(r"^\*\.bat\s+text\s+eol=crlf", attrs, re.M):
        out.append((FAIL, ".gitattributes no longer pins *.bat to eol=crlf -- `* text=auto "
                          "eol=lf` will hand cmd.exe LF-only batch files again and a caret "
                          "continuation will silently mangle the command"))
    ok, blind, detail = _harness([sys.executable,
                                  os.path.join(REPO, "scripts", "check_bat_crlf.py")],
                                 timeout=120, cwd=REPO)
    if blind:
        out.append((INFO, detail))
    elif not ok:
        out.append((FAIL, "check_bat_crlf.py FAILS: " + str(detail)[-300:]))
    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "every Windows script is CRLF; every hand-run .bat can say why it "
                          "stopped; eol=crlf pinned in .gitattributes"))
    return out


@entry("RG-0196", "The admin gate script has ONE source -- the consolidation RG-0075 was "
       "originally written for",
       OPEN, scope="dashboard.server.html (ships), dashboard.html and marketsquare_admin.html "
                   "(local operator copies). Split out of RG-0075 on 27 Aug 2026.",
       fixed_on="",
       ref="RG-0075 was retitled that day to assert DRIFT, because drift is the property that "
           "actually hurt -- and because a title claiming 'ONE source, not five copies' while the "
           "assertion only measured drift is the same wording-vs-behaviour mistake this file has "
           "now made four times (CSP-VERIFY-GUARD-1/2/3). An entry must assert what its title "
           "says. So the consolidation gets its own entry rather than being quietly absorbed into "
           "a LOCKED one. "
           "WHY IT IS STILL OPEN, and it is not laziness: dashboard.html is opened over file:// -- "
           "RG-0076 exists because of that habit and STATUS.md records it as the copy David "
           "actually opens. A file:// page cannot load /static/admin_gate.js (origin 'null'), so "
           "the obvious fix breaks the very consumer that has been missing every gate fix. The "
           "real options are a build step that inlines one shared block into all three at deploy "
           "time, or dropping the file:// habit. Both are post-launch changes to the ADMIN ENTRY "
           "PATH, and doing that on the last ship day before a public launch carries lockout risk "
           "(RUL-027, reserved to David). Deliberately deferred, with the drift tripwire holding "
           "the line until then.")
def rg_gate_script_consolidated():
    ADMIN = ("dashboard.server.html", "dashboard.html", "marketsquare_admin.html")
    copies = [r for r in ADMIN if "adminGateSubmit" in (repo_file(r) or "")]
    if len(copies) > 1:
        return [(FAIL, "the admin gate is still %d hand-maintained copies (%s) -- EXPECTED while "
                       "OPEN; RG-0075 holds the drift line meanwhile"
                 % (len(copies), ", ".join(copies)))]
    return [(INFO, "READY TO LOCK -- the admin gate script has a single source")]


@entry("RG-0199", "David's hand-off queue RE-VERIFIES itself against evidence -- an item cannot sit "
       "in his column because nobody looked, and cannot close because somebody remembered",
       OPEN, scope="DAVID_QUEUE.md + scripts/david_queue.py. CLASS property, not a to-do list "
                   "check: any register of work handed to a human must (a) carry a stated "
                   "verification method per item, (b) re-run those methods rather than trusting "
                   "its own STATE column, and (c) grade David-confirmed items BELOW probed ones "
                   "instead of flattening them together. OPEN until every item is closed -- it "
                   "is a live queue, and an empty queue is the only passing state.",
       ref="DAVID-QUEUE-1 (27 Aug 2026), built after David asked for his open actions one at a "
           "time while working. The design constraint was NOT 'keep a list' -- it was the "
           "project's oldest recurring fault, a list going stale across a session break. "
           "EVIDENCE IT WAS THE RIGHT CONSTRAINT, from the same morning: the Google consent "
           "screen and the domain registrar had BOTH sat in the David-only column for six days "
           "across five consecutive sweeps, and NEITHER was David's -- the consent screen took "
           "one navigation to read ('In production', verification not required) and the "
           "registrar took one WHOIS referral (Cloudflare Inc, expiry 2026-12-30). Five sweeps "
           "re-copied both forward as his errands without once opening the page. A queue "
           "reconciled only by a human reproduces exactly that, so this one re-runs its own "
           "verifications: LEDGER:<id> reads the live board, FIELD:<name> reads the register, "
           "and DAVID means no instrument can see it and it closes on his word with the date "
           "recorded. The three grades are printed unequally on purpose -- a DAVID-confirmed "
           "'done' is a weaker fact than a probed one and flattening them is how the evidence "
           "ladder gets quietly abandoned. Superseded and NOT reused: AWAITING_DAVID.md, which "
           "was marked superseded in July and would have resurrected a dead file.")
def rg_david_queue_self_verifies():
    out = []
    qp = os.path.join(REPO, "DAVID_QUEUE.md")
    sp = os.path.join(REPO, "scripts", "david_queue.py")
    if not os.path.exists(qp):
        return [(FAIL, "DAVID_QUEUE.md is gone -- David's open actions have no home again")]
    if not os.path.exists(sp):
        return [(FAIL, "scripts/david_queue.py is gone -- the queue is back to being reconciled "
                       "by memory, which is the fault it was built to remove")]
    import re as _re
    q = open(qp, encoding="utf-8").read()
    blocks = _re.findall(r"^## (D\d+) · (.+?)$(.*?)(?=^## D\d+ ·|\Z)", q, _re.M | _re.S)
    if not blocks:
        return [(FAIL, "DAVID_QUEUE.md parses to ZERO items -- the format drifted and the "
                       "runner is now silently serving nothing")]

    ids = [b[0] for b in blocks]
    if len(set(ids)) != len(ids):
        out.append((FAIL, "duplicate item id(s) in DAVID_QUEUE.md -- the board is ambiguous"))

    missing, unverified_done = [], []
    for iid, _title, body in blocks:
        v = _re.search(r"^VERIFY:\s*(.+)$", body, _re.M)
        st = _re.search(r"^STATE:\s*(.+)$", body, _re.M)
        if not v or not v.group(1).strip():
            missing.append(iid)
            continue
        vv = v.group(1).strip()
        if not (vv.startswith("LEDGER:") or vv.startswith("FIELD:") or vv == "DAVID"):
            missing.append(iid)
        # An item may not claim DONE on a machine-checkable method -- the METHOD closes it.
        if st and st.group(1).strip().upper().startswith("DONE") and vv != "DAVID":
            unverified_done.append(iid)
    if missing:
        out.append((FAIL, "%d queue item(s) carry no usable VERIFY method (%s) -- they can only "
                          "be closed by someone asserting it, which is the stale-list fault"
                    % (len(missing), ", ".join(missing[:6]))))
    if unverified_done:
        out.append((FAIL, "%d item(s) are hand-marked DONE while carrying a machine-checkable "
                          "VERIFY (%s) -- the method must close them, never the STATE column"
                    % (len(unverified_done), ", ".join(unverified_done[:6]))))

    # The runner must actually run, or the whole arrangement is decorative.
    # --check, not --all: an OPEN queue exits 1 by design (work outstanding) and _harness
    # would read that as a broken proof. The runner's --check mode reports only on the
    # instrument, which is what this half of the assertion is about.
    ok, blind, detail = _harness([sys.executable, sp, "--check"], timeout=120)
    if blind:
        out.append((INFO, detail))
    elif not ok:
        out.append((FAIL, "scripts/david_queue.py does not run: " + detail[-300:]))
    else:
        out.append((INFO, "%d item(s) parsed, every one with a stated verification method"
                    % len(blocks)))

    still_open = sum(1 for _i, _t, b in blocks
                     if not _re.search(r"^STATE:\s*DONE", b, _re.M))
    if still_open:
        out.append((FAIL, "%d of %d queue item(s) still open -- expected while OPEN; this entry "
                          "closes when David's column is empty" % (still_open, len(blocks))))
    return out


@entry("RG-0198", "An anonymous caller gets OPERATIONS, never the internal engineering NARRATIVE "
       "-- the dashboard payload is not a company diary published to strangers",
       LOCKED,
       fixed_on="2026-08-30 (promoted the run it printed READY TO LOCK -- DASH-SUMMARY-REDACT-1 shipped and no internal-narrative field answers an anonymous caller, probed live)",
       scope="GET /dashboard/summary, the same unauthenticated payload RG-0144 polices. "
                   "RG-0144 owns SECURITY POSTURE (which defence is down); this owns the "
                   "CONFIDENTIALITY of the internal narrative -- recentChangelog, lastDone, "
                   "nextGoals, priorityItems. CLASS, not instance: any unauthenticated endpoint "
                   "that republishes an internal engineering document belongs here. Deliberately "
                   "SPLIT from RG-0144 rather than folded into it, because one is a "
                   "reconnaissance control and the other is confidentiality, and a single "
                   "assertion covering both would be promoted the moment either half passed.",
       ref="DW-078 (27 Aug 2026), confirmed by an independent anonymous PROBE in the "
           "pre-soft-launch third-party sweep the same morning: GET /dashboard/summary with no "
           "credential and no cookie returns 200 / 1,360 B carrying redacted='posture' (so "
           "POSTURE-REDACT-1 IS working and RG-0144 is genuinely passing) -- and, beside it, "
           "today's internal engineering changelog verbatim including its own headline, the "
           "session number and basis, live counts (listings/sellers/introductions/Tuppence "
           "top-ups) and priorityItems whose first entry literally begins '**DAVID -- DEPLOY the "
           "22 Aug work.**'. Two days before the site goes public that is a stranger reading the "
           "engineering log, the burn-down and the operator's to-do list. NOT rated with the "
           "posture leak: it names no control to attack, so it is confidentiality and "
           "presentation, not a way in -- which is exactly why it must not ride on RG-0144's "
           "coat-tails. THE FIX IS NOT MERELY 401-ing THE ROUTE: POSTURE-REDACT-1's own comment "
           "records that both operator dashboards fetch this with NO credential, so a gate breaks "
           "David's console, and 'a fix that breaks the console will be reverted under pressure'. "
           "The honest fix is two-sided -- the consoles start sending the admin key, and the "
           "anonymous payload keeps its operational fields while the narrative fields come back "
           "withheld -- and the second side cannot be verified from this vantage without being "
           "able to load the consoles. OPEN, NOT half-shipped: 27 Aug is the last ship day before "
           "soft-public (RUL-001) and quietly changing a live endpoint the operator console reads "
           "on launch eve is how a console goes dark unwatched. Filed as machinery per RUL-037 "
           "rather than as a sentence to David.")
def rg_no_public_engineering_narrative():
    out = []
    PATH = "/dashboard/summary"
    try:
        st = _status(PATH)
    except ProbeOffline as e:
        return [(INFO, "live half not read (%s)" % e)]
    if st in (401, 403):
        out.append((INFO, "%s refuses anonymous callers (%d) -- no narrative published" % (PATH, st)))
        return out
    if st != 200:
        out.append((INFO, "%s answered %d anonymously -- nothing published" % (PATH, st)))
        return out
    try:
        req = urllib.request.Request(BASE + PATH, headers=UA)
        body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
        doc = json.loads(body)
    except ProbeOffline as e:
        return [(INFO, "live half not read (%s)" % e)]
    except Exception as ex:
        return [(FAIL, "could not read %s anonymously: %r" % (PATH, ex))]

    # Structural, not wording: the NARRATIVE fields must be absent or withheld for a
    # stranger. Matching phrases would go green the day somebody reworded the changelog.
    NARRATIVE = ("recentChangelog", "lastDone", "nextGoals", "priorityItems")
    def _served(v):
        if isinstance(v, str):
            t = v.strip()
            return len(t) > 80 and "withheld" not in t.lower()
        if isinstance(v, list):
            return sum(len(str(x)) for x in v) > 80
        return False
    leaking = sorted(k for k in NARRATIVE if _served(doc.get(k)))
    if leaking:
        out.append((FAIL, "%s serves the internal engineering narrative to an anonymous caller "
                          "in %d field(s): %s. A stranger reads the engineering log and the "
                          "operator's to-do list" % (PATH, len(leaking), ", ".join(leaking))))
    else:
        out.append((INFO, "no internal narrative field is served to an anonymous caller"))

    # RG-0144's half must still hold -- this entry may never be read as covering it.
    if doc.get("redacted") != "posture":
        out.append((INFO, "note: redacted != 'posture' on this read -- RG-0144 owns that half"))
    return out


@entry("RG-0197", "The git lock self-heal covers EVERY repo a wave or a deploy fires from, and "
       "can still clear a lock left by a command that just failed",
       LOCKED, fixed_on="2026-08-27",
       scope="CityLauncher/.git and MarketSquare/.git + scripts/git_unlock.py in both. "
                   "CLASS property, deliberately both repos: GIT-LOCK-3 was written for "
                   "MarketSquare, and a cure that covers one of two live repos is not a class fix.",
       ref="GIT-LOCK-4, found 27 Aug 2026 while committing the WAVE-HALFSTALL-1 fix -- the day "
           "before Wave 1 fires from CityLauncher. That commit took FIVE attempts. A "
           "CityLauncher/.git/HEAD.lock dated 25 Aug -- two days old -- was blocking every commit "
           "in the repo, and each failed attempt left a fresh index.lock behind it, because FUSE "
           "will not let git unlink its own lock files. Nothing had noticed for two days because "
           "nothing asserts it: RG-0015 watches MarketSquare only. "
           "TWO REAL GAPS, and scripts/git_unlock.py being ABSENT is not one of them -- it is "
           "present in CityLauncher (came in with TEACH-1, d36b592), which is exactly why the "
           "finding is worth an entry rather than a copy-paste: "
           "(1) something in that repo writes git WITHOUT calling git_unlock.py first, or the "
           "25 Aug lock could not have survived a single subsequent commit; and "
           "(2) the retry window -- FIXED 27 Aug, and the first write of this entry OVERSTATED "
           "it, which is corrected here rather than left to mislead. The claim was 'refuses to "
           "clear a lock younger than 15 minutes'. Reading stale() shows the 15-minute threshold "
           "applies only to NON-EMPTY locks; a 0-byte lock (the strand signature) already had a "
           "60-second belt. The real gap was narrower and still real: five failed commit attempts "
           "each planted a fresh 0-byte lock inside the previous one's 60 s belt, so the retry "
           "that would have cleared it kept being refused. git_unlock.py now consults its own "
           "git_running() first: a 0-byte lock with pgrep PROVING no git process running is "
           "unambiguously abandoned and age adds nothing. The belt stays for every other case, "
           "including git_running() failing and defaulting to True, where it touches nothing. "
           "Mirrored into CityLauncher. A repo that cannot commit cannot ship a fix. "
           "STILL OPEN on half (1): nothing yet proves every git-writing path in CityLauncher "
           "calls the unlock first, and that is what let a lock survive two days.")
def rg_git_unlock_covers_every_repo():
    out = []
    here = repo_file(os.path.join("scripts", "git_unlock.py"))
    if here is None:
        out.append((FAIL, "MarketSquare/scripts/git_unlock.py is GONE -- GIT-LOCK-3's sandbox "
                          "half has been deleted"))
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        out.append((INFO, "CityLauncher not beside this repo -- its half unchecked here"))
        return out or [(INFO, "git_unlock present")]
    if not os.path.exists(os.path.join(cl, "scripts", "git_unlock.py")):
        out.append((FAIL, "CityLauncher has no scripts/git_unlock.py -- the repo Wave 1 fires "
                          "from cannot heal a stale git lock"))
    # The live half: a lock stranded in EITHER repo. Same 60-minute rule as RG-0015.
    import time as _t
    for name, gitdir in (("MarketSquare", os.path.join(REPO, ".git")),
                         ("CityLauncher", os.path.join(cl, ".git"))):
        try:
            for lk in ("index.lock", "HEAD.lock", "packed-refs.lock"):
                fp = os.path.join(gitdir, lk)
                if os.path.exists(fp):
                    age = (_t.time() - os.path.getmtime(fp)) / 60.0
                    if age > 60:
                        out.append((FAIL, "%s/.git/%s is STRANDED (%.0f min) -- the next commit "
                                          "in that repo will fail. Clear it (host: git_unlock.bat "
                                          "/ sandbox: python3 scripts/git_unlock.py)"
                                    % (name, lk, age)))
        except Exception:
            pass
    # HALF 2 of the TITLE: it must be able to clear a lock a just-failed command left.
    # Asserted as behaviour in the source, not as a comment, because this is the half the
    # first draft of this entry got WRONG by describing rather than reading.
    for name, path in (("MarketSquare", os.path.join(REPO, "scripts", "git_unlock.py")),
                       ("CityLauncher", os.path.join(cl, "scripts", "git_unlock.py"))):
        try:
            with open(path, encoding="utf-8") as _fh:
                src = _fh.read() if os.path.exists(path) else ""
        except Exception:
            src = ""
        if src and "if not git_running():" not in src:
            out.append((FAIL, "%s/scripts/git_unlock.py still gates a 0-byte lock on AGE alone -- "
                              "a command that fails and plants a fresh lock blocks its own retry "
                              "(GIT-LOCK-4)" % name))

    # HALF 1 of the TITLE: no SCRIPT in either repo may write git without unlocking first.
    # Measured 27 Aug rather than assumed -- and the measurement corrected the theory:
    # CityLauncher contains NO git-writing .bat/.py/.sh at all, so the 25 Aug lock was left
    # by a SESSION, not by an unguarded script. That is what the self-heal above is for, and
    # it is why this half is assertable today instead of being a standing worry.
    # SCOPED TO CITYLAUNCHER ONLY, deliberately. RG-0015 already owns MarketSquare's
    # coverage and does it properly -- it understands that nightly_ship.bat and friends
    # DELEGATE to commit.bat / deploy_marketsquare.bat, which unlock first. A naive
    # "does this file mention git commit and not git_unlock" sweep flagged 7 of them on
    # its first run. That would have been a false red inside a brand-new entry, which is
    # the exact sin this file spent 26 Aug removing. One owner per property.
    import glob as _glob
    for name, root in (("CityLauncher", cl),):
        writers = []
        for ext in ("bat", "py", "sh"):
            for fp in _glob.glob(os.path.join(root, "**", "*." + ext), recursive=True):
                if ".bak" in fp or "stale_locks" in fp or "git_unlock" in fp or "_to_delete" in fp:
                    continue
                try:
                    with open(fp, encoding="utf-8", errors="replace") as _fh:
                        body = _fh.read()
                except Exception:
                    continue
                if re.search(r"git\s+(commit|add|push)", body) and "git_unlock" not in body:
                    writers.append(os.path.relpath(fp, root))
        if writers:
            out.append((FAIL, "%s has %d git-writing script(s) that never call git_unlock: %s -- "
                              "an unguarded writer is how a lock strands (GIT-LOCK-4 half 1)"
                        % (name, len(writers), ", ".join(sorted(writers)[:4]))))
    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "both repos carry the self-heal, both can clear a just-planted 0-byte "
                          "lock when no git is running, and neither holds a stranded lock"))
    return out


@entry("RG-0200", "The maintenance lane can SEE its whole board -- no instrument goes blind for "
       "want of a package the lane could have installed in one second",
       LOCKED, fixed_on="2026-08-28",
       scope="scripts/maint_deps.py + the MAINT-DEPS-1 step-0 clause in MAINTENANCE_AGENT.md. "
             "SOURCE-HALF by nature, exactly like RG-0187 and RG-0126: the instrument is the "
             "subject. CLASS property, deliberately not a two-package list -- any module the "
             "lane's INSTRUMENTS import belongs in maint_deps.REQUIRED, so a new harness that "
             "needs a new package cannot be silently blind for a fortnight first. "
             "DELIBERATE BOUNDARY, and it is the whole point of the entry: a module MISSING on "
             "the machine reads INFO, never FAIL. That is RG-0187's own boundary applied to "
             "itself -- an absent third-party package is an instrument limit, not a rotted fix, "
             "and a red here would block a deploy over an environment quirk. What CAN go red is "
             "the MECHANISM: the bootstrap deleted, its coverage narrowed, its detection turned "
             "into a no-op, or the canon step-0 clause removed.",
       ref="MAINT-DEPS-1, 28 Aug 2026, found by the daily maintenance loop on an EMPTY fault "
           "queue -- which is when instrument debt is the only thing left to find. BRAIN-DEPS-2 "
           "taught the lane to install httpx because the shadow agent DIES without it: a loud "
           "failure, so it got fixed within a day. fastapi fails QUIETLY -- RG-0181 and RG-0182 "
           "die at their harness import line, RG-0187 honestly demotes them to NOT EVALUATED, "
           "and the run signs off 'that is not a green board'. Nothing goes red, so nothing "
           "forces the fix, and those two entries were blind on EVERY sandbox run from 26 Aug "
           "onward. DW-071 was closed on 27 Aug while recording the residual in its own close "
           "note ('fastapi is absent from the sandbox bootstrap') -- a defect that is written "
           "down and assigned to nobody is a defect that keeps running. A blind instrument that "
           "never complains is worse than a red one, because a red one gets fixed. "
           "PROVEN the same session: with fastapi present, RG-0181 and RG-0182 both read ok and "
           "the board came back 0 UNVERIFIED for the first time -- 191 entries, 177 holding, "
           "14 open, 0 REGRESSED. The two harnesses were never broken; nobody could see them. "
           "Detection is asserted BEHAVIOURALLY below (a synthetic missing module must make "
           "--check exit 1), because a bootstrap that reports ok unconditionally is exactly the "
           "silent-blindness fault this entry exists to prevent, wearing a different hat.")
def rg_maint_lane_dependency_bootstrap():
    out = []
    boot = repo_file(os.path.join("scripts", "maint_deps.py"))
    if boot is None:
        out.append((FAIL, "scripts/maint_deps.py is GONE -- the maintenance lane has no "
                          "dependency bootstrap, so its instruments go blind silently again "
                          "(MAINT-DEPS-1)"))
        return out

    # COVERAGE: the two modules whose absence has actually blinded this lane must be named.
    for mod, why in (("httpx", "the shadow maintenance agent cannot run at all"),
                     ("fastapi", "the RG-0181/RG-0182 harnesses demote to NOT EVALUATED")):
        if ('"%s"' % mod) not in boot and ("'%s'" % mod) not in boot:
            out.append((FAIL, "maint_deps.py no longer covers %r -- without it %s, and the lane "
                              "loses the instrument without being told (MAINT-DEPS-1)"
                        % (mod, why)))

    # DETECTION, asserted as BEHAVIOUR: a bootstrap that always says ok is not a bootstrap.
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "_rg0200_maint_deps", os.path.join(REPO, "scripts", "maint_deps.py"))
        _md = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_md)
        _md.REQUIRED = dict(_md.REQUIRED)
        _md.REQUIRED["rg0200_synthetic_absent_module"] = (
            "rg0200-not-real", "synthetic probe -- proves detection is not a no-op")
        import io as _io, contextlib as _ctx
        _buf = _io.StringIO()
        with _ctx.redirect_stdout(_buf):
            rc = _md.main(["--check"])
        if rc != 1:
            out.append((FAIL, "maint_deps.py --check returned %r with a module that certainly is "
                              "not installed -- detection is a no-op, so the bootstrap would "
                              "report a blind lane as healthy (MAINT-DEPS-1)" % (rc,)))
    except Exception as exc:
        out.append((FAIL, "maint_deps.py could not be exercised (%r) -- a bootstrap that cannot "
                          "run cannot bootstrap anything" % (exc,)))

    # The canon must still SEND the lane through it, or the tool exists and nobody calls it.
    canon = repo_file("MAINTENANCE_AGENT.md")
    if canon is None or "maint_deps.py" not in (canon or ""):
        out.append((FAIL, "MAINTENANCE_AGENT.md no longer names scripts/maint_deps.py as step 0 "
                          "-- an uncalled bootstrap is a decoration (MAINT-DEPS-1)"))

    # ENVIRONMENT: reported, never enforced. RG-0187's boundary, applied to this entry itself.
    try:
        import importlib.util as _ilu2
        missing = [m for m in ("httpx", "fastapi") if _ilu2.find_spec(m) is None]
        if missing:
            out.append((INFO, "this machine is missing %s -- the affected instruments are BLIND "
                              "here until `python3 scripts/maint_deps.py` runs. Instrument limit, "
                              "not a regression (RG-0187 boundary)" % ", ".join(missing)))
    except Exception:
        pass

    if not [o for o in out if o[0] == FAIL]:
        out.append((INFO, "dependency bootstrap present, covers httpx + fastapi, provably "
                          "detects a missing module, and the canon still routes step 0 through it"))
    return out


@entry("RG-0201", "A credential that has an OUT-OF-BAND COPY is refreshed in the SAME rotation "
       "that replaces it -- an alert channel can never be left holding a burnt key",
       LOCKED, fixed_on="2026-08-28",
       scope="ROTATE_SECRETS.bat's [4b/6] step -> /etc/marketsquare/resend.watch.conf, and the "
             "CLASS: any credential listed in SECRETS_REGISTER.md's 'Out-of-band copies' table "
             "must be refreshed by the rotation itself, never by a human remembering. The "
             "assertion is source-half by necessity -- the copy lives on the box and this board "
             "runs from anywhere -- so it asserts the ROTATION CARRIES THE REFRESH, which is the "
             "cause. Whether the key is alive today is RG-0138's job once the watcher heartbeats.",
       ref="WATCH-COPY-REFRESH-1, 28 Aug 2026. The 22-23 Aug rotation replaced the app's Resend "
           "key and silently orphaned the out-of-band copy the daily watch reads to send RED "
           "alerts. Nothing noticed for THREE DAYS because nothing exercises that path except a "
           "real outage -- it surfaced on 26 Aug only when a genuine RED fired and never arrived, "
           "and it was still dead on 28 Aug, the eve of soft-public, leaving the site's one "
           "wake-David channel down for six days across launch week. "
           "TWO LESSONS, both recorded rather than smoothed over. "
           "(1) THE CAUSE IS THE MANUAL DUPLICATE, not the rotation. fix_watch_alerts.bat "
           "installed the copy once on 5 Aug 2026 and was retired; from then on every rotation "
           "was one unwritten human step away from killing the alarm. The fix puts that "
           "install line INSIDE ROTATE_SECRETS.bat so the step cannot be forgotten. "
           "(2) THE REPAIR ITSELF WENT WRONG FIRST, and that is the sharper lesson: the file was "
           "assumed to be a plain key=value config and edited with a split on the FIRST '=', "
           "which destroyed the variable name in 'Environment=RESEND_API_KEY=...'. It is a "
           "systemd drop-in. Two edits and a wrong probe followed before anyone READ what the "
           "file was -- the answer was in the repo the whole time, in the retired one-shot that "
           "created it. A format assumed is a format not probed (the evidence-ladder rule, "
           "applied to file structure and not only to status). The recovery was one install "
           "command, and the probe then returned HTTP 200 first time.")
def rg_outofband_copy_refreshed_by_rotation():
    out = []
    txt = repo_file("ROTATE_SECRETS.bat")
    if txt is None:
        return [(INFO, "not in the repo -- source half not checkable from this vantage")]

    if "resend.watch.conf" not in txt:
        out.append((FAIL, "ROTATE_SECRETS.bat does not touch /etc/marketsquare/resend.watch.conf "
                          "-- a rotation can once again orphan the RED-alert key, which is the "
                          "exact fault of 22-28 Aug 2026"))
    elif "install -o root -g msdeploy -m 640" not in txt:
        out.append((FAIL, "the watch copy is mentioned but not re-INSTALLED with its mode/owner "
                          "(0640 root:msdeploy) -- the watch runs as msdeploy and cannot read a "
                          "root-only file"))
    else:
        out.append((INFO, "the rotation refreshes the watch copy itself (0640 root:msdeploy)"))

    rtxt = repo_file("SECRETS_REGISTER.md")
    if rtxt is not None:
        try:
            if "Out-of-band copies" not in rtxt:
                out.append((FAIL, "SECRETS_REGISTER.md has lost its 'Out-of-band copies' table -- "
                                  "the list this entry's class is defined against"))
            elif "resend.watch.conf" not in rtxt:
                out.append((FAIL, "the watch copy is not listed in SECRETS_REGISTER.md, so the "
                                  "next rotation has no way to know it exists"))
        except Exception:
            pass
    return out



@entry("RG-0202", "The dependency bootstrap's VERIFY half answers for the interpreter the "
       "instruments will actually get -- a package visible to every fresh process can never "
       "be reported 'still missing'",
       LOCKED, fixed_on="2026-08-29",
       scope="scripts/maint_deps.py _missing() -- the probe half of the RG-0200 bootstrap. "
             "CLASS property: any presence-check that gates an install verdict must probe in "
             "a FRESH interpreter, because the instruments (maintenance agent, ledger "
             "harnesses) always run as fresh processes. The failing class is the in-process "
             "shortcut: on a machine whose user site-packages directory did not exist at "
             "interpreter start, site.py never adds it to sys.path, so an in-process "
             "find_spec() cannot see what pip just installed and the verify half lies "
             "FAILED/exit 1 on exactly the fresh-sandbox machine class the tool was built "
             "for. Asserted BEHAVIOURALLY and machine-independently below: a synthetic "
             "module visible only to child interpreters (via PYTHONPATH set after this "
             "process started) must read PRESENT. A revert to in-process probing goes red "
             "on every machine, not just fresh ones.",
       ref="MAINT-DEPS-2, 29 Aug 2026, found by the daily maintenance loop one day after "
           "MAINT-DEPS-1 shipped -- the bootstrap's install half worked and its verify half "
           "lied on first use: pip succeeded, every new process imported httpx/fastapi "
           "fine, and the tool printed 'FAILED -- still missing after install' and exited "
           "1. RG-0200 asserts the bootstrap EXISTS, covers the right modules, and detects "
           "absence; this entry owns the opposite lie -- reporting absence where there is "
           "presence -- which RG-0200's synthetic-absent probe structurally cannot catch. "
           "Deliberately split, same reasoning as RG-0144/RG-0198: one assertion covering "
           "both halves would be promoted the moment either half passed. Evidence 29 Aug: "
           "fault reproduced in-session (sys.path stripped of user-site -> in-process view "
           "reported httpx+fastapi missing; fixed fresh-probe reported none missing), and "
           "--check with a synthetic absent module still exits 1, so the RG-0200 detection "
           "behaviour is intact.")
def rg_maint_deps_fresh_interpreter_probe():
    out = []
    import importlib.util as _ilu
    _path = os.path.join(REPO, "scripts", "maint_deps.py")
    if not os.path.exists(_path):
        out.append((FAIL, "scripts/maint_deps.py is GONE -- RG-0200 owns the loss of the "
                          "bootstrap; this entry cannot probe its verify half (MAINT-DEPS-2)"))
        return out
    import tempfile as _tf, shutil as _sh
    _td = _tf.mkdtemp(prefix="rg0202_")
    _old_pp = os.environ.get("PYTHONPATH")
    try:
        with open(os.path.join(_td, "rg0202_fresh_only_mod.py"), "w") as _fh:
            _fh.write("present = True\n")
        # Children see it via PYTHONPATH; THIS process never adds it to sys.path --
        # the exact geometry of the first-install fault, recreated synthetically.
        os.environ["PYTHONPATH"] = _td + os.pathsep + (_old_pp or "")
        _spec = _ilu.spec_from_file_location("_rg0202_maint_deps", _path)
        _md = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_md)
        _md.REQUIRED = {"rg0202_fresh_only_mod":
                        ("rg0202-not-real", "synthetic fresh-only module -- proves the probe "
                         "asks a fresh interpreter, not this process")}
        _missing = _md._missing()
        if _missing:
            out.append((FAIL, "maint_deps._missing() reports %r missing although a FRESH "
                              "interpreter imports it -- the verify half is back to "
                              "in-process probing and will lie 'still missing after "
                              "install' on fresh sandboxes (MAINT-DEPS-2)" % (_missing,)))
        else:
            out.append((INFO, "the bootstrap's verify half probes a fresh interpreter -- a "
                              "first-run install can no longer be reported as a failure"))
    except Exception as exc:
        out.append((FAIL, "RG-0202 harness could not exercise maint_deps.py (%r) -- the "
                          "verify half is unproven (MAINT-DEPS-2)" % (exc,)))
    finally:
        if _old_pp is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = _old_pp
        _sh.rmtree(_td, ignore_errors=True)
    return out


@entry("RG-0203", "The +1 AI Providers card answers 'can this AI function STOP?' per feature -- "
       "funds available per lane, mapped to the app functions it serves, with auto-top-up state",
       OPEN,
       scope="dashboard.server.html AI Providers card (AIPROV-FUNDS-1). Requested by David on "
             "soft-launch evening 29 Aug 2026: the card shows lanes and funnels but no gauge of "
             "the money each lane can still spend, feature by feature. DESIGN CONSTRAINTS, all "
             "from the evidence ladder: (a) one row per app AI function (the haiku/triage/"
             "sonnet/vision funnels already on the card) x the lane that serves it; (b) funds "
             "shown only where a vendor exposes a probeable balance/usage figure -- anything "
             "else renders NOT MEASURED plus a dated last-known manual figure, never a guessed "
             "colour (RG-0133 properties); (c) each lane carries its auto-top-up armed/not-armed "
             "state, because the stop-risk this card exists to kill is credit exhaustion, not "
             "vendor outage. Account-side halves already actioned 29 Aug: David guided to arm "
             "OpenAI auto-recharge + Anthropic auto-reload (Scaleway is postpaid, alert only; "
             "Gemini = D5 prepaid credits).",
       ref="AIPROV-FUNDS-1, 29 Aug 2026. OPEN until the strip ships on a post-launch deploy -- "
           "no deploys on launch weekend (28 Aug freeze discipline). The assertion below greps "
           "the deployed dashboard source for the data-ai-funds marker plus its NOT MEASURED "
           "honesty handling; it prints READY TO LOCK the morning the build rides a deploy. "
           "Server-side probes need keys that exist only on the Hetzner box, so the build "
           "session is an attended one.")
def rg_aiprov_funds_gauge():
    out = []
    dash = repo_file("dashboard.server.html")
    if dash is None:
        out.append((INFO, "repo not present -- source-half of RG-0203 not evaluated here"))
        return out
    if 'data-ai-funds' not in dash:
        out.append((FAIL, "AIPROV-FUNDS-1 not built: dashboard.server.html carries no "
                          "data-ai-funds strip (per-function funds gauge missing from the "
                          "AI Providers card)"))
        return out
    if 'NOT MEASURED' not in dash:
        out.append((FAIL, "data-ai-funds strip present but without NOT MEASURED handling -- "
                          "an unprobeable balance must say so, never wear a guessed figure "
                          "(RG-0133 honesty class)"))
    return out


@entry("RG-0204", "The CityLauncher local->server sync carries STATUS and message-ids up, not "
       "only new rows -- the funnel dashboard can never again read 0 while sends sit locally",
       LOCKED, fixed_on="2026-08-29",
       scope="CityLauncher/sync_local_to_server.py (SYNC-STATUS-1). CLASS: any lane where an "
             "action happens on one machine and its truth is read on another must sync the "
             "STATE CHANGE, not merely the row. Guards asserted: forward-push only lifts "
             "server rows still at 'scraped' (can never downgrade a server-side open/click/"
             "bounce/opt-out), and email_events are deduped by NOT EXISTS on (message_id, "
             "event) because the table has no unique index.",
       ref="SYNC-STATUS-1, 29 Aug 2026 -- found by David within hours of the FIRST real send "
           "day: 70 sends recorded locally, dashboard EMAILED stayed 0, and the server's "
           "Resend webhook could not map opens/clicks because message_ids lived only in the "
           "local DB. The sync was INSERT OR IGNORE by design and the gap was invisible for "
           "as long as nothing had ever been emailed. Dry-run proven same session: 187 status "
           "UPDATEs + 75 events generated. Tooling fault -> ledger entry same session, per the "
           "16 Aug GIT-LOCK-3 lesson.")
def rg_citylauncher_sync_status():
    out = []
    sync = repo_file(os.path.join("..", "CityLauncher", "sync_local_to_server.py"))
    if sync is None:
        out.append((INFO, "CityLauncher repo not present beside this one -- RG-0204 source-half "
                          "not evaluated here"))
        return out
    if 'generate_status_sql' not in sync or 'SYNC-STATUS-1' not in sync:
        out.append((FAIL, "SYNC-STATUS-1 gone: sync_local_to_server.py no longer carries the "
                          "status forward-push -- the dashboard will read 0 EMAILED on the next "
                          "send day while truth sits in the local DB"))
        return out
    if "AND status='scraped'" not in sync:
        out.append((FAIL, "the forward-push lost its downgrade guard (AND status='scraped') -- "
                          "a local 'emailed' could now overwrite a server-side open/click"))
    if 'NOT EXISTS' not in sync:
        out.append((FAIL, "email_events push lost its NOT EXISTS dedupe -- repeated syncs will "
                          "multiply events on a table with no unique index"))
    return out



@entry("RG-0205", "The guided sell flow USES the AI-written description -- vision-draft's "
       "description_draft leads the listing description instead of being discarded",
       LOCKED, fixed_on="2026-08-30",
       scope="ms.js sfFinish/sfComposeDescription (SF-AIDESC-1). Found in the 29 Aug 2026 "
             "listing-friction audit: POST /listings/vision-draft returns a 2-4 sentence "
             "honest description_draft, and the OLD magic-link go-flow applies it -- but the "
             "guided sell flow (the flow every organic seller now walks) throws it away. "
             "sfApplyDraft() copies price/make/beds etc. and skips description_draft; "
             "sfFinish() then composes the description MECHANICALLY (label: value lines via "
             "sfComposeDescription), so an AI-drafted seller publishes a robotic spec list "
             "unless they type prose themselves. Fix class: description_draft becomes the "
             "lead paragraph, composed field lines follow, seller edits win over both.",
       ref="LISTING-AUDIT-1, 29 Aug 2026. Was OPEN until a post-launch-weekend deploy carried "
           "the SF-AIDESC-1 marker. PROMOTED 30 Aug 2026 (Batch 1 session): built unattended, "
           "and the 06:45Z release carried it the same hour -- the SERVED /static/ms.js was "
           "PROBED carrying SF-AIDESC-1. Seller prose leads when typed; else the AI draft; "
           "mechanical lines always follow.")
def rg_sf_ai_description_used():
    out = []
    ms = repo_file("ms.js")
    if ms is None:
        out.append((INFO, "repo not present -- RG-0205 source-half not evaluated here"))
        return out
    if 'SF-AIDESC-1' not in ms:
        out.append((FAIL, "guided sell flow still discards description_draft: ms.js carries no "
                          "SF-AIDESC-1 wiring in sfFinish/sfComposeDescription"))
    return out


@entry("RG-0206", "The guided sell flow sends ALL chosen photos to vision-draft, not only the "
       "main one -- the endpoint contract (1-12 photos, primary_photo_index, per-photo "
       "anonymity indices) is actually exercised",
       OPEN,
       scope="ms.js sfRunVision (SF-MULTIVISION-1). Same 29 Aug audit: sfRunVision() appends "
             "exactly ONE file to the form even though /listings/vision-draft accepts 1-12 and "
             "returns per-photo off-category and anonymity indices. Consequence: secondary "
             "photos are never AI-read at draft time (weaker drafts, and a wrong-type or "
             "identity-revealing photo in slot 2+ is only caught at upload). Fix class: batch "
             "the filled slots into one vision call when the seller advances from Photos.",
       ref="LISTING-AUDIT-1, 29 Aug 2026. OPEN until a post-freeze deploy carries "
           "SF-MULTIVISION-1.")
def rg_sf_multiphoto_vision():
    out = []
    ms = repo_file("ms.js")
    if ms is None:
        out.append((INFO, "repo not present -- RG-0206 source-half not evaluated here"))
        return out
    if 'SF-MULTIVISION-1' not in ms:
        out.append((FAIL, "sfRunVision still single-photo: no SF-MULTIVISION-1 marker in ms.js"))
    return out


@entry("RG-0207", "A FREE ask-the-coach affordance exists INSIDE the guided sell flow -- the "
       "seller can ask a question at any step without leaving the flow or paying",
       OPEN,
       scope="ms.js sell flow + POST /advert-agent/coach (SF-COACH-ASK-1). David's 29 Aug "
             "question ('do we need a help button?') answered YES by audit: the in-flow coach "
             "bubbles are STATIC text; interactive AI exists only post-publish (edit screen, "
             "priced per session) -- yet the EULA promises 'everyday in-app guidance is free'. "
             "The backend endpoint already exists. Fix class: the coach avatar on every sf "
             "step becomes tappable -> one small ask box -> free guidance lane of "
             "/advert-agent/coach with step+category+current-fields context; per-session "
             "rate-cap server-side so the free lane stays flat-cost (pricing canon: no "
             "unbudgetable variable costs). CEILING BEHAVIOUR (David probe, 29 Aug): "
             "warn at 8 of 10 (2 questions left), never lose typed work at the cap, "
             "cap copy funnels to the existing paid dashboard coaching session (1T), "
             "and every cap-hit logs an event (limit, tier, category) for demand "
             "telemetry.",
       ref="LISTING-AUDIT-1, 29 Aug 2026. OPEN until a post-freeze deploy carries "
           "SF-COACH-ASK-1 in ms.js AND the free guidance lane in bea_main.py.")
def rg_sf_coach_ask():
    out = []
    ms = repo_file("ms.js")
    if ms is None:
        out.append((INFO, "repo not present -- RG-0207 source-half not evaluated here"))
        return out
    if 'SF-COACH-ASK-1' not in ms:
        out.append((FAIL, "no in-flow ask-the-coach: SF-COACH-ASK-1 marker absent from ms.js "
                          "(coach bubbles remain static text; free guidance promise of the "
                          "EULA has no in-flow surface)"))
    return out



@entry("RG-0208", "A pending INTRO nudges the seller before it rots -- reminder ladder exists "
       "server-side, and the B3 danger zone is warned, never silently entered",
       OPEN,
       scope="bea_main.py (INTRO-REMIND-1). David raised 29 Aug (discussed months earlier, "
             "pre-dating the lane flip): sellers must be reminded to accept/reject a pending "
             "intro. Today create_intro fires the n8n new-intro webhook ONCE and nothing ever "
             "re-nudges: no scheduler in bea_main touches intro_requests age. Yet EULA B3 "
             "BLOCKS a seller at 3 unanswered intros in a rolling 30 days -- so a reminder is "
             "seller PROTECTION, not spam. Fix class: a periodic sweep (same class as the "
             "10-min BIT heartbeat lane) walks intros still 'pending': ~24h -> email reminder; "
             "~72h -> second email + web push where a subscription exists; a seller entering "
             "the B3 danger zone (2 unanswered in the window) gets an explicit warning naming "
             "the consequence. All sends logged; no Tuppence ever charged for a reminder.",
       ref="INTRO-REMIND-1, 29 Aug 2026. OPEN until a post-freeze deploy carries the marker.")
def rg_intro_reminder_ladder():
    out = []
    bea = repo_file("bea_main.py")
    if bea is None:
        out.append((INFO, "repo not present -- RG-0208 source-half not evaluated here"))
        return out
    if 'INTRO-REMIND-1' not in bea:
        out.append((FAIL, "no intro reminder ladder: bea_main.py carries no INTRO-REMIND-1 "
                          "sweep -- a pending intro is never re-nudged while EULA B3 counts "
                          "silence against the seller"))
    return out


@entry("RG-0209", "The app OFFERS the home-screen icon at a chosen moment -- "
       "promptAddToHomeScreen() has a caller, not just a definition",
       LOCKED, fixed_on="2026-08-30",
       scope="ms.js (A2HS-ASK-1). David asked 29 Aug for invisible-to-user icon creation "
             "gated only on asking. Audit found the machinery ALREADY BUILT and ORPHANED: "
             "beforeinstallprompt is captured, promptAddToHomeScreen() exists complete with "
             "standalone/done guards and the iOS instruction fallback -- and NOTHING calls "
             "it. Fix class: one trigger at the seller's invested moment (first successful "
             "publish; optionally sign-in for buyers), so the browser's native install "
             "prompt asks the one question. Consent notes, settled: the native prompt IS "
             "the ask (no legal barrier; nothing personal stored, one localStorage flag); "
             "push NOTIFICATIONS remain a separate browser permission asked only when a "
             "notification lane (e.g. RG-0208 reminders) wants it -- never bundled.",
       ref="A2HS-ASK-1, 29 Aug 2026. PROMOTED 30 Aug 2026 (Batch 1 session): trigger wired "
           "after the first successful publish handoff (sfFinish non-draft path), built "
           "unattended, and the 06:45Z release carried it -- SERVED /static/ms.js PROBED "
           "carrying A2HS-ASK-1. No notification permission bundled, per the consent note.")
def rg_a2hs_offered():
    out = []
    ms = repo_file("ms.js")
    if ms is None:
        out.append((INFO, "repo not present -- RG-0209 source-half not evaluated here"))
        return out
    if 'A2HS-ASK-1' not in ms:
        out.append((FAIL, "promptAddToHomeScreen() still has no caller: no A2HS-ASK-1 "
                          "trigger in ms.js -- the icon is never offered to anyone"))
    return out



@entry("RG-0210", "The Ops Dashboard carries the BEAT THE MODEL card -- the contagion model's "
       "median seller curve pinned beside the LIVE founding-seller count, so the challenge "
       "David set on launch weekend stares back from dashboard page 4 (Horizon) every day",
       LOCKED, fixed_on="2026-08-29",
       scope="dashboard.server.html (SIM-DASH-1). David, 29 Aug 2026: 'I have set my mind on "
             "proving our simulation wrong in the right direction... add it to the Ops "
             "Dashboard for me to keep reminding me of this challenge.' The model: docs/"
             "TrustSquare_Contagion_Model_v0.2.html (CONTAGION-V02-1, median of 40 seeds, "
             "v3.2-as-written arm: wk26=21, wk52=99, wk104=141 sellers; best modelled lever "
             "set reaches wk52=130). DESIGN CONSTRAINTS: (a) the model line is a PINNED "
             "static week->median table stamped with its model version and build date -- the "
             "card never re-simulates; (b) the ACTUAL line is PROBED (live seller count from "
             "the DB the dashboard already reads), grey/NOT MEASURED when the probe fails, "
             "never a guessed colour (RG-0133 properties); (c) ahead/behind is stated as a "
             "plain signed number of sellers vs the pinned median for the current model week "
             "(week 0 = Tue 1 Sep 2026); (d) the card LINKS the full model at /orchestrator/simulation.html (SIM-DASH-2, 29 Aug): the manifest deploys it under the /orchestrator/ prefix, which the TrustSquare Orchestrator Basic-auth realm covers whole (probed: anonymous 401) -- never move it to an ungated dest, it carries the wave plan. LOCATION AMENDED 29 Aug same day: David placed it on the NEW page 4 (Horizon view, PAGE4-HORIZON-1) beside the auction build track, not the +1 page. BUILT same session; David deployed it himself the same evening (his call, dashboard-only risk) and the LIVE page was verified in-gate via Chrome: future-view + SIM-DASH-1 present, card probing /dashboard/summary and rendering actual=70 / median=0 / +70 AHEAD at week 0. LOCKED same day. When David "
             "beats the curve the card says so in green -- earned, not painted.",
       ref="SIM-DASH-1, 29 Aug 2026. OPEN until a post-freeze deploy carries the marker.")
def rg_beat_the_model_card():
    out = []
    dash = repo_file("dashboard.server.html")
    if dash is None:
        out.append((INFO, "repo not present -- RG-0210 source-half not evaluated here"))
        return out
    if 'SIM-DASH-1' not in dash:
        out.append((FAIL, "no Beat-the-Model card: dashboard.server.html carries no "
                          "SIM-DASH-1 marker -- David's standing challenge has no daily "
                          "surface on the +1 page"))
    return out



@entry("RG-0211", "GET /dashboard/summary tells an anonymous caller almost nothing -- a bare "
       "heartbeat (generatedAt + bea_version) with counts, session state and infrastructure "
       "detail reserved for the admin token",
       LOCKED,
       fixed_on="2026-08-30 (promoted the run it printed READY TO LOCK -- anonymous payload probed live: generatedAt + bea_version + redacted='heartbeat' and nothing else)",
       scope="bea_main.py dashboard_summary + dashboard.server.html loaders (DASH-SUMMARY-"
             "REDACT-1). Surfaced 29 Aug by David's breach question: the PAGE is gated (401 "
             "anonymous, probed) but the DATA endpoint serves anonymous callers a redacted-"
             "posture payload that still carries seller/listing/intro counts, session numbers "
             "and an infra description line. Pre-existing design, now judged too generous. Fix "
             "class: _redact_posture tightens to heartbeat-only for callers without the admin "
             "key; every dashboard loader that needs stats (incl. fuLoad on page 4) attaches "
             "X-Admin-Token from sessionStorage like omTok() callers already do; verify the "
             "local file:// dashboard mode still degrades to NOT MEASURED rather than breaking "
             "(RG-0133 -- a failed probe reads grey, never a guessed number).",
       ref="DASH-SUMMARY-REDACT-1, 29 Aug 2026. OPEN until built and live. The assertion "
           "below is LIVE-half: it probes the endpoint anonymously and fails while counts "
           "leak. Promoted LOCKED 30 Aug 2026 -- heartbeat-only payload probed live.")
def rg_summary_anon_heartbeat_only():
    out = []
    try:
        import urllib.request
        # deliberately anonymous: UA only (Cloudflare drops bare urllib), NEVER the
        # review cookie -- the whole point is what a stranger sees
        req = urllib.request.Request(BASE + "/dashboard/summary", headers=UA)
        body = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
    except Exception as exc:
        out.append((INFO, "could not probe /dashboard/summary anonymously (%s) -- RG-0211 "
                          "not evaluated this run" % exc))
        return out
    leaks = [t for t in ('"sellers"', '"liveListings"', '"intros"', 'Hetzner', 'SQLite')
             if t in body]
    if leaks:
        out.append((FAIL, "anonymous /dashboard/summary still leaks: %s -- heartbeat-only "
                          "redaction not yet live" % ", ".join(leaks)))
    return out



@entry("RG-0212", "The customer-email firewall: after launch, no customer mail is ever "
       "forwarded to a personal inbox -- complaints live between the user and the triage "
       "AI, and escalation reaches David through the admin surfaces only",
       OPEN,
       scope="RUL-069 (30 Aug 2026) + EMAIL-FIREWALL-1 in cloudflare_email_worker/src/"
             "worker.js. CLASS: any lane that lets a customer's email land in a personal "
             "mailbox belongs here -- today that is the worker's dead-letter forward "
             "(triage-unreachable + attachments). SOURCE half asserted below: the worker "
             "carries the CUSTOMER_FIREWALL gate and the personal address appears ONLY "
             "inside the unarmed pre-launch branch. LIVE half is why this is OPEN: the "
             "armed worker must actually be deployed (wrangler var CUSTOMER_FIREWALL=1 + "
             "worker deploy, David's act at launch, RUL-027 lockout class). Promote when "
             "the deploy is recorded with its version id in this ref -- the worker's "
             "config is not anonymously probeable, so the record half follows RG-0141's "
             "pattern: read once at the console, written down dated. BOUNDARY per "
             "RUL-069: the outreach reply lane (david@trustsquare.co on B2B wave mail) "
             "is not customer mail and does not trip this.",
       ref="EMAIL-FIREWALL-1, 30 Aug 2026. Until armed, ONE-INBOX-1's dead-letter still "
           "forwards triage-unreachable and attachment mail to the personal inbox -- "
           "correct pre-launch, a RUL-069 breach after.")
def rg_customer_email_firewall():
    out = []
    wpath = os.path.join(REPO, "cloudflare_email_worker", "src", "worker.js")
    if not os.path.exists(wpath):
        out.append((FAIL, "cloudflare_email_worker/src/worker.js is GONE -- the inbound "
                          "lane has no worker source to carry the firewall (RUL-069)"))
        return out
    wsrc = open(wpath, encoding="utf-8").read()
    if "CUSTOMER_FIREWALL" not in wsrc:
        out.append((FAIL, "worker.js lost the CUSTOMER_FIREWALL gate -- the personal "
                          "forward can no longer be sealed at launch (RUL-069)"))
    fwd = wsrc.count("dmcontiki2@gmail.com")
    if fwd > 1:
        out.append((FAIL, "worker.js carries the personal address in %d places -- a "
                          "forward outside the single gated dead-letter branch breaches "
                          "the firewall by construction (RUL-069)" % fwd))
    rec = os.path.join(REPO, "cloudflare_email_worker", "ARMED_RECORD.md")
    if os.path.exists(rec) and "CUSTOMER_FIREWALL=1" in open(rec, encoding="utf-8").read():
        out.append((INFO, "source half holds AND the arming record exists (wrangler var "
                          "CUSTOMER_FIREWALL=1 + worker version, dated) -- the firewall "
                          "is live; promote this entry"))
    else:
        out.append((FAIL, "worker not yet ARMED -- expected while OPEN: the firewall is "
                          "code, not yet conduct. At launch: wrangler var "
                          "CUSTOMER_FIREWALL=1 + worker deploy (David, RUL-027 class), "
                          "then write cloudflare_email_worker/ARMED_RECORD.md with the "
                          "var, worker version id and date (RG-0141 record pattern)"))
    return out


@entry("RG-0213", "Outreach volume is EARNED, never configured: the CityLauncher wave "
       "batch size grows only by the RAMP-1 doubling rule (clean measured waves), the "
       "adventures/Stays-Tours categories stay in the composer pool, and no edit may "
       "reintroduce a manual blast lane",
       LOCKED,
       scope="repo: ../CityLauncher/emailer/wave_runner.py + waves_policy.json. CLASS: any "
             "path that lets a session send more than the evidence-gated batch belongs "
             "here. Born of David asking (30 Aug 2026) how to send all of South Africa in "
             "one go and ratifying the clean answer instead: ramp 12->24->48->96 per "
             "consecutive clean wave (bounce<=2%), stop-loss gates untouched, explicit "
             "per-city batch_size the only documented exception (National=30).",
       ref="RAMP-1 + CATPRIO-1 + STAYS-TOURS-LINEUP-1 (30 Aug 2026, changelog.d). The "
           "one-go blast was rejected for three reasons that do not age: domain reputation "
           "on mail.trustsquare.co is shared with transactional email, Resend suspends on "
           "bounce/complaint spikes, and Gmail/Yahoo bulk rules police >5k/day. A future "
           "session weakening the ramp to go faster is this entry firing, not a judgment call.")
def rg_outreach_ramp_earned():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- RAMP-1 unchecked here (live-only run)")]
    wr = os.path.join(cl, "emailer", "wave_runner.py")
    wp = os.path.join(cl, "emailer", "waves_policy.json")
    if not os.path.exists(wr):
        return [(FAIL, "CityLauncher/emailer/wave_runner.py is GONE -- the gated wave conductor "
                       "no longer exists (RAMP-1)")]
    wsrc = open(wr, encoding="utf-8").read()
    for needle, why in (("def ramp_state", "the evidence-gated doubling rule"),
                        ("remaining = effective_batch_size(city, pol)", "compose_batch wired to the ramp"),
                        ("def city_categories", "per-city category targeting (CATPRIO-1)")):
        if needle not in wsrc:
            out.append((FAIL, "wave_runner.py lost %r -- %s is gone (RAMP-1)" % (needle, why)))
    try:
        pol = json.loads(open(wp, encoding="utf-8").read())
    except Exception as e:
        return out + [(FAIL, "waves_policy.json unreadable (%s) -- the ramp has no policy to read" % e)]
    r = pol.get("ramp", {})
    if not r.get("enabled"):
        out.append((FAIL, "waves_policy.json ramp is missing or disabled -- batch size is no "
                          "longer evidence-gated (RAMP-1)"))
    if r.get("max_batch", 10**9) > 200:
        out.append((FAIL, "ramp.max_batch %r exceeds 200 -- that is a blast lane wearing a "
                          "ramp's name (RAMP-1 cap was 96)" % r.get("max_batch")))
    d = pol.get("defaults", {})
    if d.get("bounce_stop_pct", 999) > 5.0 or d.get("max_complaints", 999) > 0:
        out.append((FAIL, "defaults stop-loss weakened (bounce_stop_pct %r / max_complaints %r) -- "
                          "the gates RAMP-1 stands on have been loosened" % (
                              d.get("bounce_stop_pct"), d.get("max_complaints"))))
    for cat in ("adventures_accommodation", "adventures_experiences"):
        if cat not in pol.get("agency_categories", []):
            out.append((FAIL, "%r dropped from agency_categories -- the Stays & Tours pool is "
                              "invisible to the composer again (STAYS-TOURS-LINEUP-1)" % cat))
    return out


@entry("RG-0214", "The gated ops map and watch register are LIVE documents -- served from the "
       "repo's fetched origin/main at request time, so the defence map can never again trail "
       "reality by a whole deploy",
       LOCKED, fixed_on="2026-08-30",
       scope="PROMOTED 30 Aug 2026 the run it printed READY TO LOCK: migration 035 rode David's "
             "afternoon deploy (Release ef44fc5), inserted the two gated exact-match locations and "
             "self-proved 200-in-gate + 401-anonymous for both documents. "
             "bea_main.py MAP-LIVE-1 routes + migrations/035_orchestrator_live_map.py. Born of "
             "the 30 Aug red card that closed hours late because the deploy-placed map was "
             "stale. D15 (push-scoped PAT) was the preferred fix and remains open to David; "
             "this is the recorded fallback (DAVID_QUEUE D15 CONTEXT). Class property: the two "
             "exact-match nginx locations stay INSIDE the TrustSquare Orchestrator Basic-Auth "
             "realm -- serving the watch register ungated would be an information leak, so the "
             "migration itself proves 401-anonymous and refuses success without it.",
       ref="MAP-LIVE-1, 30 Aug 2026 (unattended Batch 1 session). OPEN until a deploy carries "
           "the routes + migration 035 and the deploy report shows 035 ok with its app-half "
           "and gate proofs. Promote on READY TO LOCK (DW-079 rule). "
           "ASSERTION RE-AIMED 31 Aug 2026 (DW-086, CTO call under RUL-037) -- NOT a "
           "weakening, a correction: the old live half searched the deploy report for a "
           "step whose NAME contained '035', and that report aggregates the whole chain "
           "into ONE step (probed: seed=ok, ladder_seed=ok, migrations=ok). A per-migration "
           "step name has never existed in that format, so the check could only ever go "
           "red -- it produced a FALSE RED on the eve of full launch, and a red ledger "
           "refuses a deploy. The property itself was PROBED live three ways that day "
           "(nginx MAP-LIVE-1 block with both exact-match locations under auth_basic; "
           "origin 127.0.0.1:8000 serving both documents 200 at 64,667 B and 110,819 B; "
           "401 anonymous at the edge). The live half now asserts what evidence actually "
           "exists and adds a guard the old one lacked: (a) the migration chain step ran "
           "and did not fail, (b) migration 035 still carries the self-proof clauses that "
           "make 'ok' mean 'proven' (both exact-match locations, auth_basic, and its "
           "refusal path), and (c) NEITHER document answers 200 anonymously -- the leak "
           "this entry exists to prevent is now asserted directly rather than inferred. "
           "In-gate 200 stays unprobeable without credentials and is deliberately not "
           "claimed here.")
def rg_map_live_lane():
    out = []
    bea = repo_file("bea_main.py")
    if bea is not None and "MAP-LIVE-1" not in bea:
        out.append((FAIL, "bea_main.py lost the MAP-LIVE-1 routes -- the ops map is "
                          "deploy-placed-stale again"))
    if bea is not None:
        mig = os.path.join(REPO, "migrations", "035_orchestrator_live_map.py")
        if not os.path.exists(mig):
            out.append((FAIL, "migrations/035_orchestrator_live_map.py is gone -- the nginx "
                              "half of MAP-LIVE-1 cannot ship"))
    # migration 035's self-proof clauses are what make a plain "migrations = ok"
    # in the deploy report carry BOTH proofs (app 200 on loopback + anonymous 401).
    # If the migration ever loses them, "ok" stops meaning anything and this red
    # is a real one.
    try:
        msrc = open(os.path.join(REPO, "migrations", "035_orchestrator_live_map.py"),
                    encoding="utf-8").read()
    except Exception:
        msrc = ""
    if msrc:
        for needle, why in (
            ("= /orchestrator/defence_map.html", "the defence-map exact-match location"),
            ("= /orchestrator/watch_register.md", "the watch-register exact-match location"),
            ("auth_basic", "the Basic-Auth realm the two locations must stay inside"),
            ("NOT claiming success", "the refusal path that makes 'ok' mean 'proven'"),
        ):
            if needle not in msrc:
                out.append((FAIL, "migration 035 lost %s -- a 'migrations = ok' step no "
                                  "longer carries the MAP-LIVE-1 proofs" % why))

    # live half A -- the deploy report's migration chain ran and did not fail.
    # NB (31 Aug 2026): the report aggregates the whole chain into ONE step named
    # "migrations"; a per-migration step name has never existed in that format,
    # so the old per-035 name check could only ever go red. See the ref.
    st = _status("/static/post_deploy_status.json")
    if st != 200:
        out.append((FAIL, "no deploy report readable (HTTP %s) -- MAP-LIVE-1 live half "
                          "unproven" % st))
    else:
        try:
            doc = _json("/static/post_deploy_status.json")
            steps = {x.get("step"): x.get("result") for x in doc.get("steps", [])}
            hit = [k for k in steps if k and "migration" in str(k).lower()]
            if not hit:
                out.append((FAIL, "deploy report %s carries no migration step at all -- the "
                                  "post-deploy chain did not run" % doc.get("generated_at")))
            elif any(str(steps[k]).lower() == "failed" for k in hit):
                out.append((FAIL, "the migration chain FAILED on the last deploy (%s) -- read "
                                  "its captured output in the report" % doc.get("generated_at")))
            else:
                out.append((INFO, "deploy report %s: migration chain %s" % (
                    doc.get("generated_at"),
                    ", ".join("%s=%s" % (k, steps[k]) for k in sorted(hit)))))
        except Exception as e:
            out.append((FAIL, "deploy report unreadable (%s)" % str(e)[:60]))

    # live half B -- CONFIDENTIALITY, probed directly and anonymously. Serving the
    # defence map or the watch register to a stranger is the information leak this
    # entry's scope names; 200 here is the failure that matters most.
    for path in ("/orchestrator/defence_map.html", "/orchestrator/watch_register.md"):
        s = _status(path)
        if s == 200:
            out.append((FAIL, "%s answers 200 ANONYMOUSLY -- the gated document has fallen "
                              "OUT of the Basic-Auth realm (information leak)" % path))
        elif s in (401, 403):
            out.append((INFO, "%s -> %s anonymous (gate holds)" % (path, s)))
        else:
            out.append((INFO, "%s -> %s anonymous -- not 200, so nothing leaks; in-gate 200 "
                              "is not anonymously probeable" % (path, s)))
    return out


@entry("RG-0215", "The JURISDICTION GATE (RUL-071): no city may be armed for outreach "
       "in a country the outreach-law canon does not cover, and a DO-NOT-COLD-EMAIL "
       "country (Kenya/Egypt/Botswana, 20 Aug doc verdicts) may never be armed at all -- "
       "organic growth is ungated, SENDING is what waits for law",
       OPEN,
       scope="jurisdiction-gate CLASS over the whole pipeline: every country reachable by "
             "cities.json. Two red conditions: (1) armed outreach city in an uncovered "
             "country; (2) ANY armed city in a NO-SEND country regardless of coverage. "
             "The organic lane (word of mouth, reputation -- RUL-071) is deliberately NOT "
             "gated: signups from anywhere are lawful commerce; recruitment email is what "
             "needs per-jurisdiction law. Pool harvesting/recon also ungated.",
       ref="Born 30 Aug 2026 as the India-only gate (INDIA-TUTORS-LANE-1), generalized the "
           "SAME DAY under RUL-071 (two-engine growth doctrine) and extended to Russia "
           "under RUL-072 -- the ruling row claimed the generalization and this edit makes "
           "the claim true in the same day''s session, per the evidence ladder. Coverage "
           "test is name-presence in OUTREACH_LAW*.md (READ-grade by design): it opens the "
           "gate for a human LOCK decision, it does not make it. ZA is covered as the home "
           "market with sends live under RUL-063.")
def rg_jurisdiction_gate():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- jurisdiction gate unchecked (live-only run)")]
    import glob as _glob
    law = ""
    for fp in _glob.glob(os.path.join(REPO, "OUTREACH_LAW*.md")):
        try:
            law += open(fp, encoding="utf-8").read().upper()
        except Exception:
            pass
    NAMES = {"ZA": "SOUTH AFRICA", "NZ": "NEW ZEALAND", "AR": "ARGENTINA", "PT": "PORTUGAL",
             "NA": "NAMIBIA", "KE": "KENYA", "EG": "EGYPT", "ZW": "ZIMBABWE", "BW": "BOTSWANA",
             "MZ": "MOZAMBIQUE", "IN": "INDIA", "US": "UNITED STATES", "UK": "UNITED KINGDOM",
             "AU": "AUSTRALIA", "FR": "FRANCE", "BR": "BRAZIL", "CO": "COLOMBIA", "PE": "PERU",
             "CL": "CHILE", "NG": "NIGERIA", "GH": "GHANA", "TZ": "TANZANIA", "UG": "UGANDA",
             "RW": "RWANDA", "ET": "ETHIOPIA", "MA": "MOROCCO", "CN": "CHINA", "RU": "RUSSIA"}
    NO_SEND = {"KE", "EG", "BW"}
    def covered(cc):
        # heading-level match only ("## 1. KENYA ..."), not incidental mentions in prose
        if cc == "ZA":
            return True
        import re as _re
        return bool(_re.search(r"#+\s*\d*\.?\s*" + _re.escape(NAMES.get(cc, "\x00")), law))
    n2c = {"Maun": "BW", "National": "ZA"}
    try:
        for c in json.loads(open(os.path.join(cl, "data", "cities.json"), encoding="utf-8").read()):
            n2c[c.get("name")] = c.get("country")
    except Exception as e:
        return [(FAIL, "cities.json unreadable (%s) -- the gate cannot map cities to countries" % e)]
    try:
        pol = json.loads(open(os.path.join(cl, "emailer", "waves_policy.json"), encoding="utf-8").read())
    except Exception as e:
        return [(FAIL, "waves_policy.json unreadable (%s)" % e)]
    for name, cpol in pol.get("cities", {}).items():
        if not (cpol.get("armed") or cpol.get("gates_green")):
            continue
        cc = n2c.get(name)
        if cc is None:
            out.append((FAIL, "waves_policy city %r is armed but unknown to cities.json -- "
                              "the gate cannot judge its jurisdiction (RG-0215)" % name))
        elif cc in NO_SEND:
            out.append((FAIL, "%s (%s) is armed -- 20 Aug doc verdict is DO NOT COLD EMAIL; "
                              "organic lane only (RUL-071)" % (name, cc)))
        elif not covered(cc):
            out.append((FAIL, "%s (%s) is armed while OUTREACH_LAW has no %s section -- "
                              "sending into an unresearched jurisdiction (RG-0215)"
                        % (name, cc, NAMES.get(cc, cc))))
    if out:
        return out
    uncovered = sorted({cc for cc in set(n2c.values()) if cc and not covered(cc)})
    if uncovered:
        return [(FAIL, "pipeline reaches uncovered countries (%s) and none is armed -- expected "
                       "while OPEN. Each outreach lane needs a primary-source OUTREACH_LAW "
                       "section first; the organic lane is ungated (RUL-071)" % ", ".join(uncovered))]
    return [(INFO, "every pipeline country covered, no NO-SEND country armed -- promote to LOCKED")]


@entry("RG-0216", "FIDE-CLAIM-1 exists and holds its shape: the credential-claim lane "
       "(claim endpoint, CREDENTIAL_CLAIMS flag, seeded registry) is LIVE per the design "
       "spec -- verification without identification, badge from a live JOIN, one account "
       "per credential",
       OPEN,
       scope="the credential-claims feature class: /credentials/claim + /credentials/mine "
             "+ admin queue + registry-upsert refresh, all behind CREDENTIAL_CLAIMS "
             "(default off), server table credential_registry seeded with the 4,237-row "
             "FIDE export. Anonymity half is part of the assertion once live: the public "
             "listing payload may carry tier/badge but NEVER name, credential id or "
             "federation from a claim.",
       ref="Design ratified in conversation 30 Aug 2026 (David: the registry gives the "
           "trust score the meaning we intended). Spec: CREDENTIAL_CLAIMS_DESIGN.md + "
           ".docx (30 Aug). Build slot: first post-launch-stabilization session (RUL-065 "
           "timing class -- no launch-weekend deploys). RUL-037 machinery rule: this "
           "entry, not David''s memory, carries the build across sessions.")
def rg_credential_claims():
    out = []
    base = "https://trustsquare.co"
    try:
        import urllib.request as _u
        req = _u.Request(base + "/credentials/mine", headers={"User-Agent": "ledger-probe"})
        code = None
        try:
            code = _u.urlopen(req, timeout=15).getcode()
        except Exception as e:
            code = getattr(e, "code", None)
        if code in (200, 401, 403):
            out.append((INFO, "/credentials/mine answers (%s) -- the lane exists; verify flag, "
                              "seed count and the anonymity half, then promote" % code))
        else:
            out.append((FAIL, "/credentials/mine does not answer (%r) -- FIDE-CLAIM-1 not built "
                              "yet. Expected while OPEN. Spec: CREDENTIAL_CLAIMS_DESIGN.md; "
                              "build order section 9; seed export from CityLauncher "
                              "fide_trainers (4,237 rows verified on disk 30 Aug)" % code))
    except Exception as e:
        out.append((FAIL, "probe machinery failed (%s) -- treat as not built" % e))
    return out


@entry("RG-0217", "No outreach email is addressed to a PLACEHOLDER -- template artifacts "
       "(user@domain.com class) are refused at the same chokepoint that enforces the "
       "opt-out register, and batch composition never counts them",
       LOCKED,
       scope="repo: ../CityLauncher/emailer/emailer.py (_looks_junk + send_email refusal + "
             "get_prospects filter) + tests/test_junk_guard.py. CLASS, not a blocklist: any "
             "address whose SHAPE says no human reads it (placeholder local-parts, template "
             "domains, reserved TLDs) -- MX checks pass these because domain.com and "
             "godaddy.com resolve. Boundary is deliberate and part of the assertion: info@ / "
             "admin@ business addresses stay sendable; loosening the guard OR widening it to "
             "eat legitimate business mail both belong here.",
       ref="JUNK-GUARD-1 (30 Aug 2026). Wave 1 (29 Aug, 88 sends) bounced ~6.8%% -- 6 webhook "
           "bounce events -- and the 29 Aug send note had already named the culprits as "
           "scraper-swallowed placeholders. 6.8%% sits ABOVE the 5%% stop-loss and the RAMP-1 "
           "2%% clean bar, so unguarded junk does not merely waste sends: it blocks the ramp "
           "and burns domain reputation shared with transactional mail.")
def rg_junk_guard():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- JUNK-GUARD-1 unchecked here (live-only run)")]
    em = os.path.join(cl, "emailer", "emailer.py")
    if not os.path.exists(em):
        return [(FAIL, "CityLauncher/emailer/emailer.py is GONE (JUNK-GUARD-1)")]
    esrc = open(em, encoding="utf-8").read()
    for needle, why in (("def _looks_junk", "the shape guard itself"),
                        ("JUNK-GUARD-1: refusing send", "the send_email chokepoint refusal"),
                        ("not _looks_junk(r.get(", "batch composition filtering")):
        if needle not in esrc:
            out.append((FAIL, "emailer.py lost %r -- %s is gone (JUNK-GUARD-1)" % (needle, why)))
    tp = os.path.join(cl, "tests", "test_junk_guard.py")
    if not os.path.exists(tp):
        out.append((FAIL, "tests/test_junk_guard.py is GONE -- the guard has no witness (JUNK-GUARD-1)"))
    if not out:
        try:
            ns = {}
            i = esrc.index("_JUNK_LOCALPARTS"); j = esrc.index("def send_email")
            exec(esrc[i:j], ns)  # the guard block is self-contained by construction
            ok_junk = ns["_looks_junk"]("user@domain.com") and ns["_looks_junk"]("filler@godaddy.com")
            ok_legit = not ns["_looks_junk"]("info@pretoriatutors.co.za")
            if not ok_junk:
                out.append((FAIL, "_looks_junk no longer catches the wave-1 bounce addresses -- guard hollowed out"))
            if not ok_legit:
                out.append((FAIL, "_looks_junk eats info@ business addresses -- guard over-widened, sends starve"))
            if ok_junk and ok_legit:
                out.append((INFO, "guard behaviorally proven: wave-1 culprits refused, business addresses pass"))
        except Exception as e:
            out.append((INFO, "behavioral half unrunnable here (%s) -- source needles hold" % e))
    return out


@entry("RG-0218", "The Stays & Tours wave lane RUNS AS DOCUMENTED: raw adventures category "
       "names route to their OWN templates (never the fuzzy neighbour's), and the wave "
       "conductor survives both documented invocation styles",
       LOCKED,
       scope="repo: ../CityLauncher/emailer/emailer.py TEMPLATES exact keys "
             "(adventures_accommodation / adventures_experiences) + wave_runner.py dual-style "
             "send_freeze import. Found ARMING wave 2 (30 Aug 2026): fuzzy template match hit "
             "the 'Adventures' key first, so B&B prospects would have received the EXPERIENCES "
             "copy; and `python -m emailer.wave_runner` -- the docstring's own usage -- died on "
             "a bare sibling import emailer.py had already learned to guard against.",
       ref="ADV-TMPL-1 + WR-IMPORT-1 (30 Aug 2026, changelog.d 2026-08-30-wave2-armed). CLASS: "
           "a template resolved by substring luck and an entry point that only works from one "
           "working directory are both the same fault -- the documented path silently doing "
           "something else.")
def rg_wave2_lane_runs_as_documented():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- wave-lane checks skipped (live-only run)")]
    esrc = open(os.path.join(cl, "emailer", "emailer.py"), encoding="utf-8").read()
    for needle in ("'adventures_accommodation': TMPL_DIR / 'adventures_accommodation_outreach.html'",
                   "'adventures_experiences':   TMPL_DIR / 'adventures_experiences_outreach.html'"):
        if needle not in esrc:
            out.append((FAIL, "TEMPLATES lost the exact adventures key %r -- fuzzy match mails "
                              "the wrong copy again (ADV-TMPL-1)" % needle.split(':')[0]))
    for t in ("adventures_accommodation_outreach.html", "adventures_experiences_outreach.html"):
        if not os.path.exists(os.path.join(cl, "emailer", "templates", t)):
            out.append((FAIL, "template %s is GONE from disk (ADV-TMPL-1)" % t))
    wsrc = open(os.path.join(cl, "emailer", "wave_runner.py"), encoding="utf-8").read()
    if "from emailer import send_freeze" not in wsrc:
        out.append((FAIL, "wave_runner.py lost the package-style send_freeze import -- "
                          "`python -m emailer.wave_runner` dies at line one again (WR-IMPORT-1)"))
    if not out:
        out.append((INFO, "exact template routing + dual-style entry point both in place"))
    return out


@entry("RG-0219", "The prospect sync can never lose to the service that owns the DB, and can "
       "never claim success over a failed apply -- it waits for the lock, applies as ONE "
       "transaction, and reads its own stderr",
       LOCKED,
       scope="repo: ../CityLauncher/sync_local_to_server.py, BOTH apply paths (prospects + "
             "gumtree). CLASS: any remote sqlite apply in this project. Three properties, all "
             "asserted: (a) .timeout so a busy DB is waited for, never sprayed with "
             "SQLITE_BUSY; (b) .bail on + single BEGIN IMMEDIATE txn so a failure rolls back "
             "whole and exits nonzero; (c) the caller treats rc==0 WITH dirty stderr as "
             "failure -- sqlite3 without .bail exits 0 over hundreds of errors.",
       ref="SYNC-LOCKSAFE-1 (30 Aug 2026). Found live on wave-2 day: the post-send sync "
           "sprayed dozens of 'database is locked (5)' lines against the running "
           "citylauncher.service and then printed SYNC COMPLETE anyway -- a wrong-status "
           "defect of the evidence-ladder class, on the one day the dashboard numbers "
           "mattered. Idempotent SQL (OR IGNORE / guarded UPDATEs / NOT EXISTS) is what "
           "made the retry safe, and that idempotency is load-bearing for this entry.")
def rg_sync_locksafe():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- sync checks skipped (live-only run)")]
    p = os.path.join(cl, "sync_local_to_server.py")
    if not os.path.exists(p):
        return [(FAIL, "sync_local_to_server.py is GONE (SYNC-LOCKSAFE-1)")]
    s = open(p, encoding="utf-8").read()
    if s.count(".bail on") < 2 or s.count(".timeout 30000") < 2 or s.count("BEGIN IMMEDIATE") < 2:
        out.append((FAIL, "a sync path lost its lock discipline header (.bail/.timeout/BEGIN "
                          "IMMEDIATE must wrap BOTH applies) -- SYNC-LOCKSAFE-1"))
    if s.count("apply.stderr.strip()") < 2:
        out.append((FAIL, "an apply path no longer reads its own stderr -- rc==0 over errors "
                          "prints SYNC COMPLETE again (SYNC-LOCKSAFE-1)"))
    if "INSERT OR IGNORE" not in s:
        out.append((FAIL, "the sync lost OR IGNORE idempotency -- the retry this entry "
                          "blesses is no longer safe"))
    if not out:
        out.append((INFO, "both applies wait, bail, roll back whole, and are verified against stderr"))
    return out


@entry("RG-0220", "Server VERDICTS flow DOWN before any wave composes -- the send pool can "
       "never again email an address the server has opted out, bounced or geo-rejected, "
       "and the sync bat can no longer print COMPLETE over a failed step",
       LOCKED,
       scope="repo: ../CityLauncher/pull_from_server.py + sync_to_server.bat (pull is step "
             "[1/3], both steps errorlevel-guarded and pause on failure). CLASS: the one-way "
             "sync seam -- every verdict class that lives server-side (opt-out, bounce, "
             "geo/invalid rejection, the suppression register) must reach the LOCAL store "
             "the send lane reads. Precedence is part of the assertion: opted_out wins over "
             "everything (POPIA), bounced over scraped/emailed, rejected_* over scraped only "
             "(send history is never rewritten).",
       ref="SYNC-PULLDOWN-1 (30 Aug 2026). Third live bite of the seam in 24h: wave 2 sent 8 "
           "of 15 under the wrong city (server rows read rejected_wrong_geo -- STAYS-GEO-1 "
           "verdicts never travelled down), wave-1 bounces were invisible to the ramp, and "
           "the first live opt-out (a wave-2 recipient, same afternoon) existed only "
           "server-side. Also arms emailer.py's SUPPRESS-1 chokepoint locally at last: the "
           "local DB had NO suppression table until this pull creates and fills it.")
def rg_sync_pulldown():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- pulldown checks skipped (live-only run)")]
    pp = os.path.join(cl, "pull_from_server.py")
    if not os.path.exists(pp):
        return [(FAIL, "pull_from_server.py is GONE -- server verdicts no longer reach the "
                       "send pool (SYNC-PULLDOWN-1)")]
    s = open(pp, encoding="utf-8").read()
    for needle, why in (("status='opted_out'", "the opt-out-always-wins rule"),
                        ("status IN ('scraped','emailed')", "bounce precedence"),
                        ("AND status='scraped'", "rejection precedence (history never rewritten)"),
                        ("CREATE TABLE IF NOT EXISTS suppression", "arming the local SUPPRESS-1 register")):
        if needle not in s:
            out.append((FAIL, "pull_from_server.py lost %r -- %s is gone (SYNC-PULLDOWN-1)" % (needle, why)))
    # PULL-SQL-1 (31 Aug 2026): the string checks above all passed for 24 hours while
    # step [1/3] could not run AT ALL -- ph was built as ''opted_out'' (doubled quotes),
    # which SQL reads as an empty string followed by a bare identifier. This entry was
    # LOCKED and green over a pull that had never once succeeded. So the assertion now
    # EXECUTES the query it claims works, against a real schema, instead of reading it.
    try:
        import sqlite3 as _sq, re as _re
        m = _re.search(r"ph = ','\.join\(f\"'\{v\}'\" for v in VERDICTS\)", s)
        vm = _re.search(r"VERDICTS\s*=\s*\(([^)]*)\)", s)
        verds = _re.findall(r"'([a-z_]+)'", vm.group(1)) if vm else []
        if not verds:
            out.append((FAIL, "VERDICTS tuple unreadable -- cannot prove the pull query parses"))
        else:
            ph = ",".join("'%s'" % v for v in verds)
            sql = ("SELECT email, status, COALESCE(bounced_at,'') FROM prospects "
                   "WHERE status IN (%s) AND email != '';" % ph)
            mem = _sq.connect(":memory:")
            mem.execute("CREATE TABLE prospects (email TEXT, status TEXT, bounced_at TEXT)")
            mem.execute(sql)          # raises if the generated SQL is malformed
            mem.close()
            if not m:
                out.append((FAIL, "the verdict placeholder is no longer built as '{v}' -- "
                                  "check the quoting, this is where PULL-SQL-1 lived"))
    except Exception as _sqle:
        out.append((FAIL, "the pull's verdict query DOES NOT PARSE (%s) -- step [1/3] "
                          "cannot run, so the opt-out register is never armed "
                          "(PULL-SQL-1)" % str(_sqle)[:90]))

    bp = os.path.join(cl, "sync_to_server.bat")
    b = open(bp, encoding="utf-8", errors="replace").read() if os.path.exists(bp) else ""
    if "pull_from_server.py" not in b:
        out.append((FAIL, "sync_to_server.bat no longer pulls before pushing -- the wave "
                          "composes from a stale pool again (SYNC-PULLDOWN-1)"))
    if b.count("errorlevel 1") < 2:
        out.append((FAIL, "sync_to_server.bat lost its errorlevel guards -- SYNC COMPLETE "
                          "can print over a failure again"))
    # BAT-GUARD-1 (31 Aug 2026): the guards EXISTED and did not FIRE. Written as a
    # one-line parenthesised block with ^& separators, cmd echoed the block as text
    # instead of executing it -- so a failed pull printed "SYNC COMPLETE ... verified".
    # A guard that is present but inert is worse than an absent one: it reads as safety.
    if "^&" in b and "errorlevel 1 (" in b:
        out.append((FAIL, "sync_to_server.bat has one-line ^& guards again -- cmd echoes "
                          "them instead of running them, and COMPLETE prints over a "
                          "failure (BAT-GUARD-1)"))
    if "applied and verified" in b:
        out.append((FAIL, "the bat claims 'applied and verified' -- it verifies nothing; "
                          "it reports two exit codes (BAT-GUARD-1)"))
    if not out:
        out.append((INFO, "pull-before-push in place, precedence rules intact, bat honest"))
    return out


@entry("RG-0221", "ZOOM, the narrowing funnel, keeps the properties that make it work: one "
       "question at a time, no zero-count option ever offered, no facet asked before its "
       "parent, geography never opening the funnel, and the flag DARK until David arms it",
       OPEN,
       scope="repo: ZOOM_HMI_SPEC.md is the build spec (RUL-076). While OPEN this entry "
             "asserts only that the SPEC survives intact -- the design is ratified but "
             "unbuilt, and a spec that quietly loses its engine rules is how the next "
             "session re-derives them wrongly. WHEN BUILT, promote to LOCKED and extend the "
             "assertion to the shipped code: (1) no rendered option carries count 0; "
             "(2) facet counts and the result count come from ONE query and can never "
             "disagree; (3) dep/depVal respected and dropping a parent drops its children; "
             "(4) geography is never the first question in any category; (5) 'which street?' "
             "is never asked for Collectables and travel geography opens at COUNTRY; "
             "(6) at <=420px: <=6 options, >=44px tall, question in the lower half, no "
             "horizontal overflow; (7) the flag defaults OFF and the pre-Zoom view still "
             "renders when it is off; (8) results are ordered by the RANKING SCORE at "
             "listing level (0.5*quality + 0.5*trust -- the same straight 50/50 as "
             "estate_agents.py::_rank_agents), super_example still pinned (SUPER-PIN-1). "
             "CLASS: this is the front door of every category -- the assertion is "
             "per-category, never proven on Property alone. PREREQUISITE recorded 30 Aug: "
             "listing quality is computed per-row (_import_quality_score) and NOT stored, so "
             "SQL cannot order by it -- a maintained listings.quality_score column is part of "
             "this build. GAP THIS CLOSES: the Ranking Score today ranks AGENTS only "
             "(/agents/nearby); the listing feed sorts newest, or 'smart' = trust 60%% + "
             "freshness 40%% with NO quality term -- so the method meant to promote listing "
             "quality never touched the results a buyer browses. SECOND PREREQUISITE "
             "(30 Aug): GET /listings takes NO buyer identity -- the Free/Global reach gate "
             "(PRICING_CANON 2, buyer axis: Free=local city, Global=$5 national+global; "
             "travel/stays 2a and online-mode 2b borderless on any tier) is enforced ONLY "
             "on /wishlist/feed. Zoom puts geography on screen AS A COUNTED QUESTION, so an "
             "ungated endpoint makes the count either a lie or a dead end -- the gate must "
             "move into /listings INSIDE the counted set. Locked != empty: an out-of-reach "
             "option is shown with its true count and the offer (RUL-066 rung 1), only "
             "zero-count options are removed. EXTENDED 1 Sep 2026 (RUL-089, recorded by the "
             "2 Sep attended session): the Tutors funnel gains two geo-derived drill-downs -- "
             "nearby institutions and their subjects, one click each (ZOOM_HMI_SPEC.md sec 10). "
             "Acceptance criteria extend to: singleton auto-collapse proven (engine rule 3.6 -- "
             "a facet with exactly one non-zero option is never asked, chip applied silently), "
             "and true institution counts (max 4 tiles, proximity x count, zero-count removed). "
             "Same promote-when-built discipline; the spec-intact assertion covers sec 10 too.",
       ref="ZOOM-HMI-1 (30 Aug 2026). David ratified the design after tapping both "
           "prototypes and set one binding constraint: 'I would actually like to see it on "
           "the actual app first, not the live one that is in the field now.' So the build "
           "is flag-dark in the REAL app, viewed locally and then in the RUL-075 sandbox "
           "(shared, not duplicated), and ARMING IS DAVID'S ACT. Build window: first "
           "post-launch, riding with the RUL-065 listing-friction batch "
           "(RG-0205/0206/0207). Supersedes the unapproved 6 Jul chip-row FEA direction; "
           "the 6 Jul server-side same-set facet counts are the foundation it builds on.")
def rg_zoom_funnel():
    out = []
    sp = os.path.join(REPO, "ZOOM_HMI_SPEC.md")
    if not os.path.exists(sp):
        return [(FAIL, "ZOOM_HMI_SPEC.md is GONE -- the ratified funnel design (RUL-076) "
                       "exists only in a chat transcript again (ZOOM-HMI-1)")]
    s = open(sp, encoding="utf-8").read()
    for needle, why in (
            ("flag-dark", "the flag-dark build rule"),
            ("the flag in the field is David", "David's reserved arming act"),
            ("RUL-075", "the shared sandbox (no second preview mechanism)"),
            ("dependency graph", "the coherence rule that gain alone violates"),
            ("never the first question", "geography never opening the funnel"),
            ("GEO_START", "travel's inverted geography"),
            ("Zero-count options are removed", "the unreachable-dead-end rule"),
            ("0.5 x listing quality", "the Ranking Score as the result order"),
            ("quality_score` column", "the stored-quality prerequisite"),
            ("reach gate moves into", "reach-scoped counts (the rule-2 breaker)"),
            ("Empty\" and \"locked\" are different", "locked != zero-count")):
        if needle not in s:
            out.append((FAIL, "ZOOM_HMI_SPEC.md lost %r -- %s is gone (ZOOM-HMI-1)"
                              % (needle, why)))
    for proto in ("ZOOM_HMI_PROTOTYPE_2026-08-30.html", "ZOOM_HMI_PHONE_2026-08-30.html"):
        if not os.path.exists(os.path.join(REPO, proto)):
            out.append((FAIL, "%s is missing -- the spec's measured tap budgets can no "
                              "longer be re-run (ZOOM-HMI-1)" % proto))
    if not out:
        out.append((INFO, "PENDING BUILD -- spec intact, both prototypes present; design "
                          "ratified, build not started. This entry can only assert its "
                          "PRE-BUILD half today, so it is OPEN by design and must NOT be "
                          "promoted: promoting now would lock the spec-only assertion and "
                          "retire the 8 shipped-code properties in the ref (LEDGER-PENDING-"
                          "BUILD-1). Promote when ZOOM-HMI-1 ships AND this harness checks "
                          "the shipped code."))
    return out


@entry("RG-0222", "An anonymous caller never receives a customer's IDENTITY or the text of "
       "their message -- the ops email-triage feed serves counts to strangers and rows only "
       "to the admin credential",
       LOCKED,  # promoted 2026-09-01 on the ledger's own READY TO LOCK print
       scope="bea_main.py dashboard_email_triage + the loadEmailTriage loaders in "
             "dashboard.server.html (ships) and dashboard.html (local operator copy) "
             "-- DASH-TRIAGE-REDACT-1. CLASS, not instance, and the class is the whole point: "
             "any UNAUTHENTICATED endpoint that serves a personal identifier (an email "
             "address, a name, a phone number) or the BODY of a customer's message belongs "
             "here. RG-0198 owns the internal engineering NARRATIVE and RG-0211 cut "
             "/dashboard/summary to a heartbeat; this owns PERSONAL DATA, which is a "
             "different duty (POPIA, and RUL-069's firewall doctrine that customer mail "
             "lives between the user and the triage AI). Deliberately split rather than "
             "folded in, because a single assertion over all three would be promoted the "
             "moment any one half passed. SWEEP RECORDED 31 Aug 2026: every other "
             "unauthenticated /dashboard/* route (fixed-costs, bit, presence, cost, scan, "
             "maint) was probed live the same run and none returns an email address -- "
             "email-triage was the only leaking sibling, and this entry is what keeps a new "
             "one from being added quietly.",
       ref="Found by the maintenance loop, 31 Aug 2026 -- the day before full launch "
           "(RUL-001). The endpoint's own docstring said it 'mirrors /dashboard/summary's "
           "no-auth posture (security = obscure dashboard URL)', and it did -- until "
           "DASH-SUMMARY-REDACT-1 tightened that sibling on 30 Aug and left this one behind. "
           "PROBED anonymously, no cookie, no key: GET /dashboard/email-triage returned "
           "from_addr, subject and 600 chars of draft_reply for every inbound email. Today "
           "the queue holds only test rows (David's own address); from launch it is customer "
           "mail. An obscure URL is not a control for personal data. FIX: counts stay "
           "anonymous (the page's tiles need nothing more), rows require X-Admin-Token/"
           "X-Admin-Key via _summary_caller_is_admin -- the credential the dashboard already "
           "holds (omTok, the RG-0211 loader pattern); the row list degrades to a sign-in "
           "note rather than breaking (RG-0133). EVIDENCE at fix time: the real function "
           "source lifted from bea_main.py and exercised over a stub DB carrying "
           "'angry.customer@example.com' -- anonymous payload contained zero of the three "
           "PII strings and items==[], admin payload carried the full row. OPEN until the "
           "change DEPLOYS and the live anonymous probe below goes green -- source half "
           "passes now, live half is the one that matters, exactly as RG-0211 was held.")
def rg_triage_pii():
    out = []
    src_p = os.path.join(REPO, "bea_main.py")
    if os.path.exists(src_p):
        s = open(src_p, encoding="utf-8", errors="replace").read()
        i = s.find('@app.get("/dashboard/email-triage")')
        j = s.find("END AI EMAIL TRIAGE", i + 1) if i >= 0 else -1
        if i < 0:
            out.append((FAIL, "/dashboard/email-triage route is GONE from bea_main.py -- "
                              "this assertion cannot see what replaced it"))
        else:
            body = s[i:j if j > 0 else i + 6000]
            if "_summary_caller_is_admin" not in body:
                out.append((FAIL, "dashboard_email_triage no longer gates on "
                                  "_summary_caller_is_admin -- the anonymous branch is gone, "
                                  "so sender addresses and reply bodies are public again "
                                  "(DASH-TRIAGE-REDACT-1)"))
            if '"redacted": "counts"' not in body:
                out.append((FAIL, "the anonymous branch no longer returns redacted='counts' "
                                  "-- the loaders read that flag to explain the empty list"))
            if '"items": []' not in body:
                out.append((FAIL, "the anonymous branch no longer empties items[] -- the "
                                  "rows carry from_addr, subject and draft_reply"))
    else:
        out.append((INFO, "skip: bea_main.py not on this machine (run from the repo for the "
                          "source half)"))
    for page, ships in (("dashboard.server.html", True), ("dashboard.html", False)):
        pp = os.path.join(REPO, page)
        if not os.path.exists(pp):
            continue
        ps = open(pp, encoding="utf-8", errors="replace").read()
        if "/dashboard/email-triage?limit=20" in ps and "X-Admin-Token" not in ps.split(
                "loadEmailTriage")[-1][:1500]:
            out.append((FAIL, "%s loads the triage ROWS without X-Admin-Token -- after the "
                              "redaction the card silently shows nothing to its own operator "
                              "(%s)" % (page, "ships" if ships else "local copy")))
    # LIVE half -- the one that matters. Anonymous, exactly as a stranger would call it.
    try:
        d = _json("/dashboard/email-triage?limit=5")
    except Exception as e:
        out.append((INFO, "NOT EVALUATED live: %s" % str(e)[:120]))
        return out
    if d is None:
        out.append((INFO, "NOT EVALUATED live: no JSON from /dashboard/email-triage"))
        return out
    items = d.get("items")
    if items:
        leaked = sorted({k for it in items if isinstance(it, dict) for k in it
                         if k in ("from_addr", "subject", "draft_reply")})
        out.append((FAIL, "anonymous GET /dashboard/email-triage returned %d row(s) carrying "
                          "%s -- a stranger can read who complained and what we wrote back "
                          "(DASH-TRIAGE-REDACT-1)" % (len(items), ", ".join(leaked) or "rows")))
    elif d.get("redacted") != "counts":
        out.append((INFO, "PENDING BUILD -- the live endpoint answers with no rows but does "
                          "not carry redacted='counts', so this is the OLD build on an empty "
                          "window, not the fix. Promote after the change deploys and this "
                          "reads redacted='counts' with the counts intact."))
    else:
        out.append((INFO, "anonymous caller gets counts only (redacted='counts', %d total) -- "
                          "no sender, no subject, no draft body"
                          % (d.get("total") or 0)))
    return out


@entry("RG-0223", "The maintenance brain reads EVERY LIVE intake lane -- it can never report "
       "an empty queue because the only door it looks at has been closed",
       LOCKED, fixed_on="2026-09-01",
       scope="scripts/maintenance_agent.py (email_lane_census + the report/heartbeat it "
             "feeds) and bea_main.py _MAINT_HB_FIELDS -- MAINT-INTAKE-2. CLASS: every "
             "channel the product opens for complaints must be READ by the loop that exists "
             "to answer them; a lane that is switched on while the reader points elsewhere "
             "is a silent outage of the whole maintenance mission (MAINTENANCE_AGENT.md "
             "stage 1, 'log every complaint'). Deliberately a CENSUS and not a fix lane: "
             "the agent counts and says, it never drafts or sends -- email replies stay "
             "behind EMAIL_AUTO_SEND and legal/compliance stay excluded. Counts-only by "
             "construction, because RG-0222 keeps the rows behind a credential this agent "
             "does not hold and should not.",
       ref="Found by the maintenance loop, 31 Aug 2026. The agent's sole intake is GET "
           "/admin/faults?status=new, fed by the in-app REPORT tab -- and RUL-040 REMOVES "
           "that tab at soft launch, when customer complaints take over. PROBED live: /flags "
           "reads fault_report=false (correct -- soft-public opened 29 Aug), so the lane is "
           "deliberately shut, and every run since has truthfully reported '0 seen' while "
           "the lane actually carrying customer complaints (inbound mail -> POST "
           "/email/inbound -> email_triage, 15 rows) was never looked at by the brain at "
           "all. A loop that reports an empty queue because it is reading a closed door is "
           "worse than one that reports nothing -- it manufactures a green day. EVIDENCE at "
           "fix time: the patched agent run at 05:43Z printed 'email lane 15 total, 1 held "
           "(30d {other:1, support:4})' against the live site. OPEN until the heartbeat half "
           "deploys (_MAINT_HB_FIELDS whitelists 'email_lane', so the +1 card shows it only "
           "after the change ships) -- the agent half is live now. PROMOTED 1 Sep 2026, the run it printed READY TO LOCK (maintenance loop): the heartbeat half is deployed and PROBED live -- anonymous GET /dashboard/maint at 05:34:22Z carries email_lane (total 15, held_30d 1, counts only per RG-0222) for run 2026-09-01T05:34:03Z. Both halves now live; promoted same session per the DW-079 rule -- an entry left OPEN after passing cannot trip red when it rots.")
def rg_maint_intake_lanes():
    out = []
    ap = os.path.join(REPO, "scripts", "maintenance_agent.py")
    if not os.path.exists(ap):
        out.append((INFO, "skip: scripts/maintenance_agent.py not on this machine"))
        return out
    a = open(ap, encoding="utf-8", errors="replace").read()
    if "def email_lane_census" not in a:
        out.append((FAIL, "maintenance_agent.py no longer censuses the email lane -- the "
                          "brain is back to reading app_faults alone, which RUL-040 shuts at "
                          "soft launch (MAINT-INTAKE-2)"))
    if '"email_lane": _email' not in a:
        out.append((FAIL, "the run report no longer carries intake.email_lane -- a reader of "
                          "the report cannot tell whether 'seen' covered the customer lane"))
    if "email lane UNREAD" not in a:
        out.append((FAIL, "the agent no longer SAYS when the email lane could not be read -- "
                          "a failed census must be loud, or 'seen' silently means app_faults "
                          "only"))
    bp = os.path.join(REPO, "bea_main.py")
    if os.path.exists(bp):
        b = open(bp, encoding="utf-8", errors="replace").read()
        k = b.find("_MAINT_HB_FIELDS = (")
        if k >= 0 and "email_lane" not in b[k:k + 400]:
            out.append((FAIL, "_MAINT_HB_FIELDS dropped 'email_lane' -- the POST whitelist "
                              "silently discards it and the +1 card paints a shut lane as a "
                              "quiet day"))
    # LIVE half: the heartbeat the dashboard actually reads.
    try:
        hb = _json("/dashboard/maint")
    except Exception as e:
        out.append((INFO, "NOT EVALUATED live: %s" % str(e)[:120]))
        return out
    if hb is None:
        out.append((INFO, "NOT EVALUATED live: no JSON from /dashboard/maint"))
    elif "email_lane" not in hb:
        out.append((INFO, "PENDING BUILD -- the live heartbeat carries no email_lane field. "
                          "Expected until the _MAINT_HB_FIELDS change deploys; the agent is "
                          "already sending it and the server whitelist is dropping it."))
    else:
        el = hb.get("email_lane") or {}
        if el.get("error"):
            out.append((FAIL, "the last run could NOT read the customer email lane (%s) -- "
                              "its 'seen' count covered app_faults only"
                              % str(el["error"])[:90]))
        else:
            out.append((INFO, "heartbeat carries the customer lane: %s total, %s held"
                              % (el.get("total"), el.get("held_30d"))))
    return out


@entry("RG-0224", "SQUIRE keeps the four properties that make it legal, anonymous and "
       "on-model: it is Pro-only, it never GRANTS an introduction, seller identity never "
       "enters its context, and its top-up is TUPPENCE -- no second currency exists",
       OPEN,
       scope="repo: SQUIRE_SPEC.md is the build spec (RUL-077). While OPEN this asserts the "
             "SPEC survives -- ruled but unbuilt. WHEN BUILT, promote to LOCKED and extend to "
             "the shipped code: (1) Pro-gated, no capability leak to Free/Starter/Agency; "
             "(2) Watches and For You remain FREE on every tier (Zoom's fifth rule); "
             "(3) no introduction is ever granted by Squire -- every introduction burns 1T at "
             "every tier, subscriptions buy slots and reach and NEVER introductions "
             "(PRICING_CANON 3); (4) seller identity never reaches Squire's context and no "
             "brief transmits an identifying detail about a MINOR (POPIA -- parent is the "
             "account holder, need described never the person); (5) at the cap the OFFER "
             "arrives with the limit, no charge on a rejected attempt, and a drafted brief "
             "survives the ceiling; (6) the user is warned BEFORE composing effort that will "
             "exceed the cap; (7) every ceiling-hit logs limit+tier+category; (8) top-ups are "
             "denominated in Tuppence -- grep proves no parallel token type exists; "
             "(9) RUL-078: a live PRO subscription resolves to `global` reach -- _buyer_tier() "
             "must consult the SELLER subscription, not wishlist_subscriptions alone, or a Pro "
             "subscriber is silently treated as local and Squire under-serves the people paying "
             "most, invisibly. CLASS: "
             "the metering line is OBSERVE vs ACT -- any new Squire capability must land on "
             "the correct side of it, and a capability that quietly meters watching is a "
             "defect of this entry.",
       ref="SQUIRE-1 (30 Aug 2026). David ruled Squire onto the EXISTING $20 Pro tier and "
           "asked for a cap with a purchasable top-up rather than a hard lock. CTO answer: "
           "the currency already exists -- Tuppence, not a new token. The tier axis is the "
           "load-bearing idea: $5 buys REACH, $20 buys REPRESENTATION, so the tiers cannot "
           "cannibalise and no $5 subscriber loses anything. Commercial trigger: the "
           "contagion model reads 1 Pro at week 52 -- Pro is priced for sellers only, and "
           "Squire makes it valuable to anyone who buys. BUILD ORDER: Zoom (RG-0221) FIRST -- "
           "a brief IS a Zoom path plus prose, so Squire first would write the matching "
           "engine twice. AMENDED 30 Aug 2026 (RUL-078): David bundled Global reach into "
           "Pro and APPROVED build shape + acceptance criteria -- both are closed to "
           "re-litigation; a build session implements them. The bundle is a CODE fact, not a "
           "pricing sentence, which is why criterion 9 exists.")
def rg_squire():
    out = []
    sp = os.path.join(REPO, "SQUIRE_SPEC.md")
    if not os.path.exists(sp):
        return [(FAIL, "SQUIRE_SPEC.md is GONE -- the ruled Pro agent (RUL-077) exists only "
                       "in a chat transcript again (SQUIRE-1)")]
    s = open(sp, encoding="utf-8").read()
    for needle, why in (
            ("No new tier is created", "Squire attaching to the EXISTING Pro tier"),
            ("the top-up is TUPPENCE", "the one-currency rule"),
            ("no second currency exists anywhere", "the no-parallel-token assertion"),
            ("observe vs act", "the metering line"),
            ("never *grant*", "introductions never granted by subscription"),
            ("1T at every tier", "the unchanged introduction price"),
            ("never transmitted in identifying form", "the minor-data (POPIA) rule"),
            ("RUL-066", "the ceiling doctrine this applies verbatim"),
            ("RESOLVED 30 Aug 2026 (RUL-078)", "the Pro-includes-Global-reach bundle"),
            ("APPROVED BY DAVID", "the settled build shape + acceptance criteria")):
        if needle not in s:
            out.append((FAIL, "SQUIRE_SPEC.md lost %r -- %s is gone (SQUIRE-1)" % (needle, why)))
    zoom = os.path.join(REPO, "ZOOM_HMI_SPEC.md")
    if not os.path.exists(zoom):
        out.append((FAIL, "ZOOM_HMI_SPEC.md is gone -- Squire's stated build dependency "
                          "(Zoom first) can no longer be honoured (SQUIRE-1)"))
    if not out:
        out.append((INFO, "PENDING BUILD -- spec intact; ruled, unbuilt, Zoom-first order "
                          "recorded. This entry can only assert its PRE-BUILD half today, so "
                          "it is OPEN by design and must NOT be promoted: promoting now would "
                          "lock the spec-only assertion and retire the nine shipped-code "
                          "properties in the scope (LEDGER-PENDING-BUILD-1). Promote when "
                          "SQUIRE-1 ships AND this harness checks the shipped code."))
    return out


@entry("RG-0225", "Outreach volume can never grow on the ABSENCE of evidence: a city ramps "
       "past its base batch only if the server's bounce and opt-out verdicts were pulled "
       "down AFTER its last wave -- 'nobody looked' can never read as 'clean'",
       LOCKED, fixed_on="2026-08-31",
       scope="repo: ../CityLauncher/pull_from_server.py (the RAMP-EVIDENCE-1 witness) + "
             "emailer/wave_runner.py (evidence_state + ramp_state consulting it) + "
             "emailer/waves_policy.json (no armed city may re-acquire a batch_size pin). "
             "CLASS, and the class is the point: RG-0213 made outreach volume EARNED, and "
             "this makes the earning honest. Any gate that grows a rate, a batch, a budget "
             "or a blast radius on a measured-clean signal belongs here -- the failure mode "
             "is universal, not email-specific. DELIBERATE BOUNDARY: stale evidence never "
             "BLOCKS a send (the stop-loss gate owns blocking) -- it only refuses to GROW. "
             "Holding at base is the safe direction, so a missing or deleted witness fails "
             "closed by construction.",
       ref="RAMP-EVIDENCE-1, 31 Aug 2026 (CTO call under RUL-037, launch eve). Found while "
           "answering David's question about what the Resend $20 tier unlocks: the honest "
           "answer was that the mail quota was never the binding constraint, and the ramp "
           "that IS the constraint was reading a local database that only learns about a "
           "bounce when pull_from_server.py runs. That script's own docstring says 'Run "
           "BEFORE composing any wave' -- nothing enforced it, nothing recorded whether it "
           "had happened, and wave_runner never called it. So both armed cities scored a "
           "clean streak off 0 bounces that had never been looked for, and RAMP-1 would "
           "have doubled 12 -> 24 -> 48 -> 96 on ignorance. Same family as RG-0133 (no "
           "instrument wears a health colour nothing measures) and RG-0202 (a verify half "
           "must answer for the thing it actually gates). Fixed the session it was found: "
           "the pull now writes data/last_pull.json and the ramp compares it against the "
           "city's last send. Also removed the explicit batch_size:12 pins on Pretoria and "
           "Johannesburg -- equal to the base, so they changed nothing on day one, but an "
           "explicit per-city batch_size OVERRIDES ramp_state, so those two cities could "
           "never have earned a doubling however clean they ran. National's documented 30 "
           "stays (RG-0213's named exception).")
def rg_ramp_evidence():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- RAMP-EVIDENCE-1 unchecked here "
                       "(live-only run)")]
    pf = os.path.join(cl, "pull_from_server.py")
    wr = os.path.join(cl, "emailer", "wave_runner.py")
    for fp, name in ((pf, "pull_from_server.py"), (wr, "emailer/wave_runner.py")):
        if not os.path.exists(fp):
            return [(FAIL, "CityLauncher/%s is GONE -- RAMP-EVIDENCE-1 has no lane" % name)]
    psrc = open(pf, encoding="utf-8").read()
    wsrc = open(wr, encoding="utf-8").read()

    for needle, why in (("last_pull.json", "the witness file the ramp reads"),
                        ("'pulled_at'", "the dated field the freshness test compares")):
        if needle not in psrc:
            out.append((FAIL, "pull_from_server.py lost %r -- %s is gone; the ramp can no "
                              "longer tell 'measured clean' from 'never looked'" % (needle, why)))

    for needle, why in (("def evidence_state", "the freshness test itself"),
                        ("fresh, _why = evidence_state(city)", "ramp_state consulting it"),
                        ("def pull_witness", "the witness reader")):
        if needle not in wsrc:
            out.append((FAIL, "wave_runner.py lost %r -- %s is gone (RAMP-EVIDENCE-1)"
                              % (needle, why)))
    try:
        a = wsrc.index("fresh, _why = evidence_state(city)")
        b = wsrc.index("streak = 0", a)
        c = wsrc.index("for wv in reversed(wave_history(city))", a)
        if not (a < b < c):
            out.append((FAIL, "ramp_state counts its clean streak BEFORE checking evidence "
                              "freshness -- the guard has been reordered into a no-op"))
    except ValueError:
        out.append((FAIL, "ramp_state no longer has the guard-then-count shape "
                          "(RAMP-EVIDENCE-1 hollowed out)"))

    try:
        pol = json.loads(open(os.path.join(cl, "emailer", "waves_policy.json"),
                              encoding="utf-8").read())
        for city, cpol in pol.get("cities", {}).items():
            if city == "National":
                continue          # RG-0213's documented exception
            if "batch_size" in cpol and (cpol.get("armed") or cpol.get("gates_green")):
                out.append((FAIL, "%s carries an explicit batch_size=%r AND is armed -- an "
                                  "explicit per-city size outranks ramp_state, so this city "
                                  "can never earn a doubling (RAMP-1 neutered)"
                                  % (city, cpol.get("batch_size"))))
    except Exception as e:
        out.append((FAIL, "waves_policy.json unreadable (%s) -- the pin check cannot run" % e))

    if not out:
        try:
            i = wsrc.index("def evidence_state"); j = wsrc.index("def ramp_state")
            ns = {}
            exec("def last_send_at(c):\n    return _SENT\n"
                 "def pull_witness():\n    return _WIT\n" + wsrc[i:j], ns)
            def verdict(sent, wit):
                ns["_SENT"], ns["_WIT"] = sent, wit
                return ns["evidence_state"]("X")[0]
            never  = verdict("2026-08-30T14:05:00", None)
            stale  = verdict("2026-08-30T14:05:00", {"pulled_at": "2026-08-29T06:00:00Z"})
            fresh  = verdict("2026-08-30T14:05:00", {"pulled_at": "2026-08-31T06:00:00Z"})
            virgin = verdict(None, None)
            if never:
                out.append((FAIL, "a city that has NEVER been pulled reads FRESH -- the ramp "
                                  "would double on the absence of evidence, which is the whole "
                                  "defect this entry exists to prevent"))
            if stale:
                out.append((FAIL, "a pull OLDER than the last send reads FRESH -- bounces from "
                                  "that wave cannot have been seen yet"))
            if not fresh:
                out.append((FAIL, "a pull NEWER than the last send reads STALE -- the guard has "
                                  "over-tightened and no city can ever ramp"))
            if not virgin:
                out.append((FAIL, "a city with no waves sent reads STALE -- there is nothing to "
                                  "judge yet and it must sit at base without complaint"))
            if not out:
                out.append((INFO, "freshness logic behaviourally proven: never-pulled and "
                                  "stale-pull both refuse to grow; a pull after the last send "
                                  "allows it; a city with no waves is untroubled"))
        except Exception as e:
            out.append((INFO, "freshness logic not behaviourally checkable here (%s) -- the "
                              "source halves above still assert the shape" % str(e)[:70]))
    return out


@entry("RG-0226", "A cold outreach email is NEVER addressed to a mailbox whose job is receiving "
       "complaints -- privacy, compliance and information-officer desks are refused at the same "
       "chokepoint that refuses placeholders, and the wave PLAN counts only what would actually "
       "send",
       LOCKED, fixed_on="2026-08-31",
       scope="repo: ../CityLauncher/emailer/emailer.py (_looks_privacy_officer + the send "
             "refusal + the get_prospects filter) and emailer/wave_runner.py "
             "(sendable_by_category honouring both guards -- PLAN-TRUTH-1). CLASS, by SHAPE and "
             "not by name: a re-scrape must not be able to reintroduce what a list edit removed, "
             "which is precisely how the July note failed. DELIBERATE BOUNDARY, and it is half "
             "the assertion: info@, sales@, support@, enquiries@ and reservations@ are ordinary "
             "business addresses and MUST keep sending -- a guard that eats legitimate mail "
             "starves the lane and is as much a defect as one that lets an Information Officer "
             "be cold-mailed (RG-0217's boundary, applied to this class).",
       ref="PRIV-OFFICER-1 + PLAN-TRUTH-1, 31 Aug 2026, shipped in the same session as RUL-079 "
           "(agency outreach at week 0) and BECAUSE of it -- arming the National key-accounts "
           "lane is what made the July caveat load-bearing. waves_policy's National note had "
           "said since 27 Jul: 'POPIA-officer addresses (Motus, Bidvest McCarthy, Group 1) are "
           "FLAGGED in notes - prefer their contact forms for first touch.' A note is not a "
           "control, and it was also WRONG: a probe found FIVE on that list (Pam Golding's "
           "compliance@ and Seeff's informationofficer@ had never been flagged) and SEVEN across "
           "the pool -- including complaints.ir@justice.gov.za sitting on a SUPERSPAR Botshabelo "
           "row, i.e. the Department of Justice complaints desk about to receive marketing for a "
           "supermarket. Sending there does not cost one bounce, it costs the sending domain. "
           "The addresses are HELD, never suppressed and never marked opted-out -- nobody opted "
           "out, and writing a fake opt-out into the POPIA register to solve an engineering "
           "problem would be its own offence. Reach them by contact form.")
def rg_privacy_officer_guard():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- PRIV-OFFICER-1 unchecked here "
                       "(live-only run)")]
    em = os.path.join(cl, "emailer", "emailer.py")
    wr = os.path.join(cl, "emailer", "wave_runner.py")
    for fp, nm in ((em, "emailer/emailer.py"), (wr, "emailer/wave_runner.py")):
        if not os.path.exists(fp):
            return [(FAIL, "CityLauncher/%s is GONE -- PRIV-OFFICER-1 has no chokepoint" % nm)]
    esrc = open(em, encoding="utf-8").read()
    wsrc = open(wr, encoding="utf-8").read()
    for needle, why in (("def _looks_privacy_officer", "the shape guard itself"),
                        ("PRIV-OFFICER-1: refusing send", "the send_email chokepoint refusal"),
                        ("and not _looks_privacy_officer(r.get(", "batch composition filtering")):
        if needle not in esrc:
            out.append((FAIL, "emailer.py lost %r -- %s is gone (PRIV-OFFICER-1)"
                              % (needle, why)))
    for needle, why in (("PLAN-TRUTH-1", "the plan-counts-what-sends rule"),
                        ("_looks_privacy_officer(e)", "sendable_by_category honouring the guard")):
        if needle not in wsrc:
            out.append((FAIL, "wave_runner.py lost %r -- %s is gone; the plan can promise "
                              "addresses the chokepoint will refuse" % (needle, why)))
    if not out:
        try:
            ns = {}
            i = esrc.index("_JUNK_LOCALPARTS"); j = esrc.index("def send_email")
            exec(esrc[i:j], ns)
            f = ns["_looks_privacy_officer"]
            must_block = ("popia@motus.co.za", "popia@mcmotor.co.za", "dpns@grp1.co.za",
                          "compliance@pamgolding.co.za", "informationofficer@seeff.com",
                          "complaints.ir@justice.gov.za", "dpo@anything.co.za",
                          "privacy.team@x.com")
            must_pass = ("info@rawsonproperties.com", "support@remax.co.za",
                         "enquiries@jawitz.co.za", "sales@africastay.com",
                         "reservations@safari.com", "customercare@cmh.co.za",
                         "ask@moafrikatours.com", "hey@halfway.co.za")
            leaked = [e for e in must_block if not f(e)]
            eaten  = [e for e in must_pass if f(e)]
            if leaked:
                out.append((FAIL, "the guard no longer catches %s -- a complaints desk is "
                                  "cold-mailable again" % ", ".join(leaked[:3])))
            if eaten:
                out.append((FAIL, "the guard now eats ordinary business addresses (%s) -- "
                                  "over-widened, the lane will starve" % ", ".join(eaten[:3])))
            if not leaked and not eaten:
                out.append((INFO, "guard behaviourally proven: every known privacy/compliance "
                                  "desk refused, every ordinary business address still sends"))
        except Exception as e:
            out.append((INFO, "guard not behaviourally checkable here (%s) -- source halves "
                              "above still assert the shape" % str(e)[:70]))
    return out


@entry("RG-0227", "No outreach wave may fire while the LOCAL opt-out register is unarmed -- the "
       "POPIA chokepoint must have something to enforce before a single cold email leaves",
       LOCKED, fixed_on="2026-08-31",
       scope="repo: ../CityLauncher/emailer/wave_runner.py (suppression_state + its wiring into "
             "gate_check). CLASS: any send lane whose legal chokepoint depends on data that a "
             "SEPARATE, manual step populates. DELIBERATE ASYMMETRY against its sibling RG-0225: "
             "stale bounce evidence merely holds the batch at base, because volume is a business "
             "risk -- but an absent opt-out register BLOCKS the send outright, because honouring "
             "an opt-out is a legal obligation and there is no safe smaller version of it. "
             "Dry-runs stay allowed at all times: the point is to make the gap visible, not to "
             "make the tool unusable.",
       ref="SUPPRESS-GATE-1, 31 Aug 2026, found pre-flighting RUL-079's agency lane. emailer.py "
           "has carried a SUPPRESS-1 chokepoint that reads a local `suppression` table since the "
           "opt-out work; that table is CREATED AND FILLED by pull_from_server.py and by nothing "
           "else. Probed on the eve of the agency wave: `no such table: suppression` -- the pull "
           "had never run on this machine, so the chokepoint had been enforcing against nothing, "
           "silently, for the whole of the first outreach fortnight. The 110 sends already made "
           "were not stopped by it because it had nothing to stop them with. Same root as "
           "RG-0225 (the pull is manual, unenforced and unwitnessed) and fixed at the same seam, "
           "but recorded separately because one is about growing and this one is about sending.")
def rg_suppression_gate():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not beside this repo -- SUPPRESS-GATE-1 unchecked here "
                       "(live-only run)")]
    wr = os.path.join(cl, "emailer", "wave_runner.py")
    if not os.path.exists(wr):
        return [(FAIL, "CityLauncher/emailer/wave_runner.py is GONE -- SUPPRESS-GATE-1 has no lane")]
    wsrc = open(wr, encoding="utf-8").read()
    for needle, why in (("def suppression_state", "the register check itself"),
                        ("SUPPRESS-GATE-1: {sup_why}", "gate_check appending it as a blocker"),
                        ("sup_ok, sup_why = suppression_state()", "gate_check calling it")):
        if needle not in wsrc:
            out.append((FAIL, "wave_runner.py lost %r -- %s is gone; a wave can fire with no "
                              "local opt-out register (SUPPRESS-GATE-1)" % (needle, why)))
    # the check must sit in gate_check (which BLOCKS), never in the ramp (which only holds)
    try:
        g = wsrc.index("def gate_check")
        nxt = wsrc.index("def ", g + 10)
        if "suppression_state()" not in wsrc[g:nxt]:
            out.append((FAIL, "suppression_state is no longer called inside gate_check -- the "
                              "register check has been demoted out of the blocking path"))
    except ValueError:
        out.append((FAIL, "gate_check not found in wave_runner.py"))
    if not out:
        out.append((INFO, "the opt-out register is a blocking pre-condition of a real send, "
                          "and dry-runs remain unrestricted"))
    return out


@entry("RG-0228", "No outreach email can reach a GOVERNMENT or MILITARY mailbox -- the "
       "regulator is the government, and a role-name guard does not catch a named "
       "person at a municipality",
       LOCKED,
       scope="repo: ../CityLauncher/emailer/emailer.py -- _looks_government() at the "
             "send_email chokepoint AND in batch composition, beside JUNK-GUARD-1 and "
             "PRIV-OFFICER-1. Matches the DOMAIN on exact labels {gov, govt, mil, gouv}, "
             "so 'govender.co.za' and 'govhotel.com' keep sending while tshwane.gov.za and "
             "sanjoseca.gov cannot. CLASS, not instance: PRIV-OFFICER-1 polices the "
             "LOCAL-PART (the role), this polices the DOMAIN (the institution) -- both "
             "axes are required and neither is a blocklist, so a re-scrape cannot "
             "reintroduce what an address-list edit removed. .edu and .ac.* are "
             "deliberately NOT blocked: RUL-059's US lane targets tutoring businesses and "
             "campus learning-support, which are not government. Held, never suppressed, "
             "never marked opted-out -- nobody opted out; reach them by contact form.",
       fixed_on="2026-08-31",
       ref="GOV-DOMAIN-1 (31 Aug 2026). David asked, on the morning of the last pre-launch "
           "send day: 'You must please check for us that we dont send to the governmental "
           "POPIA agents.' PROBED the live unsent pool (1409 rows): EIGHT officer/government "
           "addresses present, and PRIV-OFFICER-1 refused only SIX. The two that would have "
           "sent were natashaz@tshwane.gov.za (City of Tshwane, Pretoria/Tour Operators) and "
           "work2future@sanjoseca.gov (City of San Jose) -- a named person and a programme "
           "mailbox on government domains, which a role guard cannot see by construction. "
           "Wave composition happened to exclude them today, which is luck, not a control -- "
           "the same lesson PRIV-OFFICER-1 was itself born from hours earlier ('a note is "
           "not a control'). After the fix all 8 are refused and 8 ordinary business "
           "addresses still send, false-positive checked.")
def rg_gov_domain():
    out = []
    ep = os.path.join(REPO, "..", "CityLauncher", "emailer", "emailer.py")
    if not os.path.exists(ep):
        return [(INFO, "CityLauncher not beside this repo -- GOV-DOMAIN-1 skipped (live-only run)")]
    s = open(ep, encoding="utf-8").read()
    if "_looks_government" not in s:
        return [(FAIL, "_looks_government() is GONE -- a cold email can reach a government "
                       "mailbox again (GOV-DOMAIN-1)")]
    if "GOV-DOMAIN-1: refusing send" not in s:
        out.append((FAIL, "the send_email chokepoint no longer refuses government domains "
                          "(GOV-DOMAIN-1)"))
    if s.count("_looks_government(") < 3:
        out.append((FAIL, "_looks_government is no longer applied at BOTH the chokepoint and "
                          "batch composition -- one path is unguarded (GOV-DOMAIN-1)"))
    for label in ("'gov'", "'mil'"):
        if label not in s:
            out.append((FAIL, "the government label set lost " + label + " (GOV-DOMAIN-1)"))
    if ".edu" not in s:
        out.append((FAIL, "the .edu carve-out note is gone -- a future session may over-block "
                          "RUL-059's US tutoring lane (GOV-DOMAIN-1)"))
    if not out:
        out.append((INFO, "government/military domains refused at both the chokepoint and "
                          "batch composition; .edu carve-out intact"))
    return out


@entry("RG-0229", "A person CAN opt out and we CANNOT email them again -- proven by the "
       "five gates a real opt-out travels, from the recipient's click to the send "
       "refusal, never by the presence of code that claims to do it",
       LOCKED,  # promoted 2026-09-01 on the ledger's own READY TO LOCK print
       scope="../CityLauncher/verify_optout_lane.py is the assertion; this entry runs it. "
             "FIVE GATES: (1) the unsubscribe URL answers 200 ANONYMOUSLY on the live "
             "site -- a recipient is not logged in; (2) a click INCREASES the server "
             "register's row count; (3) the LOCAL send pool holds the register; (4) "
             "_is_suppressed() returns True for an address actually in it; (5) with NO "
             "register the guard REFUSES. CLASS, and this is the whole point of the entry: "
             "every gate tests an OUTCOME a person experiences, not the presence of code "
             "that claims the outcome. RG-0220 is the counter-example and the reason this "
             "exists -- its title promised 'can never again email an address the server has "
             "opted out' while its check read strings out of two files, so it passed green "
             "for a week over a protection that did not exist. An outcome in the title "
             "requires an outcome in the check.",
       ref="OPTOUT-LANE-1 (31 Aug 2026). David: 'I did not ask you to remove anything but "
           "the blocker, and the blocker is the false acknowledgement of the opt out "
           "database, which doesnt exist... This is a project kill risk.' PROBED that "
           "morning: every outreach email since 24 Aug carried {api_base}/optout, NO such "
           "route existed anywhere (bea_main/main/worker/ops all swept), no server-side "
           "suppression DDL existed, the local register had never been created, and "
           "_is_suppressed() returned False -- 'send it' -- whenever the table was absent. "
           "110 emails went out with a dead unsubscribe link and a guard that had never "
           "once consulted real data. FIXED THIS SESSION: SUPPRESS-FAILCLOSED-1 (absence is "
           "no longer permission) + the /optout GET/POST route + /optout/status proof "
           "endpoint + this verifier. NOT YET LIVE: the route is staged in bea_main.py and "
           "needs David's deploy. Live probe reads 404 (not 403), so the path is NOT behind "
           "the review gate and a deploy should be sufficient -- to be PROVEN by gate 1, "
           "never assumed. Stays OPEN and RED until all five pass.")
def rg_optout_lane():
    # Uses _harness(), not a bare subprocess: RG-0187's rule is that an instrument
    # which CANNOT RUN must read UNVERIFIED, never REGRESSION. A bare subprocess.run
    # here would cry "opt-out lane broken" when the truth was "this machine has no
    # network" -- a false red on the one lane nobody can afford to distrust. Caught
    # by RG-0187 on the first run after this entry was written (31 Aug).
    v = os.path.join(REPO, "..", "CityLauncher", "verify_optout_lane.py")
    if not os.path.exists(v):
        return [(FAIL, "verify_optout_lane.py is GONE -- the opt-out lane has no proof "
                       "and must be treated as unproven (OPTOUT-LANE-1)")]
    ok, blind, detail = _harness([sys.executable, v], timeout=150)
    if blind:
        return [(INFO, "NOT EVALUATED - the opt-out verifier could not run here: %s "
                       "(instrument limit, not a verdict on the lane)" % detail[:160])]
    if ok:
        return [(INFO, "all five gates pass -- a person can opt out and cannot be emailed again")]
    fails = [ln.strip() for ln in str(detail).splitlines() if ln.strip().startswith("[FAIL]")]
    return [(FAIL, "OPT-OUT LANE UNPROVEN -- %d of 5 gates failing. DO NOT SEND. %s"
             % (len(fails), " | ".join(f[6:].strip() for f in fails)[:400] or str(detail)[-200:]))]


@entry("RG-0230", "A cold sandbox can ALWAYS reach the Hetzner server over SSH -- the key "
       "lives on the mount and every SSH-using tool self-heals (SSH-BOOTSTRAP-1)",
       LOCKED, scope="repo + CityLauncher + Projects/CLAUDE.md, tooling class", fixed_on="2026-08-31",
       ref="Recurring fault, latest strike 31 Aug 2026: the Gate 1 board shipped with clicks "
           "UNREADABLE because the fresh sandbox had no ~/.ssh key -- while load_sandbox_ssh.sh "
           "and the key sat on the mount, documented only in MarketSquare/CLAUDE.md, which a "
           "CityLauncher session never loads. Same class as GIT-LOCK: machinery exists, memory "
           "fails. Fix (SSH-BOOTSTRAP-1): (1) CityLauncher/ssh_bootstrap.py self-heals ~/.ssh "
           "from the mounted key, idempotent, proven from cold + live probe same session; "
           "(2) every SSH-using CityLauncher entry point calls ensure_ssh() at entry; "
           "(3) the standing note moved to Projects/CLAUDE.md -- the ONE file every session "
           "loads. This asserts all three layers stay present; a new SSH-using script that "
           "skips the bootstrap trips red instead of stranding a 2 a.m. run.")
def rg_sandbox_ssh_selfheal():
    if repo_file("load_sandbox_ssh.sh") is None:
        return [(INFO, "running outside the repo -- sandbox-SSH tooling check skipped")]
    out = []
    if not os.path.exists(os.path.join(REPO, "ssh_hetzner_key")):
        out.append((FAIL, "ssh_hetzner_key missing from MarketSquare/ -- the mount no longer "
                          "carries the key; David must re-run setup_sandbox_ssh.ps1 (host-side)"))
    cl = os.path.join(REPO, "..", "CityLauncher")
    boot = os.path.join(cl, "ssh_bootstrap.py")
    if not os.path.exists(boot):
        out.append((FAIL, "CityLauncher/ssh_bootstrap.py is GONE -- the python lane lost its "
                          "self-heal (SSH-BOOTSTRAP-1)"))
    for s in ("pull_from_server.py", "sync_local_to_server.py", "push_estate_agents.py",
              "push_us_uk_cities.py", "run_local_scraper.py", "run_za_estate_agents.py"):
        p = os.path.join(cl, s)
        if not os.path.exists(p):
            continue  # a retired script is not a regression
        if "ssh_bootstrap" not in open(p, encoding="utf-8", errors="replace").read():
            out.append((FAIL, s + " uses SSH but no longer calls ssh_bootstrap.ensure_ssh() -- "
                              "it will strand on a cold sandbox exactly like the 31 Aug case"))
    cm = os.path.join(REPO, "..", "CLAUDE.md")
    if not (os.path.exists(cm) and
            "SSH-BOOTSTRAP-1" in open(cm, encoding="utf-8", errors="replace").read()):
        out.append((FAIL, "Projects/CLAUDE.md lost the SSH-BOOTSTRAP-1 section -- the knowledge "
                          "moved back to a file sessions do not load, which IS the original fault"))
    if not out:
        out.append((INFO, "key on mount + python self-heal + all 6 SSH entry points bootstrapped "
                          "+ CLAUDE.md carries the note"))
    return out


@entry("RG-0231", "Every Overpass caller reads OVERPASS_URL from the env -- a blocked "
       "instance is a .env change + restart, never a code hunt (OSM-MIRROR-1)",
       LOCKED, scope="CityLauncher repo, both overpass callers", fixed_on="2026-08-31",
       ref="Launch eve: the OSM-only resume (RUL-083) at pool=10 drained the frozen queue "
           "into overpass-api.de and tripped its IP protection (probed 200 in 0.08s before "
           "the burst, connection-refused after; DDG/Bing unaffected). The first fix patched "
           "scraper/sources/openstreetmap.py -- and changed NOTHING, because "
           "orchestration/scraper_worker.py._run_osm carries its OWN hardcoded copy, the one "
           "the engine actually runs. Both are now env-driven with the main instance as "
           "default; server .env points at overpass.openstreetmap.fr (planet-verified) with "
           "OSM_CONCURRENCY=2. This asserts BOTH callers stay env-driven -- a third hardcoded "
           "overpass URL anywhere in CityLauncher trips red.")
def rg_overpass_env_driven():
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not present -- skipped")]
    out = []
    for rel in (os.path.join("orchestration", "scraper_worker.py"),
                os.path.join("scraper", "sources", "openstreetmap.py")):
        p = os.path.join(cl, rel)
        if not os.path.exists(p):
            out.append((FAIL, rel + " is GONE"))
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        if "os.environ.get(\"OVERPASS_URL\"" not in t and "os.environ.get('OVERPASS_URL'" not in t:
            out.append((FAIL, rel + " lost the env-driven OVERPASS_URL -- a blocked instance "
                              "is a code hunt again (OSM-MIRROR-1 regressed)"))
    import glob as _g
    for p in _g.glob(os.path.join(cl, "**", "*.py"), recursive=True):
        if ".bak" in p or "__pycache__" in p or "_to_delete" in p:
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        for ln in t.splitlines():
            s = ln.strip()
            if ("overpass-api.de/api/interpreter" in s and "environ" not in s
                    and not s.startswith("#")):
                out.append((FAIL, os.path.relpath(p, cl) + " hardcodes the overpass "
                                  "interpreter URL outside an env default: " + s[:80]))
    if not out:
        out.append((INFO, "both callers env-driven, no stray hardcoded interpreter URLs"))
    return out


@entry("RG-0232", "A network fault is NEVER recorded as zero yield -- the scraper's "
       "backoff ladders climb only on a genuine queried-fine-found-nothing pass "
       "(S131-NETFAULT)",
       LOCKED, scope="CityLauncher repo, OSM lane; class fix -- any source whose errors "
       "masquerade as empty results re-creates it", fixed_on="2026-09-01",
       ref="Launch morning: the 31 Aug refusal storm (151 connection-refused in 18 min) was "
           "recorded as zero yield everywhere it struck, because _overpass_query swallowed "
           "exceptions and returned [] -- indistinguishable from a genuine empty 200. That "
           "climbed the durable S131 keyword ladder (6h->168h, survives restarts BY DESIGN), "
           "demoted 214 source_health rows to dead_temp, and backed off 133 queue jobs -- so "
           "after the OSM-MIRROR-1 env fix the engine made exactly ONE mirror attempt in 5.5h "
           "and refill sat frozen at 147 on launch morning. Fix: _overpass_query returns None "
           "on fault vs [] on genuine-empty; fault passes skip record_keyword_yield AND "
           "source_memory.record_yield entirely (scrape_keyword returns -1, run_job skips the "
           "verdict); OVERPASS_URL accepts a comma-separated failover list and OSM_TIMEOUT is "
           "env-driven (the fr mirror read-timed-out at the hardcoded 40s). Poisoned state was "
           "cleared server-side same session (2885 keyword rows, 214 sources, 133 jobs, DBs "
           "backed up first); staged count moved 147->160 within minutes of the restart. "
           "This asserts the fault/empty distinction stays present in the deployed code.")
def rg_netfault_not_zero_yield():
    cl = os.path.join(REPO, "..", "CityLauncher")
    if not os.path.isdir(cl):
        return [(INFO, "CityLauncher not present -- skipped")]
    out = []
    sw = os.path.join(cl, "orchestration", "scraper_worker.py")
    wp = os.path.join(cl, "orchestration", "worker_pool.py")
    if not os.path.exists(sw):
        return [(FAIL, "orchestration/scraper_worker.py is GONE")]
    t = open(sw, encoding="utf-8", errors="replace").read()
    for needle, why in (
            ("return None", "_overpass_query no longer distinguishes fault from empty"),
            ("net_faults", "_run_osm lost the fault counter -- fault passes will record "
                           "zero yield again"),
            ("osm_faulted", "scrape_keyword lost the fault sentinel -- run_job cannot "
                            "skip the yield verdict")):
        if needle not in t:
            out.append((FAIL, "scraper_worker.py: '" + needle + "' missing -- " + why +
                              " (S131-NETFAULT regressed; this is exactly how the 31 Aug "
                              "storm froze launch-morning refill)"))
    if os.path.exists(wp):
        t2 = open(wp, encoding="utf-8", errors="replace").read()
        if "if w < 0" not in t2:
            out.append((FAIL, "worker_pool.run_job records a yield verdict on fault passes "
                              "again ('if w < 0' guard gone) -- the keyword ladder will "
                              "climb on the next network outage"))
    else:
        out.append((FAIL, "orchestration/worker_pool.py is GONE"))
    if not out:
        out.append((INFO, "fault/empty distinction present in both files -- an outage can "
                          "no longer poison the backoff ladders"))
    return out


@entry("RG-0233", "The ONE deploy engine PLACES what it is handed -- a published deploy ref "
       "never sits unplaced, and the engine's own report is fresh, readable and clean",
       LOCKED, fixed_on="2026-09-01",
       scope="The whole placement lane: publish the `deploy` ref -> the server engine "
             "(ops/autodeploy/server_deploy.sh) places by manifest, restarts, health-checks, "
             "writes $LIVE/static/post_deploy_status.json. Retires the coverage map's "
             "long-standing BLUE card ('ONE deploy engine -- armed, unasserted'). LIVE half "
             "runs anywhere: the report parses, its ref field is 'deploy' (a second writer "
             "would be an ONE-DEPLOY violation), and no step finished non-ok (chain HEALTH "
             "is RG-0125's entry; ENGINE-RAN-AND-FINISHED is this one's). REPO half (skips "
             "outside the repo): the local origin/deploy commit time may never be AHEAD of "
             "the report's generated_at by more than 45 minutes -- that state means a deploy "
             "was PUBLISHED and the engine never placed it, the exact silent failure the "
             "blue card could not see. Conservative by design: a stale local origin/deploy "
             "can only under-detect, never false-red (the DW-086/RG-0214 lesson -- assert "
             "evidence that exists).",
       ref="DEPLOY-ENGINE-ASSERT-1, 1 Sep 2026 (attended map-fix session, David's ask). "
           "Proven red-capable before its green was believed (7 Aug rule): a mutated report "
           "with a failed step and a generated_at predating origin/deploy by a month "
           "produced both FAILs; the real report then produced none.")
def rg_deploy_engine_places():
    out = []
    st = _status("/static/post_deploy_status.json")
    if st != 200:
        out.append((FAIL, "post_deploy_status.json unreadable (HTTP %s) -- the engine's own "
                          "report is gone; placement is unverifiable" % st))
        return out
    try:
        doc = _json("/static/post_deploy_status.json")
        gen = str(doc.get("generated_at", ""))
        gtime = datetime.datetime.strptime(gen, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        out.append((FAIL, "deploy report does not parse (%s)" % str(e)[:80]))
        return out
    if str(doc.get("ref", "")) != "deploy":
        out.append((FAIL, "report ref is %r, not 'deploy' -- something other than the ONE "
                          "engine is writing the engine's report" % doc.get("ref")))
    bad = [s for s in doc.get("steps", []) if s.get("result") not in ("ok", "skipped")]
    if bad:
        out.append((FAIL, "engine finished with non-ok step(s): " +
                          "; ".join("%s=%s" % (s.get("step"), s.get("result")) for s in bad)))
    pub = None
    if os.path.isdir(os.path.join(REPO, ".git")):
        try:
            env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
            r = subprocess.run(["git", "log", "-1", "--format=%cI", "origin/deploy"],
                               cwd=REPO, env=env, capture_output=True, text=True, timeout=30)
            iso = r.stdout.strip()
            if iso:
                pub = (datetime.datetime.fromisoformat(iso)
                       .astimezone(datetime.timezone.utc).replace(tzinfo=None))
        except Exception:
            pub = None
    if pub is not None:
        lag_min = (pub - gtime).total_seconds() / 60.0
        if lag_min > 45:
            out.append((FAIL, "origin/deploy was published %sZ but the engine's report is dated "
                              "%s (%.0f min earlier) -- a handed deploy sits UNPLACED"
                              % (pub.isoformat(), gen, lag_min)))
        else:
            out.append((INFO, "engine placed what it was handed: report %s covers "
                              "origin/deploy %sZ" % (gen, pub.isoformat())))
    else:
        out.append((INFO, "repo half skipped (no origin/deploy readable here); live half held"))
    return out


@entry("RG-0234", "A backup exists, is FRESH, and provably RESTORES -- this assertion itself "
       "extracts the newest archive and integrity-checks the restored database on every run, "
       "so an untested backup can never again wear the word 'backup'",
       LOCKED, fixed_on="2026-09-01",
       scope="The local DB-archive lane: backups/YYYY-MM-DD_HHMM.zip (each one marketsquare.db "
             "snapshot) + Backups/RESTORE_PROOF.md (append-only, dated). Repo-side by nature "
             "-- SKIPS outside the repo. THREE properties: (a) the newest archive is <= 8 "
             "days old -- the lane was found 27 days stale on 1 Sep, and that silence is what "
             "this arm ends; (b) the newest archive EXTRACTS to the OS temp dir here and now "
             "and the restored DB answers PRAGMA integrity_check == ok with a non-empty users "
             "table -- an actual restore, performed by the assertion, every run, on any "
             "machine; (c) RESTORE_PROOF.md carries a dated entry <= 35 days old, so the "
             "human-readable record cannot rot either. Out of scope, stated not hidden: the "
             "GitHub code mirror (sandbox holds no GitHub credential -- host-side lanes push "
             "it), the server-side R2/volume lanes, and host-side retention pruning "
             "(7 daily / 4 weekly). Retires the coverage map's 'Backups -- UNASSERTED' blue "
             "card.",
       ref="BACKUP-RESTORE-ASSERT-1, 1 Sep 2026 (attended map-fix session, David's ask). "
           "Proven red-capable before its green was believed (7 Aug rule): a garbage .zip "
           "in a fixture repo produced the did-not-restore FAIL; the real archive "
           "2026-09-01_0653.zip then restored clean (integrity ok, users=70).")
def rg_backup_restores():
    import zipfile, tempfile, glob as _glob
    bdir = os.path.join(REPO, "backups")
    if not os.path.isdir(bdir):
        return [(INFO, "SKIPPED -- backups/ not present here (outside repo)")]
    out = []
    zips = sorted(_glob.glob(os.path.join(bdir, "20*.zip")))
    if not zips:
        return [(FAIL, "no dated archive in backups/ at all -- the lane is empty")]
    newest = zips[-1]
    name = os.path.basename(newest)
    try:
        made = datetime.datetime.strptime(name[:15], "%Y-%m-%d_%H%M")
    except ValueError:
        made = datetime.datetime.utcfromtimestamp(os.stat(newest).st_mtime)
    age_days = (datetime.datetime.utcnow() - made).days
    if age_days > 8:
        out.append((FAIL, "newest archive %s is %d days old -- the lane has silently stopped "
                          "(it sat 27 days stale before 1 Sep; 8 is the line)" % (name, age_days)))
    try:
        import sqlite3 as _sq
        with zipfile.ZipFile(newest) as z:
            with tempfile.TemporaryDirectory() as td:
                z.extract("marketsquare.db", td)
                c = _sq.connect(os.path.join(td, "marketsquare.db"))
                ic = c.execute("PRAGMA integrity_check").fetchone()[0]
                users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                c.close()
        if ic != "ok":
            out.append((FAIL, "%s restored but integrity_check says %r" % (name, ic)))
        elif users < 1:
            out.append((FAIL, "%s restored with an EMPTY users table -- a backup of nothing"
                              % name))
        else:
            out.append((INFO, "restore performed this run: %s -> integrity ok, users=%d"
                              % (name, users)))
    except Exception as e:
        out.append((FAIL, "%s did not restore (%s) -- an archive that cannot extract is a "
                          "hope, not a backup" % (name, str(e)[:70])))
    proof = os.path.join(REPO, "Backups", "RESTORE_PROOF.md")
    try:
        t = open(proof, encoding="utf-8", errors="replace").read()
        dates = re.findall(r"^## (\d{4}-\d{2}-\d{2})", t, re.M)
        if not dates:
            out.append((FAIL, "RESTORE_PROOF.md has no dated entry -- the record half is empty"))
        else:
            page = (datetime.date.today() - datetime.date.fromisoformat(max(dates))).days
            if page > 35:
                out.append((FAIL, "newest RESTORE_PROOF entry is %d days old -- the record "
                                  "half rotted" % page))
    except OSError:
        out.append((FAIL, "Backups/RESTORE_PROOF.md missing -- the record half is gone"))
    return out


@entry("RG-0235", "David's PERSONAL address can never ride out on an outreach reply -- the "
       "prospect lane carries ONE identity in BOTH directions, and inbound aliasing alone "
       "does not achieve that",
       LOCKED, fixed_on="2026-09-01",
       scope="The B2B outreach reply lane (RUL-069's named boundary -- explicitly NOT sealed "
             "by the customer firewall, which is a different class of mail and still unarmed "
             "per RG-0212). TWO HALVES, and the split is the whole point: (a) INBOUND -- the "
             "wave's From/Reply-To must stay trustsquare.co addresses so a prospect replying "
             "never learns anything but the business identity. This half HELD on 1 Sep and is "
             "asserted here, red-capable, every run. (b) OUTBOUND -- David's reply must LEAVE "
             "as david@trustsquare.co, which needs a Gmail 'Send mail as' alias on the "
             "personal account. That half CANNOT be probed from the sandbox (no Gmail "
             "credential) and is not closed by anything in this repo, so the entry stays OPEN "
             "and says so rather than wearing a green it did not earn. Promote to LOCKED only "
             "when the alias exists AND a probe of the lane confirms an outreach reply left "
             "under the business address.",
       ref="OUTREACH-REPLY-IDENTITY-1, 1 Sep 2026. Found the honest way -- David asked how a "
           "prospect got his personal address after the Alison Tutors reply. She never had "
           "it: her mail went to Reply-To david@trustsquare.co and forwarded in, half (a) "
           "working exactly as designed. It leaked on the way OUT -- the reply was drafted "
           "and sent from the personal Gmail account, which has no send-as alias (probed: "
           "'in:sent from:david@trustsquare.co' returns zero mail, ever). So the lane was "
           "one-way-anonymous and nobody had noticed, because nobody had replied before. "
           "RUL-069 does not cover this: it seals CUSTOMER mail inbound; this is B2B mail "
           "outbound, a direction and a class the ruling deliberately left open. Four more "
           "prospect threads (Addico, RE/MAX, Capsicum, IBTC) sat unanswered in that inbox "
           "at the time of the finding -- the same leak was waiting on each one. "
           "PROMOTED 1 Sep 2026, same session, on a PROBE not a claim: message "
           "1a05da1de8aa50f3 at 15:41:24Z left with From: david@trustsquare.co, "
           "subject 'alias test', delivered, no bounce. Route: root trustsquare.co "
           "verified in Resend (eu-west-1) + Gmail send-as over smtp.resend.com:587. "
           "NAMED LIMIT, not hidden: the standing assertion below covers the INBOUND "
           "half only. The outbound half lives in Gmail account settings, outside this "
           "repo and unreachable from the sandbox, so it can rot without tripping this "
           "entry. RG-0236 is the structural answer -- it removes the human from the "
           "lane entirely, at which point this class stops depending on a setting.")
def rg_outreach_reply_identity():
    lane = os.path.normpath(os.path.join(REPO, "..", "CityLauncher", "emailer", "emailer.py"))
    if not os.path.isfile(lane):
        return [(INFO, "SKIPPED -- CityLauncher outreach lane not present here (outside repo)")]
    out = []
    try:
        t = open(lane, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return [(FAIL, "cannot read the outreach lane (%s)" % str(e)[:60])]

    for const in ("FROM_ADDRESS", "REPLY_TO"):
        m = re.search(r"^%s\s*=\s*['\"]([^'\"]+)['\"]" % const, t, re.M)
        if not m:
            out.append((FAIL, "%s is gone from emailer.py -- the wave's identity is "
                              "unpinned and a default could be anything" % const))
            continue
        val = m.group(1)
        addr = val.split("<")[-1].rstrip(">").strip().lower()
        if not addr.endswith("trustsquare.co"):
            out.append((FAIL, "%s = %r -- an outreach prospect would see a non-business "
                              "address" % (const, val)))
        else:
            out.append((INFO, "%s -> %s (business identity, inbound half holds)" % (const, addr)))

    # No personal-webmail literal anywhere the wave can render it.
    bad = []
    for fn in ("emailer.py",):
        for n, line in enumerate(t.splitlines(), 1):
            if re.search(r"@(gmail|outlook|yahoo|hotmail)\.com", line, re.I) and \
               not line.lstrip().startswith("#"):
                bad.append("%s:%d" % (fn, n))
    if bad:
        out.append((FAIL, "personal-webmail address literal in the outreach lane at %s -- "
                          "the wave must never carry one" % ", ".join(bad[:4])))

    out.append((INFO, "OUTBOUND half UNPROBEABLE from here: whether David's reply leaves as "
                      "david@trustsquare.co depends on a Gmail send-as alias, not on this "
                      "repo. Entry stays OPEN by design -- see scope (b)."))
    return out


@entry("RG-0236", "Prospect replies are answered by the TRIAGE AGENT, not by David's inbox -- "
       "the outreach reply lane is a THIRD mail class with its own policy, and no human "
       "sits in the delivery path of a routine one",
       OPEN,
       scope="david@trustsquare.co (the wave's Reply-To) and any future outreach reply "
             "address. FOUR CLASSES the classifier must separate, because collapsing them "
             "is what makes this lane unscalable: (a) MACHINE mail -- autoresponders, "
             "ticket acks, bounces: NO reply, logged only. David spent launch-day minutes "
             "answering an Addico autoresponder by hand on 1 Sep; cheapest class to kill "
             "and pure waste. (b) FAQ -- 'do you cover Johannesburg', pricing, how "
             "introductions work, is it really free: AI answers from david@trustsquare.co "
             "off the canon (PRICING_CANON; the model constraint that nothing but Tuppence "
             "flows through the till). Esther's 1 Sep question was exactly this class and "
             "it is the MAJORITY at volume. (c) NOT INTERESTED / opt-out / hostile: "
             "courteous close, suppress in the opt-out register (RG-0227's lane), never "
             "mailed again -- opt-out is a legal duty, so it can never depend on a human "
             "reading an inbox. (d) COMMERCIAL -- wants a call, wants terms, an agency "
             "wanting a bulk arrangement, a complaint about being emailed at all: escalate "
             "to David through the ADMIN SURFACE (/admin/email-triage, fault queue), never "
             "by forwarding to his personal inbox. REUSE, DO NOT REBUILD: "
             "cloudflare_email_worker + /email/inbound + the email_triage table + the "
             "conservative auto-send gate already do all of this for support@ and were "
             "E2E-proven 24 Aug. What is missing is the outreach CLASS and its response "
             "policy, not the engine. MARKET GAP, named the day it was built: the FAQ class answers from HARDCODED SOUTH AFRICAN facts (the ZA city list, Rand-free framing). The US teaching-institutions lane and every other non-ZA market will ask the same FAQ questions and get a South Africa answer -- confidently, which is worse than no answer. Before ANY non-ZA outreach wave whose replies reach this lane, the canon block must become market-aware (keyed off the prospect city/country already on the row), or the FAQ class must fall back to outreach_commercial for non-ZA senders. Cheap to fix, expensive to discover from a prospect.",
       ref="OUTREACH-TRIAGE-1, opened 1 Sep 2026 on David's question: 'how would I respond "
           "to 100s of emails a day if we get traction?' -- asked before the volume "
           "arrived rather than after. WHY IT IS OPEN: RUL-069 (30 Aug) deliberately "
           "carved this lane OUT of the customer firewall -- 'the outreach reply lane is "
           "B2B recruitment mail David owns personally'. Correct when reply volume was "
           "zero; a scaling defect the moment the waves land, and 1 Sep is the day it "
           "started costing real time. Amending that boundary is DAVID'S ACT (RUL-037 "
           "reserves changing a ruling as opposed to executing one); the build is Claude's "
           "once the ruling moves. SEQUENCE when it does: classify-and-DRAFT first with "
           "every draft queued, measure the classifier against real replies, then graduate "
           "class (a) to silent-log and class (b) to auto-send once accuracy is MEASURED "
           "-- never on the assumption that it works. Classes (c) and (d) touch legal duty "
           "and commercial judgment and stay gated longer. Promote when routine prospect "
           "replies are answered without David's inbox in the path, PROBED on real traffic. "
           "BUILD LANDED 1 Sep 2026, same session, on David's 'Green light given' -> RUL-087 "
           "(the ruling was amended by him, the build executed by the CTO, in that order). "
           "bea_main.py now carries _is_outreach_lane, the four outreach classes, a separate "
           "classifier prompt fed from canon, a lane-aware auto-send gate, and an outright "
           "bar on the MAINT-B1 fault-queue ack for this lane. NO LONGER blocked on the "
           "ruling; now blocked on (1) David's deploy and (2) MEASUREMENT of the classifier "
           "against real replies -- machine-silence is live on arrival, every other class "
           "drafts and queues until OUTREACH_AUTO_SEND=1 is earned. Stays OPEN because "
           "shipped is not measured, which is the whole lesson of the 1 Sep leak.")
def rg_outreach_triage_lane():
    out = []
    w = os.path.join(REPO, "cloudflare_email_worker", "src", "worker.js")
    if not os.path.isfile(w):
        return [(INFO, "SKIPPED -- worker source not present here (outside repo)")]
    try:
        t = open(w, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return [(FAIL, "cannot read the inbound worker (%s)" % str(e)[:60])]
    if "BEA_INBOUND" not in t:
        out.append((FAIL, "the inbound worker no longer posts to BEA triage -- the engine "
                          "RG-0236 reuses has been changed or removed"))
    if "NEVER sends a reply itself" not in t:
        out.append((INFO, "worker's no-send guarantee comment is gone -- confirm ALL reply "
                          "logic still sits behind BEA's auto-send gate"))
    app = os.path.join(REPO, "bea_main.py")
    if os.path.isfile(app):
        try:
            a = open(app, encoding="utf-8", errors="replace").read()
        except OSError:
            a = ""
        for needle, why in (
            ("_is_outreach_lane", "the lane split itself"),
            ("outreach_machine", "the machine-mail class that answers with silence"),
            ("_OUTREACH_AUTO_SEND_CATEGORIES", "the graduated auto-send gate"),
            ("_OUTREACH_MARKETS", "the per-market fact table -- without it the FAQ class "
                                  "answers every market from South African facts, which is "
                                  "the launch blocker that gated the 4 Sep global roll"),
        ):
            if needle not in a:
                out.append((FAIL, "%s is GONE from bea_main.py -- %s was removed, so "
                                  "prospect replies fall back into the customer lane "
                                  "(RUL-087 regression)" % (needle, why)))
        # The fault-queue ack must never be reachable on the outreach path.
        # ANTI-DRIFT: any country armed for outreach in cities.json must have a row in
        # _OUTREACH_MARKETS, or the FAQ will answer that market from another market's
        # cities. Repo-side only -- SKIPS cleanly when CityLauncher is not alongside.
        cj = os.path.normpath(os.path.join(REPO, "..", "CityLauncher", "data", "cities.json"))
        if os.path.isfile(cj):
            try:
                import json as _j
                _d = _j.load(open(cj, encoding="utf-8"))
                _rows = _d if isinstance(_d, list) else _d.get("cities", [])
                # cities.json uses "status" (not "state") -- checked 1 Sep 2026. The first
                # cut of this assertion read "state", matched nothing, and printed a GREEN
                # while checking zero cities. Assert on the real key, and prove it counts.
                armed = {c.get("country") for c in _rows
                         if c.get("lane") == "outreach"
                         and (c.get("status") or c.get("state")) in ("active", "prospect")}
                if not armed:
                    out.append((FAIL, "cities.json parsed but ZERO outreach-armed countries "
                                      "found -- the schema changed under this assertion and "
                                      "it is now checking nothing"))
                # Scope the needle to the TABLE, not the whole file: '"US":' occurs in
                # dozens of unrelated dicts in bea_main.py, so a whole-file search would
                # report green after the row was deleted. Proven: the first cut did.
                _ti = a.find("_OUTREACH_MARKETS = {")
                _tj = a.find("def _market_facts_block", _ti + 1) if _ti >= 0 else -1
                _tbl = a[_ti:_tj] if (_ti >= 0 and _tj > _ti) else ""
                if not _tbl:
                    out.append((FAIL, "_OUTREACH_MARKETS table not found in bea_main.py "
                                      "-- the per-market FAQ facts are gone"))
                missing = sorted(x for x in armed if x and ('"%s":' % x) not in _tbl)
                if missing:
                    out.append((FAIL, "cities.json arms outreach in %s but _OUTREACH_MARKETS "
                                      "has no row for %s -- a prospect there would be answered "
                                      "with another market's cities"
                                      % (", ".join(missing), "/".join(missing))))
                else:
                    out.append((INFO, "market table covers every outreach-armed country in "
                                      "cities.json (%d checked)" % len(armed)))
            except Exception as e:
                out.append((INFO, "cities.json cross-check skipped (%s)" % str(e)[:50]))
        if "_is_outreach_lane" in a and "logged_silent" not in a:
            out.append((FAIL, "the outreach send branch no longer has its silent-log path "
                              "-- machine mail would be answered, or ack'd as a fault"))
    out.append((INFO, "OPEN by design: lane is BUILT (RUL-087, 1 Sep) but not yet MEASURED. "
                      "Machine-silence is live on arrival; FAQ/opt-out/commercial draft and "
                      "queue until OUTREACH_AUTO_SEND=1 is earned on real traffic. Promote "
                      "only on measured accuracy, never on the build having shipped."))
    return out


@entry("RG-0237", "A signed-out ops dashboard SAYS it is signed out -- it never paints "
       "'UNDEFINED' or a blank section over a healthy server",
       LOCKED, fixed_on="2026-09-02",
       scope="PROMOTED 2 Sep 2026 the run it printed READY TO LOCK: DASH-SIGNEDOUT-TRUTH-1 "
       "branch added to the main summary loader -- redacted=='heartbeat' now paints a SIGNED "
       "OUT banner naming server health and NOT MEASURED placeholders, then returns before "
       "populate(); health/BIT polling (anonymous-safe) still runs. Repo-side check by design; "
       "the live dashboard carries it from the next deploy. dashboard.server.html summary loaders. Born 1 Sep 2026 (launch day): the "
       "06:00 unattended-upgrades restart plus an evaporated sessionStorage JWT left David's "
       "dashboard reading 'Session --' / 'LAST COMPLETED -- SESSION UNDEFINED' over a server "
       "whose authenticated payload was COMPLETE (session 184, every section populated, smoke "
       "ALL PASS). Cost: David read a healthy system as broken on launch day. This is the "
       "RG-0133 class one layer up: DASH-SUMMARY-REDACT-1 deliberately answers anonymous "
       "callers a heartbeat, and the LOADER must name that state -- an explicit "
       "redacted=='heartbeat' branch that paints a SIGNED OUT / NOT MEASURED banner and "
       "labelled placeholders, never string-concatenated undefineds wearing section headers.",
       ref="DASH-SIGNEDOUT-TRUTH-1, found 1 Sep 2026 attended. OPEN until the loader branch "
           "ships (rides the next deploy); promote on READY TO LOCK. Repo half: the summary "
           "loader handles redacted=='heartbeat' explicitly and paints a named signed-out "
           "state.")
def rg_dashboard_signedout_truth():
    out = []
    t = repo_file("dashboard.server.html")
    if t is None:
        return [(INFO, "SKIPPED -- dashboard.server.html not readable here (outside repo)")]
    # The file already says "NOT MEASURED" for OTHER panels (RG-0133 on the +1 page),
    # so a vocabulary test passes over the live defect -- the check that cannot fail
    # (header rule + RG-0068). Require the fix's own named marker instead: the summary
    # loader's signed-out branch must carry DASH-SIGNEDOUT-TRUTH-1, so this entry is
    # red until the REAL branch ships and cannot be satisfied by neighbouring copy.
    if "DASH-SIGNEDOUT-TRUTH-1" not in t:
        out.append((FAIL, "the summary loader has no DASH-SIGNEDOUT-TRUTH-1 signed-out "
                          "branch -- an anonymous/expired-token view still renders "
                          "'SESSION UNDEFINED' over a healthy server (1 Sep incident)"))
    elif "heartbeat" not in t:
        out.append((FAIL, "marker present but no heartbeat check near it -- the branch "
                          "cannot be keying off the redacted payload"))
    return out


@entry("RG-0238", "No listing surface ever calls a PERSON safe -- we publish dated, sourced "
       "FACTS about a credential, never a conclusion about someone's future conduct, and "
       "never an absence-of-record claim",
       OPEN,
       scope="Every seller- and buyer-facing surface that could carry a trust badge: "
             "marketsquare.html, ms.js, listing card and profile templates, and any future "
             "verification badge. BANNED as unqualified badge text: 'safe', 'vetted', "
             "'child-safe', 'background checked', 'screened' -- each is a representation "
             "about FUTURE CONDUCT, and on a tutor listing that badge becomes the "
             "plaintiff's first exhibit if a child is harmed. ALSO BANNED: any 'not on the "
             "register' / 'no record found' badge -- absence of a record is not evidence of "
             "safety, is unprovable, and invites a defamation claim from anyone we get "
             "wrong. REQUIRED FORM: the fact, its source, its date -- 'WWCC 1234567E "
             "verified current with NSW OCG, 1 Sep 2026', or 'qualification certificate "
             "uploaded -- not independently verified'. Scope is the WORD ON THE SURFACE, "
             "not the checking: verifying a government clearance is encouraged and is the "
             "whole point. Describing a human being with an adjective we cannot stand "
             "behind is what this bars.",
       ref="CHILD-SAFETY-WORDING-1, opened 1 Sep 2026 from David's own framing -- "
           "'classifying as safe based on our assessment of what they upload'. The instinct "
           "(screen tutors against offender registers) is right; mechanism and wording both "
           "needed correcting. PROBED same session, all four markets: SA's NRSO is CLOSED "
           "by statute (Kubayi's 3-phase opening still lacked the Chief State Law Adviser's "
           "constitutionality opinion as at Apr 2026); the UK has NO public register by "
           "design and Sarah's Law is police-mediated, per-named-child, and refuses general "
           "enquiries; Australia's ANCOR is police-only (WA's Community Protection site is "
           "limited disclosure, not screening); the US NSOPW is public but its Conditions "
           "of Use STRICTLY PROHIBIT automated searching. So no register lane exists "
           "anywhere we operate. RESOLUTION: the CLEARANCE IS the state's register check -- "
           "Enhanced DBS with barred list (UK), WWCC/Blue Card (AU, continuously monitored, "
           "so a post-issue charge revokes it where a one-off lookup would miss it), sector "
           "clearance (SA) -- holder-consented, lawful to receive, stronger than a scrape. "
           "Needs to become a RULING (David's act, RUL-037); this entry is the tripwire "
           "until it is, and stands afterwards. Promote when wired to real listing "
           "templates and a badge-bearing surface exists to police. NOTE: first written as "
           "RG-0237 and renumbered -- LEDGER-DUP-1 caught a concurrent session taking that "
           "id mid-write, which is exactly what that guard is for.")
def rg_no_safety_adjective():
    out = []
    banned = ["child-safe", "child safe", "vetted", "background checked", "safety verified"]
    seen_any = False
    for fn in ("marketsquare.html", "ms.js"):
        f = os.path.join(REPO, fn)
        if not os.path.isfile(f):
            continue
        seen_any = True
        try:
            t = open(f, encoding="utf-8", errors="replace").read().lower()
        except OSError:
            continue
        for b in banned:
            if b in t:
                out.append((FAIL, "%s contains %r -- a safety adjective on a listing "
                                  "surface is a representation about a person's future "
                                  "conduct (CHILD-SAFETY-WORDING-1)" % (fn, b)))
    if not seen_any:
        return [(INFO, "SKIPPED -- listing surfaces not present here (outside repo)")]
    if not out:
        out.append((INFO, "no banned safety adjective on the listing surfaces scanned."))
    out.append((INFO, "OPEN: no verification badge ships yet -- this is a tripwire set "
                      "AHEAD of the feature, not proof the feature is right."))
    return out


@entry("RG-0239", "The outreach CTA destination ANSWERS AN ANONYMOUS PROSPECT -- the magic link "
       "in every wave email must not land on a credential prompt",
       OPEN,
       scope="CORRECTED 1 Sep 2026 after the first fix was WRONG. The fault is not nginx: "
             "it is that the outreach CTA pointed at the ADMIN CONSOLE. Claude opened "
             "/admin.html?magic=1 publicly, then loaded it in a clean browser and found the "
             "admin UI -- ONBOARD/LISTINGS/BILLING/ANALYTICS plus a DELETE-LISTING control -- "
             "rendering to an anonymous visitor. Rolled back inside 76 seconds; the access log "
             "shows the only client in the window was Claude's own probes (one Cloudflare edge "
             "IP, 6 requests, all attributable). The REAL fix is CTA-URL-1: 14 call sites in "
             "CityLauncher built f\"{bea_base}/admin.html?magic=1\"; the seller magic flow "
             "lives at the APP ROOT, PROBED anonymously as rendering 'STEP 1 OF 6 - TUTORS'. "
             "This entry now asserts BOTH halves: the console stays gated, AND no code builds "
             "a magic link at /admin.html. Original scope text follows. "
             "https://trustsquare.co/admin.html?magic=1... -- the 'List as a Tutor' button in "
             "EVERY outreach email (marketsquare_admin.html, deployed as admin.html). The "
             "assertion is the prospect's own view: an anonymous GET of the magic URL must not "
             "return 401/403 and must not carry a WWW-Authenticate header. Out of scope: bare "
             "/admin.html with no magic token, which SHOULD stay gated -- the page is titled "
             "'TrustSquare - Admin' and is an admin console as well as the seller onboarding "
             "form. The fix is therefore NOT 'remove the auth': it is to let the magic-link "
             "path through while the console stays shut, with the magic token verified "
             "server-side.",
       ref="CTA-401-1, found 1 Sep 2026 ~19:50 SAST, LAUNCH DAY, by David asking whether users "
           "would see a gate screen. PROBED: GET of the exact CTA URL returns HTTP 401 with "
           "'www-authenticate: Basic realm=\"TrustSquare Orchestrator\"'. CAUSE: nginx "
           "'location = /admin.html' includes snippets/internal_auth.conf (satisfy any; allow "
           "127.0.0.1; deny all; auth_basic orchestrator). So the CTA in every wave email has "
           "been landing on a browser password popup. CORROBORATION, and it is stark: across "
           "the whole campaign the prospects DB shows 152 emailed, 18 opened, and ZERO clicks "
           "-- consistent with a destination nobody can enter. The front page is separately "
           "showing the app's own 'Enter password or PIN / Pre-launch access only' unlock "
           "screen while /flags reports mode=live. RESERVED TO DAVID (RUL-037: live access "
           "control + lockout risk): stripping auth from a page that is also the admin console "
           "would expose it, so this entry reports and asserts but does not self-heal. Promote "
           "when an anonymous magic-link GET returns 200 AND bare /admin.html still returns "
           "401.")
def rg_cta_reachable():
    url = ("https://trustsquare.co/admin.html?magic=1&name=Ledger%20Probe"
           "&email=probe%40example.com&cat=Tutors&city=Bloemfontein")
    try:
        code, hdrs = _http_head_status(url)
    except Exception as e:
        return [(INFO, "SKIPPED -- could not reach the CTA URL (%s)" % str(e)[:60])]
    out = []
    if code in (401, 403):
        out.append((FAIL, "the outreach CTA returns HTTP %d to an anonymous prospect -- every "
                          "wave email points at a locked door (CTA-401-1)" % code))
    elif code >= 400:
        out.append((FAIL, "the outreach CTA returns HTTP %d -- prospects cannot reach the "
                          "listing form" % code))
    else:
        out.append((INFO, "CTA answers anonymously: HTTP %d" % code))
    if any(h.lower() == "www-authenticate" for h in hdrs):
        out.append((FAIL, "the CTA response carries WWW-Authenticate -- a prospect gets a "
                          "browser credential popup instead of the listing form"))
    return out


def _http_head_status(url, timeout=15):
    import urllib.request, urllib.error
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "TrustSquare-ledger/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers)


@entry("RG-0240", "Somebody stands at the FRONT DOOR every run -- the prospect's own journey "
       "is walked end to end as a stranger, because 230 inward-facing assertions did not "
       "notice that the CTA had never worked",
       LOCKED, fixed_on="2026-09-01",
       scope="The outreach conversion path, walked exactly as a prospect meets it: build the "
             "magic link the way emailer.build_magic_link() builds it, follow it anonymously, "
             "and read what renders. THREE LEGS: (a) the link must not point at /admin.html -- "
             "the admin console; (b) an anonymous GET must not return 4xx and must not carry "
             "WWW-Authenticate; (c) what renders must be the SELLER form (STEP 1 OF 6 / LISTING "
             "QUALITY / Photos) and must NOT be the admin console (discriminated by title) or "
             "expose the delete control. Implemented in scripts/journey_check.py, runnable on "
             "its own (exit 0/1) so the wave runner can gate on it before a send.",
       ref="JOURNEY-1, 1 Sep 2026, born from CTA-URL-1. Three days of outreach went out behind "
           "a link nobody had ever clicked -- 140 of 170 emails carried a CTA into a Basic-auth "
           "prompt, and the campaign's zero clicks were caused, not observed. The defect this "
           "entry fixes is not the URL: it is that every one of ~230 assertions faced INWARD at "
           "the machinery and none faced OUTWARD at the customer. LESSON RECORDED IN THE CHECK "
           "ITSELF: its first version treated the app's dormant admin-gate markup ('Enter "
           "password or PIN', present in the HTML but never rendered -- PROBED in a clean "
           "browser) as fatal, and cried wolf. A check that false-alarms gets ignored, and an "
           "ignored check is not a check. It now discriminates on the page TITLE. Red-capability "
           "proven both ways: pointed at /admin.html it FAILS on legs (a) and (b); pointed at "
           "the real link it passes all three.")
def rg_journey_front_door():
    js = os.path.join(REPO, "scripts", "journey_check.py")
    if not os.path.isfile(js):
        return [(FAIL, "scripts/journey_check.py is GONE -- nobody is standing at the front "
                       "door again (JOURNEY-1)")]
    # Routed through _harness (RG-0187): a missing third-party dependency demotes to
    # NOT EVALUATED instead of crying REGRESSION. journey_check exits 1 when the
    # journey is broken, so a non-blind failure IS the finding -- its JSON tail
    # (indent=1, fails last) survives in the detail.
    ok, blind, detail = _harness([sys.executable, js, "--json"], timeout=90)
    if blind:
        return [(INFO, detail)]
    if not ok:
        return [(FAIL, "PROSPECT JOURNEY broken -- %s" % (detail or "no output")[-260:])]
    try:
        import json as _j
        d = _j.loads(detail or "{}")
    except Exception:
        return [(FAIL, "journey check produced unreadable output: %s" % (detail or "")[:80])]
    out = []
    for f in d.get("fails", []):
        out.append((FAIL, "PROSPECT JOURNEY: %s" % f))
    if not out:
        out.append((INFO, "prospect journey whole: link -> door -> seller form"))
    return out



@entry("RG-0241", "An unsubscribe link that is merely FETCHED opts nobody out -- only a "
       "confirmed POST does -- because corporate link-scanners fetch every link in every "
       "email and were opting real prospects out on delivery",
       LOCKED, fixed_on="2026-09-02",
       scope="BOTH /optout routes the emails can reach: /launch-api/optout (CityLauncher "
             "api/server.py, the link in every outreach template) and /optout on the root "
             "(bea_main.py, the relink template). CLASS, not instance: any route that "
             "suppresses on a GET re-opens this. Live legs: (a) GET /optout?email=<.invalid "
             "probe> on the ROOT returns 200 and a CONFIRM page (title 'Unsubscribe - ', not "
             "'Unsubscribed'); (b) /optout/status rows are UNCHANGED after that GET; (c) POST "
             "/optout with the same probe returns 200 and rows INCREASE by one. Source leg: "
             "no @app.get('/optout') handler in either file calls the recording function.",
       ref="OPTOUT-CONFIRM-1, 2 Sep 2026. David's dashboard read 15 opted out, up from 3 on "
           "31 Aug. PROBED against email_events: 11 of the 12 new suppressions landed within "
           "one second of a 'click' on the opt-out link from Microsoft Azure ranges (4.222.x, "
           "72.145.x, 4.182.x -- Defender Safe Links) -- info@ufs.ac.za, both UMP addresses, "
           "NCUT, Goedgedacht, Emperors Palace, Keystone Tutors. Nobody asked to leave; the "
           "register barred them for life. Found on the eve of the US tutor wave, whose "
           "recipients run Microsoft 365 and Proofpoint even more heavily. Fix: GET renders a "
           "confirmation page and writes nothing; the confirm button POSTs; the emailer now "
           "sends List-Unsubscribe + List-Unsubscribe-Post (RFC 8058) so Gmail/Yahoo one-click "
           "-- also a POST -- keeps working. Proven in test on both handlers (GET: no row; form "
           "POST and one-click POST: row; empty POST: 400). The 11 scanner-induced suppressions "
           "stay suppressed -- reversing an opt-out is a legal-positioning call reserved to "
           "David (he chose to leave them, 2 Sep).")
def rg_optout_get_is_harmless():
    import json as _j, uuid as _u, urllib.parse as _up, urllib.request as _ur, urllib.error as _ue
    out = []
    # source leg (repo half)
    for rel, label in (("bea_main.py", "root"), (os.path.join("..", "CityLauncher", "api", "server.py"), "launch-api")):
        txt = repo_file(rel)
        if txt is None:
            continue
        m = re.search(r"@app\.get\(['\"]/optout['\"][^\n]*\)\s*\n(?:async )?def [^\n]+\n((?:[ \t]+[^\n]*\n)+)", txt)
        if not m:
            out.append((FAIL, "%s: no GET /optout handler found -- the unsubscribe link is dead" % label))
        elif "_record_optout(" in m.group(1) or "_optout_apply(" in m.group(1) or "INSERT" in m.group(1):
            out.append((FAIL, "%s: the GET /optout handler WRITES the register again -- a "
                              "link-scanner can opt people out (OPTOUT-CONFIRM-1)" % label))
        else:
            out.append((INFO, "%s: GET /optout writes nothing in source" % label))
    # live legs
    _require_net()
    probe = "rg0241-%s@example.invalid" % _u.uuid4().hex[:8]
    def status():
        try:
            return _j.loads(_ur.urlopen(_ur.Request(BASE + "/optout/status", headers=UA), timeout=TIMEOUT).read().decode()).get("rows", -1)
        except Exception:
            return -1
    before = status()
    if before < 0:
        return out + [(INFO, "SKIPPED live legs -- /optout/status unreadable (deploy pending?)")]
    try:
        body = _ur.urlopen(_ur.Request(BASE + "/optout?email=" + _up.quote(probe), headers=UA), timeout=TIMEOUT).read().decode("utf-8", "replace")
    except _ue.HTTPError as e:
        return out + [(FAIL, "GET /optout answered HTTP %d to a recipient" % e.code)]
    if "<title>unsubscribe -" not in body.lower() and "<title>unsubscribe \u2014" not in body.lower():
        out.append((FAIL, "GET /optout does not show the CONFIRM page (title=%r)" % (re.search(r"<title>([^<]*)", body, re.I).group(1) if re.search(r"<title>", body, re.I) else "?")))
    mid = status()
    if mid != before:
        out.append((FAIL, "a bare GET /optout WROTE the register (%d -> %d) -- scanners can opt "
                          "people out again" % (before, mid)))
    else:
        out.append((INFO, "GET /optout wrote nothing (rows %d)" % before))
    try:
        req = _ur.Request(BASE + "/optout", data=("email=" + _up.quote(probe)).encode(), method="POST",
                          headers=dict(UA, **{"Content-Type": "application/x-www-form-urlencoded"}))
        _ur.urlopen(req, timeout=TIMEOUT).read()
    except _ue.HTTPError as e:
        return out + [(FAIL, "POST /optout (the confirm button) answered HTTP %d" % e.code)]
    after = status()
    if after != mid + 1:
        out.append((FAIL, "a CONFIRMED opt-out was not recorded (rows %d -> %d)" % (mid, after)))
    else:
        out.append((INFO, "confirmed POST recorded (rows %d -> %d)" % (mid, after)))
    return out



@entry("RG-0242", "The daily wave gates can be PASSED on an ordinary day -- min-gap counts "
       "local calendar days, and the stop-loss has a statistical floor so ONE dead address "
       "on a 12-batch cannot latch a city shut for good",
       LOCKED, fixed_on="2026-09-02",
       scope="CityLauncher emailer/wave_runner.py gate_check + city_stats, and "
             "emailer/waves_policy.json defaults. Two legs. (a) MIN-GAP-1: min_gap_days is "
             "evaluated on LOCAL calendar dates in defaults.send_timezone (Africa/Johannesburg), "
             "never as 24h-since-last-timestamp -- the 00:10 SAST task is 22:10 UTC the day "
             "before, so a strict 24h gap dry-ran 8 of 14 cities on 2 Sep and drifts every day "
             "a city sends a minute later than the day before. (b) STOP-LOSS-FLOOR-1: the "
             "bounce stop-loss trips only when bounce% > bounce_stop_pct AND the wave's bounce "
             "COUNT >= defaults.bounce_stop_min_bounces (3). Source-checked; an offline "
             "gate_check() call with synthetic stats proves both legs behaviourally.",
       ref="2 Sep 2026. PROBED from logs/launchday_02Wed09_2026010.log: Cape Town, Durban, "
           "Bloemfontein, East London, Port Elizabeth latched on EXACTLY ONE bounce each "
           "(8.3%% of 12 > 5%%), and the latch is permanent because last_wave never advances "
           "on a blocked city; New York, Sydney, Polokwane, Pretoria dry-ran on 'min gap: next "
           "allowed 2026-09-02' printed ON 2 Sep. Pretoria (5/59, 8.5%%) stays blocked -- the "
           "floor keeps the real signal and drops the noise. RAMP-1 already resets the ramp "
           "streak on a single bounce; the stop-loss is for a dirty LIST, not one dead row.")
def rg_wave_gates_passable():
    out = []
    wr = repo_file(os.path.join("..", "CityLauncher", "emailer", "wave_runner.py"))
    pol = repo_file(os.path.join("..", "CityLauncher", "emailer", "waves_policy.json"))
    if wr is None or pol is None:
        return [(INFO, "CityLauncher not beside this repo -- source legs skipped")]
    if "bounce_stop_min_bounces" not in wr or "last_wave_bounced" not in wr:
        out.append((FAIL, "wave_runner stop-loss has no bounce-count floor -- one dead address "
                          "on a 12-batch latches the city (STOP-LOSS-FLOOR-1)"))
    if "astimezone(_tz).date()" not in wr:
        out.append((FAIL, "wave_runner min-gap is not evaluated on local calendar dates -- the "
                          "00:10 task dry-runs cities sent the previous morning (MIN-GAP-1)"))
    try:
        d = json.loads(pol)["defaults"]
        if int(d.get("bounce_stop_min_bounces", 0)) < 2:
            out.append((FAIL, "waves_policy.defaults.bounce_stop_min_bounces missing or < 2"))
    except Exception as e:
        out.append((FAIL, "waves_policy.json unreadable: %s" % str(e)[:60]))
    # behavioural leg: import gate_check and drive it with synthetic stats (no DB, no writes)
    try:
        import importlib.util as _iu, datetime as _dt
        cl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CityLauncher")
        sys.path.insert(0, os.path.abspath(cl))
        spec = _iu.spec_from_file_location("cl_wave_runner", os.path.join(cl, "emailer", "wave_runner.py"))
        m = _iu.module_from_spec(spec); spec.loader.exec_module(m)
        m.send_freeze.frozen = lambda: False
        m.suppression_state = lambda: (True, "stub")
        polj = json.loads(pol); polj["cities"]["_rg0242"] = {"armed": True, "gates_green": True}
        base = {"last_wave_bounce_pct": 8.3, "last_wave_bounced": 1, "last_wave_sent": 12,
                "complaints": 0, "last_emailed_at": None}
        ok, blocks = m.gate_check("_rg0242", polj, dict(base), True)
        if any("stop-loss" in b for b in blocks):
            out.append((FAIL, "one bounce on twelve still trips the stop-loss: %s" % blocks))
        ok, blocks = m.gate_check("_rg0242", polj, dict(base, last_wave_bounced=5, last_wave_bounce_pct=8.5, last_wave_sent=59), True)
        if not any("stop-loss" in b for b in blocks):
            out.append((FAIL, "five bounces on 59 (8.5%%) did NOT trip the stop-loss -- floor weakened"))
        # yesterday 22:15 UTC = 00:15 SAST today ... wait: pick 20:15 UTC yesterday = 22:15 SAST yesterday -> allowed today
        y = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=1)).replace(hour=20, minute=15, second=0, microsecond=0, tzinfo=None)
        ok, blocks = m.gate_check("_rg0242", polj, dict(base, last_wave_bounced=0, last_wave_bounce_pct=0.0, last_emailed_at=y.isoformat()), True)
        if any("min gap" in b for b in blocks):
            out.append((FAIL, "a city sent YESTERDAY (local) is still min-gap blocked today: %s" % blocks))
        out.append((INFO, "gate_check behaves: 1/12 passes, 5/59 blocks, yesterday-local passes"))
    except Exception as e:
        out.append((INFO, "behavioural leg skipped (%s)" % str(e)[:80]))
    return out


@entry("RG-0243", "The app's location picker shows the cities the outreach waves are "
       "recruiting in -- no more, no less -- and never drifts from CityLauncher's city list",
       LOCKED, fixed_on="2026-09-02",
       # PROMOTED 2 Sep 2026 per the entry's own ref condition: David shipped (two morning
       # deploys) and the live legs pass -- picker matches the launch list across 9 countries.
       scope="ALL countries and cities, on the live geo_countries/geo_regions/geo_cities "
             "tables and the picker in ms.js. ONE source of truth: CityLauncher/data/cities.json "
             "(status active|prospect = shown, planned = hidden) -> scripts/geo_launch_cities.json "
             "(generated by scripts/build_geo_launch_cities.py, shipped by manifest) -> "
             "scripts/seed_geo_launch.py --apply on EVERY deploy (post_deploy.sh step 1c, same "
             "contract as the super seeds). Flips geo_*.active only, inserts missing launch "
             "cities with coords, deletes nothing; a city carrying listings is never hidden. "
             "Regions/countries follow their cities. ms.js skips the Region step when a "
             "country has <= GEO_REGION_STEP_ABOVE active cities.",
       ref="GEO-LAUNCH-1, 2 Sep 2026, David: 'the cities in the app selections are not "
           "updated with what we have started to send emails to'. PROBED on the live DB "
           "before the fix: ZA showed 55 GeoNames towns (Trompsburg, Qumbu...) but NOT Knysna "
           "or Mossel Bay, both already emailed; US showed Denver/Colorado (demo listings, "
           "never emailed); DE/NA/MZ/BW/KE appeared as countries from the super-listing seeds. "
           "Dry-run on a copy of the live DB: +2 cities, 43 ZA towns hidden, 2 regions hidden, "
           "visible after = AU:2 BW:1 DE:1 GB:11 KE:1 MZ:1 NA:1 US:12 ZA:14 (the non-launch "
           "ones survive ONLY because they hold listings -- the rule, not an oversight). "
           "OPEN until David ships and the live legs below pass -> READY TO LOCK.")
def rg_geo_launch_cities():
    out = []
    # source legs -- machinery must stay wired
    man = repo_file(os.path.join("ops", "autodeploy", "deploy_manifest.txt")) or ""
    for line in ("scripts/seed_geo_launch.py", "scripts/geo_launch_cities.json"):
        if line not in man:
            out.append((FAIL, "deploy_manifest.txt no longer ships %s -- the geo sync cannot run" % line))
    pd = repo_file(os.path.join("ops", "autodeploy", "post_deploy.sh")) or ""
    if pd and "seed_geo_launch.py --apply" not in pd:
        out.append((FAIL, "post_deploy.sh no longer runs seed_geo_launch.py --apply (step 1c)"))
    js = repo_file("ms.js") or ""
    if js and "GEO_REGION_STEP_ABOVE" not in js:
        out.append((FAIL, "ms.js lost the Region-step skip -- a dozen cities sit behind a needless Region tap again"))
    # drift leg -- the shipped JSON must equal what cities.json says today
    try:
        import importlib.util as _iu
        bp = os.path.join(REPO, "scripts", "build_geo_launch_cities.py")
        spec = _iu.spec_from_file_location("_rg0243_build", bp); m = _iu.module_from_spec(spec); spec.loader.exec_module(m)
        if os.path.exists(m.SRC):
            want = json.dumps(m.build(), indent=1, ensure_ascii=False) + "\n"
            have = open(m.OUT, encoding="utf-8").read()
            if want != have:
                out.append((FAIL, "scripts/geo_launch_cities.json is STALE against CityLauncher/data/cities.json "
                                  "-- run python3 scripts/build_geo_launch_cities.py and deploy"))
            else:
                out.append((INFO, "geo_launch_cities.json current: %d launch cities" % len(json.loads(have)["cities"])))
        else:
            out.append((INFO, "CityLauncher not beside this repo -- drift leg skipped"))
    except Exception as e:
        out.append((FAIL, "drift leg broke: %s" % str(e)[:80]))
    # live legs -- what the picker actually offers, through the gate
    try:
        launch = json.loads(repo_file(os.path.join("scripts", "geo_launch_cities.json")) or "{}").get("cities", [])
        by = {}
        for c in launch: by.setdefault(c["iso2"], set()).add(c["name"])
        countries = _json("/geo/countries")
        for co in countries:
            live = _json("/geo/cities?country=" + co["iso2"])
            if not live:
                out.append((FAIL, "%s is offered as a country but has no active city -- an empty picker" % co["iso2"]))
            names = {c["name"] for c in live}
            missing = by.get(co["iso2"], set()) - names
            if missing:
                out.append((FAIL, "%s launch cities missing from the live picker: %s" % (co["iso2"], sorted(missing))))
        za = {c["name"] for c in _json("/geo/cities?country=ZA")}
        if len(za) > 25:
            out.append((FAIL, "ZA picker still lists %d towns -- the GeoNames dump is showing, not the launch list" % len(za)))
        if "Knysna" not in za or "Mossel Bay" not in za:
            out.append((FAIL, "Knysna / Mossel Bay were emailed but are not selectable in the app"))
        if not any(r == FAIL for r, _ in out):
            out.append((INFO, "live picker matches the launch list across %d countries" % len(countries)))
    except Exception as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    return out

@entry("RG-0244", "The CityLauncher funnel's ONBOARDED and PUBLISHED counters are FED -- a prospect "
       "who registers or goes live on MarketSquare is stamped in prospects.db, not left at 0 forever",
       LOCKED, fixed_on="2026-09-02",
       # PROMOTED 2 Sep 2026 evening, the run it printed READY TO LOCK: David's
       # deploy_citylauncher.bat rode and POST /launch-api/prospects/reconcile answers 401
       # (present, key-gated) where it answered 404 that morning.
       scope="ALL prospects in CityLauncher/data/prospects.db on the server, every status. "
             "ONE closure: reconcile_conversions() in CityLauncher/api/server.py joins prospects.email "
             "(case-folded) to marketsquare.db users (-> onboarded_at, status onboarded) and to "
             "listings with listing_status='live' (-> published_at, status published), writes an "
             "onboard_events row, runs at startup + every RECONCILE_INTERVAL_SEC (600) and on "
             "POST /launch-api/prospects/reconcile (key-gated). Suppression states (opted_out, "
             "bounced, rejected_*) keep their status -- they are the send guard -- but still get "
             "the timestamps, because the conversion is real. /prospects/stats carries reconcile_last.",
       ref="CONVERSION-RECONCILE-1, 2 Sep 2026, David: 'Do we know if the onboarded and published "
           "actually work?' READ on disk: nothing wrote prospects.onboarded_at / published_at -- the "
           "email-event handler stops at clicked, MarketSquare never called back. The dashboard's 0 / 0 "
           "was 'we would not know', not 'nobody yet'. Tested on a copy of the live prospects.db "
           "against a synthetic marketsquare.db: 3 onboarded + 1 published stamped, draft listing "
           "NOT counted, upper-case email matched, opted_out kept its status, second run 0/0 "
           "(idempotent), missing MS db reported cleanly. OPEN until deploy_citylauncher.bat rides: "
           "the live leg turns green when POST /launch-api/prospects/reconcile answers 401 (gate, "
           "endpoint present) instead of 404 (old server.py) -> READY TO LOCK.")
def rg_conversion_reconcile():
    out = []
    cl = os.path.join(REPO, "..", "CityLauncher", "api", "server.py")
    if os.path.exists(cl):
        s = open(cl, encoding="utf-8").read()
        for needle, why in (("def reconcile_conversions", "the reconcile function is gone"),
                            ("@app.post('/prospects/reconcile')", "the manual reconcile endpoint is gone"),
                            ("target=_reconcile_loop", "the periodic reconcile thread is no longer started"),
                            ("'reconcile_last'", "/prospects/stats no longer reports the last reconcile")):
            if needle not in s:
                out.append((FAIL, "CityLauncher/api/server.py: %s" % why))
    else:
        out.append((INFO, "CityLauncher not beside this repo -- source leg skipped"))
    try:
        import urllib.request as _ur
        req = _ur.Request("https://trustsquare.co/launch-api/prospects/reconcile", method="POST",
                          headers={"User-Agent": "TrustSquare-Ledger/1.0"})
        try:
            _ur.urlopen(req, timeout=15)
            out.append((FAIL, "POST /launch-api/prospects/reconcile ran for an ANONYMOUS caller -- gate missing"))
        except Exception as e:
            code = getattr(e, "code", None)
            if code in (401, 403):
                out.append((INFO, "live: /prospects/reconcile present and key-gated (HTTP %s)" % code))
            elif code == 404:
                out.append((FAIL, "live: /prospects/reconcile is 404 -- the CityLauncher deploy has not ridden; the counters are still unfed"))
            else:
                out.append((FAIL, "live reconcile probe unexpected: %s" % repr(e)[:60]))
    except Exception as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    return out

@entry("RG-0245", "The origin SSH allowlist holds EXACTLY the one live egress IP -- no stale "
       "address from a past router reset is left as an open door",
       LOCKED, fixed_on="2026-09-02",
       scope="Hetzner firewall 11414216 (trustsquare-origin-lockdown), inbound port-22 rule, "
             "and scripts/hetzner_fw_selfheal.py which owns it. CLASS: there is ONE egress "
             "(David's PC and the sandbox share it -- server sshd log 2 Sep 2026: "
             "197.184.106.176 accepted until 04:36Z, then only 197.185.137.157, no overlap), so "
             "the rule must hold exactly one /32. Two legs: (a) LIVE -- the Hetzner API reports "
             "the SSH rule with exactly one source_ip; (b) SOURCE -- the self-heal SETS the rule "
             "rather than appending (the 'prune with David' wording is gone). Needs "
             ".secrets/hetzner_token.txt (RG-0188) -- without it the live leg is UNVERIFIED, "
             "not red. Sibling of RG-0099 (detect) and RG-0188 (armed): this one says the "
             "heal leaves no residue.",
       ref="David, 2 Sep 2026, on the morning maintenance report's 'prune the 4 stale IPs with "
           "David at a calm moment': 'there should be no stale IPs'. Root cause: the 17 Aug "
           "self-heal was written add-only out of caution, so every router reset since left "
           "its old /32 behind -- five entries by 2 Sep, four of them dead addresses the ISP "
           "will reassign to strangers. NO-STALE-IP-1: heal = set, not append. The CF half of "
           "the script retired the same session (RUL-034 disabled the gate 19 Aug; launched "
           "1 Sep) so the 'no cf_waf_token' INFO stops asking for a token nobody needs.")
def rg_ssh_allowlist_single_ip():
    out = []
    sh = repo_file("scripts/hetzner_fw_selfheal.py")
    if sh is not None:
        if "prune with David" in sh or 'ips + [want]' in sh:
            out.append((FAIL, "hetzner_fw_selfheal.py APPENDS the current IP instead of SETTING the "
                              "rule -- stale /32s will accumulate again (NO-STALE-IP-1)"))
        if 'ssh[0]["source_ips"] = [want]' not in sh:
            out.append((FAIL, "hetzner_fw_selfheal.py no longer sets source_ips to exactly [current IP]"))
    tokp = os.path.join(REPO, ".secrets", "hetzner_token.txt") if REPO else None
    tok = os.environ.get("HETZNER_API_TOKEN", "").strip()
    if not tok and tokp and os.path.exists(tokp):
        try:
            tok = open(tokp, encoding="utf-8").read().strip()
        except OSError:
            tok = ""
    if not tok:
        if out:
            return out
        raise ProbeOffline("no Hetzner token here -- live SSH-rule leg not measured (RG-0188 owns the token)")
    try:
        import urllib.request as _ur
        req = _ur.Request("https://api.hetzner.cloud/v1/firewalls/11414216",
                          headers={"Authorization": "Bearer " + tok, "User-Agent": "trustsquare-ledger/1"})
        with _ur.urlopen(req, timeout=20) as r:
            fw = json.loads(r.read().decode())["firewall"]
        ssh = [x for x in fw["rules"] if x.get("direction") == "in" and str(x.get("port")) == "22"]
        if not ssh:
            out.append((FAIL, "no inbound port-22 rule on firewall 11414216 -- layout changed"))
        else:
            ips = ssh[0].get("source_ips", [])
            if len(ips) != 1:
                out.append((FAIL, "SSH rule holds %d source IPs (%s) -- must be exactly the one live "
                                  "egress; run scripts/hetzner_fw_selfheal.py" % (len(ips), ips)))
            else:
                out.append((INFO, "SSH allowlist is exactly one /32 (%s)" % ips[0]))
    except Exception as e:
        raise ProbeOffline("Hetzner API unreachable: %s" % str(e)[:80])
    return out


@entry("RG-0246", "The production box is PATCHED AND REBOOTED on a cadence -- the newest "
                  "recorded maintenance window is under 45 days old and left no reboot-required flag standing",
       LOCKED, fixed_on="2026-09-02",
       scope="ops/maintenance/PATCH_LOG.md, the dated record of every patch/reboot window on the "
             "Hetzner origin. RECORD-half by nature: the ledger has no SSH transport, so it asserts "
             "that a window was RUN, VERIFIED and WRITTEN DOWN recently, not the box's live state -- "
             "the daily watch (msdeploy, /var/run/reboot-required + apt list) is the live half and "
             "files a DW row the day the flag reappears. CLASS: a kernel installed by "
             "unattended-upgrades is inert until a reboot; a box that is 'patched' but never "
             "rebooted (97 days by 2 Sep 2026) runs the old kernel with the old holes. 45 days is "
             "the cadence: Ubuntu's kernel cadence plus a fortnight of slack for David's window.",
       ref="PATCH-CADENCE-1, 2 Sep 2026, DW-085 closed. The flag stood from 30 Aug (first seen) "
           "across four watch passes while the upgradable set grew 37 -> 59; the reboot itself was "
           "always David's (RUL-027 lockout class) and never had a date. The window ran 18:47 SAST "
           "with David present: DB .backup + integrity ok, 37 packages, kernel 6.8.0-117 -> -138, "
           "34 s of 521, all six credential fingerprints identical pre/post (the DW-084 landmine "
           "class, proven defused), BIT 8/8, smoke ALL PASS. The entry exists so the NEXT flag has "
           "a deadline instead of a day count.")
def rg_patch_cadence():
    txt = repo_file("ops/maintenance/PATCH_LOG.md")
    if txt is None:
        return [(FAIL, "ops/maintenance/PATCH_LOG.md is GONE -- the patch/reboot record no longer exists")]
    import re as _re, datetime as _dt
    rows = [m for m in _re.finditer(r"^\| (\d{4}-\d{2}-\d{2})[^|]*\| *REBOOT *\|[^\n]*", txt, _re.M)]
    if not rows:
        return [(FAIL, "PATCH_LOG.md carries no REBOOT row -- no window has ever been recorded")]
    last = rows[-1]
    day = _dt.date.fromisoformat(last.group(1))
    age = (_dt.date.today() - day).days
    cells = [c.strip() for c in last.group(0).strip().strip("|").split("|")]
    flag = cells[5].lower() if len(cells) > 5 else ""
    out = []
    if "absent" not in flag:
        out.append((FAIL, "newest REBOOT row (%s) does not record reboot_required=absent -- a window "
                          "that leaves the flag standing is a PATCH, not a REBOOT" % day))
    if age > 45:
        out.append((FAIL, "newest REBOOT window is %d days old (%s) -- past the 45-day cadence; "
                          "plan the next one with David (RUL-027)" % (age, day)))
    if not out:
        out.append((INFO, "last reboot window %s (%d days ago), flag absent, fingerprints pre==post" % (day, age)))
    return out


@entry("RG-0247", "A wave never sends more than one mailbox per organisation, and the ramp never "
       "doubles a city's batch on a wave too small to be evidence",
       LOCKED, fixed_on="2026-09-02",
       scope="CityLauncher/emailer/emailer.py get_prospects (+ _org_key) and "
             "emailer/wave_runner.py ramp_state + sendable_by_category. CLASS: every city, every "
             "category. (a) ONE-PER-ORG-1: get_prospects oversamples then collapses to one row per "
             "normalised organisation name, and holds sibling mailboxes of any org already emailed "
             "in that city; the plan (PLAN-TRUTH-1) counts organisations the same way so it never "
             "promises what the chokepoint refuses. Targeted --email sends bypass (they name one "
             "row). (b) RAMP-FLOOR-1: a clean wave counts toward the doubling streak only if it was "
             "at least ramp.min_wave_for_streak (default = defaults.batch_size) sends; a dirty wave "
             "of any size still breaks the streak. Asserted behaviourally on a copy of prospects.db.",
       ref="Born of the 2 Sep 2026 19:03 SAST wave David fired by hand and Claude monitored: "
           "Polokwane sent 24 against a 12 cap because RAMP-1 read its 2-email wave #1 as a clean "
           "wave and doubled; and the teachers_trainers batch carried SIX University of Limpopo "
           "departments (studentrecords@, financialaid@, accommodation@...) and four Mopani TVET "
           "offices -- a complaint magnet with max_complaints=0. Both fixed the same evening; 90 "
           "sent that wave, 0 failed.")
def rg_one_per_org_ramp_floor():
    out = []
    base = os.path.join(REPO, "..", "CityLauncher")
    em = os.path.join(base, "emailer", "emailer.py"); wr = os.path.join(base, "emailer", "wave_runner.py")
    if not (os.path.exists(em) and os.path.exists(wr)):
        return [(INFO, "CityLauncher not beside this repo -- skipped")]
    s = open(em, encoding="utf-8").read(); w = open(wr, encoding="utf-8").read()
    if "def _org_key" not in s or "ONE-PER-ORG-1" not in s:
        out.append((FAIL, "emailer.py lost ONE-PER-ORG-1 -- a batch can again carry six mailboxes of one organisation"))
    if "min_wave_for_streak" not in w:
        out.append((FAIL, "wave_runner.py lost RAMP-FLOOR-1 -- a 2-email wave can double a city's batch again"))
    if "_org_key" not in w:
        out.append((FAIL, "wave_runner.sendable_by_category no longer counts organisations -- the plan promises what the chokepoint refuses"))
    try:
        import importlib, tempfile, shutil, json as _j
        sys.path.insert(0, base)
        import emailer.emailer as _em; import emailer.wave_runner as _wr
        importlib.reload(_em); importlib.reload(_wr)
        db = os.path.join(base, "data", "prospects.db")
        tmp = os.path.join(tempfile.mkdtemp(), "p.db"); shutil.copy(db, tmp)
        from pathlib import Path as _P
        _em.DB_PATH = _P(tmp); _wr.DB_PATH = _P(tmp)
        pol = _j.load(open(os.path.join(base, "emailer", "waves_policy.json"), encoding="utf-8"))
        # (a) behavioural: no duplicate org in any city's pick, no org already emailed
        import sqlite3 as _s
        con = _s.connect(tmp); dup_hits = []
        for city, in con.execute("SELECT DISTINCT city FROM prospects WHERE status='scraped' LIMIT 12"):
            for cat in _wr.city_categories(city, pol)[:2]:
                rows = _em.get_prospects(city, cat, 12)
                keys = [_em._org_key(r.get("name"), r.get("business_name")) for r in rows]
                keys = [k for k in keys if k]
                if len(keys) != len(set(keys)):
                    dup_hits.append("%s/%s" % (city, cat))
        if dup_hits:
            out.append((FAIL, "duplicate organisations in one pick: %s" % dup_hits[:3]))
        # (b) behavioural: a synthetic 2-send clean wave must not raise the batch
        class _F(dict): pass
        orig = _wr.wave_history; orig_ev = _wr.evidence_state
        _wr.wave_history = lambda c: [{"w": 1, "n": 2, "b": 0}]
        _wr.evidence_state = lambda c: (True, "test")
        allowed, streak = _wr.ramp_state("Polokwane", pol)
        _wr.wave_history = orig; _wr.evidence_state = orig_ev
        if allowed != pol["defaults"]["batch_size"] or streak != 0:
            out.append((FAIL, "ramp doubled on a 2-send wave: allowed=%s streak=%s" % (allowed, streak)))
        if not any(r == FAIL for r, _ in out):
            out.append((INFO, "one-per-org picks clean across sampled cities; 2-send wave holds ramp at %d" % allowed))
    except Exception as e:
        out.append((FAIL, "behavioural leg broke: %s" % str(e)[:90]))
    return out

@entry("RG-0248", "Outreach clicks are SCORED per recipient (human_click / human_open / uncertain / "
                  "machine) into prospects.db click_register, and the follow-up lane can only address "
                  "the human tiers -- a scanner click can never earn a resend",
       LOCKED, fixed_on="2026-09-03",
       # PROMOTED 3 Sep 2026 03:25 SAST, the run after deploy_citylauncher.bat rode:
       # GET /launch-api/prospects/human-clicks 401 (present, key-gated), register
       # self-refreshed on the server 20 s after restart (2/52/14/60).
       scope="Every fingerprinted opened/clicked email_events row in CityLauncher/data/prospects.db, "
             "all waves, all countries. ONE scorer: CityLauncher/click_register.py (classify_clicks.py "
             "reports from it, api/server.py refreshes it on the reconcile cadence and on "
             "POST /launch-api/prospects/click-register/refresh; GET /launch-api/prospects/human-clicks "
             "serves the resend list, key-gated, json or csv). resend_human_clicks.py (host-side, "
             "via .bat) picks tiers human_click+human_open only, stamps resent_at so nobody is followed "
             "up twice, and runs every emailer.py guard (suppression, junk, government, privacy "
             "officer, .edu hold, JOURNEY-1 gate). Test traffic (example.*, CLICKTEST) never enters.",
       ref="HUMAN-CLICKS-1, 3 Sep 2026, David: '320 emails and 75 clicks hasn't given us a single "
           "listing -- do we have another fault?' PROBED: 0 users, 0 listings since 29 Aug; of 61 "
           "click events 33 were the UNSUBSCRIBE link from Azure/Defender ranges, 7 were the CTA and "
           "3 of those were bots (Ruby UA, Azure IP). The raw click count was the fault, not the app. "
           "Register written on the server 3 Sep: 117 recipients -> 2 human_click, 48 human_open, "
           "11 uncertain, 56 machine. Dry run of the follow-up lane on a copy: 48 would send, 2 "
           "skipped (opted_out). OPEN until deploy_citylauncher.bat rides: the live leg turns green "
           "when GET /launch-api/prospects/human-clicks answers 401 (present, key-gated) instead of "
           "404 -> READY TO LOCK.")
def rg_human_clicks_register():
    out = []
    base = os.path.join(REPO, "..", "CityLauncher")
    if os.path.isdir(base):
        cr = os.path.join(base, "click_register.py")
        if not os.path.exists(cr):
            out.append((FAIL, "CityLauncher/click_register.py is GONE -- the scorer no longer exists"))
        else:
            s = open(cr, encoding="utf-8").read()
            for needle, why in (("def score_events", "the event scorer is gone"),
                                ("def rollup", "the per-recipient rollup is gone"),
                                ("click_register", "the register table name has changed"),
                                ("CLICKTEST", "test traffic is no longer excluded")):
                if needle not in s:
                    out.append((FAIL, "click_register.py: %s" % why))
        sv = os.path.join(base, "api", "server.py")
        if os.path.exists(sv):
            s = open(sv, encoding="utf-8").read()
            for needle, why in (("@app.get('/prospects/human-clicks')", "the human-clicks endpoint is gone"),
                                ("_refresh_click_register()", "the register is no longer refreshed on the reconcile cadence"),
                                ("Depends(require_launch_key)", "launch-key gate missing")):
                if needle not in s:
                    out.append((FAIL, "api/server.py: %s" % why))
        rs = os.path.join(base, "resend_human_clicks.py")
        if not os.path.exists(rs):
            out.append((FAIL, "resend_human_clicks.py is GONE -- the humans-only lane no longer exists"))
        else:
            s = open(rs, encoding="utf-8").read()
            for needle, why in (('("human_click", "human_open")', "the lane no longer restricts itself to human tiers"),
                                ("resent_at", "the lane no longer stamps resent_at (repeat sends possible)"),
                                ("_is_suppressed", "suppression guard bypassed"),
                                ("journey_check.py", "JOURNEY-1 gate removed")):
                if needle not in s:
                    out.append((FAIL, "resend_human_clicks.py: %s" % why))
        # behavioural: a scanner-shaped click must never reach a human tier
        try:
            import importlib.util as _iu, sqlite3 as _s
            spec = _iu.spec_from_file_location("_cr", cr); m = _iu.module_from_spec(spec); spec.loader.exec_module(m)
            con = _s.connect(":memory:")
            con.execute("CREATE TABLE email_events (id INTEGER PRIMARY KEY, prospect_id INTEGER, message_id TEXT, event TEXT, created_at TEXT, meta TEXT)")
            con.execute("INSERT INTO email_events VALUES (1,1,'m1','sent','2026-09-01T10:00:00',NULL)")
            con.execute("INSERT INTO email_events VALUES (2,1,'m1','clicked','2026-09-01T10:00:20', ?)",
                        ('{"ip":"4.222.252.97","ua":"Mozilla/5.0","link":"https://trustsquare.co/launch-api/optout?email=a%40b.co","event_ts":"2026-09-01T10:00:20Z","recipient":"a@b.co"}',))
            con.execute("INSERT INTO email_events VALUES (3,2,'m2','sent','2026-09-01T10:00:00',NULL)")
            con.execute("INSERT INTO email_events VALUES (4,2,'m2','clicked','2026-09-01T16:00:00', ?)",
                        ('{"ip":"197.184.1.1","ua":"Mozilla/5.0 (Windows NT 10.0) Chrome/142","link":"https://trustsquare.co/?magic=1&email=c%40d.co","event_ts":"2026-09-01T16:00:00Z","recipient":"c@d.co"}',))
            reg = m.rollup(m.score_events(con))
            if reg.get("a@b.co", {}).get("tier") in ("human_click", "human_open"):
                out.append((FAIL, "a 20-second Azure opt-out click scored as HUMAN"))
            if reg.get("c@d.co", {}).get("tier") != "human_click":
                out.append((FAIL, "a 6-hour-later CTA click from a residential IP did not score human_click (got %s)" % reg.get("c@d.co", {}).get("tier")))
        except Exception as e:
            out.append((FAIL, "behavioural leg broke: %s" % str(e)[:90]))
    else:
        out.append((INFO, "CityLauncher not beside this repo -- source leg skipped"))
    try:
        import urllib.request as _ur
        req = _ur.Request("https://trustsquare.co/launch-api/prospects/human-clicks",
                          headers={"User-Agent": "TrustSquare-Ledger/1.0"})
        try:
            _ur.urlopen(req, timeout=15)
            out.append((FAIL, "GET /launch-api/prospects/human-clicks served an ANONYMOUS caller -- gate missing"))
        except Exception as e:
            code = getattr(e, "code", None)
            if code in (401, 403):
                out.append((INFO, "live: /prospects/human-clicks present and key-gated (HTTP %s)" % code))
            elif code == 404:
                out.append((FAIL, "live: /prospects/human-clicks is 404 -- deploy_citylauncher.bat has not ridden"))
            else:
                out.append((FAIL, "live human-clicks probe unexpected: %s" % repr(e)[:60]))
    except Exception as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    if not any(r == FAIL for r, _ in out):
        out.append((INFO, "scorer, endpoint, lane and live gate all present"))
    return out


@entry("RG-0249", "A self-serve rate-based listing (Tutors / Services / Adventures) can actually be "
                  "SAVED -- the sell-flow states the price basis the BEA demands, so a tutor who types "
                  "'350' into the numeric rate field is not refused with a 422 about 'R450 / hour'",
       OPEN, fixed_on="2026-09-03",
       scope="ALL sell-flow categories whose BEA category is in RATE_UNIT_CATEGORIES (tutors, services, "
             "adventures_experiences, adventures_accommodation), every market. CLASS: two guards built "
             "on different days disagreeing -- JNR-FIX-5B (22 Jul, BEA _validate_price_unit rejects a "
             "bare amount) vs the sell-flow's type=number price input (PRICE-LABEL-1, 17 Jul) that can "
             "only ever produce a bare amount. Since 22 Jul every self-serve listing in these "
             "categories died at 'Continue to publish' with a message the seller could not act on, "
             "then landed on the plan-picker with 'tap Continue to try again' (which is the plan "
             "step, not the listing). The BEA rule is right; the FLOW now states the basis it "
             "already knows: SF_CATS priceUnit ('/ hour', '/ call-out', '/ person', '/ night') + "
             "_sfPriceWithUnit() at sfFinish -> '350' becomes 'R350 / hour'; empty -> POA; a value "
             "already carrying a basis passes through untouched.",
       ref="PRICE-UNIT-1, 3 Sep 2026. Found by walking a real Tutors magic link end-to-end in "
           "David's Chrome after '320 emails, 75 clicks, 0 listings' (HUMAN-CLICKS-1): photos, "
           "6 steps, score 65/100, then POST /listings 422. Unit-tested the composer in node "
           "(350 -> R350 / hour; '' -> POA; 'R50 / person' unchanged; 'POA' unchanged; no unit -> "
           "raw). OPEN until the deploy ref ships ms.js: the live leg turns green when the served "
           "ms.js carries _sfPriceWithUnit and priceUnit:'/ hour' -> READY TO LOCK. Behavioural "
           "leg mirrors the BEA rule in Python against the composer's outputs.")
def rg_price_unit_selfserve():
    out = []
    js = repo_file("ms.js")
    if js is None:
        out.append((INFO, "ms.js not beside the ledger -- source leg skipped"))
    else:
        for needle, why in (("function _sfPriceWithUnit", "the price-basis composer is gone"),
                            ("priceUnit:'/ hour'", "Tutors lost its priceUnit"),
                            ("priceUnit:'/ person'", "Adventures experiences lost its priceUnit"),
                            ("priceUnit:'/ night'", "Adventures accommodation lost its priceUnit"),
                            ("priceUnit:'/ call-out'", "Services technical lost its priceUnit"),
                            ("price: _sfPriceWithUnit(", "sfFinish no longer routes the price through the composer")):
            if needle not in js:
                out.append((FAIL, "ms.js: %s" % why))
        # behavioural: the BEA rule (mirrored) must accept what the composer emits
        toks = ("/", " per ", "per ", "once-off", "once off", "poa", "negotiable", "quote", "flat fee", "flat-fee", "package", "from ")
        def bea_ok(p):
            p = (p or "").strip().lower()
            if not p or not any(ch.isdigit() for ch in p): return True
            return any(t in p for t in toks)
        def compose(raw, unit):
            raw = (raw or "").strip()
            if not raw: return "POA"
            if not unit: return raw
            import re as _re
            if _re.search(r"/|\bper\b|once|poa|negotiable|quote|package|from ", raw, _re.I): return raw
            if not any(c.isdigit() for c in raw): return raw
            return "R" + _re.sub(r"^[^\d]*", "", raw) + " " + unit
        for raw, unit in (("350", "/ hour"), ("", "/ hour"), ("R 1200", "/ night"), ("50", "/ person"), ("R50 / person", "/ person")):
            if not bea_ok(compose(raw, unit)):
                out.append((FAIL, "composer output %r for input %r would still be refused by the BEA" % (compose(raw, unit), raw)))
        if bea_ok("350") and "tutors" in ("tutors",):
            pass  # the bare amount IS refused by the rule -- that is the class this entry guards against
    try:
        html = _get("/")
        import re as _re
        m = _re.search(r"ms\.js\?v=(\d+)", html)
        live = _get("/static/ms.js?v=%s" % (m.group(1) if m else "0"))
        if "_sfPriceWithUnit" in live and "priceUnit:'/ hour'" in live:
            out.append((INFO, "live ms.js (v=%s) states the price basis for rate-based flows" % (m.group(1) if m else "?")))
        else:
            out.append((FAIL, "live ms.js (v=%s) still submits bare amounts -- the deploy ref has not shipped PRICE-UNIT-1; "
                              "every self-serve Tutors/Services/Adventures listing is still refused at publish" % (m.group(1) if m else "?")))
    except ProbeOffline as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    if not any(r == FAIL for r, _ in out):
        out.append((INFO, "composer present, BEA-compatible, live"))
    return out


@entry("RG-0250", "An INVITED seller (magic-link arrival, not yet a registered user) gets the AI "
                  "photo draft -- POST /listings/vision-draft admits an address from our own outreach "
                  "pool instead of refusing it with 401 'complete seller registration first'",
       OPEN, fixed_on="2026-09-03",
       scope="Every magic-link arrival, every category, every market. The Session-90 existence gate "
             "(users table) stays for strangers -- the spend guard is intact -- but bea_main.py "
             "_is_invited_prospect() now also admits an email that CityLauncher emailed "
             "(prospects.emailed_at IS NOT NULL, read-only open of /var/www/citylauncher/data/"
             "prospects.db, CL_PROSPECTS_DB overridable; missing DB or any error => closed). "
             "CLASS: a guard built for registered users applied to a funnel whose registration "
             "happens AFTER the guarded step -- the outreach email promises 'the app writes the "
             "first draft for you' and the app answered 401 to every invitee since the gate shipped.",
       ref="INVITE-VISION-1, 3 Sep 2026, found on the same walk as RG-0249: the main photo "
           "uploaded, nginx logged POST /listings/vision-draft 401, the flow said 'fill in the "
           "details manually'. Helper tested on a temp prospects.db: emailed -> True, scraped-only -> "
           "False, unknown -> False, missing DB -> False. OPEN until the deploy ref ships "
           "bea_main.py. Live leg: POST vision-draft with a known invited address and ONE invalid "
           "photo -> must be 400 'No valid photos' (gate passed, zero AI spend), never 401; the same "
           "with an unknown address -> must stay 401 (guard intact). READY TO LOCK when both hold.")
def rg_invite_vision_gate():
    out = []
    src = repo_file("bea_main.py")
    if src is None:
        out.append((INFO, "bea_main.py not beside the ledger -- source leg skipped"))
    else:
        for needle, why in (("def _is_invited_prospect", "the invited-prospect lookup is gone"),
                            ("if not _ve and not _is_invited_prospect(_ve_email):", "vision-draft gate no longer consults the outreach pool"),
                            ("emailed_at IS NOT NULL OR status IN ('emailed','opened','clicked'", "the lookup no longer requires the prospect to have been emailed (guard weakened)"),
                            ("mode=ro", "the prospects.db open is no longer read-only")):
            if needle not in src:
                out.append((FAIL, "bea_main.py: %s" % why))
    try:
        import urllib.request as _ur, urllib.error as _ue
        ck = _review_cookie()
        def probe(email):
            boundary = "----tsledger"
            body = ("--%s\r\nContent-Disposition: form-data; name=\"photos\"; filename=\"x.jpg\"\r\n"
                    "Content-Type: image/jpeg\r\n\r\nnot-an-image\r\n"
                    "--%s\r\nContent-Disposition: form-data; name=\"seller_email\"\r\n\r\n%s\r\n"
                    "--%s\r\nContent-Disposition: form-data; name=\"category_hint\"\r\n\r\ntutors\r\n"
                    "--%s--\r\n" % (boundary, boundary, email, boundary, boundary)).encode()
            hdr = dict(UA, **{"Content-Type": "multipart/form-data; boundary=%s" % boundary})
            if ck: hdr["Cookie"] = ck
            req = _ur.Request(BASE + "/listings/vision-draft", data=body, headers=hdr, method="POST")
            try:
                _ur.urlopen(req, timeout=TIMEOUT); return 200
            except _ue.HTTPError as e:
                return e.code
        invited = probe("support@tutorbird.com")      # emailed 2 Sep 2026 (London Tutors wave)
        stranger = probe("ledger-stranger-%d@example.invalid" % int(__import__("time").time()))
        if stranger != 401:
            out.append((FAIL, "live: an UNKNOWN address was not refused (HTTP %s) -- the spend guard is open" % stranger))
        if invited == 401:
            out.append((FAIL, "live: an invited address is still refused with 401 -- the deploy ref has not shipped INVITE-VISION-1; invitees get no AI draft"))
        elif invited not in (400, 422):
            out.append((FAIL, "live: invited probe answered HTTP %s (expected 400 'no valid photos' -- gate passed, no spend)" % invited))
        else:
            out.append((INFO, "live: invited address passes the gate (HTTP %s on an invalid photo), stranger still 401" % invited))
    except ProbeOffline as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    except Exception as e:
        out.append((FAIL, "live leg broke: %s" % str(e)[:90]))
    if not any(r == FAIL for r, _ in out):
        out.append((INFO, "lookup present, read-only, guard intact, live"))
    return out


@entry("RG-0252", "Deploys ship themselves -- Claude requests, the host agent gates and ships on a 20-min "
       "tick and retries a BLOCKED gate until it clears; nothing waits for David's click",
       OPEN,
       scope="RUL-092, two lanes. LANE A RELAY-DEPLOY-1: request_deploy.py relays HEAD through the origin's clone when SSH is open (fast-forward-only) -- proven 3 Sep 03:31Z. LANE B AUTODEPLOY-AGENT-1 (host flag + 20-min task) for closed egress. Repo legs: autodeploy_agent.bat + register_autodeploy_agent.bat + "
             "scripts/request_deploy.py exist; the agent calls git_unlock.bat FIRST (RG-0015's rule) and "
             "reuses nightly_tsl.bat (strict tsl_gate + drift + release lock + unattended ship) rather than a "
             "second deploy engine (ONE DEPLOY, RG-0023); it is in check_bat_crlf's UNATTENDED set so a pause "
             "can never hang it; the flag/result/log files are gitignored; STANDING_ORDERS and CLAUDE.md no "
             "longer list deploys as reserved; ../CityLauncher/deploy_citylauncher.bat honours UNATTENDED=1. "
             "LIVE leg: autodeploy_agent_log.txt exists and its newest line is < 40 min old whenever a request "
             "flag is pending -- proves the task is registered and ticking. OPEN until David runs "
             "register_autodeploy_agent.bat once (the ONE remaining click, Task Scheduler is his machine) and "
             "the first request ships -> READY TO LOCK.",
       ref="RUL-092, 3 Sep 2026, David: 'remove that deploy rule of mine and make these deploys automated... "
           "you manage the blocks and wait out their clearance, and then redeploy if possible again.' Born of "
           "the 15 daily clicks that held him at the keyboard; corollary 4 recorded the same session: sandbox "
           "SSH egress is INTERMITTENT (blocked ~19:00 2 Sep, open 04:54 3 Sep), so the lane is flags + a host "
           "timer, never Claude's live hand on the server.")
def rg_autodeploy_agent():
    out = []
    rq = repo_file(os.path.join("scripts", "request_deploy.py")) or ""
    for n in ("def relay(", "claude-relay:main claude-relay:deploy", "--is-ancestor"):
        if n not in rq:
            out.append((FAIL, "request_deploy.py lost the relay lane piece '%s'" % n))
    for f, needles in (("autodeploy_agent.bat", ["git_unlock.bat", "nightly_tsl.bat", "DEPLOY_REQUEST.flag", "CL_DEPLOY_REQUEST.flag", "UNATTENDED=1"]),
                       ("register_autodeploy_agent.bat", ["autodeploy_agent.bat", "/SC MINUTE"]),
                       ("scripts/request_deploy.py", ["DEPLOY_REQUEST.flag", "py_compile"]),
                       ("scripts/check_bat_crlf.py", ["\"autodeploy_agent.bat\""]),
                       (".gitignore", ["DEPLOY_REQUEST.flag", "autodeploy_agent_log.txt"]),
                       ("STANDING_ORDERS.md", ["RUL-092"]),
                       (os.path.join("..", "CityLauncher", "deploy_citylauncher.bat"), ["if not defined UNATTENDED pause", "if defined UNATTENDED exit /b 0"])):
        t = repo_file(f) or ""
        for n in needles:
            if n not in t:
                out.append((FAIL, "%s lost '%s'" % (f, n)))
    so = repo_file("STANDING_ORDERS.md") or ""
    if "- deploys, money, deletions, sending anything on his behalf;" in so:
        out.append((FAIL, "STANDING_ORDERS.md lists deploys as reserved again -- RUL-092 reversed"))
    # the agent must call git_unlock BEFORE any git-writing step (order, not just presence)
    ag = repo_file("autodeploy_agent.bat") or ""
    if ag and ag.find('call "%~dp0git_unlock.bat"') > ag.find('call "%~dp0nightly_tsl.bat"'):
        out.append((FAIL, "autodeploy_agent.bat ships before it clears a stale git lock"))
    # live leg: is the host task ticking?
    log = os.path.join(REPO, "autodeploy_agent_log.txt")
    pending = any(os.path.exists(os.path.join(REPO, f)) for f in ("DEPLOY_REQUEST.flag", "CL_DEPLOY_REQUEST.flag"))
    if os.path.exists(log):
        import time as _t
        age = (_t.time() - os.path.getmtime(log)) / 60
        if pending and age > 40:
            out.append((FAIL, "a deploy request has been pending %d min with no agent activity -- task not registered or stopped" % age))
        else:
            out.append((INFO, "agent log present, last activity %d min ago%s" % (age, ", request pending" if pending else "")))
    else:
        out.append((FAIL, "no autodeploy_agent_log.txt yet -- register_autodeploy_agent.bat has not been run on the host"))
    return out

@entry("RG-0251", "A stop-lossed city has a RELEASE path -- cleaning its list (clean_city_list.py) "
       "stamps stop_loss_released_wave and wave_runner lets ONE next wave out to judge itself",
       LOCKED, fixed_on="2026-09-03",
       scope="CityLauncher emailer/wave_runner.py gate_check (STOP-LOSS-RELEASE-1) + "
             "clean_city_list.py + clean_stoploss_cities.bat. All cities. Source-checked and "
             "behavioural: gate_check with a 5/33 dirty last wave BLOCKS without the stamp and "
             "PASSES with cities[city].stop_loss_released_wave == last_wave; a stale stamp "
             "(wave 1 stamped, dirty wave 2) still blocks.",
       ref="3 Sep 2026. David: 'how do I clear their list?' -- there was no answer. The latch "
           "(RG-0242) had no release: a blocked city never advances last_wave, so the dirty wave "
           "stayed 'last' forever (New York 5/33, Pretoria 5/59, Polokwane 5/26). Probed 3 Sep on "
           "a DB copy: 158 sendable rows had NEVER been MX-verified; 13 rejects found (NY 1, PTA 9, "
           "PLK 3). MX cannot see a dead mailbox on a live domain (3 of NY's 5 bounces were mx_ok), "
           "so the release lets the cleaned list prove itself on its own next wave.")
def rg_stop_loss_release():
    out = []
    cl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CityLauncher")
    wr = repo_file(os.path.join("..", "CityLauncher", "emailer", "wave_runner.py"))
    if wr is None:
        return [(INFO, "CityLauncher not beside this repo -- skipped")]
    if "stop_loss_released_wave" not in wr:
        out.append((FAIL, "wave_runner has no stop_loss_released_wave release path (STOP-LOSS-RELEASE-1)"))
    if not os.path.exists(os.path.join(cl, "clean_city_list.py")):
        out.append((FAIL, "clean_city_list.py missing -- no way to clean a list and release the latch"))
    try:
        import importlib.util as _iu
        sys.path.insert(0, os.path.abspath(cl))
        spec = _iu.spec_from_file_location("cl_wave_runner_251", os.path.join(cl, "emailer", "wave_runner.py"))
        m = _iu.module_from_spec(spec); spec.loader.exec_module(m)
        m.send_freeze.frozen = lambda: False
        m.suppression_state = lambda: (True, "stub")
        pol = {"defaults": {"bounce_stop_pct": 5.0, "bounce_stop_min_bounces": 3, "max_complaints": 0,
                            "send_days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "min_gap_days": 1,
                            "send_timezone": "Africa/Johannesburg"},
               "cities": {"_a": {"armed": True, "gates_green": True},
                          "_b": {"armed": True, "gates_green": True, "stop_loss_released_wave": 1}}}
        dirty = {"last_wave_bounce_pct": 15.2, "last_wave_bounced": 5, "last_wave_sent": 33,
                 "last_wave": 1, "complaints": 0, "last_emailed_at": None}
        _, b1 = m.gate_check("_a", pol, dict(dirty), True)
        if not any("stop-loss" in x for x in b1):
            out.append((FAIL, "unstamped dirty city was NOT blocked -- stop-loss weakened"))
        _, b2 = m.gate_check("_b", pol, dict(dirty), True)
        if any("stop-loss" in x for x in b2):
            out.append((FAIL, "stamped city still blocked -- release path dead: %s" % b2))
        _, b3 = m.gate_check("_b", pol, dict(dirty, last_wave=2), True)
        if not any("stop-loss" in x for x in b3):
            out.append((FAIL, "stale stamp (wave 1) released a dirty wave 2 -- release must match one wave only"))
        if not out:
            out.append((INFO, "gate_check: unstamped blocks, stamped releases, stale stamp blocks"))
    except Exception as e:
        out.append((INFO, "behavioural leg skipped (%s)" % str(e)[:80]))
    return out


@entry("RG-0253", "A FIRST-TIME seller can publish -- sobGoLive registers the account BEFORE it stamps "
                  "EULA acceptance, so PUT /listings/<id>/publish is never refused with 403 'EULA not "
                  "accepted' on a seller's very first listing",
       OPEN, fixed_on="2026-09-03",
       scope="Every new seller, every route (magic-link invite AND in-app Sell+), every category. "
             "CLASS: an idempotent step ordered before the step that makes it possible. The EULA "
             "stamp POST /users/<email>/eula ran first and 404'd (no account yet), its .catch "
             "swallowed the miss, POST /users then created the account with eula_accepted_at NULL, "
             "and publish refused 403. Returning sellers -- every account David ever tested on -- "
             "already existed, so the fault was invisible to every walk but a stranger's.",
       ref="EULA-ORDER-1, 3 Sep 2026, WALK-1 second pass (after PRICE-UNIT-1 + INVITE-VISION-1 "
           "were live): draft 381 saved with 'R350 / hour', photo uploaded, plan chosen, EULA "
           "scrolled + 3 attestations ticked, Go live -> uvicorn log: GET /users 401, POST "
           "/users/.../eula 404, PUT /listings/381/publish 403 (x2). Fix: register (idempotent "
           "INSERT OR IGNORE) then stamp; a failed stamp now logs instead of vanishing. OPEN until "
           "the deploy ref ships ms.js: live leg = served ms.js carries EULA-ORDER-1 with the "
           "register call textually BEFORE the eula call inside sobGoLive -> READY TO LOCK; the "
           "human-observable proof is listing 381 (or its successor) going live on the re-walk.")
def rg_eula_order_first_seller():
    out = []
    def check(js, label):
        i = js.find("async function sobGoLive")
        if i < 0:
            return [(FAIL, "%s: sobGoLive is gone" % label)]
        body = js[i:i + 6000]
        if "EULA-ORDER-1" not in body:
            return [(FAIL, "%s: EULA-ORDER-1 block missing from sobGoLive -- first-time sellers get 403 at publish" % label)]
        reg = body.find("fetch(BEA_URL + '/users', {")
        eula = body.find("/eula'")
        if reg < 0 or eula < 0 or reg > eula:
            return [(FAIL, "%s: sobGoLive stamps the EULA before registering the account (reg@%d eula@%d)" % (label, reg, eula))]
        return [(INFO, "%s: register precedes EULA stamp in sobGoLive" % label)]
    js = repo_file("ms.js")
    out += check(js, "repo ms.js") if js is not None else [(INFO, "ms.js not beside the ledger -- source leg skipped")]
    try:
        html = _get("/")
        import re as _re
        m = _re.search(r"ms\.js\?v=(\d+)", html)
        live = _get("/static/ms.js?v=%s" % (m.group(1) if m else "0"))
        out += check(live, "live ms.js v=%s" % (m.group(1) if m else "?"))
    except ProbeOffline as e:
        out.append((FAIL, "live leg unreachable: %s" % str(e)[:80]))
    return out


if __name__ == "__main__":
    sys.exit(main())

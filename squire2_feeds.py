"""
squire2_feeds.py -- SQUIRE-2 Phase 1 free data feeds (SQUIRE_2_BUILD_BRIEF.md s2; built 10 Oct 2026)
=====================================================================================================
Every function here FAILS SAFE: on any problem it returns None (or an empty result) and the caller
reports "not available" -- it never guesses a number. Every feed is free (no per-request cost);
each is also gated by its provider flag in feature_flags (a provider set false is never called).

  mtgjson       daily price file -> card_price_history (nightly; NO per-request calls)
  epc_register  UK energy certificate (free registration key; env EPC_API_KEY, never echoed)
  police_uk     street-level crime count (keyless)
  ea_flood      Environment Agency flood areas (keyless)
  boe_rate      Bank of England Bank Rate (published series IUDBEDR)
  sarb_rate     SARB policy (repo) rate (published)

Prices from MTGJSON are by FINISH (normal/foil), never by condition -- the condition-specific
Near Mint price comes from the existing JustTCG lane (tier_resolvers.justtcg_price).
"""
from __future__ import annotations

import gzip
import io
import json
import os
from datetime import date, timedelta
from typing import Iterable, Optional

import feature_flags

UA = {"User-Agent": "TrustSquare/1.0 (+https://trustsquare.co)", "Accept": "application/json"}
MTGJSON_BASE = os.environ.get("MTGJSON_BASE", "https://mtgjson.com/api/v5")
HISTORY_DAYS = 90                      # s2: "keep 90 days rolling"
_PROVIDERS = ("tcgplayer", "cardkingdom", "cardmarket", "manapool")


def _live(name: str) -> bool:
    try:
        return feature_flags.is_provider_live(name)
    except Exception:
        return False


# ── MTGJSON ───────────────────────────────────────────────────────────────────
def mtgjson_set_map(set_code: str, *, fetch=None, timeout: float = 30.0) -> dict:
    """{scryfall_id: mtgjson_uuid} for one set, from the set's own small file (~1-2 MB)."""
    if not set_code or not _live("mtgjson"):
        return {}
    try:
        raw = fetch("%s/%s.json.gz" % (MTGJSON_BASE, set_code.upper())) if fetch else _get_bytes(
            "%s/%s.json.gz" % (MTGJSON_BASE, set_code.upper()), timeout)
        if not raw:
            return {}
        d = json.loads(gzip.decompress(raw)) if raw[:2] == b"\x1f\x8b" else json.loads(raw)
        out = {}
        for c in (d.get("data") or {}).get("cards") or []:
            sid = (c.get("identifiers") or {}).get("scryfallId")
            if sid and c.get("uuid"):
                out[sid] = c["uuid"]
        return out
    except Exception:
        return {}


def mtgjson_rows_for(uuids: Iterable[str], raw_today: bytes) -> list[tuple]:
    """Pull ONLY the wanted cards out of the daily AllPricesToday file without loading the whole tree
    (the file is ~50 MB of text; a full json.load needs ~500 MB). Returns
    (uuid, provider, finish, date, price, currency) rows for PAPER RETAIL prices."""
    want = {u for u in uuids if u}
    if not want or not raw_today:
        return []
    text = (gzip.decompress(raw_today) if raw_today[:2] == b"\x1f\x8b" else raw_today).decode("utf-8", "replace")
    dec = json.JSONDecoder()
    rows = []
    for u in want:
        i = text.find('"%s"' % u)
        if i < 0:
            continue
        j = text.find(":", i + len(u) + 2)
        if j < 0:
            continue
        j += 1
        while j < len(text) and text[j] in " \r\n\t":
            j += 1
        try:
            obj, _ = dec.raw_decode(text, j)
        except ValueError:
            continue
        paper = (obj or {}).get("paper") or {}
        for prov in _PROVIDERS:
            p = paper.get(prov) or {}
            cur = p.get("currency") or "USD"
            for finish, series in (p.get("retail") or {}).items():
                for d, price in (series or {}).items():
                    try:
                        v = float(price)
                    except (TypeError, ValueError):
                        continue
                    if v > 0:
                        rows.append((u, prov, finish, str(d)[:10], v, cur))
    return rows


def store_history(conn, rows: list[tuple], *, keep_days: int = HISTORY_DAYS, today: Optional[date] = None) -> int:
    """Insert-or-replace the day's rows and trim to a rolling window. Standard SQL only."""
    n = 0
    for r in rows:
        conn.execute("INSERT INTO card_price_history (uuid, provider, finish, date, price, currency) VALUES (?,?,?,?,?,?) "
                     "ON CONFLICT(uuid, provider, finish, date) DO UPDATE SET price=excluded.price, currency=excluded.currency", r)
        n += 1
    cutoff = ((today or date.today()) - timedelta(days=keep_days)).isoformat()
    conn.execute("DELETE FROM card_price_history WHERE date < ?", (cutoff,))
    return n


def history_for(conn, uuid: str, finish: str = "normal", provider: str = "tcgplayer") -> list[tuple]:
    """(date, price) rows for one card, USD provider first (tcgplayer), falling back to any USD provider."""
    if not uuid:
        return []
    rows = conn.execute("SELECT date, price FROM card_price_history WHERE uuid=? AND finish=? AND provider=? ORDER BY date",
                        (uuid, finish, provider)).fetchall()
    if not rows:
        rows = conn.execute("SELECT date, AVG(price) AS price FROM card_price_history WHERE uuid=? AND finish=? AND currency='USD' "
                            "GROUP BY date ORDER BY date", (uuid, finish)).fetchall()
    return [(r[0], r[1]) for r in rows]


def _get_bytes(url: str, timeout: float = 60.0) -> Optional[bytes]:
    try:
        import httpx
        r = httpx.get(url, headers=UA, timeout=timeout, follow_redirects=True)
        return r.content if r.status_code == 200 else None
    except Exception:
        return None


def nightly_mtgjson(conn, *, fetch=None) -> dict:
    """The nightly job (RUL-070 server-side). Maps every active card line to its MTGJSON uuid (per-set
    files, cached in mtgjson_ids) and stores today's prices for those cards only."""
    if not _live("mtgjson"):
        return {"skipped": "mtgjson provider off"}
    get = fetch or _get_bytes
    lines = conn.execute("SELECT DISTINCT l.scryfall_id, l.set_code FROM squire_lines l JOIN squire_briefs b ON b.id=l.brief_id "
                         "WHERE b.status='active' AND l.scryfall_id IS NOT NULL").fetchall()
    known = {r[0]: r[1] for r in conn.execute("SELECT scryfall_id, uuid FROM mtgjson_ids").fetchall()}
    need_sets = {(r[1] or "").upper() for r in lines if r[0] not in known and r[1]}
    for sc in sorted(need_sets):
        m = mtgjson_set_map(sc, fetch=get)
        for sid, u in m.items():
            conn.execute("INSERT INTO mtgjson_ids (scryfall_id, uuid, set_code) VALUES (?,?,?) "
                         "ON CONFLICT(scryfall_id) DO UPDATE SET uuid=excluded.uuid, set_code=excluded.set_code", (sid, u, sc))
            known[sid] = u
    uuids = [known[r[0]] for r in lines if r[0] in known]
    if not uuids:
        conn.commit()
        return {"cards": 0, "rows": 0, "sets_fetched": len(need_sets)}
    raw = get("%s/AllPricesToday.json.gz" % MTGJSON_BASE)
    rows = mtgjson_rows_for(uuids, raw or b"")
    n = store_history(conn, rows)
    conn.commit()
    return {"cards": len(uuids), "rows": n, "sets_fetched": len(need_sets)}


# ── UK property context ───────────────────────────────────────────────────────
async def police_crime_count(lat: float, lng: float, *, timeout: float = 12.0) -> Optional[dict]:
    if lat is None or lng is None or not _live("police_uk"):
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers=UA) as c:
            r = await c.get("https://data.police.uk/api/crimes-street/all-crime", params={"lat": lat, "lng": lng})
            if r.status_code != 200:
                return None
            d = r.json()
        month = d[0].get("month") if d else None
        return {"count": len(d), "month": month, "provenance": "data.police.uk street-level crime, %s, ~1 mile" % (month or "latest month")}
    except Exception:
        return None


async def ea_flood_area(lat: float, lng: float, *, timeout: float = 12.0) -> Optional[dict]:
    if lat is None or lng is None or not _live("ea_flood"):
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers=UA) as c:
            r = await c.get("https://environment.data.gov.uk/flood-monitoring/id/floodAreas",
                            params={"lat": lat, "long": lng, "dist": 0.5})
            if r.status_code != 200:
                return None
            items = (r.json() or {}).get("items") or []
        label = items[0].get("label") if items else None
        return {"in_area": bool(items), "label": label, "provenance": "Environment Agency flood areas (within 500 m)"}
    except Exception:
        return None


async def epc_lookup(postcode: str, address_hint: str = "", *, timeout: float = 12.0) -> Optional[dict]:
    """UK energy certificate. Needs the free registration key in env EPC_API_KEY (and the account e-mail
    in EPC_API_EMAIL). With no key this returns None and the report says 'not available'. The key is
    sent only in the Authorization header and is never logged, returned or echoed."""
    key = os.environ.get("EPC_API_KEY") or ""
    if not postcode or not key or not _live("epc_register"):
        return None
    base = os.environ.get("EPC_API_BASE", "https://epc.opendatacommunities.org/api/v1/domestic/search")
    try:
        import base64
        import httpx
        tok = base64.b64encode(("%s:%s" % (os.environ.get("EPC_API_EMAIL", ""), key)).encode()).decode()
        async with httpx.AsyncClient(timeout=timeout, headers={**UA, "Authorization": "Basic " + tok}) as c:
            r = await c.get(base, params={"postcode": postcode, "size": 25})
            if r.status_code != 200:
                return None
            rows = (r.json() or {}).get("rows") or []
        if not rows:
            return None
        hint = (address_hint or "").lower()
        pick = next((x for x in rows if hint and hint in str(x.get("address", "")).lower()), rows[0])
        return {"rating": pick.get("current-energy-rating"), "floor_area": pick.get("total-floor-area"),
                "age_band": pick.get("construction-age-band"),
                "provenance": "UK EPC register, postcode %s%s" % (postcode, "" if hint else " (nearest certificate, not this exact address)")}
    except Exception:
        return None


# ── Rates ─────────────────────────────────────────────────────────────────────
async def boe_bank_rate(*, timeout: float = 12.0) -> Optional[dict]:
    if not _live("boe_rate"):
        return None
    try:
        import httpx
        frm = (date.today() - timedelta(days=60)).strftime("%d/%b/%Y")
        url = ("https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=%s"
               "&Dateto=now&SeriesCodes=IUDBEDR&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N" % frm)
        async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "Mozilla/5.0 TrustSquare/1.0"}) as c:
            r = await c.get(url)
            if r.status_code != 200:
                return None
        last = [ln for ln in r.text.strip().splitlines() if "," in ln][-1].split(",")
        return {"pct": float(last[1]), "date": last[0].strip(), "provenance": "Bank of England Bank Rate, %s" % last[0].strip()}
    except Exception:
        return None


async def sarb_repo_rate(*, timeout: float = 12.0) -> Optional[dict]:
    if not _live("sarb_rate"):
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers=UA) as c:
            r = await c.get("https://custom.resbank.co.za/SarbWebApi/WebIndicators/HomePageRates")
            if r.status_code != 200:
                return None
            d = r.json() or []
        for x in d:
            if "policy rate" in str(x.get("Name", "")).lower() or "repo" in str(x.get("Name", "")).lower():
                return {"pct": float(x["Value"]), "date": str(x.get("Date", ""))[:10],
                        "provenance": "SARB policy rate, %s" % str(x.get("Date", ""))[:10]}
        return None
    except Exception:
        return None

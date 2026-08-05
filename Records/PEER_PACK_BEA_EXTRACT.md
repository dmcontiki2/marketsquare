# PEER PACK — targeted evidence extract (v3)

*Generated 2026-08-05 18:04 UTC. Each line keeps its REAL line number in its source file so*
*citations are checkable. If a section you need is absent, name the exact file and*
*line range as a finding and it will be supplied next run.*

## COMPUTED TOTALITY EVIDENCE (Author-derived greps over the full bea_main.py — treat as claims; spot-check by requesting ranges)

- Vendor inference hosts named in bea_main.py (17348 lines): {'api.anthropic.com': 0, 'api.openai.com': 0, 'api.scaleway.ai': 0}
- Old vendor-specific gates ('if not ANTHROPIC_API_KEY') remaining: NONE
- Vendor-neutral gates ('if not ai_provider.any_lane_configured()'): 15 at lines [3411, 5335, 5455, 5531, 5607, 9297, 9518, 10115, 14223, 14311, 14895, 15207, 15430, 15689, 16575]
- Every line invoking ai_provider.complete: [13, 3441, 5354, 5489, 5558, 5856, 9349, 9544, 10131, 10160, 11799, 13864, 13869, 14269, 14372, 15060, 15344, 15500, 15722, 16632, 17342]
- Every _deduct_tuppence call line: [5891, 14291, 14398, 15086, 15368, 15534]

## Admin auth dependency (used by /admin/ai-* endpoints) — from bea_main.py

```
    43  MS_ADMIN_KEY = os.environ.get("MS_ADMIN_KEY", "")
    44  
    45  def _require_admin_or_key(x_admin_token: str = Header(default=None),
    46                            x_admin_key: str = Header(default=None)):
    47      if x_admin_key and MS_ADMIN_KEY and x_admin_key == MS_ADMIN_KEY:
    48          return {"via": "admin-key"}
    49      if x_admin_token and _JWT_SECRET:
    50          try:  # _pyjwt/_JWT_SECRET defined later at module level — resolved at call time
    51              return _pyjwt.decode(x_admin_token, _JWT_SECRET, algorithms=[_JWT_ALGO])
    52          except Exception:
    53              pass
    54      raise HTTPException(status_code=401, detail="Admin credentials required.")
    55  from email.utils import parseaddr, formataddr
    56  from datetime import datetime, timezone, timedelta
    57  
    58  app = FastAPI(title="TrustSquare BEA", version="1.3.1")
    59  
    60  # S4 (audit · HIGH): CORS locked to TrustSquare origins only.
    61  # Previously allow_origins=["*"] + allow_origin_regex=".*" — any site could call the BEA
    62  # from a user's browser. Auth is X-Api-Key/email (allow_credentials stays False), and the
    63  # buyer/admin/dashboard are all same-origin on trustsquare.co, so an explicit allowlist
    64  # breaks nothing. A new origin must be added here deliberately.
    65  ALLOWED_ORIGINS = [
    66      "https://trustsquare.co",
    67      "https://www.trustsquare.co",
    68  ]
    69  app.add_middleware(
    70      CORSMiddleware,
    71      allow_origins=ALLOWED_ORIGINS,
    72      allow_credentials=False,
```

## Breaker wiring at BEA startup (attach + alert hook) — from bea_main.py

```
    79  # an attach failure leaves the seam exactly as it was yesterday (naive any-of fallback).
    80  try:
    81      import ai_breaker as _ai_brk
    82      def _brk_alert(payload):
    83          try:
    84              _log.warning("AI-BREAKER %s: %s", payload.get("event"), payload)
    85              _hook = os.getenv("N8N_WEBHOOK_AI_ALERT")
    86              if _hook:
    87                  import httpx as _hx
    88                  with _hx.Client(timeout=5) as _c: _c.post(_hook, json={"source": "ai_breaker", **payload})
    89          except Exception:
    90              pass
    91      _ai_brk.attach(database.get_db, alert=_brk_alert)
    92  except Exception as _brk_e:
    93      import logging as _lg; _lg.getLogger("bea").warning("ai_breaker attach failed (fail-open): %r", _brk_e)
    94  
    95  
    96  # CityLauncher scrapes AGENCY vocabulary ("Estate Agents", "Car Dealers", ...); the app
    97  # speaks 6 category names. This maps a scraped label to the app category the demand loop
    98  # matches on. Keyword-based so it survives new agency labels; None = leave unmatched.
    99  def _demand_norm_category(raw):
   100      t = (raw or "").strip().lower()
```

## transactions table schema (Tuppence ledger) — from database.py

```
    55          );
    56  
    57          CREATE TABLE IF NOT EXISTS transactions (
    58              id INTEGER PRIMARY KEY AUTOINCREMENT,
    59              user_email TEXT NOT NULL,
    60              type TEXT NOT NULL,
    61              amount INTEGER NOT NULL,
    62              description TEXT,
    63              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    64          );
    65  
    66          CREATE INDEX IF NOT EXISTS idx_listings_city ON listings(city);
    67          CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);
    68          CREATE INDEX IF NOT EXISTS idx_listings_claim ON listings(claim_status);
    69          CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    70          CREATE INDEX IF NOT EXISTS idx_intros_listing ON intro_requests(listing_id);
    71          CREATE INDEX IF NOT EXISTS idx_intros_status ON intro_requests(status);
    72      """)
    73      conn.commit()
    74      conn.close()
    75      print("Database initialised successfully.")
    76  
    77  if __name__ == "__main__":
    78      init_db()
```

## ai_spend_config schema + ceiling columns — from bea_main.py

```
   711          conn.execute("ALTER TABLE ai_spend_log ADD COLUMN provider TEXT")
   712  
   713      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_config (
   714          id                  INTEGER PRIMARY KEY CHECK (id = 1),
   715          monthly_income_usd  REAL    NOT NULL DEFAULT 0.0,
   716          alert_threshold_pct REAL    NOT NULL DEFAULT 20.0,
   717          alert_email         TEXT    NOT NULL DEFAULT 'dmcontiki2@gmail.com',
   718          last_alerted_at     TEXT
   719      )""")
   720      # Seed default config row (id=1 enforced by CHECK constraint)
   721      conn.execute("""INSERT OR IGNORE INTO ai_spend_config
   722          (id, monthly_income_usd, alert_threshold_pct, alert_email)
   723          VALUES (1, 0.0, 20.0, 'dmcontiki2@gmail.com')""")
   724  
   725      # C1-RES (AI-SERVICES-AUDIT-1 F2, 5 Aug 2026): pre-dispatch spend RESERVATIONS.
   726      # The ceiling check summed only LOGGED spend, which is written AFTER the call — so
   727      # N concurrent calls all passed the check before any recorded its cost and could
   728      # collectively overshoot. A reservation is a short-lived worst-case hold placed
   729      # BEFORE dispatch and counted by the ceiling check; it is settled when real spend
   730      # is logged, and self-expires so an aborted call can never wedge the budget.
   731      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_holds (
   732          id         INTEGER PRIMARY KEY AUTOINCREMENT,
   733          email      TEXT    NOT NULL DEFAULT '',
   734          est_usd    REAL    NOT NULL DEFAULT 0.0,
   735          created_at TEXT    NOT NULL DEFAULT '',
   736          expires_at TEXT    NOT NULL
   737      )""")
   738  
   739      # INTRO-RELAY-1 (5 Aug 2026, David's Option B ruling): masked-alias introduction
   740      # relay. Two rows per accepted intro - one alias per party. real_email is the ONLY
   741      # place the real address lives; it never enters an outbound body, header, or
   742      # webhook. Doctrine: nothing of the customer's leaves TrustSquare except a
   743      # consented, revocable email channel - never the address itself.
   744      conn.execute("""CREATE TABLE IF NOT EXISTS intro_relay_aliases (
   745          alias         TEXT PRIMARY KEY,
   746          intro_id      INTEGER NOT NULL,
   747          party         TEXT NOT NULL,
   748          real_email    TEXT NOT NULL,
   749          counter_alias TEXT NOT NULL,
   750          active        INTEGER NOT NULL DEFAULT 1,
   751          created_at    TEXT NOT NULL DEFAULT '',
   752          expires_at    TEXT NOT NULL
   753      )""")
   754      conn.execute("CREATE INDEX IF NOT EXISTS idx_relay_intro ON intro_relay_aliases(intro_id)")
   755  
   756      # Launch Switch (free-only <-> verified) — singleton flag row; default = launch/free-only
   757      conn.execute("""CREATE TABLE IF NOT EXISTS launch_switches (
   758          id            INTEGER PRIMARY KEY CHECK (id = 1),
   759          mode          TEXT    NOT NULL DEFAULT 'launch',
   760          verified_tier INTEGER NOT NULL DEFAULT 0,
   761          videos        INTEGER NOT NULL DEFAULT 0,
   762          data_ops      INTEGER NOT NULL DEFAULT 0,
   763          data_places   INTEGER NOT NULL DEFAULT 0,
   764          data_flights  INTEGER NOT NULL DEFAULT 0,
   765          data_mapbox   INTEGER NOT NULL DEFAULT 0,
   766          p_heritage    INTEGER NOT NULL DEFAULT 0,
   767          p_expedition  INTEGER NOT NULL DEFAULT 0,
   768          p_weekend     INTEGER NOT NULL DEFAULT 0,
   769          -- BIT safe-state flags (Mitigator flips these to a SAFE value on a confirmed BIT failure).
   770          -- Defaults = NORMAL/healthy state; the Mitigator only ever moves them toward safe.
   771          ai_example_enabled     INTEGER NOT NULL DEFAULT 1,
   772          auth_fail_closed       INTEGER NOT NULL DEFAULT 0,
   773          tuppence_burn_enabled  INTEGER NOT NULL DEFAULT 1,
   774          -- AI provider seam (D1): live-switchable inference vendor (Page-4 control). Default = anthropic.
   775          ai_active     TEXT    NOT NULL DEFAULT 'anthropic',
   776          -- MANUAL PIN (David 1 Aug 2026): operator override with DECAY — precedence over any
   777          -- auto selection while unexpired; expiry returns control to the standing lane.
   778          ai_active_override  TEXT,
   779          ai_override_expires TEXT,
   780          -- MAINT-B1b: in-app tester fault intake. OFF by default (fail-closed).
```

## Spend logging, alerting, cost ceiling — from bea_main.py

```
  1536  
  1537  
  1538  def _log_ai_spend(email: str, endpoint: str, model_key: str,
  1539                    in_tok: int | None = None, out_tok: int | None = None):
  1540      """Background task: log AI call cost + trigger alert check if threshold crossed.
  1541      Non-blocking — called via background_tasks.add_task() after every AI call.
  1542      Never raises — log errors only.
  1543  
  1544      C2 (Session 97): real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
  1545      No tokens (legacy sites) -> flat _AI_COST estimate, cost_is_real=0. Backward compatible.
  1546      """
  1547      try:
  1548          if in_tok is not None or out_tok is not None:
  1549              it, ot = int(in_tok or 0), int(out_tok or 0)
  1550              cost = _token_cost(model_key, it, ot)
  1551              is_real = 1
  1552          else:
  1553              it, ot = 0, 0
  1554              cost = _AI_COST.get(model_key, 0.0023)
  1555              is_real = 0
  1556          try:
  1557              _prov = _ts_active_provider()   # P1: provider attribution — signature & call sites unchanged
  1558          except Exception:
  1559              _prov = 'anthropic'
  1560          conn = database.get_db()
  1561          try:
  1562              conn.execute(
  1563                  "INSERT INTO ai_spend_log "
  1564                  "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real, provider) "
  1565                  "VALUES (?,?,?,?,?,?,?,?)",
  1566                  (email or '', endpoint, model_key, cost, it, ot, is_real, _prov)
  1567              )
  1568              conn.commit()
  1569              _maybe_fire_spend_alert(conn)
  1570          finally:
  1571              conn.close()
  1572          _settle_hold(email or '')   # C1-RES: real spend recorded — release the reservation
  1573      except Exception as exc:
  1574          _log.error("_log_ai_spend failed: %s", exc)
  1575  
  1576  
  1577  def _maybe_fire_spend_alert(conn):
  1578      """Check if current month AI spend has crossed the configured threshold.
  1579      Fires n8n webhook at most once per day. Silent if not configured.
  1580      """
  1581      try:
  1582          cfg = conn.execute(
  1583              "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
  1584              "FROM ai_spend_config WHERE id = 1"
  1585          ).fetchone()
  1586          if not cfg or cfg["monthly_income_usd"] <= 0:
  1587              return  # income not configured yet — skip
  1588  
  1589          # Current calendar month spend
  1590          month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
  1591          row = conn.execute(
  1592              "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
  1593              "WHERE logged_at >= ?", (month_start,)
  1594          ).fetchone()
  1595          month_spend = row["total"] if row else 0.0
  1596  
  1597          threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
  1598          if month_spend < threshold_usd:
  1599              return  # under threshold — nothing to do
  1600  
  1601          # Check last alerted — don't fire more than once per day
  1602          last = cfg["last_alerted_at"] or ""
  1603          today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
  1604          if last.startswith(today):
  1605              return  # already alerted today
  1606  
  1607          # Update last_alerted_at
  1608          conn.execute(
  1609              "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
  1610              (__import__('datetime').datetime.utcnow().isoformat(),)
  1611          )
  1612          conn.commit()
  1613  
  1614          # Fire n8n alert webhook if configured
  1615          pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
  1616          payload = {
  1617              "alert": "ai_spend_threshold",
  1618              "month_spend_usd": round(month_spend, 4),
  1619              "income_usd": cfg["monthly_income_usd"],
  1620              "threshold_pct": cfg["alert_threshold_pct"],
  1621              "pct_used": round(pct_used, 1),
  1622              "alert_email": cfg["alert_email"],
  1623              "message": (
  1624                  f"TrustSquare AI spend alert: ${month_spend:.4f} spent this month "
  1625                  f"({pct_used:.1f}% of ${cfg['monthly_income_usd']:.2f} income). "
  1626                  f"Threshold: {cfg['alert_threshold_pct']}%."
  1627              ),
  1628          }
  1629          _log.warning("AI spend alert fired: %s", payload["message"])
  1630          if N8N_WEBHOOK_AI_ALERT:
  1631              import asyncio
  1632              try:
  1633                  loop = asyncio.get_event_loop()
  1634                  if loop.is_running():
  1635                      loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
  1636              except Exception:
  1637                  pass  # alert failure must never affect user response
  1638      except Exception as exc:
  1639          _log.error("_maybe_fire_spend_alert failed: %s", exc)
  1640  
  1641  
  1642  # C1-RES worst-case hold (USD): a conservative per-call ceiling — the dearest metered
  1643  # call (Sonnet vision batch) rounds up to this. Over-reserves slightly (safe direction);
  1644  # settled down to the real figure the moment _log_ai_spend records actual tokens.
  1645  _AI_WORST_CASE_HOLD_USD = 0.06
  1646  _HOLD_TTL_S = 180
  1647  
  1648  def _active_holds_usd(conn, email: str | None = None) -> float:
  1649      """Sum of unexpired reservations (optionally for one user). Purges expired rows."""
  1650      now = __import__('datetime').datetime.utcnow().isoformat(timespec="seconds")
  1651      conn.execute("DELETE FROM ai_spend_holds WHERE expires_at < ?", (now,))
  1652      if email is not None:
  1653          row = conn.execute("SELECT COALESCE(SUM(est_usd),0) t FROM ai_spend_holds "
  1654                             "WHERE email=? AND expires_at >= ?", (email, now)).fetchone()
  1655      else:
  1656          row = conn.execute("SELECT COALESCE(SUM(est_usd),0) t FROM ai_spend_holds "
  1657                             "WHERE expires_at >= ?", (now,)).fetchone()
  1658      return float(row["t"] if row else 0.0)
  1659  
  1660  def _settle_hold(email: str) -> None:
  1661      """Release the oldest reservation for this user — called once real spend is logged.
  1662      Never raises (bookkeeping must not break serving)."""
  1663      try:
  1664          conn = database.get_db()
  1665          try:
  1666              row = conn.execute("SELECT id FROM ai_spend_holds WHERE email=? "
  1667                                 "ORDER BY id ASC LIMIT 1", (email or '',)).fetchone()
  1668              if row:
  1669                  conn.execute("DELETE FROM ai_spend_holds WHERE id=?", (row["id"],))
  1670                  conn.commit()
  1671          finally:
  1672              conn.close()
  1673      except Exception as exc:
  1674          _log.error("_settle_hold failed: %s", exc)
  1675  
  1676  
  1677  def _check_cost_ceiling(email: str) -> None:
  1678      """C1 (Session 97) — HARD daily cost ceiling. Pre-flight guard before every paid
  1679      AI call. REFUSES (HTTP 429) when today's logged AI spend has reached the per-user
  1680      or platform-wide USD ceiling. Distinct from observe-and-alert. Ceiling 0 = off.
  1681      Superusers exempt from the per-user rail (still counted toward platform).
  1682      Fail-OPEN on internal error — never lock a legitimate paying user out.
  1683      """
  1684      try:
  1685          conn = database.get_db()
  1686          try:
  1687              cfg = conn.execute(
  1688                  "SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  1689                  "FROM ai_spend_config WHERE id = 1"
  1690              ).fetchone()
  1691              if not cfg:
  1692                  return
  1693              user_cap     = cfg["daily_user_ceiling_usd"]     or 0.0
  1694              platform_cap = cfg["daily_platform_ceiling_usd"] or 0.0
  1695              if user_cap <= 0 and platform_cap <= 0:
```

## Active provider switch + pin/override (TTL decay) — from bea_main.py

```
  1409  # Manual-pin TTL (hours). David 1 Aug 2026: 24h now; REVIEW dated ~1 Nov 2026 (3 months
  1410  # proven live) to consider shortening to 1h. Env-tunable, no deploy needed to change.
  1411  AI_OVERRIDE_TTL_HOURS = float(os.getenv("AI_OVERRIDE_TTL_HOURS", "24"))
  1412  
  1413  _TS_AI_CACHE = {"prov": None, "standing": None, "override": None, "expires": None, "ts": 0.0}
  1414  def _ts_active_provider():
  1415      """The LIVE active provider — DB-backed (Page-4 switchable, no restart). Falls back to the
  1416      startup env value if the DB is unreachable. Cached ~10s so we never hammer the DB per call."""
  1417      import time as _t
  1418      now=_t.time()
  1419      if _TS_AI_CACHE["prov"] and (now-_TS_AI_CACHE["ts"])<10:
  1420          return _TS_AI_CACHE["prov"]
  1421      prov=_TS_AI_PROVIDER  # startup default
  1422      standing, override, expires = prov, None, None
  1423      try:
  1424          conn=database.get_db()
  1425          try:
  1426              row=conn.execute("SELECT ai_active, ai_active_override, ai_override_expires "
  1427                               "FROM launch_switches WHERE id=1").fetchone()
  1428              if row:
  1429                  if row["ai_active"]: standing = prov = row["ai_active"]
  1430                  override, expires = row["ai_active_override"], row["ai_override_expires"]
  1431          finally:
  1432              conn.close()
  1433      except Exception:
  1434          pass
  1435      # MANUAL PIN precedence with DECAY (David 1 Aug 2026): an unexpired operator pin
  1436      # outranks the standing/auto lane; past expiry the standing lane silently resumes.
  1437      import datetime as _dt
  1438      if override and expires:
  1439          try:
  1440              if _dt.datetime.utcnow() < _dt.datetime.fromisoformat(expires):
  1441                  prov = override
  1442              else:
  1443                  override = None   # expired — report as inactive, standing rules
  1444          except Exception:
  1445              override = None
  1446      else:
  1447          override = None
  1448      _TS_AI_CACHE.update(prov=prov, standing=standing, override=override, expires=expires if override else None, ts=now)
  1449      return prov
  1450  
  1451  def _ts_models_for(prov):
  1452      try:
  1453          return _ts_ai.TASK_MODEL.get(prov, _ts_ai.TASK_MODEL["anthropic"])
  1454      except Exception:
  1455          return _TS_AI_MODELS
  1456  
  1457  # _ts_ai_url()/_ts_ai_headers() REMOVED 31 Jul 2026 — their sole caller (vision-draft) migrated
  1458  # to the ai_provider seam, completing P0 at 22/22 call sites. The wire protocol now lives ONLY in
  1459  # ai_provider.py adapters; RG-0017 asserts no raw vendor endpoint ever returns to this file.
  1460  if not EMAIL_INBOUND_SECRET:
  1461      _log.warning("EMAIL_INBOUND_SECRET not set — /email/inbound will reject all calls")
  1462  if not GMAIL_APP_PASSWORD:
  1463      _log.warning("GMAIL_APP_PASSWORD not set — triage replies will be drafted, never sent")
  1464  
  1465  CF_ZONE_ID    = os.getenv("CF_ZONE_ID")
  1466  CF_CACHE_TOKEN = os.getenv("CF_CACHE_TOKEN")
  1467  
  1468  async def _cf_purge_all():
```

## Tuppence helpers (deduct / balance / pre-flight require) — from bea_main.py

```
 14169  
 14170  
 14171  def _deduct_tuppence(conn, email: str, amount: int, description: str) -> int:
 14172      """Deduct `amount` Tuppence from `email`. Returns new balance.
 14173      Raises HTTPException 402 if balance insufficient. Does NOT commit."""
 14174      row = conn.execute(
 14175          "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 14176          (email,)
 14177      ).fetchone()
 14178      balance = int(row["bal"])
 14179      if balance < amount:
 14180          raise HTTPException(
 14181              status_code=402,
 14182              detail=f"Insufficient Tuppence — you have {balance}T, need {amount}T"
 14183          )
 14184      conn.execute(
 14185          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'ai_service', ?, ?)",
 14186          (email, -amount, description)
 14187      )
 14188      return balance - amount
 14189  
 14190  
 14191  def _current_tuppence(email: str) -> int:
 14192      """Read-only Tuppence balance on a fresh connection. Used by deliver-then-charge
 14193      paths to report 'tuppence_remaining' when NO charge was made."""
 14194      c = database.get_db()
 14195      try:
 14196          row = c.execute(
 14197              "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 14198              (email,)
 14199          ).fetchone()
 14200          return int(row["bal"])
 14201      finally:
 14202          c.close()
 14203  
 14204  
 14205  def _require_tuppence(email: str, amount: int = 1) -> None:
 14206      """Pre-flight guard: ensure the buyer COULD pay before we run a paid AI service.
 14207      Raises 402 if not. Does NOT deduct — deduction happens only on a verified result."""
 14208      if _current_tuppence(email) < amount:
 14209          raise HTTPException(
 14210              status_code=402,
 14211              detail=f"Insufficient Tuppence — you need {amount}T to run this check."
 14212          )
 14213  
 14214  
 14215  # ── AI1 — Listing Rewrite ─────────────────────────────────────────────────────
 14216  
 14217  @app.post("/listings/{listing_id}/ai-rewrite")
 14218  async def ai_listing_rewrite(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
```

## AI1 Listing Rewrite (full endpoint) — from bea_main.py

```
 14216  
 14217  @app.post("/listings/{listing_id}/ai-rewrite")
 14218  async def ai_listing_rewrite(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 14219      """AI1: Seller pays 1T — Claude Haiku rewrites title + description.
 14220      Uses current market language and buyer psychology for the listing category.
 14221      Returns {new_title, new_description, tuppence_remaining}.
 14222      """
 14223      if not ai_provider.any_lane_configured():
 14224          raise HTTPException(status_code=503, detail="AI not configured")
 14225      email = _bind_charged_email(email, ts_user, "ai1-rewrite")   # ACCOUNT-BIND-1
 14226      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 14227  
 14228      conn = database.get_db()
 14229      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14230      if not listing:
 14231          conn.close()
 14232          raise HTTPException(status_code=404, detail="Listing not found")
 14233      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 14234          conn.close()
 14235          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 14236  
 14237      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 14238      _rw_charge_desc = f"AI Listing Rewrite · #{listing_id} · {listing['title'][:40]}"
 14239      conn.close()
 14240  
 14241      category = listing["category"] or "General"
 14242      city     = listing["city"] or "South Africa"
 14243      title    = listing["title"] or ""
 14244      desc     = listing["description"] or ""
 14245      price    = listing["price"] or ""
 14246  
 14247      system_prompt = (
 14248          "You are an expert marketplace copywriter for TrustSquare, a South African peer-to-peer local marketplace. "
 14249          "You write short, honest, buyer-friendly listings using current South African market language. "
 14250          "You never invent details. You prefer concrete facts over adjectives. "
 14251          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include street addresses, "
 14252          "business names, complex names, seller names, agent names, phone numbers, email addresses, "
 14253          "or any other identifying information in any generated text. "
 14254          "Always respond with a single valid JSON object — no markdown, no explanation."
 14255      )
 14256  
 14257      user_prompt = (
 14258          f"Rewrite this {category} listing for a buyer in {city}, South Africa.\n\n"
 14259          f"CURRENT TITLE: {title}\n"
 14260          f"CURRENT DESCRIPTION: {desc}\n"
 14261          f"PRICE: {price}\n\n"
 14262          "Return JSON with exactly two keys:\n"
 14263          '{"new_title": "<15 words max, specific and punchy>", '
 14264          '"new_description": "<60-120 words, 2-3 short paragraphs, buyer psychology, honest, no clichés>"}'
 14265      )
 14266  
 14267      try:
 14268          _sr = await asyncio.to_thread(
 14269              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14270              task="haiku", max_tokens=350, system=system_prompt,
 14271              provider=_ts_active_provider(), timeout=20)
 14272          _rw_in, _rw_out = _sr.in_tokens, _sr.out_tokens
 14273          # P2 — Tuppence covers the revenue side; log token spend so the cost
 14274          # dashboard sees it too (sweep 12 Jun 2026)
 14275          _log_ai_spend(email, "/listings/ai-rewrite", "haiku", _rw_in, _rw_out)
 14276          raw = _sr.text.strip()
 14277          # Strip markdown fences if model adds them
 14278          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14279          raw = _re_match.sub(r"\s*```$", "", raw)
 14280          result = json.loads(raw)
 14281          new_title = str(result.get("new_title", "")).strip()[:120]
 14282          new_desc  = str(result.get("new_description", "")).strip()[:1000]
 14283      except Exception as exc:
 14284          _log.error("ai-rewrite: %s", exc)
 14285          raise HTTPException(status_code=500, detail="AI rewrite failed — no Tuppence was charged") from exc
 14286  
 14287      # F2 fix: deliver-then-charge — deduction happens ONLY here, after a good result,
 14288      # so the help card's "server error = no Tuppence deducted" promise is true.
 14289      _conn2 = database.get_db()
 14290      try:
 14291          remaining = _deduct_tuppence(_conn2, email, 1, _rw_charge_desc)
 14292          _conn2.commit()
 14293      finally:
 14294          _conn2.close()
 14295      _log.info("ai-rewrite: listing #%d email=%s", listing_id, email)
 14296      return {
 14297          "new_title": new_title,
 14298          "new_description": new_desc,
 14299          "tuppence_remaining": remaining,
 14300      }
 14301  
 14302  
 14303  # ── AI2 — Seller Audit ────────────────────────────────────────────────────────
 14304  
 14305  @app.post("/listings/{listing_id}/ai-audit")
 14306  async def ai_seller_audit(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 14307      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 14308      3 specific, actionable improvement steps.
 14309      Returns {actions: [{step, reason}], tuppence_remaining}.
 14310      """
 14311      if not ai_provider.any_lane_configured():
 14312          raise HTTPException(status_code=503, detail="AI not configured")
 14313      email = _bind_charged_email(email, ts_user, "ai2-audit")   # ACCOUNT-BIND-1
 14314      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 14315  
```

## AI2 Seller Audit (full endpoint) — from bea_main.py

```
 14304  
 14305  @app.post("/listings/{listing_id}/ai-audit")
 14306  async def ai_seller_audit(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 14307      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 14308      3 specific, actionable improvement steps.
 14309      Returns {actions: [{step, reason}], tuppence_remaining}.
 14310      """
 14311      if not ai_provider.any_lane_configured():
 14312          raise HTTPException(status_code=503, detail="AI not configured")
 14313      email = _bind_charged_email(email, ts_user, "ai2-audit")   # ACCOUNT-BIND-1
 14314      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 14315  
 14316      conn = database.get_db()
 14317      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14318      if not listing:
 14319          conn.close()
 14320          raise HTTPException(status_code=404, detail="Listing not found")
 14321      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 14322          conn.close()
 14323          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 14324  
 14325      # Read intro request count for context
 14326      intro_row = conn.execute(
 14327          "SELECT COUNT(*) as cnt FROM intro_requests WHERE listing_id = ?", (listing_id,)
 14328      ).fetchone()
 14329      intro_count = intro_row["cnt"] if intro_row else 0
 14330  
 14331      # Read trust score
 14332      user_row = conn.execute(
 14333          "SELECT trust_score FROM users WHERE email = ?", (email,)
 14334      ).fetchone()
 14335      trust_score = user_row["trust_score"] if user_row and user_row["trust_score"] else "unknown"
 14336  
 14337      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 14338      _au_charge_desc = f"AI Seller Audit · #{listing_id} · {listing['title'][:40]}"
 14339      conn.close()
 14340  
 14341      category = listing["category"] or "General"
 14342      city     = listing["city"] or "South Africa"
 14343      title    = listing["title"] or "(no title)"
 14344      desc     = listing["description"] or "(no description)"
 14345      price    = listing["price"] or "(no price)"
 14346  
 14347      system_prompt = (
 14348          "You are a marketplace performance coach for TrustSquare, a South African peer-to-peer marketplace. "
 14349          "You give direct, specific, actionable advice — no filler, no encouragement padding. "
 14350          "Think like a top-performing seller in the same category who has seen hundreds of listings. "
 14351          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include or suggest including "
 14352          "street addresses, business names, seller names, agent names, phone numbers, or contact details "
 14353          "in any generated text or improvement suggestions. "
 14354          "Always respond with a single valid JSON object — no markdown, no explanation."
 14355      )
 14356  
 14357      user_prompt = (
 14358          f"This {category} listing in {city} has received {intro_count} intro request(s) and "
 14359          f"the seller has a trust score of {trust_score}.\n\n"
 14360          f"TITLE: {title}\n"
 14361          f"DESCRIPTION: {desc}\n"
 14362          f"PRICE: {price}\n\n"
 14363          "Identify the 3 most important reasons a buyer might scroll past this listing without requesting an intro. "
 14364          "For each reason give a specific fix the seller can do right now.\n\n"
 14365          "Return JSON: "
 14366          '{"actions": [{"step": "<imperative fix, 8 words max>", "reason": "<why this matters, 1 sentence>"}, ...]}'
 14367          " — exactly 3 items in the array."
 14368      )
 14369  
 14370      try:
 14371          _sr = await asyncio.to_thread(
 14372              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14373              task="haiku", max_tokens=400, system=system_prompt,
 14374              provider=_ts_active_provider(), timeout=20)
 14375          _au_in, _au_out = _sr.in_tokens, _sr.out_tokens
 14376          # P2 — Tuppence covers the revenue side; log token spend so the cost
 14377          # dashboard sees it too (sweep 12 Jun 2026)
 14378          _log_ai_spend(email, "/listings/ai-audit", "haiku", _au_in, _au_out)
 14379          raw = _sr.text.strip()
 14380          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14381          raw = _re_match.sub(r"\s*```$", "", raw)
 14382          result = json.loads(raw)
 14383          actions = result.get("actions", [])
 14384          # Sanitise — max 3, enforce fields
 14385          clean_actions = []
 14386          for a in actions[:3]:
 14387              if isinstance(a, dict) and a.get("step"):
 14388                  clean_actions.append({
 14389                      "step":   str(a.get("step",   ""))[:80],
 14390                      "reason": str(a.get("reason", ""))[:200],
 14391                  })
 14392      except Exception as exc:
 14393          _log.error("ai-audit: %s", exc)
 14394          raise HTTPException(status_code=500, detail="AI audit failed — no Tuppence was charged") from exc
 14395  
 14396      _conn2 = database.get_db()
 14397      try:
 14398          remaining = _deduct_tuppence(_conn2, email, 1, _au_charge_desc)   # F2: charge on delivery
 14399          _conn2.commit()
 14400      finally:
 14401          _conn2.close()
 14402      _log.info("ai-audit: listing #%d email=%s intros=%d", listing_id, email, intro_count)
 14403      return {
 14404          "actions": clean_actions,
 14405          "tuppence_remaining": remaining,
 14406      }
 14407  
 14408  
 14409  # ── AI3 — Buyer Price Check (upgraded Session 77: three-panel intelligence) ──
 14410  
 14411  # -- Tiered Value Selector: availability helpers + value-tiers endpoint --------
 14412  # STEP 5: the paid master switch AND per-provider liveness now come from the
 14413  # server-readable feature_flags store (feature_flags.json), so enabling a paid
 14414  # provider later is a CONFIG change, not a code edit. Safe defaults: paid OFF,
 14415  # every paid/contract provider OFF, free/open/owned providers ON.
 14416  def _paid_tiers_enabled() -> bool:
 14417      return feature_flags.paid_tiers_enabled()
 14418  
```

## AI3 Price Check (charge logic + integrity model) — from bea_main.py

```
 14876  
 14877  @app.post("/listings/{listing_id}/price-check")
 14878  async def ai_price_check(listing_id: int, email: str, tier: Optional[str] = None,
 14879                           ts_user: str = Cookie(default=None)):
 14880      """AI3: Buyer pays 1T — honest, three-panel price intelligence.
 14881  
 14882      INTEGRITY MODEL (price-integrity fix):
 14883        The model writes the SENTENCE; the system produces the NUMBER.
 14884        - Collectibles with a resolved Scryfall id  -> VERIFIED feed price (USD->ZAR
 14885          live rate). The LLM only narrates the real figures it is handed.
 14886        - Everything else -> an explicitly-labelled QUALITATIVE GUIDE. The LLM may
 14887          give a rough range but it is flagged 'not a verified price', and we never
 14888          cheerlead ('move quickly' is not permitted anywhere).
 14889        - A first-class fraud guard fires when asking price is far below a VERIFIED
 14890          floor: the verdict becomes a warning, never a 'buy' nudge.
 14891      Returns {verdict, source, sa_context, sa_range, assessment, official_context,
 14892               official_range, local_vs_global, asking_price, verified, safety_flag,
 14893               tuppence_remaining, ...legacy}.
 14894      """
 14895      if not ai_provider.any_lane_configured():
 14896          raise HTTPException(status_code=503, detail="AI not configured")
 14897  
 14898      conn = database.get_db()
 14899      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14900      if not listing:
 14901          conn.close()
 14902          raise HTTPException(status_code=404, detail="Listing not found")
 14903  
 14904      # DELIVER-THEN-CHARGE (Session 95): we do NOT deduct here. Tuppence is only
 14905      # charged at the end, and ONLY if we produced a verified service. A guess,
 14906      # a 'cannot verify', or any failure costs the buyer nothing.
 14907      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour; a
 14908      # tier-aware caller must request a tier actually offered for this listing.
 14909      if tier is None:
 14910          _charge = 1
 14911      else:
 14912          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "fair_price")}
 14913          if tier not in _offered_t:
 14914              conn.close()
 14915              raise HTTPException(status_code=400,
 14916                  detail=f"Tier {tier} is not available for this listing")
 14917          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 14918      _require_tuppence(email, _charge)   # pre-flight only — no deduction yet
 14919      email = _bind_charged_email(email, ts_user, "ai3-price")   # ACCOUNT-BIND-1
 14920      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 14921      category    = listing["category"] or "General"
 14922      city        = listing["city"] or "South Africa"
 14923      title       = listing["title"] or "(no title)"
 14924      desc        = listing["description"] or "(no description)"
 14925      price       = listing["price"] or "(no price)"
 14926      scryfall_id = listing["scryfall_id"] if "scryfall_id" in listing.keys() else None
 14927      conn.close()  # done reading; charging happens on its own connection at the end
 14928  
 14929      # Parse the buyer-facing asking price into a number for ratio checks.
 14930      asking_zar = None
 14931      try:
 14932          asking_zar = float(str(price).replace("R", "").replace(",", "").strip())
 14933      except Exception:
 14934          asking_zar = None
 14935  
 14936      # ── Step 1+2: try to resolve a REAL verified price (collectibles) ──────────
 14937      verified_block = None        # text handed to the model as ground truth
 14938      official_range = "N/A"
 14939      official_ctx   = ""
 14940      floor_zar      = None
 14941      verified       = False
 14942      source         = "ai_estimate"
 14943  
 14944      # Late-resolve a scryfall id if the listing predates this column.
 14945      if not scryfall_id:
 14946          try:
 14947              scryfall_id = await resolve_scryfall_id(title, category)
 14948              if scryfall_id:
 14949                  c2 = database.get_db()
 14950                  c2.execute("UPDATE listings SET scryfall_id = ? WHERE id = ?",
 14951                             (scryfall_id, listing_id))
 14952                  c2.commit(); c2.close()
 14953          except Exception:
 14954              scryfall_id = None
 14955  
 14956      if scryfall_id:
 14957          feed = await scryfall_price_by_id(scryfall_id)
 14958          if feed and feed.get("usd"):
 14959              rate = await live_usd_zar()
 14960              usd  = feed["usd"]
 14961              floor_zar = usd * rate
 14962              verified = True
 14963              source   = "scryfall"
 14964              reserved = " (Reserved List — cannot be reprinted)" if feed.get("reserved") else ""
 14965              official_range = f"R{floor_zar:,.0f}  (USD ${usd:,.2f} \u00d7 R{rate:.2f}/USD)"
 14966              official_ctx   = (f"Verified market price for {feed.get('name')} "
 14967                                f"[{feed.get('set_name')}]{reserved}: "
 14968                                f"USD ${usd:,.2f} on TCGPlayer (via Scryfall), "
 14969                                f"\u2248 R{floor_zar:,.0f} at today's rate.")
 14970              verified_block = (
 14971                  f"VERIFIED MARKET DATA (use these EXACT figures, do not alter them):\n"
 14972                  f"- Card: {feed.get('name')} [{feed.get('set_name')}]{reserved}\n"
 14973                  f"- Verified market price: USD ${usd:,.2f} = R{floor_zar:,.0f} "
 14974                  f"(live rate R{rate:.2f}/USD)\n"
 14975                  f"- Buyer's asking price: {price}\n"
 14976              )
 14977  
 14978      # ── Step 3: narrate. Two prompt modes: verified vs qualitative-guide ───────
 14979      # -- STEP 3: no card feed -> try the FREE/owned resolver for the chosen tier
 14980      if (not verified_block) and (tier is not None):
 14981          _fpx = await _fair_price_resolve(
 14982              listing, listing_id, tier, _tierkey_for(listing, "fair_price"),
 14983              _listing_country_iso2(listing), category, city, asking_zar)
 14984          if _fpx and _fpx[0] == "verified":
 14985              _e = _fpx[1]
 14986              verified = True
 14987              source = _e["source"]
 14988              floor_zar = _e.get("floor_zar")
 14989              official_range = _e["official_range"]
 14990              official_ctx = _e["official_ctx"]
 14991              verified_block = _e["block"]
 14992          elif _fpx and _fpx[0] == "area_guide":
 14993              _e = _fpx[1]
 14994              _log.info("ai-price-check: listing #%d buyer=%s AREA-GUIDE %s (0T free)",
 14995                        listing_id, email, _e["source"])
 14996              return {
 14997                  "verdict": "area_guide", "source": _e["source"],
 14998                  "verified": False, "charged": False,
 14999                  "sa_context": "", "sa_range": _e.get("range_text", "N/A"),
 15000                  "assessment": _e["assessment"],
 15001                  "official_context": _e.get("provenance", ""),
 15002                  "official_range": _e.get("range_text", "N/A"),
 15003                  "local_vs_global": "cannot_compare", "asking_price": price,
 15004                  "safety_flag": None, "tuppence_remaining": _current_tuppence(email),
 15005                  "indicative_label": _INDICATIVE_LABEL,
 15006                  "provenance_date": _e.get("date", ""),
 15007                  "context": _e["assessment"], "suggested_range": _e.get("range_text", "N/A"),
 15008              }
 15009      if verified_block:
 15010          system_prompt = (
 15011              "You are a pricing analyst for TrustSquare, a South African marketplace. "
 15012              "You are given VERIFIED market figures. You must NEVER invent, round, or "
 15013              "contradict them — only explain them in plain language. Never tell a buyer "
 15014              "to 'move quickly' or 'buy now'. Be honest and protective. "
 15015              "Always respond with a single valid JSON object — no markdown."
 15016          )
 15017          user_prompt = (
 15018              f"A buyer is considering this {category} listing in {city}, South Africa.\n\n"
 15019              f"TITLE: {title}\nDESCRIPTION: {desc[:400]}\n\n"
 15020              f"{verified_block}\n"
 15021              "Write a short, honest assessment comparing the asking price to the verified "
 15022              "market price. Do not output any price number other than those given above.\n"
 15023              "Return JSON with these keys (strings, 50 words max each):\n"
 15024              "{\n"
 15025              '  "verdict": "fair" | "above_market" | "below_market" | "cannot_assess",\n'
 15026              '  "sa_context": "<note on the SA second-hand reality for this item, qualitative>",\n'
 15027              '  "assessment": "<plain-language read on the asking price vs the verified figure>",\n'
 15028              '  "local_vs_global": "cheaper_locally" | "cheaper_globally" | "similar" | "cannot_compare"\n'
 15029              "}"
 15030          )
 15031      else:
 15032          # No verified price feed for this category. Per the integrity rule, we do
 15033          # NOT sell a guess. Return an honest 'cannot verify' and charge nothing.
 15034          _log.info("ai-price-check: listing #%d buyer=%s NO-FEED -> free cannot_verify",
 15035                    listing_id, email)
 15036          bal = _current_tuppence(email)
 15037          return {
 15038              "verdict":          "cannot_verify",
 15039              "source":           "no_feed",
 15040              "verified":         False,
 15041              "charged":          False,
 15042              "sa_context":       "",
 15043              "sa_range":         "N/A",
 15044              "assessment":       ("We don\u2019t yet have a verified price source for this "
 15045                                   "category, so we won\u2019t guess. No Tuppence was charged. "
 15046                                   "Compare the asking price against similar local listings "
 15047                                   "before deciding."),
 15048              "official_context": "",
 15049              "official_range":   "N/A",
 15050              "local_vs_global":  "cannot_compare",
 15051              "asking_price":     price,
 15052              "safety_flag":      None,
 15053              "tuppence_remaining": bal,
 15054              "context":          "",
 15055              "suggested_range":  "N/A",
```

## AI4 Yield (deliver-then-charge reference) — from bea_main.py

```
 15189  
 15190  @app.post("/listings/{listing_id}/yield-calc")
 15191  async def ai_yield_calc(listing_id: int, email: str,
 15192                          ts_user: str = Cookie(default=None),
 15193                          rent: float | None = None,
 15194                          purchase_price: float | None = None,
 15195                          tier: Optional[str] = None):
 15196      """AI4: Property yield — HONEST & deliver-then-charge (Session 95).
 15197  
 15198      A real gross yield needs BOTH a purchase price and an annual rent. A listing
 15199      only carries one number (sale price OR monthly rent), so we:
 15200        - take the listing's own figure for its side, and
 15201        - accept the OTHER figure from the caller (?rent= or ?purchase_price=).
 15202      If the second figure is missing we return needs_input and charge NOTHING.
 15203      The yield is computed in PYTHON (not guessed by the model). The LLM only
 15204      writes the benchmark sentence. 1T is charged ONLY when a real yield is
 15205      produced from real inputs.
 15206      """
 15207      if not ai_provider.any_lane_configured():
 15208          raise HTTPException(status_code=503, detail="AI not configured")
 15209  
 15210      conn = database.get_db()
 15211      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 15212      if not listing:
 15213          conn.close()
 15214          raise HTTPException(status_code=404, detail="Listing not found")
 15215  
 15216      category = listing["category"] or ""
 15217      if "property" not in category.lower() and category.lower() not in ("property", "estate agents", "accommodation"):
 15218          conn.close()
 15219          raise HTTPException(status_code=400, detail="Yield calculator is only available for Property listings")
 15220  
 15221      city          = listing["city"] or "South Africa"
 15222      suburb        = listing["suburb"] or ""
 15223      title         = listing["title"] or "(no title)"
 15224      desc          = listing["description"] or ""
 15225      price_raw     = listing["price"] or ""
 15226      listing_type  = (listing["listing_type"] if "listing_type" in listing.keys() else None) or ""
 15227      conn.close()
 15228  
 15229      # Pre-flight: can the buyer pay at all? (No deduction yet.)
 15230      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour.
 15231      if tier is None:
 15232          _charge = 1
 15233      else:
 15234          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "yield")}
 15235          if tier not in _offered_t:
 15236              raise HTTPException(status_code=400,
 15237                  detail=f"Tier {tier} is not available for this listing")
 15238          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 15239      _require_tuppence(email, _charge)
 15240      email = _bind_charged_email(email, ts_user, "ai4-yield")   # ACCOUNT-BIND-1
 15241      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 15242  
 15243      def _num(v):
 15244          try:
 15245              return float(str(v).replace("R", "").replace(",", "")
 15246                           .replace("/month", "").replace("pm", "").strip())
 15247          except Exception:
 15248              return None
 15249  
 15250      listing_amount = _num(price_raw)
 15251      lt = listing_type.lower()
 15252      is_rental = ("rent" in lt) or ("rent" in (title + " " + desc).lower() and "for sale" not in lt)
 15253  
 15254      # Resolve purchase_price (annual rent / monthly rent) from listing + caller input.
 15255      monthly_rent = None
 15256      buy_price    = None
 15257      need = None
 15258      if is_rental:
 15259          # Listing price IS the monthly rent. Need the purchase price from caller.
 15260          monthly_rent = listing_amount
 15261          buy_price    = purchase_price
 15262          if not buy_price:
 15263              need = "purchase_price"
 15264      else:
 15265          # Listing price IS the sale/purchase price. Need expected monthly rent.
 15266          buy_price    = listing_amount
 15267          monthly_rent = rent
 15268          if not monthly_rent:
 15269              need = "rent"
 15270  
 15271      # Honest 'needs input' — FREE, no Tuppence charged.
 15272      # -- STEP 3: source the missing half from a FREE/owned feed (per tier+country)
 15273      _country_y = _listing_country_iso2(listing)
 15274      _rent_src = "your figure"
 15275      _price_src = "the listing"
 15276      if need and tier is not None:
 15277          _filled = await _yield_fill_missing(need, tier, _country_y, city, suburb, listing, listing_id)
 15278          if _filled:
 15279              if need == "rent":
 15280                  monthly_rent = _filled["value"]; _rent_src = _filled["provenance"]
 15281              else:
 15282                  buy_price = _filled["value"]; _price_src = _filled["provenance"]
 15283              need = None
 15284  
 15285      if need or not buy_price or not monthly_rent or buy_price <= 0 or monthly_rent <= 0:
 15286          bal = _current_tuppence(email)
 15287          prompt_for = ("the expected monthly rent" if need == "rent"
 15288                        else "the likely purchase price" if need == "purchase_price"
 15289                        else "both the purchase price and the monthly rent")
 15290          return {
 15291              "status":           "needs_input",
 15292              "charged":          False,
 15293              "need":             need or "both",
 15294              "listing_amount":   listing_amount,
 15295              "is_rental":        is_rental,
 15296              "message":          (f"To calculate a real yield we need {prompt_for}. "
 15297                                   f"Enter it and we\u2019ll compute the actual figure — "
 15298                                   f"no Tuppence is charged until we do."),
 15299              "tuppence_remaining": bal,
 15300          }
 15301  
 15302      # ── REAL computation in Python (deterministic, auditable) ──────────────────
 15303      annual_rent = monthly_rent * 12.0
 15304      gross = (annual_rent / buy_price) * 100.0
 15305  
 15306      # Net estimate: subtract a transparent cost band (rates, levies, maintenance,
 15307      # vacancy). We show the assumption rather than hiding it inside a model guess.
 15308      # STEP 3: versioned, dated per-region net-cost band replaces the flat 3%.
 15309      _band = tier_resolvers.net_cost_band(_country_y)
 15310      NET_COST_PCT = float(_band.get("typical", 3.0))
 15311      net = gross - NET_COST_PCT
 15312  
 15313      # LLM writes ONLY the qualitative benchmark sentence — handed the real numbers.
 15314      location_str = f"{suburb}, {city}" if suburb else city
 15315      _BENCHMARKS = {
 15316          "ZA": ("SA GROSS YIELD BENCHMARKS (2026): Pretoria residential 7-10%, "
 15317                 "Cape Town 5-7%, Johannesburg 6-9%, Durban 7-10%, secondary cities 8-12%, "
 15318                 "commercial 9-12%, student accommodation 10-14%."),
```

## AI5 Batch Cards (full endpoint) — from bea_main.py

```
 15421  
 15422  @app.post("/listings/batch-cards")
 15423  async def ai_batch_card_listings(req: BatchCardRequest, ts_user: str = Cookie(default=None)):
 15424      """AI5: Seller pays 2T — Claude Sonnet Vision analyses up to 10 card photos and
 15425      returns an array of draft listing JSONs ready for review and publish.
 15426      Each draft contains title, description, price_suggestion, condition, category.
 15427      Capped at 10 images per call. 2T flat cost regardless of card count.
 15428      Returns {drafts: [...], cards_processed, tuppence_remaining}.
 15429      """
 15430      if not ai_provider.any_lane_configured():
 15431          raise HTTPException(status_code=503, detail="AI not configured")
 15432  
 15433      if not req.images:
 15434          raise HTTPException(status_code=400, detail="At least one image is required")
 15435      _bind_charged_email(req.seller_email, ts_user, "ai5-batch-cards")   # ACCOUNT-BIND-1
 15436      _check_cost_ceiling(req.seller_email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 15437  
 15438      # Cap at 10 cards
 15439      images = req.images[:10]
 15440      card_count = len(images)
 15441  
 15442      _require_tuppence(req.seller_email, 2)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 15443      _bc_charge_desc = f"AI Batch Cards · {card_count} card(s) · {req.city}"
 15444  
 15445      suburb_str = req.suburb or req.city
 15446      location_str = f"{suburb_str}, {req.city}"
 15447  
 15448      system_prompt = (
 15449          "You are an expert trading card and collectables appraiser and marketplace copywriter "
 15450          "for TrustSquare, a South African peer-to-peer local marketplace. "
 15451          "You identify cards/collectables from photos, assess condition, and write concise buyer-friendly listings. "
 15452          "You know SA collectables market values. "
 15453          "Always respond with a single valid JSON object — no markdown, no explanation."
 15454      )
 15455  
 15456      # Build the message content: one text block + one image block per card
 15457      content_blocks = [
 15458          {
 15459              "type": "text",
 15460              "text": (
 15461                  f"Analyse these {card_count} trading card / collectable image(s) for a seller in {location_str}, "
 15462                  "South Africa. For each image, generate a complete listing draft.\n\n"
 15463                  "For each card/item return:\n"
 15464                  '{"title": "<specific card/item name, set, year if visible, max 12 words>", '
 15465                  '"description": "<40-80 words: card details, set/series, condition notes, notable features>", '
 15466                  '"price_suggestion": "<e.g. R150 or R200–R350 depending on condition>", '
 15467                  '"condition": "mint" | "near_mint" | "excellent" | "good" | "fair" | "poor", '
 15468                  '"category": "Collectors"}\n\n'
 15469                  f'Return JSON: {{"drafts": [<one object per image in order>]}}'
 15470              )
 15471          }
 15472      ]
 15473  
 15474      for _, img_b64 in enumerate(images):
 15475          # Detect media type from base64 header or default to jpeg
 15476          media_type = "image/jpeg"
 15477          if img_b64.startswith("data:"):
 15478              header, data = img_b64.split(",", 1)
 15479              if "png" in header:
 15480                  media_type = "image/png"
 15481              elif "gif" in header:
 15482                  media_type = "image/gif"
 15483              elif "webp" in header:
 15484                  media_type = "image/webp"
 15485              img_b64 = data
 15486  
 15487          content_blocks.append({
 15488              "type": "image",
 15489              "source": {
 15490                  "type": "base64",
 15491                  "media_type": media_type,
 15492                  "data": img_b64,
 15493              }
 15494          })
 15495  
 15496      try:
 15497          # SEAM-ROUTED (P0): task="vision" — resolves to the haiku id today (Haiku-first,
 15498          # 3 Jul 2026); flipping TASK_MODEL's vision row back to sonnet re-arms the documented revert.
 15499          _sr = await asyncio.to_thread(
 15500              ai_provider.complete, [{"role": "user", "content": content_blocks}],
 15501              task="vision", max_tokens=2000, system=system_prompt,
 15502              provider=_ts_active_provider(), timeout=60)
 15503          _bc_in, _bc_out = _sr.in_tokens, _sr.out_tokens
 15504          # P2 — Tuppence covers the revenue side; log token spend so the cost
 15505          # dashboard sees it too (sweep 12 Jun 2026)
 15506          _log_ai_spend(req.seller_email, "/listings/batch-cards", "sonnet_vision", _bc_in, _bc_out)
 15507          raw = _sr.text.strip()
 15508          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 15509          raw = _re_match.sub(r"\s*```$", "", raw)
 15510          result = json.loads(raw)
 15511          drafts = result.get("drafts", [])
 15512  
 15513          # Sanitise each draft
 15514          clean_drafts = []
 15515          valid_conditions = {"mint", "near_mint", "excellent", "good", "fair", "poor"}
 15516          for d in drafts[:card_count]:
 15517              if isinstance(d, dict):
 15518                  clean_drafts.append({
 15519                      "title":            str(d.get("title", ""))[:120],
 15520                      "description":      str(d.get("description", ""))[:800],
 15521                      "price_suggestion": str(d.get("price_suggestion", ""))[:60],
 15522                      "condition":        d.get("condition", "good") if d.get("condition") in valid_conditions else "good",
 15523                      "category":         "Collectors",
 15524                      "city":             req.city,
 15525                      "suburb":           req.suburb or "",
 15526                  })
 15527  
 15528      except Exception as exc:
 15529          _log.error("ai-batch-cards: %s", exc)
 15530          raise HTTPException(status_code=500, detail="AI batch card listing failed — no Tuppence was charged") from exc
 15531  
 15532      _conn2 = database.get_db()
 15533      try:
 15534          remaining = _deduct_tuppence(_conn2, req.seller_email, 2, _bc_charge_desc)   # F2: charge on delivery
 15535          _conn2.commit()
 15536      finally:
 15537          _conn2.close()
 15538      _log.info("ai-batch-cards: seller=%s city=%s cards=%d drafts=%d",
 15539                req.seller_email, req.city, card_count, len(clean_drafts))
 15540      return {
 15541          "drafts":           clean_drafts,
 15542          "cards_processed":  card_count,
 15543          "tuppence_remaining": remaining,
 15544      }
 15545  
 15546  
 15547  
 15548  @app.get("/tuppence/history")
 15549  def get_tuppence_history(email: str, limit: int = 50, offset: int = 0):
 15550      """Return paginated tuppence transaction history with running balance."""
 15551      conn = database.get_db()
 15552      try:
 15553          # Verify user exists
 15554          user = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
 15555          if not user:
 15556              raise HTTPException(status_code=404, detail="User not found")
 15557  
 15558          total = conn.execute(
 15559              "SELECT COUNT(*) FROM transactions WHERE user_email=?", (email,)
 15560          ).fetchone()[0]
 15561  
 15562          # Get all rows ascending to compute running balances
 15563          all_rows = conn.execute(
 15564              "SELECT id, type, amount, description, created_at "
 15565              "FROM transactions WHERE user_email=? ORDER BY id ASC",
 15566              (email,)
 15567          ).fetchall()
 15568  
 15569          # Compute running balance_after for each row (cumulative sum)
 15570          running = 0
```

## KYC identity verification (vision, cost-guarded) — from bea_main.py

```
 10104  
 10105  
 10106  async def _sonnet_verify_identity(doc_url: str, claimed_name: str,
 10107                                     claimed_id: str, doc_type: str, email: str = "") -> dict:
 10108      """Call Sonnet vision to verify identity document.
 10109      SWAP POINT: replace this function with PaddleOCR/PassportEye for zero-token operation.
 10110      Self-contained cost guard (P2, 22 Jul 2026): checks the daily ceiling BEFORE the call
 10111      (raises HTTPException 429, same as every other paid endpoint) and logs spend itself
 10112      so this helper stays metered even if a future caller forgets to.
 10113      Returns: {verified(bool), confidence(float), extracted_name(str),
 10114                extracted_id(str), notes(str), model(str)}"""
 10115      if not ai_provider.any_lane_configured():
 10116          return {"verified": False, "confidence": 0.0, "extracted_name": "",
 10117                  "extracted_id": "", "notes": "AI verification unavailable — API key not set",
 10118                  "model": "none"}
 10119      _check_cost_ceiling(email)   # C1 — refuse if daily cost ceiling reached
 10120      try:
 10121          # Fetch the document image (KYC-SSRF-1: allowlisted host, no redirects, size-capped)
 10122          img_bytes = _fetch_kyc_document(doc_url)
 10123          img_b64 = base64.standard_b64encode(img_bytes).decode()
 10124          # Detect media type
 10125          media_type = "image/jpeg"
 10126          if doc_url.lower().endswith(".png"):
 10127              media_type = "image/png"
 10128          elif doc_url.lower().endswith(".webp"):
 10129              media_type = "image/webp"
 10130  
 10131          # SEAM-ROUTED (P0, 17 Jul 2026): KYC vision call goes through ai_provider.complete()
 10132          # with task="sonnet" — same claude-sonnet-4-6 on the Anthropic path as the old SDK call.
 10133          prompt = f"""You are a document verification assistant for TrustSquare marketplace.
 10134  Examine this identity document image carefully.
 10135  
 10136  The seller claims:
 10137  - Full name: {claimed_name}
 10138  - ID/passport number: {claimed_id}
 10139  - Document type: {doc_type}
 10140  
 10141  Your task:
 10142  1. Extract the FULL NAME exactly as printed on the document
 10143  2. Extract the ID NUMBER / PASSPORT NUMBER exactly as printed
 10144  3. Determine if the claimed name matches the document name (allow for initials, middle names)
 10145  4. Determine if the claimed number matches the document number
 10146  
 10147  Respond ONLY with valid JSON in this exact format:
 10148  {{
 10149    "extracted_name": "<full name from document>",
 10150    "extracted_id": "<id/passport number from document>",
 10151    "name_match": <true/false>,
 10152    "id_match": <true/false>,
 10153    "confidence": <0.0-1.0>,
 10154    "document_appears_genuine": <true/false>,
 10155    "notes": "<any concerns or observations, empty string if none>"
 10156  }}
 10157  
 10158  If you cannot read the document clearly, set confidence below 0.5 and explain in notes."""
 10159  
 10160          _sr = ai_provider.complete(
 10161              [{
 10162                  "role": "user",
 10163                  "content": [
 10164                      {"type": "image", "source": {
 10165                          "type": "base64", "media_type": media_type, "data": img_b64
 10166                      }},
 10167                      {"type": "text", "text": prompt}
 10168                  ]
 10169              }],
 10170              task="sonnet", max_tokens=300,
 10171              provider=_ts_active_provider(), allow_fallback=False, timeout=120)   # KYC-PIN-1 (F3): ID docs never fan out to standby vendors
 10172          raw = _sr.text.strip()
 10173          # Parse JSON from response
 10174          json_match = re.search(r'\{[\s\S]*\}', raw)
 10175          if not json_match:
 10176              raise ValueError("No JSON in Sonnet response")
 10177          result = json.loads(json_match.group())
 10178          verified = (result.get("name_match") and result.get("id_match") and
 10179                      result.get("confidence", 0) >= 0.75 and
 10180                      result.get("document_appears_genuine", True))
 10181          _log_ai_spend(email, "/users/verify-identity", "sonnet_vision",
 10182                        getattr(_sr, "in_tokens", None), getattr(_sr, "out_tokens", None))
 10183          return {
 10184              "verified": bool(verified),
 10185              "confidence": float(result.get("confidence", 0)),
 10186              "extracted_name": result.get("extracted_name", ""),
 10187              "extracted_id": result.get("extracted_id", ""),
 10188              "notes": result.get("notes", ""),
 10189              "model": SONNET_MODEL,
 10190          }
 10191      except HTTPException:
 10192          raise
 10193      except Exception as e:
```

## /admin/ai-restore + /flags provider block — from bea_main.py

```
 12974      return {"services": out, "checked_at": datetime.utcnow().isoformat() + "Z"}
 12975  
 12976  @app.post("/admin/ai-restore")
 12977  def admin_ai_restore(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12978      """P2a: MANUAL restore — the ONLY path back to traffic for a banned (T3) lane
 12979      (David's ruling 31 Jul: dropouts auto-recover, bans wait for the operator)."""
 12980      _p = ((payload or {}).get("provider") or "").strip()
 12981      _t = ((payload or {}).get("task") or "").strip() or None
 12982      if _p not in ai_provider.ADAPTERS:
 12983          raise HTTPException(status_code=400, detail="unknown provider")
 12984      try:
 12985          import ai_breaker as _brk
 12986          n = _brk.restore(_p, _t, who="dashboard-admin")
 12987          _log.warning("AI-BREAKER manual restore: %s/%s (%d rows)", _p, _t or "ALL", n)
 12988          return {"restored": n, "provider": _p, "task": _t or "ALL"}
 12989      except Exception as e:
 12990          raise HTTPException(status_code=500, detail="restore failed: " + str(e)[:120]) from e
 12991  
 12992  @app.post("/admin/ai-test")   # AITEST-ROUTE-1 (17 Jul, found live by David's demo): decorator was pasted onto demand_sweep; real tester was never registered
 12993  def admin_ai_test(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12994      """David-only: run a tiny prompt through the ACTIVE provider via the ai_provider seam
 12995      (full translate+call+parse path). Lets the Page-4 switch be tested live against either
 12996      provider without touching the 15 production call sites. Returns the text + which provider/model answered."""
 12997      _req_prov=((payload or {}).get("provider") or "").strip()   # P1: optional explicit provider
 12998      if _req_prov and _req_prov not in ai_provider.ADAPTERS:
 12999          raise HTTPException(status_code=400, detail="unknown provider: "+_req_prov[:40])
 13000      try:
 13001          import ai_provider as _ap
 13002          prov=_req_prov or _ts_active_provider()
 13003          prompt=((payload or {}).get("prompt") or "Reply with exactly: TrustSquare AI provider test OK.").strip()
 13004          r=_ap.complete([{"role":"user","content":prompt}], task="haiku", max_tokens=40, provider=prov)
 13005          return {"ok": bool(r.ok), "provider": r.provider, "model": r.model,
 13006                  "text": (r.text or "")[:400], "in_tokens": r.in_tokens, "out_tokens": r.out_tokens}
 13007      except Exception as e:
 13008          raise HTTPException(status_code=500, detail="ai-test failed: "+str(e)[:160]) from e
 13009  
 13010  
 13011  class _FlagsUpdate(BaseModel):
 13012      mode:          Optional[str]  = None
 13013      verified_tier: Optional[bool] = None
 13014      videos:        Optional[bool] = None
 13015      data_ops:      Optional[bool] = None
 13016      data_places:   Optional[bool] = None
 13017      data_flights:  Optional[bool] = None
 13018      data_mapbox:   Optional[bool] = None
 13019      p_heritage:    Optional[bool] = None
 13020      p_expedition:  Optional[bool] = None
 13021      p_weekend:     Optional[bool] = None
 13022      # BIT safe-state flags (Mitigator-writable; see §13.1)
 13023      ai_example_enabled:    Optional[bool] = None
 13024      auth_fail_closed:      Optional[bool] = None
 13025      tuppence_burn_enabled: Optional[bool] = None
 13026      ai_active:             Optional[str]  = None  # AI provider seam: 'anthropic' | 'openai' | 'scaleway' (Page-4 switch)
 13027      ai_active_override:    Optional[str]  = None  # MANUAL PIN: provider = pin (TTL decay) | '' = unpin (1 Aug 2026)
 13028      fault_report:          Optional[bool] = None  # MAINT-B1b: in-app tester fault intake visible
 13029  
 13030  def _flags_payload(d):
 13031      def b(k): return bool(d.get(k, 0))
 13032      live = (d.get("mode", "launch") == "live")
 13033      return {
 13034          "mode": d.get("mode", "launch"),
 13035          "verified_tier": b("verified_tier"), "videos": b("videos"),
 13036          "fault_report": b("fault_report"),
 13037          "data": {"ops": b("data_ops"), "places": b("data_places"),
 13038                   "flights": b("data_flights"), "mapbox": b("data_mapbox")},
 13039          "planners": {"heritage": b("p_heritage"), "expedition": b("p_expedition"),
 13040                       "weekend": b("p_weekend")},
 13041          "effective": {
 13042              "verified_visible":    live and b("verified_tier"),
 13043              "videos_visible":      b("videos"),  # decoupled from live mode (David 29 Jun): dashboard videos toggle controls it on its own; verified/paid-feed gates stay live-gated
 13044              "heritage_verified":   live and b("verified_tier") and b("p_heritage"),
 13045              "expedition_verified": live and b("verified_tier") and b("p_expedition"),
 13046              "weekend_verified":    live and b("verified_tier") and b("p_weekend"),
 13047          },
 13048          "bit_flags": {
 13049              "ai_example_enabled":    bool(d.get("ai_example_enabled", 1)),
 13050              "auth_fail_closed":      bool(d.get("auth_fail_closed", 0)),
 13051              "tuppence_burn_enabled": bool(d.get("tuppence_burn_enabled", 1)),
 13052          },
 13053          "ai_provider": {
 13054              # effective = the lane calls actually use RIGHT NOW (pin-aware); standing = the
 13055              # auto/default lane the system returns to when the pin decays.
 13056              "active": _ts_active_provider(),   # pin-aware effective lane
 13057              "standing": d.get("ai_active", "anthropic"),
 13058              "override": ({"provider": _TS_AI_CACHE["override"], "expires_at": _TS_AI_CACHE["expires"]}
 13059                            if _TS_AI_CACHE.get("override") else None),
 13060              "override_ttl_hours": AI_OVERRIDE_TTL_HOURS,
 13061              "funnel": _ts_funnel_snapshot(),
 13062              # FAIL-OPEN here too (FLAGS-BRK-1, 1 Aug): a missing/broken breaker module must
 13063              # never take /flags down — the card degrades, the platform does not.
 13064              "breaker": _ts_breaker_safe("snapshot"),
 13065              "drill": _ts_breaker_safe("drill"),
 13066              # which providers have a REAL adapter wired (vs stub) — Page 4 greys out the stubs
 13067              "available": {"anthropic": bool(ANTHROPIC_API_KEY), "openai": bool(ai_provider.envkey("OPENAI_API_KEY")),
 13068                            "scaleway": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY"))},
 13069              # P1: ordered provider cards for the NEW dashboard UI (old card keeps reading active/available above)
 13070              "providers": [
 13071                  {"id": "anthropic", "label": "Anthropic (Claude)", "family": "us", "jurisdiction": "US",
 13072                   "available": bool(ANTHROPIC_API_KEY),
 13073                   "models": ai_provider.TASK_MODEL.get("anthropic", {})},
 13074                  {"id": "scaleway", "label": "Scaleway EU", "family": "open", "jurisdiction": "EU · Paris",
 13075                   "available": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")),
 13076                   "models": ai_provider.TASK_MODEL.get("scaleway", {})},
 13077                  {"id": "openai", "label": "OpenAI (GPT-5.6)", "family": "us", "jurisdiction": "US",
 13078                   "available": bool(ai_provider.envkey("OPENAI_API_KEY")),
 13079                   "models": ai_provider.TASK_MODEL.get("openai", {})},
 13080              ],
 13081          },
 13082          "updated_at": d.get("updated_at", ""),
 13083      }
 13084  
 13085  def _ts_breaker_safe(what):
 13086      try:
 13087          import ai_breaker as _b
 13088          if what == "snapshot": return _b.snapshot()
 13089          return sorted(_b.drill_banned()) or None
 13090      except Exception:
 13091          return None
 13092  
 13093  _TS_FUNNEL_CACHE = {"mtime": None, "data": None}
 13094  def _ts_funnel_snapshot():
 13095      """The +1 card's funnel strip: ORDER AND GATE-TYPES ONLY (David 1 Aug 2026 — no numbers).
 13096      Read from ai_funnel_snapshot.json, generated by scripts/price_truth.py --snapshot (ONE
 13097      ranking engine); absent file -> None, dashboard shows nothing. Cached on mtime."""
 13098      import os as _os
 13099      p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ai_funnel_snapshot.json")
 13100      try:
 13101          mt = _os.path.getmtime(p)
 13102          if _TS_FUNNEL_CACHE["mtime"] != mt:
 13103              with open(p, encoding="utf-8") as fh:
 13104                  _TS_FUNNEL_CACHE.update(mtime=mt, data=json.load(fh))
 13105          return _TS_FUNNEL_CACHE["data"]
 13106      except Exception:
 13107          return None
 13108  
 13109  @app.get("/flags")
 13110  def get_flags():
 13111      """Public — buyer app + dashboard read launch-switch state. Safe default = launch/free-only."""
 13112      conn = database.get_db()
 13113      try:
 13114          row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
 13115      finally:
 13116          conn.close()
 13117      return _flags_payload(dict(row) if row else {})
 13118  
 13119  @app.post("/admin/flags")
 13120  def set_flags(upd: _FlagsUpdate, _admin=Depends(_require_admin)):
 13121      """Admin (JWT) — flip the launch switch. Writes the singleton row, returns full state."""
 13122      data = upd.dict(exclude_unset=True)
 13123      sets, vals = [], []
```

## /admin/ai-spend summary endpoint — from bea_main.py

```
  5228  # ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
  5229  
  5230  @app.get("/admin/ai-spend/summary")
  5231  def admin_ai_spend_daily_summary(_admin=Depends(_require_admin_or_key)):
  5232      """Live AI-spend summary for the nightly cost-compliance sweep (P2, 11 Jun 2026).
  5233      Returns today's and 7-day spend, the configured ceilings, and a 7-day
  5234      per-endpoint/model breakdown. Read-only; $0; admin key required."""
  5235      conn = database.get_db()
  5236      try:
  5237          today = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
  5238          week = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
  5239          t = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  5240                           "FROM ai_spend_log WHERE logged_at >= ?", (today,)).fetchone()
  5241          w = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  5242                           "FROM ai_spend_log WHERE logged_at >= ?", (week,)).fetchone()
  5243          cfg = conn.execute("SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  5244                             "FROM ai_spend_config WHERE id = 1").fetchone()
  5245          by_ep = conn.execute(
  5246              "SELECT endpoint, model, COALESCE(SUM(est_cost_usd),0) AS usd, COUNT(*) AS calls, "
  5247              "SUM(cost_is_real) AS real_rows FROM ai_spend_log WHERE logged_at >= ? "
  5248              "GROUP BY endpoint, model ORDER BY usd DESC LIMIT 25", (week,)).fetchall()
  5249      finally:
  5250          conn.close()
  5251      return {
  5252          "today_usd": round(t["u"], 4), "today_calls": t["n"],
  5253          "week_usd": round(w["u"], 4), "week_calls": w["n"],
  5254          "daily_user_ceiling_usd": (cfg["daily_user_ceiling_usd"] if cfg else 0) or 0,
  5255          "daily_platform_ceiling_usd": (cfg["daily_platform_ceiling_usd"] if cfg else 0) or 0,
  5256          "ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
  5257                              else "platform ceiling is 0/unset — AI spend is UNCAPPED"),
  5258          "by_endpoint": [{"endpoint": r["endpoint"], "model": r["model"],
  5259                           "usd": round(r["usd"], 4), "calls": r["calls"],
  5260                           "estimated_rows": r["calls"] - (r["real_rows"] or 0)} for r in by_ep],
  5261      }
  5262  
  5263  
  5264  @app.post("/admin/migrate-photos")
  5265  def migrate_photos(_admin=Depends(_require_admin_or_key)):
  5266      """Migrate existing local photos to Hetzner Object Storage.
  5267      Idempotent — skips listings already pointing to an S3 URL.
  5268      Does NOT delete local files.
  5269      Returns: { migrated, failed, skipped }
  5270      """
  5271      if not _S3_CONFIGURED:
  5272          raise HTTPException(status_code=503, detail="Object Storage not configured — set HETZNER_S3_* env vars")
  5273      conn = database.get_db()
  5274      rows = conn.execute(
  5275          "SELECT id, thumb_url, medium_url FROM listings WHERE thumb_url LIKE '/media/%'"
  5276      ).fetchall()
  5277      migrated = failed = skipped = 0
  5278      for row in rows:
  5279          listing_id  = row["id"]
  5280          thumb_path  = row["thumb_url"]  or ""
  5281          medium_path = row["medium_url"] or ""
  5282          if not thumb_path.startswith("/media/"):
```

## Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop — from bea_main.py

```
 17274  
 17275  
 17276  # ── SCOREBOARD-1 (3 Aug 2026): the silent scoreboard agent, nightly ──────────
 17277  # The SLOW-signal half of the failover programme (fast signals = ai_breaker):
 17278  # probes every configured lane x task tier each night at 03:33 SAST (01:33 UTC,
 17279  # after the 03:17 backup), stores history in ai_scoreboard_probes (primary DB,
 17280  # so it rides the backup lanes), writes the rolling 90-day ranking to
 17281  # ai_scoreboard.json. Quality is a GATE not a weight (golden-set registry).
 17282  # Spend-gated OFF by default — launch_switches.scoreboard_enabled=1
 17283  # (enable_scoreboard.bat) is David's explicit click. Import-guarded and
 17284  # exception-walled: a scoreboard failure can never hurt the app.
 17285  try:
 17286      import ai_scoreboard as _ts_scoreboard
 17287  except Exception as _ts_sb_err:
 17288      _ts_scoreboard = None
 17289      print("SCOREBOARD-1: module not importable (%s) — nightly probes off" % _ts_sb_err)
 17290  
 17291  if _ts_scoreboard is not None:
 17292      @app.on_event("startup")
 17293      async def _ts_scoreboard_nightly():
 17294          async def _sb_loop():
 17295              while True:
 17296                  _now = datetime.now(timezone.utc)
 17297                  _nxt = _now.replace(hour=1, minute=33, second=0, microsecond=0)
 17298                  if _nxt <= _now:
 17299                      _nxt += timedelta(days=1)
 17300                  await asyncio.sleep(max(60.0, (_nxt - _now).total_seconds()))
 17301                  try:
 17302                      await asyncio.get_running_loop().run_in_executor(
 17303                          None, _ts_scoreboard.run_nightly)
 17304                  except Exception as _sb_e:
 17305                      print("SCOREBOARD-1 nightly error: %s" % _sb_e)
 17306          asyncio.get_running_loop().create_task(_sb_loop())
 17307  
 17308  
 17309  # ── HEARTBEAT-1 (5 Aug 2026, David's F5 ruling: live NOW, confidence before launch) ──
 17310  # P2c idle-recovery heartbeat per AI_AUTO_FAILOVER_P2_DESIGN §6: every 60 s, if any
 17311  # breaker row is eligible (tripped/half_open, probe window open), claim and send ONE
 17312  # direct probe — one per tick TOTAL, round-robin, so a bad night can never multiply
 17313  # cost. Text ping only (~$0.00002); T3 rows carry hourly probe_after, so bans probe
 17314  # hourly. Spend is logged like all spend. Fail-open: any error waits for the next tick.
 17315  @app.on_event("startup")
 17316  async def _ts_breaker_heartbeat():
 17317      async def _hb_loop():
 17318          _rr = 0
 17319          while True:
 17320              await asyncio.sleep(60)
 17321              try:
 17322                  import ai_breaker as _hb_brk
 17323                  if getattr(_hb_brk, "_get_db", None) is None:
 17324                      continue   # breaker unattached — nothing to probe
 17325                  _hb_conn = database.get_db()
 17326                  try:
 17327                      _rows = _hb_conn.execute(
 17328                          "SELECT provider, task FROM ai_breaker "
 17329                          "WHERE state IN ('tripped','half_open') "
 17330                          "AND (probe_after IS NULL OR probe_after <= ?) "
 17331                          "ORDER BY provider, task",
 17332                          (datetime.utcnow().isoformat(timespec="seconds"),)).fetchall()
 17333                  finally:
 17334                      _hb_conn.close()
 17335                  if not _rows:
 17336                      continue
 17337                  _row = _rows[_rr % len(_rows)]; _rr += 1
 17338                  _p, _t = _row["provider"], _row["task"]
 17339                  if not _hb_brk.claim_probe(_p, _t):
 17340                      continue   # someone else holds the half-open lease
 17341                  _r = await asyncio.to_thread(
 17342                      ai_provider.complete, [{"role": "user", "content": "ping"}],
 17343                      task=_t, max_tokens=8, provider=_p, probe=True, timeout=20)
 17344                  _log_ai_spend("system:heartbeat", "/breaker/heartbeat", _t,
 17345                                _r.in_tokens, _r.out_tokens)
 17346              except Exception as _hb_e:
 17347                  print("HEARTBEAT-1 error: %s" % _hb_e)
 17348      asyncio.get_running_loop().create_task(_hb_loop())
```

## AI Services help card copy (user-facing, F3 vendor-neutral fix) — from marketsquare.html

```
  1368            <div style="font-size:22px;flex-shrink:0;">&#10024;</div>
  1369            <div style="flex:1;">
  1370              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Listing Rewrite <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1371              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI rewrites your title and description using current SA market language and buyer psychology &mdash; pre-fills your edit form to review and save.</div>
  1372              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; Edit &rarr; "&#10024; Rewrite"</div>
  1373            </div>
  1374            <div style="font-size:12px;font-weight:700;color:#d97706;background:#fef3c7;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1375          </div>
  1376          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1377            <div style="font-size:22px;flex-shrink:0;">&#128269;</div>
  1378            <div style="flex:1;">
  1379              <div style="font-size:13px;font-weight:700;color:var(--text);">Why No Intros? AI Audit <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1380              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI reviews your listing &mdash; title, description, price and trust score &mdash; then gives you 3 specific fixes to attract more buyers right now.</div>
  1381              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; Edit &rarr; "&#128269; Why No Intros?"</div>
  1382            </div>
  1383            <div style="font-size:12px;font-weight:700;color:#059669;background:#d1fae5;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1384          </div>
  1385          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1386            <div style="font-size:22px;flex-shrink:0;">&#127183;</div>
  1387            <div style="flex:1;">
  1388              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Batch Card Lister <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; per run</span></div>
  1389              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Upload photos of many collector cards at once and our AI drafts a separate listing for each &mdash; title, set, condition and a suggested price.</div>
  1390              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; + Sell &rarr; Collector cards &rarr; "Batch Cards"</div>
  1391            </div>
  1392            <div style="font-size:12px;font-weight:700;color:#5b21b6;background:#ede9fe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">bulk</div>
  1393          </div>
  1394        </div>
  1395        <!-- Buyer AI services -->
  1396        <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-3);margin-bottom:8px;">For buyers &middot; on any listing</div>
  1397        <div style="display:flex;flex-direction:column;gap:8px;">
  1398          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1399            <div style="font-size:22px;flex-shrink:0;">&#128161;</div>
  1400            <div style="flex:1;">
  1401              <div style="font-size:13px;font-weight:700;color:var(--text);">Is This a Fair Price? <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1402              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI compares the asking price to current SA market rates and gives a verdict &mdash; fair, above or below market &mdash; plus a suggested fair range.</div>
  1403              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; "&#128161; Is this a fair price?"</div>
  1404            </div>
  1405            <div style="font-size:12px;font-weight:700;color:#1d4ed8;background:#dbeafe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1406          </div>
  1407          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1408            <div style="font-size:22px;flex-shrink:0;">&#128200;</div>
  1409            <div style="flex:1;">
  1410              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Yield Estimate <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1411              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI estimates rental yield and return for a property or accommodation listing using current SA market data. Sellers can run it from Edit too.</div>
  1412              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Property / accommodation listing &rarr; "&#128200; Investor Yield Calculator"</div>
  1413            </div>
  1414            <div style="font-size:12px;font-weight:700;color:#0e7490;background:#cffafe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1415          </div>
  1416        </div>
  1417        <div style="font-size:11px;color:var(--text-3);margin-top:12px;padding:10px 12px;background:var(--surface-2);border-radius:8px;">
  1418          <strong>Non-refundable policy:</strong> AI services are charged on use. If the AI call fails due to a server error, no Tuppence is deducted. Results are provided as-is for guidance only.
  1419        </div>
  1420        </div>
  1421      </details>
  1422  
```

## VIZ map legend naming Sonnet (F4 context: display text, not a call site) — from dashboard.server.html

```
   980       App categories:  Listings/Adverts purple · Trust&Safety green · Search blue ·
   981                        Tuppence cyan · Ops amber
   982       Task tiers:      haiku sky · sonnet violet · vision pink · triage gold
   983       Vendor lanes:    Anthropic terracotta · OpenAI green · Scaleway purple
   984       Status:          ok green · warn amber · fail red · no-key grey            */
   985    var CAT={listings:'#8b5cf6',trust:'#10b981',search:'#3b82f6',tuppence:'#06b6d4',ops:'#f59e0b'};
   986    var TIER={haiku:'#38bdf8',sonnet:'#a78bfa',vision:'#f472b6',triage:'#fbbf24'};
   987    var LANE={anthropic:'#e07a5f',openai:'#10a37f',scaleway:'#8b5cf6'};
   988    var STAT={ok:'#22c55e',warn:'#eab308',fail:'#ef4444',nokey:'#6b7280'};
   989  
   990    /* ════════ 1 · AI PROVIDERS MAP ════════ */
   991    window.msVizBuildAI=function(){
   992      var d=window._apv3||{active:'anthropic',standing:'anthropic',override:null,providers:[]};
   993      var avail={}; (d.providers||[]).forEach(function(p){avail[p.id]=!!p.available;});
   994      if(!(d.providers||[]).length){avail={anthropic:true};}
   995      var groups=[
   996        {id:'listings',name:'LISTINGS &amp; ADVERTS',c:CAT.listings,items:[
   997          {n:'Advert coach &amp; super-adverts',t:['sonnet','haiku']},
   998          {n:'Mode B anonymity rewrite',t:['sonnet']},
   999          {n:'Import photo scan',t:['sonnet','vision']}]},
  1000        {id:'trust',name:'TRUST &amp; SAFETY',c:CAT.trust,items:[
  1001          {n:'KYC ID verification',t:['sonnet','vision']},
  1002          {n:'Photo checks — orientation &middot; anonymity',t:['vision']}]},
  1003        {id:'search',name:'SEARCH &amp; DISCOVERY',c:CAT.search,items:[
  1004          {n:'Search interpretation',t:['haiku']}]},
  1005        {id:'tuppence',name:'TUPPENCE AI SERVICES',c:CAT.tuppence,items:[
  1006          {n:'Tier 1 &amp; 2 buyer/seller services',t:['haiku','sonnet']}]},
  1007        {id:'ops',name:'OPS &amp; ADMIN',c:CAT.ops,items:[
  1008          {n:'Email triage',t:['triage']},
  1009          {n:'Provider self-test (this dashboard)',t:['haiku']}]}
  1010      ];
  1011      var s='';
  1012      s+='<defs><filter id="msvGlow" x="-40%" y="-40%" width="180%" height="180%">'+
  1013         '<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';
  1014      /* column headings */
  1015      s+=txt(180,32,'APP FEATURES',12,'#64748b',800,'middle','2px');
  1016      s+=txt(487,32,'TASK TIERS',12,'#64748b',800,'middle','2px');
  1017      s+=txt(770,32,'THE SEAM',12,'#64748b',800,'middle','2px');
  1018      s+=txt(1170,32,'VENDOR LANES',12,'#64748b',800,'middle','2px');
  1019  
  1020      /* tier chips */
  1021      var tiers={haiku:{y:170,d:'everyday text'},sonnet:{y:290,d:'heavy reasoning'},vision:{y:410,d:'image analysis'},triage:{y:530,d:'inbox sorting'}};
  1022      Object.keys(tiers).forEach(function(k){var t=tiers[k];
  1023        s+=box(432,t.y-26,112,52,TIER[k],'#0d1526',26);
  1024        s+=txt(488,t.y-2,k,14,TIER[k],800,'middle');
```

## INTRO-RELAY-1: alias mint, forward, relay endpoint (Option B) — from bea_main.py

```
  4530  
  4531  
  4532  # ══ INTRO-RELAY-1 (5 Aug 2026) — masked-alias introduction relay (Option B) ══
  4533  # David's doctrine: "Nothing of the customer's leaves TrustSquare except a consented,
  4534  # revocable email channel — never the address itself. We disclose nothing; we relay."
  4535  # Dark until launch_switches.intro_relay = 1 (fail-closed). Spec:
  4536  # Records/INTRO_RELAY_BUILD_SPEC.md. Inbound rides Cloudflare Email Routing via the
  4537  # Worker (ops/cloudflare/intro_relay_worker.js); outbound rides the Resend lane.
  4538  RELAY_DOMAIN = os.getenv("RELAY_DOMAIN", "relay.trustsquare.co")
  4539  RELAY_INBOUND_SECRET = os.getenv("RELAY_INBOUND_SECRET", "")
  4540  _RELAY_MAX_BODY = 100_000        # relayed text cap; attachments are v2, dropped loudly
  4541  _RELAY_TTL_DAYS = int(os.getenv("RELAY_TTL_DAYS", "30"))
  4542  
  4543  
  4544  def _intro_relay_enabled() -> bool:
  4545      """Read the launch switch. Fail-closed on any error (mirror of _fault_report_enabled)."""
  4546      try:
  4547          conn = database.get_db()
  4548          try:
  4549              row = conn.execute("SELECT intro_relay FROM launch_switches WHERE id = 1").fetchone()
  4550          finally:
  4551              conn.close()
  4552          return bool(row and row["intro_relay"])
  4553      except Exception as exc:
  4554          _log.error("intro_relay flag read failed: %s", exc)
  4555          return False
  4556  
  4557  
  4558  def _mint_relay_aliases(conn, intro_id: int, buyer_email: str, seller_email: str):
  4559      """Create the two masked aliases for an accepted intro. Random, unguessable, no PII
  4560      in the string. buyer_alias MASKS the buyer (mail sent to it reaches the buyer);
  4561      each party is GIVEN the counterparty's alias to write to."""
  4562      import secrets as _sec
  4563      b_alias = "intro-%s@%s" % (_sec.token_hex(6), RELAY_DOMAIN)
  4564      s_alias = "intro-%s@%s" % (_sec.token_hex(6), RELAY_DOMAIN)
  4565      now = datetime.now(timezone.utc)
  4566      exp = (now + timedelta(days=_RELAY_TTL_DAYS)).isoformat(timespec="seconds")
  4567      for alias, party, real, counter in (
  4568              (b_alias, "buyer", buyer_email, s_alias),
  4569              (s_alias, "seller", seller_email, b_alias)):
  4570          conn.execute(
  4571              "INSERT INTO intro_relay_aliases "
  4572              "(alias, intro_id, party, real_email, counter_alias, created_at, expires_at) "
  4573              "VALUES (?,?,?,?,?,?,?)",
  4574              (alias, intro_id, party, (real or "").strip().lower(), counter,
  4575               now.isoformat(timespec="seconds"), exp))
  4576      return b_alias, s_alias
  4577  
  4578  
  4579  def _relay_sanitize_subject(s: str) -> str:
  4580      """One line, header-injection-proof, bounded."""
  4581      return " ".join((s or "").replace("\r", " ").replace("\n", " ").split())[:200]
  4582  
  4583  
  4584  def _relay_forward(to_real: str, from_alias: str, subject: str, body: str) -> bool:
  4585      """Forward one relayed message via the Resend lane. From AND Reply-To are the
  4586      sender's ALIAS — never a real address — so the reply loops back through the
  4587      curtain. Text only in v1. Never raises."""
  4588      to_clean = parseaddr(to_real)[1]
  4589      if not to_clean:
  4590          _log.warning("INTRO-RELAY-1 forward skipped — bad recipient")
  4591          return False
  4592      key = os.getenv("RESEND_API_KEY", "")
  4593      if not key:
  4594          _log.error("INTRO-RELAY-1 forward skipped — RESEND_API_KEY not set")
  4595          return False
  4596      try:
  4597          import httpx as _hx
  4598          r = _hx.post("https://api.resend.com/emails",
  4599              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
  4600              json={"from": "TrustSquare Intro <%s>" % from_alias,
  4601                    "to": [to_clean],
  4602                    "subject": _relay_sanitize_subject(subject) or "TrustSquare introduction",
  4603                    "text": (body or "")[:_RELAY_MAX_BODY],
  4604                    "reply_to": from_alias},
  4605              timeout=20)
  4606          if r.status_code in (200, 201):
  4607              return True
  4608          _log.error("INTRO-RELAY-1 forward HTTP %s: %s", r.status_code, r.text[:200])
  4609          return False
  4610      except Exception as exc:
  4611          _log.error("INTRO-RELAY-1 forward failed: %s", exc)
  4612          return False
  4613  
  4614  
  4615  def _relay_send_intro_notes(intro_id: int, buyer_email: str, buyer_name: str,
  4616                              seller_email: str, listing_title: str,
  4617                              b_alias: str, s_alias: str) -> None:
  4618      """Introduce both parties through the curtain. Each note arrives FROM the
  4619      counterparty's alias, so simply replying starts the relayed conversation.
  4620      Background task — never raises."""
  4621      try:
  4622          t = (listing_title or "your listing")[:80]
  4623          privacy = ("Reply to THIS email to talk. Your email address stays private: messages "
  4624                     "travel through TrustSquare's introduction relay and each of you sees only "
  4625                     "a TrustSquare address. The channel stays open %d days.\n\n"
  4626                     "— TrustSquare · anonymous until you choose otherwise" % _RELAY_TTL_DAYS)
  4627          note_seller = ("Good news — %s asked to be introduced about \"%s\" and the "
  4628                         "introduction is now open.\n\n%s" % (buyer_name or "a buyer", t, privacy))
  4629          note_buyer = ("Good news — the seller accepted your introduction request about "
  4630                        "\"%s\".\n\n%s" % (t, privacy))
  4631          # the seller's note arrives FROM the buyer's alias; the buyer's FROM the seller's
  4632          _relay_forward(seller_email, b_alias, "Introduction: %s" % t, note_seller)
  4633          _relay_forward(buyer_email, s_alias, "You're introduced: %s" % t, note_buyer)
  4634          _log.info("INTRO-RELAY-1 notes sent for intro #%s (aliases only)", intro_id)
  4635      except Exception as exc:
  4636          _log.error("INTRO-RELAY-1 notes failed for intro #%s: %s", intro_id, exc)
  4637  
  4638  
  4639  class _RelayInbound(BaseModel):
  4640      to_alias: str
  4641      from_addr: str
  4642      subject: str = ""
  4643      body: str = ""
  4644  
  4645  
  4646  @app.post("/intro/relay")
  4647  def intro_relay_inbound(req: _RelayInbound, x_relay_secret: str = Header(default="")):
  4648      """Receive one relayed message from the Cloudflare Email Worker and forward it to
  4649      the hidden counterparty. Enrolled-parties-only: the sender's address must match the
  4650      counter-alias's real_email — a stranger who guesses an alias is rejected and the
  4651      real addresses never move. No outbound fetch exists on this path (nothing
  4652      SSRF-shaped). Auth: X-Relay-Secret (RELAY_INBOUND_SECRET)."""
  4653      if not _intro_relay_enabled():
  4654          raise HTTPException(status_code=503, detail="The introduction relay is not open.")
  4655      if not RELAY_INBOUND_SECRET or x_relay_secret != RELAY_INBOUND_SECRET:
  4656          raise HTTPException(status_code=401, detail="Invalid relay secret")
  4657      to_alias = (req.to_alias or "").strip().lower()
  4658      from_addr = (parseaddr(req.from_addr or "")[1] or "").strip().lower()
  4659      if not to_alias or not from_addr:
  4660          raise HTTPException(status_code=400, detail="to_alias and from_addr are required")
  4661      conn = database.get_db()
  4662      try:
  4663          now = datetime.now(timezone.utc).isoformat(timespec="seconds")
  4664          row = conn.execute("SELECT * FROM intro_relay_aliases WHERE alias=?",
  4665                             (to_alias,)).fetchone()
  4666          if not row or not row["active"] or row["expires_at"] < now:
  4667              raise HTTPException(status_code=404, detail="This introduction channel is closed.")
  4668          counter = conn.execute("SELECT * FROM intro_relay_aliases WHERE alias=?",
  4669                                 (row["counter_alias"],)).fetchone()
  4670          if not counter or not counter["active"]:
  4671              raise HTTPException(status_code=404, detail="This introduction channel is closed.")
  4672          if from_addr != counter["real_email"]:
  4673              _log.warning("INTRO-RELAY-1 rejected non-enrolled sender on %s", to_alias)
  4674              raise HTTPException(status_code=403,
  4675                                  detail="Only the introduced parties can use this channel.")
  4676      finally:
  4677          conn.close()
  4678      ok = _relay_forward(row["real_email"], counter["alias"],
  4679                          req.subject, (req.body or "")[:_RELAY_MAX_BODY])
  4680      if not ok:
  4681          raise HTTPException(status_code=502, detail="The relay could not deliver this message.")
  4682      return {"relayed": True}
  4683  
  4684  
  4685  @app.post("/intros")
  4686  def create_intro(intro: IntroRequest, background_tasks: BackgroundTasks,
  4687                   ts_user: str = Cookie(default=None)):
  4688      _bind_charged_email(intro.buyer_email, ts_user, "create-intro")   # ACCOUNT-BIND-1
  4689      conn = database.get_db()
  4690      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro.listing_id,)).fetchone()
  4691      if not listing:
  4692          conn.close()
  4693          raise HTTPException(status_code=404, detail="Listing not found")
  4694      listing_status = listing["listing_status"] if listing["listing_status"] else "live"
  4695      if listing_status != "live":
  4696          conn.close()
  4697          raise HTTPException(status_code=409, detail=f"Listing is not available for introductions (status: {listing_status})")
  4698      # Self-intro guard — buyer cannot intro their own listing
  4699      if listing["seller_email"] and intro.buyer_email and        listing["seller_email"].lower() == intro.buyer_email.lower():
```

## ACCOUNT-BIND-1: session helpers + bind — from bea_main.py

```
  4472  
  4473  
  4474  # ══ ACCOUNT-BIND-1 (5 Aug 2026) — charged identity is PROVEN, never asserted ══
  4475  # Peer round-2 BLOCKER (F1), David's Option A ruling: the account an action charges
  4476  # comes from the authenticated session (ts_user cookie, set by /auth/verify after a
  4477  # magic-link proof of email possession), never from a caller-typed email behind the
  4478  # public app key. Dark until launch_switches.account_binding = 1; while OFF, every
  4479  # mismatch is shadow-logged so the flip is informed, not hopeful.
  4480  
  4481  def _account_binding_enabled() -> bool:
  4482      """Read the launch switch. Fail-closed on any error."""
  4483      try:
  4484          conn = database.get_db()
  4485          try:
  4486              row = conn.execute("SELECT account_binding FROM launch_switches WHERE id = 1").fetchone()
  4487          finally:
  4488              conn.close()
  4489          return bool(row and row["account_binding"])
  4490      except Exception as exc:
  4491          _log.error("account_binding flag read failed: %s", exc)
  4492          return False
  4493  
  4494  
  4495  def _session_email(ts_user):
  4496      """Proven email from the ts_user session cookie (JWT scope 'user'), or None.
  4497      The cookie is set ONLY by /auth/verify after a magic-link click — possession of
  4498      the inbox is the proof. The shared review token has scope 'review' and can never
  4499      pass this check even though it rides the same secret."""
  4500      if not ts_user:
  4501          return None
  4502      try:
  4503          p = _pyjwt.decode(ts_user, _JWT_SECRET, algorithms=[_JWT_ALGO])
  4504          if p.get("scope") != "user":
  4505              return None
  4506          return ((p.get("sub") or "").strip().lower()) or None
  4507      except Exception:
  4508          return None
  4509  
  4510  
  4511  def _bind_charged_email(passed_email, ts_user, ctx=""):
  4512      """Enforce (flag ON) or shadow-log (flag OFF) that the charged account is the
  4513      session's proven identity. Returns the canonical charged email. Flag OFF is
  4514      byte-identical to today's behaviour apart from one log line."""
  4515      passed = (passed_email or "").strip().lower()
  4516      sess = _session_email(ts_user)
  4517      if not _account_binding_enabled():
  4518          if not sess:
  4519              _log.info("ACCOUNT-BIND-1 shadow: no session (ctx=%s passed=%s)", ctx, passed)
  4520          elif passed and sess != passed:
  4521              _log.warning("ACCOUNT-BIND-1 shadow MISMATCH (ctx=%s): session=%s passed=%s",
  4522                           ctx, sess, passed)
  4523          return passed
  4524      if not sess:
  4525          raise HTTPException(status_code=401, detail="Please sign in to use this feature.")
  4526      if passed and passed != sess:
  4527          raise HTTPException(status_code=403,
  4528                              detail="This action can only be performed on your own account.")
  4529      return sess
  4530  
  4531  
  4532  # ══ INTRO-RELAY-1 (5 Aug 2026) — masked-alias introduction relay (Option B) ══
  4533  # David's doctrine: "Nothing of the customer's leaves TrustSquare except a consented,
  4534  # revocable email channel — never the address itself. We disclose nothing; we relay."
  4535  # Dark until launch_switches.intro_relay = 1 (fail-closed). Spec:
  4536  # Records/INTRO_RELAY_BUILD_SPEC.md. Inbound rides Cloudflare Email Routing via the
  4537  # Worker (ops/cloudflare/intro_relay_worker.js); outbound rides the Resend lane.
  4538  RELAY_DOMAIN = os.getenv("RELAY_DOMAIN", "relay.trustsquare.co")
  4539  RELAY_INBOUND_SECRET = os.getenv("RELAY_INBOUND_SECRET", "")
  4540  _RELAY_MAX_BODY = 100_000        # relayed text cap; attachments are v2, dropped loudly
  4541  _RELAY_TTL_DAYS = int(os.getenv("RELAY_TTL_DAYS", "30"))
```

## accept_intro: owner gate + relay wiring + alias-only webhook — from bea_main.py

```
  4780  
  4781  @app.put("/intros/{intro_id}/accept")
  4782  def accept_intro(intro_id: int, background_tasks: BackgroundTasks,
  4783                   _key: str = Depends(auth.require_api_key),
  4784                   ts_user: str = Cookie(default=None)):
  4785      conn = database.get_db()
  4786      intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
  4787      if not intro:
  4788          conn.close()
  4789          raise HTTPException(status_code=404, detail="Intro not found")
  4790      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
  4791      # BIND-OWNER-1 (ACCOUNT-BIND-1, 5 Aug 2026): accepting charges the BUYER, so the
  4792      # accepter must be PROVEN to be the listing owner — not merely hold the public key.
  4793      if _account_binding_enabled():
  4794          _sess = _session_email(ts_user)
  4795          _owner = ((listing["seller_email"] or "") if listing else "").strip().lower()
  4796          if not _sess:
  4797              conn.close()
  4798              raise HTTPException(status_code=401,
  4799                                  detail="Please sign in to accept introductions.")
  4800          if _owner and _sess != _owner:
  4801              conn.close()
  4802              raise HTTPException(status_code=403,
  4803                                  detail="Only the listing owner can accept an introduction.")
  4804      conn.execute(
  4805          "UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 WHERE id = ?",
  4806          (intro_id,)
  4807      )
  4808      # Deduct 1 Tuppence from the buyer's wallet
  4809      conn.execute(
  4810          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'intro_deduct', -1, ?)",
  4811          (intro["buyer_email"], f"Intro accepted · listing #{intro['listing_id']} · {listing['title'] if listing else ''}")
  4812      )
  4813      conn.commit()
  4814      # INTRO-RELAY-1 (5 Aug 2026): with the relay ON, the introduction happens through
  4815      # masked aliases — the raw counterpart addresses never leave TrustSquare (not to the
  4816      # parties, not to the webhook). Flag OFF = today's behaviour, byte for byte.
  4817      _relay_on = _intro_relay_enabled()
  4818      _b_alias = _s_alias = None
  4819      if _relay_on and listing and listing["seller_email"]:
  4820          try:
  4821              _b_alias, _s_alias = _mint_relay_aliases(
  4822                  conn, intro_id, intro["buyer_email"], listing["seller_email"])
  4823              conn.commit()
  4824          except Exception as _re:
  4825              _log.error("INTRO-RELAY-1 mint failed — legacy flow for intro #%s: %s", intro_id, _re)
  4826              _relay_on = False
  4827      conn.close()
  4828      if _relay_on and _b_alias and _s_alias:
  4829          background_tasks.add_task(
  4830              _relay_send_intro_notes, intro_id,
  4831              intro["buyer_email"], intro["buyer_name"] or "",
  4832              listing["seller_email"], listing["title"] or "",
  4833              _b_alias, _s_alias)
  4834      if N8N_WEBHOOK_ACCEPT:
  4835          payload = {
  4836              "event":              "intro_accepted",
  4837              "intro_id":           intro_id,
  4838              "listing_id":         intro["listing_id"],
  4839              "listing_title":      listing["title"] if listing else None,
  4840              "category":           listing["category"] if listing else None,
  4841              # relay ON: aliases only — the raw addresses stay inside TrustSquare
  4842              "buyer_email":        _b_alias if _relay_on else intro["buyer_email"],
  4843              "buyer_name":         intro["buyer_name"],
  4844              "seller_email":       (_s_alias if _relay_on else
  4845                                     (listing["seller_email"] if listing and listing["seller_email"] else None)),
  4846              "relay":              bool(_relay_on),
  4847              "city":               listing["city"] if listing else None,
  4848              "timestamp":          datetime.now(timezone.utc).isoformat(),
  4849          }
  4850          background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_ACCEPT, payload)
  4851      return {"message": "Introduction accepted — 1T charged"}
  4852  
  4853  @app.put("/intros/{intro_id}/decline")
  4854  def decline_intro(intro_id: int, background_tasks: BackgroundTasks,
  4855                    _key: str = Depends(auth.require_api_key),
  4856                    ts_user: str = Cookie(default=None)):
  4857      conn = database.get_db()
  4858      intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
  4859      if not intro:
  4860          conn.close()
  4861          raise HTTPException(status_code=404, detail="Intro not found")
  4862      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
  4863      # BIND-OWNER-1: declining is the owner's decision too — no griefing declines.
  4864      if _account_binding_enabled():
  4865          _sess = _session_email(ts_user)
  4866          _owner = ((listing["seller_email"] or "") if listing else "").strip().lower()
  4867          if not _sess:
  4868              conn.close()
  4869              raise HTTPException(status_code=401, detail="Please sign in to decline introductions.")
```

## /auth/verify: magic-link proof kept as ts_user session — from bea_main.py

```
 11410  
 11411  @app.post("/auth/verify")
 11412  def auth_verify(req: _SignInVerify, response: Response):
 11413      """Verify a sign-in token; create the account on first use. Returns email+name."""
 11414      try:
 11415          payload = _pyjwt.decode(req.token, _JWT_SECRET, algorithms=[_JWT_ALGO])
 11416      except _pyjwt.ExpiredSignatureError:
 11417          raise HTTPException(status_code=401, detail="This sign-in link has expired — request a new one.") from None
 11418      except _pyjwt.InvalidTokenError:
 11419          raise HTTPException(status_code=401, detail="This sign-in link is not valid.") from None
 11420      if payload.get("purpose") != "signin":
 11421          raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
 11422      email = (payload.get("email") or "").strip().lower()
 11423      if not email:
 11424          raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
 11425      conn = database.get_db()
 11426      try:
 11427          conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
 11428          # AGENCY-MEMBER-1 (3 Aug 2026, David): agency_members.status was written
 11429          # 'invited' at invite time and NEVER advanced — nothing anywhere set
 11430          # 'active' or joined_at, so any future logic keyed on active membership
 11431          # would have misfired. First successful sign-in IS the join.
 11432          try:
 11433              conn.execute(
 11434                  "UPDATE agency_members SET status='active', joined_at=? "
 11435                  "WHERE LOWER(agent_email)=? AND status='invited'",
 11436                  (datetime.now(timezone.utc).isoformat(), email))
 11437          except Exception:
 11438              pass
 11439          conn.commit()
 11440          row = conn.execute("SELECT name FROM users WHERE email=?", (email,)).fetchone()
 11441          name = row["name"] if row and row["name"] else email.split("@")[0]
 11442      finally:
 11443          conn.close()
 11444      # ACCOUNT-BIND-1 (5 Aug 2026): a verified magic link now ESTABLISHES a server
 11445      # session — the missing piece of LAUNCH-AUTH-1. The proof of email possession is
 11446      # kept as an HttpOnly cookie so charging endpoints can bind to a PROVEN identity
 11447      # instead of a caller-typed email. Same JWT machinery, distinct scope 'user'.
 11448      _sess_tok = _pyjwt.encode(
 11449          {"scope": "user", "sub": email,
 11450           "exp": datetime.now(timezone.utc) + timedelta(days=180),
 11451           "iat": datetime.now(timezone.utc)},
 11452          _JWT_SECRET, algorithm=_JWT_ALGO)
 11453      response.set_cookie("ts_user", _sess_tok, max_age=180*24*3600,
 11454                          httponly=True, secure=True, samesite="lax", path="/")
 11455      return {"ok": True, "email": email, "name": name}
 11456  
 11457  # ── AGENCY (Team plan) — umbrella over agent sellers ───────────────────────
 11458  class _AgencyCreate(_BaseModel):
 11459      name: str
 11460      admin_email: str
 11461      countries: list = []
 11462  
 11463  class _AgentInvite(_BaseModel):
 11464      email: str
```


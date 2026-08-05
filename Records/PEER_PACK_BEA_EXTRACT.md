# PEER PACK — targeted evidence extract (v3)

*Generated 2026-08-05 12:45 UTC. Each line keeps its REAL line number in its source file so*
*citations are checkable. If a section you need is absent, name the exact file and*
*line range as a finding and it will be supplied next run.*

## COMPUTED TOTALITY EVIDENCE (Author-derived greps over the full bea_main.py — treat as claims; spot-check by requesting ranges)

- Vendor inference hosts named in bea_main.py (16984 lines): {'api.anthropic.com': 0, 'api.openai.com': 0, 'api.scaleway.ai': 0}
- Old vendor-specific gates ('if not ANTHROPIC_API_KEY') remaining: NONE
- Vendor-neutral gates ('if not ai_provider.any_lane_configured()'): 15 at lines [3379, 5022, 5142, 5218, 5294, 8961, 9177, 9774, 13866, 13953, 14535, 14845, 15067, 15325, 16211]
- Every line invoking ai_provider.complete: [13, 3409, 5041, 5176, 5245, 5543, 9008, 9203, 9790, 9819, 11447, 13507, 13512, 13911, 14013, 14699, 14981, 15136, 15358, 16268, 16978]
- Every _deduct_tuppence call line: [5578, 13933, 14039, 14725, 15005, 15170]

## Admin auth dependency (used by /admin/ai-* endpoints) — from bea_main.py

```
    34  MS_ADMIN_KEY = os.environ.get("MS_ADMIN_KEY", "")
    35  
    36  def _require_admin_or_key(x_admin_token: str = Header(default=None),
    37                            x_admin_key: str = Header(default=None)):
    38      if x_admin_key and MS_ADMIN_KEY and x_admin_key == MS_ADMIN_KEY:
    39          return {"via": "admin-key"}
    40      if x_admin_token and _JWT_SECRET:
    41          try:  # _pyjwt/_JWT_SECRET defined later at module level — resolved at call time
    42              return _pyjwt.decode(x_admin_token, _JWT_SECRET, algorithms=[_JWT_ALGO])
    43          except Exception:
    44              pass
    45      raise HTTPException(status_code=401, detail="Admin credentials required.")
    46  from email.utils import parseaddr, formataddr
    47  from datetime import datetime, timezone, timedelta
    48  
    49  app = FastAPI(title="TrustSquare BEA", version="1.3.1")
    50  
    51  # S4 (audit · HIGH): CORS locked to TrustSquare origins only.
    52  # Previously allow_origins=["*"] + allow_origin_regex=".*" — any site could call the BEA
    53  # from a user's browser. Auth is X-Api-Key/email (allow_credentials stays False), and the
    54  # buyer/admin/dashboard are all same-origin on trustsquare.co, so an explicit allowlist
    55  # breaks nothing. A new origin must be added here deliberately.
    56  ALLOWED_ORIGINS = [
    57      "https://trustsquare.co",
    58      "https://www.trustsquare.co",
    59  ]
    60  app.add_middleware(
    61      CORSMiddleware,
    62      allow_origins=ALLOWED_ORIGINS,
    63      allow_credentials=False,
```

## Breaker wiring at BEA startup (attach + alert hook) — from bea_main.py

```
    70  # an attach failure leaves the seam exactly as it was yesterday (naive any-of fallback).
    71  try:
    72      import ai_breaker as _ai_brk
    73      def _brk_alert(payload):
    74          try:
    75              _log.warning("AI-BREAKER %s: %s", payload.get("event"), payload)
    76              _hook = os.getenv("N8N_WEBHOOK_AI_ALERT")
    77              if _hook:
    78                  import httpx as _hx
    79                  with _hx.Client(timeout=5) as _c: _c.post(_hook, json={"source": "ai_breaker", **payload})
    80          except Exception:
    81              pass
    82      _ai_brk.attach(database.get_db, alert=_brk_alert)
    83  except Exception as _brk_e:
    84      import logging as _lg; _lg.getLogger("bea").warning("ai_breaker attach failed (fail-open): %r", _brk_e)
    85  
    86  
    87  # CityLauncher scrapes AGENCY vocabulary ("Estate Agents", "Car Dealers", ...); the app
    88  # speaks 6 category names. This maps a scraped label to the app category the demand loop
    89  # matches on. Keyword-based so it survives new agency labels; None = leave unmatched.
    90  def _demand_norm_category(raw):
    91      t = (raw or "").strip().lower()
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
   702          conn.execute("ALTER TABLE ai_spend_log ADD COLUMN provider TEXT")
   703  
   704      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_config (
   705          id                  INTEGER PRIMARY KEY CHECK (id = 1),
   706          monthly_income_usd  REAL    NOT NULL DEFAULT 0.0,
   707          alert_threshold_pct REAL    NOT NULL DEFAULT 20.0,
   708          alert_email         TEXT    NOT NULL DEFAULT 'dmcontiki2@gmail.com',
   709          last_alerted_at     TEXT
   710      )""")
   711      # Seed default config row (id=1 enforced by CHECK constraint)
   712      conn.execute("""INSERT OR IGNORE INTO ai_spend_config
   713          (id, monthly_income_usd, alert_threshold_pct, alert_email)
   714          VALUES (1, 0.0, 20.0, 'dmcontiki2@gmail.com')""")
   715  
   716      # C1-RES (AI-SERVICES-AUDIT-1 F2, 5 Aug 2026): pre-dispatch spend RESERVATIONS.
   717      # The ceiling check summed only LOGGED spend, which is written AFTER the call — so
   718      # N concurrent calls all passed the check before any recorded its cost and could
   719      # collectively overshoot. A reservation is a short-lived worst-case hold placed
   720      # BEFORE dispatch and counted by the ceiling check; it is settled when real spend
   721      # is logged, and self-expires so an aborted call can never wedge the budget.
   722      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_holds (
   723          id         INTEGER PRIMARY KEY AUTOINCREMENT,
   724          email      TEXT    NOT NULL DEFAULT '',
   725          est_usd    REAL    NOT NULL DEFAULT 0.0,
   726          created_at TEXT    NOT NULL DEFAULT (datetime('now')),
   727          expires_at TEXT    NOT NULL
   728      )""")
   729  
   730      # Launch Switch (free-only <-> verified) — singleton flag row; default = launch/free-only
   731      conn.execute("""CREATE TABLE IF NOT EXISTS launch_switches (
   732          id            INTEGER PRIMARY KEY CHECK (id = 1),
   733          mode          TEXT    NOT NULL DEFAULT 'launch',
   734          verified_tier INTEGER NOT NULL DEFAULT 0,
   735          videos        INTEGER NOT NULL DEFAULT 0,
   736          data_ops      INTEGER NOT NULL DEFAULT 0,
   737          data_places   INTEGER NOT NULL DEFAULT 0,
   738          data_flights  INTEGER NOT NULL DEFAULT 0,
   739          data_mapbox   INTEGER NOT NULL DEFAULT 0,
   740          p_heritage    INTEGER NOT NULL DEFAULT 0,
   741          p_expedition  INTEGER NOT NULL DEFAULT 0,
   742          p_weekend     INTEGER NOT NULL DEFAULT 0,
   743          -- BIT safe-state flags (Mitigator flips these to a SAFE value on a confirmed BIT failure).
   744          -- Defaults = NORMAL/healthy state; the Mitigator only ever moves them toward safe.
   745          ai_example_enabled     INTEGER NOT NULL DEFAULT 1,
   746          auth_fail_closed       INTEGER NOT NULL DEFAULT 0,
   747          tuppence_burn_enabled  INTEGER NOT NULL DEFAULT 1,
   748          -- AI provider seam (D1): live-switchable inference vendor (Page-4 control). Default = anthropic.
   749          ai_active     TEXT    NOT NULL DEFAULT 'anthropic',
   750          -- MANUAL PIN (David 1 Aug 2026): operator override with DECAY — precedence over any
   751          -- auto selection while unexpired; expiry returns control to the standing lane.
   752          ai_active_override  TEXT,
   753          ai_override_expires TEXT,
   754          -- MAINT-B1b: in-app tester fault intake. OFF by default (fail-closed).
   755          fault_report  INTEGER NOT NULL DEFAULT 0,
   756          updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
   757      )""")
   758      conn.execute("INSERT OR IGNORE INTO launch_switches (id) VALUES (1)")
   759      # BIT safe-state flags — add to pre-existing launch_switches rows (idempotent).
   760      for _ddl in (
   761          "ALTER TABLE launch_switches ADD COLUMN ai_example_enabled    INTEGER NOT NULL DEFAULT 1",
   762          "ALTER TABLE launch_switches ADD COLUMN auth_fail_closed      INTEGER NOT NULL DEFAULT 0",
   763          "ALTER TABLE launch_switches ADD COLUMN tuppence_burn_enabled INTEGER NOT NULL DEFAULT 1",
   764          "ALTER TABLE launch_switches ADD COLUMN ai_active TEXT NOT NULL DEFAULT 'anthropic'",
   765          "ALTER TABLE launch_switches ADD COLUMN ai_active_override TEXT",
   766          "ALTER TABLE launch_switches ADD COLUMN ai_override_expires TEXT",
   767          "ALTER TABLE launch_switches ADD COLUMN fault_report INTEGER NOT NULL DEFAULT 0",
   768      ):
   769          try:
   770              conn.execute(_ddl)
   771          except Exception:
```

## Spend logging, alerting, cost ceiling — from bea_main.py

```
  1505  
  1506  
  1507  def _log_ai_spend(email: str, endpoint: str, model_key: str,
  1508                    in_tok: int | None = None, out_tok: int | None = None):
  1509      """Background task: log AI call cost + trigger alert check if threshold crossed.
  1510      Non-blocking — called via background_tasks.add_task() after every AI call.
  1511      Never raises — log errors only.
  1512  
  1513      C2 (Session 97): real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
  1514      No tokens (legacy sites) -> flat _AI_COST estimate, cost_is_real=0. Backward compatible.
  1515      """
  1516      try:
  1517          if in_tok is not None or out_tok is not None:
  1518              it, ot = int(in_tok or 0), int(out_tok or 0)
  1519              cost = _token_cost(model_key, it, ot)
  1520              is_real = 1
  1521          else:
  1522              it, ot = 0, 0
  1523              cost = _AI_COST.get(model_key, 0.0023)
  1524              is_real = 0
  1525          try:
  1526              _prov = _ts_active_provider()   # P1: provider attribution — signature & call sites unchanged
  1527          except Exception:
  1528              _prov = 'anthropic'
  1529          conn = database.get_db()
  1530          try:
  1531              conn.execute(
  1532                  "INSERT INTO ai_spend_log "
  1533                  "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real, provider) "
  1534                  "VALUES (?,?,?,?,?,?,?,?)",
  1535                  (email or '', endpoint, model_key, cost, it, ot, is_real, _prov)
  1536              )
  1537              conn.commit()
  1538              _maybe_fire_spend_alert(conn)
  1539          finally:
  1540              conn.close()
  1541          _settle_hold(email or '')   # C1-RES: real spend recorded — release the reservation
  1542      except Exception as exc:
  1543          _log.error("_log_ai_spend failed: %s", exc)
  1544  
  1545  
  1546  def _maybe_fire_spend_alert(conn):
  1547      """Check if current month AI spend has crossed the configured threshold.
  1548      Fires n8n webhook at most once per day. Silent if not configured.
  1549      """
  1550      try:
  1551          cfg = conn.execute(
  1552              "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
  1553              "FROM ai_spend_config WHERE id = 1"
  1554          ).fetchone()
  1555          if not cfg or cfg["monthly_income_usd"] <= 0:
  1556              return  # income not configured yet — skip
  1557  
  1558          # Current calendar month spend
  1559          month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
  1560          row = conn.execute(
  1561              "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
  1562              "WHERE logged_at >= ?", (month_start,)
  1563          ).fetchone()
  1564          month_spend = row["total"] if row else 0.0
  1565  
  1566          threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
  1567          if month_spend < threshold_usd:
  1568              return  # under threshold — nothing to do
  1569  
  1570          # Check last alerted — don't fire more than once per day
  1571          last = cfg["last_alerted_at"] or ""
  1572          today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
  1573          if last.startswith(today):
  1574              return  # already alerted today
  1575  
  1576          # Update last_alerted_at
  1577          conn.execute(
  1578              "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
  1579              (__import__('datetime').datetime.utcnow().isoformat(),)
  1580          )
  1581          conn.commit()
  1582  
  1583          # Fire n8n alert webhook if configured
  1584          pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
  1585          payload = {
  1586              "alert": "ai_spend_threshold",
  1587              "month_spend_usd": round(month_spend, 4),
  1588              "income_usd": cfg["monthly_income_usd"],
  1589              "threshold_pct": cfg["alert_threshold_pct"],
  1590              "pct_used": round(pct_used, 1),
  1591              "alert_email": cfg["alert_email"],
  1592              "message": (
  1593                  f"TrustSquare AI spend alert: ${month_spend:.4f} spent this month "
  1594                  f"({pct_used:.1f}% of ${cfg['monthly_income_usd']:.2f} income). "
  1595                  f"Threshold: {cfg['alert_threshold_pct']}%."
  1596              ),
  1597          }
  1598          _log.warning("AI spend alert fired: %s", payload["message"])
  1599          if N8N_WEBHOOK_AI_ALERT:
  1600              import asyncio
  1601              try:
  1602                  loop = asyncio.get_event_loop()
  1603                  if loop.is_running():
  1604                      loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
  1605              except Exception:
  1606                  pass  # alert failure must never affect user response
  1607      except Exception as exc:
  1608          _log.error("_maybe_fire_spend_alert failed: %s", exc)
  1609  
  1610  
  1611  # C1-RES worst-case hold (USD): a conservative per-call ceiling — the dearest metered
  1612  # call (Sonnet vision batch) rounds up to this. Over-reserves slightly (safe direction);
  1613  # settled down to the real figure the moment _log_ai_spend records actual tokens.
  1614  _AI_WORST_CASE_HOLD_USD = 0.06
  1615  _HOLD_TTL_S = 180
  1616  
  1617  def _active_holds_usd(conn, email: str | None = None) -> float:
  1618      """Sum of unexpired reservations (optionally for one user). Purges expired rows."""
  1619      now = __import__('datetime').datetime.utcnow().isoformat(timespec="seconds")
  1620      conn.execute("DELETE FROM ai_spend_holds WHERE expires_at < ?", (now,))
  1621      if email is not None:
  1622          row = conn.execute("SELECT COALESCE(SUM(est_usd),0) t FROM ai_spend_holds "
  1623                             "WHERE email=? AND expires_at >= ?", (email, now)).fetchone()
  1624      else:
  1625          row = conn.execute("SELECT COALESCE(SUM(est_usd),0) t FROM ai_spend_holds "
  1626                             "WHERE expires_at >= ?", (now,)).fetchone()
  1627      return float(row["t"] if row else 0.0)
  1628  
  1629  def _settle_hold(email: str) -> None:
  1630      """Release the oldest reservation for this user — called once real spend is logged.
  1631      Never raises (bookkeeping must not break serving)."""
  1632      try:
  1633          conn = database.get_db()
  1634          try:
  1635              row = conn.execute("SELECT id FROM ai_spend_holds WHERE email=? "
  1636                                 "ORDER BY id ASC LIMIT 1", (email or '',)).fetchone()
  1637              if row:
  1638                  conn.execute("DELETE FROM ai_spend_holds WHERE id=?", (row["id"],))
  1639                  conn.commit()
  1640          finally:
  1641              conn.close()
  1642      except Exception as exc:
  1643          _log.error("_settle_hold failed: %s", exc)
  1644  
  1645  
  1646  def _check_cost_ceiling(email: str) -> None:
  1647      """C1 (Session 97) — HARD daily cost ceiling. Pre-flight guard before every paid
  1648      AI call. REFUSES (HTTP 429) when today's logged AI spend has reached the per-user
  1649      or platform-wide USD ceiling. Distinct from observe-and-alert. Ceiling 0 = off.
  1650      Superusers exempt from the per-user rail (still counted toward platform).
  1651      Fail-OPEN on internal error — never lock a legitimate paying user out.
  1652      """
  1653      try:
  1654          conn = database.get_db()
  1655          try:
  1656              cfg = conn.execute(
  1657                  "SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  1658                  "FROM ai_spend_config WHERE id = 1"
  1659              ).fetchone()
  1660              if not cfg:
  1661                  return
  1662              user_cap     = cfg["daily_user_ceiling_usd"]     or 0.0
  1663              platform_cap = cfg["daily_platform_ceiling_usd"] or 0.0
  1664              if user_cap <= 0 and platform_cap <= 0:
```

## Active provider switch + pin/override (TTL decay) — from bea_main.py

```
  1378  # Manual-pin TTL (hours). David 1 Aug 2026: 24h now; REVIEW dated ~1 Nov 2026 (3 months
  1379  # proven live) to consider shortening to 1h. Env-tunable, no deploy needed to change.
  1380  AI_OVERRIDE_TTL_HOURS = float(os.getenv("AI_OVERRIDE_TTL_HOURS", "24"))
  1381  
  1382  _TS_AI_CACHE = {"prov": None, "standing": None, "override": None, "expires": None, "ts": 0.0}
  1383  def _ts_active_provider():
  1384      """The LIVE active provider — DB-backed (Page-4 switchable, no restart). Falls back to the
  1385      startup env value if the DB is unreachable. Cached ~10s so we never hammer the DB per call."""
  1386      import time as _t
  1387      now=_t.time()
  1388      if _TS_AI_CACHE["prov"] and (now-_TS_AI_CACHE["ts"])<10:
  1389          return _TS_AI_CACHE["prov"]
  1390      prov=_TS_AI_PROVIDER  # startup default
  1391      standing, override, expires = prov, None, None
  1392      try:
  1393          conn=database.get_db()
  1394          try:
  1395              row=conn.execute("SELECT ai_active, ai_active_override, ai_override_expires "
  1396                               "FROM launch_switches WHERE id=1").fetchone()
  1397              if row:
  1398                  if row["ai_active"]: standing = prov = row["ai_active"]
  1399                  override, expires = row["ai_active_override"], row["ai_override_expires"]
  1400          finally:
  1401              conn.close()
  1402      except Exception:
  1403          pass
  1404      # MANUAL PIN precedence with DECAY (David 1 Aug 2026): an unexpired operator pin
  1405      # outranks the standing/auto lane; past expiry the standing lane silently resumes.
  1406      import datetime as _dt
  1407      if override and expires:
  1408          try:
  1409              if _dt.datetime.utcnow() < _dt.datetime.fromisoformat(expires):
  1410                  prov = override
  1411              else:
  1412                  override = None   # expired — report as inactive, standing rules
  1413          except Exception:
  1414              override = None
  1415      else:
  1416          override = None
  1417      _TS_AI_CACHE.update(prov=prov, standing=standing, override=override, expires=expires if override else None, ts=now)
  1418      return prov
  1419  
  1420  def _ts_models_for(prov):
  1421      try:
  1422          return _ts_ai.TASK_MODEL.get(prov, _ts_ai.TASK_MODEL["anthropic"])
  1423      except Exception:
  1424          return _TS_AI_MODELS
  1425  
  1426  # _ts_ai_url()/_ts_ai_headers() REMOVED 31 Jul 2026 — their sole caller (vision-draft) migrated
  1427  # to the ai_provider seam, completing P0 at 22/22 call sites. The wire protocol now lives ONLY in
  1428  # ai_provider.py adapters; RG-0017 asserts no raw vendor endpoint ever returns to this file.
  1429  if not EMAIL_INBOUND_SECRET:
  1430      _log.warning("EMAIL_INBOUND_SECRET not set — /email/inbound will reject all calls")
  1431  if not GMAIL_APP_PASSWORD:
  1432      _log.warning("GMAIL_APP_PASSWORD not set — triage replies will be drafted, never sent")
  1433  
  1434  CF_ZONE_ID    = os.getenv("CF_ZONE_ID")
  1435  CF_CACHE_TOKEN = os.getenv("CF_CACHE_TOKEN")
  1436  
  1437  async def _cf_purge_all():
```

## Tuppence helpers (deduct / balance / pre-flight require) — from bea_main.py

```
 13812  
 13813  
 13814  def _deduct_tuppence(conn, email: str, amount: int, description: str) -> int:
 13815      """Deduct `amount` Tuppence from `email`. Returns new balance.
 13816      Raises HTTPException 402 if balance insufficient. Does NOT commit."""
 13817      row = conn.execute(
 13818          "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 13819          (email,)
 13820      ).fetchone()
 13821      balance = int(row["bal"])
 13822      if balance < amount:
 13823          raise HTTPException(
 13824              status_code=402,
 13825              detail=f"Insufficient Tuppence — you have {balance}T, need {amount}T"
 13826          )
 13827      conn.execute(
 13828          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'ai_service', ?, ?)",
 13829          (email, -amount, description)
 13830      )
 13831      return balance - amount
 13832  
 13833  
 13834  def _current_tuppence(email: str) -> int:
 13835      """Read-only Tuppence balance on a fresh connection. Used by deliver-then-charge
 13836      paths to report 'tuppence_remaining' when NO charge was made."""
 13837      c = database.get_db()
 13838      try:
 13839          row = c.execute(
 13840              "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 13841              (email,)
 13842          ).fetchone()
 13843          return int(row["bal"])
 13844      finally:
 13845          c.close()
 13846  
 13847  
 13848  def _require_tuppence(email: str, amount: int = 1) -> None:
 13849      """Pre-flight guard: ensure the buyer COULD pay before we run a paid AI service.
 13850      Raises 402 if not. Does NOT deduct — deduction happens only on a verified result."""
 13851      if _current_tuppence(email) < amount:
 13852          raise HTTPException(
 13853              status_code=402,
 13854              detail=f"Insufficient Tuppence — you need {amount}T to run this check."
 13855          )
 13856  
 13857  
 13858  # ── AI1 — Listing Rewrite ─────────────────────────────────────────────────────
 13859  
 13860  @app.post("/listings/{listing_id}/ai-rewrite")
 13861  async def ai_listing_rewrite(listing_id: int, email: str):
```

## AI1 Listing Rewrite (full endpoint) — from bea_main.py

```
 13859  
 13860  @app.post("/listings/{listing_id}/ai-rewrite")
 13861  async def ai_listing_rewrite(listing_id: int, email: str):
 13862      """AI1: Seller pays 1T — Claude Haiku rewrites title + description.
 13863      Uses current market language and buyer psychology for the listing category.
 13864      Returns {new_title, new_description, tuppence_remaining}.
 13865      """
 13866      if not ai_provider.any_lane_configured():
 13867          raise HTTPException(status_code=503, detail="AI not configured")
 13868      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13869  
 13870      conn = database.get_db()
 13871      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 13872      if not listing:
 13873          conn.close()
 13874          raise HTTPException(status_code=404, detail="Listing not found")
 13875      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 13876          conn.close()
 13877          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 13878  
 13879      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 13880      _rw_charge_desc = f"AI Listing Rewrite · #{listing_id} · {listing['title'][:40]}"
 13881      conn.close()
 13882  
 13883      category = listing["category"] or "General"
 13884      city     = listing["city"] or "South Africa"
 13885      title    = listing["title"] or ""
 13886      desc     = listing["description"] or ""
 13887      price    = listing["price"] or ""
 13888  
 13889      system_prompt = (
 13890          "You are an expert marketplace copywriter for TrustSquare, a South African peer-to-peer local marketplace. "
 13891          "You write short, honest, buyer-friendly listings using current South African market language. "
 13892          "You never invent details. You prefer concrete facts over adjectives. "
 13893          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include street addresses, "
 13894          "business names, complex names, seller names, agent names, phone numbers, email addresses, "
 13895          "or any other identifying information in any generated text. "
 13896          "Always respond with a single valid JSON object — no markdown, no explanation."
 13897      )
 13898  
 13899      user_prompt = (
 13900          f"Rewrite this {category} listing for a buyer in {city}, South Africa.\n\n"
 13901          f"CURRENT TITLE: {title}\n"
 13902          f"CURRENT DESCRIPTION: {desc}\n"
 13903          f"PRICE: {price}\n\n"
 13904          "Return JSON with exactly two keys:\n"
 13905          '{"new_title": "<15 words max, specific and punchy>", '
 13906          '"new_description": "<60-120 words, 2-3 short paragraphs, buyer psychology, honest, no clichés>"}'
 13907      )
 13908  
 13909      try:
 13910          _sr = await asyncio.to_thread(
 13911              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 13912              task="haiku", max_tokens=350, system=system_prompt,
 13913              provider=_ts_active_provider(), timeout=20)
 13914          _rw_in, _rw_out = _sr.in_tokens, _sr.out_tokens
 13915          # P2 — Tuppence covers the revenue side; log token spend so the cost
 13916          # dashboard sees it too (sweep 12 Jun 2026)
 13917          _log_ai_spend(email, "/listings/ai-rewrite", "haiku", _rw_in, _rw_out)
 13918          raw = _sr.text.strip()
 13919          # Strip markdown fences if model adds them
 13920          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 13921          raw = _re_match.sub(r"\s*```$", "", raw)
 13922          result = json.loads(raw)
 13923          new_title = str(result.get("new_title", "")).strip()[:120]
 13924          new_desc  = str(result.get("new_description", "")).strip()[:1000]
 13925      except Exception as exc:
 13926          _log.error("ai-rewrite: %s", exc)
 13927          raise HTTPException(status_code=500, detail="AI rewrite failed — no Tuppence was charged") from exc
 13928  
 13929      # F2 fix: deliver-then-charge — deduction happens ONLY here, after a good result,
 13930      # so the help card's "server error = no Tuppence deducted" promise is true.
 13931      _conn2 = database.get_db()
 13932      try:
 13933          remaining = _deduct_tuppence(_conn2, email, 1, _rw_charge_desc)
 13934          _conn2.commit()
 13935      finally:
 13936          _conn2.close()
 13937      _log.info("ai-rewrite: listing #%d email=%s", listing_id, email)
 13938      return {
 13939          "new_title": new_title,
 13940          "new_description": new_desc,
 13941          "tuppence_remaining": remaining,
 13942      }
 13943  
 13944  
 13945  # ── AI2 — Seller Audit ────────────────────────────────────────────────────────
 13946  
 13947  @app.post("/listings/{listing_id}/ai-audit")
 13948  async def ai_seller_audit(listing_id: int, email: str):
 13949      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 13950      3 specific, actionable improvement steps.
 13951      Returns {actions: [{step, reason}], tuppence_remaining}.
 13952      """
 13953      if not ai_provider.any_lane_configured():
 13954          raise HTTPException(status_code=503, detail="AI not configured")
 13955      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13956  
 13957      conn = database.get_db()
 13958      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
```

## AI2 Seller Audit (full endpoint) — from bea_main.py

```
 13946  
 13947  @app.post("/listings/{listing_id}/ai-audit")
 13948  async def ai_seller_audit(listing_id: int, email: str):
 13949      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 13950      3 specific, actionable improvement steps.
 13951      Returns {actions: [{step, reason}], tuppence_remaining}.
 13952      """
 13953      if not ai_provider.any_lane_configured():
 13954          raise HTTPException(status_code=503, detail="AI not configured")
 13955      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13956  
 13957      conn = database.get_db()
 13958      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 13959      if not listing:
 13960          conn.close()
 13961          raise HTTPException(status_code=404, detail="Listing not found")
 13962      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 13963          conn.close()
 13964          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 13965  
 13966      # Read intro request count for context
 13967      intro_row = conn.execute(
 13968          "SELECT COUNT(*) as cnt FROM intro_requests WHERE listing_id = ?", (listing_id,)
 13969      ).fetchone()
 13970      intro_count = intro_row["cnt"] if intro_row else 0
 13971  
 13972      # Read trust score
 13973      user_row = conn.execute(
 13974          "SELECT trust_score FROM users WHERE email = ?", (email,)
 13975      ).fetchone()
 13976      trust_score = user_row["trust_score"] if user_row and user_row["trust_score"] else "unknown"
 13977  
 13978      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 13979      _au_charge_desc = f"AI Seller Audit · #{listing_id} · {listing['title'][:40]}"
 13980      conn.close()
 13981  
 13982      category = listing["category"] or "General"
 13983      city     = listing["city"] or "South Africa"
 13984      title    = listing["title"] or "(no title)"
 13985      desc     = listing["description"] or "(no description)"
 13986      price    = listing["price"] or "(no price)"
 13987  
 13988      system_prompt = (
 13989          "You are a marketplace performance coach for TrustSquare, a South African peer-to-peer marketplace. "
 13990          "You give direct, specific, actionable advice — no filler, no encouragement padding. "
 13991          "Think like a top-performing seller in the same category who has seen hundreds of listings. "
 13992          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include or suggest including "
 13993          "street addresses, business names, seller names, agent names, phone numbers, or contact details "
 13994          "in any generated text or improvement suggestions. "
 13995          "Always respond with a single valid JSON object — no markdown, no explanation."
 13996      )
 13997  
 13998      user_prompt = (
 13999          f"This {category} listing in {city} has received {intro_count} intro request(s) and "
 14000          f"the seller has a trust score of {trust_score}.\n\n"
 14001          f"TITLE: {title}\n"
 14002          f"DESCRIPTION: {desc}\n"
 14003          f"PRICE: {price}\n\n"
 14004          "Identify the 3 most important reasons a buyer might scroll past this listing without requesting an intro. "
 14005          "For each reason give a specific fix the seller can do right now.\n\n"
 14006          "Return JSON: "
 14007          '{"actions": [{"step": "<imperative fix, 8 words max>", "reason": "<why this matters, 1 sentence>"}, ...]}'
 14008          " — exactly 3 items in the array."
 14009      )
 14010  
 14011      try:
 14012          _sr = await asyncio.to_thread(
 14013              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14014              task="haiku", max_tokens=400, system=system_prompt,
 14015              provider=_ts_active_provider(), timeout=20)
 14016          _au_in, _au_out = _sr.in_tokens, _sr.out_tokens
 14017          # P2 — Tuppence covers the revenue side; log token spend so the cost
 14018          # dashboard sees it too (sweep 12 Jun 2026)
 14019          _log_ai_spend(email, "/listings/ai-audit", "haiku", _au_in, _au_out)
 14020          raw = _sr.text.strip()
 14021          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14022          raw = _re_match.sub(r"\s*```$", "", raw)
 14023          result = json.loads(raw)
 14024          actions = result.get("actions", [])
 14025          # Sanitise — max 3, enforce fields
 14026          clean_actions = []
 14027          for a in actions[:3]:
 14028              if isinstance(a, dict) and a.get("step"):
 14029                  clean_actions.append({
 14030                      "step":   str(a.get("step",   ""))[:80],
 14031                      "reason": str(a.get("reason", ""))[:200],
 14032                  })
 14033      except Exception as exc:
 14034          _log.error("ai-audit: %s", exc)
 14035          raise HTTPException(status_code=500, detail="AI audit failed — no Tuppence was charged") from exc
 14036  
 14037      _conn2 = database.get_db()
 14038      try:
 14039          remaining = _deduct_tuppence(_conn2, email, 1, _au_charge_desc)   # F2: charge on delivery
 14040          _conn2.commit()
 14041      finally:
 14042          _conn2.close()
 14043      _log.info("ai-audit: listing #%d email=%s intros=%d", listing_id, email, intro_count)
 14044      return {
 14045          "actions": clean_actions,
 14046          "tuppence_remaining": remaining,
 14047      }
 14048  
 14049  
 14050  # ── AI3 — Buyer Price Check (upgraded Session 77: three-panel intelligence) ──
 14051  
 14052  # -- Tiered Value Selector: availability helpers + value-tiers endpoint --------
 14053  # STEP 5: the paid master switch AND per-provider liveness now come from the
 14054  # server-readable feature_flags store (feature_flags.json), so enabling a paid
 14055  # provider later is a CONFIG change, not a code edit. Safe defaults: paid OFF,
 14056  # every paid/contract provider OFF, free/open/owned providers ON.
 14057  def _paid_tiers_enabled() -> bool:
 14058      return feature_flags.paid_tiers_enabled()
 14059  
 14060  def _tier_providers() -> dict:
```

## AI3 Price Check (charge logic + integrity model) — from bea_main.py

```
 14517  
 14518  @app.post("/listings/{listing_id}/price-check")
 14519  async def ai_price_check(listing_id: int, email: str, tier: Optional[str] = None):
 14520      """AI3: Buyer pays 1T — honest, three-panel price intelligence.
 14521  
 14522      INTEGRITY MODEL (price-integrity fix):
 14523        The model writes the SENTENCE; the system produces the NUMBER.
 14524        - Collectibles with a resolved Scryfall id  -> VERIFIED feed price (USD->ZAR
 14525          live rate). The LLM only narrates the real figures it is handed.
 14526        - Everything else -> an explicitly-labelled QUALITATIVE GUIDE. The LLM may
 14527          give a rough range but it is flagged 'not a verified price', and we never
 14528          cheerlead ('move quickly' is not permitted anywhere).
 14529        - A first-class fraud guard fires when asking price is far below a VERIFIED
 14530          floor: the verdict becomes a warning, never a 'buy' nudge.
 14531      Returns {verdict, source, sa_context, sa_range, assessment, official_context,
 14532               official_range, local_vs_global, asking_price, verified, safety_flag,
 14533               tuppence_remaining, ...legacy}.
 14534      """
 14535      if not ai_provider.any_lane_configured():
 14536          raise HTTPException(status_code=503, detail="AI not configured")
 14537  
 14538      conn = database.get_db()
 14539      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14540      if not listing:
 14541          conn.close()
 14542          raise HTTPException(status_code=404, detail="Listing not found")
 14543  
 14544      # DELIVER-THEN-CHARGE (Session 95): we do NOT deduct here. Tuppence is only
 14545      # charged at the end, and ONLY if we produced a verified service. A guess,
 14546      # a 'cannot verify', or any failure costs the buyer nothing.
 14547      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour; a
 14548      # tier-aware caller must request a tier actually offered for this listing.
 14549      if tier is None:
 14550          _charge = 1
 14551      else:
 14552          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "fair_price")}
 14553          if tier not in _offered_t:
 14554              conn.close()
 14555              raise HTTPException(status_code=400,
 14556                  detail=f"Tier {tier} is not available for this listing")
 14557          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 14558      _require_tuppence(email, _charge)   # pre-flight only — no deduction yet
 14559      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 14560      category    = listing["category"] or "General"
 14561      city        = listing["city"] or "South Africa"
 14562      title       = listing["title"] or "(no title)"
 14563      desc        = listing["description"] or "(no description)"
 14564      price       = listing["price"] or "(no price)"
 14565      scryfall_id = listing["scryfall_id"] if "scryfall_id" in listing.keys() else None
 14566      conn.close()  # done reading; charging happens on its own connection at the end
 14567  
 14568      # Parse the buyer-facing asking price into a number for ratio checks.
 14569      asking_zar = None
 14570      try:
 14571          asking_zar = float(str(price).replace("R", "").replace(",", "").strip())
 14572      except Exception:
 14573          asking_zar = None
 14574  
 14575      # ── Step 1+2: try to resolve a REAL verified price (collectibles) ──────────
 14576      verified_block = None        # text handed to the model as ground truth
 14577      official_range = "N/A"
 14578      official_ctx   = ""
 14579      floor_zar      = None
 14580      verified       = False
 14581      source         = "ai_estimate"
 14582  
 14583      # Late-resolve a scryfall id if the listing predates this column.
 14584      if not scryfall_id:
 14585          try:
 14586              scryfall_id = await resolve_scryfall_id(title, category)
 14587              if scryfall_id:
 14588                  c2 = database.get_db()
 14589                  c2.execute("UPDATE listings SET scryfall_id = ? WHERE id = ?",
 14590                             (scryfall_id, listing_id))
 14591                  c2.commit(); c2.close()
 14592          except Exception:
 14593              scryfall_id = None
 14594  
 14595      if scryfall_id:
 14596          feed = await scryfall_price_by_id(scryfall_id)
 14597          if feed and feed.get("usd"):
 14598              rate = await live_usd_zar()
 14599              usd  = feed["usd"]
 14600              floor_zar = usd * rate
 14601              verified = True
 14602              source   = "scryfall"
 14603              reserved = " (Reserved List — cannot be reprinted)" if feed.get("reserved") else ""
 14604              official_range = f"R{floor_zar:,.0f}  (USD ${usd:,.2f} \u00d7 R{rate:.2f}/USD)"
 14605              official_ctx   = (f"Verified market price for {feed.get('name')} "
 14606                                f"[{feed.get('set_name')}]{reserved}: "
 14607                                f"USD ${usd:,.2f} on TCGPlayer (via Scryfall), "
 14608                                f"\u2248 R{floor_zar:,.0f} at today's rate.")
 14609              verified_block = (
 14610                  f"VERIFIED MARKET DATA (use these EXACT figures, do not alter them):\n"
 14611                  f"- Card: {feed.get('name')} [{feed.get('set_name')}]{reserved}\n"
 14612                  f"- Verified market price: USD ${usd:,.2f} = R{floor_zar:,.0f} "
 14613                  f"(live rate R{rate:.2f}/USD)\n"
 14614                  f"- Buyer's asking price: {price}\n"
 14615              )
 14616  
 14617      # ── Step 3: narrate. Two prompt modes: verified vs qualitative-guide ───────
 14618      # -- STEP 3: no card feed -> try the FREE/owned resolver for the chosen tier
 14619      if (not verified_block) and (tier is not None):
 14620          _fpx = await _fair_price_resolve(
 14621              listing, listing_id, tier, _tierkey_for(listing, "fair_price"),
 14622              _listing_country_iso2(listing), category, city, asking_zar)
 14623          if _fpx and _fpx[0] == "verified":
 14624              _e = _fpx[1]
 14625              verified = True
 14626              source = _e["source"]
 14627              floor_zar = _e.get("floor_zar")
 14628              official_range = _e["official_range"]
 14629              official_ctx = _e["official_ctx"]
 14630              verified_block = _e["block"]
 14631          elif _fpx and _fpx[0] == "area_guide":
 14632              _e = _fpx[1]
 14633              _log.info("ai-price-check: listing #%d buyer=%s AREA-GUIDE %s (0T free)",
 14634                        listing_id, email, _e["source"])
 14635              return {
 14636                  "verdict": "area_guide", "source": _e["source"],
 14637                  "verified": False, "charged": False,
 14638                  "sa_context": "", "sa_range": _e.get("range_text", "N/A"),
 14639                  "assessment": _e["assessment"],
 14640                  "official_context": _e.get("provenance", ""),
 14641                  "official_range": _e.get("range_text", "N/A"),
 14642                  "local_vs_global": "cannot_compare", "asking_price": price,
 14643                  "safety_flag": None, "tuppence_remaining": _current_tuppence(email),
 14644                  "indicative_label": _INDICATIVE_LABEL,
 14645                  "provenance_date": _e.get("date", ""),
 14646                  "context": _e["assessment"], "suggested_range": _e.get("range_text", "N/A"),
 14647              }
 14648      if verified_block:
 14649          system_prompt = (
 14650              "You are a pricing analyst for TrustSquare, a South African marketplace. "
 14651              "You are given VERIFIED market figures. You must NEVER invent, round, or "
 14652              "contradict them — only explain them in plain language. Never tell a buyer "
 14653              "to 'move quickly' or 'buy now'. Be honest and protective. "
 14654              "Always respond with a single valid JSON object — no markdown."
 14655          )
 14656          user_prompt = (
 14657              f"A buyer is considering this {category} listing in {city}, South Africa.\n\n"
 14658              f"TITLE: {title}\nDESCRIPTION: {desc[:400]}\n\n"
 14659              f"{verified_block}\n"
 14660              "Write a short, honest assessment comparing the asking price to the verified "
 14661              "market price. Do not output any price number other than those given above.\n"
 14662              "Return JSON with these keys (strings, 50 words max each):\n"
 14663              "{\n"
 14664              '  "verdict": "fair" | "above_market" | "below_market" | "cannot_assess",\n'
 14665              '  "sa_context": "<note on the SA second-hand reality for this item, qualitative>",\n'
 14666              '  "assessment": "<plain-language read on the asking price vs the verified figure>",\n'
 14667              '  "local_vs_global": "cheaper_locally" | "cheaper_globally" | "similar" | "cannot_compare"\n'
 14668              "}"
 14669          )
 14670      else:
 14671          # No verified price feed for this category. Per the integrity rule, we do
 14672          # NOT sell a guess. Return an honest 'cannot verify' and charge nothing.
 14673          _log.info("ai-price-check: listing #%d buyer=%s NO-FEED -> free cannot_verify",
 14674                    listing_id, email)
 14675          bal = _current_tuppence(email)
 14676          return {
 14677              "verdict":          "cannot_verify",
 14678              "source":           "no_feed",
 14679              "verified":         False,
 14680              "charged":          False,
 14681              "sa_context":       "",
 14682              "sa_range":         "N/A",
 14683              "assessment":       ("We don\u2019t yet have a verified price source for this "
 14684                                   "category, so we won\u2019t guess. No Tuppence was charged. "
 14685                                   "Compare the asking price against similar local listings "
 14686                                   "before deciding."),
 14687              "official_context": "",
 14688              "official_range":   "N/A",
 14689              "local_vs_global":  "cannot_compare",
 14690              "asking_price":     price,
 14691              "safety_flag":      None,
 14692              "tuppence_remaining": bal,
 14693              "context":          "",
 14694              "suggested_range":  "N/A",
 14695          }
 14696  
 14697      try:
 14698          _sr = await asyncio.to_thread(
 14699              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14700              task="sonnet", max_tokens=700, system=system_prompt,
 14701              provider=_ts_active_provider(), timeout=30)
 14702          raw = _sr.text.strip()
 14703          _pc_in, _pc_out = _sr.in_tokens, _sr.out_tokens   # C2/C3
 14704          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14705          raw = _re_match.sub(r"\s*```$", "", raw)
 14706          result = json.loads(raw)
 14707          verdict         = str(result.get("verdict", "cannot_assess"))[:20]
 14708          sa_context      = str(result.get("sa_context", ""))[:600]
 14709          sa_range        = str(result.get("sa_range", "N/A"))[:100]
 14710          assessment      = str(result.get("assessment", ""))[:400]
 14711          local_vs_global = str(result.get("local_vs_global", "cannot_compare"))[:20]
 14712      except Exception as exc:
 14713          _log.error("ai-price-check: %s", exc)
 14714          raise HTTPException(status_code=500, detail="AI price check failed — no Tuppence charged") from exc
 14715  
 14716      # ── Price-position note: only fires against a VERIFIED floor. Not a fraud
 14717      #    allegation — a neutral observation that the price is well below market. ─
 14718      safety_flag = price_caution(asking_zar, floor_zar)
 14719      if safety_flag and safety_flag["level"] == "danger":
 14720          verdict = "below_verified_market"
 14721  
 14722      # DELIVER-THEN-CHARGE: a verified result was produced — charge exactly now.
 14723      cc = database.get_db()
 14724      try:
 14725          remaining = _deduct_tuppence(
 14726              cc, email, _charge,
 14727              f"AI Price Check \u00b7 #{listing_id} \u00b7 {title[:40]}"
 14728          )
 14729          cc.commit()
 14730      finally:
 14731          cc.close()
 14732  
 14733      # C3 — log real AI spend for this paid call (was previously unlogged).
 14734      _log_ai_spend(email, "/listings/ai-price-check", "sonnet", _pc_in, _pc_out)
 14735  
 14736      _log.info("ai-price-check: listing #%d buyer=%s verdict=%s verified=%s flag=%s charged=1T",
 14737                listing_id, email, verdict, verified,
 14738                safety_flag["level"] if safety_flag else "none")
 14739      return {
 14740          "verdict":          verdict,
 14741          "source":           source,            # 'scryfall'
 14742          "verified":         verified,          # True only when a real feed was used
 14743          "charged":          True,
 14744          "sa_context":       sa_context,
 14745          "sa_range":         sa_range,
 14746          "assessment":       assessment,
 14747          "official_context": official_ctx,
 14748          "official_range":   official_range,
 14749          "local_vs_global":  local_vs_global,
 14750          "asking_price":     price,
 14751          "safety_flag":      safety_flag,        # None | {level, headline, detail}
 14752          "tuppence_remaining": remaining,
 14753          # Legacy fields — kept for backward compat
 14754          "context":          assessment,
 14755          "suggested_range":  sa_range,
 14756          **_report_stamp("Price reflects feeds/market data available at the time above; re-run for a current figure.", volatile=_is_volatile_item(source, verdict, locals().get("subject"), locals().get("_cat"))),
 14757      }
 14758  
 14759  # ── END AI TUPPENCE SERVICES (Session 73) ────────────────────────────────────
 14760  
 14761  
 14762  # ── AI TUPPENCE SERVICES — TIER 2 (Session 74) ───────────────────────────────
 14763  #
 14764  #   AI4  POST /listings/{id}/yield-calc?email=     Haiku   Property yield calculator (1T)
 14765  #   AI5  POST /listings/batch-cards?email=         Sonnet  Batch card listing via vision (2T)
 14766  #
 14767  # AI4: Property listings only. Calculates gross yield, net estimate, SA comparison.
 14768  # AI5: Collectors category. Accepts up to 10 base64 images, returns array of draft JSONs.
 14769  
 14770  
 14771  # ── AI4 — Property Yield Calculator ──────────────────────────────────────────
 14772  
 14773  async def _yield_fill_missing(need, tier, country, city, suburb, listing, listing_id):
 14774      """STEP 3: source the missing yield half (rent OR purchase price) from a
 14775      FREE/owned feed, per tier + country. Returns {value, provenance, date,
 14776      specificity} or None. Numbers come from feeds/arithmetic, never a model."""
```

## AI4 Yield (deliver-then-charge reference) — from bea_main.py

```
 14828  
 14829  @app.post("/listings/{listing_id}/yield-calc")
 14830  async def ai_yield_calc(listing_id: int, email: str,
 14831                          rent: float | None = None,
 14832                          purchase_price: float | None = None,
 14833                          tier: Optional[str] = None):
 14834      """AI4: Property yield — HONEST & deliver-then-charge (Session 95).
 14835  
 14836      A real gross yield needs BOTH a purchase price and an annual rent. A listing
 14837      only carries one number (sale price OR monthly rent), so we:
 14838        - take the listing's own figure for its side, and
 14839        - accept the OTHER figure from the caller (?rent= or ?purchase_price=).
 14840      If the second figure is missing we return needs_input and charge NOTHING.
 14841      The yield is computed in PYTHON (not guessed by the model). The LLM only
 14842      writes the benchmark sentence. 1T is charged ONLY when a real yield is
 14843      produced from real inputs.
 14844      """
 14845      if not ai_provider.any_lane_configured():
 14846          raise HTTPException(status_code=503, detail="AI not configured")
 14847  
 14848      conn = database.get_db()
 14849      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14850      if not listing:
 14851          conn.close()
 14852          raise HTTPException(status_code=404, detail="Listing not found")
 14853  
 14854      category = listing["category"] or ""
 14855      if "property" not in category.lower() and category.lower() not in ("property", "estate agents", "accommodation"):
 14856          conn.close()
 14857          raise HTTPException(status_code=400, detail="Yield calculator is only available for Property listings")
 14858  
 14859      city          = listing["city"] or "South Africa"
 14860      suburb        = listing["suburb"] or ""
 14861      title         = listing["title"] or "(no title)"
 14862      desc          = listing["description"] or ""
 14863      price_raw     = listing["price"] or ""
 14864      listing_type  = (listing["listing_type"] if "listing_type" in listing.keys() else None) or ""
 14865      conn.close()
 14866  
 14867      # Pre-flight: can the buyer pay at all? (No deduction yet.)
 14868      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour.
 14869      if tier is None:
 14870          _charge = 1
 14871      else:
 14872          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "yield")}
 14873          if tier not in _offered_t:
 14874              raise HTTPException(status_code=400,
 14875                  detail=f"Tier {tier} is not available for this listing")
 14876          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 14877      _require_tuppence(email, _charge)
 14878      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 14879  
 14880      def _num(v):
 14881          try:
 14882              return float(str(v).replace("R", "").replace(",", "")
 14883                           .replace("/month", "").replace("pm", "").strip())
 14884          except Exception:
 14885              return None
 14886  
 14887      listing_amount = _num(price_raw)
 14888      lt = listing_type.lower()
 14889      is_rental = ("rent" in lt) or ("rent" in (title + " " + desc).lower() and "for sale" not in lt)
 14890  
 14891      # Resolve purchase_price (annual rent / monthly rent) from listing + caller input.
 14892      monthly_rent = None
 14893      buy_price    = None
 14894      need = None
 14895      if is_rental:
 14896          # Listing price IS the monthly rent. Need the purchase price from caller.
 14897          monthly_rent = listing_amount
 14898          buy_price    = purchase_price
 14899          if not buy_price:
 14900              need = "purchase_price"
 14901      else:
 14902          # Listing price IS the sale/purchase price. Need expected monthly rent.
 14903          buy_price    = listing_amount
 14904          monthly_rent = rent
 14905          if not monthly_rent:
 14906              need = "rent"
 14907  
 14908      # Honest 'needs input' — FREE, no Tuppence charged.
 14909      # -- STEP 3: source the missing half from a FREE/owned feed (per tier+country)
 14910      _country_y = _listing_country_iso2(listing)
 14911      _rent_src = "your figure"
 14912      _price_src = "the listing"
 14913      if need and tier is not None:
 14914          _filled = await _yield_fill_missing(need, tier, _country_y, city, suburb, listing, listing_id)
 14915          if _filled:
 14916              if need == "rent":
 14917                  monthly_rent = _filled["value"]; _rent_src = _filled["provenance"]
 14918              else:
 14919                  buy_price = _filled["value"]; _price_src = _filled["provenance"]
 14920              need = None
 14921  
 14922      if need or not buy_price or not monthly_rent or buy_price <= 0 or monthly_rent <= 0:
 14923          bal = _current_tuppence(email)
 14924          prompt_for = ("the expected monthly rent" if need == "rent"
 14925                        else "the likely purchase price" if need == "purchase_price"
 14926                        else "both the purchase price and the monthly rent")
 14927          return {
 14928              "status":           "needs_input",
 14929              "charged":          False,
 14930              "need":             need or "both",
 14931              "listing_amount":   listing_amount,
 14932              "is_rental":        is_rental,
 14933              "message":          (f"To calculate a real yield we need {prompt_for}. "
 14934                                   f"Enter it and we\u2019ll compute the actual figure — "
 14935                                   f"no Tuppence is charged until we do."),
 14936              "tuppence_remaining": bal,
 14937          }
 14938  
 14939      # ── REAL computation in Python (deterministic, auditable) ──────────────────
 14940      annual_rent = monthly_rent * 12.0
 14941      gross = (annual_rent / buy_price) * 100.0
 14942  
 14943      # Net estimate: subtract a transparent cost band (rates, levies, maintenance,
 14944      # vacancy). We show the assumption rather than hiding it inside a model guess.
 14945      # STEP 3: versioned, dated per-region net-cost band replaces the flat 3%.
 14946      _band = tier_resolvers.net_cost_band(_country_y)
 14947      NET_COST_PCT = float(_band.get("typical", 3.0))
 14948      net = gross - NET_COST_PCT
 14949  
 14950      # LLM writes ONLY the qualitative benchmark sentence — handed the real numbers.
 14951      location_str = f"{suburb}, {city}" if suburb else city
 14952      _BENCHMARKS = {
 14953          "ZA": ("SA GROSS YIELD BENCHMARKS (2026): Pretoria residential 7-10%, "
 14954                 "Cape Town 5-7%, Johannesburg 6-9%, Durban 7-10%, secondary cities 8-12%, "
 14955                 "commercial 9-12%, student accommodation 10-14%."),
 14956          "UK": ("UK GROSS YIELD BENCHMARKS: prime London 3-5%, regional cities 5-8%, "
 14957                 "northern England 6-9%."),
 14958          "US": ("US GROSS YIELD BENCHMARKS: coastal metros 3-5%, Sunbelt 5-8%, "
 14959                 "Midwest/secondary 7-10%."),
 14960          "AU": "AU GROSS YIELD BENCHMARKS: Sydney/Melbourne 2.5-4%, Brisbane/Perth 4-6%.",
 14961      }
 14962      sa_benchmarks = _BENCHMARKS.get(_country_y, _BENCHMARKS["ZA"])
 14963      system_prompt = (
 14964          "You are a property market analyst. You are GIVEN a computed gross "
 14965          "yield — never recalculate or contradict it. Write one honest sentence placing "
 14966          "it against the local benchmark. No filler, no 'buy now'. "
 14967          "Respond with a single valid JSON object — no markdown."
 14968      )
 14969      user_prompt = (
 14970          f"Property in {location_str} ({_country_y}).\n"
 14971          f"Purchase price: R{buy_price:,.0f}. Monthly rent: R{monthly_rent:,.0f}. "
 14972          f"COMPUTED gross yield: {gross:.1f}% (annual rent / purchase price).\n"
 14973          f"{sa_benchmarks}\n"
 14974          "Return JSON: {\"market_context\": \"<one honest sentence vs the benchmark for "
 14975          "this city/type>\", \"sa_yield_benchmark\": \"<the matching benchmark, e.g. "
 14976          "Pretoria residential: 7-10% gross>\"}"
 14977      )
 14978  
 14979      try:
 14980          _sr = await asyncio.to_thread(
 14981              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14982              task="haiku", max_tokens=250, system=system_prompt,
 14983              provider=_ts_active_provider(), timeout=20)
 14984          raw = _sr.text.strip()
 14985          _yc_in, _yc_out = _sr.in_tokens, _sr.out_tokens   # C2/C3
 14986          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14987          raw = _re_match.sub(r"\s*```$", "", raw)
 14988          result = json.loads(raw)
 14989          market_context     = str(result.get("market_context", ""))[:400]
 14990          sa_yield_benchmark = str(result.get("sa_yield_benchmark", ""))[:120]
 14991      except Exception as exc:
 14992          # The model only writes the narrative; if it fails we STILL have the real
 14993          # numbers. Degrade gracefully with a neutral sentence rather than failing —
 14994          # but only charge because the core (computed) service succeeded.
 14995          _log.warning("ai-yield-calc narration failed (numbers still valid): %s", exc)
 14996          market_context = (f"Computed gross yield {gross:.1f}% on a R{buy_price:,.0f} "
 14997                            f"purchase at R{monthly_rent:,.0f}/month.")
 14998          sa_yield_benchmark = "SA residential benchmark: ~7-10% gross (varies by city)."
 14999          _yc_in, _yc_out = None, None   # narration failed — flat estimate
 15000  
 15001      # DELIVER-THEN-CHARGE: a real, computed yield was produced — charge now.
 15002      if _charge and _charge > 0:
 15003          cc = database.get_db()
 15004          try:
 15005              remaining = _deduct_tuppence(
 15006                  cc, email, _charge,
 15007                  f"AI Yield Calc \u00b7 #{listing_id} \u00b7 {title[:40]}"
 15008              )
 15009              cc.commit()
 15010          finally:
 15011              cc.close()
 15012      else:
 15013          remaining = _current_tuppence(email)
 15014  
 15015      # C3 — log real AI spend for this paid call (was previously unlogged).
 15016      _log_ai_spend(email, "/listings/yield-calc", "haiku", _yc_in, _yc_out)
 15017  
 15018      _log.info("ai-yield-calc: listing #%d email=%s gross=%.1f%% charged=1T",
 15019                listing_id, email, gross)
 15020      return {
 15021          "status":                 "ok",
 15022          "charged":                True,
 15023          "computed":               True,        # numbers came from arithmetic, not a model
 15024          "gross_yield_pct":        f"{gross:.1f}%",
 15025          "net_yield_estimate_pct": f"{net:.1f}%",
 15026          "net_cost_assumption_pct": f"{NET_COST_PCT:.1f}%",
 15027          "purchase_price_used":    f"R{buy_price:,.0f}",
```

## AI5 Batch Cards (full endpoint) — from bea_main.py

```
 15058  
 15059  @app.post("/listings/batch-cards")
 15060  async def ai_batch_card_listings(req: BatchCardRequest):
 15061      """AI5: Seller pays 2T — Claude Sonnet Vision analyses up to 10 card photos and
 15062      returns an array of draft listing JSONs ready for review and publish.
 15063      Each draft contains title, description, price_suggestion, condition, category.
 15064      Capped at 10 images per call. 2T flat cost regardless of card count.
 15065      Returns {drafts: [...], cards_processed, tuppence_remaining}.
 15066      """
 15067      if not ai_provider.any_lane_configured():
 15068          raise HTTPException(status_code=503, detail="AI not configured")
 15069  
 15070      if not req.images:
 15071          raise HTTPException(status_code=400, detail="At least one image is required")
 15072      _check_cost_ceiling(req.seller_email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 15073  
 15074      # Cap at 10 cards
 15075      images = req.images[:10]
 15076      card_count = len(images)
 15077  
 15078      _require_tuppence(req.seller_email, 2)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 15079      _bc_charge_desc = f"AI Batch Cards · {card_count} card(s) · {req.city}"
 15080  
 15081      suburb_str = req.suburb or req.city
 15082      location_str = f"{suburb_str}, {req.city}"
 15083  
 15084      system_prompt = (
 15085          "You are an expert trading card and collectables appraiser and marketplace copywriter "
 15086          "for TrustSquare, a South African peer-to-peer local marketplace. "
 15087          "You identify cards/collectables from photos, assess condition, and write concise buyer-friendly listings. "
 15088          "You know SA collectables market values. "
 15089          "Always respond with a single valid JSON object — no markdown, no explanation."
 15090      )
 15091  
 15092      # Build the message content: one text block + one image block per card
 15093      content_blocks = [
 15094          {
 15095              "type": "text",
 15096              "text": (
 15097                  f"Analyse these {card_count} trading card / collectable image(s) for a seller in {location_str}, "
 15098                  "South Africa. For each image, generate a complete listing draft.\n\n"
 15099                  "For each card/item return:\n"
 15100                  '{"title": "<specific card/item name, set, year if visible, max 12 words>", '
 15101                  '"description": "<40-80 words: card details, set/series, condition notes, notable features>", '
 15102                  '"price_suggestion": "<e.g. R150 or R200–R350 depending on condition>", '
 15103                  '"condition": "mint" | "near_mint" | "excellent" | "good" | "fair" | "poor", '
 15104                  '"category": "Collectors"}\n\n'
 15105                  f'Return JSON: {{"drafts": [<one object per image in order>]}}'
 15106              )
 15107          }
 15108      ]
 15109  
 15110      for _, img_b64 in enumerate(images):
 15111          # Detect media type from base64 header or default to jpeg
 15112          media_type = "image/jpeg"
 15113          if img_b64.startswith("data:"):
 15114              header, data = img_b64.split(",", 1)
 15115              if "png" in header:
 15116                  media_type = "image/png"
 15117              elif "gif" in header:
 15118                  media_type = "image/gif"
 15119              elif "webp" in header:
 15120                  media_type = "image/webp"
 15121              img_b64 = data
 15122  
 15123          content_blocks.append({
 15124              "type": "image",
 15125              "source": {
 15126                  "type": "base64",
 15127                  "media_type": media_type,
 15128                  "data": img_b64,
 15129              }
 15130          })
 15131  
 15132      try:
 15133          # SEAM-ROUTED (P0): task="vision" — resolves to the haiku id today (Haiku-first,
 15134          # 3 Jul 2026); flipping TASK_MODEL's vision row back to sonnet re-arms the documented revert.
 15135          _sr = await asyncio.to_thread(
 15136              ai_provider.complete, [{"role": "user", "content": content_blocks}],
 15137              task="vision", max_tokens=2000, system=system_prompt,
 15138              provider=_ts_active_provider(), timeout=60)
 15139          _bc_in, _bc_out = _sr.in_tokens, _sr.out_tokens
 15140          # P2 — Tuppence covers the revenue side; log token spend so the cost
 15141          # dashboard sees it too (sweep 12 Jun 2026)
 15142          _log_ai_spend(req.seller_email, "/listings/batch-cards", "sonnet_vision", _bc_in, _bc_out)
 15143          raw = _sr.text.strip()
 15144          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 15145          raw = _re_match.sub(r"\s*```$", "", raw)
 15146          result = json.loads(raw)
 15147          drafts = result.get("drafts", [])
 15148  
 15149          # Sanitise each draft
 15150          clean_drafts = []
 15151          valid_conditions = {"mint", "near_mint", "excellent", "good", "fair", "poor"}
 15152          for d in drafts[:card_count]:
 15153              if isinstance(d, dict):
 15154                  clean_drafts.append({
 15155                      "title":            str(d.get("title", ""))[:120],
 15156                      "description":      str(d.get("description", ""))[:800],
 15157                      "price_suggestion": str(d.get("price_suggestion", ""))[:60],
 15158                      "condition":        d.get("condition", "good") if d.get("condition") in valid_conditions else "good",
 15159                      "category":         "Collectors",
 15160                      "city":             req.city,
 15161                      "suburb":           req.suburb or "",
 15162                  })
 15163  
 15164      except Exception as exc:
 15165          _log.error("ai-batch-cards: %s", exc)
 15166          raise HTTPException(status_code=500, detail="AI batch card listing failed — no Tuppence was charged") from exc
 15167  
 15168      _conn2 = database.get_db()
 15169      try:
 15170          remaining = _deduct_tuppence(_conn2, req.seller_email, 2, _bc_charge_desc)   # F2: charge on delivery
 15171          _conn2.commit()
 15172      finally:
 15173          _conn2.close()
 15174      _log.info("ai-batch-cards: seller=%s city=%s cards=%d drafts=%d",
 15175                req.seller_email, req.city, card_count, len(clean_drafts))
 15176      return {
 15177          "drafts":           clean_drafts,
 15178          "cards_processed":  card_count,
 15179          "tuppence_remaining": remaining,
 15180      }
 15181  
 15182  
 15183  
 15184  @app.get("/tuppence/history")
 15185  def get_tuppence_history(email: str, limit: int = 50, offset: int = 0):
 15186      """Return paginated tuppence transaction history with running balance."""
 15187      conn = database.get_db()
 15188      try:
 15189          # Verify user exists
 15190          user = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
 15191          if not user:
 15192              raise HTTPException(status_code=404, detail="User not found")
 15193  
 15194          total = conn.execute(
 15195              "SELECT COUNT(*) FROM transactions WHERE user_email=?", (email,)
 15196          ).fetchone()[0]
 15197  
 15198          # Get all rows ascending to compute running balances
 15199          all_rows = conn.execute(
 15200              "SELECT id, type, amount, description, created_at "
 15201              "FROM transactions WHERE user_email=? ORDER BY id ASC",
 15202              (email,)
 15203          ).fetchall()
 15204  
 15205          # Compute running balance_after for each row (cumulative sum)
 15206          running = 0
 15207          balance_after = []
```

## KYC identity verification (vision, cost-guarded) — from bea_main.py

```
  9763  
  9764  
  9765  async def _sonnet_verify_identity(doc_url: str, claimed_name: str,
  9766                                     claimed_id: str, doc_type: str, email: str = "") -> dict:
  9767      """Call Sonnet vision to verify identity document.
  9768      SWAP POINT: replace this function with PaddleOCR/PassportEye for zero-token operation.
  9769      Self-contained cost guard (P2, 22 Jul 2026): checks the daily ceiling BEFORE the call
  9770      (raises HTTPException 429, same as every other paid endpoint) and logs spend itself
  9771      so this helper stays metered even if a future caller forgets to.
  9772      Returns: {verified(bool), confidence(float), extracted_name(str),
  9773                extracted_id(str), notes(str), model(str)}"""
  9774      if not ai_provider.any_lane_configured():
  9775          return {"verified": False, "confidence": 0.0, "extracted_name": "",
  9776                  "extracted_id": "", "notes": "AI verification unavailable — API key not set",
  9777                  "model": "none"}
  9778      _check_cost_ceiling(email)   # C1 — refuse if daily cost ceiling reached
  9779      try:
  9780          # Fetch the document image (KYC-SSRF-1: allowlisted host, no redirects, size-capped)
  9781          img_bytes = _fetch_kyc_document(doc_url)
  9782          img_b64 = base64.standard_b64encode(img_bytes).decode()
  9783          # Detect media type
  9784          media_type = "image/jpeg"
  9785          if doc_url.lower().endswith(".png"):
  9786              media_type = "image/png"
  9787          elif doc_url.lower().endswith(".webp"):
  9788              media_type = "image/webp"
  9789  
  9790          # SEAM-ROUTED (P0, 17 Jul 2026): KYC vision call goes through ai_provider.complete()
  9791          # with task="sonnet" — same claude-sonnet-4-6 on the Anthropic path as the old SDK call.
  9792          prompt = f"""You are a document verification assistant for TrustSquare marketplace.
  9793  Examine this identity document image carefully.
  9794  
  9795  The seller claims:
  9796  - Full name: {claimed_name}
  9797  - ID/passport number: {claimed_id}
  9798  - Document type: {doc_type}
  9799  
  9800  Your task:
  9801  1. Extract the FULL NAME exactly as printed on the document
  9802  2. Extract the ID NUMBER / PASSPORT NUMBER exactly as printed
  9803  3. Determine if the claimed name matches the document name (allow for initials, middle names)
  9804  4. Determine if the claimed number matches the document number
  9805  
  9806  Respond ONLY with valid JSON in this exact format:
  9807  {{
  9808    "extracted_name": "<full name from document>",
  9809    "extracted_id": "<id/passport number from document>",
  9810    "name_match": <true/false>,
  9811    "id_match": <true/false>,
  9812    "confidence": <0.0-1.0>,
  9813    "document_appears_genuine": <true/false>,
  9814    "notes": "<any concerns or observations, empty string if none>"
  9815  }}
  9816  
  9817  If you cannot read the document clearly, set confidence below 0.5 and explain in notes."""
  9818  
  9819          _sr = ai_provider.complete(
  9820              [{
  9821                  "role": "user",
  9822                  "content": [
  9823                      {"type": "image", "source": {
  9824                          "type": "base64", "media_type": media_type, "data": img_b64
  9825                      }},
  9826                      {"type": "text", "text": prompt}
  9827                  ]
  9828              }],
  9829              task="sonnet", max_tokens=300,
  9830              provider=_ts_active_provider(), allow_fallback=False, timeout=120)   # KYC-PIN-1 (F3): ID docs never fan out to standby vendors
  9831          raw = _sr.text.strip()
  9832          # Parse JSON from response
  9833          json_match = re.search(r'\{[\s\S]*\}', raw)
  9834          if not json_match:
  9835              raise ValueError("No JSON in Sonnet response")
  9836          result = json.loads(json_match.group())
  9837          verified = (result.get("name_match") and result.get("id_match") and
  9838                      result.get("confidence", 0) >= 0.75 and
  9839                      result.get("document_appears_genuine", True))
  9840          _log_ai_spend(email, "/users/verify-identity", "sonnet_vision",
  9841                        getattr(_sr, "in_tokens", None), getattr(_sr, "out_tokens", None))
  9842          return {
  9843              "verified": bool(verified),
  9844              "confidence": float(result.get("confidence", 0)),
  9845              "extracted_name": result.get("extracted_name", ""),
  9846              "extracted_id": result.get("extracted_id", ""),
  9847              "notes": result.get("notes", ""),
  9848              "model": SONNET_MODEL,
  9849          }
  9850      except HTTPException:
  9851          raise
  9852      except Exception as e:
  9853          return {"verified": False, "confidence": 0.0, "extracted_name": "",
  9854                  "extracted_id": "", "notes": f"Verification error: {str(e)}", "model": SONNET_MODEL}
  9855  
  9856  
  9857  class IdentityVerifyIn(BaseModel):
  9858      id_number: str          # SA ID (13 digits) or passport number
  9859      full_name: str          # As it appears on the document
  9860      doc_type: str = "sa_id" # sa_id | passport | national_id
  9861      doc_url: str            # URL of the already-uploaded ID document in R2
  9862  
  9863  
  9864  class BankingIn(BaseModel):
  9865      account_holder: str
  9866      bank_name: str
  9867      account_number: str   # We store last 4 digits only
  9868      branch_code: str = ""
  9869  
  9870  
  9871  @app.post("/users/{email}/verify-identity")
  9872  async def verify_identity(
```

## /admin/ai-restore + /flags provider block — from bea_main.py

```
 12617      return {"services": out, "checked_at": datetime.utcnow().isoformat() + "Z"}
 12618  
 12619  @app.post("/admin/ai-restore")
 12620  def admin_ai_restore(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12621      """P2a: MANUAL restore — the ONLY path back to traffic for a banned (T3) lane
 12622      (David's ruling 31 Jul: dropouts auto-recover, bans wait for the operator)."""
 12623      _p = ((payload or {}).get("provider") or "").strip()
 12624      _t = ((payload or {}).get("task") or "").strip() or None
 12625      if _p not in ai_provider.ADAPTERS:
 12626          raise HTTPException(status_code=400, detail="unknown provider")
 12627      try:
 12628          import ai_breaker as _brk
 12629          n = _brk.restore(_p, _t, who="dashboard-admin")
 12630          _log.warning("AI-BREAKER manual restore: %s/%s (%d rows)", _p, _t or "ALL", n)
 12631          return {"restored": n, "provider": _p, "task": _t or "ALL"}
 12632      except Exception as e:
 12633          raise HTTPException(status_code=500, detail="restore failed: " + str(e)[:120]) from e
 12634  
 12635  @app.post("/admin/ai-test")   # AITEST-ROUTE-1 (17 Jul, found live by David's demo): decorator was pasted onto demand_sweep; real tester was never registered
 12636  def admin_ai_test(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12637      """David-only: run a tiny prompt through the ACTIVE provider via the ai_provider seam
 12638      (full translate+call+parse path). Lets the Page-4 switch be tested live against either
 12639      provider without touching the 15 production call sites. Returns the text + which provider/model answered."""
 12640      _req_prov=((payload or {}).get("provider") or "").strip()   # P1: optional explicit provider
 12641      if _req_prov and _req_prov not in ai_provider.ADAPTERS:
 12642          raise HTTPException(status_code=400, detail="unknown provider: "+_req_prov[:40])
 12643      try:
 12644          import ai_provider as _ap
 12645          prov=_req_prov or _ts_active_provider()
 12646          prompt=((payload or {}).get("prompt") or "Reply with exactly: TrustSquare AI provider test OK.").strip()
 12647          r=_ap.complete([{"role":"user","content":prompt}], task="haiku", max_tokens=40, provider=prov)
 12648          return {"ok": bool(r.ok), "provider": r.provider, "model": r.model,
 12649                  "text": (r.text or "")[:400], "in_tokens": r.in_tokens, "out_tokens": r.out_tokens}
 12650      except Exception as e:
 12651          raise HTTPException(status_code=500, detail="ai-test failed: "+str(e)[:160]) from e
 12652  
 12653  
 12654  class _FlagsUpdate(BaseModel):
 12655      mode:          Optional[str]  = None
 12656      verified_tier: Optional[bool] = None
 12657      videos:        Optional[bool] = None
 12658      data_ops:      Optional[bool] = None
 12659      data_places:   Optional[bool] = None
 12660      data_flights:  Optional[bool] = None
 12661      data_mapbox:   Optional[bool] = None
 12662      p_heritage:    Optional[bool] = None
 12663      p_expedition:  Optional[bool] = None
 12664      p_weekend:     Optional[bool] = None
 12665      # BIT safe-state flags (Mitigator-writable; see §13.1)
 12666      ai_example_enabled:    Optional[bool] = None
 12667      auth_fail_closed:      Optional[bool] = None
 12668      tuppence_burn_enabled: Optional[bool] = None
 12669      ai_active:             Optional[str]  = None  # AI provider seam: 'anthropic' | 'openai' | 'scaleway' (Page-4 switch)
 12670      ai_active_override:    Optional[str]  = None  # MANUAL PIN: provider = pin (TTL decay) | '' = unpin (1 Aug 2026)
 12671      fault_report:          Optional[bool] = None  # MAINT-B1b: in-app tester fault intake visible
 12672  
 12673  def _flags_payload(d):
 12674      def b(k): return bool(d.get(k, 0))
 12675      live = (d.get("mode", "launch") == "live")
 12676      return {
 12677          "mode": d.get("mode", "launch"),
 12678          "verified_tier": b("verified_tier"), "videos": b("videos"),
 12679          "fault_report": b("fault_report"),
 12680          "data": {"ops": b("data_ops"), "places": b("data_places"),
 12681                   "flights": b("data_flights"), "mapbox": b("data_mapbox")},
 12682          "planners": {"heritage": b("p_heritage"), "expedition": b("p_expedition"),
 12683                       "weekend": b("p_weekend")},
 12684          "effective": {
 12685              "verified_visible":    live and b("verified_tier"),
 12686              "videos_visible":      b("videos"),  # decoupled from live mode (David 29 Jun): dashboard videos toggle controls it on its own; verified/paid-feed gates stay live-gated
 12687              "heritage_verified":   live and b("verified_tier") and b("p_heritage"),
 12688              "expedition_verified": live and b("verified_tier") and b("p_expedition"),
 12689              "weekend_verified":    live and b("verified_tier") and b("p_weekend"),
 12690          },
 12691          "bit_flags": {
 12692              "ai_example_enabled":    bool(d.get("ai_example_enabled", 1)),
 12693              "auth_fail_closed":      bool(d.get("auth_fail_closed", 0)),
 12694              "tuppence_burn_enabled": bool(d.get("tuppence_burn_enabled", 1)),
 12695          },
 12696          "ai_provider": {
 12697              # effective = the lane calls actually use RIGHT NOW (pin-aware); standing = the
 12698              # auto/default lane the system returns to when the pin decays.
 12699              "active": _ts_active_provider(),   # pin-aware effective lane
 12700              "standing": d.get("ai_active", "anthropic"),
 12701              "override": ({"provider": _TS_AI_CACHE["override"], "expires_at": _TS_AI_CACHE["expires"]}
 12702                            if _TS_AI_CACHE.get("override") else None),
 12703              "override_ttl_hours": AI_OVERRIDE_TTL_HOURS,
 12704              "funnel": _ts_funnel_snapshot(),
 12705              # FAIL-OPEN here too (FLAGS-BRK-1, 1 Aug): a missing/broken breaker module must
 12706              # never take /flags down — the card degrades, the platform does not.
 12707              "breaker": _ts_breaker_safe("snapshot"),
 12708              "drill": _ts_breaker_safe("drill"),
 12709              # which providers have a REAL adapter wired (vs stub) — Page 4 greys out the stubs
 12710              "available": {"anthropic": bool(ANTHROPIC_API_KEY), "openai": bool(ai_provider.envkey("OPENAI_API_KEY")),
 12711                            "scaleway": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY"))},
 12712              # P1: ordered provider cards for the NEW dashboard UI (old card keeps reading active/available above)
 12713              "providers": [
 12714                  {"id": "anthropic", "label": "Anthropic (Claude)", "family": "us", "jurisdiction": "US",
 12715                   "available": bool(ANTHROPIC_API_KEY),
 12716                   "models": ai_provider.TASK_MODEL.get("anthropic", {})},
 12717                  {"id": "scaleway", "label": "Scaleway EU", "family": "open", "jurisdiction": "EU · Paris",
 12718                   "available": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")),
 12719                   "models": ai_provider.TASK_MODEL.get("scaleway", {})},
 12720                  {"id": "openai", "label": "OpenAI (GPT-5.6)", "family": "us", "jurisdiction": "US",
 12721                   "available": bool(ai_provider.envkey("OPENAI_API_KEY")),
 12722                   "models": ai_provider.TASK_MODEL.get("openai", {})},
 12723              ],
 12724          },
 12725          "updated_at": d.get("updated_at", ""),
 12726      }
 12727  
 12728  def _ts_breaker_safe(what):
 12729      try:
 12730          import ai_breaker as _b
 12731          if what == "snapshot": return _b.snapshot()
 12732          return sorted(_b.drill_banned()) or None
 12733      except Exception:
 12734          return None
 12735  
 12736  _TS_FUNNEL_CACHE = {"mtime": None, "data": None}
 12737  def _ts_funnel_snapshot():
 12738      """The +1 card's funnel strip: ORDER AND GATE-TYPES ONLY (David 1 Aug 2026 — no numbers).
 12739      Read from ai_funnel_snapshot.json, generated by scripts/price_truth.py --snapshot (ONE
 12740      ranking engine); absent file -> None, dashboard shows nothing. Cached on mtime."""
 12741      import os as _os
 12742      p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ai_funnel_snapshot.json")
 12743      try:
 12744          mt = _os.path.getmtime(p)
 12745          if _TS_FUNNEL_CACHE["mtime"] != mt:
 12746              with open(p, encoding="utf-8") as fh:
 12747                  _TS_FUNNEL_CACHE.update(mtime=mt, data=json.load(fh))
 12748          return _TS_FUNNEL_CACHE["data"]
 12749      except Exception:
 12750          return None
 12751  
 12752  @app.get("/flags")
 12753  def get_flags():
 12754      """Public — buyer app + dashboard read launch-switch state. Safe default = launch/free-only."""
 12755      conn = database.get_db()
 12756      try:
 12757          row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
 12758      finally:
 12759          conn.close()
 12760      return _flags_payload(dict(row) if row else {})
 12761  
 12762  @app.post("/admin/flags")
 12763  def set_flags(upd: _FlagsUpdate, _admin=Depends(_require_admin)):
 12764      """Admin (JWT) — flip the launch switch. Writes the singleton row, returns full state."""
 12765      data = upd.dict(exclude_unset=True)
 12766      sets, vals = [], []
```

## /admin/ai-spend summary endpoint — from bea_main.py

```
  4915  # ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
  4916  
  4917  @app.get("/admin/ai-spend/summary")
  4918  def admin_ai_spend_daily_summary(_admin=Depends(_require_admin_or_key)):
  4919      """Live AI-spend summary for the nightly cost-compliance sweep (P2, 11 Jun 2026).
  4920      Returns today's and 7-day spend, the configured ceilings, and a 7-day
  4921      per-endpoint/model breakdown. Read-only; $0; admin key required."""
  4922      conn = database.get_db()
  4923      try:
  4924          today = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
  4925          week = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
  4926          t = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  4927                           "FROM ai_spend_log WHERE logged_at >= ?", (today,)).fetchone()
  4928          w = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  4929                           "FROM ai_spend_log WHERE logged_at >= ?", (week,)).fetchone()
  4930          cfg = conn.execute("SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  4931                             "FROM ai_spend_config WHERE id = 1").fetchone()
  4932          by_ep = conn.execute(
  4933              "SELECT endpoint, model, COALESCE(SUM(est_cost_usd),0) AS usd, COUNT(*) AS calls, "
  4934              "SUM(cost_is_real) AS real_rows FROM ai_spend_log WHERE logged_at >= ? "
  4935              "GROUP BY endpoint, model ORDER BY usd DESC LIMIT 25", (week,)).fetchall()
  4936      finally:
  4937          conn.close()
  4938      return {
  4939          "today_usd": round(t["u"], 4), "today_calls": t["n"],
  4940          "week_usd": round(w["u"], 4), "week_calls": w["n"],
  4941          "daily_user_ceiling_usd": (cfg["daily_user_ceiling_usd"] if cfg else 0) or 0,
  4942          "daily_platform_ceiling_usd": (cfg["daily_platform_ceiling_usd"] if cfg else 0) or 0,
  4943          "ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
  4944                              else "platform ceiling is 0/unset — AI spend is UNCAPPED"),
  4945          "by_endpoint": [{"endpoint": r["endpoint"], "model": r["model"],
  4946                           "usd": round(r["usd"], 4), "calls": r["calls"],
  4947                           "estimated_rows": r["calls"] - (r["real_rows"] or 0)} for r in by_ep],
  4948      }
  4949  
  4950  
  4951  @app.post("/admin/migrate-photos")
  4952  def migrate_photos(_admin=Depends(_require_admin_or_key)):
  4953      """Migrate existing local photos to Hetzner Object Storage.
  4954      Idempotent — skips listings already pointing to an S3 URL.
  4955      Does NOT delete local files.
  4956      Returns: { migrated, failed, skipped }
  4957      """
  4958      if not _S3_CONFIGURED:
  4959          raise HTTPException(status_code=503, detail="Object Storage not configured — set HETZNER_S3_* env vars")
  4960      conn = database.get_db()
  4961      rows = conn.execute(
  4962          "SELECT id, thumb_url, medium_url FROM listings WHERE thumb_url LIKE '/media/%'"
  4963      ).fetchall()
  4964      migrated = failed = skipped = 0
  4965      for row in rows:
  4966          listing_id  = row["id"]
  4967          thumb_path  = row["thumb_url"]  or ""
  4968          medium_path = row["medium_url"] or ""
  4969          if not thumb_path.startswith("/media/"):
```

## Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop — from bea_main.py

```
 16910  
 16911  
 16912  # ── SCOREBOARD-1 (3 Aug 2026): the silent scoreboard agent, nightly ──────────
 16913  # The SLOW-signal half of the failover programme (fast signals = ai_breaker):
 16914  # probes every configured lane x task tier each night at 03:33 SAST (01:33 UTC,
 16915  # after the 03:17 backup), stores history in ai_scoreboard_probes (primary DB,
 16916  # so it rides the backup lanes), writes the rolling 90-day ranking to
 16917  # ai_scoreboard.json. Quality is a GATE not a weight (golden-set registry).
 16918  # Spend-gated OFF by default — launch_switches.scoreboard_enabled=1
 16919  # (enable_scoreboard.bat) is David's explicit click. Import-guarded and
 16920  # exception-walled: a scoreboard failure can never hurt the app.
 16921  try:
 16922      import ai_scoreboard as _ts_scoreboard
 16923  except Exception as _ts_sb_err:
 16924      _ts_scoreboard = None
 16925      print("SCOREBOARD-1: module not importable (%s) — nightly probes off" % _ts_sb_err)
 16926  
 16927  if _ts_scoreboard is not None:
 16928      @app.on_event("startup")
 16929      async def _ts_scoreboard_nightly():
 16930          async def _sb_loop():
 16931              while True:
 16932                  _now = datetime.now(timezone.utc)
 16933                  _nxt = _now.replace(hour=1, minute=33, second=0, microsecond=0)
 16934                  if _nxt <= _now:
 16935                      _nxt += timedelta(days=1)
 16936                  await asyncio.sleep(max(60.0, (_nxt - _now).total_seconds()))
 16937                  try:
 16938                      await asyncio.get_running_loop().run_in_executor(
 16939                          None, _ts_scoreboard.run_nightly)
 16940                  except Exception as _sb_e:
 16941                      print("SCOREBOARD-1 nightly error: %s" % _sb_e)
 16942          asyncio.get_running_loop().create_task(_sb_loop())
 16943  
 16944  
 16945  # ── HEARTBEAT-1 (5 Aug 2026, David's F5 ruling: live NOW, confidence before launch) ──
 16946  # P2c idle-recovery heartbeat per AI_AUTO_FAILOVER_P2_DESIGN §6: every 60 s, if any
 16947  # breaker row is eligible (tripped/half_open, probe window open), claim and send ONE
 16948  # direct probe — one per tick TOTAL, round-robin, so a bad night can never multiply
 16949  # cost. Text ping only (~$0.00002); T3 rows carry hourly probe_after, so bans probe
 16950  # hourly. Spend is logged like all spend. Fail-open: any error waits for the next tick.
 16951  @app.on_event("startup")
 16952  async def _ts_breaker_heartbeat():
 16953      async def _hb_loop():
 16954          _rr = 0
 16955          while True:
 16956              await asyncio.sleep(60)
 16957              try:
 16958                  import ai_breaker as _hb_brk
 16959                  if getattr(_hb_brk, "_get_db", None) is None:
 16960                      continue   # breaker unattached — nothing to probe
 16961                  _hb_conn = database.get_db()
 16962                  try:
 16963                      _rows = _hb_conn.execute(
 16964                          "SELECT provider, task FROM ai_breaker "
 16965                          "WHERE state IN ('tripped','half_open') "
 16966                          "AND (probe_after IS NULL OR probe_after <= ?) "
 16967                          "ORDER BY provider, task",
 16968                          (datetime.utcnow().isoformat(timespec="seconds"),)).fetchall()
 16969                  finally:
 16970                      _hb_conn.close()
 16971                  if not _rows:
 16972                      continue
 16973                  _row = _rows[_rr % len(_rows)]; _rr += 1
 16974                  _p, _t = _row["provider"], _row["task"]
 16975                  if not _hb_brk.claim_probe(_p, _t):
 16976                      continue   # someone else holds the half-open lease
 16977                  _r = await asyncio.to_thread(
 16978                      ai_provider.complete, [{"role": "user", "content": "ping"}],
 16979                      task=_t, max_tokens=8, provider=_p, probe=True, timeout=20)
 16980                  _log_ai_spend("system:heartbeat", "/breaker/heartbeat", _t,
 16981                                _r.in_tokens, _r.out_tokens)
 16982              except Exception as _hb_e:
 16983                  print("HEARTBEAT-1 error: %s" % _hb_e)
 16984      asyncio.get_running_loop().create_task(_hb_loop())
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
   976       App categories:  Listings/Adverts purple · Trust&Safety green · Search blue ·
   977                        Tuppence cyan · Ops amber
   978       Task tiers:      haiku sky · sonnet violet · vision pink · triage gold
   979       Vendor lanes:    Anthropic terracotta · OpenAI green · Scaleway purple
   980       Status:          ok green · warn amber · fail red · no-key grey            */
   981    var CAT={listings:'#8b5cf6',trust:'#10b981',search:'#3b82f6',tuppence:'#06b6d4',ops:'#f59e0b'};
   982    var TIER={haiku:'#38bdf8',sonnet:'#a78bfa',vision:'#f472b6',triage:'#fbbf24'};
   983    var LANE={anthropic:'#e07a5f',openai:'#10a37f',scaleway:'#8b5cf6'};
   984    var STAT={ok:'#22c55e',warn:'#eab308',fail:'#ef4444',nokey:'#6b7280'};
   985  
   986    /* ════════ 1 · AI PROVIDERS MAP ════════ */
   987    window.msVizBuildAI=function(){
   988      var d=window._apv3||{active:'anthropic',standing:'anthropic',override:null,providers:[]};
   989      var avail={}; (d.providers||[]).forEach(function(p){avail[p.id]=!!p.available;});
   990      if(!(d.providers||[]).length){avail={anthropic:true};}
   991      var groups=[
   992        {id:'listings',name:'LISTINGS &amp; ADVERTS',c:CAT.listings,items:[
   993          {n:'Advert coach &amp; super-adverts',t:['sonnet','haiku']},
   994          {n:'Mode B anonymity rewrite',t:['sonnet']},
   995          {n:'Import photo scan',t:['sonnet','vision']}]},
   996        {id:'trust',name:'TRUST &amp; SAFETY',c:CAT.trust,items:[
   997          {n:'KYC ID verification',t:['sonnet','vision']},
   998          {n:'Photo checks — orientation &middot; anonymity',t:['vision']}]},
   999        {id:'search',name:'SEARCH &amp; DISCOVERY',c:CAT.search,items:[
  1000          {n:'Search interpretation',t:['haiku']}]},
  1001        {id:'tuppence',name:'TUPPENCE AI SERVICES',c:CAT.tuppence,items:[
  1002          {n:'Tier 1 &amp; 2 buyer/seller services',t:['haiku','sonnet']}]},
  1003        {id:'ops',name:'OPS &amp; ADMIN',c:CAT.ops,items:[
  1004          {n:'Email triage',t:['triage']},
  1005          {n:'Provider self-test (this dashboard)',t:['haiku']}]}
  1006      ];
  1007      var s='';
  1008      s+='<defs><filter id="msvGlow" x="-40%" y="-40%" width="180%" height="180%">'+
  1009         '<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';
  1010      /* column headings */
  1011      s+=txt(180,32,'APP FEATURES',12,'#64748b',800,'middle','2px');
  1012      s+=txt(487,32,'TASK TIERS',12,'#64748b',800,'middle','2px');
  1013      s+=txt(770,32,'THE SEAM',12,'#64748b',800,'middle','2px');
  1014      s+=txt(1170,32,'VENDOR LANES',12,'#64748b',800,'middle','2px');
  1015  
  1016      /* tier chips */
  1017      var tiers={haiku:{y:170,d:'everyday text'},sonnet:{y:290,d:'heavy reasoning'},vision:{y:410,d:'image analysis'},triage:{y:530,d:'inbox sorting'}};
  1018      Object.keys(tiers).forEach(function(k){var t=tiers[k];
  1019        s+=box(432,t.y-26,112,52,TIER[k],'#0d1526',26);
  1020        s+=txt(488,t.y-2,k,14,TIER[k],800,'middle');
```


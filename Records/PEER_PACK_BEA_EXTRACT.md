# PEER PACK — bea_main.py targeted extract

*Generated 2026-08-05 09:56 UTC from bea_main.py (16867 lines). Each line keeps its REAL line number*
*so citations are checkable against the repo. Sections chosen for the AI services audit;*
*anything outside them is available on request — say which line range you need.*

## Vendor-neutral endpoint gates (F1 fix) — all occurrences

Lines gating with `if not ai_provider.any_lane_configured():` -> [3319, 4962, 5082, 5158, 5234, 8901, 9117, 9655, 13749, 13836, 14418, 14728, 14950, 15208, 16094]

## Breaker wiring at BEA startup (attach + alert hook)

```python
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

## ai_spend_config schema + ceiling columns

```python
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
   716      # Launch Switch (free-only <-> verified) — singleton flag row; default = launch/free-only
   717      conn.execute("""CREATE TABLE IF NOT EXISTS launch_switches (
   718          id            INTEGER PRIMARY KEY CHECK (id = 1),
   719          mode          TEXT    NOT NULL DEFAULT 'launch',
   720          verified_tier INTEGER NOT NULL DEFAULT 0,
   721          videos        INTEGER NOT NULL DEFAULT 0,
   722          data_ops      INTEGER NOT NULL DEFAULT 0,
   723          data_places   INTEGER NOT NULL DEFAULT 0,
   724          data_flights  INTEGER NOT NULL DEFAULT 0,
   725          data_mapbox   INTEGER NOT NULL DEFAULT 0,
   726          p_heritage    INTEGER NOT NULL DEFAULT 0,
   727          p_expedition  INTEGER NOT NULL DEFAULT 0,
   728          p_weekend     INTEGER NOT NULL DEFAULT 0,
   729          -- BIT safe-state flags (Mitigator flips these to a SAFE value on a confirmed BIT failure).
   730          -- Defaults = NORMAL/healthy state; the Mitigator only ever moves them toward safe.
   731          ai_example_enabled     INTEGER NOT NULL DEFAULT 1,
   732          auth_fail_closed       INTEGER NOT NULL DEFAULT 0,
   733          tuppence_burn_enabled  INTEGER NOT NULL DEFAULT 1,
   734          -- AI provider seam (D1): live-switchable inference vendor (Page-4 control). Default = anthropic.
   735          ai_active     TEXT    NOT NULL DEFAULT 'anthropic',
   736          -- MANUAL PIN (David 1 Aug 2026): operator override with DECAY — precedence over any
   737          -- auto selection while unexpired; expiry returns control to the standing lane.
   738          ai_active_override  TEXT,
   739          ai_override_expires TEXT,
   740          -- MAINT-B1b: in-app tester fault intake. OFF by default (fail-closed).
   741          fault_report  INTEGER NOT NULL DEFAULT 0,
   742          updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
   743      )""")
   744      conn.execute("INSERT OR IGNORE INTO launch_switches (id) VALUES (1)")
   745      # BIT safe-state flags — add to pre-existing launch_switches rows (idempotent).
   746      for _ddl in (
   747          "ALTER TABLE launch_switches ADD COLUMN ai_example_enabled    INTEGER NOT NULL DEFAULT 1",
   748          "ALTER TABLE launch_switches ADD COLUMN auth_fail_closed      INTEGER NOT NULL DEFAULT 0",
   749          "ALTER TABLE launch_switches ADD COLUMN tuppence_burn_enabled INTEGER NOT NULL DEFAULT 1",
   750          "ALTER TABLE launch_switches ADD COLUMN ai_active TEXT NOT NULL DEFAULT 'anthropic'",
   751          "ALTER TABLE launch_switches ADD COLUMN ai_active_override TEXT",
   752          "ALTER TABLE launch_switches ADD COLUMN ai_override_expires TEXT",
   753          "ALTER TABLE launch_switches ADD COLUMN fault_report INTEGER NOT NULL DEFAULT 0",
   754      ):
   755          try:
   756              conn.execute(_ddl)
   757          except Exception:
   758              pass
   759      # C1 (Session 97) — HARD daily cost ceilings (USD), per-user + platform. 0 = off.
   760      # When the day's spend reaches the cap, the next paid AI call is REFUSED (429).
   761      for _col, _ddl in (
   762          ("daily_user_ceiling_usd",     "ALTER TABLE ai_spend_config ADD COLUMN daily_user_ceiling_usd     REAL NOT NULL DEFAULT 0.50"),
   763          ("daily_platform_ceiling_usd", "ALTER TABLE ai_spend_config ADD COLUMN daily_platform_ceiling_usd REAL NOT NULL DEFAULT 100.0"),
   764      ):
   765          try:
   766              conn.execute(_ddl)
   767          except Exception:
   768              pass
   769  
   770      # AI Email Triage (Session 94) — one row per inbound email handled by POST /email/inbound
   771      conn.execute("""CREATE TABLE IF NOT EXISTS email_triage (
```

## Spend logging, alerting, cost ceiling

```python
  1491  
  1492  
  1493  def _log_ai_spend(email: str, endpoint: str, model_key: str,
  1494                    in_tok: int | None = None, out_tok: int | None = None):
  1495      """Background task: log AI call cost + trigger alert check if threshold crossed.
  1496      Non-blocking — called via background_tasks.add_task() after every AI call.
  1497      Never raises — log errors only.
  1498  
  1499      C2 (Session 97): real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
  1500      No tokens (legacy sites) -> flat _AI_COST estimate, cost_is_real=0. Backward compatible.
  1501      """
  1502      try:
  1503          if in_tok is not None or out_tok is not None:
  1504              it, ot = int(in_tok or 0), int(out_tok or 0)
  1505              cost = _token_cost(model_key, it, ot)
  1506              is_real = 1
  1507          else:
  1508              it, ot = 0, 0
  1509              cost = _AI_COST.get(model_key, 0.0023)
  1510              is_real = 0
  1511          try:
  1512              _prov = _ts_active_provider()   # P1: provider attribution — signature & call sites unchanged
  1513          except Exception:
  1514              _prov = 'anthropic'
  1515          conn = database.get_db()
  1516          try:
  1517              conn.execute(
  1518                  "INSERT INTO ai_spend_log "
  1519                  "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real, provider) "
  1520                  "VALUES (?,?,?,?,?,?,?,?)",
  1521                  (email or '', endpoint, model_key, cost, it, ot, is_real, _prov)
  1522              )
  1523              conn.commit()
  1524              _maybe_fire_spend_alert(conn)
  1525          finally:
  1526              conn.close()
  1527      except Exception as exc:
  1528          _log.error("_log_ai_spend failed: %s", exc)
  1529  
  1530  
  1531  def _maybe_fire_spend_alert(conn):
  1532      """Check if current month AI spend has crossed the configured threshold.
  1533      Fires n8n webhook at most once per day. Silent if not configured.
  1534      """
  1535      try:
  1536          cfg = conn.execute(
  1537              "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
  1538              "FROM ai_spend_config WHERE id = 1"
  1539          ).fetchone()
  1540          if not cfg or cfg["monthly_income_usd"] <= 0:
  1541              return  # income not configured yet — skip
  1542  
  1543          # Current calendar month spend
  1544          month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
  1545          row = conn.execute(
  1546              "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
  1547              "WHERE logged_at >= ?", (month_start,)
  1548          ).fetchone()
  1549          month_spend = row["total"] if row else 0.0
  1550  
  1551          threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
  1552          if month_spend < threshold_usd:
  1553              return  # under threshold — nothing to do
  1554  
  1555          # Check last alerted — don't fire more than once per day
  1556          last = cfg["last_alerted_at"] or ""
  1557          today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
  1558          if last.startswith(today):
  1559              return  # already alerted today
  1560  
  1561          # Update last_alerted_at
  1562          conn.execute(
  1563              "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
  1564              (__import__('datetime').datetime.utcnow().isoformat(),)
  1565          )
  1566          conn.commit()
  1567  
  1568          # Fire n8n alert webhook if configured
  1569          pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
  1570          payload = {
  1571              "alert": "ai_spend_threshold",
  1572              "month_spend_usd": round(month_spend, 4),
  1573              "income_usd": cfg["monthly_income_usd"],
  1574              "threshold_pct": cfg["alert_threshold_pct"],
  1575              "pct_used": round(pct_used, 1),
  1576              "alert_email": cfg["alert_email"],
  1577              "message": (
  1578                  f"TrustSquare AI spend alert: ${month_spend:.4f} spent this month "
  1579                  f"({pct_used:.1f}% of ${cfg['monthly_income_usd']:.2f} income). "
  1580                  f"Threshold: {cfg['alert_threshold_pct']}%."
  1581              ),
  1582          }
  1583          _log.warning("AI spend alert fired: %s", payload["message"])
  1584          if N8N_WEBHOOK_AI_ALERT:
  1585              import asyncio
  1586              try:
  1587                  loop = asyncio.get_event_loop()
  1588                  if loop.is_running():
  1589                      loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
  1590              except Exception:
  1591                  pass  # alert failure must never affect user response
  1592      except Exception as exc:
  1593          _log.error("_maybe_fire_spend_alert failed: %s", exc)
  1594  
  1595  
  1596  def _check_cost_ceiling(email: str) -> None:
  1597      """C1 (Session 97) — HARD daily cost ceiling. Pre-flight guard before every paid
  1598      AI call. REFUSES (HTTP 429) when today's logged AI spend has reached the per-user
  1599      or platform-wide USD ceiling. Distinct from observe-and-alert. Ceiling 0 = off.
  1600      Superusers exempt from the per-user rail (still counted toward platform).
  1601      Fail-OPEN on internal error — never lock a legitimate paying user out.
  1602      """
  1603      try:
  1604          conn = database.get_db()
  1605          try:
  1606              cfg = conn.execute(
  1607                  "SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  1608                  "FROM ai_spend_config WHERE id = 1"
  1609              ).fetchone()
  1610              if not cfg:
  1611                  return
  1612              user_cap     = cfg["daily_user_ceiling_usd"]     or 0.0
  1613              platform_cap = cfg["daily_platform_ceiling_usd"] or 0.0
  1614              if user_cap <= 0 and platform_cap <= 0:
  1615                  return
  1616              day_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
  1617              if platform_cap > 0:
  1618                  prow = conn.execute(
  1619                      "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log WHERE logged_at >= ?",
  1620                      (day_start,)
  1621                  ).fetchone()
  1622                  if (prow["t"] if prow else 0.0) >= platform_cap:
  1623                      _log.warning("C1 platform ceiling hit: $%.4f >= $%.2f — refusing (%s)",
  1624                                   prow["t"], platform_cap, email)
  1625                      raise HTTPException(
  1626                          status_code=429,
  1627                          detail="AI services are temporarily paused (daily platform budget reached). "
  1628                                 "Please try again later."
  1629                      )
  1630              if user_cap > 0 and email:
  1631                  su = conn.execute("SELECT is_superuser FROM users WHERE email = ?", (email,)).fetchone()
  1632                  if not (su and su["is_superuser"]):
  1633                      urow = conn.execute(
  1634                          "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log "
  1635                          "WHERE email = ? AND logged_at >= ?", (email, day_start)
  1636                      ).fetchone()
  1637                      if (urow["t"] if urow else 0.0) >= user_cap:
  1638                          _log.warning("C1 user ceiling hit: %s $%.4f >= $%.2f — refusing",
  1639                                       email, urow["t"], user_cap)
  1640                          raise HTTPException(
  1641                              status_code=429,
  1642                              detail="You've reached today's AI usage limit on this account. "
  1643                                     "It resets at 00:00 UTC."
  1644                          )
  1645          finally:
  1646              conn.close()
  1647      except HTTPException:
  1648          raise
  1649      except Exception as exc:
  1650          _log.error("_check_cost_ceiling failed (failing open): %s", exc)
```

## Active provider switch + pin/override (TTL decay)

```python
  1364  # Manual-pin TTL (hours). David 1 Aug 2026: 24h now; REVIEW dated ~1 Nov 2026 (3 months
  1365  # proven live) to consider shortening to 1h. Env-tunable, no deploy needed to change.
  1366  AI_OVERRIDE_TTL_HOURS = float(os.getenv("AI_OVERRIDE_TTL_HOURS", "24"))
  1367  
  1368  _TS_AI_CACHE = {"prov": None, "standing": None, "override": None, "expires": None, "ts": 0.0}
  1369  def _ts_active_provider():
  1370      """The LIVE active provider — DB-backed (Page-4 switchable, no restart). Falls back to the
  1371      startup env value if the DB is unreachable. Cached ~10s so we never hammer the DB per call."""
  1372      import time as _t
  1373      now=_t.time()
  1374      if _TS_AI_CACHE["prov"] and (now-_TS_AI_CACHE["ts"])<10:
  1375          return _TS_AI_CACHE["prov"]
  1376      prov=_TS_AI_PROVIDER  # startup default
  1377      standing, override, expires = prov, None, None
  1378      try:
  1379          conn=database.get_db()
  1380          try:
  1381              row=conn.execute("SELECT ai_active, ai_active_override, ai_override_expires "
  1382                               "FROM launch_switches WHERE id=1").fetchone()
  1383              if row:
  1384                  if row["ai_active"]: standing = prov = row["ai_active"]
  1385                  override, expires = row["ai_active_override"], row["ai_override_expires"]
  1386          finally:
  1387              conn.close()
  1388      except Exception:
  1389          pass
  1390      # MANUAL PIN precedence with DECAY (David 1 Aug 2026): an unexpired operator pin
  1391      # outranks the standing/auto lane; past expiry the standing lane silently resumes.
  1392      import datetime as _dt
  1393      if override and expires:
  1394          try:
  1395              if _dt.datetime.utcnow() < _dt.datetime.fromisoformat(expires):
  1396                  prov = override
  1397              else:
  1398                  override = None   # expired — report as inactive, standing rules
  1399          except Exception:
  1400              override = None
  1401      else:
  1402          override = None
  1403      _TS_AI_CACHE.update(prov=prov, standing=standing, override=override, expires=expires if override else None, ts=now)
  1404      return prov
  1405  
  1406  def _ts_models_for(prov):
  1407      try:
  1408          return _ts_ai.TASK_MODEL.get(prov, _ts_ai.TASK_MODEL["anthropic"])
  1409      except Exception:
  1410          return _TS_AI_MODELS
  1411  
  1412  # _ts_ai_url()/_ts_ai_headers() REMOVED 31 Jul 2026 — their sole caller (vision-draft) migrated
  1413  # to the ai_provider seam, completing P0 at 22/22 call sites. The wire protocol now lives ONLY in
  1414  # ai_provider.py adapters; RG-0017 asserts no raw vendor endpoint ever returns to this file.
  1415  if not EMAIL_INBOUND_SECRET:
  1416      _log.warning("EMAIL_INBOUND_SECRET not set — /email/inbound will reject all calls")
  1417  if not GMAIL_APP_PASSWORD:
  1418      _log.warning("GMAIL_APP_PASSWORD not set — triage replies will be drafted, never sent")
  1419  
  1420  CF_ZONE_ID    = os.getenv("CF_ZONE_ID")
  1421  CF_CACHE_TOKEN = os.getenv("CF_CACHE_TOKEN")
  1422  
  1423  async def _cf_purge_all():
```

## Tuppence helpers (deduct / balance / pre-flight require)

```python
 13695  
 13696  
 13697  def _deduct_tuppence(conn, email: str, amount: int, description: str) -> int:
 13698      """Deduct `amount` Tuppence from `email`. Returns new balance.
 13699      Raises HTTPException 402 if balance insufficient. Does NOT commit."""
 13700      row = conn.execute(
 13701          "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 13702          (email,)
 13703      ).fetchone()
 13704      balance = int(row["bal"])
 13705      if balance < amount:
 13706          raise HTTPException(
 13707              status_code=402,
 13708              detail=f"Insufficient Tuppence — you have {balance}T, need {amount}T"
 13709          )
 13710      conn.execute(
 13711          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'ai_service', ?, ?)",
 13712          (email, -amount, description)
 13713      )
 13714      return balance - amount
 13715  
 13716  
 13717  def _current_tuppence(email: str) -> int:
 13718      """Read-only Tuppence balance on a fresh connection. Used by deliver-then-charge
 13719      paths to report 'tuppence_remaining' when NO charge was made."""
 13720      c = database.get_db()
 13721      try:
 13722          row = c.execute(
 13723              "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 13724              (email,)
 13725          ).fetchone()
 13726          return int(row["bal"])
 13727      finally:
 13728          c.close()
 13729  
 13730  
 13731  def _require_tuppence(email: str, amount: int = 1) -> None:
 13732      """Pre-flight guard: ensure the buyer COULD pay before we run a paid AI service.
 13733      Raises 402 if not. Does NOT deduct — deduction happens only on a verified result."""
 13734      if _current_tuppence(email) < amount:
 13735          raise HTTPException(
 13736              status_code=402,
 13737              detail=f"Insufficient Tuppence — you need {amount}T to run this check."
 13738          )
 13739  
 13740  
 13741  # ── AI1 — Listing Rewrite ─────────────────────────────────────────────────────
 13742  
 13743  @app.post("/listings/{listing_id}/ai-rewrite")
 13744  async def ai_listing_rewrite(listing_id: int, email: str):
```

## AI1 Listing Rewrite (full endpoint)

```python
 13742  
 13743  @app.post("/listings/{listing_id}/ai-rewrite")
 13744  async def ai_listing_rewrite(listing_id: int, email: str):
 13745      """AI1: Seller pays 1T — Claude Haiku rewrites title + description.
 13746      Uses current market language and buyer psychology for the listing category.
 13747      Returns {new_title, new_description, tuppence_remaining}.
 13748      """
 13749      if not ai_provider.any_lane_configured():
 13750          raise HTTPException(status_code=503, detail="AI not configured")
 13751      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13752  
 13753      conn = database.get_db()
 13754      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 13755      if not listing:
 13756          conn.close()
 13757          raise HTTPException(status_code=404, detail="Listing not found")
 13758      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 13759          conn.close()
 13760          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 13761  
 13762      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 13763      _rw_charge_desc = f"AI Listing Rewrite · #{listing_id} · {listing['title'][:40]}"
 13764      conn.close()
 13765  
 13766      category = listing["category"] or "General"
 13767      city     = listing["city"] or "South Africa"
 13768      title    = listing["title"] or ""
 13769      desc     = listing["description"] or ""
 13770      price    = listing["price"] or ""
 13771  
 13772      system_prompt = (
 13773          "You are an expert marketplace copywriter for TrustSquare, a South African peer-to-peer local marketplace. "
 13774          "You write short, honest, buyer-friendly listings using current South African market language. "
 13775          "You never invent details. You prefer concrete facts over adjectives. "
 13776          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include street addresses, "
 13777          "business names, complex names, seller names, agent names, phone numbers, email addresses, "
 13778          "or any other identifying information in any generated text. "
 13779          "Always respond with a single valid JSON object — no markdown, no explanation."
 13780      )
 13781  
 13782      user_prompt = (
 13783          f"Rewrite this {category} listing for a buyer in {city}, South Africa.\n\n"
 13784          f"CURRENT TITLE: {title}\n"
 13785          f"CURRENT DESCRIPTION: {desc}\n"
 13786          f"PRICE: {price}\n\n"
 13787          "Return JSON with exactly two keys:\n"
 13788          '{"new_title": "<15 words max, specific and punchy>", '
 13789          '"new_description": "<60-120 words, 2-3 short paragraphs, buyer psychology, honest, no clichés>"}'
 13790      )
 13791  
 13792      try:
 13793          _sr = await asyncio.to_thread(
 13794              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 13795              task="haiku", max_tokens=350, system=system_prompt,
 13796              provider=_ts_active_provider(), timeout=20)
 13797          _rw_in, _rw_out = _sr.in_tokens, _sr.out_tokens
 13798          # P2 — Tuppence covers the revenue side; log token spend so the cost
 13799          # dashboard sees it too (sweep 12 Jun 2026)
 13800          _log_ai_spend(email, "/listings/ai-rewrite", "haiku", _rw_in, _rw_out)
 13801          raw = _sr.text.strip()
 13802          # Strip markdown fences if model adds them
 13803          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 13804          raw = _re_match.sub(r"\s*```$", "", raw)
 13805          result = json.loads(raw)
 13806          new_title = str(result.get("new_title", "")).strip()[:120]
 13807          new_desc  = str(result.get("new_description", "")).strip()[:1000]
 13808      except Exception as exc:
 13809          _log.error("ai-rewrite: %s", exc)
 13810          raise HTTPException(status_code=500, detail="AI rewrite failed — no Tuppence was charged") from exc
 13811  
 13812      # F2 fix: deliver-then-charge — deduction happens ONLY here, after a good result,
 13813      # so the help card's "server error = no Tuppence deducted" promise is true.
 13814      _conn2 = database.get_db()
 13815      try:
 13816          remaining = _deduct_tuppence(_conn2, email, 1, _rw_charge_desc)
 13817          _conn2.commit()
 13818      finally:
 13819          _conn2.close()
 13820      _log.info("ai-rewrite: listing #%d email=%s", listing_id, email)
 13821      return {
 13822          "new_title": new_title,
 13823          "new_description": new_desc,
 13824          "tuppence_remaining": remaining,
 13825      }
 13826  
 13827  
 13828  # ── AI2 — Seller Audit ────────────────────────────────────────────────────────
 13829  
 13830  @app.post("/listings/{listing_id}/ai-audit")
 13831  async def ai_seller_audit(listing_id: int, email: str):
 13832      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 13833      3 specific, actionable improvement steps.
 13834      Returns {actions: [{step, reason}], tuppence_remaining}.
 13835      """
 13836      if not ai_provider.any_lane_configured():
 13837          raise HTTPException(status_code=503, detail="AI not configured")
 13838      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13839  
 13840      conn = database.get_db()
 13841      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
```

## AI2 Seller Audit (full endpoint)

```python
 13829  
 13830  @app.post("/listings/{listing_id}/ai-audit")
 13831  async def ai_seller_audit(listing_id: int, email: str):
 13832      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 13833      3 specific, actionable improvement steps.
 13834      Returns {actions: [{step, reason}], tuppence_remaining}.
 13835      """
 13836      if not ai_provider.any_lane_configured():
 13837          raise HTTPException(status_code=503, detail="AI not configured")
 13838      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 13839  
 13840      conn = database.get_db()
 13841      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 13842      if not listing:
 13843          conn.close()
 13844          raise HTTPException(status_code=404, detail="Listing not found")
 13845      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 13846          conn.close()
 13847          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 13848  
 13849      # Read intro request count for context
 13850      intro_row = conn.execute(
 13851          "SELECT COUNT(*) as cnt FROM intro_requests WHERE listing_id = ?", (listing_id,)
 13852      ).fetchone()
 13853      intro_count = intro_row["cnt"] if intro_row else 0
 13854  
 13855      # Read trust score
 13856      user_row = conn.execute(
 13857          "SELECT trust_score FROM users WHERE email = ?", (email,)
 13858      ).fetchone()
 13859      trust_score = user_row["trust_score"] if user_row and user_row["trust_score"] else "unknown"
 13860  
 13861      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 13862      _au_charge_desc = f"AI Seller Audit · #{listing_id} · {listing['title'][:40]}"
 13863      conn.close()
 13864  
 13865      category = listing["category"] or "General"
 13866      city     = listing["city"] or "South Africa"
 13867      title    = listing["title"] or "(no title)"
 13868      desc     = listing["description"] or "(no description)"
 13869      price    = listing["price"] or "(no price)"
 13870  
 13871      system_prompt = (
 13872          "You are a marketplace performance coach for TrustSquare, a South African peer-to-peer marketplace. "
 13873          "You give direct, specific, actionable advice — no filler, no encouragement padding. "
 13874          "Think like a top-performing seller in the same category who has seen hundreds of listings. "
 13875          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include or suggest including "
 13876          "street addresses, business names, seller names, agent names, phone numbers, or contact details "
 13877          "in any generated text or improvement suggestions. "
 13878          "Always respond with a single valid JSON object — no markdown, no explanation."
 13879      )
 13880  
 13881      user_prompt = (
 13882          f"This {category} listing in {city} has received {intro_count} intro request(s) and "
 13883          f"the seller has a trust score of {trust_score}.\n\n"
 13884          f"TITLE: {title}\n"
 13885          f"DESCRIPTION: {desc}\n"
 13886          f"PRICE: {price}\n\n"
 13887          "Identify the 3 most important reasons a buyer might scroll past this listing without requesting an intro. "
 13888          "For each reason give a specific fix the seller can do right now.\n\n"
 13889          "Return JSON: "
 13890          '{"actions": [{"step": "<imperative fix, 8 words max>", "reason": "<why this matters, 1 sentence>"}, ...]}'
 13891          " — exactly 3 items in the array."
 13892      )
 13893  
 13894      try:
 13895          _sr = await asyncio.to_thread(
 13896              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 13897              task="haiku", max_tokens=400, system=system_prompt,
 13898              provider=_ts_active_provider(), timeout=20)
 13899          _au_in, _au_out = _sr.in_tokens, _sr.out_tokens
 13900          # P2 — Tuppence covers the revenue side; log token spend so the cost
 13901          # dashboard sees it too (sweep 12 Jun 2026)
 13902          _log_ai_spend(email, "/listings/ai-audit", "haiku", _au_in, _au_out)
 13903          raw = _sr.text.strip()
 13904          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 13905          raw = _re_match.sub(r"\s*```$", "", raw)
 13906          result = json.loads(raw)
 13907          actions = result.get("actions", [])
 13908          # Sanitise — max 3, enforce fields
 13909          clean_actions = []
 13910          for a in actions[:3]:
 13911              if isinstance(a, dict) and a.get("step"):
 13912                  clean_actions.append({
 13913                      "step":   str(a.get("step",   ""))[:80],
 13914                      "reason": str(a.get("reason", ""))[:200],
 13915                  })
 13916      except Exception as exc:
 13917          _log.error("ai-audit: %s", exc)
 13918          raise HTTPException(status_code=500, detail="AI audit failed — no Tuppence was charged") from exc
 13919  
 13920      _conn2 = database.get_db()
 13921      try:
 13922          remaining = _deduct_tuppence(_conn2, email, 1, _au_charge_desc)   # F2: charge on delivery
 13923          _conn2.commit()
 13924      finally:
 13925          _conn2.close()
 13926      _log.info("ai-audit: listing #%d email=%s intros=%d", listing_id, email, intro_count)
 13927      return {
 13928          "actions": clean_actions,
 13929          "tuppence_remaining": remaining,
 13930      }
 13931  
 13932  
 13933  # ── AI3 — Buyer Price Check (upgraded Session 77: three-panel intelligence) ──
 13934  
 13935  # -- Tiered Value Selector: availability helpers + value-tiers endpoint --------
 13936  # STEP 5: the paid master switch AND per-provider liveness now come from the
 13937  # server-readable feature_flags store (feature_flags.json), so enabling a paid
 13938  # provider later is a CONFIG change, not a code edit. Safe defaults: paid OFF,
 13939  # every paid/contract provider OFF, free/open/owned providers ON.
 13940  def _paid_tiers_enabled() -> bool:
 13941      return feature_flags.paid_tiers_enabled()
 13942  
 13943  def _tier_providers() -> dict:
```

## AI3 Price Check (charge logic + integrity model)

```python
 14400  
 14401  @app.post("/listings/{listing_id}/price-check")
 14402  async def ai_price_check(listing_id: int, email: str, tier: Optional[str] = None):
 14403      """AI3: Buyer pays 1T — honest, three-panel price intelligence.
 14404  
 14405      INTEGRITY MODEL (price-integrity fix):
 14406        The model writes the SENTENCE; the system produces the NUMBER.
 14407        - Collectibles with a resolved Scryfall id  -> VERIFIED feed price (USD->ZAR
 14408          live rate). The LLM only narrates the real figures it is handed.
 14409        - Everything else -> an explicitly-labelled QUALITATIVE GUIDE. The LLM may
 14410          give a rough range but it is flagged 'not a verified price', and we never
 14411          cheerlead ('move quickly' is not permitted anywhere).
 14412        - A first-class fraud guard fires when asking price is far below a VERIFIED
 14413          floor: the verdict becomes a warning, never a 'buy' nudge.
 14414      Returns {verdict, source, sa_context, sa_range, assessment, official_context,
 14415               official_range, local_vs_global, asking_price, verified, safety_flag,
 14416               tuppence_remaining, ...legacy}.
 14417      """
 14418      if not ai_provider.any_lane_configured():
 14419          raise HTTPException(status_code=503, detail="AI not configured")
 14420  
 14421      conn = database.get_db()
 14422      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14423      if not listing:
 14424          conn.close()
 14425          raise HTTPException(status_code=404, detail="Listing not found")
 14426  
 14427      # DELIVER-THEN-CHARGE (Session 95): we do NOT deduct here. Tuppence is only
 14428      # charged at the end, and ONLY if we produced a verified service. A guess,
 14429      # a 'cannot verify', or any failure costs the buyer nothing.
 14430      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour; a
 14431      # tier-aware caller must request a tier actually offered for this listing.
 14432      if tier is None:
 14433          _charge = 1
 14434      else:
 14435          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "fair_price")}
 14436          if tier not in _offered_t:
 14437              conn.close()
 14438              raise HTTPException(status_code=400,
 14439                  detail=f"Tier {tier} is not available for this listing")
 14440          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 14441      _require_tuppence(email, _charge)   # pre-flight only — no deduction yet
 14442      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 14443      category    = listing["category"] or "General"
 14444      city        = listing["city"] or "South Africa"
 14445      title       = listing["title"] or "(no title)"
 14446      desc        = listing["description"] or "(no description)"
 14447      price       = listing["price"] or "(no price)"
 14448      scryfall_id = listing["scryfall_id"] if "scryfall_id" in listing.keys() else None
 14449      conn.close()  # done reading; charging happens on its own connection at the end
 14450  
 14451      # Parse the buyer-facing asking price into a number for ratio checks.
 14452      asking_zar = None
 14453      try:
 14454          asking_zar = float(str(price).replace("R", "").replace(",", "").strip())
 14455      except Exception:
 14456          asking_zar = None
 14457  
 14458      # ── Step 1+2: try to resolve a REAL verified price (collectibles) ──────────
 14459      verified_block = None        # text handed to the model as ground truth
 14460      official_range = "N/A"
 14461      official_ctx   = ""
 14462      floor_zar      = None
 14463      verified       = False
 14464      source         = "ai_estimate"
 14465  
 14466      # Late-resolve a scryfall id if the listing predates this column.
 14467      if not scryfall_id:
 14468          try:
 14469              scryfall_id = await resolve_scryfall_id(title, category)
 14470              if scryfall_id:
 14471                  c2 = database.get_db()
 14472                  c2.execute("UPDATE listings SET scryfall_id = ? WHERE id = ?",
 14473                             (scryfall_id, listing_id))
 14474                  c2.commit(); c2.close()
 14475          except Exception:
 14476              scryfall_id = None
 14477  
 14478      if scryfall_id:
 14479          feed = await scryfall_price_by_id(scryfall_id)
 14480          if feed and feed.get("usd"):
 14481              rate = await live_usd_zar()
 14482              usd  = feed["usd"]
 14483              floor_zar = usd * rate
 14484              verified = True
 14485              source   = "scryfall"
 14486              reserved = " (Reserved List — cannot be reprinted)" if feed.get("reserved") else ""
 14487              official_range = f"R{floor_zar:,.0f}  (USD ${usd:,.2f} \u00d7 R{rate:.2f}/USD)"
 14488              official_ctx   = (f"Verified market price for {feed.get('name')} "
 14489                                f"[{feed.get('set_name')}]{reserved}: "
 14490                                f"USD ${usd:,.2f} on TCGPlayer (via Scryfall), "
 14491                                f"\u2248 R{floor_zar:,.0f} at today's rate.")
 14492              verified_block = (
 14493                  f"VERIFIED MARKET DATA (use these EXACT figures, do not alter them):\n"
 14494                  f"- Card: {feed.get('name')} [{feed.get('set_name')}]{reserved}\n"
 14495                  f"- Verified market price: USD ${usd:,.2f} = R{floor_zar:,.0f} "
 14496                  f"(live rate R{rate:.2f}/USD)\n"
 14497                  f"- Buyer's asking price: {price}\n"
 14498              )
 14499  
 14500      # ── Step 3: narrate. Two prompt modes: verified vs qualitative-guide ───────
 14501      # -- STEP 3: no card feed -> try the FREE/owned resolver for the chosen tier
 14502      if (not verified_block) and (tier is not None):
 14503          _fpx = await _fair_price_resolve(
 14504              listing, listing_id, tier, _tierkey_for(listing, "fair_price"),
 14505              _listing_country_iso2(listing), category, city, asking_zar)
 14506          if _fpx and _fpx[0] == "verified":
 14507              _e = _fpx[1]
 14508              verified = True
 14509              source = _e["source"]
 14510              floor_zar = _e.get("floor_zar")
 14511              official_range = _e["official_range"]
 14512              official_ctx = _e["official_ctx"]
 14513              verified_block = _e["block"]
 14514          elif _fpx and _fpx[0] == "area_guide":
 14515              _e = _fpx[1]
 14516              _log.info("ai-price-check: listing #%d buyer=%s AREA-GUIDE %s (0T free)",
 14517                        listing_id, email, _e["source"])
 14518              return {
 14519                  "verdict": "area_guide", "source": _e["source"],
 14520                  "verified": False, "charged": False,
 14521                  "sa_context": "", "sa_range": _e.get("range_text", "N/A"),
 14522                  "assessment": _e["assessment"],
 14523                  "official_context": _e.get("provenance", ""),
 14524                  "official_range": _e.get("range_text", "N/A"),
 14525                  "local_vs_global": "cannot_compare", "asking_price": price,
 14526                  "safety_flag": None, "tuppence_remaining": _current_tuppence(email),
 14527                  "indicative_label": _INDICATIVE_LABEL,
 14528                  "provenance_date": _e.get("date", ""),
 14529                  "context": _e["assessment"], "suggested_range": _e.get("range_text", "N/A"),
 14530              }
 14531      if verified_block:
 14532          system_prompt = (
 14533              "You are a pricing analyst for TrustSquare, a South African marketplace. "
 14534              "You are given VERIFIED market figures. You must NEVER invent, round, or "
 14535              "contradict them — only explain them in plain language. Never tell a buyer "
 14536              "to 'move quickly' or 'buy now'. Be honest and protective. "
 14537              "Always respond with a single valid JSON object — no markdown."
 14538          )
 14539          user_prompt = (
 14540              f"A buyer is considering this {category} listing in {city}, South Africa.\n\n"
 14541              f"TITLE: {title}\nDESCRIPTION: {desc[:400]}\n\n"
 14542              f"{verified_block}\n"
 14543              "Write a short, honest assessment comparing the asking price to the verified "
 14544              "market price. Do not output any price number other than those given above.\n"
 14545              "Return JSON with these keys (strings, 50 words max each):\n"
 14546              "{\n"
 14547              '  "verdict": "fair" | "above_market" | "below_market" | "cannot_assess",\n'
 14548              '  "sa_context": "<note on the SA second-hand reality for this item, qualitative>",\n'
 14549              '  "assessment": "<plain-language read on the asking price vs the verified figure>",\n'
 14550              '  "local_vs_global": "cheaper_locally" | "cheaper_globally" | "similar" | "cannot_compare"\n'
 14551              "}"
 14552          )
 14553      else:
 14554          # No verified price feed for this category. Per the integrity rule, we do
 14555          # NOT sell a guess. Return an honest 'cannot verify' and charge nothing.
 14556          _log.info("ai-price-check: listing #%d buyer=%s NO-FEED -> free cannot_verify",
 14557                    listing_id, email)
 14558          bal = _current_tuppence(email)
 14559          return {
 14560              "verdict":          "cannot_verify",
 14561              "source":           "no_feed",
 14562              "verified":         False,
 14563              "charged":          False,
 14564              "sa_context":       "",
 14565              "sa_range":         "N/A",
 14566              "assessment":       ("We don\u2019t yet have a verified price source for this "
 14567                                   "category, so we won\u2019t guess. No Tuppence was charged. "
 14568                                   "Compare the asking price against similar local listings "
 14569                                   "before deciding."),
 14570              "official_context": "",
 14571              "official_range":   "N/A",
 14572              "local_vs_global":  "cannot_compare",
 14573              "asking_price":     price,
 14574              "safety_flag":      None,
 14575              "tuppence_remaining": bal,
 14576              "context":          "",
 14577              "suggested_range":  "N/A",
 14578          }
 14579  
 14580      try:
 14581          _sr = await asyncio.to_thread(
 14582              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14583              task="sonnet", max_tokens=700, system=system_prompt,
 14584              provider=_ts_active_provider(), timeout=30)
 14585          raw = _sr.text.strip()
 14586          _pc_in, _pc_out = _sr.in_tokens, _sr.out_tokens   # C2/C3
 14587          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14588          raw = _re_match.sub(r"\s*```$", "", raw)
 14589          result = json.loads(raw)
 14590          verdict         = str(result.get("verdict", "cannot_assess"))[:20]
 14591          sa_context      = str(result.get("sa_context", ""))[:600]
 14592          sa_range        = str(result.get("sa_range", "N/A"))[:100]
 14593          assessment      = str(result.get("assessment", ""))[:400]
 14594          local_vs_global = str(result.get("local_vs_global", "cannot_compare"))[:20]
 14595      except Exception as exc:
 14596          _log.error("ai-price-check: %s", exc)
 14597          raise HTTPException(status_code=500, detail="AI price check failed — no Tuppence charged") from exc
 14598  
 14599      # ── Price-position note: only fires against a VERIFIED floor. Not a fraud
 14600      #    allegation — a neutral observation that the price is well below market. ─
 14601      safety_flag = price_caution(asking_zar, floor_zar)
 14602      if safety_flag and safety_flag["level"] == "danger":
 14603          verdict = "below_verified_market"
 14604  
 14605      # DELIVER-THEN-CHARGE: a verified result was produced — charge exactly now.
 14606      cc = database.get_db()
 14607      try:
 14608          remaining = _deduct_tuppence(
 14609              cc, email, _charge,
 14610              f"AI Price Check \u00b7 #{listing_id} \u00b7 {title[:40]}"
 14611          )
 14612          cc.commit()
 14613      finally:
 14614          cc.close()
 14615  
 14616      # C3 — log real AI spend for this paid call (was previously unlogged).
 14617      _log_ai_spend(email, "/listings/ai-price-check", "sonnet", _pc_in, _pc_out)
 14618  
 14619      _log.info("ai-price-check: listing #%d buyer=%s verdict=%s verified=%s flag=%s charged=1T",
 14620                listing_id, email, verdict, verified,
 14621                safety_flag["level"] if safety_flag else "none")
 14622      return {
 14623          "verdict":          verdict,
 14624          "source":           source,            # 'scryfall'
 14625          "verified":         verified,          # True only when a real feed was used
 14626          "charged":          True,
 14627          "sa_context":       sa_context,
 14628          "sa_range":         sa_range,
 14629          "assessment":       assessment,
 14630          "official_context": official_ctx,
 14631          "official_range":   official_range,
 14632          "local_vs_global":  local_vs_global,
 14633          "asking_price":     price,
 14634          "safety_flag":      safety_flag,        # None | {level, headline, detail}
 14635          "tuppence_remaining": remaining,
 14636          # Legacy fields — kept for backward compat
 14637          "context":          assessment,
 14638          "suggested_range":  sa_range,
 14639          **_report_stamp("Price reflects feeds/market data available at the time above; re-run for a current figure.", volatile=_is_volatile_item(source, verdict, locals().get("subject"), locals().get("_cat"))),
 14640      }
 14641  
 14642  # ── END AI TUPPENCE SERVICES (Session 73) ────────────────────────────────────
 14643  
 14644  
 14645  # ── AI TUPPENCE SERVICES — TIER 2 (Session 74) ───────────────────────────────
 14646  #
 14647  #   AI4  POST /listings/{id}/yield-calc?email=     Haiku   Property yield calculator (1T)
 14648  #   AI5  POST /listings/batch-cards?email=         Sonnet  Batch card listing via vision (2T)
 14649  #
 14650  # AI4: Property listings only. Calculates gross yield, net estimate, SA comparison.
 14651  # AI5: Collectors category. Accepts up to 10 base64 images, returns array of draft JSONs.
 14652  
 14653  
 14654  # ── AI4 — Property Yield Calculator ──────────────────────────────────────────
 14655  
 14656  async def _yield_fill_missing(need, tier, country, city, suburb, listing, listing_id):
 14657      """STEP 3: source the missing yield half (rent OR purchase price) from a
 14658      FREE/owned feed, per tier + country. Returns {value, provenance, date,
 14659      specificity} or None. Numbers come from feeds/arithmetic, never a model."""
```

## AI4 Yield (deliver-then-charge reference)

```python
 14711  
 14712  @app.post("/listings/{listing_id}/yield-calc")
 14713  async def ai_yield_calc(listing_id: int, email: str,
 14714                          rent: float | None = None,
 14715                          purchase_price: float | None = None,
 14716                          tier: Optional[str] = None):
 14717      """AI4: Property yield — HONEST & deliver-then-charge (Session 95).
 14718  
 14719      A real gross yield needs BOTH a purchase price and an annual rent. A listing
 14720      only carries one number (sale price OR monthly rent), so we:
 14721        - take the listing's own figure for its side, and
 14722        - accept the OTHER figure from the caller (?rent= or ?purchase_price=).
 14723      If the second figure is missing we return needs_input and charge NOTHING.
 14724      The yield is computed in PYTHON (not guessed by the model). The LLM only
 14725      writes the benchmark sentence. 1T is charged ONLY when a real yield is
 14726      produced from real inputs.
 14727      """
 14728      if not ai_provider.any_lane_configured():
 14729          raise HTTPException(status_code=503, detail="AI not configured")
 14730  
 14731      conn = database.get_db()
 14732      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 14733      if not listing:
 14734          conn.close()
 14735          raise HTTPException(status_code=404, detail="Listing not found")
 14736  
 14737      category = listing["category"] or ""
 14738      if "property" not in category.lower() and category.lower() not in ("property", "estate agents", "accommodation"):
 14739          conn.close()
 14740          raise HTTPException(status_code=400, detail="Yield calculator is only available for Property listings")
 14741  
 14742      city          = listing["city"] or "South Africa"
 14743      suburb        = listing["suburb"] or ""
 14744      title         = listing["title"] or "(no title)"
 14745      desc          = listing["description"] or ""
 14746      price_raw     = listing["price"] or ""
 14747      listing_type  = (listing["listing_type"] if "listing_type" in listing.keys() else None) or ""
 14748      conn.close()
 14749  
 14750      # Pre-flight: can the buyer pay at all? (No deduction yet.)
 14751      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour.
 14752      if tier is None:
 14753          _charge = 1
 14754      else:
 14755          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "yield")}
 14756          if tier not in _offered_t:
 14757              raise HTTPException(status_code=400,
 14758                  detail=f"Tier {tier} is not available for this listing")
 14759          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 14760      _require_tuppence(email, _charge)
 14761      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 14762  
 14763      def _num(v):
 14764          try:
 14765              return float(str(v).replace("R", "").replace(",", "")
 14766                           .replace("/month", "").replace("pm", "").strip())
 14767          except Exception:
 14768              return None
 14769  
 14770      listing_amount = _num(price_raw)
 14771      lt = listing_type.lower()
 14772      is_rental = ("rent" in lt) or ("rent" in (title + " " + desc).lower() and "for sale" not in lt)
 14773  
 14774      # Resolve purchase_price (annual rent / monthly rent) from listing + caller input.
 14775      monthly_rent = None
 14776      buy_price    = None
 14777      need = None
 14778      if is_rental:
 14779          # Listing price IS the monthly rent. Need the purchase price from caller.
 14780          monthly_rent = listing_amount
 14781          buy_price    = purchase_price
 14782          if not buy_price:
 14783              need = "purchase_price"
 14784      else:
 14785          # Listing price IS the sale/purchase price. Need expected monthly rent.
 14786          buy_price    = listing_amount
 14787          monthly_rent = rent
 14788          if not monthly_rent:
 14789              need = "rent"
 14790  
 14791      # Honest 'needs input' — FREE, no Tuppence charged.
 14792      # -- STEP 3: source the missing half from a FREE/owned feed (per tier+country)
 14793      _country_y = _listing_country_iso2(listing)
 14794      _rent_src = "your figure"
 14795      _price_src = "the listing"
 14796      if need and tier is not None:
 14797          _filled = await _yield_fill_missing(need, tier, _country_y, city, suburb, listing, listing_id)
 14798          if _filled:
 14799              if need == "rent":
 14800                  monthly_rent = _filled["value"]; _rent_src = _filled["provenance"]
 14801              else:
 14802                  buy_price = _filled["value"]; _price_src = _filled["provenance"]
 14803              need = None
 14804  
 14805      if need or not buy_price or not monthly_rent or buy_price <= 0 or monthly_rent <= 0:
 14806          bal = _current_tuppence(email)
 14807          prompt_for = ("the expected monthly rent" if need == "rent"
 14808                        else "the likely purchase price" if need == "purchase_price"
 14809                        else "both the purchase price and the monthly rent")
 14810          return {
 14811              "status":           "needs_input",
 14812              "charged":          False,
 14813              "need":             need or "both",
 14814              "listing_amount":   listing_amount,
 14815              "is_rental":        is_rental,
 14816              "message":          (f"To calculate a real yield we need {prompt_for}. "
 14817                                   f"Enter it and we\u2019ll compute the actual figure — "
 14818                                   f"no Tuppence is charged until we do."),
 14819              "tuppence_remaining": bal,
 14820          }
 14821  
 14822      # ── REAL computation in Python (deterministic, auditable) ──────────────────
 14823      annual_rent = monthly_rent * 12.0
 14824      gross = (annual_rent / buy_price) * 100.0
 14825  
 14826      # Net estimate: subtract a transparent cost band (rates, levies, maintenance,
 14827      # vacancy). We show the assumption rather than hiding it inside a model guess.
 14828      # STEP 3: versioned, dated per-region net-cost band replaces the flat 3%.
 14829      _band = tier_resolvers.net_cost_band(_country_y)
 14830      NET_COST_PCT = float(_band.get("typical", 3.0))
 14831      net = gross - NET_COST_PCT
 14832  
 14833      # LLM writes ONLY the qualitative benchmark sentence — handed the real numbers.
 14834      location_str = f"{suburb}, {city}" if suburb else city
 14835      _BENCHMARKS = {
 14836          "ZA": ("SA GROSS YIELD BENCHMARKS (2026): Pretoria residential 7-10%, "
 14837                 "Cape Town 5-7%, Johannesburg 6-9%, Durban 7-10%, secondary cities 8-12%, "
 14838                 "commercial 9-12%, student accommodation 10-14%."),
 14839          "UK": ("UK GROSS YIELD BENCHMARKS: prime London 3-5%, regional cities 5-8%, "
 14840                 "northern England 6-9%."),
 14841          "US": ("US GROSS YIELD BENCHMARKS: coastal metros 3-5%, Sunbelt 5-8%, "
 14842                 "Midwest/secondary 7-10%."),
 14843          "AU": "AU GROSS YIELD BENCHMARKS: Sydney/Melbourne 2.5-4%, Brisbane/Perth 4-6%.",
 14844      }
 14845      sa_benchmarks = _BENCHMARKS.get(_country_y, _BENCHMARKS["ZA"])
 14846      system_prompt = (
 14847          "You are a property market analyst. You are GIVEN a computed gross "
 14848          "yield — never recalculate or contradict it. Write one honest sentence placing "
 14849          "it against the local benchmark. No filler, no 'buy now'. "
 14850          "Respond with a single valid JSON object — no markdown."
 14851      )
 14852      user_prompt = (
 14853          f"Property in {location_str} ({_country_y}).\n"
 14854          f"Purchase price: R{buy_price:,.0f}. Monthly rent: R{monthly_rent:,.0f}. "
 14855          f"COMPUTED gross yield: {gross:.1f}% (annual rent / purchase price).\n"
 14856          f"{sa_benchmarks}\n"
 14857          "Return JSON: {\"market_context\": \"<one honest sentence vs the benchmark for "
 14858          "this city/type>\", \"sa_yield_benchmark\": \"<the matching benchmark, e.g. "
 14859          "Pretoria residential: 7-10% gross>\"}"
 14860      )
 14861  
 14862      try:
 14863          _sr = await asyncio.to_thread(
 14864              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 14865              task="haiku", max_tokens=250, system=system_prompt,
 14866              provider=_ts_active_provider(), timeout=20)
 14867          raw = _sr.text.strip()
 14868          _yc_in, _yc_out = _sr.in_tokens, _sr.out_tokens   # C2/C3
 14869          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 14870          raw = _re_match.sub(r"\s*```$", "", raw)
 14871          result = json.loads(raw)
 14872          market_context     = str(result.get("market_context", ""))[:400]
 14873          sa_yield_benchmark = str(result.get("sa_yield_benchmark", ""))[:120]
 14874      except Exception as exc:
 14875          # The model only writes the narrative; if it fails we STILL have the real
 14876          # numbers. Degrade gracefully with a neutral sentence rather than failing —
 14877          # but only charge because the core (computed) service succeeded.
 14878          _log.warning("ai-yield-calc narration failed (numbers still valid): %s", exc)
 14879          market_context = (f"Computed gross yield {gross:.1f}% on a R{buy_price:,.0f} "
 14880                            f"purchase at R{monthly_rent:,.0f}/month.")
 14881          sa_yield_benchmark = "SA residential benchmark: ~7-10% gross (varies by city)."
 14882          _yc_in, _yc_out = None, None   # narration failed — flat estimate
 14883  
 14884      # DELIVER-THEN-CHARGE: a real, computed yield was produced — charge now.
 14885      if _charge and _charge > 0:
 14886          cc = database.get_db()
 14887          try:
 14888              remaining = _deduct_tuppence(
 14889                  cc, email, _charge,
 14890                  f"AI Yield Calc \u00b7 #{listing_id} \u00b7 {title[:40]}"
 14891              )
 14892              cc.commit()
 14893          finally:
 14894              cc.close()
 14895      else:
 14896          remaining = _current_tuppence(email)
 14897  
 14898      # C3 — log real AI spend for this paid call (was previously unlogged).
 14899      _log_ai_spend(email, "/listings/yield-calc", "haiku", _yc_in, _yc_out)
 14900  
 14901      _log.info("ai-yield-calc: listing #%d email=%s gross=%.1f%% charged=1T",
 14902                listing_id, email, gross)
 14903      return {
 14904          "status":                 "ok",
 14905          "charged":                True,
 14906          "computed":               True,        # numbers came from arithmetic, not a model
 14907          "gross_yield_pct":        f"{gross:.1f}%",
 14908          "net_yield_estimate_pct": f"{net:.1f}%",
 14909          "net_cost_assumption_pct": f"{NET_COST_PCT:.1f}%",
 14910          "purchase_price_used":    f"R{buy_price:,.0f}",
```

## AI5 Batch Cards (full endpoint)

```python
 14941  
 14942  @app.post("/listings/batch-cards")
 14943  async def ai_batch_card_listings(req: BatchCardRequest):
 14944      """AI5: Seller pays 2T — Claude Sonnet Vision analyses up to 10 card photos and
 14945      returns an array of draft listing JSONs ready for review and publish.
 14946      Each draft contains title, description, price_suggestion, condition, category.
 14947      Capped at 10 images per call. 2T flat cost regardless of card count.
 14948      Returns {drafts: [...], cards_processed, tuppence_remaining}.
 14949      """
 14950      if not ai_provider.any_lane_configured():
 14951          raise HTTPException(status_code=503, detail="AI not configured")
 14952  
 14953      if not req.images:
 14954          raise HTTPException(status_code=400, detail="At least one image is required")
 14955      _check_cost_ceiling(req.seller_email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 14956  
 14957      # Cap at 10 cards
 14958      images = req.images[:10]
 14959      card_count = len(images)
 14960  
 14961      _require_tuppence(req.seller_email, 2)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 14962      _bc_charge_desc = f"AI Batch Cards · {card_count} card(s) · {req.city}"
 14963  
 14964      suburb_str = req.suburb or req.city
 14965      location_str = f"{suburb_str}, {req.city}"
 14966  
 14967      system_prompt = (
 14968          "You are an expert trading card and collectables appraiser and marketplace copywriter "
 14969          "for TrustSquare, a South African peer-to-peer local marketplace. "
 14970          "You identify cards/collectables from photos, assess condition, and write concise buyer-friendly listings. "
 14971          "You know SA collectables market values. "
 14972          "Always respond with a single valid JSON object — no markdown, no explanation."
 14973      )
 14974  
 14975      # Build the message content: one text block + one image block per card
 14976      content_blocks = [
 14977          {
 14978              "type": "text",
 14979              "text": (
 14980                  f"Analyse these {card_count} trading card / collectable image(s) for a seller in {location_str}, "
 14981                  "South Africa. For each image, generate a complete listing draft.\n\n"
 14982                  "For each card/item return:\n"
 14983                  '{"title": "<specific card/item name, set, year if visible, max 12 words>", '
 14984                  '"description": "<40-80 words: card details, set/series, condition notes, notable features>", '
 14985                  '"price_suggestion": "<e.g. R150 or R200–R350 depending on condition>", '
 14986                  '"condition": "mint" | "near_mint" | "excellent" | "good" | "fair" | "poor", '
 14987                  '"category": "Collectors"}\n\n'
 14988                  f'Return JSON: {{"drafts": [<one object per image in order>]}}'
 14989              )
 14990          }
 14991      ]
 14992  
 14993      for _, img_b64 in enumerate(images):
 14994          # Detect media type from base64 header or default to jpeg
 14995          media_type = "image/jpeg"
 14996          if img_b64.startswith("data:"):
 14997              header, data = img_b64.split(",", 1)
 14998              if "png" in header:
 14999                  media_type = "image/png"
 15000              elif "gif" in header:
 15001                  media_type = "image/gif"
 15002              elif "webp" in header:
 15003                  media_type = "image/webp"
 15004              img_b64 = data
 15005  
 15006          content_blocks.append({
 15007              "type": "image",
 15008              "source": {
 15009                  "type": "base64",
 15010                  "media_type": media_type,
 15011                  "data": img_b64,
 15012              }
 15013          })
 15014  
 15015      try:
 15016          # SEAM-ROUTED (P0): task="vision" — resolves to the haiku id today (Haiku-first,
 15017          # 3 Jul 2026); flipping TASK_MODEL's vision row back to sonnet re-arms the documented revert.
 15018          _sr = await asyncio.to_thread(
 15019              ai_provider.complete, [{"role": "user", "content": content_blocks}],
 15020              task="vision", max_tokens=2000, system=system_prompt,
 15021              provider=_ts_active_provider(), timeout=60)
 15022          _bc_in, _bc_out = _sr.in_tokens, _sr.out_tokens
 15023          # P2 — Tuppence covers the revenue side; log token spend so the cost
 15024          # dashboard sees it too (sweep 12 Jun 2026)
 15025          _log_ai_spend(req.seller_email, "/listings/batch-cards", "sonnet_vision", _bc_in, _bc_out)
 15026          raw = _sr.text.strip()
 15027          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 15028          raw = _re_match.sub(r"\s*```$", "", raw)
 15029          result = json.loads(raw)
 15030          drafts = result.get("drafts", [])
 15031  
 15032          # Sanitise each draft
 15033          clean_drafts = []
 15034          valid_conditions = {"mint", "near_mint", "excellent", "good", "fair", "poor"}
 15035          for d in drafts[:card_count]:
 15036              if isinstance(d, dict):
 15037                  clean_drafts.append({
 15038                      "title":            str(d.get("title", ""))[:120],
 15039                      "description":      str(d.get("description", ""))[:800],
 15040                      "price_suggestion": str(d.get("price_suggestion", ""))[:60],
 15041                      "condition":        d.get("condition", "good") if d.get("condition") in valid_conditions else "good",
 15042                      "category":         "Collectors",
 15043                      "city":             req.city,
 15044                      "suburb":           req.suburb or "",
 15045                  })
 15046  
 15047      except Exception as exc:
 15048          _log.error("ai-batch-cards: %s", exc)
 15049          raise HTTPException(status_code=500, detail="AI batch card listing failed — no Tuppence was charged") from exc
 15050  
 15051      _conn2 = database.get_db()
 15052      try:
 15053          remaining = _deduct_tuppence(_conn2, req.seller_email, 2, _bc_charge_desc)   # F2: charge on delivery
 15054          _conn2.commit()
 15055      finally:
 15056          _conn2.close()
 15057      _log.info("ai-batch-cards: seller=%s city=%s cards=%d drafts=%d",
 15058                req.seller_email, req.city, card_count, len(clean_drafts))
 15059      return {
 15060          "drafts":           clean_drafts,
 15061          "cards_processed":  card_count,
 15062          "tuppence_remaining": remaining,
 15063      }
 15064  
 15065  
 15066  
 15067  @app.get("/tuppence/history")
 15068  def get_tuppence_history(email: str, limit: int = 50, offset: int = 0):
 15069      """Return paginated tuppence transaction history with running balance."""
 15070      conn = database.get_db()
 15071      try:
 15072          # Verify user exists
 15073          user = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
 15074          if not user:
 15075              raise HTTPException(status_code=404, detail="User not found")
 15076  
 15077          total = conn.execute(
 15078              "SELECT COUNT(*) FROM transactions WHERE user_email=?", (email,)
 15079          ).fetchone()[0]
 15080  
 15081          # Get all rows ascending to compute running balances
 15082          all_rows = conn.execute(
 15083              "SELECT id, type, amount, description, created_at "
 15084              "FROM transactions WHERE user_email=? ORDER BY id ASC",
 15085              (email,)
 15086          ).fetchall()
 15087  
 15088          # Compute running balance_after for each row (cumulative sum)
 15089          running = 0
 15090          balance_after = []
```

## KYC identity verification (vision, cost-guarded)

```python
  9644  
  9645  
  9646  async def _sonnet_verify_identity(doc_url: str, claimed_name: str,
  9647                                     claimed_id: str, doc_type: str, email: str = "") -> dict:
  9648      """Call Sonnet vision to verify identity document.
  9649      SWAP POINT: replace this function with PaddleOCR/PassportEye for zero-token operation.
  9650      Self-contained cost guard (P2, 22 Jul 2026): checks the daily ceiling BEFORE the call
  9651      (raises HTTPException 429, same as every other paid endpoint) and logs spend itself
  9652      so this helper stays metered even if a future caller forgets to.
  9653      Returns: {verified(bool), confidence(float), extracted_name(str),
  9654                extracted_id(str), notes(str), model(str)}"""
  9655      if not ai_provider.any_lane_configured():
  9656          return {"verified": False, "confidence": 0.0, "extracted_name": "",
  9657                  "extracted_id": "", "notes": "AI verification unavailable — API key not set",
  9658                  "model": "none"}
  9659      _check_cost_ceiling(email)   # C1 — refuse if daily cost ceiling reached
  9660      try:
  9661          # Fetch the document image
  9662          req = urllib.request.Request(doc_url, headers={"User-Agent": "TrustSquare-KYC/1.0"})
  9663          with urllib.request.urlopen(req, timeout=10) as resp:
  9664              img_bytes = resp.read()
  9665          img_b64 = base64.standard_b64encode(img_bytes).decode()
  9666          # Detect media type
  9667          media_type = "image/jpeg"
  9668          if doc_url.lower().endswith(".png"):
  9669              media_type = "image/png"
  9670          elif doc_url.lower().endswith(".webp"):
  9671              media_type = "image/webp"
  9672  
  9673          # SEAM-ROUTED (P0, 17 Jul 2026): KYC vision call goes through ai_provider.complete()
  9674          # with task="sonnet" — same claude-sonnet-4-6 on the Anthropic path as the old SDK call.
  9675          prompt = f"""You are a document verification assistant for TrustSquare marketplace.
  9676  Examine this identity document image carefully.
  9677  
  9678  The seller claims:
  9679  - Full name: {claimed_name}
  9680  - ID/passport number: {claimed_id}
  9681  - Document type: {doc_type}
  9682  
  9683  Your task:
  9684  1. Extract the FULL NAME exactly as printed on the document
  9685  2. Extract the ID NUMBER / PASSPORT NUMBER exactly as printed
  9686  3. Determine if the claimed name matches the document name (allow for initials, middle names)
  9687  4. Determine if the claimed number matches the document number
  9688  
  9689  Respond ONLY with valid JSON in this exact format:
  9690  {{
  9691    "extracted_name": "<full name from document>",
  9692    "extracted_id": "<id/passport number from document>",
  9693    "name_match": <true/false>,
  9694    "id_match": <true/false>,
  9695    "confidence": <0.0-1.0>,
  9696    "document_appears_genuine": <true/false>,
  9697    "notes": "<any concerns or observations, empty string if none>"
  9698  }}
  9699  
  9700  If you cannot read the document clearly, set confidence below 0.5 and explain in notes."""
  9701  
  9702          _sr = ai_provider.complete(
  9703              [{
  9704                  "role": "user",
  9705                  "content": [
  9706                      {"type": "image", "source": {
  9707                          "type": "base64", "media_type": media_type, "data": img_b64
  9708                      }},
  9709                      {"type": "text", "text": prompt}
  9710                  ]
  9711              }],
  9712              task="sonnet", max_tokens=300,
  9713              provider=_ts_active_provider(), timeout=120)
  9714          raw = _sr.text.strip()
  9715          # Parse JSON from response
  9716          json_match = re.search(r'\{[\s\S]*\}', raw)
  9717          if not json_match:
  9718              raise ValueError("No JSON in Sonnet response")
  9719          result = json.loads(json_match.group())
  9720          verified = (result.get("name_match") and result.get("id_match") and
  9721                      result.get("confidence", 0) >= 0.75 and
  9722                      result.get("document_appears_genuine", True))
  9723          _log_ai_spend(email, "/users/verify-identity", "sonnet_vision",
  9724                        getattr(_sr, "in_tokens", None), getattr(_sr, "out_tokens", None))
  9725          return {
  9726              "verified": bool(verified),
  9727              "confidence": float(result.get("confidence", 0)),
  9728              "extracted_name": result.get("extracted_name", ""),
  9729              "extracted_id": result.get("extracted_id", ""),
  9730              "notes": result.get("notes", ""),
  9731              "model": SONNET_MODEL,
  9732          }
  9733      except HTTPException:
  9734          raise
  9735      except Exception as e:
  9736          return {"verified": False, "confidence": 0.0, "extracted_name": "",
  9737                  "extracted_id": "", "notes": f"Verification error: {str(e)}", "model": SONNET_MODEL}
  9738  
  9739  
  9740  class IdentityVerifyIn(BaseModel):
  9741      id_number: str          # SA ID (13 digits) or passport number
  9742      full_name: str          # As it appears on the document
  9743      doc_type: str = "sa_id" # sa_id | passport | national_id
  9744      doc_url: str            # URL of the already-uploaded ID document in R2
  9745  
  9746  
  9747  class BankingIn(BaseModel):
  9748      account_holder: str
  9749      bank_name: str
  9750      account_number: str   # We store last 4 digits only
  9751      branch_code: str = ""
  9752  
  9753  
```

## /admin/ai-restore + /flags provider block

```python
 12500      return {"services": out, "checked_at": datetime.utcnow().isoformat() + "Z"}
 12501  
 12502  @app.post("/admin/ai-restore")
 12503  def admin_ai_restore(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12504      """P2a: MANUAL restore — the ONLY path back to traffic for a banned (T3) lane
 12505      (David's ruling 31 Jul: dropouts auto-recover, bans wait for the operator)."""
 12506      _p = ((payload or {}).get("provider") or "").strip()
 12507      _t = ((payload or {}).get("task") or "").strip() or None
 12508      if _p not in ai_provider.ADAPTERS:
 12509          raise HTTPException(status_code=400, detail="unknown provider")
 12510      try:
 12511          import ai_breaker as _brk
 12512          n = _brk.restore(_p, _t, who="dashboard-admin")
 12513          _log.warning("AI-BREAKER manual restore: %s/%s (%d rows)", _p, _t or "ALL", n)
 12514          return {"restored": n, "provider": _p, "task": _t or "ALL"}
 12515      except Exception as e:
 12516          raise HTTPException(status_code=500, detail="restore failed: " + str(e)[:120]) from e
 12517  
 12518  @app.post("/admin/ai-test")   # AITEST-ROUTE-1 (17 Jul, found live by David's demo): decorator was pasted onto demand_sweep; real tester was never registered
 12519  def admin_ai_test(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 12520      """David-only: run a tiny prompt through the ACTIVE provider via the ai_provider seam
 12521      (full translate+call+parse path). Lets the Page-4 switch be tested live against either
 12522      provider without touching the 15 production call sites. Returns the text + which provider/model answered."""
 12523      _req_prov=((payload or {}).get("provider") or "").strip()   # P1: optional explicit provider
 12524      if _req_prov and _req_prov not in ai_provider.ADAPTERS:
 12525          raise HTTPException(status_code=400, detail="unknown provider: "+_req_prov[:40])
 12526      try:
 12527          import ai_provider as _ap
 12528          prov=_req_prov or _ts_active_provider()
 12529          prompt=((payload or {}).get("prompt") or "Reply with exactly: TrustSquare AI provider test OK.").strip()
 12530          r=_ap.complete([{"role":"user","content":prompt}], task="haiku", max_tokens=40, provider=prov)
 12531          return {"ok": bool(r.ok), "provider": r.provider, "model": r.model,
 12532                  "text": (r.text or "")[:400], "in_tokens": r.in_tokens, "out_tokens": r.out_tokens}
 12533      except Exception as e:
 12534          raise HTTPException(status_code=500, detail="ai-test failed: "+str(e)[:160]) from e
 12535  
 12536  
 12537  class _FlagsUpdate(BaseModel):
 12538      mode:          Optional[str]  = None
 12539      verified_tier: Optional[bool] = None
 12540      videos:        Optional[bool] = None
 12541      data_ops:      Optional[bool] = None
 12542      data_places:   Optional[bool] = None
 12543      data_flights:  Optional[bool] = None
 12544      data_mapbox:   Optional[bool] = None
 12545      p_heritage:    Optional[bool] = None
 12546      p_expedition:  Optional[bool] = None
 12547      p_weekend:     Optional[bool] = None
 12548      # BIT safe-state flags (Mitigator-writable; see §13.1)
 12549      ai_example_enabled:    Optional[bool] = None
 12550      auth_fail_closed:      Optional[bool] = None
 12551      tuppence_burn_enabled: Optional[bool] = None
 12552      ai_active:             Optional[str]  = None  # AI provider seam: 'anthropic' | 'openai' | 'scaleway' (Page-4 switch)
 12553      ai_active_override:    Optional[str]  = None  # MANUAL PIN: provider = pin (TTL decay) | '' = unpin (1 Aug 2026)
 12554      fault_report:          Optional[bool] = None  # MAINT-B1b: in-app tester fault intake visible
 12555  
 12556  def _flags_payload(d):
 12557      def b(k): return bool(d.get(k, 0))
 12558      live = (d.get("mode", "launch") == "live")
 12559      return {
 12560          "mode": d.get("mode", "launch"),
 12561          "verified_tier": b("verified_tier"), "videos": b("videos"),
 12562          "fault_report": b("fault_report"),
 12563          "data": {"ops": b("data_ops"), "places": b("data_places"),
 12564                   "flights": b("data_flights"), "mapbox": b("data_mapbox")},
 12565          "planners": {"heritage": b("p_heritage"), "expedition": b("p_expedition"),
 12566                       "weekend": b("p_weekend")},
 12567          "effective": {
 12568              "verified_visible":    live and b("verified_tier"),
 12569              "videos_visible":      b("videos"),  # decoupled from live mode (David 29 Jun): dashboard videos toggle controls it on its own; verified/paid-feed gates stay live-gated
 12570              "heritage_verified":   live and b("verified_tier") and b("p_heritage"),
 12571              "expedition_verified": live and b("verified_tier") and b("p_expedition"),
 12572              "weekend_verified":    live and b("verified_tier") and b("p_weekend"),
 12573          },
 12574          "bit_flags": {
 12575              "ai_example_enabled":    bool(d.get("ai_example_enabled", 1)),
 12576              "auth_fail_closed":      bool(d.get("auth_fail_closed", 0)),
 12577              "tuppence_burn_enabled": bool(d.get("tuppence_burn_enabled", 1)),
 12578          },
 12579          "ai_provider": {
 12580              # effective = the lane calls actually use RIGHT NOW (pin-aware); standing = the
 12581              # auto/default lane the system returns to when the pin decays.
 12582              "active": _ts_active_provider(),   # pin-aware effective lane
 12583              "standing": d.get("ai_active", "anthropic"),
 12584              "override": ({"provider": _TS_AI_CACHE["override"], "expires_at": _TS_AI_CACHE["expires"]}
 12585                            if _TS_AI_CACHE.get("override") else None),
 12586              "override_ttl_hours": AI_OVERRIDE_TTL_HOURS,
 12587              "funnel": _ts_funnel_snapshot(),
 12588              # FAIL-OPEN here too (FLAGS-BRK-1, 1 Aug): a missing/broken breaker module must
 12589              # never take /flags down — the card degrades, the platform does not.
 12590              "breaker": _ts_breaker_safe("snapshot"),
 12591              "drill": _ts_breaker_safe("drill"),
 12592              # which providers have a REAL adapter wired (vs stub) — Page 4 greys out the stubs
 12593              "available": {"anthropic": bool(ANTHROPIC_API_KEY), "openai": bool(ai_provider.envkey("OPENAI_API_KEY")),
 12594                            "scaleway": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY"))},
 12595              # P1: ordered provider cards for the NEW dashboard UI (old card keeps reading active/available above)
 12596              "providers": [
 12597                  {"id": "anthropic", "label": "Anthropic (Claude)", "family": "us", "jurisdiction": "US",
 12598                   "available": bool(ANTHROPIC_API_KEY),
 12599                   "models": ai_provider.TASK_MODEL.get("anthropic", {})},
 12600                  {"id": "scaleway", "label": "Scaleway EU", "family": "open", "jurisdiction": "EU · Paris",
 12601                   "available": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")),
 12602                   "models": ai_provider.TASK_MODEL.get("scaleway", {})},
 12603                  {"id": "openai", "label": "OpenAI (GPT-5.6)", "family": "us", "jurisdiction": "US",
 12604                   "available": bool(ai_provider.envkey("OPENAI_API_KEY")),
 12605                   "models": ai_provider.TASK_MODEL.get("openai", {})},
 12606              ],
 12607          },
 12608          "updated_at": d.get("updated_at", ""),
 12609      }
 12610  
 12611  def _ts_breaker_safe(what):
 12612      try:
 12613          import ai_breaker as _b
 12614          if what == "snapshot": return _b.snapshot()
 12615          return sorted(_b.drill_banned()) or None
 12616      except Exception:
 12617          return None
 12618  
 12619  _TS_FUNNEL_CACHE = {"mtime": None, "data": None}
 12620  def _ts_funnel_snapshot():
 12621      """The +1 card's funnel strip: ORDER AND GATE-TYPES ONLY (David 1 Aug 2026 — no numbers).
 12622      Read from ai_funnel_snapshot.json, generated by scripts/price_truth.py --snapshot (ONE
 12623      ranking engine); absent file -> None, dashboard shows nothing. Cached on mtime."""
 12624      import os as _os
 12625      p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ai_funnel_snapshot.json")
 12626      try:
 12627          mt = _os.path.getmtime(p)
 12628          if _TS_FUNNEL_CACHE["mtime"] != mt:
 12629              with open(p, encoding="utf-8") as fh:
 12630                  _TS_FUNNEL_CACHE.update(mtime=mt, data=json.load(fh))
 12631          return _TS_FUNNEL_CACHE["data"]
 12632      except Exception:
 12633          return None
 12634  
 12635  @app.get("/flags")
 12636  def get_flags():
 12637      """Public — buyer app + dashboard read launch-switch state. Safe default = launch/free-only."""
 12638      conn = database.get_db()
 12639      try:
 12640          row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
 12641      finally:
 12642          conn.close()
 12643      return _flags_payload(dict(row) if row else {})
 12644  
 12645  @app.post("/admin/flags")
 12646  def set_flags(upd: _FlagsUpdate, _admin=Depends(_require_admin)):
 12647      """Admin (JWT) — flip the launch switch. Writes the singleton row, returns full state."""
 12648      data = upd.dict(exclude_unset=True)
 12649      sets, vals = [], []
```

## /admin/ai-spend summary endpoint

```python
  4855  # ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
  4856  
  4857  @app.get("/admin/ai-spend/summary")
  4858  def admin_ai_spend_daily_summary(_admin=Depends(_require_admin_or_key)):
  4859      """Live AI-spend summary for the nightly cost-compliance sweep (P2, 11 Jun 2026).
  4860      Returns today's and 7-day spend, the configured ceilings, and a 7-day
  4861      per-endpoint/model breakdown. Read-only; $0; admin key required."""
  4862      conn = database.get_db()
  4863      try:
  4864          today = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
  4865          week = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
  4866          t = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  4867                           "FROM ai_spend_log WHERE logged_at >= ?", (today,)).fetchone()
  4868          w = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  4869                           "FROM ai_spend_log WHERE logged_at >= ?", (week,)).fetchone()
  4870          cfg = conn.execute("SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  4871                             "FROM ai_spend_config WHERE id = 1").fetchone()
  4872          by_ep = conn.execute(
  4873              "SELECT endpoint, model, COALESCE(SUM(est_cost_usd),0) AS usd, COUNT(*) AS calls, "
  4874              "SUM(cost_is_real) AS real_rows FROM ai_spend_log WHERE logged_at >= ? "
  4875              "GROUP BY endpoint, model ORDER BY usd DESC LIMIT 25", (week,)).fetchall()
  4876      finally:
  4877          conn.close()
  4878      return {
  4879          "today_usd": round(t["u"], 4), "today_calls": t["n"],
  4880          "week_usd": round(w["u"], 4), "week_calls": w["n"],
  4881          "daily_user_ceiling_usd": (cfg["daily_user_ceiling_usd"] if cfg else 0) or 0,
  4882          "daily_platform_ceiling_usd": (cfg["daily_platform_ceiling_usd"] if cfg else 0) or 0,
  4883          "ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
  4884                              else "platform ceiling is 0/unset — AI spend is UNCAPPED"),
  4885          "by_endpoint": [{"endpoint": r["endpoint"], "model": r["model"],
  4886                           "usd": round(r["usd"], 4), "calls": r["calls"],
  4887                           "estimated_rows": r["calls"] - (r["real_rows"] or 0)} for r in by_ep],
  4888      }
  4889  
  4890  
  4891  @app.post("/admin/migrate-photos")
  4892  def migrate_photos(_admin=Depends(_require_admin_or_key)):
  4893      """Migrate existing local photos to Hetzner Object Storage.
  4894      Idempotent — skips listings already pointing to an S3 URL.
  4895      Does NOT delete local files.
  4896      Returns: { migrated, failed, skipped }
  4897      """
  4898      if not _S3_CONFIGURED:
  4899          raise HTTPException(status_code=503, detail="Object Storage not configured — set HETZNER_S3_* env vars")
  4900      conn = database.get_db()
  4901      rows = conn.execute(
  4902          "SELECT id, thumb_url, medium_url FROM listings WHERE thumb_url LIKE '/media/%'"
  4903      ).fetchall()
  4904      migrated = failed = skipped = 0
  4905      for row in rows:
  4906          listing_id  = row["id"]
  4907          thumb_path  = row["thumb_url"]  or ""
  4908          medium_path = row["medium_url"] or ""
  4909          if not thumb_path.startswith("/media/"):
```

## Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop

```python
 16793  
 16794  
 16795  # ── SCOREBOARD-1 (3 Aug 2026): the silent scoreboard agent, nightly ──────────
 16796  # The SLOW-signal half of the failover programme (fast signals = ai_breaker):
 16797  # probes every configured lane x task tier each night at 03:33 SAST (01:33 UTC,
 16798  # after the 03:17 backup), stores history in ai_scoreboard_probes (primary DB,
 16799  # so it rides the backup lanes), writes the rolling 90-day ranking to
 16800  # ai_scoreboard.json. Quality is a GATE not a weight (golden-set registry).
 16801  # Spend-gated OFF by default — launch_switches.scoreboard_enabled=1
 16802  # (enable_scoreboard.bat) is David's explicit click. Import-guarded and
 16803  # exception-walled: a scoreboard failure can never hurt the app.
 16804  try:
 16805      import ai_scoreboard as _ts_scoreboard
 16806  except Exception as _ts_sb_err:
 16807      _ts_scoreboard = None
 16808      print("SCOREBOARD-1: module not importable (%s) — nightly probes off" % _ts_sb_err)
 16809  
 16810  if _ts_scoreboard is not None:
 16811      @app.on_event("startup")
 16812      async def _ts_scoreboard_nightly():
 16813          async def _sb_loop():
 16814              while True:
 16815                  _now = datetime.now(timezone.utc)
 16816                  _nxt = _now.replace(hour=1, minute=33, second=0, microsecond=0)
 16817                  if _nxt <= _now:
 16818                      _nxt += timedelta(days=1)
 16819                  await asyncio.sleep(max(60.0, (_nxt - _now).total_seconds()))
 16820                  try:
 16821                      await asyncio.get_running_loop().run_in_executor(
 16822                          None, _ts_scoreboard.run_nightly)
 16823                  except Exception as _sb_e:
 16824                      print("SCOREBOARD-1 nightly error: %s" % _sb_e)
 16825          asyncio.get_running_loop().create_task(_sb_loop())
 16826  
 16827  
 16828  # ── HEARTBEAT-1 (5 Aug 2026, David's F5 ruling: live NOW, confidence before launch) ──
 16829  # P2c idle-recovery heartbeat per AI_AUTO_FAILOVER_P2_DESIGN §6: every 60 s, if any
 16830  # breaker row is eligible (tripped/half_open, probe window open), claim and send ONE
 16831  # direct probe — one per tick TOTAL, round-robin, so a bad night can never multiply
 16832  # cost. Text ping only (~$0.00002); T3 rows carry hourly probe_after, so bans probe
 16833  # hourly. Spend is logged like all spend. Fail-open: any error waits for the next tick.
 16834  @app.on_event("startup")
 16835  async def _ts_breaker_heartbeat():
 16836      async def _hb_loop():
 16837          _rr = 0
 16838          while True:
 16839              await asyncio.sleep(60)
 16840              try:
 16841                  import ai_breaker as _hb_brk
 16842                  if getattr(_hb_brk, "_get_db", None) is None:
 16843                      continue   # breaker unattached — nothing to probe
 16844                  _hb_conn = database.get_db()
 16845                  try:
 16846                      _rows = _hb_conn.execute(
 16847                          "SELECT provider, task FROM ai_breaker "
 16848                          "WHERE state IN ('tripped','half_open') "
 16849                          "AND (probe_after IS NULL OR probe_after <= ?) "
 16850                          "ORDER BY provider, task",
 16851                          (datetime.utcnow().isoformat(timespec="seconds"),)).fetchall()
 16852                  finally:
 16853                      _hb_conn.close()
 16854                  if not _rows:
 16855                      continue
 16856                  _row = _rows[_rr % len(_rows)]; _rr += 1
 16857                  _p, _t = _row["provider"], _row["task"]
 16858                  if not _hb_brk.claim_probe(_p, _t):
 16859                      continue   # someone else holds the half-open lease
 16860                  _r = await asyncio.to_thread(
 16861                      ai_provider.complete, [{"role": "user", "content": "ping"}],
 16862                      task=_t, max_tokens=8, provider=_p, probe=True, timeout=20)
 16863                  _log_ai_spend("system:heartbeat", "/breaker/heartbeat", _t,
 16864                                _r.in_tokens, _r.out_tokens)
 16865              except Exception as _hb_e:
 16866                  print("HEARTBEAT-1 error: %s" % _hb_e)
 16867      asyncio.get_running_loop().create_task(_hb_loop())
```


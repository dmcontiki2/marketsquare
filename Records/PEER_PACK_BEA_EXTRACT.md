# PEER PACK — targeted evidence extract (v3)

*Generated 2026-08-22 04:47 UTC. Each line keeps its REAL line number in its source file so*
*citations are checkable. If a section you need is absent, name the exact file and*
*line range as a finding and it will be supplied next run.*

## COMPUTED TOTALITY EVIDENCE (Author-derived greps over the full bea_main.py — treat as claims; spot-check by requesting ranges)

- Vendor inference hosts named in bea_main.py (19639 lines): {'api.anthropic.com': 0, 'api.openai.com': 0, 'api.scaleway.ai': 0}
- Old vendor-specific gates ('if not ANTHROPIC_API_KEY') remaining: NONE
- Vendor-neutral gates ('if not ai_provider.any_lane_configured()'): 15 at lines [3993, 6273, 6394, 6471, 6548, 10270, 10492, 11121, 16279, 16368, 16953, 17266, 17492, 17752, 18692]
- Every line invoking ai_provider.complete: [15, 4023, 6292, 6428, 6498, 6797, 10322, 10518, 11137, 11166, 13523, 15877, 15882, 16325, 16429, 17118, 17403, 17562, 17785, 18749, 19479, 19495, 19563]
- Every _deduct_tuppence call line: [5620, 6832, 16348, 16456, 17144, 17429, 17597]

## Admin auth dependency (used by /admin/ai-* endpoints) — from bea_main.py

```
   113  MS_ADMIN_KEY = os.environ.get("MS_ADMIN_KEY", "")
   114  
   115  def _require_admin_or_key(x_admin_token: str = Header(default=None),
   116                            x_admin_key: str = Header(default=None)):
   117      if x_admin_key and MS_ADMIN_KEY and x_admin_key == MS_ADMIN_KEY:
   118          return {"via": "admin-key"}
   119      if x_admin_token and _JWT_SECRET:
   120          try:  # _pyjwt/_JWT_SECRET defined later at module level — resolved at call time
   121              return _pyjwt.decode(x_admin_token, _JWT_SECRET, algorithms=[_JWT_ALGO])
   122          except Exception:
   123              pass
   124      raise HTTPException(status_code=401, detail="Admin credentials required.")
   125  from email.utils import parseaddr, formataddr
   126  from datetime import datetime, timezone, timedelta
   127  
   128  app = FastAPI(title="TrustSquare BEA", version="1.3.1")
   129  
   130  # DEPLOY-HOOK-1 (17 Aug 2026): authenticated HTTPS deploy trigger — see
   131  # ops/autodeploy/deploy_router.py. Fail-closed twice over: import-safe when the
   132  # file is absent (local dev), and the endpoint itself answers 503 until David
   133  # mints MS_DEPLOY_TOKEN on the server (add_deploy_token.bat).
   134  try:
   135      from deploy_router import router as _deploy_router      # noqa: E402
   136      app.include_router(_deploy_router)
   137  except ImportError:
   138      pass  # router not deployed alongside — hook lane simply absent
   139  
   140  # S4 (audit · HIGH): CORS locked to TrustSquare origins only.
   141  # Previously allow_origins=["*"] + allow_origin_regex=".*" — any site could call the BEA
   142  # from a user's browser. Auth is X-Api-Key/email (allow_credentials stays False), and the
```

## Breaker wiring at BEA startup (attach + alert hook) — from bea_main.py

```
   202  # an attach failure leaves the seam exactly as it was yesterday (naive any-of fallback).
   203  try:
   204      import ai_breaker as _ai_brk
   205      def _brk_alert(payload):
   206          try:
   207              _log.warning("AI-BREAKER %s: %s", payload.get("event"), payload)
   208              _hook = os.getenv("N8N_WEBHOOK_AI_ALERT")
   209              if _hook:
   210                  import httpx as _hx
   211                  with _hx.Client(timeout=5) as _c: _c.post(_hook, json={"source": "ai_breaker", **payload})
   212          except Exception:
   213              pass
   214      _ai_brk.attach(database.get_db, alert=_brk_alert)
   215  except Exception as _brk_e:
   216      import logging as _lg; _lg.getLogger("bea").warning("ai_breaker attach failed (fail-open): %r", _brk_e)
   217  
   218  
   219  # CityLauncher scrapes AGENCY vocabulary ("Estate Agents", "Car Dealers", ...); the app
   220  # speaks 6 category names. This maps a scraped label to the app category the demand loop
   221  # matches on. Keyword-based so it survives new agency labels; None = leave unmatched.
   222  def _demand_norm_category(raw):
   223      t = (raw or "").strip().lower()
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
   883          conn.execute("ALTER TABLE ai_spend_log ADD COLUMN provider TEXT")
   884  
   885      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_config (
   886          id                  INTEGER PRIMARY KEY CHECK (id = 1),
   887          monthly_income_usd  REAL    NOT NULL DEFAULT 0.0,
   888          alert_threshold_pct REAL    NOT NULL DEFAULT 20.0,
   889          alert_email         TEXT    NOT NULL DEFAULT 'dmcontiki2@gmail.com',
   890          last_alerted_at     TEXT
   891      )""")
   892      # Seed default config row (id=1 enforced by CHECK constraint)
   893      conn.execute("""INSERT OR IGNORE INTO ai_spend_config
   894          (id, monthly_income_usd, alert_threshold_pct, alert_email)
   895          VALUES (1, 0.0, 20.0, 'dmcontiki2@gmail.com')""")
   896  
   897      # C1-RES (AI-SERVICES-AUDIT-1 F2, 5 Aug 2026): pre-dispatch spend RESERVATIONS.
   898      # The ceiling check summed only LOGGED spend, which is written AFTER the call — so
   899      # N concurrent calls all passed the check before any recorded its cost and could
   900      # collectively overshoot. A reservation is a short-lived worst-case hold placed
   901      # BEFORE dispatch and counted by the ceiling check; it is settled when real spend
   902      # is logged, and self-expires so an aborted call can never wedge the budget.
   903      conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_holds (
   904          id         INTEGER PRIMARY KEY AUTOINCREMENT,
   905          email      TEXT    NOT NULL DEFAULT '',
   906          est_usd    REAL    NOT NULL DEFAULT 0.0,
   907          created_at TEXT    NOT NULL DEFAULT '',
   908          expires_at TEXT    NOT NULL
   909      )""")
   910  
   911      # INTRO-RELAY-1 (5 Aug 2026, David's Option B ruling): masked-alias introduction
   912      # relay. Two rows per accepted intro - one alias per party. real_email is the ONLY
   913      # place the real address lives; it never enters an outbound body, header, or
   914      # webhook. Doctrine: nothing of the customer's leaves TrustSquare except a
   915      # consented, revocable email channel - never the address itself.
   916      conn.execute("""CREATE TABLE IF NOT EXISTS intro_relay_aliases (
   917          alias         TEXT PRIMARY KEY,
   918          intro_id      INTEGER NOT NULL,
   919          party         TEXT NOT NULL,
   920          real_email    TEXT NOT NULL,
   921          counter_alias TEXT NOT NULL,
   922          active        INTEGER NOT NULL DEFAULT 1,
   923          created_at    TEXT NOT NULL DEFAULT '',
   924          expires_at    TEXT NOT NULL
   925      )""")
   926      conn.execute("CREATE INDEX IF NOT EXISTS idx_relay_intro ON intro_relay_aliases(intro_id)")
   927  
   928      # Launch Switch (free-only <-> verified) — singleton flag row; default = launch/free-only
   929      conn.execute("""CREATE TABLE IF NOT EXISTS launch_switches (
   930          id            INTEGER PRIMARY KEY CHECK (id = 1),
   931          mode          TEXT    NOT NULL DEFAULT 'launch',
   932          verified_tier INTEGER NOT NULL DEFAULT 0,
   933          videos        INTEGER NOT NULL DEFAULT 0,
   934          data_ops      INTEGER NOT NULL DEFAULT 0,
   935          data_places   INTEGER NOT NULL DEFAULT 0,
   936          data_flights  INTEGER NOT NULL DEFAULT 0,
   937          data_mapbox   INTEGER NOT NULL DEFAULT 0,
   938          p_heritage    INTEGER NOT NULL DEFAULT 0,
   939          p_expedition  INTEGER NOT NULL DEFAULT 0,
   940          p_weekend     INTEGER NOT NULL DEFAULT 0,
   941          -- BIT safe-state flags (Mitigator flips these to a SAFE value on a confirmed BIT failure).
   942          -- Defaults = NORMAL/healthy state; the Mitigator only ever moves them toward safe.
   943          ai_example_enabled     INTEGER NOT NULL DEFAULT 1,
   944          auth_fail_closed       INTEGER NOT NULL DEFAULT 0,
   945          tuppence_burn_enabled  INTEGER NOT NULL DEFAULT 1,
   946          -- AI provider seam (D1): live-switchable inference vendor (Page-4 control). Default = anthropic.
   947          ai_active     TEXT    NOT NULL DEFAULT 'anthropic',
   948          -- MANUAL PIN (David 1 Aug 2026): operator override with DECAY — precedence over any
   949          -- auto selection while unexpired; expiry returns control to the standing lane.
   950          ai_active_override  TEXT,
   951          ai_override_expires TEXT,
   952          -- MAINT-B1b: in-app tester fault intake. OFF by default (fail-closed).
```

## Spend logging, alerting, cost ceiling — from bea_main.py

```
  1767  
  1768  
  1769  def _log_ai_spend(email: str, endpoint: str, model_key: str,
  1770                    in_tok: int | None = None, out_tok: int | None = None,
  1771                    provider: str | None = None, model: str | None = None):
  1772      """Background task: log AI call cost + trigger alert check if threshold crossed.
  1773      Non-blocking — called via background_tasks.add_task() after every AI call.
  1774      Never raises — log errors only.
  1775  
  1776      C2 (Session 97): real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
  1777      No tokens (legacy sites) -> flat _AI_COST estimate, cost_is_real=0. Backward compatible.
  1778  
  1779      P6 (15 Aug 2026 — AI_LANE_GUIDANCE, baseline drift D3): call sites that hold the
  1780      AIResult pass provider= and model= — the lane and model that ACTUALLY answered — so
  1781      a failover is attributed to the serving lane and costed at that lane's price. With
  1782      OpenAI as base, a sustained failover to Anthropic is a ~4.4x cost event on the haiku
  1783      tier; before this fix it was attributed to the intended lane and costed at the wrong
  1784      rate, i.e. invisible. Callers passing neither keep intended-lane attribution (an
  1785      honest guess, wrong exactly when a mid-call failover occurred).
  1786      """
  1787      try:
  1788          if provider:
  1789              _prov = provider            # serving lane, straight from AIResult.provider
  1790          else:
  1791              try:
  1792                  _prov = _ts_active_provider()   # legacy caller: INTENDED lane
  1793              except Exception:
  1794                  _prov = 'anthropic'
  1795          _mid = model or _tier_model(model_key, _prov)   # model that answered (or lane's map)
  1796          if in_tok is not None or out_tok is not None:
  1797              it, ot = int(in_tok or 0), int(out_tok or 0)
  1798              cost = _token_cost(_mid, it, ot, _prov)
  1799              is_real = 1
  1800          else:
  1801              it, ot = 0, 0
  1802              cost = _AI_COST.get(model_key, 0.0023)
  1803              is_real = 0
  1804          conn = database.get_db()
  1805          try:
  1806              conn.execute(
  1807                  "INSERT INTO ai_spend_log "
  1808                  "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real, provider) "
  1809                  "VALUES (?,?,?,?,?,?,?,?)",
  1810                  (email or '', endpoint, model_key, cost, it, ot, is_real, _prov)
  1811              )
  1812              conn.commit()
  1813              _maybe_fire_spend_alert(conn)
  1814          finally:
  1815              conn.close()
  1816          _maybe_fire_lane_alert(_prov, endpoint, email or '')   # AL-1/AL-2, AI_BASELINE alert_rules
  1817          _settle_hold(email or '')   # C1-RES: real spend recorded — release the reservation
  1818      except Exception as exc:
  1819          _log.error("_log_ai_spend failed: %s", exc)
  1820  
  1821  
  1822  # ── AL-1 / AL-2 — lane alert rules (AI_BASELINE.json alert_rules, 15 Aug 2026) ──────
  1823  # AL-1: the serving lane is not the base lane for >60 min — a sustained failover is a
  1824  #       re-pricing event (anthropic is 4.4x base on haiku). AL-2: the SAFETY NET lane
  1825  #       serves at all — cost-exempt by role, but reaching it must alert and be time-boxed.
  1826  # Heartbeat/probe rows are excluded: they exercise every lane by design.
  1827  _LANE_ALERT = {"base": None, "safety": None, "offbase_since": None,
  1828                 "last_al1": 0.0, "last_al2": 0.0}
  1829  
  1830  def _lane_alert_roles():
  1831      """(base_lane, safety_net_lane) from AI_BASELINE.json; RUL-002 literals if absent."""
  1832      if _LANE_ALERT["base"] is None:
  1833          base_lane, safety = "openai", "scaleway"
  1834          try:
  1835              with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
  1836                                     "AI_BASELINE.json"), encoding="utf-8") as _fh:
  1837                  _b = json.load(_fh)
  1838              base_lane = _b.get("baseline_lane") or base_lane
  1839              for _ln, _r in (_b.get("lane_roles") or {}).items():
  1840                  if _r.get("cost_exempt"):
  1841                      safety = _ln
  1842          except Exception:
  1843              pass
  1844          _LANE_ALERT["base"], _LANE_ALERT["safety"] = base_lane, safety
  1845      return _LANE_ALERT["base"], _LANE_ALERT["safety"]
  1846  
  1847  def _maybe_fire_lane_alert(prov: str, endpoint: str, email: str = ""):
  1848      """Never raises; at most one webhook per rule per hour."""
  1849      try:
  1850          if endpoint == "/breaker/heartbeat" or (email or "").startswith("system:"):
  1851              return
  1852          import time as _t
  1853          base_lane, safety = _lane_alert_roles()
  1854          now = _t.time()
  1855          payload = None
  1856          if prov == safety and (now - _LANE_ALERT["last_al2"]) > 3600:
  1857              _LANE_ALERT["last_al2"] = now
  1858              _log.error("AL-2: SAFETY NET lane %r served %s — cost-exempt by role, but an "
  1859                         "unnoticed week here is an ~8x cost event nobody approved", prov, endpoint)
  1860              payload = {"alert": "ai_lane_al2_safety_net", "serving": prov,
  1861                         "endpoint": endpoint, "rule": "AL-2: safety net serving at all"}
  1862          if prov != base_lane:
  1863              if _LANE_ALERT["offbase_since"] is None:
  1864                  _LANE_ALERT["offbase_since"] = now
  1865              elif (now - _LANE_ALERT["offbase_since"]) > 3600 and (now - _LANE_ALERT["last_al1"]) > 3600:
  1866                  _LANE_ALERT["last_al1"] = now
  1867                  _log.error("AL-1: serving lane %r off-base (base=%r) for >60 min — a sustained "
  1868                             "failover is a re-pricing event", prov, base_lane)
  1869                  payload = payload or {"alert": "ai_lane_al1_offbase_60m", "serving": prov,
  1870                                        "base": base_lane, "endpoint": endpoint,
  1871                                        "rule": "AL-1: off-base >60 minutes"}
  1872          else:
  1873              _LANE_ALERT["offbase_since"] = None   # base lane served — the failover has ended
  1874          if payload and N8N_WEBHOOK_AI_ALERT:
  1875              import asyncio as _aio
  1876              try:
  1877                  _loop = _aio.get_event_loop()
  1878                  if _loop.is_running():
  1879                      _loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
  1880              except Exception:
  1881                  pass  # alert failure must never affect user response
  1882      except Exception as exc:
  1883          _log.error("_maybe_fire_lane_alert failed: %s", exc)
  1884  
  1885  
  1886  def _maybe_fire_spend_alert(conn):
  1887      """Check if current month AI spend has crossed the configured threshold.
  1888      Fires n8n webhook at most once per day. Silent if not configured.
  1889      """
  1890      try:
  1891          cfg = conn.execute(
  1892              "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
  1893              "FROM ai_spend_config WHERE id = 1"
  1894          ).fetchone()
  1895          if not cfg or cfg["monthly_income_usd"] <= 0:
  1896              return  # income not configured yet — skip
  1897  
  1898          # Current calendar month spend
  1899          month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
  1900          row = conn.execute(
  1901              "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
  1902              "WHERE logged_at >= ?", (month_start,)
  1903          ).fetchone()
  1904          month_spend = row["total"] if row else 0.0
  1905  
  1906          threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
  1907          if month_spend < threshold_usd:
  1908              return  # under threshold — nothing to do
  1909  
  1910          # Check last alerted — don't fire more than once per day
  1911          last = cfg["last_alerted_at"] or ""
  1912          today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
  1913          if last.startswith(today):
  1914              return  # already alerted today
  1915  
  1916          # Update last_alerted_at
  1917          conn.execute(
  1918              "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
  1919              (__import__('datetime').datetime.utcnow().isoformat(),)
  1920          )
  1921          conn.commit()
  1922  
  1923          # Fire n8n alert webhook if configured
  1924          pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
  1925          payload = {
  1926              "alert": "ai_spend_threshold",
```

## Active provider switch + pin/override (TTL decay) — from bea_main.py

```
  1640  # Manual-pin TTL (hours). David 1 Aug 2026: 24h now; REVIEW dated ~1 Nov 2026 (3 months
  1641  # proven live) to consider shortening to 1h. Env-tunable, no deploy needed to change.
  1642  AI_OVERRIDE_TTL_HOURS = float(os.getenv("AI_OVERRIDE_TTL_HOURS", "24"))
  1643  
  1644  _TS_AI_CACHE = {"prov": None, "standing": None, "override": None, "expires": None, "ts": 0.0}
  1645  def _ts_active_provider():
  1646      """The LIVE active provider — DB-backed (Page-4 switchable, no restart). Falls back to the
  1647      startup env value if the DB is unreachable. Cached ~10s so we never hammer the DB per call."""
  1648      import time as _t
  1649      now=_t.time()
  1650      if _TS_AI_CACHE["prov"] and (now-_TS_AI_CACHE["ts"])<10:
  1651          return _TS_AI_CACHE["prov"]
  1652      prov=_TS_AI_PROVIDER  # startup default
  1653      standing, override, expires = prov, None, None
  1654      try:
  1655          conn=database.get_db()
  1656          try:
  1657              row=conn.execute("SELECT ai_active, ai_active_override, ai_override_expires "
  1658                               "FROM launch_switches WHERE id=1").fetchone()
  1659              if row:
  1660                  if row["ai_active"]: standing = prov = row["ai_active"]
  1661                  override, expires = row["ai_active_override"], row["ai_override_expires"]
  1662          finally:
  1663              conn.close()
  1664      except Exception:
  1665          pass
  1666      # MANUAL PIN precedence with DECAY (David 1 Aug 2026): an unexpired operator pin
  1667      # outranks the standing/auto lane; past expiry the standing lane silently resumes.
  1668      import datetime as _dt
  1669      if override and expires:
  1670          try:
  1671              if _dt.datetime.utcnow() < _dt.datetime.fromisoformat(expires):
  1672                  prov = override
  1673              else:
  1674                  override = None   # expired — report as inactive, standing rules
  1675          except Exception:
  1676              override = None
  1677      else:
  1678          override = None
  1679      _TS_AI_CACHE.update(prov=prov, standing=standing, override=override, expires=expires if override else None, ts=now)
  1680      return prov
  1681  
  1682  def _ts_models_for(prov):
  1683      try:
  1684          return _ts_ai.TASK_MODEL.get(prov, _ts_ai.TASK_MODEL["anthropic"])
  1685      except Exception:
  1686          return _TS_AI_MODELS
  1687  
  1688  # _ts_ai_url()/_ts_ai_headers() REMOVED 31 Jul 2026 — their sole caller (vision-draft) migrated
  1689  # to the ai_provider seam, completing P0 at 22/22 call sites. The wire protocol now lives ONLY in
  1690  # ai_provider.py adapters; RG-0017 asserts no raw vendor endpoint ever returns to this file.
  1691  if not EMAIL_INBOUND_SECRET:
  1692      _log.warning("EMAIL_INBOUND_SECRET not set — /email/inbound will reject all calls")
  1693  if not GMAIL_APP_PASSWORD:
  1694      _log.warning("GMAIL_APP_PASSWORD not set — triage replies will be drafted, never sent")
  1695  
  1696  CF_ZONE_ID    = os.getenv("CF_ZONE_ID")
  1697  CF_CACHE_TOKEN = os.getenv("CF_CACHE_TOKEN")
  1698  
  1699  async def _cf_purge_all():
```

## Tuppence helpers (deduct / balance / pre-flight require) — from bea_main.py

```
 16225  
 16226  
 16227  def _deduct_tuppence(conn, email: str, amount: int, description: str) -> int:
 16228      """Deduct `amount` Tuppence from `email`. Returns new balance.
 16229      Raises HTTPException 402 if balance insufficient. Does NOT commit."""
 16230      row = conn.execute(
 16231          "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 16232          (email,)
 16233      ).fetchone()
 16234      balance = int(row["bal"])
 16235      if balance < amount:
 16236          raise HTTPException(
 16237              status_code=402,
 16238              detail=f"Insufficient Tuppence — you have {balance}T, need {amount}T"
 16239          )
 16240      conn.execute(
 16241          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'ai_service', ?, ?)",
 16242          (email, -amount, description)
 16243      )
 16244      return balance - amount
 16245  
 16246  
 16247  def _current_tuppence(email: str) -> int:
 16248      """Read-only Tuppence balance on a fresh connection. Used by deliver-then-charge
 16249      paths to report 'tuppence_remaining' when NO charge was made."""
 16250      c = database.get_db()
 16251      try:
 16252          row = c.execute(
 16253              "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
 16254              (email,)
 16255          ).fetchone()
 16256          return int(row["bal"])
 16257      finally:
 16258          c.close()
 16259  
 16260  
 16261  def _require_tuppence(email: str, amount: int = 1) -> None:
 16262      """Pre-flight guard: ensure the buyer COULD pay before we run a paid AI service.
 16263      Raises 402 if not. Does NOT deduct — deduction happens only on a verified result."""
 16264      if _current_tuppence(email) < amount:
 16265          raise HTTPException(
 16266              status_code=402,
 16267              detail=f"Insufficient Tuppence — you need {amount}T to run this check."
 16268          )
 16269  
 16270  
 16271  # ── AI1 — Listing Rewrite ─────────────────────────────────────────────────────
 16272  
 16273  @app.post("/listings/{listing_id}/ai-rewrite")
 16274  async def ai_listing_rewrite(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
```

## AI1 Listing Rewrite (full endpoint) — from bea_main.py

```
 16272  
 16273  @app.post("/listings/{listing_id}/ai-rewrite")
 16274  async def ai_listing_rewrite(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 16275      """AI1: Seller pays 1T — Claude Haiku rewrites title + description.
 16276      Uses current market language and buyer psychology for the listing category.
 16277      Returns {new_title, new_description, tuppence_remaining}.
 16278      """
 16279      if not ai_provider.any_lane_configured():
 16280          raise HTTPException(status_code=503, detail="AI not configured")
 16281      email = _bind_charged_email(email, ts_user, "ai1-rewrite")   # ACCOUNT-BIND-1
 16282      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 16283  
 16284      conn = database.get_db()
 16285      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 16286      if not listing:
 16287          conn.close()
 16288          raise HTTPException(status_code=404, detail="Listing not found")
 16289      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 16290          conn.close()
 16291          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 16292  
 16293      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 16294      _rw_charge_desc = f"AI Listing Rewrite · #{listing_id} · {listing['title'][:40]}"
 16295      conn.close()
 16296  
 16297      category = listing["category"] or "General"
 16298      city     = listing["city"] or "South Africa"
 16299      title    = listing["title"] or ""
 16300      desc     = listing["description"] or ""
 16301      price    = listing["price"] or ""
 16302  
 16303      system_prompt = (
 16304          "You are an expert marketplace copywriter for TrustSquare, a South African peer-to-peer local marketplace. "
 16305          "You write short, honest, buyer-friendly listings using current South African market language. "
 16306          "You never invent details. You prefer concrete facts over adjectives. "
 16307          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include street addresses, "
 16308          "business names, complex names, seller names, agent names, phone numbers, email addresses, "
 16309          "or any other identifying information in any generated text. "
 16310          "Always respond with a single valid JSON object — no markdown, no explanation."
 16311      )
 16312  
 16313      user_prompt = (
 16314          f"Rewrite this {category} listing for a buyer in {city}, South Africa.\n\n"
 16315          f"CURRENT TITLE: {title}\n"
 16316          f"CURRENT DESCRIPTION: {desc}\n"
 16317          f"PRICE: {price}\n\n"
 16318          "Return JSON with exactly two keys:\n"
 16319          '{"new_title": "<15 words max, specific and punchy>", '
 16320          '"new_description": "<60-120 words, 2-3 short paragraphs, buyer psychology, honest, no clichés>"}'
 16321      )
 16322  
 16323      try:
 16324          _sr = await asyncio.to_thread(
 16325              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 16326              task="haiku", max_tokens=350, system=system_prompt,
 16327              provider=_ts_active_provider(), timeout=20)
 16328          _rw_in, _rw_out = _sr.in_tokens, _sr.out_tokens
 16329          # P2 — Tuppence covers the revenue side; log token spend so the cost
 16330          # dashboard sees it too (sweep 12 Jun 2026)
 16331          _log_ai_spend(email, "/listings/ai-rewrite", "haiku", _rw_in, _rw_out,
 16332                        provider=_sr.provider, model=_sr.model)
 16333          raw = _sr.text.strip()
 16334          # Strip markdown fences if model adds them
 16335          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 16336          raw = _re_match.sub(r"\s*```$", "", raw)
 16337          result = json.loads(raw)
 16338          new_title = str(result.get("new_title", "")).strip()[:120]
 16339          new_desc  = str(result.get("new_description", "")).strip()[:1000]
 16340      except Exception as exc:
 16341          _log.error("ai-rewrite: %s", exc)
 16342          raise HTTPException(status_code=500, detail="AI rewrite failed — no Tuppence was charged") from exc
 16343  
 16344      # F2 fix: deliver-then-charge — deduction happens ONLY here, after a good result,
 16345      # so the help card's "server error = no Tuppence deducted" promise is true.
 16346      _conn2 = database.get_db()
 16347      try:
 16348          remaining = _deduct_tuppence(_conn2, email, 1, _rw_charge_desc)
 16349          _conn2.commit()
 16350      finally:
 16351          _conn2.close()
 16352      _log.info("ai-rewrite: listing #%d email=%s", listing_id, email)
 16353      return {
 16354          "new_title": new_title,
 16355          "new_description": new_desc,
 16356          "tuppence_remaining": remaining,
 16357      }
 16358  
 16359  
 16360  # ── AI2 — Seller Audit ────────────────────────────────────────────────────────
 16361  
 16362  @app.post("/listings/{listing_id}/ai-audit")
 16363  async def ai_seller_audit(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 16364      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 16365      3 specific, actionable improvement steps.
 16366      Returns {actions: [{step, reason}], tuppence_remaining}.
 16367      """
 16368      if not ai_provider.any_lane_configured():
 16369          raise HTTPException(status_code=503, detail="AI not configured")
 16370      email = _bind_charged_email(email, ts_user, "ai2-audit")   # ACCOUNT-BIND-1
 16371      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
```

## AI2 Seller Audit (full endpoint) — from bea_main.py

```
 16361  
 16362  @app.post("/listings/{listing_id}/ai-audit")
 16363  async def ai_seller_audit(listing_id: int, email: str, ts_user: str = Cookie(default=None)):
 16364      """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
 16365      3 specific, actionable improvement steps.
 16366      Returns {actions: [{step, reason}], tuppence_remaining}.
 16367      """
 16368      if not ai_provider.any_lane_configured():
 16369          raise HTTPException(status_code=503, detail="AI not configured")
 16370      email = _bind_charged_email(email, ts_user, "ai2-audit")   # ACCOUNT-BIND-1
 16371      _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 16372  
 16373      conn = database.get_db()
 16374      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 16375      if not listing:
 16376          conn.close()
 16377          raise HTTPException(status_code=404, detail="Listing not found")
 16378      if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
 16379          conn.close()
 16380          raise HTTPException(status_code=403, detail="Email does not match listing owner")
 16381  
 16382      # Read intro request count for context
 16383      intro_row = conn.execute(
 16384          "SELECT COUNT(*) as cnt FROM intro_requests WHERE listing_id = ?", (listing_id,)
 16385      ).fetchone()
 16386      intro_count = intro_row["cnt"] if intro_row else 0
 16387  
 16388      # Read trust score
 16389      user_row = conn.execute(
 16390          "SELECT trust_score FROM users WHERE email = ?", (email,)
 16391      ).fetchone()
 16392      trust_score = user_row["trust_score"] if user_row and user_row["trust_score"] else "unknown"
 16393  
 16394      _require_tuppence(email, 1)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 16395      _au_charge_desc = f"AI Seller Audit · #{listing_id} · {listing['title'][:40]}"
 16396      conn.close()
 16397  
 16398      category = listing["category"] or "General"
 16399      city     = listing["city"] or "South Africa"
 16400      title    = listing["title"] or "(no title)"
 16401      desc     = listing["description"] or "(no description)"
 16402      price    = listing["price"] or "(no price)"
 16403  
 16404      system_prompt = (
 16405          "You are a marketplace performance coach for TrustSquare, a South African peer-to-peer marketplace. "
 16406          "You give direct, specific, actionable advice — no filler, no encouragement padding. "
 16407          "Think like a top-performing seller in the same category who has seen hundreds of listings. "
 16408          "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include or suggest including "
 16409          "street addresses, business names, seller names, agent names, phone numbers, or contact details "
 16410          "in any generated text or improvement suggestions. "
 16411          "Always respond with a single valid JSON object — no markdown, no explanation."
 16412      )
 16413  
 16414      user_prompt = (
 16415          f"This {category} listing in {city} has received {intro_count} intro request(s) and "
 16416          f"the seller has a trust score of {trust_score}.\n\n"
 16417          f"TITLE: {title}\n"
 16418          f"DESCRIPTION: {desc}\n"
 16419          f"PRICE: {price}\n\n"
 16420          "Identify the 3 most important reasons a buyer might scroll past this listing without requesting an intro. "
 16421          "For each reason give a specific fix the seller can do right now.\n\n"
 16422          "Return JSON: "
 16423          '{"actions": [{"step": "<imperative fix, 8 words max>", "reason": "<why this matters, 1 sentence>"}, ...]}'
 16424          " — exactly 3 items in the array."
 16425      )
 16426  
 16427      try:
 16428          _sr = await asyncio.to_thread(
 16429              ai_provider.complete, [{"role": "user", "content": user_prompt}],
 16430              task="haiku", max_tokens=400, system=system_prompt,
 16431              provider=_ts_active_provider(), timeout=20)
 16432          _au_in, _au_out = _sr.in_tokens, _sr.out_tokens
 16433          # P2 — Tuppence covers the revenue side; log token spend so the cost
 16434          # dashboard sees it too (sweep 12 Jun 2026)
 16435          _log_ai_spend(email, "/listings/ai-audit", "haiku", _au_in, _au_out,
 16436                        provider=_sr.provider, model=_sr.model)
 16437          raw = _sr.text.strip()
 16438          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 16439          raw = _re_match.sub(r"\s*```$", "", raw)
 16440          result = json.loads(raw)
 16441          actions = result.get("actions", [])
 16442          # Sanitise — max 3, enforce fields
 16443          clean_actions = []
 16444          for a in actions[:3]:
 16445              if isinstance(a, dict) and a.get("step"):
 16446                  clean_actions.append({
 16447                      "step":   str(a.get("step",   ""))[:80],
 16448                      "reason": str(a.get("reason", ""))[:200],
 16449                  })
 16450      except Exception as exc:
 16451          _log.error("ai-audit: %s", exc)
 16452          raise HTTPException(status_code=500, detail="AI audit failed — no Tuppence was charged") from exc
 16453  
 16454      _conn2 = database.get_db()
 16455      try:
 16456          remaining = _deduct_tuppence(_conn2, email, 1, _au_charge_desc)   # F2: charge on delivery
 16457          _conn2.commit()
 16458      finally:
 16459          _conn2.close()
 16460      _log.info("ai-audit: listing #%d email=%s intros=%d", listing_id, email, intro_count)
 16461      return {
 16462          "actions": clean_actions,
 16463          "tuppence_remaining": remaining,
 16464      }
 16465  
 16466  
 16467  # ── AI3 — Buyer Price Check (upgraded Session 77: three-panel intelligence) ──
 16468  
 16469  # -- Tiered Value Selector: availability helpers + value-tiers endpoint --------
 16470  # STEP 5: the paid master switch AND per-provider liveness now come from the
 16471  # server-readable feature_flags store (feature_flags.json), so enabling a paid
 16472  # provider later is a CONFIG change, not a code edit. Safe defaults: paid OFF,
 16473  # every paid/contract provider OFF, free/open/owned providers ON.
 16474  def _paid_tiers_enabled() -> bool:
 16475      return feature_flags.paid_tiers_enabled()
```

## AI3 Price Check (charge logic + integrity model) — from bea_main.py

```
 16934  
 16935  @app.post("/listings/{listing_id}/price-check")
 16936  async def ai_price_check(listing_id: int, email: str, tier: Optional[str] = None,
 16937                           ts_user: str = Cookie(default=None)):
 16938      """AI3: Buyer pays 1T — honest, three-panel price intelligence.
 16939  
 16940      INTEGRITY MODEL (price-integrity fix):
 16941        The model writes the SENTENCE; the system produces the NUMBER.
 16942        - Collectibles with a resolved Scryfall id  -> VERIFIED feed price (USD->ZAR
 16943          live rate). The LLM only narrates the real figures it is handed.
 16944        - Everything else -> an explicitly-labelled QUALITATIVE GUIDE. The LLM may
 16945          give a rough range but it is flagged 'not a verified price', and we never
 16946          cheerlead ('move quickly' is not permitted anywhere).
 16947        - A first-class fraud guard fires when asking price is far below a VERIFIED
 16948          floor: the verdict becomes a warning, never a 'buy' nudge.
 16949      Returns {verdict, source, sa_context, sa_range, assessment, official_context,
 16950               official_range, local_vs_global, asking_price, verified, safety_flag,
 16951               tuppence_remaining, ...legacy}.
 16952      """
 16953      if not ai_provider.any_lane_configured():
 16954          raise HTTPException(status_code=503, detail="AI not configured")
 16955  
 16956      conn = database.get_db()
 16957      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 16958      if not listing:
 16959          conn.close()
 16960          raise HTTPException(status_code=404, detail="Listing not found")
 16961  
 16962      # DELIVER-THEN-CHARGE (Session 95): we do NOT deduct here. Tuppence is only
 16963      # charged at the end, and ONLY if we produced a verified service. A guess,
 16964      # a 'cannot verify', or any failure costs the buyer nothing.
 16965      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour; a
 16966      # tier-aware caller must request a tier actually offered for this listing.
 16967      if tier is None:
 16968          _charge = 1
 16969      else:
 16970          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "fair_price")}
 16971          if tier not in _offered_t:
 16972              conn.close()
 16973              raise HTTPException(status_code=400,
 16974                  detail=f"Tier {tier} is not available for this listing")
 16975          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 16976      _require_tuppence(email, _charge)   # pre-flight only — no deduction yet
 16977      email = _bind_charged_email(email, ts_user, "ai3-price")   # ACCOUNT-BIND-1
 16978      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 16979      category    = listing["category"] or "General"
 16980      city        = listing["city"] or "South Africa"
 16981      title       = listing["title"] or "(no title)"
 16982      desc        = listing["description"] or "(no description)"
 16983      price       = listing["price"] or "(no price)"
 16984      scryfall_id = listing["scryfall_id"] if "scryfall_id" in listing.keys() else None
 16985      conn.close()  # done reading; charging happens on its own connection at the end
 16986  
 16987      # Parse the buyer-facing asking price into a number for ratio checks.
 16988      asking_zar = None
 16989      try:
 16990          asking_zar = float(str(price).replace("R", "").replace(",", "").strip())
 16991      except Exception:
 16992          asking_zar = None
 16993  
 16994      # ── Step 1+2: try to resolve a REAL verified price (collectibles) ──────────
 16995      verified_block = None        # text handed to the model as ground truth
 16996      official_range = "N/A"
 16997      official_ctx   = ""
 16998      floor_zar      = None
 16999      verified       = False
 17000      source         = "ai_estimate"
 17001  
 17002      # Late-resolve a scryfall id if the listing predates this column.
 17003      if not scryfall_id:
 17004          try:
 17005              scryfall_id = await resolve_scryfall_id(title, category)
 17006              if scryfall_id:
 17007                  c2 = database.get_db()
 17008                  c2.execute("UPDATE listings SET scryfall_id = ? WHERE id = ?",
 17009                             (scryfall_id, listing_id))
 17010                  c2.commit(); c2.close()
 17011          except Exception:
 17012              scryfall_id = None
 17013  
 17014      if scryfall_id:
 17015          feed = await scryfall_price_by_id(scryfall_id)
 17016          if feed and feed.get("usd"):
 17017              rate = await live_usd_zar()
 17018              usd  = feed["usd"]
 17019              floor_zar = usd * rate
 17020              verified = True
 17021              source   = "scryfall"
 17022              reserved = " (Reserved List — cannot be reprinted)" if feed.get("reserved") else ""
 17023              official_range = f"R{floor_zar:,.0f}  (USD ${usd:,.2f} \u00d7 R{rate:.2f}/USD)"
 17024              official_ctx   = (f"Verified market price for {feed.get('name')} "
 17025                                f"[{feed.get('set_name')}]{reserved}: "
 17026                                f"USD ${usd:,.2f} on TCGPlayer (via Scryfall), "
 17027                                f"\u2248 R{floor_zar:,.0f} at today's rate.")
 17028              verified_block = (
 17029                  f"VERIFIED MARKET DATA (use these EXACT figures, do not alter them):\n"
 17030                  f"- Card: {feed.get('name')} [{feed.get('set_name')}]{reserved}\n"
 17031                  f"- Verified market price: USD ${usd:,.2f} = R{floor_zar:,.0f} "
 17032                  f"(live rate R{rate:.2f}/USD)\n"
 17033                  f"- Buyer's asking price: {price}\n"
 17034              )
 17035  
 17036      # ── Step 3: narrate. Two prompt modes: verified vs qualitative-guide ───────
 17037      # -- STEP 3: no card feed -> try the FREE/owned resolver for the chosen tier
 17038      if (not verified_block) and (tier is not None):
 17039          _fpx = await _fair_price_resolve(
 17040              listing, listing_id, tier, _tierkey_for(listing, "fair_price"),
 17041              _listing_country_iso2(listing), category, city, asking_zar)
 17042          if _fpx and _fpx[0] == "verified":
 17043              _e = _fpx[1]
 17044              verified = True
 17045              source = _e["source"]
 17046              floor_zar = _e.get("floor_zar")
 17047              official_range = _e["official_range"]
 17048              official_ctx = _e["official_ctx"]
 17049              verified_block = _e["block"]
 17050          elif _fpx and _fpx[0] == "area_guide":
 17051              _e = _fpx[1]
 17052              _log.info("ai-price-check: listing #%d buyer=%s AREA-GUIDE %s (0T free)",
 17053                        listing_id, email, _e["source"])
 17054              return {
 17055                  "verdict": "area_guide", "source": _e["source"],
 17056                  "verified": False, "charged": False,
 17057                  "sa_context": "", "sa_range": _e.get("range_text", "N/A"),
 17058                  "assessment": _e["assessment"],
 17059                  "official_context": _e.get("provenance", ""),
 17060                  "official_range": _e.get("range_text", "N/A"),
 17061                  "local_vs_global": "cannot_compare", "asking_price": price,
 17062                  "safety_flag": None, "tuppence_remaining": _current_tuppence(email),
 17063                  "indicative_label": _INDICATIVE_LABEL,
 17064                  "provenance_date": _e.get("date", ""),
 17065                  "context": _e["assessment"], "suggested_range": _e.get("range_text", "N/A"),
 17066              }
 17067      if verified_block:
 17068          system_prompt = (
 17069              "You are a pricing analyst for TrustSquare, a South African marketplace. "
 17070              "You are given VERIFIED market figures. You must NEVER invent, round, or "
 17071              "contradict them — only explain them in plain language. Never tell a buyer "
 17072              "to 'move quickly' or 'buy now'. Be honest and protective. "
 17073              "Always respond with a single valid JSON object — no markdown."
 17074          )
 17075          user_prompt = (
 17076              f"A buyer is considering this {category} listing in {city}, South Africa.\n\n"
 17077              f"TITLE: {title}\nDESCRIPTION: {desc[:400]}\n\n"
 17078              f"{verified_block}\n"
 17079              "Write a short, honest assessment comparing the asking price to the verified "
 17080              "market price. Do not output any price number other than those given above.\n"
 17081              "Return JSON with these keys (strings, 50 words max each):\n"
 17082              "{\n"
 17083              '  "verdict": "fair" | "above_market" | "below_market" | "cannot_assess",\n'
 17084              '  "sa_context": "<note on the SA second-hand reality for this item, qualitative>",\n'
 17085              '  "assessment": "<plain-language read on the asking price vs the verified figure>",\n'
 17086              '  "local_vs_global": "cheaper_locally" | "cheaper_globally" | "similar" | "cannot_compare"\n'
 17087              "}"
 17088          )
 17089      else:
 17090          # No verified price feed for this category. Per the integrity rule, we do
 17091          # NOT sell a guess. Return an honest 'cannot verify' and charge nothing.
 17092          _log.info("ai-price-check: listing #%d buyer=%s NO-FEED -> free cannot_verify",
 17093                    listing_id, email)
 17094          bal = _current_tuppence(email)
 17095          return {
 17096              "verdict":          "cannot_verify",
 17097              "source":           "no_feed",
 17098              "verified":         False,
 17099              "charged":          False,
 17100              "sa_context":       "",
 17101              "sa_range":         "N/A",
 17102              "assessment":       ("We don\u2019t yet have a verified price source for this "
 17103                                   "category, so we won\u2019t guess. No Tuppence was charged. "
 17104                                   "Compare the asking price against similar local listings "
 17105                                   "before deciding."),
 17106              "official_context": "",
 17107              "official_range":   "N/A",
 17108              "local_vs_global":  "cannot_compare",
 17109              "asking_price":     price,
 17110              "safety_flag":      None,
 17111              "tuppence_remaining": bal,
 17112              "context":          "",
 17113              "suggested_range":  "N/A",
```

## AI4 Yield (deliver-then-charge reference) — from bea_main.py

```
 17248  
 17249  @app.post("/listings/{listing_id}/yield-calc")
 17250  async def ai_yield_calc(listing_id: int, email: str,
 17251                          ts_user: str = Cookie(default=None),
 17252                          rent: float | None = None,
 17253                          purchase_price: float | None = None,
 17254                          tier: Optional[str] = None):
 17255      """AI4: Property yield — HONEST & deliver-then-charge (Session 95).
 17256  
 17257      A real gross yield needs BOTH a purchase price and an annual rent. A listing
 17258      only carries one number (sale price OR monthly rent), so we:
 17259        - take the listing's own figure for its side, and
 17260        - accept the OTHER figure from the caller (?rent= or ?purchase_price=).
 17261      If the second figure is missing we return needs_input and charge NOTHING.
 17262      The yield is computed in PYTHON (not guessed by the model). The LLM only
 17263      writes the benchmark sentence. 1T is charged ONLY when a real yield is
 17264      produced from real inputs.
 17265      """
 17266      if not ai_provider.any_lane_configured():
 17267          raise HTTPException(status_code=503, detail="AI not configured")
 17268  
 17269      conn = database.get_db()
 17270      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
 17271      if not listing:
 17272          conn.close()
 17273          raise HTTPException(status_code=404, detail="Listing not found")
 17274  
 17275      category = listing["category"] or ""
 17276      if "property" not in category.lower() and category.lower() not in ("property", "estate agents", "accommodation"):
 17277          conn.close()
 17278          raise HTTPException(status_code=400, detail="Yield calculator is only available for Property listings")
 17279  
 17280      city          = listing["city"] or "South Africa"
 17281      suburb        = listing["suburb"] or ""
 17282      title         = listing["title"] or "(no title)"
 17283      desc          = listing["description"] or ""
 17284      price_raw     = listing["price"] or ""
 17285      listing_type  = (listing["listing_type"] if "listing_type" in listing.keys() else None) or ""
 17286      conn.close()
 17287  
 17288      # Pre-flight: can the buyer pay at all? (No deduction yet.)
 17289      # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour.
 17290      if tier is None:
 17291          _charge = 1
 17292      else:
 17293          _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "yield")}
 17294          if tier not in _offered_t:
 17295              raise HTTPException(status_code=400,
 17296                  detail=f"Tier {tier} is not available for this listing")
 17297          _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
 17298      _require_tuppence(email, _charge)
 17299      email = _bind_charged_email(email, ts_user, "ai4-yield")   # ACCOUNT-BIND-1
 17300      _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
 17301  
 17302      def _num(v):
 17303          try:
 17304              return float(str(v).replace("R", "").replace(",", "")
 17305                           .replace("/month", "").replace("pm", "").strip())
 17306          except Exception:
 17307              return None
 17308  
 17309      listing_amount = _num(price_raw)
 17310      lt = listing_type.lower()
 17311      is_rental = ("rent" in lt) or ("rent" in (title + " " + desc).lower() and "for sale" not in lt)
 17312  
 17313      # Resolve purchase_price (annual rent / monthly rent) from listing + caller input.
 17314      monthly_rent = None
 17315      buy_price    = None
 17316      need = None
 17317      if is_rental:
 17318          # Listing price IS the monthly rent. Need the purchase price from caller.
 17319          monthly_rent = listing_amount
 17320          buy_price    = purchase_price
 17321          if not buy_price:
 17322              need = "purchase_price"
 17323      else:
 17324          # Listing price IS the sale/purchase price. Need expected monthly rent.
 17325          buy_price    = listing_amount
 17326          monthly_rent = rent
 17327          if not monthly_rent:
 17328              need = "rent"
 17329  
 17330      # Honest 'needs input' — FREE, no Tuppence charged.
 17331      # -- STEP 3: source the missing half from a FREE/owned feed (per tier+country)
 17332      _country_y = _listing_country_iso2(listing)
 17333      _rent_src = "your figure"
 17334      _price_src = "the listing"
 17335      if need and tier is not None:
 17336          _filled = await _yield_fill_missing(need, tier, _country_y, city, suburb, listing, listing_id)
 17337          if _filled:
 17338              if need == "rent":
 17339                  monthly_rent = _filled["value"]; _rent_src = _filled["provenance"]
 17340              else:
 17341                  buy_price = _filled["value"]; _price_src = _filled["provenance"]
 17342              need = None
 17343  
 17344      if need or not buy_price or not monthly_rent or buy_price <= 0 or monthly_rent <= 0:
 17345          bal = _current_tuppence(email)
 17346          prompt_for = ("the expected monthly rent" if need == "rent"
 17347                        else "the likely purchase price" if need == "purchase_price"
 17348                        else "both the purchase price and the monthly rent")
 17349          return {
 17350              "status":           "needs_input",
 17351              "charged":          False,
 17352              "need":             need or "both",
 17353              "listing_amount":   listing_amount,
 17354              "is_rental":        is_rental,
 17355              "message":          (f"To calculate a real yield we need {prompt_for}. "
 17356                                   f"Enter it and we\u2019ll compute the actual figure — "
 17357                                   f"no Tuppence is charged until we do."),
 17358              "tuppence_remaining": bal,
 17359          }
 17360  
 17361      # ── REAL computation in Python (deterministic, auditable) ──────────────────
 17362      annual_rent = monthly_rent * 12.0
 17363      gross = (annual_rent / buy_price) * 100.0
 17364  
 17365      # Net estimate: subtract a transparent cost band (rates, levies, maintenance,
 17366      # vacancy). We show the assumption rather than hiding it inside a model guess.
 17367      # STEP 3: versioned, dated per-region net-cost band replaces the flat 3%.
 17368      _band = tier_resolvers.net_cost_band(_country_y)
 17369      NET_COST_PCT = float(_band.get("typical", 3.0))
 17370      net = gross - NET_COST_PCT
 17371  
 17372      # LLM writes ONLY the qualitative benchmark sentence — handed the real numbers.
 17373      location_str = f"{suburb}, {city}" if suburb else city
 17374      _BENCHMARKS = {
 17375          "ZA": ("SA GROSS YIELD BENCHMARKS (2026): Pretoria residential 7-10%, "
 17376                 "Cape Town 5-7%, Johannesburg 6-9%, Durban 7-10%, secondary cities 8-12%, "
 17377                 "commercial 9-12%, student accommodation 10-14%."),
```

## AI5 Batch Cards (full endpoint) — from bea_main.py

```
 17483  
 17484  @app.post("/listings/batch-cards")
 17485  async def ai_batch_card_listings(req: BatchCardRequest, ts_user: str = Cookie(default=None)):
 17486      """AI5: Seller pays 2T — Claude Sonnet Vision analyses up to 10 card photos and
 17487      returns an array of draft listing JSONs ready for review and publish.
 17488      Each draft contains title, description, price_suggestion, condition, category.
 17489      Capped at 10 images per call. 2T flat cost regardless of card count.
 17490      Returns {drafts: [...], cards_processed, tuppence_remaining}.
 17491      """
 17492      if not ai_provider.any_lane_configured():
 17493          raise HTTPException(status_code=503, detail="AI not configured")
 17494  
 17495      if not req.images:
 17496          raise HTTPException(status_code=400, detail="At least one image is required")
 17497      _bind_charged_email(req.seller_email, ts_user, "ai5-batch-cards")   # ACCOUNT-BIND-1
 17498      _check_cost_ceiling(req.seller_email)   # P2 — hard daily rail, BEFORE the Tuppence charge
 17499  
 17500      # Cap at 10 cards
 17501      images = req.images[:10]
 17502      card_count = len(images)
 17503  
 17504      _require_tuppence(req.seller_email, 2)   # F2 fix (5 Aug 2026): pre-flight only — charge on delivery
 17505      _bc_charge_desc = f"AI Batch Cards · {card_count} card(s) · {req.city}"
 17506  
 17507      suburb_str = req.suburb or req.city
 17508      location_str = f"{suburb_str}, {req.city}"
 17509  
 17510      system_prompt = (
 17511          "You are an expert trading card and collectables appraiser and marketplace copywriter "
 17512          "for TrustSquare, a South African peer-to-peer local marketplace. "
 17513          "You identify cards/collectables from photos, assess condition, and write concise buyer-friendly listings. "
 17514          "You know SA collectables market values. "
 17515          "Always respond with a single valid JSON object — no markdown, no explanation."
 17516      )
 17517  
 17518      # Build the message content: one text block + one image block per card
 17519      content_blocks = [
 17520          {
 17521              "type": "text",
 17522              "text": (
 17523                  f"Analyse these {card_count} trading card / collectable image(s) for a seller in {location_str}, "
 17524                  "South Africa. For each image, generate a complete listing draft.\n\n"
 17525                  "For each card/item return:\n"
 17526                  '{"title": "<specific card/item name, set, year if visible, max 12 words>", '
 17527                  '"description": "<40-80 words: card details, set/series, condition notes, notable features>", '
 17528                  '"price_suggestion": "<e.g. R150 or R200–R350 depending on condition>", '
 17529                  '"condition": "mint" | "near_mint" | "excellent" | "good" | "fair" | "poor", '
 17530                  '"category": "Collectors"}\n\n'
 17531                  f'Return JSON: {{"drafts": [<one object per image in order>]}}'
 17532              )
 17533          }
 17534      ]
 17535  
 17536      for _, img_b64 in enumerate(images):
 17537          # Detect media type from base64 header or default to jpeg
 17538          media_type = "image/jpeg"
 17539          if img_b64.startswith("data:"):
 17540              header, data = img_b64.split(",", 1)
 17541              if "png" in header:
 17542                  media_type = "image/png"
 17543              elif "gif" in header:
 17544                  media_type = "image/gif"
 17545              elif "webp" in header:
 17546                  media_type = "image/webp"
 17547              img_b64 = data
 17548  
 17549          content_blocks.append({
 17550              "type": "image",
 17551              "source": {
 17552                  "type": "base64",
 17553                  "media_type": media_type,
 17554                  "data": img_b64,
 17555              }
 17556          })
 17557  
 17558      try:
 17559          # SEAM-ROUTED (P0): task="vision" — resolves to the haiku id today (Haiku-first,
 17560          # 3 Jul 2026); flipping TASK_MODEL's vision row back to sonnet re-arms the documented revert.
 17561          _sr = await asyncio.to_thread(
 17562              ai_provider.complete, [{"role": "user", "content": content_blocks}],
 17563              task="vision", max_tokens=2000, system=system_prompt,
 17564              provider=_ts_active_provider(), timeout=60)
 17565          _bc_in, _bc_out = _sr.in_tokens, _sr.out_tokens
 17566          # P2 — Tuppence covers the revenue side; log token spend so the cost
 17567          # dashboard sees it too (sweep 12 Jun 2026)
 17568          _log_ai_spend(req.seller_email, "/listings/batch-cards", "sonnet_vision", _bc_in, _bc_out,
 17569                        provider=_sr.provider, model=_sr.model)
 17570          raw = _sr.text.strip()
 17571          raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
 17572          raw = _re_match.sub(r"\s*```$", "", raw)
 17573          result = json.loads(raw)
 17574          drafts = result.get("drafts", [])
 17575  
 17576          # Sanitise each draft
 17577          clean_drafts = []
 17578          valid_conditions = {"mint", "near_mint", "excellent", "good", "fair", "poor"}
 17579          for d in drafts[:card_count]:
 17580              if isinstance(d, dict):
 17581                  clean_drafts.append({
 17582                      "title":            str(d.get("title", ""))[:120],
 17583                      "description":      str(d.get("description", ""))[:800],
 17584                      "price_suggestion": str(d.get("price_suggestion", ""))[:60],
 17585                      "condition":        d.get("condition", "good") if d.get("condition") in valid_conditions else "good",
 17586                      "category":         "Collectors",
 17587                      "city":             req.city,
 17588                      "suburb":           req.suburb or "",
 17589                  })
 17590  
 17591      except Exception as exc:
 17592          _log.error("ai-batch-cards: %s", exc)
 17593          raise HTTPException(status_code=500, detail="AI batch card listing failed — no Tuppence was charged") from exc
 17594  
 17595      _conn2 = database.get_db()
 17596      try:
 17597          remaining = _deduct_tuppence(_conn2, req.seller_email, 2, _bc_charge_desc)   # F2: charge on delivery
 17598          _conn2.commit()
 17599      finally:
 17600          _conn2.close()
 17601      _log.info("ai-batch-cards: seller=%s city=%s cards=%d drafts=%d",
 17602                req.seller_email, req.city, card_count, len(clean_drafts))
 17603      return {
 17604          "drafts":           clean_drafts,
 17605          "cards_processed":  card_count,
 17606          "tuppence_remaining": remaining,
 17607      }
 17608  
 17609  
 17610  
 17611  @app.get("/tuppence/history")
 17612  def get_tuppence_history(email: str, limit: int = 50, offset: int = 0, _key: str = Depends(auth.require_api_key)):
 17613      """Return paginated tuppence transaction history with running balance."""
 17614      conn = database.get_db()
 17615      try:
 17616          # Verify user exists
 17617          user = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
 17618          if not user:
 17619              raise HTTPException(status_code=404, detail="User not found")
 17620  
 17621          total = conn.execute(
 17622              "SELECT COUNT(*) FROM transactions WHERE user_email=?", (email,)
 17623          ).fetchone()[0]
 17624  
 17625          # Get all rows ascending to compute running balances
 17626          all_rows = conn.execute(
 17627              "SELECT id, type, amount, description, created_at "
 17628              "FROM transactions WHERE user_email=? ORDER BY id ASC",
 17629              (email,)
 17630          ).fetchall()
 17631  
 17632          # Compute running balance_after for each row (cumulative sum)
```

## KYC identity verification (vision, cost-guarded) — from bea_main.py

```
 11110  
 11111  
 11112  async def _sonnet_verify_identity(doc_url: str, claimed_name: str,
 11113                                     claimed_id: str, doc_type: str, email: str = "") -> dict:
 11114      """Call Sonnet vision to verify identity document.
 11115      SWAP POINT: replace this function with PaddleOCR/PassportEye for zero-token operation.
 11116      Self-contained cost guard (P2, 22 Jul 2026): checks the daily ceiling BEFORE the call
 11117      (raises HTTPException 429, same as every other paid endpoint) and logs spend itself
 11118      so this helper stays metered even if a future caller forgets to.
 11119      Returns: {verified(bool), confidence(float), extracted_name(str),
 11120                extracted_id(str), notes(str), model(str)}"""
 11121      if not ai_provider.any_lane_configured():
 11122          return {"verified": False, "confidence": 0.0, "extracted_name": "",
 11123                  "extracted_id": "", "notes": "AI verification unavailable — API key not set",
 11124                  "model": "none"}
 11125      _check_cost_ceiling(email)   # C1 — refuse if daily cost ceiling reached
 11126      try:
 11127          # Fetch the document image (KYC-SSRF-1: allowlisted host, no redirects, size-capped)
 11128          img_bytes = _fetch_kyc_document(doc_url)
 11129          img_b64 = base64.standard_b64encode(img_bytes).decode()
 11130          # Detect media type
 11131          media_type = "image/jpeg"
 11132          if doc_url.lower().endswith(".png"):
 11133              media_type = "image/png"
 11134          elif doc_url.lower().endswith(".webp"):
 11135              media_type = "image/webp"
 11136  
 11137          # SEAM-ROUTED (P0, 17 Jul 2026): KYC vision call goes through ai_provider.complete()
 11138          # with task="sonnet" — same claude-sonnet-4-6 on the Anthropic path as the old SDK call.
 11139          prompt = f"""You are a document verification assistant for TrustSquare marketplace.
 11140  Examine this identity document image carefully.
 11141  
 11142  The seller claims:
 11143  - Full name: {claimed_name}
 11144  - ID/passport number: {claimed_id}
 11145  - Document type: {doc_type}
 11146  
 11147  Your task:
 11148  1. Extract the FULL NAME exactly as printed on the document
 11149  2. Extract the ID NUMBER / PASSPORT NUMBER exactly as printed
 11150  3. Determine if the claimed name matches the document name (allow for initials, middle names)
 11151  4. Determine if the claimed number matches the document number
 11152  
 11153  Respond ONLY with valid JSON in this exact format:
 11154  {{
 11155    "extracted_name": "<full name from document>",
 11156    "extracted_id": "<id/passport number from document>",
 11157    "name_match": <true/false>,
 11158    "id_match": <true/false>,
 11159    "confidence": <0.0-1.0>,
 11160    "document_appears_genuine": <true/false>,
 11161    "notes": "<any concerns or observations, empty string if none>"
 11162  }}
 11163  
 11164  If you cannot read the document clearly, set confidence below 0.5 and explain in notes."""
 11165  
 11166          _sr = ai_provider.complete(
 11167              [{
 11168                  "role": "user",
 11169                  "content": [
 11170                      {"type": "image", "source": {
 11171                          "type": "base64", "media_type": media_type, "data": img_b64
 11172                      }},
 11173                      {"type": "text", "text": prompt}
 11174                  ]
 11175              }],
 11176              task="sonnet", max_tokens=300,
 11177              provider=_ts_active_provider(), allow_fallback=False, timeout=120)   # KYC-PIN-1 (F3): ID docs never fan out to standby vendors
 11178          raw = _sr.text.strip()
 11179          # Parse JSON from response
 11180          json_match = re.search(r'\{[\s\S]*\}', raw)
 11181          if not json_match:
 11182              raise ValueError("No JSON in Sonnet response")
 11183          result = json.loads(json_match.group())
 11184          verified = (result.get("name_match") and result.get("id_match") and
 11185                      result.get("confidence", 0) >= 0.75 and
 11186                      result.get("document_appears_genuine", True))
 11187          _log_ai_spend(email, "/users/verify-identity", "sonnet_vision",
 11188                        getattr(_sr, "in_tokens", None), getattr(_sr, "out_tokens", None),
 11189                        provider=getattr(_sr, "provider", None), model=getattr(_sr, "model", None))
 11190          return {
 11191              "verified": bool(verified),
 11192              "confidence": float(result.get("confidence", 0)),
 11193              "extracted_name": result.get("extracted_name", ""),
 11194              "extracted_id": result.get("extracted_id", ""),
 11195              "notes": result.get("notes", ""),
 11196              "model": SONNET_MODEL,
 11197          }
 11198      except HTTPException:
 11199          raise
```

## /admin/ai-restore + /flags provider block — from bea_main.py

```
 14930      return {"services": out, "checked_at": datetime.utcnow().isoformat() + "Z"}
 14931  
 14932  @app.post("/admin/ai-restore")
 14933  def admin_ai_restore(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 14934      """P2a: MANUAL restore — the ONLY path back to traffic for a banned (T3) lane
 14935      (David's ruling 31 Jul: dropouts auto-recover, bans wait for the operator)."""
 14936      _p = ((payload or {}).get("provider") or "").strip()
 14937      _t = ((payload or {}).get("task") or "").strip() or None
 14938      if _p not in ai_provider.ADAPTERS:
 14939          raise HTTPException(status_code=400, detail="unknown provider")
 14940      try:
 14941          import ai_breaker as _brk
 14942          n = _brk.restore(_p, _t, who="dashboard-admin")
 14943          _log.warning("AI-BREAKER manual restore: %s/%s (%d rows)", _p, _t or "ALL", n)
 14944          return {"restored": n, "provider": _p, "task": _t or "ALL"}
 14945      except Exception as e:
 14946          raise HTTPException(status_code=500, detail="restore failed: " + str(e)[:120]) from e
 14947  
 14948  @app.post("/admin/ai-test")   # AITEST-ROUTE-1 (17 Jul, found live by David's demo): decorator was pasted onto demand_sweep; real tester was never registered
 14949  def admin_ai_test(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
 14950      """David-only: run a tiny prompt through the ACTIVE provider via the ai_provider seam
 14951      (full translate+call+parse path). Lets the Page-4 switch be tested live against either
 14952      provider without touching the 15 production call sites. Returns the text + which provider/model answered."""
 14953      _req_prov=((payload or {}).get("provider") or "").strip()   # P1: optional explicit provider
 14954      if _req_prov and _req_prov not in ai_provider.ADAPTERS:
 14955          raise HTTPException(status_code=400, detail="unknown provider: "+_req_prov[:40])
 14956      try:
 14957          import ai_provider as _ap
 14958          prov=_req_prov or _ts_active_provider()
 14959          prompt=((payload or {}).get("prompt") or "Reply with exactly: TrustSquare AI provider test OK.").strip()
 14960          r=_ap.complete([{"role":"user","content":prompt}], task="haiku", max_tokens=40, provider=prov)
 14961          return {"ok": bool(r.ok), "provider": r.provider, "model": r.model,
 14962                  "text": (r.text or "")[:400], "in_tokens": r.in_tokens, "out_tokens": r.out_tokens}
 14963      except Exception as e:
 14964          raise HTTPException(status_code=500, detail="ai-test failed: "+str(e)[:160]) from e
 14965  
 14966  
 14967  class _FlagsUpdate(BaseModel):
 14968      mode:          Optional[str]  = None
 14969      verified_tier: Optional[bool] = None
 14970      videos:        Optional[bool] = None
 14971      data_ops:      Optional[bool] = None
 14972      data_places:   Optional[bool] = None
 14973      data_flights:  Optional[bool] = None
 14974      data_mapbox:   Optional[bool] = None
 14975      p_heritage:    Optional[bool] = None
 14976      p_expedition:  Optional[bool] = None
 14977      p_weekend:     Optional[bool] = None
 14978      # BIT safe-state flags (Mitigator-writable; see §13.1)
 14979      ai_example_enabled:    Optional[bool] = None
 14980      auth_fail_closed:      Optional[bool] = None
 14981      tuppence_burn_enabled: Optional[bool] = None
 14982      ai_active:             Optional[str]  = None  # AI provider seam: 'anthropic' | 'openai' | 'scaleway' (Page-4 switch)
 14983      ai_active_override:    Optional[str]  = None  # MANUAL PIN: provider = pin (TTL decay) | '' = unpin (1 Aug 2026)
 14984      reason:                Optional[str]  = None  # free-text WHY for the audit row (D4, 15 Aug 2026) - never a launch_switches column
 14985      fault_report:          Optional[bool] = None  # MAINT-B1b: in-app tester fault intake visible
 14986      intro_relay:           Optional[bool] = None  # INTRO-RELAY-1: masked-alias introductions (dark until CF rail is live)
 14987      account_binding:       Optional[bool] = None  # ACCOUNT-BIND-1: charges bound to the proven session
 14988      photo_replace_request: Optional[bool] = None  # PHOTO-REPLACE-1: ask for a new photo rather than blur it into ruin (TS-0022)
 14989  
 14990  def _flags_payload(d):
 14991      def b(k): return bool(d.get(k, 0))
 14992      live = (d.get("mode", "launch") == "live")
 14993      return {
 14994          "mode": d.get("mode", "launch"),
 14995          "verified_tier": b("verified_tier"), "videos": b("videos"),
 14996          "fault_report": b("fault_report"),
 14997          "intro_relay": b("intro_relay"),
 14998          "account_binding": b("account_binding"),
 14999          # PHOTO-REPLACE-1 defaults ON (David's 7 Aug ruling), so a row predating the
 15000          # column must read as ON - b() would read a missing key as OFF and silently
 15001          # restore the very behaviour Maroushka reported three times.
 15002          "photo_replace_request": bool(d.get("photo_replace_request", 1)),
 15003          "photo_max_blur_pct": round(_ANON_MAX_BLUR_FRAC * 100),
 15004          "relay_configured": bool(RELAY_INBOUND_SECRET),
 15005          "data": {"ops": b("data_ops"), "places": b("data_places"),
 15006                   "flights": b("data_flights"), "mapbox": b("data_mapbox")},
 15007          "planners": {"heritage": b("p_heritage"), "expedition": b("p_expedition"),
 15008                       "weekend": b("p_weekend")},
 15009          "effective": {
 15010              "verified_visible":    live and b("verified_tier"),
 15011              "videos_visible":      b("videos"),  # decoupled from live mode (David 29 Jun): dashboard videos toggle controls it on its own; verified/paid-feed gates stay live-gated
 15012              "heritage_verified":   live and b("verified_tier") and b("p_heritage"),
 15013              "expedition_verified": live and b("verified_tier") and b("p_expedition"),
 15014              "weekend_verified":    live and b("verified_tier") and b("p_weekend"),
 15015          },
 15016          "bit_flags": {
 15017              "ai_example_enabled":    bool(d.get("ai_example_enabled", 1)),
 15018              "auth_fail_closed":      bool(d.get("auth_fail_closed", 0)),
 15019              "tuppence_burn_enabled": bool(d.get("tuppence_burn_enabled", 1)),
 15020          },
 15021          "ai_provider": {
 15022              # effective = the lane calls actually use RIGHT NOW (pin-aware); standing = the
 15023              # auto/default lane the system returns to when the pin decays.
 15024              "active": _ts_active_provider(),   # pin-aware effective lane
 15025              "standing": d.get("ai_active", "anthropic"),
 15026              "override": ({"provider": _TS_AI_CACHE["override"], "expires_at": _TS_AI_CACHE["expires"]}
 15027                            if _TS_AI_CACHE.get("override") else None),
 15028              "override_ttl_hours": AI_OVERRIDE_TTL_HOURS,
 15029              "funnel": _ts_funnel_snapshot(),
 15030              # FAIL-OPEN here too (FLAGS-BRK-1, 1 Aug): a missing/broken breaker module must
 15031              # never take /flags down — the card degrades, the platform does not.
 15032              "breaker": _ts_breaker_safe("snapshot"),
 15033              "drill": _ts_breaker_safe("drill"),
 15034              # which providers have a REAL adapter wired (vs stub) — Page 4 greys out the stubs
 15035              "available": {"anthropic": bool(ANTHROPIC_API_KEY), "openai": bool(ai_provider.envkey("OPENAI_API_KEY")),
 15036                            "scaleway": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY"))},
 15037              # P1: ordered provider cards for the NEW dashboard UI (old card keeps reading active/available above)
 15038              "providers": [
 15039                  {"id": "anthropic", "label": "Anthropic (Claude)", "family": "us", "jurisdiction": "US",
 15040                   "available": bool(ANTHROPIC_API_KEY),
 15041                   "models": ai_provider.TASK_MODEL.get("anthropic", {})},
 15042                  {"id": "scaleway", "label": "Scaleway EU", "family": "open", "jurisdiction": "EU · Paris",
 15043                   "available": bool(ai_provider.envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")),
 15044                   "models": ai_provider.TASK_MODEL.get("scaleway", {})},
 15045                  {"id": "openai", "label": "OpenAI (GPT-5.6)", "family": "us", "jurisdiction": "US",
 15046                   "available": bool(ai_provider.envkey("OPENAI_API_KEY")),
 15047                   "models": ai_provider.TASK_MODEL.get("openai", {})},
 15048              ],
 15049          },
 15050          "updated_at": d.get("updated_at", ""),
 15051      }
 15052  
 15053  def _ts_breaker_safe(what):
 15054      try:
 15055          import ai_breaker as _b
 15056          if what == "snapshot": return _b.snapshot()
 15057          return sorted(_b.drill_banned()) or None
 15058      except Exception:
 15059          return None
 15060  
 15061  _TS_FUNNEL_CACHE = {"mtime": None, "data": None}
 15062  def _ts_funnel_snapshot():
 15063      """The +1 card's funnel strip: ORDER AND GATE-TYPES ONLY (David 1 Aug 2026 — no numbers).
 15064      Read from ai_funnel_snapshot.json, generated by scripts/price_truth.py --snapshot (ONE
 15065      ranking engine); absent file -> None, dashboard shows nothing. Cached on mtime."""
 15066      import os as _os
 15067      p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ai_funnel_snapshot.json")
 15068      try:
 15069          mt = _os.path.getmtime(p)
 15070          if _TS_FUNNEL_CACHE["mtime"] != mt:
 15071              with open(p, encoding="utf-8") as fh:
 15072                  _TS_FUNNEL_CACHE.update(mtime=mt, data=json.load(fh))
 15073          return _TS_FUNNEL_CACHE["data"]
 15074      except Exception:
 15075          return None
 15076  
 15077  @app.get("/flags")
 15078  def get_flags():
 15079      """Public — buyer app + dashboard read launch-switch state. Safe default = launch/free-only."""
```

## /admin/ai-spend summary endpoint — from bea_main.py

```
  6166  # ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
  6167  
  6168  @app.get("/admin/ai-spend/summary")
  6169  def admin_ai_spend_daily_summary(_admin=Depends(_require_admin_or_key)):
  6170      """Live AI-spend summary for the nightly cost-compliance sweep (P2, 11 Jun 2026).
  6171      Returns today's and 7-day spend, the configured ceilings, and a 7-day
  6172      per-endpoint/model breakdown. Read-only; $0; admin key required."""
  6173      conn = database.get_db()
  6174      try:
  6175          today = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
  6176          week = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
  6177          t = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  6178                           "FROM ai_spend_log WHERE logged_at >= ?", (today,)).fetchone()
  6179          w = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
  6180                           "FROM ai_spend_log WHERE logged_at >= ?", (week,)).fetchone()
  6181          cfg = conn.execute("SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
  6182                             "FROM ai_spend_config WHERE id = 1").fetchone()
  6183          by_ep = conn.execute(
  6184              "SELECT endpoint, model, COALESCE(SUM(est_cost_usd),0) AS usd, COUNT(*) AS calls, "
  6185              "SUM(cost_is_real) AS real_rows FROM ai_spend_log WHERE logged_at >= ? "
  6186              "GROUP BY endpoint, model ORDER BY usd DESC LIMIT 25", (week,)).fetchall()
  6187      finally:
  6188          conn.close()
  6189      return {
  6190          "today_usd": round(t["u"], 4), "today_calls": t["n"],
  6191          "week_usd": round(w["u"], 4), "week_calls": w["n"],
  6192          "daily_user_ceiling_usd": (cfg["daily_user_ceiling_usd"] if cfg else 0) or 0,
  6193          "daily_platform_ceiling_usd": (cfg["daily_platform_ceiling_usd"] if cfg else 0) or 0,
  6194          "ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
  6195                              else "platform ceiling is 0/unset — AI spend is UNCAPPED"),
  6196          "by_endpoint": [{"endpoint": r["endpoint"], "model": r["model"],
  6197                           "usd": round(r["usd"], 4), "calls": r["calls"],
  6198                           "estimated_rows": r["calls"] - (r["real_rows"] or 0)} for r in by_ep],
  6199      }
  6200  
  6201  
  6202  @app.post("/admin/migrate-photos")
  6203  def migrate_photos(_admin=Depends(_require_admin_or_key)):
  6204      """Migrate existing local photos to Hetzner Object Storage.
  6205      Idempotent — skips listings already pointing to an S3 URL.
  6206      Does NOT delete local files.
  6207      Returns: { migrated, failed, skipped }
  6208      """
  6209      if not _S3_CONFIGURED:
  6210          raise HTTPException(status_code=503, detail="Object Storage not configured — set HETZNER_S3_* env vars")
  6211      conn = database.get_db()
  6212      rows = conn.execute(
  6213          "SELECT id, thumb_url, medium_url FROM listings WHERE thumb_url LIKE '/media/%'"
  6214      ).fetchall()
  6215      migrated = failed = skipped = 0
  6216      for row in rows:
  6217          listing_id  = row["id"]
  6218          thumb_path  = row["thumb_url"]  or ""
  6219          medium_path = row["medium_url"] or ""
  6220          if not thumb_path.startswith("/media/"):
```

## Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop — from bea_main.py

```
 19402  
 19403  
 19404  # ── SCOREBOARD-1 (3 Aug 2026): the silent scoreboard agent, nightly ──────────
 19405  # The SLOW-signal half of the failover programme (fast signals = ai_breaker):
 19406  # probes every configured lane x task tier each night at 03:33 SAST (01:33 UTC,
 19407  # after the 03:17 backup), stores history in ai_scoreboard_probes (primary DB,
 19408  # so it rides the backup lanes), writes the rolling 90-day ranking to
 19409  # ai_scoreboard.json. Quality is a GATE not a weight (golden-set registry).
 19410  # Spend-gated OFF by default — launch_switches.scoreboard_enabled=1
 19411  # (enable_scoreboard.bat) is David's explicit click. Import-guarded and
 19412  # exception-walled: a scoreboard failure can never hurt the app.
 19413  try:
 19414      import ai_scoreboard as _ts_scoreboard
 19415  except Exception as _ts_sb_err:
 19416      _ts_scoreboard = None
 19417      print("SCOREBOARD-1: module not importable (%s) — nightly probes off" % _ts_sb_err)
 19418  
 19419  if _ts_scoreboard is not None:
 19420      @app.on_event("startup")
 19421      async def _ts_scoreboard_nightly():
 19422          async def _sb_loop():
 19423              while True:
 19424                  _now = datetime.now(timezone.utc)
 19425                  _nxt = _now.replace(hour=1, minute=33, second=0, microsecond=0)
 19426                  if _nxt <= _now:
 19427                      _nxt += timedelta(days=1)
 19428                  await asyncio.sleep(max(60.0, (_nxt - _now).total_seconds()))
 19429                  try:
 19430                      await asyncio.get_running_loop().run_in_executor(
 19431                          None, _ts_scoreboard.run_nightly)
 19432                  except Exception as _sb_e:
 19433                      print("SCOREBOARD-1 nightly error: %s" % _sb_e)
 19434          asyncio.get_running_loop().create_task(_sb_loop())
 19435  
 19436  
 19437  # ── HEARTBEAT-1 (5 Aug 2026, David's F5 ruling: live NOW, confidence before launch) ──
 19438  # P2c idle-recovery heartbeat per AI_AUTO_FAILOVER_P2_DESIGN §6: every 60 s, if any
 19439  # breaker row is eligible (tripped/half_open, probe window open), claim and send ONE
 19440  # direct probe — one per tick TOTAL, round-robin, so a bad night can never multiply
 19441  # cost. Text ping only (~$0.00002); T3 rows carry hourly probe_after, so bans probe
 19442  # hourly. Spend is logged like all spend. Fail-open: any error waits for the next tick.
 19443  @app.on_event("startup")
 19444  async def _ts_breaker_heartbeat():
 19445      async def _hb_loop():
 19446          _rr = 0
 19447          while True:
 19448              await asyncio.sleep(60)
 19449              try:
 19450                  import ai_breaker as _hb_brk
 19451                  if getattr(_hb_brk, "_get_db", None) is None:
 19452                      continue   # breaker unattached — nothing to probe
 19453                  _hb_conn = database.get_db()
 19454                  try:
 19455                      _rows = _hb_conn.execute(
 19456                          "SELECT provider, task FROM ai_breaker "
 19457                          "WHERE state IN ('tripped','half_open') "
 19458                          "AND (probe_after IS NULL OR probe_after <= ?) "
 19459                          "ORDER BY provider, task",
 19460                          (datetime.utcnow().isoformat(timespec="seconds"),)).fetchall()
 19461                  finally:
 19462                      _hb_conn.close()
 19463                  if not _rows:
 19464                      continue
 19465                  _row = _rows[_rr % len(_rows)]; _rr += 1
 19466                  _p, _t = _row["provider"], _row["task"]
 19467                  if not _hb_brk.claim_probe(_p, _t):
 19468                      continue   # someone else holds the half-open lease
 19469                  # HEARTBEAT-CEILING-1 (20 Aug 2026, DW-021): the probe is tiny but it is
 19470                  # still spend, and this loop runs unattended forever. _check_cost_ceiling
 19471                  # raises 429 when the platform ceiling is reached; in a background loop
 19472                  # that means SKIP THIS TICK, not crash — the breaker probes again next
 19473                  # minute once the day rolls over or the ceiling is raised.
 19474                  try:
 19475                      _check_cost_ceiling("system:heartbeat")
 19476                  except Exception:
 19477                      continue   # over the daily ceiling — do not spend on a probe
 19478                  _r = await asyncio.to_thread(
 19479                      ai_provider.complete, [{"role": "user", "content": "ping"}],
 19480                      task=_t, max_tokens=8, provider=_p, probe=True, timeout=20)
 19481                  _log_ai_spend("system:heartbeat", "/breaker/heartbeat", _t,
 19482                                _r.in_tokens, _r.out_tokens,
 19483                                provider=_r.provider, model=_r.model)
 19484              except Exception as _hb_e:
 19485                  print("HEARTBEAT-1 error: %s" % _hb_e)
 19486      asyncio.get_running_loop().create_task(_hb_loop())
 19487  
 19488  
 19489  # ══════════════════════════════════════════════════════════════════════════════
 19490  # PLANNER LANE · Phase A (16 Aug 2026, David: "Build phase A")
 19491  # Design: PLANNER_LANE_DESIGN_2026-08-16_rev2.docx · flag-dark behind
 19492  # launch_switches.p_heritage (planners.heritage) — OFF answers 404 as if absent.
 19493  # FREE class: no Tuppence machinery is touched. The AI never writes coordinates:
 19494  # it picks wonder IDs + words at the everyday task tier through the seam
 19495  # (ai_provider.complete — no vendor names, the Model Register resolves the lane);
 19496  # journey_render.assemble_heritage_spec builds the spec from wonders.json rows.
 19497  # ══════════════════════════════════════════════════════════════════════════════
 19498  
 19499  def _planner_flag_on(name="p_heritage"):
 19500      conn = database.get_db()
 19501      try:
 19502          row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
 19503      finally:
 19504          conn.close()
 19505      return bool(dict(row).get(name, 0)) if row else False
 19506  
 19507  
 19508  class PlannerComposeReq(BaseModel):
 19509      email: str
 19510      country: str
 19511      days: int = 3
```

## AI Services help card copy (user-facing, F3 vendor-neutral fix) — from marketsquare.html

```
  1551            <div style="font-size:22px;flex-shrink:0;">&#10024;</div>
  1552            <div style="flex:1;">
  1553              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Listing Rewrite <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1554              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI rewrites your title and description using current SA market language and buyer psychology &mdash; pre-fills your edit form to review and save.</div>
  1555              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; Edit &rarr; "&#10024; Rewrite"</div>
  1556            </div>
  1557            <div style="font-size:12px;font-weight:700;color:#d97706;background:#fef3c7;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1558          </div>
  1559          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1560            <div style="font-size:22px;flex-shrink:0;">&#128269;</div>
  1561            <div style="flex:1;">
  1562              <div style="font-size:13px;font-weight:700;color:var(--text);">Why No Intros? AI Audit <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1563              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI reviews your listing &mdash; title, description, price and trust score &mdash; then gives you 3 specific fixes to attract more buyers right now.</div>
  1564              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; Edit &rarr; "&#128269; Why No Intros?"</div>
  1565            </div>
  1566            <div style="font-size:12px;font-weight:700;color:#059669;background:#d1fae5;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1567          </div>
  1568          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1569            <div style="font-size:22px;flex-shrink:0;">&#127183;</div>
  1570            <div style="flex:1;">
  1571              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Batch Card Lister <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; per run</span></div>
  1572              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Upload photos of many collector cards at once and our AI drafts a separate listing for each &mdash; title, set, condition and a suggested price.</div>
  1573              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; + Sell &rarr; Collector cards &rarr; "Batch Cards"</div>
  1574            </div>
  1575            <div style="font-size:12px;font-weight:700;color:#5b21b6;background:#ede9fe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">bulk</div>
  1576          </div>
  1577        </div>
  1578        <!-- Buyer AI services -->
  1579        <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-3);margin-bottom:8px;">For buyers &middot; on any listing</div>
  1580        <div style="display:flex;flex-direction:column;gap:8px;">
  1581          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1582            <div style="font-size:22px;flex-shrink:0;">&#128161;</div>
  1583            <div style="flex:1;">
  1584              <div style="font-size:13px;font-weight:700;color:var(--text);">Is This a Fair Price? <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1585              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI compares the asking price to current SA market rates and gives a verdict &mdash; fair, above or below market &mdash; plus a suggested fair range.</div>
  1586              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Open any listing &rarr; "&#128161; Is this a fair price?"</div>
  1587            </div>
  1588            <div style="font-size:12px;font-weight:700;color:#1d4ed8;background:#dbeafe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1589          </div>
  1590          <div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border);">
  1591            <div style="font-size:22px;flex-shrink:0;">&#128200;</div>
  1592            <div style="flex:1;">
  1593              <div style="font-size:13px;font-weight:700;color:var(--text);">AI Yield Estimate <span style="font-size:11px;font-weight:400;color:var(--text-3);">&middot; 1T</span></div>
  1594              <div style="font-size:12px;color:var(--text-2);margin-top:3px;line-height:1.5;">Our AI estimates rental yield and return for a property or accommodation listing using current SA market data. Sellers can run it from Edit too.</div>
  1595              <div style="font-size:11px;color:var(--text-3);margin-top:4px;">&#128205; Property / accommodation listing &rarr; "&#128200; Investor Yield Calculator"</div>
  1596            </div>
  1597            <div style="font-size:12px;font-weight:700;color:#0e7490;background:#cffafe;padding:3px 8px;border-radius:20px;white-space:nowrap;flex-shrink:0;">1T</div>
  1598          </div>
  1599        </div>
  1600        <div style="font-size:11px;color:var(--text-3);margin-top:12px;padding:10px 12px;background:var(--surface-2);border-radius:8px;">
  1601          <strong>Non-refundable policy:</strong> AI services are charged on use. If the AI call fails due to a server error, no Tuppence is deducted. Results are provided as-is for guidance only.
  1602        </div>
  1603        </div>
  1604      </details>
  1605  
```

## VIZ map legend naming Sonnet (F4 context: display text, not a call site) — from dashboard.server.html

```
  1112       App categories:  Listings/Adverts purple · Trust&Safety green · Search blue ·
  1113                        Tuppence cyan · Ops amber
  1114       Task tiers:      haiku sky · sonnet violet · vision pink · triage gold
  1115       Vendor lanes:    Anthropic terracotta · OpenAI green · Scaleway purple
  1116       Status:          ok green · warn amber · fail red · no-key grey            */
  1117    var CAT={listings:'#8b5cf6',trust:'#10b981',search:'#3b82f6',tuppence:'#06b6d4',ops:'#f59e0b'};
  1118    var TIER={haiku:'#38bdf8',sonnet:'#a78bfa',vision:'#f472b6',triage:'#fbbf24'};
  1119    var LANE={anthropic:'#e07a5f',openai:'#10a37f',scaleway:'#8b5cf6'};
  1120    var STAT={ok:'#22c55e',warn:'#eab308',fail:'#ef4444',nokey:'#6b7280'};
  1121  
  1122    /* ════════ 1 · AI PROVIDERS MAP ════════ */
  1123    window.msVizBuildAI=function(){
  1124      var d=window._apv3||{active:'openai',standing:'openai',override:null,providers:[]};
  1125      var avail={}; (d.providers||[]).forEach(function(p){avail[p.id]=!!p.available;});
  1126      if(!(d.providers||[]).length){avail={openai:true,anthropic:true,scaleway:true};}
  1127      var groups=[
  1128        {id:'listings',name:'LISTINGS &amp; ADVERTS',c:CAT.listings,items:[
  1129          {n:'Advert coach &amp; super-adverts',t:['sonnet','haiku']},
  1130          {n:'Mode B anonymity rewrite',t:['sonnet']},
  1131          {n:'Import photo scan',t:['sonnet','vision']}]},
  1132        {id:'trust',name:'TRUST &amp; SAFETY',c:CAT.trust,items:[
  1133          {n:'KYC ID verification',t:['sonnet','vision']},
  1134          {n:'Photo checks — orientation &middot; anonymity',t:['vision']}]},
  1135        {id:'search',name:'SEARCH &amp; DISCOVERY',c:CAT.search,items:[
  1136          {n:'Search interpretation',t:['haiku']}]},
  1137        {id:'tuppence',name:'TUPPENCE AI SERVICES',c:CAT.tuppence,items:[
  1138          {n:'Tier 1 &amp; 2 buyer/seller services',t:['haiku','sonnet']}]},
  1139        {id:'ops',name:'OPS &amp; ADMIN',c:CAT.ops,items:[
  1140          {n:'Email triage',t:['triage']},
  1141          {n:'Provider self-test (this dashboard)',t:['haiku']}]}
  1142      ];
  1143      var s='';
  1144      s+='<defs><filter id="msvGlow" x="-40%" y="-40%" width="180%" height="180%">'+
  1145         '<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';
  1146      /* column headings */
  1147      s+=txt(180,32,'APP FEATURES',12,'#64748b',800,'middle','2px');
  1148      s+=txt(487,32,'TASK TIERS',12,'#64748b',800,'middle','2px');
  1149      s+=txt(770,32,'THE SEAM',12,'#64748b',800,'middle','2px');
  1150      s+=txt(1170,32,'VENDOR LANES',12,'#64748b',800,'middle','2px');
  1151  
  1152      /* tier chips */
  1153      var tiers={haiku:{y:170,d:'everyday text'},sonnet:{y:290,d:'heavy reasoning'},vision:{y:410,d:'image analysis'},triage:{y:530,d:'inbox sorting'}};
  1154      Object.keys(tiers).forEach(function(k){var t=tiers[k];
  1155        s+=box(432,t.y-26,112,52,TIER[k],'#0d1526',26);
  1156        s+=txt(488,t.y-2,k,14,TIER[k],800,'middle');
```

## INTRO-RELAY-1: alias mint, forward, relay endpoint (Option B) — from bea_main.py

```
  5178  
  5179  
  5180  # ══ INTRO-RELAY-1 (5 Aug 2026) — masked-alias introduction relay (Option B) ══
  5181  # David's doctrine: "Nothing of the customer's leaves TrustSquare except a consented,
  5182  # revocable email channel — never the address itself. We disclose nothing; we relay."
  5183  # Dark until launch_switches.intro_relay = 1 (fail-closed). Spec:
  5184  # Records/INTRO_RELAY_BUILD_SPEC.md. Inbound rides Cloudflare Email Routing via the
  5185  # Worker (ops/cloudflare/intro_relay_worker.js); outbound rides the Resend lane.
  5186  # ENVKEY-1 class (fixed 5 Aug 2026, found live by the rail light staying off): the
  5187  # systemd unit does NOT export the server .env to this process — a bare os.getenv is
  5188  # empty on the server. ai_provider.envkey() checks the environment FIRST, then falls
  5189  # back to reading /var/www/marketsquare/.env — the established pattern for every key.
  5190  RELAY_DOMAIN = ai_provider.envkey("RELAY_DOMAIN") or "relay.trustsquare.co"
  5191  RELAY_INBOUND_SECRET = ai_provider.envkey("RELAY_INBOUND_SECRET") or ""
  5192  _RELAY_MAX_BODY = 100_000        # relayed text cap; attachments are v2, dropped loudly
  5193  _RELAY_TTL_DAYS = int(os.getenv("RELAY_TTL_DAYS", "30"))
  5194  
  5195  
  5196  def _intro_relay_enabled() -> bool:
  5197      """Read the launch switch. Fail-closed on any error (mirror of _fault_report_enabled)."""
  5198      try:
  5199          conn = database.get_db()
  5200          try:
  5201              row = conn.execute("SELECT intro_relay FROM launch_switches WHERE id = 1").fetchone()
  5202          finally:
  5203              conn.close()
  5204          return bool(row and row["intro_relay"])
  5205      except Exception as exc:
  5206          _log.error("intro_relay flag read failed: %s", exc)
  5207          return False
  5208  
  5209  
  5210  def _mint_relay_aliases(conn, intro_id: int, buyer_email: str, seller_email: str):
  5211      """Create the two masked aliases for an accepted intro. Random, unguessable, no PII
  5212      in the string. buyer_alias MASKS the buyer (mail sent to it reaches the buyer);
  5213      each party is GIVEN the counterparty's alias to write to."""
  5214      import secrets as _sec
  5215      b_alias = "intro-%s@%s" % (_sec.token_hex(6), RELAY_DOMAIN)
  5216      s_alias = "intro-%s@%s" % (_sec.token_hex(6), RELAY_DOMAIN)
  5217      now = datetime.now(timezone.utc)
  5218      exp = (now + timedelta(days=_RELAY_TTL_DAYS)).isoformat(timespec="seconds")
  5219      for alias, party, real, counter in (
  5220              (b_alias, "buyer", buyer_email, s_alias),
  5221              (s_alias, "seller", seller_email, b_alias)):
  5222          conn.execute(
  5223              "INSERT INTO intro_relay_aliases "
  5224              "(alias, intro_id, party, real_email, counter_alias, created_at, expires_at) "
  5225              "VALUES (?,?,?,?,?,?,?)",
  5226              (alias, intro_id, party, (real or "").strip().lower(), counter,
  5227               now.isoformat(timespec="seconds"), exp))
  5228      return b_alias, s_alias
  5229  
  5230  
  5231  def _relay_sanitize_subject(s: str) -> str:
  5232      """One line, header-injection-proof, bounded."""
  5233      return " ".join((s or "").replace("\r", " ").replace("\n", " ").split())[:200]
  5234  
  5235  
  5236  def _relay_forward(to_real: str, from_alias: str, subject: str, body: str) -> bool:
  5237      """Forward one relayed message via the Resend lane. From AND Reply-To are the
  5238      sender's ALIAS — never a real address — so the reply loops back through the
  5239      curtain. Text only in v1. Never raises."""
  5240      to_clean = parseaddr(to_real)[1]
  5241      if not to_clean:
  5242          _log.warning("INTRO-RELAY-1 forward skipped — bad recipient")
  5243          return False
  5244      key = ai_provider.envkey("RESEND_API_KEY") or ""
  5245      if not key:
  5246          _log.error("INTRO-RELAY-1 forward skipped — RESEND_API_KEY not set")
  5247          return False
  5248      try:
  5249          import httpx as _hx
  5250          r = _hx.post("https://api.resend.com/emails",
  5251              headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
  5252              json={
  5253                    # RELAY-FROM-1 (5 Aug 2026, found at the Resend paywall): a second
  5254                    # verified domain costs $20/mo; the FREE and deliverability-superior
  5255                    # route sends From the already-verified mail domain while the ALIAS
  5256                    # rides Reply-To — replying still goes through the curtain, and no
  5257                    # real address appears anywhere. Anonymity identical, cost zero.
  5258                    "from": _safe_from(ai_provider.envkey("RELAY_FROM"), "TrustSquare Intro <intro@mail.trustsquare.co>"),
  5259                    "to": [to_clean],
  5260                    "subject": _relay_sanitize_subject(subject) or "TrustSquare introduction",
  5261                    "text": (body or "")[:_RELAY_MAX_BODY],
  5262                    "reply_to": from_alias},
  5263              timeout=20)
  5264          if r.status_code in (200, 201):
  5265              return True
  5266          _log.error("INTRO-RELAY-1 forward HTTP %s: %s", r.status_code, r.text[:200])
  5267          return False
  5268      except Exception as exc:
  5269          _log.error("INTRO-RELAY-1 forward failed: %s", exc)
  5270          return False
  5271  
  5272  
  5273  def _relay_send_intro_notes(intro_id: int, buyer_email: str, buyer_name: str,
  5274                              seller_email: str, listing_title: str,
  5275                              b_alias: str, s_alias: str) -> None:
  5276      """Introduce both parties through the curtain. Each note arrives FROM the
  5277      counterparty's alias, so simply replying starts the relayed conversation.
  5278      Background task — never raises."""
  5279      try:
  5280          t = (listing_title or "your listing")[:80]
  5281          privacy = ("Reply to THIS email to talk. Your email address stays private: messages "
  5282                     "travel through TrustSquare's introduction relay and each of you sees only "
  5283                     "a TrustSquare address. The channel stays open %d days.\n\n"
  5284                     "— TrustSquare · anonymous until you choose otherwise" % _RELAY_TTL_DAYS)
  5285          note_seller = ("Good news — %s asked to be introduced about \"%s\" and the "
  5286                         "introduction is now open.\n\n%s" % (buyer_name or "a buyer", t, privacy))
  5287          note_buyer = ("Good news — the seller accepted your introduction request about "
  5288                        "\"%s\".\n\n%s" % (t, privacy))
  5289          # the seller's note arrives FROM the buyer's alias; the buyer's FROM the seller's
  5290          _relay_forward(seller_email, b_alias, "Introduction: %s" % t, note_seller)
  5291          _relay_forward(buyer_email, s_alias, "You're introduced: %s" % t, note_buyer)
  5292          _log.info("INTRO-RELAY-1 notes sent for intro #%s (aliases only)", intro_id)
  5293      except Exception as exc:
  5294          _log.error("INTRO-RELAY-1 notes failed for intro #%s: %s", intro_id, exc)
  5295  
  5296  
  5297  class _RelayInbound(BaseModel):
  5298      to_alias: str
  5299      from_addr: str
  5300      subject: str = ""
  5301      body: str = ""
  5302  
  5303  
  5304  @app.post("/intro/relay")
  5305  def intro_relay_inbound(req: _RelayInbound, x_relay_secret: str = Header(default="")):
  5306      """Receive one relayed message from the Cloudflare Email Worker and forward it to
  5307      the hidden counterparty. Enrolled-parties-only: the sender's address must match the
  5308      counter-alias's real_email — a stranger who guesses an alias is rejected and the
  5309      real addresses never move. No outbound fetch exists on this path (nothing
  5310      SSRF-shaped). Auth: X-Relay-Secret (RELAY_INBOUND_SECRET)."""
  5311      if not _intro_relay_enabled():
  5312          raise HTTPException(status_code=503, detail="The introduction relay is not open.")
  5313      if not RELAY_INBOUND_SECRET or x_relay_secret != RELAY_INBOUND_SECRET:
  5314          raise HTTPException(status_code=401, detail="Invalid relay secret")
  5315      to_alias = (req.to_alias or "").strip().lower()
  5316      from_addr = (parseaddr(req.from_addr or "")[1] or "").strip().lower()
  5317      if not to_alias or not from_addr:
  5318          raise HTTPException(status_code=400, detail="to_alias and from_addr are required")
  5319      conn = database.get_db()
  5320      try:
  5321          now = datetime.now(timezone.utc).isoformat(timespec="seconds")
  5322          row = conn.execute("SELECT * FROM intro_relay_aliases WHERE alias=?",
  5323                             (to_alias,)).fetchone()
  5324          if not row or not row["active"] or row["expires_at"] < now:
  5325              raise HTTPException(status_code=404, detail="This introduction channel is closed.")
  5326          counter = conn.execute("SELECT * FROM intro_relay_aliases WHERE alias=?",
  5327                                 (row["counter_alias"],)).fetchone()
  5328          if not counter or not counter["active"]:
  5329              raise HTTPException(status_code=404, detail="This introduction channel is closed.")
  5330          if from_addr != counter["real_email"]:
  5331              _log.warning("INTRO-RELAY-1 rejected non-enrolled sender on %s", to_alias)
  5332              raise HTTPException(status_code=403,
  5333                                  detail="Only the introduced parties can use this channel.")
  5334      finally:
  5335          conn.close()
  5336      ok = _relay_forward(row["real_email"], counter["alias"],
  5337                          req.subject, (req.body or "")[:_RELAY_MAX_BODY])
  5338      if not ok:
  5339          raise HTTPException(status_code=502, detail="The relay could not deliver this message.")
  5340      return {"relayed": True}
  5341  
  5342  
  5343  @app.post("/intros")
  5344  def create_intro(intro: IntroRequest, background_tasks: BackgroundTasks,
  5345                   ts_user: str = Cookie(default=None)):
  5346      _bind_charged_email(intro.buyer_email, ts_user, "create-intro")   # ACCOUNT-BIND-1
  5347      conn = database.get_db()
```

## ACCOUNT-BIND-1: session helpers + bind — from bea_main.py

```
  5120  
  5121  
  5122  # ══ ACCOUNT-BIND-1 (5 Aug 2026) — charged identity is PROVEN, never asserted ══
  5123  # Peer round-2 BLOCKER (F1), David's Option A ruling: the account an action charges
  5124  # comes from the authenticated session (ts_user cookie, set by /auth/verify after a
  5125  # magic-link proof of email possession), never from a caller-typed email behind the
  5126  # public app key. Dark until launch_switches.account_binding = 1; while OFF, every
  5127  # mismatch is shadow-logged so the flip is informed, not hopeful.
  5128  
  5129  def _account_binding_enabled() -> bool:
  5130      """Read the launch switch. Fail-closed on any error."""
  5131      try:
  5132          conn = database.get_db()
  5133          try:
  5134              row = conn.execute("SELECT account_binding FROM launch_switches WHERE id = 1").fetchone()
  5135          finally:
  5136              conn.close()
  5137          return bool(row and row["account_binding"])
  5138      except Exception as exc:
  5139          _log.error("account_binding flag read failed: %s", exc)
  5140          return False
  5141  
  5142  
  5143  def _session_email(ts_user):
  5144      """Proven email from the ts_user session cookie (JWT scope 'user'), or None.
  5145      The cookie is set ONLY by /auth/verify after a magic-link click — possession of
  5146      the inbox is the proof. The shared review token has scope 'review' and can never
  5147      pass this check even though it rides the same secret."""
  5148      if not ts_user:
  5149          return None
  5150      try:
  5151          p = _pyjwt.decode(ts_user, _JWT_SECRET, algorithms=[_JWT_ALGO])
  5152          if p.get("scope") != "user":
  5153              return None
  5154          return ((p.get("sub") or "").strip().lower()) or None
  5155      except Exception:
  5156          return None
  5157  
  5158  
  5159  def _bind_charged_email(passed_email, ts_user, ctx=""):
  5160      """Enforce (flag ON) or shadow-log (flag OFF) that the charged account is the
  5161      session's proven identity. Returns the canonical charged email. Flag OFF is
  5162      byte-identical to today's behaviour apart from one log line."""
  5163      passed = (passed_email or "").strip().lower()
  5164      sess = _session_email(ts_user)
  5165      if not _account_binding_enabled():
  5166          if not sess:
  5167              _log.info("ACCOUNT-BIND-1 shadow: no session (ctx=%s passed=%s)", ctx, passed)
  5168          elif passed and sess != passed:
  5169              _log.warning("ACCOUNT-BIND-1 shadow MISMATCH (ctx=%s): session=%s passed=%s",
  5170                           ctx, sess, passed)
  5171          return passed
  5172      if not sess:
  5173          raise HTTPException(status_code=401, detail="Please sign in to use this feature.")
  5174      if passed and passed != sess:
  5175          raise HTTPException(status_code=403,
  5176                              detail="This action can only be performed on your own account.")
  5177      return sess
  5178  
  5179  
  5180  # ══ INTRO-RELAY-1 (5 Aug 2026) — masked-alias introduction relay (Option B) ══
  5181  # David's doctrine: "Nothing of the customer's leaves TrustSquare except a consented,
  5182  # revocable email channel — never the address itself. We disclose nothing; we relay."
  5183  # Dark until launch_switches.intro_relay = 1 (fail-closed). Spec:
  5184  # Records/INTRO_RELAY_BUILD_SPEC.md. Inbound rides Cloudflare Email Routing via the
  5185  # Worker (ops/cloudflare/intro_relay_worker.js); outbound rides the Resend lane.
  5186  # ENVKEY-1 class (fixed 5 Aug 2026, found live by the rail light staying off): the
  5187  # systemd unit does NOT export the server .env to this process — a bare os.getenv is
  5188  # empty on the server. ai_provider.envkey() checks the environment FIRST, then falls
  5189  # back to reading /var/www/marketsquare/.env — the established pattern for every key.
```

## accept_intro: owner gate + relay wiring + alias-only webhook — from bea_main.py

```
  5716  
  5717  @app.put("/intros/{intro_id}/accept")
  5718  def accept_intro(intro_id: int, background_tasks: BackgroundTasks,
  5719                   _key: str = Depends(auth.require_api_key),
  5720                   ts_user: str = Cookie(default=None)):
  5721      conn = database.get_db()
  5722      intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
  5723      if not intro:
  5724          conn.close()
  5725          raise HTTPException(status_code=404, detail="Intro not found")
  5726      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
  5727      # BIND-OWNER-1 (ACCOUNT-BIND-1, 5 Aug 2026): accepting charges the BUYER, so the
  5728      # accepter must be PROVEN to be the listing owner — not merely hold the public key.
  5729      if _account_binding_enabled():
  5730          _sess = _session_email(ts_user)
  5731          _owner = ((listing["seller_email"] or "") if listing else "").strip().lower()
  5732          if not _sess:
  5733              conn.close()
  5734              raise HTTPException(status_code=401,
  5735                                  detail="Please sign in to accept introductions.")
  5736          if _owner and _sess != _owner:
  5737              conn.close()
  5738              raise HTTPException(status_code=403,
  5739                                  detail="Only the listing owner can accept an introduction.")
  5740      conn.execute(
  5741          "UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 WHERE id = ?",
  5742          (intro_id,)
  5743      )
  5744      # Deduct 1 Tuppence from the buyer's wallet
  5745      conn.execute(
  5746          "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'intro_deduct', -1, ?)",
  5747          (intro["buyer_email"], f"Intro accepted · listing #{intro['listing_id']} · {listing['title'] if listing else ''}")
  5748      )
  5749      conn.commit()
  5750      # INTRO-RELAY-1 (5 Aug 2026): with the relay ON, the introduction happens through
  5751      # masked aliases — the raw counterpart addresses never leave TrustSquare (not to the
  5752      # parties, not to the webhook). Flag OFF = today's behaviour, byte for byte.
  5753      _relay_on = _intro_relay_enabled()
  5754      _b_alias = _s_alias = None
  5755      if _relay_on and listing and listing["seller_email"]:
  5756          try:
  5757              _b_alias, _s_alias = _mint_relay_aliases(
  5758                  conn, intro_id, intro["buyer_email"], listing["seller_email"])
  5759              conn.commit()
  5760          except Exception as _re:
  5761              _log.error("INTRO-RELAY-1 mint failed — legacy flow for intro #%s: %s", intro_id, _re)
  5762              _relay_on = False
  5763      conn.close()
  5764      if _relay_on and _b_alias and _s_alias:
  5765          background_tasks.add_task(
  5766              _relay_send_intro_notes, intro_id,
  5767              intro["buyer_email"], intro["buyer_name"] or "",
  5768              listing["seller_email"], listing["title"] or "",
  5769              _b_alias, _s_alias)
  5770      if N8N_WEBHOOK_ACCEPT:
  5771          payload = {
  5772              "event":              "intro_accepted",
  5773              "intro_id":           intro_id,
  5774              "listing_id":         intro["listing_id"],
  5775              "listing_title":      listing["title"] if listing else None,
  5776              "category":           listing["category"] if listing else None,
  5777              # relay ON: aliases only — the raw addresses stay inside TrustSquare
  5778              "buyer_email":        _b_alias if _relay_on else intro["buyer_email"],
  5779              "buyer_name":         intro["buyer_name"],
  5780              "seller_email":       (_s_alias if _relay_on else
  5781                                     (listing["seller_email"] if listing and listing["seller_email"] else None)),
  5782              "relay":              bool(_relay_on),
  5783              "city":               listing["city"] if listing else None,
  5784              "timestamp":          datetime.now(timezone.utc).isoformat(),
  5785          }
  5786          background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_ACCEPT, payload)
  5787      return {"message": "Introduction accepted — 1T charged"}
  5788  
  5789  @app.put("/intros/{intro_id}/decline")
  5790  def decline_intro(intro_id: int, background_tasks: BackgroundTasks,
  5791                    _key: str = Depends(auth.require_api_key),
  5792                    ts_user: str = Cookie(default=None)):
  5793      conn = database.get_db()
  5794      intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
  5795      if not intro:
  5796          conn.close()
  5797          raise HTTPException(status_code=404, detail="Intro not found")
  5798      listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
  5799      # BIND-OWNER-1: declining is the owner's decision too — no griefing declines.
  5800      if _account_binding_enabled():
  5801          _sess = _session_email(ts_user)
  5802          _owner = ((listing["seller_email"] or "") if listing else "").strip().lower()
  5803          if not _sess:
  5804              conn.close()
  5805              raise HTTPException(status_code=401, detail="Please sign in to decline introductions.")
```

## /auth/verify: magic-link proof kept as ts_user session — from bea_main.py

```
 13131  
 13132  @app.post("/auth/verify-code")
 13133  def auth_verify_code(req: _SignInCodeVerify, request: Request, response: Response):
 13134      """SIGNIN-CODE-1: sign in with the 6-digit code from the email, in the tab the
 13135      person already has open. No device hop, no link to lose, nothing a mail scanner
 13136      can spend. Rate-limited per IP on top of the per-code guess budget."""
 13137      ip = (request.headers.get("x-forwarded-for")
 13138            or (request.client.host if request.client else "?")).split(",")[0].strip()
 13139      if not _review_rate_ok(ip):
 13140          raise HTTPException(status_code=429, detail="Too many attempts. Please wait a few minutes.")
 13141      email = (req.email or "").strip().lower()
 13142      if not _signin_code_ok(email, req.code or ""):
 13143          raise HTTPException(status_code=401,
 13144                              detail="That code is wrong or has expired — send yourself a new one.")
 13145      _log.info("signin-code OK for %s from %s", email, ip)
 13146      return _establish_user_session(email, response)
 13147  
 13148  @app.post("/auth/request-link")
 13149  def auth_request_link(req: _SignInRequest):
 13150      """Email a sign-in CODE (primary) and link (convenience). Always returns ok."""
 13151      import time as _t
 13152      email = (req.email or "").strip().lower()
 13153      if "@" not in email or "." not in email.split("@")[-1]:
 13154          raise HTTPException(status_code=400, detail="Please enter a valid email address.")
 13155      token = _pyjwt.encode(
 13156          {"email": email, "purpose": "signin",
 13157           "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
 13158           "iat": datetime.now(timezone.utc)},
 13159          _JWT_SECRET, algorithm=_JWT_ALGO)
 13160      code = _new_review_code()
 13161      _signin_codes[email] = {"code": code, "exp": _t.time() + _SIGNIN_CODE_MIN * 60, "tries": 0}
 13162      status = _send_login_email(email, APP_URL + "/?signin=" + token, code)
 13163      return {"ok": True, "sent": status}
 13164  
 13165  @app.post("/auth/verify")
 13166  def auth_verify(req: _SignInVerify, response: Response):
 13167      """Verify a sign-in token; create the account on first use. Returns email+name."""
 13168      try:
 13169          payload = _pyjwt.decode(req.token, _JWT_SECRET, algorithms=[_JWT_ALGO])
 13170      except _pyjwt.ExpiredSignatureError:
 13171          raise HTTPException(status_code=401, detail="This sign-in link has expired — request a new one.") from None
 13172      except _pyjwt.InvalidTokenError:
 13173          raise HTTPException(status_code=401, detail="This sign-in link is not valid.") from None
 13174      if payload.get("purpose") != "signin":
 13175          raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
 13176      email = (payload.get("email") or "").strip().lower()
 13177      if not email:
 13178          raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
 13179      return _establish_user_session(email, response)   # SIGNIN-CODE-1: one shared door
 13180  
 13181  # ── AGENCY (Team plan) — umbrella over agent sellers ───────────────────────
 13182  class _AgencyCreate(_BaseModel):
 13183      name: str
 13184      admin_email: str
 13185      countries: list = []
```


# ROADMAP 2 · BEA Modularization — STEP M1 Execution Spec
**`core_spend.py` (cost helpers) extraction**
*Planning deliverable · drafted 2 June 2026 · Session 99 follow-up. No code changed.*
*Companion to `MODULARIZATION_PLAN.md` (the M1–M9 master plan). M1 = the safe seed step.*

---

## 0 · TL;DR (what M1 does)

Move 7 self-contained AI-spend cost symbols out of the 10,705-line `bea_main.py` into a new
`core_spend.py`, then import them back so **every existing call site keeps working unchanged**.
This is the lowest-risk extraction (recently written, well-understood, one logical cluster) and
exists to **prove the extract → AST → smoke → deploy → health gate** before any router moves (M4+).

**Net effect on `bea_main.py`:** ~210 lines removed (the defs + consts), ~3 lines added (one import
block). Behaviour identical. No route changes. No schema changes.

---

## 1 · Exact symbols moving (source map, current line numbers)

All 7 live in one contiguous-ish band of `bea_main.py`. Verified line numbers (Session 99 build, 10,705 lines):

| Symbol | Kind | Current lines | Moves to `core_spend.py`? |
|---|---|---|---|
| `_AI_COST` | dict const | 835–840 | **MOVE** |
| `_MODEL_PRICE` | dict const | 843–849 | **MOVE** |
| `_token_cost(model_key, in_tok, out_tok) -> float` | pure fn | 851–857 | **MOVE** |
| `_usage_tokens(resp_json: dict)` | pure fn | 860–869 | **MOVE** |
| `_log_ai_spend(email, endpoint, model_key, in_tok=None, out_tok=None)` | fn (DB write) | 992–1023 | **MOVE** |
| `_maybe_fire_spend_alert(conn)` | fn (DB read + webhook) | 1026–1088 | **MOVE** |
| `_check_cost_ceiling(email) -> None` | fn (DB read, raises 429) | 1091–1145 | **MOVE** |

> Note the band is **not** fully contiguous: lines 871–991 (Hetzner/R2 config, `_cf_purge_all`,
> Anthropic/email/CF env, `_s3_upload`, `_fire_webhook`) sit **between** `_usage_tokens` (ends 869)
> and `_log_ai_spend` (starts 992). The driver therefore removes **two separate blocks** (835–869
> and 992–1145), not one. `_s3_upload` and `_fire_webhook` **stay** in `bea_main.py` (M2 handles
> media; `_fire_webhook` is a shared util used elsewhere — keep it home and pass it in).

---

## 2 · Dependencies of the moved code (what they reach for)

Grepped every name referenced inside the 7 symbols:

| Dependency | Defined where | Strategy for M1 |
|---|---|---|
| `database` (module) | `import database` @ bea_main line 6; `database.get_db()` | **Re-import in `core_spend.py`** (`import database`). It is a stateless module returning a fresh SQLite connection — safe to import in two places. No injection needed. |
| `_log` | module-level `logging.getLogger("bea")` @ line 766 | **Re-create in `core_spend.py`** as `logging.getLogger("bea")` (same name → same logger instance/handlers). No injection needed. |
| `HTTPException` | `from fastapi import … HTTPException` @ line 1 | **Re-import in `core_spend.py`** (`from fastapi import HTTPException`). `_check_cost_ceiling` raises 429 with it. |
| `httpx` | `import httpx` @ line 14 | Only used **indirectly** via `_fire_webhook`. Since `_fire_webhook` is **injected** (below), `core_spend.py` does **not** import httpx. |
| `asyncio` | imported locally inside `_maybe_fire_spend_alert` (line 1080 `import asyncio`) | **Keep the local import** inside the moved function — zero change. |
| `datetime` | called as `__import__('datetime').datetime.utcnow()` inside the funcs | **Keep as-is** (the funcs self-import via `__import__`). No top-level datetime needed in `core_spend.py`. (Cosmetic cleanup deferred — do NOT refactor in M1; behaviour-identical is the rule.) |
| `_fire_webhook` (async) | `async def _fire_webhook` @ bea_main line 983 — **STAYS in bea_main** | **INJECT.** `_maybe_fire_spend_alert` is the only consumer. `core_spend.py` holds a module-level slot `_fire_webhook = None`, set once at import time by bea_main via `core_spend.set_fire_webhook(_fire_webhook)`. See §3. |
| `N8N_WEBHOOK_AI_ALERT` (env) | `os.getenv(...)` @ bea_main line 825 — read at import | **INJECT alongside `_fire_webhook`** through the same `configure()` call, OR re-read via `os.getenv` in `core_spend.py`. **Chosen: re-read via `os.getenv("N8N_WEBHOOK_AI_ALERT")` at module load in `core_spend.py`** (it is a plain env string, no coupling). Keep the line in bea_main too (harmless; other code may reference it later). |

**Decision summary — move vs. inject vs. re-import:**
- **Move:** the 7 listed symbols only.
- **Re-import (no coupling, stateless):** `database`, `logging`/`_log`, `HTTPException`, `os` (for the env read).
- **Inject (stateful / lives elsewhere):** `_fire_webhook` only — passed in once at startup so we don't drag `_s3_upload`/httpx/the whole webhook util into M1.

This keeps M1 a **pure lift** of the cost cluster with a single one-way injection seam.

---

## 3 · Proposed `core_spend.py` — full contents & signatures

> This is the target file to create next session. Signatures are **byte-identical** to current defs;
> only the injection shim (`set_fire_webhook` + the module-level `_fire_webhook` slot) is new.

```python
# core_spend.py
# TrustSquare BEA — AI-spend cost helpers (extracted from bea_main.py, STEP M1).
# Pure cost math + spend logging + daily ceiling guard + monthly alert.
# Deps: `database` (stateless conn factory), stdlib logging/os, fastapi.HTTPException.
# `_fire_webhook` is INJECTED by bea_main at startup (see set_fire_webhook) so this
# module does not import httpx or the media/webhook layer.

import os
import logging

from fastapi import HTTPException

import database

_log = logging.getLogger("bea")  # same logger name as bea_main → shared handlers

# Injected by bea_main.set_fire_webhook(...) at import time. Async callable
# (url, payload) -> coroutine. Left None if bea_main never wires it (alerts no-op).
_fire_webhook = None

# n8n AI-spend alert webhook URL (plain env string, no coupling — re-read here).
N8N_WEBHOOK_AI_ALERT = os.getenv("N8N_WEBHOOK_AI_ALERT")


def set_fire_webhook(fn):
    """Wire bea_main's async _fire_webhook into this module (one-time, at startup)."""
    global _fire_webhook
    _fire_webhook = fn


# ── AI SPEND COST CONSTANTS (USD) ─────────────────────────────
# Two layers: _AI_COST flat fallback (call site passes no tokens) and
# _MODEL_PRICE real per-MILLION-token list prices (C2, Session 97).
_AI_COST = {
    "haiku":          0.0023,
    "sonnet":         0.0150,
    "sonnet_vision":  0.0400,
    "sonnet_rewrite": 0.0150,
}

# Real list prices, USD per 1,000,000 tokens (input, output).
_MODEL_PRICE = {
    "haiku":          (0.80,  4.00),
    "sonnet":         (3.00, 15.00),
    "sonnet_vision":  (3.00, 15.00),
    "sonnet_rewrite": (3.00, 15.00),
    "opus":           (15.00, 75.00),
}


def _token_cost(model_key: str, in_tok: int, out_tok: int) -> float:
    """Exact USD cost from real token counts (C2). Falls back to the flat estimate."""
    price = _MODEL_PRICE.get(model_key)
    if not price:
        return _AI_COST.get(model_key, 0.0023)
    in_rate, out_rate = price
    return (in_tok / 1_000_000.0) * in_rate + (out_tok / 1_000_000.0) * out_rate


def _usage_tokens(resp_json: dict):
    """(input_tokens, output_tokens) from an Anthropic response, or (None, None)."""
    try:
        u = resp_json.get("usage") or {}
        it = u.get("input_tokens"); ot = u.get("output_tokens")
        if it is None and ot is None:
            return (None, None)
        return (int(it or 0), int(ot or 0))
    except Exception:
        return (None, None)


def _log_ai_spend(email: str, endpoint: str, model_key: str,
                  in_tok: int | None = None, out_tok: int | None = None):
    """Background task: log AI call cost + trigger alert check if threshold crossed.
    C2: real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
    No tokens -> flat _AI_COST estimate, cost_is_real=0. Backward compatible. Never raises.
    """
    try:
        if in_tok is not None or out_tok is not None:
            it, ot = int(in_tok or 0), int(out_tok or 0)
            cost = _token_cost(model_key, it, ot)
            is_real = 1
        else:
            it, ot = 0, 0
            cost = _AI_COST.get(model_key, 0.0023)
            is_real = 0
        conn = database.get_db()
        try:
            conn.execute(
                "INSERT INTO ai_spend_log "
                "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real) "
                "VALUES (?,?,?,?,?,?,?)",
                (email or '', endpoint, model_key, cost, it, ot, is_real)
            )
            conn.commit()
            _maybe_fire_spend_alert(conn)
        finally:
            conn.close()
    except Exception as exc:
        _log.error("_log_ai_spend failed: %s", exc)


def _maybe_fire_spend_alert(conn):
    """Check if current month AI spend crossed the configured threshold.
    Fires n8n webhook at most once per day via the INJECTED _fire_webhook. Silent if unconfigured.
    """
    try:
        cfg = conn.execute(
            "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
            "FROM ai_spend_config WHERE id = 1"
        ).fetchone()
        if not cfg or cfg["monthly_income_usd"] <= 0:
            return
        month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
        row = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
            "WHERE logged_at >= ?", (month_start,)
        ).fetchone()
        month_spend = row["total"] if row else 0.0
        threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
        if month_spend < threshold_usd:
            return
        last = cfg["last_alerted_at"] or ""
        today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
        if last.startswith(today):
            return
        conn.execute(
            "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
            (__import__('datetime').datetime.utcnow().isoformat(),)
        )
        conn.commit()
        pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
        payload = {
            "alert": "ai_spend_threshold",
            "month_spend_usd": round(month_spend, 4),
            "income_usd": cfg["monthly_income_usd"],
            "threshold_pct": cfg["alert_threshold_pct"],
            "pct_used": round(pct_used, 1),
            "alert_email": cfg["alert_email"],
            "message": (
                f"TrustSquare AI spend alert: ${month_spend:.4f} spent this month "
                f"({pct_used:.1f}% of ${cfg['monthly_income_usd']:.2f} income). "
                f"Threshold: {cfg['alert_threshold_pct']}%."
            ),
        }
        _log.warning("AI spend alert fired: %s", payload["message"])
        if N8N_WEBHOOK_AI_ALERT and _fire_webhook:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
            except Exception:
                pass
    except Exception as exc:
        _log.error("_maybe_fire_spend_alert failed: %s", exc)


def _check_cost_ceiling(email: str) -> None:
    """C1 — HARD daily cost ceiling. Pre-flight guard before every paid AI call.
    REFUSES (HTTP 429) when today's logged AI spend hits the per-user or platform USD
    ceiling. Ceiling 0 = off. Superusers exempt from per-user rail. Fail-OPEN on error.
    """
    try:
        conn = database.get_db()
        try:
            cfg = conn.execute(
                "SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
                "FROM ai_spend_config WHERE id = 1"
            ).fetchone()
            if not cfg:
                return
            user_cap     = cfg["daily_user_ceiling_usd"]     or 0.0
            platform_cap = cfg["daily_platform_ceiling_usd"] or 0.0
            if user_cap <= 0 and platform_cap <= 0:
                return
            day_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
            if platform_cap > 0:
                prow = conn.execute(
                    "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log WHERE logged_at >= ?",
                    (day_start,)
                ).fetchone()
                if (prow["t"] if prow else 0.0) >= platform_cap:
                    _log.warning("C1 platform ceiling hit: $%.4f >= $%.2f — refusing (%s)",
                                 prow["t"], platform_cap, email)
                    raise HTTPException(
                        status_code=429,
                        detail="AI services are temporarily paused (daily platform budget reached). "
                               "Please try again later."
                    )
            if user_cap > 0 and email:
                su = conn.execute("SELECT is_superuser FROM users WHERE email = ?", (email,)).fetchone()
                if not (su and su["is_superuser"]):
                    urow = conn.execute(
                        "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log "
                        "WHERE email = ? AND logged_at >= ?", (email, day_start)
                    ).fetchone()
                    if (urow["t"] if urow else 0.0) >= user_cap:
                        _log.warning("C1 user ceiling hit: %s $%.4f >= $%.2f — refusing",
                                     email, urow["t"], user_cap)
                        raise HTTPException(
                            status_code=429,
                            detail="You've reached today's AI usage limit on this account. "
                                   "It resets at 00:00 UTC."
                        )
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as exc:
        _log.error("_check_cost_ceiling failed (failing open): %s", exc)
```

**The only non-mechanical change vs. the originals:** the alert-fire guard becomes
`if N8N_WEBHOOK_AI_ALERT and _fire_webhook:` (was `if N8N_WEBHOOK_AI_ALERT:`). This is required
because `_fire_webhook` is now injected and could be `None` if wiring is skipped — it makes the
module import-safe in isolation (e.g. under `ast.parse`/unit import) and cannot change live
behaviour (bea_main always wires it; see §4 step 2).

---

## 4 · How `bea_main.py` imports them back

Two edits to `bea_main.py`, both via the **Python str.replace driver** (never Edit/Write — CLAUDE.md
large-file rule; the file is 501 KB and the tools truncate it).

**Edit A — add the import + wiring.** Insert immediately AFTER `_fire_webhook` is defined
(it ends at line 989) so the function object exists before we pass it in. Anchor on the closing of
`_fire_webhook` and the start of the (now-removed) `_log_ai_spend`:

```python
# Insert after _fire_webhook (line ~989), before the old cost block:
import core_spend
from core_spend import (
    _AI_COST, _MODEL_PRICE,
    _token_cost, _usage_tokens,
    _log_ai_spend, _maybe_fire_spend_alert, _check_cost_ceiling,
)
core_spend.set_fire_webhook(_fire_webhook)   # M1 injection seam
```

Re-importing the names into bea_main's namespace means **all 18 call sites resolve unchanged** —
they keep calling bare `_log_ai_spend(...)`, `_check_cost_ceiling(...)`, `_usage_tokens(...)`, etc.

**Edit B — delete the two moved blocks** from `bea_main.py`:
- Block 1: lines **835–869** (`_AI_COST` through end of `_usage_tokens`), i.e. the comment header at
  831–834 may stay or go; remove `_AI_COST=…` through the blank line after `_usage_tokens`.
- Block 2: lines **992–1145** (`_log_ai_spend` through end of `_check_cost_ceiling`).

> **Driver requirement (CLAUDE.md):** each `str.replace(old, new)` must assert the old string matched
> **exactly once** (`assert src.count(old) == 1`). Use generous, unique anchor strings (full def line +
> docstring first line) so there is no ambiguity. After both edits: `import ast; ast.parse(open('bea_main.py').read())` must pass. Re-verify the file still ends with the BEA's
> final line (not truncated) — `bea_main.py` has no `</html>` tail, so instead assert
> `src.rstrip().endswith(...)` against the known last def/route, and confirm `wc -l` dropped by ~190.

**Shared-dep ledger (passed-in vs. moved vs. re-imported):**

| Dep | Disposition | Where it ends up |
|---|---|---|
| 7 cost symbols | **moved** | `core_spend.py`, re-imported into bea_main |
| `_fire_webhook` | **passed in** (injection) | stays in bea_main; wired via `set_fire_webhook` |
| `database`, `_log`, `HTTPException`, `os` | **re-imported** (stateless) | both files import independently |
| `N8N_WEBHOOK_AI_ALERT` | **re-read** from env | both files (harmless duplicate) |
| `_s3_upload`, `httpx`, Anthropic/CF/email env | **untouched** | stay in bea_main (not part of M1) |

---

## 5 · Call-site table — every reference, unchanged vs. needs-edit

18 call sites across `bea_main.py` (grepped). **All resolve through the re-import in Edit A → ZERO
need logic edits.** Listed exhaustively so the post-deploy review can confirm each still fires.

### `_usage_tokens` — 8 call sites (all UNCHANGED)
| Line | Context |
|---|---|
| 2316 | photo orient path — `it, ot = _usage_tokens(rj)` |
| 3484 | `/advert-agent/market-note` — `_mn_in,_mn_out = _usage_tokens(_mn_json)` |
| 3782 | `/advert-agent/coach` — `_co_in,_co_out = _usage_tokens(_coach_json)` |
| 6814 | `/trust-score/guidance` — `_g_in,_g_out = _usage_tokens(_g_json)` |
| 7020 | `/trust-score/upload-comment` — `_uc_in,_uc_out = _usage_tokens(_uc_json)` |
| 9271 | `/listings/vision-draft` — `_vd_in,_vd_out = _usage_tokens(body)` |
| 9929 | `/listings/ai-price-check` — `_pc_in,_pc_out = _usage_tokens(_resp_json)` |
| 10135 | `/listings/yield-calc` — `_yc_in,_yc_out = _usage_tokens(_yc_json)` |

### `_log_ai_spend` — 9 call sites (all UNCHANGED)
| Line | Context | Form |
|---|---|---|
| 2360 | `/listings/photo:orient` | direct call (with tokens) |
| 3485 | `/advert-agent/market-note` | `background_tasks.add_task(_log_ai_spend, …)` |
| 3818 | `/advert-agent/coach` | `background_tasks.add_task(…)` |
| 6846 | `/trust-score/guidance` | `background_tasks.add_task(…)` |
| 7029 | `/trust-score/upload-comment` | `background_tasks.add_task(…)` |
| 9366 | `/listings/vision-draft` | `background_tasks.add_task(…)` |
| 9960 | `/listings/ai-price-check` | direct call (with tokens) |
| 10163 | `/listings/yield-calc` | direct call (with tokens) |
| 10518 | `/email/inbound` | `background_tasks.add_task(_log_ai_spend, from_addr, "/email/inbound", "haiku")` — **legacy no-token form** (exercises the `cost_is_real=0` flat-estimate branch) |

> `background_tasks.add_task(_log_ai_spend, …)` passes the **function object** by reference. After
> Edit A, the name `_log_ai_spend` in bea_main's module namespace points at the `core_spend` function
> — the reference is captured at call time, so this works with no change. (Confirm in review: the
> add_task sites are the highest-value smoke targets.)

### `_check_cost_ceiling` — 7 call sites (all UNCHANGED)
| Line | Endpoint guarded |
|---|---|
| 3460 | market-note (C1) |
| 3532 | coach (C1) |
| 6702 | trust-score/guidance (C1) |
| 6958 | trust-score/upload-comment (C1) |
| 9174 | listings/vision-draft (C1) |
| 9803 | listings/ai-price-check (C1) |
| 10037 | listings/yield-calc (C1) |

### `_token_cost`, `_AI_COST`, `_MODEL_PRICE`, `_maybe_fire_spend_alert`
| Symbol | Sites | Disposition |
|---|---|---|
| `_token_cost` | 1 (line 1004, inside `_log_ai_spend`) | **moves WITH the function** — internal, not a bea_main call site |
| `_AI_COST` | line 1008 (inside `_log_ai_spend`), 855 (inside `_token_cost`) | internal — move with funcs |
| `_MODEL_PRICE` | line 853 (inside `_token_cost`) | internal — move with funcs |
| `_maybe_fire_spend_alert` | line 1019 (inside `_log_ai_spend`) | internal — move with func |

**Conclusion: NEEDS-EDIT call sites = 0.** Only the 2 structural edits in §4 (add import / delete
blocks) touch `bea_main.py`. Every one of the 18 usages is unchanged.

---

## 6 · Verify / deploy gate (the full ritual, in order)

Mirror of `MODULARIZATION_PLAN.md` rule 4, made concrete for M1. **Run from David's PowerShell for
scp/ssh; run AST/driver in the sandbox.** Never commit from the sandbox.

**Pre-flight (sandbox):**
1. `bash /sessions/<session>/mnt/MarketSquare/load_sandbox_ssh.sh` (SSH key not persisted between sessions).
2. Confirm clear of the orchestrator Fixer window — see §7.

**Build (sandbox, working copy):**
3. Write `core_spend.py` (§3 contents).
4. Run the str.replace driver on `bea_main.py` (Edit A + Edit B, §4), each `assert count==1`.
5. **AST local:** `python3 -c "import ast; ast.parse(open('bea_main.py').read()); ast.parse(open('core_spend.py').read()); print('AST OK')"`.
6. **Import-resolves check:** `python3 -c "import ast,sys; [ast.parse(open(f).read()) for f in ('bea_main.py','core_spend.py')]"` plus a grep assert that the 7 names appear in the new `from core_spend import (...)` block.
7. **Line-count sanity:** `wc -l bea_main.py` should read ~10,515 (≈190 fewer than 10,705). No truncation: assert the file's last 200 chars still contain the final route/`uvicorn`/`__main__` tail that was there before.

**Deploy (PowerShell — `cd C:\Users\David\Projects\MarketSquare` first):**
8. **Back up server main.py:** `ssh root@178.104.73.239 "cp /var/www/marketsquare/main.py /var/www/marketsquare/main.py.mod1.bak"`.
9. `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py`
10. `scp core_spend.py root@178.104.73.239:/var/www/marketsquare/core_spend.py`
11. **AST in the BEA venv (server-side, real interpreter):**
    `ssh root@178.104.73.239 "/var/www/marketsquare/venv/bin/python -c \"import ast; ast.parse(open('/var/www/marketsquare/main.py').read()); ast.parse(open('/var/www/marketsquare/core_spend.py').read()); print('VENV AST OK')\""`
    — also confirms `core_spend` is importable by the venv (`/var/www/marketsquare/venv/bin/python -c "import sys; sys.path.insert(0,'/var/www/marketsquare'); import core_spend; print('import OK')"`).
12. **Restart BEA:** `ssh root@178.104.73.239 "systemctl restart marketsquare"`.
13. **/health:** `curl -s https://trustsquare.co/health` → `{"status":"ok",...}`. Bad-key guard: a protected endpoint with a wrong `X-Api-Key` returns **401**.
14. **Smoke test:** `python3 smoke_test.py` — **must be all-green.** (Plan says "30/30"; the suite
    currently emits **32 `check()` assertions** — treat "all checks passed / 0 failed" as the gate,
    not a literal 30. `smoke_test.py` runs entirely over SSH against the live box.)
15. **Live endpoint spot-checks for the moved cost paths** (proves the import wired correctly under load):
    - A `_check_cost_ceiling`-guarded endpoint returns normally (not a spurious 429) for a funded test user — e.g. `POST /trust-score/guidance` or `/advert-agent/coach`.
    - After one such AI call, confirm a fresh row landed: `ssh root@178.104.73.239 "sqlite3 /var/www/marketsquare/marketsquare.db \"SELECT endpoint, est_cost_usd, cost_is_real FROM ai_spend_log ORDER BY id DESC LIMIT 1;\""` — proves `_log_ai_spend` (background task) still writes via the re-imported function.
    - Optional: temporarily set a near-zero `daily_platform_ceiling_usd` on a scratch row to confirm the 429 path still fires, then restore. (Skip if risky — the DB row check above is sufficient evidence.)

**Gate decision:** if **any** of steps 5–15 fail → **roll back immediately** (§ rollback) and write the
failure to CHANGELOG. M1 is "done" only when 13+14+15 are all green AND the session-end checklist
(CLAUDE.md) is run.

**Rollback (single command, server is source of truth):**
```
ssh root@178.104.73.239 "cp /var/www/marketsquare/main.py.mod1.bak /var/www/marketsquare/main.py && rm -f /var/www/marketsquare/core_spend.py && systemctl restart marketsquare"
curl -s https://trustsquare.co/health   # confirm back to ok
```
This restores the monolith and removes the orphan module in one shot. The local `bea_main.py` working
copy is discarded (re-pull from server or `git checkout` if it was committed — it should NOT be
committed until the gate is green).

---

## 7 · Atomicity & timing rule

- **Must complete within one session, start-to-deploy.** M1 leaves `bea_main.py` in a half-split
  state between Edit B and a successful restart — never stop there. If the session cannot reach
  step 14 green, **roll back** (§6) rather than leaving a partial extraction.
- **Orchestrator Fixer window:** the maintenance loop runs **Sensor 03:30 / Fixer 04:00 /
  Orchestrator 05:00** local (per `project_orchestrator_loop.md` / `ORCHESTRATION_POLICY.md`). The
  Fixer is **walled off from structural edits** (its prompt carries the "MODULARIZATION IN PROGRESS —
  do not restructure bea_main.py" guard), so it cannot collide on the split. **Even so, do not run M1
  across the 03:30–05:30 band** — avoid any overlap with Sensor/Fixer/Orchestrator touching the same
  server files or restarting the service mid-deploy. Best execution slot: a daytime watched session
  well clear of those three runs. Confirm time-to-next-scheduled-run before step 4.
- **No concurrent agent on bea_main during M1.** M1 itself is the prerequisite that *later* unlocks
  concurrent router work (M4+); during M1 there must be exactly one writer on `bea_main.py`.
- **Server backup before deploy is mandatory** (step 8) — it is the rollback's only dependency.

---

## 8 · Why this is the right seed (risk notes)

- **Pure lift:** 7 symbols, one logical cluster, no route signatures touched, no schema touched.
- **Single injection seam** (`_fire_webhook`) — everything else is stateless re-import. Smallest
  possible coupling surface to prove the pattern.
- **Backward-compatible by construction:** names re-imported into bea_main's namespace → 18 call
  sites compile and run unchanged; the only logic delta is a defensive `and _fire_webhook` guard that
  cannot alter live behaviour.
- **Reversible in one command** (`main.py.mod1.bak`).
- If M1's gate passes clean, the same recipe (write module → str.replace driver → AST → smoke →
  scp+backup → venv AST → restart → health → live checks → rollback-on-fail) is reused verbatim for
  M2 (`core_media.py`) and is the template for the riskier APIRouter extractions M4–M9.

---

*End of ROADMAP 2 · M1 spec. Build-ready for next session. No code modified in producing this.*

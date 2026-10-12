#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 2/8 -- bea_main.py (flag-dark behind launch_switches.auto_renew).

Every in-place edit is an asserted-unique string replacement. The new block (bea_block.txt) is inserted
after /payment/seller-subscription/verify. The original one-off initialize call and the webhook's old
path are left byte-identical; each gains one guarded hook that returns its "today's path" value first.
"""
import os, py_compile, ast
from patchlib import load, save, rep, root

HERE = os.path.dirname(os.path.abspath(__file__))
R = root()
P = os.path.join(R, "bea_main.py")
s, crlf, orig = load(P)
if "AUTO-RENEW-1" in s:
    print("bea_main.py already carries AUTO-RENEW-1 -- skipped")
    raise SystemExit(0)
block = open(os.path.join(HERE, "bea_block.txt"), encoding="utf-8").read()
n0 = s.count("\n")

# ── A. schema: users columns (ALTER TABLE in run_migrations, like listings.reach) ─────────────────
s = rep(s, '''    if "reach" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN reach TEXT")
''', '''    if "reach" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN reach TEXT")
    # AUTO-RENEW-1 (RUL-224, 12 Oct 2026): a paid plan renews automatically as the standard.
    # auto_renew        1 = renew (the default, the tick box); 0 = she cancelled renewal or paid month-by-month.
    #                   It only means something while paystack_subscription_code is set.
    # paystack_subscription_code / paystack_email_token   the Paystack subscription her first card payment
    #                   opened; both are needed to switch it off or back on. Never sent to any app.
    # renewal_failed_at set when a renewal payment did not go through (she is told once); cleared by the
    #                   next renewal or when the plan ends.
    _ar_user_cols = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    for _arc, _ard in (("auto_renew", "INTEGER DEFAULT 1"), ("paystack_subscription_code", "TEXT"),
                       ("paystack_email_token", "TEXT"), ("renewal_failed_at", "TEXT")):
        if _arc not in _ar_user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN %s %s" % (_arc, _ard))
''')

# ── B. the switch column (default OFF) ───────────────────────────────────────────────────────────
s = rep(s, '''        "ALTER TABLE launch_switches ADD COLUMN circle_caps INTEGER NOT NULL DEFAULT 0",
''', '''        "ALTER TABLE launch_switches ADD COLUMN circle_caps INTEGER NOT NULL DEFAULT 0",
        # AUTO-RENEW-1 (RUL-224, 12 Oct 2026): paid plans renew automatically as the standard, one tick box
        # for month-by-month. Default OFF = today's one-off 30-day payment, untouched. Arming it is DAVID'S
        # act (RUL-076), from the +1 page or POST /admin/flags {"auto_renew": true}; reversible, no deploy.
        # Switching it off again stops NEW subscriptions only -- a seller who holds one keeps being served.
        "ALTER TABLE launch_switches ADD COLUMN auto_renew INTEGER NOT NULL DEFAULT 0",
''')

# ── C. GET /users/{email}: the new columns never leave the server through the whole-row read ─────
s = rep(s, '''    for _sensitive in ("id_number_hash", "id_name", "id_ai_score"):
        data.pop(_sensitive, None)''', '''    for _sensitive in ("id_number_hash", "id_name", "id_ai_score",
                       # AUTO-RENEW-1: the subscription code and token are the server's; the plan card reads
                       # its renewal state from /users/{email}/subscription, so this answer stays as it was.
                       "auto_renew", "paystack_subscription_code", "paystack_email_token", "renewal_failed_at"):
        data.pop(_sensitive, None)''')

# ── D. the lapse pass (RUL-201): hold a plan whose renewal is due; finish one that ended ─────────
s = rep(s, '''        for row in lapsed:
            em = (row["email"] or "").lower()
            upd = conn.execute(
                "UPDATE users SET seller_tier='free', slot_limit=?, billing_period_end=NULL "''',
        '''        _ar_ended = []
        for row in lapsed:
            em = (row["email"] or "").lower()
            # AUTO-RENEW-1 (RUL-224d): None for a seller who holds no subscription -- she lapses exactly as before.
            _ar_state = _auto_renew_lapse_state(conn, em, _now_s)
            if _ar_state == "grace":
                continue          # her card is charged for the next month around now; a failed charge ends the wait
            upd = conn.execute(
                "UPDATE users SET seller_tier='free', slot_limit=?, billing_period_end=NULL "''')
s = rep(s, '''            _log.info("AUD-016: paid period over, plan lapsed: %s -> %s", em, new_tier)
        if lapsed:
            conn.commit()
''', '''            _log.info("AUD-016: paid period over, plan lapsed: %s -> %s", em, new_tier)
            if _ar_state:
                _ar_ended.append(em)
        if lapsed:
            conn.commit()
        for _ar_em in _ar_ended:
            _auto_renew_plan_ended(_ar_em)   # AUTO-RENEW-1: switch the subscription off; tell her once if a renewal never came
''')

# ── E. initialize: the tick box. Without it (and while the switch is OFF) the original call runs ──
s = rep(s, '''@app.post("/payment/seller-subscription/initialize")
def init_seller_subscription(email: str, tier: str, callback_url: str = ""):''',
        '''@app.post("/payment/seller-subscription/initialize")
def init_seller_subscription(email: str, tier: str, callback_url: str = "", auto_renew: int = 0, channel: str = ""):''')
s = rep(s, '''    reference = f"ms_sub_{tier}_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=plan["amount_rands"],
        reference=reference,
        metadata={
            "type": "seller_subscription",''', '''    reference = f"ms_sub_{tier}_{uuid.uuid4().hex[:12]}"
    # AUTO-RENEW-1 (RUL-224): a plan code only when the seller left the tick box on, pays by card, the switch
    # is ON and the tier's plan exists. Otherwise None, and the one-off payment below runs exactly as before.
    _ar_plan = _auto_renew_checkout_plan(tier, bool(auto_renew), channel)
    if _ar_plan:
        return _auto_renew_initialize(email, tier, plan, is_downgrade, reference, callback_url, _ar_plan)
    result = payments.initialize_payment(
        email=email,
        amount_rands=plan["amount_rands"],
        reference=reference,
        metadata={
            "type": "seller_subscription",''')

# ── F. verify: after the payment is applied ──────────────────────────────────────────────────────
s = rep(s, '''    _log.info("Seller subscription %s: %s → %s (ref %s, effective: %s)",
              "downgrade scheduled" if is_downgrade else "upgraded",
              email, tier, reference, effective)
    return {"status": "ok", "email": email, "tier": tier, "label": plan["label"],
            "slot_limit": slot_limit, "is_downgrade": is_downgrade, "effective": effective}
''', '''    _log.info("Seller subscription %s: %s → %s (ref %s, effective: %s)",
              "downgrade scheduled" if is_downgrade else "upgraded",
              email, tier, reference, effective)
    # AUTO-RENEW-1 (RUL-224): {} for a one-off payment by a seller who holds no subscription, so the answer
    # below is then exactly what it always was.
    _ar_extra = _auto_renew_after_purchase(email, tier, metadata, result["data"])
    return {"status": "ok", "email": email, "tier": tier, "label": plan["label"],
            "slot_limit": slot_limit, "is_downgrade": is_downgrade, "effective": effective, **_ar_extra}
''')

# ── G. the webhook: the subscription lane first; everything else takes the old path untouched ────
s = rep(s, '''    event_type = event.get("event")
    data = event.get("data", {})

    if event_type == "charge.success":
        reference = data.get("reference", "")
        metadata  = data.get("metadata", {}) or {}''', '''    event_type = event.get("event")
    data = event.get("data", {})

    # AUTO-RENEW-1 (RUL-224): subscription.create, a renewal charge (charge.success carrying one of our plans),
    # invoice.payment_failed, subscription.disable / subscription.not_renew. False for everything else --
    # and for every event while no plan and no subscription exists -- which then runs the path below as before.
    if _auto_renew_webhook(event_type, data):
        return {"status": "ok"}

    if event_type == "charge.success":
        reference = data.get("reference", "")
        metadata  = data.get("metadata", {}) or {}''')

# ── H. the new block, after verify ───────────────────────────────────────────────────────────────
s = rep(s, '''# ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
''', block + '''# AUTO-RENEW-1: the three small tables exist from start-up (the users columns are added in run_migrations).
try:
    _ar_boot = database.get_db()
    try:
        _ar_ensure_tables(_ar_boot)
        _ar_boot.commit()
    finally:
        _ar_boot.close()
except Exception as _ar_boot_e:
    _log.warning("AUTO-RENEW-1 tables not ensured at start-up: %s", _ar_boot_e)


# ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──
''')

# ── I. the subscription answer the plan card reads ───────────────────────────────────────────────
s = rep(s, '''    finally:
        conn.close()
    return {
        "circle_caps_on": bool(_cst and _cst["on"]),''', '''    finally:
        conn.close()
    _sub_out = {
        "circle_caps_on": bool(_cst and _cst["on"]),''')
s = rep(s, '''        "billing_period_end": row["billing_period_end"],
        "usd_per_month": plan["usd"],
    }

@app.get("/sellers/credentials/{listing_id}")''', '''        "billing_period_end": row["billing_period_end"],
        "usd_per_month": plan["usd"],
    }
    # AUTO-RENEW-1 (RUL-224): renewal state for the plan card. {} while the switch is OFF and she holds no
    # subscription, so the answer is then exactly what it always was.
    _sub_out.update(_auto_renew_status(email))
    return _sub_out

@app.get("/sellers/credentials/{listing_id}")''')

# ── J. a plan that ends by her act or ours also stops its subscription ───────────────────────────
s = rep(s, '''            conn.execute("UPDATE users SET pending_downgrade_tier='free' WHERE LOWER(email)=?", (email,))
            conn.commit()
            return {"email": email, "seller_tier": (user["seller_tier"] or "free").lower(),''',
        '''            conn.execute("UPDATE users SET pending_downgrade_tier='free' WHERE LOWER(email)=?", (email,))
            conn.commit()
            # AUTO-RENEW-1: moving to Free also stops the renewal (nothing is charged again). No-op unless she holds a subscription.
            _auto_renew_stop(email, "moving to Free at the end of the paid period")
            return {"email": email, "seller_tier": (user["seller_tier"] or "free").lower(),''')
s = rep(s, '''        res = _plan_changed(conn, email, "free", lowered=True)
        conn.commit()
    finally:
        conn.close()
    return {"email": email, "seller_tier": "free", "slot_limit": free_limit, "effective": "immediate",''',
        '''        res = _plan_changed(conn, email, "free", lowered=True)
        conn.commit()
    finally:
        conn.close()
    _auto_renew_stop(email, "moved to Free", forget=True)   # AUTO-RENEW-1: no-op unless she holds a subscription
    return {"email": email, "seller_tier": "free", "slot_limit": free_limit, "effective": "immediate",''')
s = rep(s, '''        _plan_changed(conn, email, tier, lowered=(new_limit < _old_lim))
        conn.commit()
    finally:
        conn.close()
    return {"email": email, "seller_tier": tier, "slot_limit": new_limit}''',
        '''        _plan_changed(conn, email, tier, lowered=(new_limit < _old_lim))
        conn.commit()
    finally:
        conn.close()
    if _SELLER_SUB_TIERS[tier]["amount_rands"] <= 0:
        # AUTO-RENEW-1: ops moved her to a plan that costs nothing -- her subscription must not keep charging.
        _auto_renew_stop(email, "plan set to %s by ops" % tier, forget=True)
    return {"email": email, "seller_tier": tier, "slot_limit": new_limit}''')
s = rep(s, '''    try:
        result = account_closure.close_account(conn, email, closure_type, cause)
    except LookupError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
''', '''    try:
        result = account_closure.close_account(conn, email, closure_type, cause)
    except LookupError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
    _auto_renew_stop(email, "account closed", forget=True)   # AUTO-RENEW-1: a closed account is never charged again
''')

# ── K. the switch: admin model, /flags, arming ───────────────────────────────────────────────────
s = rep(s, '''    circle_caps:           Optional[bool] = None  # CIRCLE-CAPS-1 (RUL-176): regulars limits 10/50/200, David's switch
''', '''    circle_caps:           Optional[bool] = None  # CIRCLE-CAPS-1 (RUL-176): regulars limits 10/50/200, David's switch
    auto_renew:            Optional[bool] = None  # AUTO-RENEW-1 (RUL-224): paid plans renew automatically, David's switch
''')
s = rep(s, '''        "circle_caps": b("circle_caps"),
        "circle_limits": dict(CIRCLE_LIMITS),''', '''        "circle_caps": b("circle_caps"),
        "circle_limits": dict(CIRCLE_LIMITS),
        # AUTO-RENEW-1 (RUL-224): a row predating the column reads OFF -- the one-off payment is the safe side.
        # auto_renew_tiers = the tiers whose Paystack plan exists; the tick box shows only for those.
        "auto_renew": b("auto_renew"),
        "auto_renew_tiers": (_auto_renew_ready_tiers() if b("auto_renew") else []),''')
s = rep(s, '''            "circle_caps":         b("circle_caps"),   # CIRCLE-CAPS-1: ms.js + quick.html show limits only when this is on
''', '''            "circle_caps":         b("circle_caps"),   # CIRCLE-CAPS-1: ms.js + quick.html show limits only when this is on
            "auto_renew":          b("auto_renew"),    # AUTO-RENEW-1: ms.js shows the tick box and the renewal lines only when this is on
''')
s = rep(s, '''            _log.error("CIRCLE-CAPS-1 grandfathering on arming failed: %s", _ge)
''', '''            _log.error("CIRCLE-CAPS-1 grandfathering on arming failed: %s", _ge)
        # AUTO-RENEW-1 (RUL-224): arming the switch (0 -> 1) makes sure Paystack holds the plan for each paid
        # tier, once. Idempotent. If Paystack can not be reached the switch stays armed, the tick box simply
        # does not show for a tier without a plan (one-off payment as today), and the hourly loop tries again.
        try:
            if data.get("auto_renew") and not int(prior.get("auto_renew") or 0) and row and int(row["auto_renew"] or 0):
                _arp = _auto_renew_sync_plans()
                _log.warning("AUTO-RENEW-1 armed: plans %s", [(p["product"], p["state"]) for p in _arp.get("plans", [])])
        except Exception as _are:
            _log.error("AUTO-RENEW-1 plan step on arming failed (the hourly loop retries): %s", _are)
''')

# ── L. the dashboard tiles (admin-gated launch-metrics) ──────────────────────────────────────────
s = rep(s, '''        out.append(_m("subscriptions", "Paid subscriptions", v, ok, "users.seller_tier", note))
''', '''        out.append(_m("subscriptions", "Paid subscriptions", v, ok, "users.seller_tier", note))

        # AUTO-RENEW-1 (RUL-224): renewals this month, failed renewals, cancellations, auto-renew share.
        # Counted from subscription_events (written only by the renewal lane); each tile is measured or
        # says NOT MEASURED, never a guess (RG-0133).
        _ar_m0 = datetime.now(timezone.utc).strftime("%Y-%m-01T00:00:00Z")
        for _ar_id, _ar_label, _ar_ev in (("renewals_month", "Renewals this month", "renewal"),
                                          ("renewals_failed_month", "Failed renewals this month", "payment_failed"),
                                          ("renewals_cancelled_month", "Renewals cancelled this month", "cancelled")):
            v, ok, note = _count("SELECT COUNT(*) FROM subscription_events WHERE event=? AND created_at >= ?",
                                 (_ar_ev, _ar_m0))
            out.append(_m(_ar_id, _ar_label, v, ok, "subscription_events.event='%s'" % _ar_ev, note))
        _ar_paid, ok1, n1 = _count("SELECT COUNT(*) FROM users WHERE LOWER(COALESCE(seller_tier,'')) IN ('starter','pro') "
                                   "AND billing_period_end IS NOT NULL")
        _ar_auto, ok2, n2 = _count("SELECT COUNT(*) FROM users WHERE LOWER(COALESCE(seller_tier,'')) IN ('starter','pro') "
                                   "AND billing_period_end IS NOT NULL AND paystack_subscription_code IS NOT NULL "
                                   "AND COALESCE(auto_renew,1)=1 AND renewal_failed_at IS NULL")
        if ok1 and ok2 and _ar_paid:
            out.append(_m("auto_renew_share", "Auto-renew share",
                          "%d of %d (%d%%)" % (_ar_auto, _ar_paid, round(100.0 * _ar_auto / _ar_paid)), True,
                          "users.paystack_subscription_code / paid plans"))
        else:
            out.append(_m("auto_renew_share", "Auto-renew share", None, False,
                          "users.paystack_subscription_code / paid plans",
                          (n1 or n2) or "NOT MEASURED — no paid plan is running, so there is no share to state"))
''')

# ── M. the hourly plan loop ──────────────────────────────────────────────────────────────────────
s = rep(s, '''        try:
            _apply_pending_downgrades()
        except Exception as _pe:
            print("PLAN-CHANGE loop error: %s" % _pe)
''', '''        try:
            _apply_pending_downgrades()
        except Exception as _pe:
            print("PLAN-CHANGE loop error: %s" % _pe)
        _auto_renew_hourly()   # AUTO-RENEW-1: retries queued stops; nothing to do while the queue is empty and the switch is OFF
''')

ast.parse(s)
save(P, s, crlf, orig)
py_compile.compile(P, doraise=True)
print("bea_main.py OK (ast + py_compile); lines %d -> %d" % (n0, s.count("\n")))

#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 1/8 -- payments.py: plan + subscription calls (nothing changes for a call without `plan`)."""
import os, py_compile
from patchlib import load, save, rep, root

R = root()
P = os.path.join(R, "payments.py")
s, crlf, orig = load(P)
if "AUTO-RENEW-1" in s:
    print("payments.py already carries AUTO-RENEW-1 -- skipped")
    raise SystemExit(0)

s = rep(s, '''    metadata: dict | None = None,
    callback_url: str | None = None,
) -> dict:
    """
    Create a Paystack transaction and return the authorization URL.

    amount_rands: float  — e.g. 36.0 for 1 Tuppence (R36)
    Returns Paystack's raw response dict.
    """''', '''    metadata: dict | None = None,
    callback_url: str | None = None,
    plan: str | None = None,
    channels: list | None = None,
) -> dict:
    """
    Create a Paystack transaction and return the authorization URL.

    amount_rands: float  — e.g. 36.0 for 1 Tuppence (R36)
    plan / channels: AUTO-RENEW-1 (RUL-224) -- a Paystack plan code makes Paystack open a subscription on
    the first successful card payment. Both default to None, and a call without them sends exactly the
    payload it always sent.
    Returns Paystack's raw response dict.
    """''')

s = rep(s, '''    if callback_url:
        payload["callback_url"] = callback_url

    try:
        resp = requests.post(
            f"{_BASE_URL}/transaction/initialize",''', '''    if callback_url:
        payload["callback_url"] = callback_url
    if plan:
        payload["plan"] = plan              # AUTO-RENEW-1: Paystack charges the plan's own amount
    if channels:
        payload["channels"] = list(channels)

    try:
        resp = requests.post(
            f"{_BASE_URL}/transaction/initialize",''')

s = s.rstrip("\n") + '''


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-RENEW-1 (RUL-224, David 11 Oct 2026; built 12 Oct 2026) -- plans and subscriptions.
#
# Paystack does the charging: a plan per tier is made ONCE by maintenance (never per checkout), a
# checkout started with that plan's code opens a subscription on the first successful card payment,
# and Paystack bills the card every month after that. This module only makes the plan, finds the
# subscription a payment opened, and switches a subscription off or back on. It never charges a
# stored card itself -- there is no charge_authorization call anywhere in this codebase.
#
# Every function returns a plain dict with "ok" and never raises, so a Paystack outage can not
# break a checkout, a webhook or the hourly plan loop.
# ══════════════════════════════════════════════════════════════════════════════
def _api(method: str, path: str, json_body: dict | None = None, params: dict | None = None,
         timeout: int = 20) -> dict:
    """One Paystack call -> its parsed JSON, or {"status": False, "message": ...} on any failure."""
    try:
        resp = requests.request(method, f"{_BASE_URL}{path}", json=json_body, params=params,
                                headers=_headers(), timeout=timeout)
        out = resp.json()
        return out if isinstance(out, dict) else {"status": False, "message": "unexpected reply"}
    except Exception as exc:
        return {"status": False, "message": type(exc).__name__, "unreachable": True}


def create_plan(name: str, amount_rands: float, interval: str = "monthly", currency: str = "ZAR") -> dict:
    """Make one Paystack plan. Returns {"ok": True, "plan_code": "PLN_..."} or {"ok": False, "reason": ...}."""
    body = _api("POST", "/plan", json_body={"name": name, "amount": int(round(amount_rands * 100)),
                                             "interval": interval, "currency": currency})
    code = ((body.get("data") or {}).get("plan_code") or "").strip() if body.get("status") else ""
    if not code:
        return {"ok": False, "reason": str(body.get("message") or "plan not created")[:160]}
    return {"ok": True, "plan_code": code}


def list_plans(max_pages: int = 5) -> dict:
    """Every plan on the Paystack account, so maintenance adopts a plan that already exists
    instead of making a second one. Returns {"ok": True, "plans": [...]} or {"ok": False, "reason": ...}."""
    plans = []
    for page in range(1, max_pages + 1):
        body = _api("GET", "/plan", params={"perPage": 100, "page": page})
        if not body.get("status"):
            return {"ok": False, "reason": str(body.get("message") or "plan list unavailable")[:160]}
        rows = body.get("data") or []
        for p in rows:
            if not isinstance(p, dict):
                continue
            plans.append({"plan_code": (p.get("plan_code") or "").strip(), "name": (p.get("name") or "").strip(),
                          "amount": int(p.get("amount") or 0), "interval": (p.get("interval") or "").strip(),
                          "currency": (p.get("currency") or "").upper(),
                          "gone": bool(p.get("is_deleted") or p.get("is_archived"))})
        if len(rows) < 100:
            break
    return {"ok": True, "plans": plans}


def _plan_code_of(obj) -> str:
    """The plan code inside a Paystack object, whichever of its shapes arrived
    (a plan object, a bare code string, or an event's data with `plan` / `plan_object`)."""
    if isinstance(obj, str):
        return obj.strip()
    if not isinstance(obj, dict):
        return ""
    if obj.get("plan_code"):
        return str(obj["plan_code"]).strip()
    for key in ("plan", "plan_object"):
        inner = obj.get(key)
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
        if isinstance(inner, dict) and inner.get("plan_code"):
            return str(inner["plan_code"]).strip()
    return ""


def find_subscription(customer_email: str, plan_code: str) -> dict:
    """The subscription Paystack opened for this customer on this plan.

    Returns {"ok": True, "subscription_code", "email_token", "status", "next_payment_date"}, or
    {"ok": False, "reason": ...} when there is none yet (Paystack opens it a moment after the payment;
    the subscription.create webhook then stores it). Only a subscription that can still charge
    (active / non-renewing / attention) is returned."""
    if not customer_email or not plan_code:
        return {"ok": False, "reason": "missing customer or plan"}
    body = _api("GET", "/customer/" + _quote(customer_email.strip().lower(), safe=""))
    if not body.get("status"):
        return {"ok": False, "reason": str(body.get("message") or "customer lookup failed")[:160]}
    subs = (body.get("data") or {}).get("subscriptions") or []
    live = [x for x in subs if isinstance(x, dict)
            and (x.get("status") or "").lower() in ("active", "non-renewing", "attention")
            and x.get("subscription_code")]
    live.sort(key=lambda x: str(x.get("createdAt") or x.get("created_at") or ""), reverse=True)
    for cand in live[:5]:
        code = _plan_code_of(cand)
        full = cand
        if not code or not cand.get("email_token"):
            # the customer record can carry the plan as a bare id: ask for the subscription itself
            got = _api("GET", "/subscription/" + _quote(str(cand["subscription_code"]), safe=""))
            full = (got.get("data") or {}) if got.get("status") else {}
            code = _plan_code_of(full) or code
        if code == plan_code and full.get("subscription_code") and full.get("email_token"):
            return {"ok": True, "subscription_code": str(full["subscription_code"]),
                    "email_token": str(full["email_token"]),
                    "status": (full.get("status") or "").lower(),
                    "next_payment_date": full.get("next_payment_date")}
    return {"ok": False, "reason": "no subscription on this plan yet"}


def disable_subscription(code: str, token: str) -> dict:
    """Stop a subscription renewing (Paystack: status non-renewing, then cancelled on its next payment
    date). Returns {"ok": True, "already": bool} or {"ok": False, "reason": ..., "unreachable": bool}.
    A subscription Paystack reports as already inactive counts as stopped."""
    if not code or not token:
        return {"ok": False, "reason": "missing subscription code or token", "unreachable": False}
    body = _api("POST", "/subscription/disable", json_body={"code": code, "token": token})
    if body.get("status"):
        return {"ok": True, "already": False}
    msg = str(body.get("message") or "")
    if "already inactive" in msg.lower():
        return {"ok": True, "already": True}
    return {"ok": False, "reason": msg[:160] or "not disabled", "unreachable": bool(body.get("unreachable"))}


def enable_subscription(code: str, token: str) -> dict:
    """Switch a stopped subscription back on (only possible before its next payment date).
    Returns {"ok": True} or {"ok": False, "reason": ..., "unreachable": bool}."""
    if not code or not token:
        return {"ok": False, "reason": "missing subscription code or token", "unreachable": False}
    body = _api("POST", "/subscription/enable", json_body={"code": code, "token": token})
    if body.get("status"):
        return {"ok": True}
    return {"ok": False, "reason": str(body.get("message") or "not enabled")[:160],
            "unreachable": bool(body.get("unreachable"))}
'''

save(P, s, crlf, orig)
py_compile.compile(P, doraise=True)
print("payments.py OK (py_compile)")

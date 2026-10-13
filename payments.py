"""
payments.py — Paystack integration for TrustSquare / TrustSquare (PTY) Ltd
-----------------------------------------------------------------------------
Reads PAYSTACK_SECRET_KEY from the server's .env file.

Key behaviour:
  - Works transparently in test mode (sk_test_...) and live mode (sk_live_...)
  - No key ever touches the codebase — loaded from environment only
  - Used by bea_main.py endpoints: /payment/initialize, /payment/verify,
    /payment/test, /wishlist/subscription/initialize, /wishlist/subscription/verify

Functions exported:
  initialize_payment(email, amount_rands, reference, metadata) → dict
  verify_payment(reference) → dict
  get_balance() → dict
"""

import os
import re
import requests
from urllib.parse import quote as _quote

# AUD-002 (4 Oct 2026 audit): a payment reference is plain characters only. The verify URL used to be built
# from the caller's raw text, so "ref#a", "ref?x=1" or "../verify/ref" all reached the SAME paid transaction
# while our once-only key saw a new string each time -- one payment, credited again and again.
_REFERENCE_RE = re.compile(r"^[A-Za-z0-9_.=-]{1,100}$")


def valid_reference(reference) -> bool:
    """True only for a reference made of plain characters (letters, digits, _ . = -), 1-100 long."""
    return isinstance(reference, str) and bool(_REFERENCE_RE.fullmatch(reference))   # fullmatch: "$" alone lets a trailing newline through

# ── Key ──────────────────────────────────────────────────────────────────────

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "")

if not PAYSTACK_SECRET_KEY:
    import logging
    logging.getLogger("payments").warning(
        "PAYSTACK_SECRET_KEY not set in environment — all payment calls will fail. "
        "Add it to /var/www/marketsquare/.env and restart the service."
    )

_BASE_URL = "https://api.paystack.co"
_HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


def _headers():
    """Return fresh headers — picks up key even if env was set after import."""
    key = os.getenv("PAYSTACK_SECRET_KEY", PAYSTACK_SECRET_KEY)
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


# ── Core API calls ────────────────────────────────────────────────────────────

def initialize_payment(
    email: str,
    amount_rands: float,
    reference: str,
    metadata: dict | None = None,
    callback_url: str | None = None,
    plan: str | None = None,
    channels: list | None = None,
    invoice_limit: int | None = None,
) -> dict:
    """
    Create a Paystack transaction and return the authorization URL.

    amount_rands: float  — e.g. 36.0 for 1 Tuppence (R36)
    plan / channels: AUTO-RENEW-1 (RUL-224) -- a Paystack plan code makes Paystack open a subscription on
    the first successful card payment. Both default to None, and a call without them sends exactly the
    payload it always sent.
    Returns Paystack's raw response dict.
    """
    amount_kobo = int(round(amount_rands * 100))  # Paystack uses smallest currency unit (kobo/cents)

    payload: dict = {
        "email": email,
        "amount": amount_kobo,
        "reference": reference,
        "currency": "ZAR",
    }
    if metadata:
        payload["metadata"] = metadata
    if callback_url:
        payload["callback_url"] = callback_url
    if plan:
        payload["plan"] = plan              # AUTO-RENEW-1: Paystack charges the plan's own amount
    if channels:
        payload["channels"] = list(channels)
    if plan and invoice_limit:
        payload["invoice_limit"] = int(invoice_limit)   # QA-RED-AR-3: Paystack stops the subscription after this many charges

    try:
        resp = requests.post(
            f"{_BASE_URL}/transaction/initialize",
            json=payload,
            headers=_headers(),
            timeout=15,
        )
        return resp.json()
    except Exception as exc:
        return {"status": False, "message": str(exc)}


def verify_payment(reference: str) -> dict:
    """
    Verify a transaction by reference.
    Returns Paystack's raw response dict.
    Check result["status"] and result["data"]["status"] == "success".
    """
    # AUD-002: refuse anything but a plain reference, encode it anyway, and only accept Paystack's answer
    # when the reference it returns is exactly the one asked for.
    if not valid_reference(reference):
        return {"status": False, "message": "invalid reference"}
    try:
        resp = requests.get(
            f"{_BASE_URL}/transaction/verify/{_quote(reference, safe='')}",
            headers=_headers(),
            timeout=15,
        )
        out = resp.json()
    except Exception as exc:
        return {"status": False, "message": str(exc)}
    data = out.get("data") if isinstance(out, dict) else None
    if out.get("status") and (not isinstance(data, dict) or data.get("reference") != reference):
        return {"status": False, "message": "reference mismatch"}
    return out


def get_balance() -> dict:
    """
    Fetch account balance — used by GET /payment/test to confirm the key works.
    Returns Paystack's raw response dict.
    """
    try:
        resp = requests.get(
            f"{_BASE_URL}/balance",
            headers=_headers(),
            timeout=15,
        )
        return resp.json()
    except Exception as exc:
        return {"status": False, "message": str(exc)}


def verify_webhook_signature(payload_bytes: bytes, signature: str) -> bool:
    """
    Validate a Paystack webhook POST using HMAC-SHA512.

    payload_bytes: raw request body bytes
    signature: value of the X-Paystack-Signature header

    Returns True if valid. Paystack signs webhooks with the account SECRET KEY (there is no
    separate webhook secret in its dashboard). AUD-022 (4 Oct 2026 audit): PAYSTACK_WEBHOOK_SECRET
    is honoured if set (on the server it holds the secret key -- checked 4 Oct without reading it),
    and otherwise the secret key itself is used, so an unset variable can never silently refuse
    every webhook. The header is compared as bytes, so a non-ASCII header is refused, not a crash.
    """
    import hmac
    import hashlib

    secret = os.getenv("PAYSTACK_WEBHOOK_SECRET", "") or os.getenv("PAYSTACK_SECRET_KEY", "") or PAYSTACK_SECRET_KEY
    if not secret or not signature:
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha512,
    ).hexdigest()
    try:
        return hmac.compare_digest(expected.encode("ascii"), str(signature).strip().encode("utf-8"))
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# BANKRESOLVE-1 (27 Sep 2026) — RUL-176/178.
#
# Ask the bank, through Paystack, for the name that stands against an account number.
# This is the only place in the codebase that handles a customer account number, and it
# handles it as an argument that is never returned, never logged and never stored: the
# caller gets {"ok": bool, "account_name": str} and writes only a verdict from it.
#
# Deliberately NOT a free call. Paystack charges per account resolution, so:
#   - one call per Seller per attempt, never a loop or a retry;
#   - a transport failure returns ok=False and the caller records NOT MEASURED, never a
#     failed match, so a vendor outage does not cost a Seller points;
#   - nothing here caches the number in order to "save" a later call.
# David approved the paid lane on 27 Sep 2026 (option 4 of four).
#
# NOTE ON LOGGING: this function must never log `account_number`, and must never put it
# in an exception it raises. scripts/test_identity_verdicts.py reads this source and
# fails if the name appears in a logging or raise statement.
# ══════════════════════════════════════════════════════════════════════════════
def resolve_account_name(account_number: str, bank_code: str) -> dict:
    """Resolve an account number to the account holder name the bank holds.

    Returns {"ok": True, "account_name": "..."} or {"ok": False, "reason": "..."}.
    The reason never contains the account number.
    """
    try:
        resp = requests.get(
            f"{_BASE_URL}/bank/resolve",
            params={"account_number": account_number, "bank_code": bank_code},
            headers=_headers(),
            timeout=20,
        )
        body = resp.json()
    except Exception:
        # The exception text can carry the query string, so it is deliberately discarded
        # rather than echoed — a leak into a log is exactly what this lane exists to avoid.
        return {"ok": False, "reason": "bank name lookup unreachable"}
    if not body.get("status"):
        return {"ok": False, "reason": "bank could not confirm that account"}
    name = ((body.get("data") or {}).get("account_name") or "").strip()
    if not name:
        return {"ok": False, "reason": "bank returned no account name"}
    return {"ok": True, "account_name": name}


def payment_account_name(verify_data: dict) -> str:
    """PAYNAME-1 (27 Sep 2026) — the account or sender name Paystack reports for a
    payment that already happened, or '' when it reports none.

    Paystack returns a usable name for EFT / DebiCheck and for some mobile-money and
    bank channels; for most card charges it returns none. So this returns '' far more
    often than not, and the caller MUST treat '' as "not measured" rather than as a
    mismatch — a Seller who paid by card has not failed a check, she was never checked.
    """
    d = verify_data or {}
    auth = d.get("authorization") or {}
    for cand in (auth.get("account_name"), auth.get("sender_name"),
                 auth.get("receiver_bank_account_name"), d.get("sender_name"),
                 (d.get("customer") or {}).get("account_name")):
        if isinstance(cand, str) and cand.strip():
            return cand.strip()
    return ""


def list_banks(currency: str = "ZAR") -> dict:
    """Banks Paystack can resolve for, as [{"name","code"}].

    BANKRESOLVE-1 (27 Sep 2026): the resolve call needs Paystack's own bank CODE, not a
    bank name. Hardcoding a code table would be inventing data we cannot verify and would
    rot silently the first time Paystack changed one, so the list is fetched and the app's
    picker is built from it. A failure returns ok=False and the picker says it cannot load
    rather than offering a guess.
    """
    try:
        resp = requests.get(
            f"{_BASE_URL}/bank",
            params={"currency": currency},
            headers=_headers(),
            timeout=20,
        )
        body = resp.json()
    except Exception as exc:
        return {"ok": False, "reason": str(exc)[:120]}
    if not body.get("status"):
        return {"ok": False, "reason": (body.get("message") or "bank list unavailable")[:120]}
    banks = []
    for b in (body.get("data") or []):
        name, code = (b.get("name") or "").strip(), (b.get("code") or "").strip()
        if name and code:
            banks.append({"name": name, "code": code})
    banks.sort(key=lambda x: x["name"].lower())
    return {"ok": True, "banks": banks}


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

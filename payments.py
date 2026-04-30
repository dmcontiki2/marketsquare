"""
payments.py — Paystack integration for MarketSquare / TrustSquare (PTY) Ltd
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
import requests

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
) -> dict:
    """
    Create a Paystack transaction and return the authorization URL.

    amount_rands: float  — e.g. 36.0 for 1 Tuppence (R36)
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
    try:
        resp = requests.get(
            f"{_BASE_URL}/transaction/verify/{reference}",
            headers=_headers(),
            timeout=15,
        )
        return resp.json()
    except Exception as exc:
        return {"status": False, "message": str(exc)}


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

    Returns True if valid. PAYSTACK_WEBHOOK_SECRET must be set in .env.
    """
    import hmac
    import hashlib

    secret = os.getenv("PAYSTACK_WEBHOOK_SECRET", "")
    if not secret:
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

"""
id_verify_provider.py — swappable adapter for South African ID verification
against the DHA National Population Register (NPR).

ID-NPR-1 · 21 August 2026 · David's ruling.

WHY AN ADAPTER, NOT A DIRECT INTEGRATION
----------------------------------------
SUPPLIER FALLBACK DOCTRINE (CLAUDE.md, 1 Aug 2026, written after the Amadeus
shutdown and the ~$360 Google Places bill): no external supplier may ever be
load-bearing. The app reads OUR OWN verification ledger in OUR OWN schema;
suppliers are swappable adapters behind it. If a provider dies, existing green
ticks keep standing — only NEW checks stop, and they fail CLOSED (no tick, no
charge), never open.

WHAT THIS DOES AND DOES NOT PROVE
---------------------------------
A positive NPR result proves the ID number exists in the population register
and that the surname/initials on record match what was submitted. It does NOT
prove the person submitting it is the holder. Closing that gap needs the DHA
photo-retrieval or fingerprint product plus a live selfie match — a strictly
higher tier, deliberately left as a future lane (see PROVIDERS below).

Therefore the copy attached to a pass must say what it means. "ID verified
against the Home Affairs population register" is true. "This person is who
they say they are" is NOT, and must never appear in the UI.

COST (checked 21 Aug 2026)
--------------------------
  DHA direct        R10 real-time / R1 off-peak batch (private sector)
  Aggregator retail ~R27-R30 per check
  Seller pays       1 Tuppence = USD $2 fixed (PRICING_CANON.md:52)

A per-check lookup is a FLAT, CAPPABLE cost, which is the only shape of
external cost the 1 Aug pricing ruling permits. There is no percentage of
anything here, and there must never be.

DHA access is not open self-service — it is reached through an accredited
party. Expect to start on an aggregator and move direct at volume. That is
precisely why this file exists.

CONFIGURATION
-------------
  ID_VERIFY_PROVIDER   provider key (default 'stub' — disabled)
  ID_VERIFY_API_KEY    provider credential (never committed; server env only)
  ID_VERIFY_BASE_URL   override endpoint for the chosen provider

With no provider configured the module reports unavailable and the caller
must NOT charge. Fail closed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


# ── Result contract ──────────────────────────────────────────────────────────

@dataclass
class NPRResult:
    """Outcome of one NPR check. `ok` False + `billable` False = never charge."""
    ok:        bool = False          # provider answered conclusively
    verified:  bool = False          # NPR says this ID exists and names match
    billable:  bool = False          # a real query was consumed at the supplier
    provider:  str  = 'stub'
    reference: str  = ''             # supplier's transaction ref, for audit
    reason:    str  = ''             # human-readable, safe to log
    raw:       dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            'ok': self.ok, 'verified': self.verified, 'billable': self.billable,
            'provider': self.provider, 'reference': self.reference,
            'reason': self.reason,
        }


# ── Provider registry ────────────────────────────────────────────────────────
# Add a provider by writing a _check_<key> function and registering it here.
# Keep 'stub' first and default so an unconfigured server cannot spend money.
PROVIDERS = {
    'stub':      'Disabled — no provider configured. Never charges.',
    # 'verifynow': DHA NPR via aggregator. ~R27-30/check.
    # 'didit':     DHA NPR + photo retrieval + fingerprint. USD pricing.
    # 'dha':       Direct, R10 real-time / R1 batch. Requires accreditation.
}


def provider_name() -> str:
    return (os.getenv('ID_VERIFY_PROVIDER') or 'stub').strip().lower()


def is_available() -> bool:
    """True only when a real provider is configured AND credentialled."""
    p = provider_name()
    if p == 'stub' or p not in PROVIDERS:
        return False
    return bool(os.getenv('ID_VERIFY_API_KEY'))


def status() -> dict:
    """Panel probe payload — a dead feed must turn red, never go silent."""
    p = provider_name()
    return {
        'provider':   p,
        'known':      p in PROVIDERS,
        'configured': bool(os.getenv('ID_VERIFY_API_KEY')),
        'available':  is_available(),
        'note':       PROVIDERS.get(p, 'Unknown provider key'),
    }


# ── The one call the app makes ───────────────────────────────────────────────

def verify_id(id_number: str, full_name: str, timeout: int = 20) -> NPRResult:
    """
    Check `id_number` against the NPR. NEVER raises — a supplier problem must
    degrade to 'no tick', not a 500 on the seller's screen.

    The caller must charge ONLY when result.billable is True.
    """
    p = provider_name()

    if not is_available():
        return NPRResult(
            ok=False, verified=False, billable=False, provider=p,
            reason='ID verification is not enabled on this server '
                   '(no provider configured).'
        )

    try:
        fn = globals().get(f'_check_{p}')
        if fn is None:
            return NPRResult(ok=False, billable=False, provider=p,
                             reason=f'No implementation for provider {p!r}.')
        return fn(id_number, full_name, timeout)
    except Exception as e:                    # noqa: BLE001 — must never bubble
        return NPRResult(ok=False, verified=False, billable=False, provider=p,
                         reason=f'Provider error ({type(e).__name__}) — '
                                f'no charge made.')


def _check_stub(id_number: str, full_name: str, timeout: int) -> NPRResult:
    """Never reachable via verify_id (is_available gates it). Here for tests."""
    return NPRResult(ok=False, verified=False, billable=False, provider='stub',
                     reason='Stub provider — verification disabled.')

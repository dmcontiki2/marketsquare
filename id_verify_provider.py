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
    'stub':  'Disabled — no provider configured. Never charges.',
    'didit': ('DHA National Population Register via Didit '
              '(zaf_africa_national_id). $1.10 per CONCLUSIVE query, '
              'pay-per-success, no contract, self-service key.'),
    # 'verifynow': DHA NPR via SA aggregator, ~R27-30/check. Not implemented.
    # 'dha':       Direct, R10 real-time / R1 batch. Needs accreditation.
}

# ── Didit ────────────────────────────────────────────────────────────────────
DIDIT_URL = 'https://verification.didit.me/v3/database-validation/'
DIDIT_SERVICE = 'zaf_africa_national_id'


def _dob_from_sa_id(id_number: str) -> str:
    '''
    Derive YYYY-MM-DD from the first 6 digits of a 13-digit SA ID (YYMMDD).

    Didit requires date_of_birth, and asking a seller to retype what is
    already encoded in their ID number is an extra field to get wrong. The
    century pivot: SA IDs are YY only, so 00-29 is read as 2000s and 30-99 as
    1900s. That is the standard convention and is safe until 2030 — a person
    born in 2030 cannot be an adult seller before then.
    '''
    digits = ''.join(ch for ch in (id_number or '') if ch.isdigit())
    if len(digits) < 6:
        return ''
    yy, mm, dd = digits[0:2], digits[2:4], digits[4:6]
    try:
        y, m, d = int(yy), int(mm), int(dd)
    except ValueError:
        return ''
    if not (1 <= m <= 12 and 1 <= d <= 31):
        return ''
    century = 2000 if y <= 29 else 1900
    return f'{century + y:04d}-{m:02d}-{d:02d}'


# Surname particles. A naive "last word is the surname" split turns
# "Johannes van der Merwe" into surname "Merwe", which comes back from the
# register as PARTIAL_MATCH — the seller is charged and refused a tick for a
# bug in our string handling. A large share of South African surnames carry
# one of these, so this is a correctness requirement here, not a nicety.
_SURNAME_PARTICLES = {
    'van', 'von', 'de', 'den', 'der', 'du', 'da', 'dos', 'das', 'di',
    'le', 'la', 'ter', 'te', 'ten', 'op', 'in', 'aan', 'aus', 'zu',
    'janse', 'jansen', 'nel',   # 'janse van', 'jansen van'
}


def _split_name(full_name: str) -> tuple[str, str]:
    """
    Split a full name into (first_names, surname), keeping particles with the
    surname. Walks backwards from the end while the preceding token is a
    particle, so "Johannes Petrus van der Merwe" -> ("Johannes Petrus",
    "van der Merwe").
    """
    parts = [p for p in (full_name or '').replace(',', ' ').split() if p]
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], parts[0]

    i = len(parts) - 1                      # index where the surname starts
    while i > 1 and parts[i - 1].lower().strip('.') in _SURNAME_PARTICLES:
        i -= 1
    # Never swallow the only given name.
    if i < 1:
        i = 1
    return ' '.join(parts[:i]), ' '.join(parts[i:])


def _check_didit(id_number: str, full_name: str, timeout: int) -> NPRResult:
    '''
    One DHA lookup via Didit.

    BILLING (their docs): charged only on a CONCLUSIVE result. Not charged
    when the registry is unreachable, when required fields are missing, or
    when the request is rejected before reaching the source. `billable`
    mirrors that exactly, so we never pass on a cost we did not incur.

    OUTCOMES:
      MATCH                       -> verified
      PARTIAL_MATCH               -> NOT verified. The ID exists but a name or
                                     DOB field did not match, which is exactly
                                     the shape of someone using an ID that is
                                     not theirs. Conclusive, so billable.
      NO_MATCH / DOCUMENT_NOT_FOUND -> not verified, conclusive, billable
      anything else / transport error -> not billable
    '''
    import requests

    api_key = (os.getenv('ID_VERIFY_API_KEY') or '').strip()
    base = (os.getenv('ID_VERIFY_BASE_URL') or DIDIT_URL).strip()
    digits = ''.join(ch for ch in (id_number or '') if ch.isdigit())
    first, last = _split_name(full_name)
    dob = _dob_from_sa_id(digits)

    if not digits or not first or not dob:
        return NPRResult(ok=False, billable=False, provider='didit',
                         reason='Missing or unusable ID number / name / date '
                                'of birth — not sent, not charged.')

    fields = {
        'issuing_state': 'ZAF',
        'services':      DIDIT_SERVICE,
        'first_name':    first,
        'last_name':     last,
        'date_of_birth': dob,
        'national_id':   digits,
    }
    try:
        resp = requests.post(
            base,
            headers={'x-api-key': api_key},
            files={k: (None, v) for k, v in fields.items()},   # multipart
            timeout=timeout,
        )
    except Exception as e:                      # noqa: BLE001
        return NPRResult(ok=False, billable=False, provider='didit',
                         reason=f'Could not reach the verification service '
                                f'({type(e).__name__}). No charge.')

    if resp.status_code != 200:
        return NPRResult(ok=False, billable=False, provider='didit',
                         reason=f'Verification service returned HTTP '
                                f'{resp.status_code}. No charge.')
    try:
        body = resp.json()
    except Exception:
        return NPRResult(ok=False, billable=False, provider='didit',
                         reason='Unreadable response from the verification '
                                'service. No charge.')

    vals = body.get('validations') or []
    code = (vals[0].get('outcome_code') if vals else '') or ''
    code = str(code).upper()
    ref = str(body.get('request_id') or '')

    CONCLUSIVE = {'MATCH', 'PARTIAL_MATCH', 'NO_MATCH', 'DOCUMENT_NOT_FOUND'}
    if code not in CONCLUSIVE:
        return NPRResult(ok=False, billable=False, provider='didit',
                         reference=ref,
                         reason=f'Inconclusive result ({code or "unknown"}). '
                                f'No charge.')

    verified = (code == 'MATCH')
    reasons = {
        'MATCH':              'Confirmed against the Home Affairs register.',
        'PARTIAL_MATCH':      'The ID number exists but the name or date of '
                              'birth did not match the register.',
        'NO_MATCH':           'The register returned no match for these details.',
        'DOCUMENT_NOT_FOUND': 'This ID number was not found in the register.',
    }
    return NPRResult(ok=True, verified=verified, billable=True,
                     provider='didit', reference=ref,
                     reason=reasons[code],
                     raw={'outcome_code': code,
                          'match_type': body.get('match_type')})


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

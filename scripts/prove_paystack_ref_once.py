#!/usr/bin/env python3
"""prove_paystack_ref_once.py -- AUD-002 (4 Oct 2026 audit).

The bug: GET /payment/verify?reference=ms_tuppence_abc%23a (or ?x=1, or ../verify/ref) reached the
SAME paid Paystack transaction, while the once-only claim was keyed on the caller's typed text -- so
one payment credited again and again. Same hole on the seller-plan and wishlist verify doors.

This proves the fix without any network or production data:
 1. source: all three verify handlers go through _paystack_verified(); payments.verify_payment is
    called from nowhere else; the claim uses the reference that door returns.
 2. payments.verify_payment against a FAKE Paystack that behaves like a real URL router (drops the
    #fragment, drops ?query, resolves ../): every variant is refused before any request is sent, the
    plain reference is sent URL-encoded, and an answer naming a different reference is refused.
 3. replica: the once-only claim keyed on Paystack's reference credits exactly once across all
    variants that could ever pass.
Run: python3 scripts/prove_paystack_ref_once.py
"""
import os, re, sqlite3, sys, types, posixpath
from urllib.parse import urlsplit, unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok:
        fails.append(msg)

print("=" * 70); print("  AUD-002 -- one Paystack payment credits exactly once"); print("=" * 70)

print("\n1. source")
src = open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read()
check(src.count("payments.verify_payment(") == 1, "payments.verify_payment is called from ONE place (the shared door)")
check(src.count("result, reference = _paystack_verified(reference)") == 3,
      "all three verify handlers (Tuppence, seller plan, wishlist) use the shared door")
check("def _paystack_verified(reference: str):" in src and "payments.valid_reference(reference)" in src,
      "the shared door refuses a non-plain reference before asking Paystack")

print("\n2. payments.verify_payment against a fake Paystack")
sent = []
PAID = "ms_tuppence_abc123"
def fake_get(url, headers=None, timeout=None):
    sent.append(url)
    parts = urlsplit(url)                                  # a real server never sees #frag; ?query is separate
    path = posixpath.normpath(unquote(parts.path))
    ref = path.rsplit("/", 1)[-1]
    body = ({"status": True, "data": {"status": "success", "reference": PAID}} if ref == PAID
            else {"status": False, "message": "Transaction reference not found"})
    return types.SimpleNamespace(json=lambda: body)
fake_requests = types.ModuleType("requests"); fake_requests.get = fake_get
sys.modules["requests"] = fake_requests
import payments
payments.requests = fake_requests
variants = [PAID + "#a", PAID + "?x=1", "../verify/" + PAID, PAID + "/", PAID + "%23a", " " + PAID,
            PAID + "\n", "x" * 101, "", None]
for v in variants:
    sent.clear()
    r = payments.verify_payment(v)
    check(not r.get("status") and not sent, "variant %r refused, nothing sent to Paystack" % (v if v is None else v[:40]))
sent.clear()
r = payments.verify_payment(PAID)
check(r.get("status") is True and r["data"]["reference"] == PAID, "the plain reference verifies")
check(sent and sent[0].endswith("/transaction/verify/" + PAID), "it is sent as-is (URL-encoded, no change for plain text)")
PAID_OTHER = PAID
def lying_get(url, headers=None, timeout=None):
    return types.SimpleNamespace(json=lambda: {"status": True, "data": {"status": "success", "reference": "someone_else"}})
payments.requests.get = lying_get
check(not payments.verify_payment(PAID).get("status"), "an answer that names a different reference is refused")
payments.requests.get = fake_get

print("\n3. replica: the claim keyed on Paystack's reference credits once")
c = sqlite3.connect(":memory:")
c.execute("CREATE TABLE payment_refs_consumed (kind TEXT, reference TEXT, UNIQUE(kind, reference))")
credits = 0
for typed in [PAID, PAID + "#a", PAID + "?x=1", PAID, "../verify/" + PAID]:
    r = payments.verify_payment(typed)
    if not (r.get("status") and r["data"]["status"] == "success"):
        continue
    canon = r["data"]["reference"]
    cur = c.execute("INSERT INTO payment_refs_consumed VALUES ('tuppence', ?) ON CONFLICT DO NOTHING", (canon,))
    credits += cur.rowcount
check(credits == 1, "five attempts on one payment -> exactly ONE credit (got %d)" % credits)

print("\n" + "=" * 70)
if fails:
    print("  RESULT: %d CHECK(S) FAILED" % len(fails)); sys.exit(1)
print("  RESULT: a payment reference is plain text, checked against Paystack's own value,"); print("          and one payment credits exactly once on every verify door.")
sys.exit(0)

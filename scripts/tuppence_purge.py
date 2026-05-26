"""
tuppence_purge.py — removes all Tuppence refund language from marketsquare.html.
Run from sandbox: python3 /tmp/tuppence_purge.py
Applies 6 targeted replacements per NEXT_SESSION_TUPPENCE_NO_REFUND.md.
"""
import re

PATH = '/sessions/affectionate-loving-ramanujan/mnt/MarketSquare/marketsquare.html'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)
changes = []

# ────────────────────────────────────────────────────────────────────
# Edit 1 — FICA-failure refund (L1958 area)
# "If verification fails ... Tuppence charged is refunded."
# ────────────────────────────────────────────────────────────────────
OLD1 = (
    'After first Introduction acceptance: FICA-compliant identity verification is initiated '
    'within 24 hours. This must be completed within 5 business days. If verification fails or '
    'is not completed, the Introduction is cancelled and any Tuppence charged is refunded.'
)
NEW1 = (
    'After first Introduction acceptance: FICA-compliant identity verification is initiated '
    'within 24 hours. This must be completed within 5 business days. If verification fails or '
    'is not completed, the Introduction is cancelled. Tuppence already spent remains spent.'
)
if OLD1 in content:
    content = content.replace(OLD1, NEW1, 1)
    changes.append('Edit 1 — FICA-failure refund rewritten')
else:
    changes.append('Edit 1 — NOT FOUND (already patched or text differs)')

# ────────────────────────────────────────────────────────────────────
# Edit 2 — "1T is refunded to the Buyer's account" on seller decline (L1999 area)
# ────────────────────────────────────────────────────────────────────
OLD2 = (
    'If the Seller declines or does not respond within the applicable window, '
    'the 1T is refunded to the Buyer’s account.'
)
NEW2 = (
    'If the Seller declines or does not respond within the applicable window, '
    'the Introduction closes. Tuppence spent on the request is consumed and is not refundable. '
    'This is the platform’s spam-prevention mechanism.'
)
# Also try with plain apostrophe
OLD2b = (
    "If the Seller declines or does not respond within the applicable window, "
    "the 1T is refunded to the Buyer's account."
)
if OLD2 in content:
    content = content.replace(OLD2, NEW2, 1)
    changes.append('Edit 2 — seller-decline refund rewritten (unicode apostrophe)')
elif OLD2b in content:
    content = content.replace(OLD2b, NEW2, 1)
    changes.append('Edit 2 — seller-decline refund rewritten (plain apostrophe)')
else:
    changes.append('Edit 2 — NOT FOUND')

# ────────────────────────────────────────────────────────────────────
# Edit 3 — 7-day cooling-off refund (L2042 area)
# ────────────────────────────────────────────────────────────────────
OLD3 = (
    'Upon cancellation within 7 days, the 1T charged is refunded to your account within 3 business days. '
    'The cooling-off right does not apply once both parties have accepted the Introduction and are in active communication.'
)
NEW3 = (
    'Tuppence spent on an Introduction request is consumed at the time of request. '
    'The Consumer Protection Act s 16 cooling-off right applies to direct marketing transactions only; '
    'Tuppence purchases are buyer-initiated and are not subject to a cooling-off refund right. '
    'Tuppence is non-refundable under any circumstance.'
)
if OLD3 in content:
    content = content.replace(OLD3, NEW3, 1)
    changes.append('Edit 3 — 7-day cooling-off refund rewritten')
else:
    changes.append('Edit 3 — NOT FOUND')

# ────────────────────────────────────────────────────────────────────
# Edit 4 — AI feature refund exception (L2058 area)
# Remove the "except where a material technical fault..." carve-out
# ────────────────────────────────────────────────────────────────────
OLD4 = (
    'AI Feature Tuppence is non-refundable once an AI interaction is completed and a response is delivered, '
    'except where a material technical fault prevented delivery of the response.'
)
NEW4 = (
    'AI Feature Tuppence is non-refundable under any circumstance once an AI request is submitted. '
    'Submitting an AI request consumes the Tuppence regardless of the output quality or outcome.'
)
if OLD4 in content:
    content = content.replace(OLD4, NEW4, 1)
    changes.append('Edit 4 — AI feature refund exception removed')
else:
    changes.append('Edit 4 — NOT FOUND')

# ────────────────────────────────────────────────────────────────────
# Edit 5 — Section header rename: "Fees, Refunds, ..." → "Fees, Subscriptions & Payment"
#           AND replace entire §6.3 Refunds section with No-Refund paragraph
# ────────────────────────────────────────────────────────────────────
OLD5_HEADER = '6. Fees, Refunds, Subscriptions &amp; Payment'
NEW5_HEADER = '6. Fees, Subscriptions &amp; Payment'
if OLD5_HEADER in content:
    content = content.replace(OLD5_HEADER, NEW5_HEADER, 1)
    changes.append('Edit 5a — section 6 header renamed (removed Refunds)')
else:
    changes.append('Edit 5a — section 6 header NOT FOUND')

# Replace the entire §6.3 Refunds block (header + 5 bullets + final sentence)
OLD5_SECTION = (
    '<div style="font-weight:700;font-size:13px;color:rgba(200,135,58,.9);margin:18px 0 6px;text-transform:uppercase;letter-spacing:.8px;border-top:1px solid rgba(255,255,255,.08);padding-top:14px;"><strong style="color:rgba(255,255,255,.75);">6.3 Refunds</strong></div>\n'
    '<div style="margin:5px 0;font-size:11px;">Refunds of Tuppence are available in the following circumstances only:</div>\n'
    '<div style="margin:5px 0;font-size:11px;">Seller did not respond to the Introduction within the 48-hour window (auto-refund);</div>\n'
    '<div style="margin:5px 0;font-size:11px;">Seller declined the Introduction (auto-refund within 3 business days);</div>\n'
    '<div style="margin:5px 0;font-size:11px;">Buyer cancels within 7 days of the request before Seller acceptance (per Section 5.4);</div>\n'
    '<div style="margin:5px 0;font-size:11px;">The Platform experiences a verified technical fault preventing Introduction delivery (refund within 5 business days of confirmed fault);</div>\n'
    '<div style="margin:5px 0;font-size:11px;">The Platform terminates your account for convenience (see Section 14.3).</div>\n'
    '<div style="margin:5px 0;font-size:11px;">Tuppence already credited to a Seller’s Wallet upon acceptance is not refundable, except as required by South African law.</div>'
)
NEW5_SECTION = (
    '<div style="font-weight:700;font-size:13px;color:rgba(200,135,58,.9);margin:18px 0 6px;text-transform:uppercase;letter-spacing:.8px;border-top:1px solid rgba(255,255,255,.08);padding-top:14px;"><strong style="color:rgba(255,255,255,.75);">6.3 No Refunds</strong></div>\n'
    '<div style="margin:5px 0;font-size:11px;"><strong style="color:rgba(255,255,255,.75);">Tuppence is non-refundable, non-transferable, and non-redeemable for cash, goods or services other than the platform Introduction feature.</strong> Spending Tuppence on an Introduction request consumes the Tuppence regardless of the outcome — whether the Seller accepts, declines, ignores, or the account is closed. This is the consideration for the buyer-commitment signal that underpins the Platform’s anti-spam Introduction-gating design. By purchasing Tuppence and submitting an Introduction request, you acknowledge that Tuppence is a service credit, not goods, and is non-refundable.</div>'
)
if OLD5_SECTION in content:
    content = content.replace(OLD5_SECTION, NEW5_SECTION, 1)
    changes.append('Edit 5b — §6.3 Refunds section replaced with §6.3 No Refunds')
else:
    # Try with plain apostrophe in "Seller's Wallet"
    OLD5_SECTION_PLAIN = OLD5_SECTION.replace('’', "'")
    if OLD5_SECTION_PLAIN in content:
        content = content.replace(OLD5_SECTION_PLAIN, NEW5_SECTION, 1)
        changes.append('Edit 5b — §6.3 Refunds replaced (plain apostrophe variant)')
    else:
        changes.append('Edit 5b — §6.3 block NOT FOUND (check spacing)')

# ────────────────────────────────────────────────────────────────────
# Edit 6 — Seller account closure Tuppence refund (L2401 area)
# ────────────────────────────────────────────────────────────────────
OLD6 = 'Buyers with open Introduction requests are notified that the Seller is no longer available and Tuppence is refunded.'
NEW6 = 'Buyers with open Introduction requests are notified that the Seller is no longer available. Tuppence spent on closed Introductions is consumed; no refund is issued.'
if OLD6 in content:
    content = content.replace(OLD6, NEW6, 1)
    changes.append('Edit 6 — seller closure refund rewritten')
else:
    changes.append('Edit 6 — NOT FOUND')

# ────────────────────────────────────────────────────────────────────
# Write and verify
# ────────────────────────────────────────────────────────────────────
with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# Integrity check
with open(PATH, 'r', encoding='utf-8') as f:
    final = f.read()

status = 'OK' if final.rstrip().endswith('</html>') else 'TRUNCATED:' + repr(final[-60:])

print('Tuppence refund purge results:')
for c in changes:
    print('  ' + c)
print()
print('File integrity:', status)
print('Size delta:', len(final) - original_len, 'bytes')

## 19 Aug 2026 — LINK-PREFETCH-1 / GATE-WHY-1: a machine can no longer spend a tester's access link

**The fault.** Maroushka opened the gate, asked for a link, clicked it, and was told the link had
expired — instantly, on a link seconds old. David had hit the identical thing. Nothing had
expired and no person had used it: **a machine had**. Resend rewrites URLs when click tracking is
on, and mail providers and security gateways fetch links before delivery. That machine fetch
claimed the single-use `jti`, so the human's click arrived second and was refused as "already
used".

**Why strict single-use was the wrong trade.** The token is already 30 minutes long, bound to the
reviewer allow-list, HTTPS-only, and scoped to browse-only passage. Single-use added very little
on top of that and cost us the entire lane the moment a scanner touched it.

- Repeat claims inside the 30-minute window are now **idempotent** — the expiry is the control,
  not the counter. A prefetch costs nothing; the human still gets in.
- The `jti` record is kept for **audit** (claim count, first claim) and an absurd replay count
  (>25) still refuses.
- `HEAD /review/enter` answers 204 and touches nothing — a HEAD is never a person.

**GATE-WHY-1 — we were blind, and that is what cost the time.** Every refusal collapsed into one
sentence ("expired or was already used"), so a link killed by a scanner was indistinguishable
from a genuinely stale one. The bounce now carries a coarse reason (`expired | used | invalid |
none` — nothing an attacker learns) and the gate screen says which. On *any* link failure the
6-digit code box now opens automatically, because that door cannot be prefetched.

**Ledger.** RG-0109 added (OPEN until deployed), asserting the class — not just this link, but
any one-time URL we email, including the account magic link and agent invites.

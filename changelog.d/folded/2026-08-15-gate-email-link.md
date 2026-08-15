## 2026-08-15 — GATE-EMAIL-1: the gate opens on an emailed link, not a memorised code (RUL-014, RG-0081)

David's ruling: "email linked and not with a code, like normal apps" — too many testers locked
out. Confirmed NOT a new request: the magic-link machinery has existed since ACCOUNT-BIND-1
(5 Aug) and the magic-link auth refactor sits in BACKLOG; what was never built is the GATE
using it. Root cause of the lockout class was never the cookie (365-day, valid) — the gate
script's sessionStorage short-circuit re-challenged every new tab session, and one mistyped
code read as "locked out".

Two-pronged fix:
- **GATE-COOKIE-2** (marketsquare.html): the gate screen now asks /review/verify cookie-first —
  a tester holding a valid cookie is never re-challenged at all.
- **Email-linked entry**: gate screen asks for an EMAIL; `POST /review/request-link` (allowlist
  file `/var/www/marketsquare/review_emails.txt`, re-read per call, no enumeration, shared
  per-IP rate limit) mails a one-time link; `GET /review/enter` burns the single-use jti
  (30-min life) and sets the SAME ts_review cookie the code path sets. Transport mirrors
  _send_login_email (Resend -> Gmail, RESEND-FROM-1 + MAIL-FALLBACK-1 lessons kept).
- **Migration 019**: exempts the two endpoints at the origin (016/018 skeleton: functional
  idempotency, collision refusal, backup + nginx -t auto-restore) and seeds the allowlist
  (David x2, Maroushka miconradie1@, Maurice conradiedm@, Marietjie marietjie.marais59@).

Containment UNCHANGED by design: origin lockdown (RG-0028), armed catch-all (GATE-ENFORCE-2),
per-IP rate limit, code path alive as break-glass. Claim email+IP logged per entry. Tokens
deliberately NOT hard-bound to claim IP — tester ISPs rotate (David's own, three times on
record); a hard bind would re-create the lockouts this ends.

Ledger: **RG-0081 OPEN** (repo half green now; live half EXPECTED failing until 019 rides a
deploy — then promote to LOCKED). Rulings: **RUL-014** registered + rulings_check reflections.
Rollbacks: bea_main.py.bak-gateemail-20260815-075832, marketsquare.html.bak-gateemail-20260815-075930.
Other gate-script copies (dashboard*, admin) deliberately untouched — admin-password doors,
not tester doors (RG-0075 single-source refactor remains the standing answer there).

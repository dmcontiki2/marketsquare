## 2026-08-19 — WAF PRELAUNCH GATE disabled: testers can finally reach the email-link gate (WAF-OPEN-1)

**Fault:** Marietjie (allow-listed tester) got Cloudflare's "Sorry, you have been blocked" page
on trustsquare.co — server journal showed ZERO requests from her in 5+ days. Root cause: the
Cloudflare custom rule "PRELAUNCH GATE - block all except allowlisted IPs" (post-breach
lockdown, 4 Aug) was still ACTIVE — only David's three 197.185.x.x IPs reached the origin.
GATE-EMAIL-1 (15 Aug) built the tester email-link gate, but the edge was never reopened, so no
tester could ever see it. The 15 Aug changelog even said "Testers: next visit, type your
email" — impossible while the edge rule stood.

**Fix (David's ruling, 19 Aug, on the phone with Marietjie):** rule set to DISABLED (not
deleted — one click re-enables) in the CF dashboard. The ORIGIN gate (GATE-ENFORCE-1 +
GATE-EMAIL-1 allow-list) is now the pre-launch guard, as designed.

**Verified end-to-end:** (1) root fetch from a non-allowlisted IP: 403 -> 200 the moment the
rule saved; (2) POST /review/request-link for dmcontiki2@gmail.com -> Resend 200 ->
"Your TrustSquare access code" landed in Gmail 1 second later. Confirmation email then sent
to Marietjie (Afrikaans) — only after the proof, per David's explicit condition.

**Watch items surfaced (not fixed this session):**
- Anonymous GET /listings and /flags answer 200 — RESOLVED as intended: RUL-029 (19 Aug,
  earlier session) took the ORIGIN gate down by ruling; ledger RG-0029/RG-0115 assert the
  gate-down state. With the CF edge rule now also disabled, the site is effectively PUBLIC
  ahead of the 29 Aug soft launch — WAF-OPEN-1 completed what RUL-029 started.
- Ledger run (live-only, executed on the server from /tmp): 6 reds, ALL run-context artifacts
  — 5 x "repo file unreadable" (run outside the repo hard-fails instead of skipping: RG-0070/
  0071/0074/0078/0079) and RG-0028 "origin accepted direct connection" (the server connecting
  to itself; verified from OUTSIDE: 80/443 both refused, firewall intact). No real regressions;
  nothing WAF-OPEN-1 touched went red. Wart worth noting: those 5 entries should demote to
  "skipped" outside the repo like their siblings do. Sandbox in-repo run hung >20 min on the
  proxy and was killed — rerun in-repo next session for the LOCK promotions (RG-0075, RG-0120
  both print READY TO LOCK).
- Resend probe 422s every ~5 min in the journal (services-status mail probe) + recurring
  ERROR RESEND-FROM-1 "malformed sender 'TrustSquare'" — real sends succeed via fallback,
  but the env var RESEND_FROM (or equivalent) needs the full "Name <addr>" form. Noise now,
  outage-mask later.

**Tester grant (David's instruction, same session):** Marietjie credited 500 Tuppence to test
freely — transactions row id 199, type `tester_grant` (deliberately NOT `topup`, so revenue
metrics stay clean, and NOT `monthly_allocation`, so the non-rolling grant sweep never expires
it). DB backup first: .db-backups/marketsquare-pre-tester-grant-20260819.db. Balance verified 500.

### Maintenance loop — 26 Aug 2026 (02:20–02:35Z)

**Fault queue clean.** 0 new · 0 triaged · 0 fix-shipped · 26 verified · 7 closed ·
2 duplicate (35 total). Shadow agent ran foreground, SHADOW mode, 0 seen / 0 acted,
heartbeat posted to `/dashboard/maint` at 02:22:32Z (brain KEYED:anthropic). No
escalation brief — no escalations in 24h.

**Ledger: 4 reds in, 3 out — and 2 of the 4 were the instrument, not the app.**

| Entry | Was | Now |
|---|---|---|
| RG-0181 / RG-0182 | RED (`ModuleNotFoundError: fastapi`) | **green** — false reds, fixed at class level by LEDGER-DEPS-1 |
| RG-0125 (migration chain jammed) | RED | fix committed; **clears when the nightly deploy rides** |
| RG-0099 (SSH lockout) | RED | **still red — needs David** (see below) |
| RG-0154 (session badge) | green | red: live 178, disk 179 — *this* sitting, clears on deploy |

**Fixed this session (both LOCKED, both with named machine evidence):**
- **RG-0187 / LEDGER-DEPS-1** — a harness killed by a missing third-party import now reads
  UNVERIFIED, never REGRESSION. Third instance of "the instrument reporting itself as the
  app" after LEDGER-OFFLINE-1 and GATE-CACHE-1. A missing *repo* module still stays red.
- **RG-0186 / CSP-SCRIPT-SRC-3** — migration 033 searched fixed, non-recursive globs and so
  could never see the file emitting the CSP; it rewrote everything it could see, restored 0
  files, failed honestly and jammed the chain. Discovery is now `nginx -T` + a recursive walk.

**Needs David (not actionable by the loop):**
- **RG-0188 (new, OPEN)** — `.secrets/hetzner_token.txt` is absent, so the SSH-LOCKOUT-1
  self-heal exits "NO TOKEN, nothing changed". The cure named in RG-0099's own failure
  message has never been armed. Origin `178.104.73.239` is unreachable from this vantage on
  22/443/80 while Cloudflare serves `/health`, `/` and `/terms` at 200 — the box is fine,
  this egress IP (197.184.106.176) is simply outside the origin allowlist. The script only
  ADDS an IP and never removes a rule, so arming it carries no lockout risk; provisioning the
  token is his (RUL-027).

**Not deployed.** Committed only — NIGHTLY-SHIP-1 (05:45 TSL) carries it. RG-0125 and RG-0154
are both "waiting for the deploy", not rot.

**Ledger: 181 entries · 158 holding · 3 regressed · 20 open · 0 unverified.**

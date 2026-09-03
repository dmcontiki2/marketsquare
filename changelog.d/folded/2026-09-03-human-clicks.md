## 2026-09-03 — HUMAN-CLICKS-1: "320 emails, 75 clicks, 0 listings" was the click count lying, not a fault

**David asked:** do we have another fault — 320 emails and 75 clicks, not one listing?

**PROBED (server, since 29 Aug):** 0 MarketSquare users created, 0 listings created. The dashboard's
3 onboarded / 2 published are David's own family addresses sitting in the prospect pool, matched by
CONVERSION-RECONCILE-1. Of 61 click events: **33 were the UNSUBSCRIBE link** (Azure/Defender Safe Links
ranges, bursts seconds apart), 18 pre-forensics with no link, 7 on the CTA — and 3 of those 7 were bots
(Ruby UA on support@ mailboxes, Azure IP). At most 3–4 humans reached the site; none finished the
photo-and-AI listing flow. Not a system fault. Two funnel weaknesses noted for later: the harvesters
are collecting institutional inboxes (info@/support@/admissions@), and `sfInit` has no mapping for
`teachers_trainers` / `Estate Agency` / `adventures_accommodation` / `Car Dealers` (falls to the tile
screen; agencies land in the individual sell-flow). `src=` / `draft_id=` are sent but never read by ms.js.

**Decided (CTO, RUL-037):** a persistent per-recipient register, not a smarter report — David's word:
"compile a database of the registered human clicks for a future resend to them only, where all of the
auto clicks can be ignored."

**Built:**
- `CityLauncher/click_register.py` — the ONE scorer (classify_clicks.py now reports from it). Scores every
  fingerprinted open/click (scanner UA, Azure/Defender egress IP, seconds-after-send, links-per-recipient,
  IP-shared-across-recipients) and rolls up per recipient into table `click_register`:
  tier `human_click` > `human_open` > `uncertain` > `machine`, counts, first/last human signal, best link,
  reasons, plus human-owned columns `overruled_tier` / `resent_at`. Test traffic (example.*, CLICKTEST)
  excluded. **Written on the live server 3 Sep: 117 recipients → 2 human_click, 48 human_open, 11
  uncertain, 56 machine.** (DB backed up beside it first.)
- `api/server.py` — refreshes the register on the reconcile cadence; `POST /prospects/click-register/refresh`;
  `GET /prospects/human-clicks?tier=&format=csv` (key-gated); `/prospects/stats` carries `click_register`.
  Passes in test (TestClient on a copy of the live DB: 401 anonymous, refresh ok, 50 rows, csv).
- `resend_human_clicks.py` + `.bat` + template `human_followup_outreach.html` — host-side, dry-run by
  default, humans-only, stamps `resent_at` (never twice), every emailer guard + JOURNEY-1 gate,
  `--min-age-days` (default 1) and `--clicks-only`. Dry run on a copy: 48 would send, 2 skipped (opted_out).
- Ledger **RG-0248 (OPEN)** — source + behavioural legs green; live leg goes green when
  `GET /launch-api/prospects/human-clicks` answers 401 instead of 404.

**Not yet live:** api/server.py ships via `deploy_citylauncher.bat` (David's lane). The register itself is
already on the server and `click_register.py` is beside it. Backups: `api/server.py.bak-clickreg-*`,
`classify_clicks.py.bak-*`, `regression_ledger.py.bak-rg0248-*`.

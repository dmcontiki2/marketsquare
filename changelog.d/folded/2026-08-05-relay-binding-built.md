## 2026-08-05 — INTRO-RELAY-1 + ACCOUNT-BIND-1 BUILT (dark), Fable 5 session

Both of David's rulings implemented in one pass on the intro flow; both fail-closed
behind new launch_switches (intro_relay, account_binding), so live behaviour is
byte-identical until flipped. NOT yet deployed.

- **INTRO-RELAY-1 (Option B):** intro_relay_aliases table; _mint_relay_aliases (2 rows
  per accepted intro, random aliases on RELAY_DOMAIN); _relay_forward via the Resend
  lane (From/Reply-To ALWAYS an alias); _relay_send_intro_notes (each party's note
  arrives FROM the counterpart's alias — reply starts the conversation); POST
  /intro/relay (X-Relay-Secret, enrolled-parties-only, expiry, kill switch, CR/LF
  sanitise, 100 KB cap, no outbound fetch — nothing SSRF-shaped); accept_intro mints +
  sends notes + webhook carries ALIASES ONLY when the relay is on. Worker for David's
  console step: ops/cloudflare/intro_relay_worker.js (setup steps in its header).
  Isolated-logic test: all 7 semantics proven (enrolment, both-direction kill,
  expiry, injection strip, no-info-leak on unknown alias).
- **ACCOUNT-BIND-1 (Option A):** /auth/verify now KEEPS its magic-link proof as an
  HttpOnly ts_user session cookie (JWT scope 'user', 180 d, same _JWT_SECRET,
  distinct scope — the shared review token can never pass). _bind_charged_email
  enforces (flag ON: 401/403) or shadow-logs (flag OFF) on AI1–AI5 + create_intro;
  BIND-OWNER-1 makes accept/decline intro owner-only. BEA_URL is same-origin so the
  cookie rides existing FEA fetches — zero FEA changes. Isolated test: scope
  separation proven (review/expired/forged/absent all refuse).
- Ledger: RG-0038 + RG-0039 LOCKED (repo assertions green on disk). Backups:
  bea_main.py.bak-20260805-relaybind. Peer pack sections extended for round 3.
- NOTE: built alongside a parallel attended session (TS-0005..20 fixback batch +
  14:55 release) — all anchors re-verified against the moved file; nothing stomped.
- NEXT: David's Cloudflare console step (worker + MX + RELAY_INBOUND_SECRET + Resend
  subdomain auth) → deploy → Peer round 3 → flip flags → live two-party drill.

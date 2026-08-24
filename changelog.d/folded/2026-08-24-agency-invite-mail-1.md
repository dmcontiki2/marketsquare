## 2026-08-24 — AGENCY-INVITE-MAIL-1: the bulk roster lane now SENDS the sign-in links it promised

- Found walking the agency funnel as a recipient (David's soft-launch traction question):
  outreach lane 2 + Import Guide promise "each agent instantly gets a sign-in link" and the
  console toasted "magic links & verification queued" — but POST /agencies/{id}/agents/bulk
  sent NOTHING. Worse, the single-invite lane emailed the sign-in CODE template with an
  EMPTY code box and "expires in 20 minutes" copy on a 72-hour token.
- Fix: one transport helper `_send_html_email` (MAIL-FALLBACK-1 kept in ONE place); a real
  invite template `_send_invite_email` (invite wording, honest 72h expiry, code path as
  fallback per SIGNIN-CODE-1); one minter `_mint_agent_invite` used by BOTH invite_agent and
  the bulk lane via estate_agents.configure(invite_fn=...) — estate_agents still never
  imports bea_main. Per-agent `"link": sent|failed|dry` in the bulk report; ms.js toast and
  report now state what actually happened.
- test_estate_agents.py de-rotted (broken since AGENCY-KEY-1 added auth: bulk calls sent no
  key; two credential checks stale since VERT-4-1 slot names) + new invite-seam check.
  56/56 pass. Ledger: RG-0171 added OPEN (live half waits for the deploy — READY TO LOCK on
  first green run after ship); RG-0167 promoted LOCKED (READY TO LOCK printed this session).
- NOT deployed — ships with David's next /ship or /tsl.

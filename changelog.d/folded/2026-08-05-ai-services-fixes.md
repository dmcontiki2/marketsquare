## 2026-08-05 — AI services audit findings ACTED ON (F1/F2/F3/F5) + Peer pack v2

David's rulings on AI-SERVICES-AUDIT-1, all implemented same session (NOT yet deployed):

- **F1 / RG-0032 — any-lane gates.** All 15 `if not ANTHROPIC_API_KEY` endpoint gates
  replaced with `ai_provider.any_lane_configured()` (new `configured_lanes()` helper in
  ai_provider.py). A single-vendor key loss can no longer 503 the AI estate while
  standby lanes are healthy. Both drill variants (AI_DRILL_BAN + unconfigured-key)
  must be re-run post-deploy.
- **F2 / RG-0033 — deliver-then-charge.** AI1 rewrite, AI2 audit, AI5 batch cards now
  pre-flight with `_require_tuppence` and deduct ONLY after a successful result
  (Session-95 pattern; AI3/AI4 were already compliant). Failure copy now honest:
  "no Tuppence was charged". The help card's refund promise is true for all five.
  (David recalled a hold/settle: that lives in the AdvertAgent metered lane
  (advert_agent.py hold/settle); these three older services had charge-first — now aligned.)
- **F3 / RG-0035 — vendor-neutral copy.** The five AI Services card descriptions in
  marketsquare.html no longer name Claude ("Our AI rewrites…") so a lane swap can
  never make user-facing copy false.
- **F5 / RG-0034 — HEARTBEAT-1 live.** P2c idle-recovery heartbeat added to BEA
  startup per design §6: 60s tick, ONE atomically-claimed direct probe per tick,
  round-robin, text ping, spend logged. Tripped lanes now recover overnight without
  traffic. (P2c's latency baseline + P2b card lights remain open.)
- **F4 answered:** the sweep's Sonnet WARN (dashboard.server.html) is display text in
  the VIZ-MAPS legend/labels, not a call site — no routing failure; DW-009 stays
  David's justify/downgrade call.
- **Ledger:** RG-0032..0035 added (all LOCKED, repo-side assertions verified green).
  Backups: *.bak-20260805-aisvcfix beside each touched file.
- **Peer pack v2:** scripts/peer_pack_ai.py builds a fresh 88 KB bea_main.py extract
  (real line numbers) each run — answers the Peer's "bea_main.py not supplied" packet
  complaint (the 120 KB/file cap forbids shipping 850 KB whole).
  PEER_AUDIT_AI_SERVICES.bat v2 includes extract + price card + breaker tests + funnel.
- **ALERT (found by the pre-fix ledger run, NOT caused by it): RG-0028 REGRESSION —
  origin 178.104.73.239:80/443 accepted a DIRECT connection from an off-allowlist
  host. The Hetzner Cloud Firewall appears to be off the server — Cloudflare WAF
  (RG-0027) is bypassable until restored. David: Hetzner console check needed.**
  (Most other ledger REGRESSION lines from the sandbox run are the known
  403-gate-artifact class — this one is not.)

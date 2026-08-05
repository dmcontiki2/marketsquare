## 2026-08-05 — LS-TIPS-1 + Ops Map relay block (the dashboard becomes David's memory)

David's ruling: the project has outgrown memory — the instruments must carry it.

- **LS-TIPS-1:** every Launch Switch now has a hover explainer (styled tooltip):
  what OFF does, what ON does, and the implication — covering verified_tier, videos,
  fault_report, all four data switches, all three per-planner switches, and the two
  new rails. No switch depends on recall anymore.
- **Launch Switch page — new "Trust & privacy rails" group:** intro_relay and
  account_binding toggles, wired to /flags + /admin/flags (server accepts + returns
  both; also returns relay_configured = RELAY_INBOUND_SECRET present). The relay row
  shows the live Cloudflare-rail status ("configured ✓" / "NOT configured") so David
  can see switch-vs-rail at a glance and can't flip ON before the rail exists.
- **Ops Map (OPS-MAP-1): new "Intro Relay" block** in the external column under
  Resend — flow line buyer ↔ CF worker ↔ BEA ↔ Resend ↔ seller, three live chips
  (switch ON/OFF, rail ready/not built, acct binding ON/OFF) tinting from /flags,
  and a hover title telling the full OFF→ON story incl. the doctrine. Flag-chips
  row also gains intro relay + acct binding.
- All dashboard script blocks node --check clean. Backup:
  dashboard.server.html.bak-20260805-lstips. Rides next /tsl with the relay/binding code.

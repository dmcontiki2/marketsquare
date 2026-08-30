## 2026-08-30 — Batch 1 listing improvements built + red/amber follow-ups (unattended, RUL-065)

- **SF-AIDESC-1 (RG-0205):** the guided sell flow now USES the AI's description_draft — it
  leads the composed listing description; mechanical "Label: value" lines follow; seller-typed
  prose wins over both. ms.js sfComposeDescription rewritten; node --check clean.
- **A2HS-ASK-1 (RG-0209):** promptAddToHomeScreen() finally has a caller — one trigger after
  the first successful publish handoff (sfFinish non-draft path). Existing standalone/done
  guards untouched; no notification permission bundled.
- **CSP-CONNECT-1 activated (RG-0180):** connect targets MEASURED live in Chrome (index,
  adventures ZA map + heritage toggle, listing detail with photos, dashboard — zero
  cross-origin fetch/XHR anywhere). migrations/034_csp_connect_src.py ships the recorded
  three-host allowlist; DRAFT_034 removed from docs/. RG-0180's live-half assertion was a
  substring test that could never pass its own recorded policy — fixed tokenwise, noted in ref.
- **MAP-LIVE-1 (new RG-0214, D15 fallback):** /orchestrator/defence_map.html +
  /orchestrator/watch_register.md now served by the app from the repo's fetched origin/main at
  request time (bea_main.py routes + migration 035, gate-preserving exact-match nginx proxy
  locations; migration proves app-200 AND anonymous-401 before claiming success). D15 (PAT)
  stays open to David — it fixes the shipping class this fallback does not.
- **DW-084 PREPARED live (root, PROBED):** MS_API_KEY live fp == unit inline fp (c42deee7),
  no other on-disk source remains — restart-safe. Junk drop-in deleted, stale
  LAUNCH_SPECIAL_DEADLINE=2026-08-01 removed (merged config: single 2026-09-01), unit
  EnvironmentFile deduped 5→1, daemon-reload done, NO restart. DW-085 re-probed: 37 updates +
  kernel reboot pending — awaiting David's window.
- **RG-0114 root-caused + fixed:** tester-intake guard red 8 scans because the contagion model
  and defence map joined the manifest under the Basic-Auth orchestrator/ realm and the guard
  demanded the tester widget on them. OPS-REALM-EXEMPT-1: tester_pages() now judges by DEST and
  exempts the gated realm. Guard suite green; clean scan logged (danger=-).
- Staged, not shipped (RUL-037): all of the above rides David's next deploy.

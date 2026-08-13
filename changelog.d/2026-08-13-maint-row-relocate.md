## 2026-08-13 — MAINT-DASH-1 relocated: B2b readiness row inside the Maintenance group

- David: the readiness view belongs IN the "Maintenance (pre-launch testers)" switch group,
  not as a standalone card above the Launch Switch. Relocated: standalone card removed, now
  one ls-row directly under "Tester fault reporting" — name + live detail line + status
  chips (STALE/KEYED/NO KEY/ARMED/SHADOW), LS-TIPS-1 hover explainer. Still chips, not a
  toggle: key + ARM stay machine-local acts. RG-0061 assertions updated to follow the row
  (id maint-b2b-row; no-toggle check scoped row→Trust header); ledger green, RG-0061 OPEN
  until first heartbeat (endpoint confirmed live this morning, awaiting tomorrow's run).

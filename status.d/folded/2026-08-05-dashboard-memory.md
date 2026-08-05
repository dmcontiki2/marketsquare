## 2026-08-05 — Dashboard as memory

- LS-TIPS-1: hover OFF/ON/implication explainers on ALL launch switches; new Trust &
  privacy rails group (intro_relay + account_binding) with live Cloudflare-rail status;
  Ops Map gains the Intro Relay block with switch/rail/binding chips. Server /flags +
  /admin/flags carry the two new switches + relay_configured. Rides next /tsl.
- FIXED-HONESTY-1: ops-map Maintenance chips no longer lump 'fixed' (shipped,
  unconfirmed) with untouched faults — majors count only genuinely-open rows;
  'fix shipped · retest' chip carries the pending-confirmation pile. If the 21
  majors still show after deploy, their DB rows need advancing via the retest
  letters (draft → send), which is the honest path to green.

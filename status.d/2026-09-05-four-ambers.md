### All four ambers cleared, each at the class (5 Sep 2026, attended)

- **RG-0196 LOCKED** — the admin gate has one source (`shared/admin_gate.js` + `scripts/sync_admin_gate.py`),
  inlined not linked so the `file://` copy keeps working. Found live drift a third time on the way in.
- **RG-0281 LOCKED (DW-090)** — `post_deploy.sh` refreshes the FEA baseline behind a source-match gate;
  proven by the first deploy that rode it. Retires a class that recurred four times.
- **DW-093 residual discharged** — RG-0241 probes one unique `.invalid` address instead of a global count;
  real addresses are refused 400.
- **DW-095** — cost sweep exits 0, no warnings.

Coverage map: 65 green · 0 blue · 0 amber · 0 red · 10 grey. One register item open: DW-087 (LOW).

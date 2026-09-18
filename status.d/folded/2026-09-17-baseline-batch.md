- Baseline batch (RUL-126) built 2026-09-17: all nine items of `BASELINE_BATCH_2026Q4.md`
  are in the tree as ONE change behind `launch_switches.baseline_q4` (default 0, dark).
  Every item was driven in the rendered real app at phone width on the smoke rig; proofs in
  `BASELINE_BATCH_PROOFS_2026-09-17.html`. The existing app is unchanged while dark.
- Arming is David's act (`POST /admin/flags {baseline_q4:true}` / the +1 page), after he has
  seen it locally and in the 30 Oct gated sandbox — sequence unchanged.
- Not a Zoom door: Local Market (no filter panel exists there today).
- Field measurements after arming, not before: DCB-001 time-to-publish before/after and
  David Jnr's retest; Quick five-tap journey on a real phone.
- Ledger: RG-0221/0216/0224/0203/0346 LOCKED, RG-0383–0392 new; live halves red until the
  deploy lands (migrations 040 quality-score backfill, 041 credential registry seed,
  042 nginx `/quick/` sub-path).

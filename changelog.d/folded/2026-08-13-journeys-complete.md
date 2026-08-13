## 2026-08-13 — Journey photos 164/164 · report-widget class fix (RG-0062)

Mozambique's final 7 flight-leg photos generated, QC'd and claimed (f1_start passed
with the reworded prompt after two prior NSFW false-flags; f1_view and f1_over also
needed rewording — the classifier flagged plain landscapes; all wordings banked in
status.d/2026-08-13-mz-run-prompts.md). **All 164 journey photos across 5 journeys are
now on disk** — the set that began 26 Jul is complete. adventures_mz_map.html rebuilt:
32 embedded / 0 pending. The rebuild dropped the ts_report.js line AGAIN (3rd
occurrence of the class), and test_tester_intake caught na/bw/c2c/ke missing it too;
root-caused this time INTO scripts/journey_template.html so no future rebuild can lose
it — asserted by new LOCKED ledger entry RG-0062. All 16 tester-intake tests green,
ledger green. Browser-run lesson banked: JS-dispatched clicks (coordinate-free) are
immune to the window resize/scale flips that broke three coordinate calibrations in
one morning.

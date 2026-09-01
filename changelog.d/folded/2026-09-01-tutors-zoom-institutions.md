## 2026-09-01 — RUL-089: Tutors funnel gains institution + subject drill-downs (design)

David's 3 a.m. direction recorded and designed same session: Zoom's Tutors lane gets
`near_institution` and `subjects` facets from data already held (3,187 DBE schools,
coordinate-proven institutions, tutor lat/lon). Single-click mechanics: ask NEAR not
WHICH (proximity×count ranks, top tile is the obvious school); NEW engine rule 3.6
singleton auto-collapse (one option = zero clicks, applies to all facets); subjects
inherit the answered institution. Spec: ZOOM_HMI_SPEC.md §10. Build rides the RUL-076
window, flag-dark; arming stays David's act. Also this session: register_daily_wave.bat
+ taskscheduler_dailywave_0010.xml automate the RUL-082 daily ladder (guards unchanged,
min-gap makes double-fire harmless) — David's one elevated click to register.

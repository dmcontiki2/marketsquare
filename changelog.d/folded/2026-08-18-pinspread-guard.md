## 2026-08-18 — PINSPREAD-GUARD-1: the bouncing-pin loop killed at the template (David's catch)

- David spotted an orange pin bouncing on the US rail map (Leg 3; earlier an orange+green
  pair). Root cause read straight out of PIN-SPREAD-1: spreadPins() adds tether legs /
  clearSpread() removes them, and queueSpread listens to layeradd+layerremove — the
  machinery retriggered ITSELF every ~140 ms, snapping clustered pins home and fanning
  them out again, animated by the .28s transition: a visible ~3x/second bounce whenever
  any cluster existed past base zoom. A synthetic-hover probe froze the tab the same way.
- Fix in scripts/journey_template.html (single source): a busy flag makes the machinery
  deaf to its OWN synchronous layer events; leg redraws, layer-control toggles and zooms
  still retrigger normally. All 11 maps rebuilt (RAIL-PHOTOS-1 embeds inherited), ms.js
  busters +1 x11 read-then-increment, planner selftest green (pin-spread still asserted),
  ledger RG-0103 LOCKED trips on template OR any built map regressing to unguarded.
- LOCAL with the heritage 319 catalog — both ride David's next deploy click.

## 2026-08-16 — PIN-SPREAD-1 v2: overview keeps true geography (David's eyeball verdict)
David's in-depth eyeball test: the full-tour view looked "too spread out — cards
everywhere on the map". v2 gates the fan-out by zoom: at the overview zoom (captured at
load) pins sit at their true locations exactly as before; the spread activates only past
it — i.e. entering a leg/day (which zooms the map) or zooming in manually. Zoom back out
and every pin returns home. Template + the 5 generated maps rebuilt. RG-0096 unchanged
(presence assertion still holds). Cost model impact: none.

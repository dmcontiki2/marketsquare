## 2026-08-16 — PIN-SPREAD-1: overlapping map pins fan out (David's HMI ruling)
David: overlapping circles are hard to see and click — spread them elegantly around the
circle. Implemented in the map GENERATOR (scripts/journey_template.html) so every future
map inherits it: pins colliding at the current zoom fan evenly onto a small circle, each
tethered to its true location by a thin dashed leg; zoom in and they return home
(animated, .28s). Popups and clicks keep their identity. Five generated maps rebuilt
(bw, c2c, ke, mz, na — the Cairo cluster in David's screenshot is c2c). RG-0096 LOCKED:
template + every generator-built map must carry the block. STAGE 2 pending David's
verdict on look/feel: port the same block to the hand-built maps (za pilot, gb, au, us).
Cost model impact: none.

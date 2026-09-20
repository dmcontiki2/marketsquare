## 2026-09-19 — SIM-SVC-1: Contagion Model v1.8, the Services lane behind a toggle (RUL-150/151/152)

David: *"update our simulation program to include the new services we plan to implement, considering the new
bigger user base in South Africa at least ... with a toggle to show it."* Done in
`docs/TrustSquare_Contagion_Model_v0.2.html` (deployed as `/orchestrator/simulation.html`).

**What the lane models.** Its own SA-only compartments, so it never borrows the ordinary seller's numbers:
a bigger addressable base (`svcDen`, casual + technical workers per 1,000 people, grounded in Stats SA QLFS
Q2 2026: 16.7m employed, 8.5m unemployed, 33.6%); employer doors in the approved order, Pretoria first
(`svcW`, `empPace`, `empYes`, lognormal `empSize` rosters, `empReach`); enrolment NEVER creates a listing,
she publishes by her own hand at the Quick door (`svcAct`); gated roles wait for clearance or a licence
(`svcGated`, 14 IN roles, RUL-153/155/156); households she already works for confirm and join (`svcAud`,
decisions 3-4); co-workers via wa.me with no number (`svcRef`); the model's own organic spread and a
services twin of b2s (`svcB2s`); service liquidity by the taxi drop (`svcTgt`); languages lift the lane
from English-only to ~90% at `svcLangW` (decision 8). Money at canon prices with ZA fees.

**The toggle.** Teal "Services lane" button in the top bar. ON adds a with/without strip, a teal
dotted "without services" curve, a fifth tier (Strain 5, teal) on the map and tier chart, a third
ensemble, four presets and a lever group. **OFF is v1.7 draw for draw** - the lane draws its parameters
and its dynamics from its own random streams. Verified in a rendered headless browser: mid run and
110-seed ensemble identical to v1.7 at weeks 2/8/26/52/104/156, no page errors.

**What it says (mid run, defaults).** SA sellers at week 156: 32,181 with the lane vs 10,994 without
(+193%); 21,097 service workers listed, 35 employers enrolled from 152 approached, ~100k of the ~160k
SA service market still unreached. Almost nothing before week 52: at 4 conversations a month the
employer door seeds the lane, and it only ignites once SA liquidity builds. Every new number is a
guess until the Quick door's beacons measure `svcAct`.

Dashboard: the BEAT THE MODEL card now pins "v1.8 (pins from v1.7, unchanged)" - RG-0287's
version-agreement check stays green.

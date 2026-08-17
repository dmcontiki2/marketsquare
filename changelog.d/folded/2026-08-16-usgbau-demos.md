## 2026-08-16 — US / GB / AU demo maps rebuilt through the generator (unattended run)
David's ask before leaving: build the new demos for US, GB and AUS with zero inputs.
REUSE BEFORE RECREATE honored: all photos EXTRACTED from the hand-built maps' embedded
data (zero Higgsfield credits, zero photo-run grants — 30 photos recovered; GB keeps
its 3 original placeholder tiles). Each map converted to a generator spec
(journeys/usa|gbr|aus.json + assets/journey/{usa,gbr,aus}/) with type mapping
(stay→over, wildlife/reef→sight, dive→view) and per-map overlay labels; rebuilt via
build_journey: US 927 KB (was 3.1 MB), GB 716 KB (was 2.4 MB), AU 778 KB (was 2.6 MB)
— 60-70% lighter, PIN-SPREAD v2 + layer control + heritage layer inherited. ms.js
ADV_COUNTRY_MAP ?v= bumped for all three. RG-0096 STRENGTHENED (spec-driven: every
journeys/*.json out must carry PIN-SPREAD-1 — the old marker scan was vacuous).
The generator fleet is now 8 maps; hand-built remainder: za pilot, de, reserve.
Cost model impact: none.

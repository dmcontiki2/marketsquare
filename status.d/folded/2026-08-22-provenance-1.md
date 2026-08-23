2026-08-22 (attended, David, evening): PROVENANCE-1 — THE DASHBOARD HAD NO INVENTORY. David:
"it feels as if I am the Automator and need to remember what changed?" Audit of dashboard.server.html
found 141 asserted surfaces: 65 live-fed, 8 doc-parsed, 68 HAND-TYPED. The same server was costed at
€4.51/mo (Ops Map chip AND hero tile) and €22.07/mo (Ops view) while canon.yml — named ON THE PAGE as
the source of truth — said €26.68 and was served to nobody. Nine chips painted a health colour with no
feed (six green: kill switches armed / nightly backup / routing on / scheduled daily / no-AI default /
per-use AI). The health dot was born green in markup and never reset on failure, so a dead feed left a
green light over an error message. Three of the five direction cards (dir_cl, dir_aa, dir_infra) are
Python literals written 4 Jun 2026, unchanged for eleven weeks, indistinguishable from the live cards.
ROOT CAUSE: nothing ENUMERATED the claims, so the only index was David's memory — he WAS the inventory;
provenance was invisible (a live chip and a typed chip render identically); and every prior fix
(RG-0133, RG-0153, INSTRUMENT-TRUTH-1/2) named specific ids, so 68 surfaces survived them.
FIX — inversion: scripts/dashboard_provenance.py enumerates every chip and proves each is fed; an unfed
health colour is a defect unless registered in DASHBOARD_PROVENANCE.json with a reason AND a review date
that expires. Wired into deploy_marketsquare.bat. Proven by injecting a fake green chip (caught, exit 1).
All 9 defects cleared: 6 demoted to not-wired, 2 registered (review 30 Sep), cost wired to a new
/dashboard/fixed-costs reading canon.yml from all three surfaces; health dot starts and fails grey;
direction cards declare source, static ones dimmed and dated. RG-0155 LOCKED. RG-0133 STRENGTHENED
(was grepping a literal price; now asserts the feed exists and no hardcoded monthly price survives —
the new form immediately caught the €4.51 hero tile the old one could not). RG-0156 OPEN: orchestrator.html
is served live but is NOT in deploy_manifest.txt (hand-uploaded, repo copy 79 days stale), hardcodes access
code 96315 behind a gate that never runs (launch gate G2, hard 29 Aug), and renders any fetch failure as
"Nothing waiting on you. ✨". Deliberately not executed — shipping the stale repo copy would overwrite live
content and rotating a live code is David's call. NOT YET DEPLOYED — deploy is David's.

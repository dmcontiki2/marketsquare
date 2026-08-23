# STUDY & WORK ABROAD — FULL DOSSIER SPEC
v1.0 · 23 Aug 2026 · Authority: RUL-042 (positioning), RUL-043 (5T confirmed, build greenlit, video standard)
Benchmark artefacts: the two worked examples on `studyabroad_teaser.html` (study route · work route).
Assessment of record: STUDY_WORK_ABROAD_ADVISOR_ASSESSMENT — nice.docx (~$0.50–1.00/report vs 5T = $10).

## 1. Product definition
One feature, two routes. Price: **5 Tuppence, fixed, all tiers** (confirmed RUL-043; free/owned-data
class — NOT paid-feed, so no Pro gate). Preparation is ours, built on actuals; the PLAN is the
agency's; the dossier ends in a Tuppence introduction to a registered agency. MarketSquare never
processes tuition, visa fees, placements or bookings.

## 2. The four stages
1. **Intake** (luna-tier chat, 5 questions): route (study / work / unsure) · field or work type ·
   budget band · timeline · constraints (marks, age, driver's licence, childcare refs, passport state).
   Output: bounded JSON profile. No free-text essays.
2. **Options** (terra-tier): 5+ routes from `data_study` ONLY. Each carries a verdict —
   HIGH / MEDIUM / LOW / **CLOSED** — with the reason stated. The engine MUST output honest
   LOW/CLOSED verdicts where the data says so (golden-set gated; the Canada rule).
3. **Dossier** (terra-tier + capped search): rendered on our HTML dossier template, visual benchmark =
   the teaser examples. Sections, in order: profile summary · options table with verdicts · route map ·
   detailed budget for the top option(s) · funding lanes (scholarships/programmes) · opportunities ·
   risks (incl. scam warnings on the work route) · sources-and-dates block with RE-CHECK flags ·
   agency handoff CTA. Every fact carries a `data_study` provenance id; an unsourced number is a defect.
4. **Handoff**: introduction flow (existing machinery) to a registered agency on MarketSquare.
   Agency categories: education/varsity consultants · registered immigration advisers · placement
   agencies (au pair / camp / cruise / seasonal). Founding-recruitment candidates identified (SOA,
   GRI, Crew Life@Sea, OVC-class J-1 agents, education consultancies) — outreach is David's.

## 3. data_study layer (the main build item)
Own-schema cache, sibling of data_flights; suppliers are swappable adapters (supplier fallback
doctrine). Tables: `countries` · `routes` (type, country, requirements, cost_band, verdict_rules) ·
`institutions` · `funding` · `visa_rules` · `agencies`. EVERY row: `source_url`, `checked_on`,
`recheck` flag. Seeded from open/official data (Wikidata, government immigration pages, DHET/DAAD/
programme registries, agency-published requirements). Monthly refresh job; staleness degrades copy to
"indicative — confirm with the official source or your adviser", never to an outage.

## 4. Cost rails (executable, computed before dispatch)
Intake ≤12k in / 2k out · options ≤30k / 4k · dossier ≤80k / 15k · searches ≤30/report ·
hard ceiling **$1.00 per report** · deliver-then-charge (no dossier = no charge) · per-call spend log ·
rides the existing 5T-class daily ceiling and breaker. No ad-valorem cost anywhere (pricing canon).

## 5. Golden set (before any traffic)
No-invention (every fact resolves to a data_study id) · honesty gate (the fixed eval profile for a
matric-only work seeker MUST return Canada CLOSED) · anonymity rules · valid JSON at pinned effort ·
gate tuple recorded on ai_price_card per the card rules.

## 6. Videos — full-length, shelved
One FULL-LENGTH quality-script video per route (RUL-043: not shorts). SHELVED until this spec is
approved; base spiel at feature-videos/12-study-abroad/SPIEL.md; work-route script to be written from
the worked example. Unshelving is David's word; nothing renders before it.

## 7. Build phases (all additive, dark behind flag `studywork_live`)
P1 teaser + two worked examples — **DONE** (SAW-1/SAW-2, RG-0158 OPEN, rides next deploy).
P2 data_study schema + seeders + refresh job (1–2 sessions).
P3 intake + options engine + golden set (1 session).
P4 dossier generator + template + rails (1–2 sessions).
P5 handoff wiring + agency onboarding content (1 session).
Each phase lands with its ledger entries in the same session. Nothing goes live before golden set +
David's deploy word; the teaser stays the only visible surface until then.

## 8. Reserved to David
Deploy timing · agency outreach (sending is his) · video unshelve moment · any launch-scope change.

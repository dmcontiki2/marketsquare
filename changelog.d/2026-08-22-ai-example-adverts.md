## 2026-08-22 — AI EXAMPLE GENERATED ADVERTS + the red DEMO banner (RUL-040)

**AI-EXAMPLE-1 — the exemplar ribbon says what the thing is.** David: the "★ SUPER
ADVERT" label "still looks like real live listings to be bought with an Intro". A star
plus the word SUPER reads as an accolade on a genuine listing; there is no seller behind
an exemplar, so an Introduction bought against one introduces the buyer to nobody. All
four ms.js renderers that paint the ribbon — browse `lcard`, Adventures `renderAdvGrid`,
the listing detail pill, Local Market cards — now read **AI EXAMPLE GENERATED ADVERT**,
no star. The detail pill leads with *not a real listing*, in ONE wording for every exemplar:

> AI EXAMPLE GENERATED ADVERT — not a real listing; an AI-made example of the benchmark
> for this category

The showcase branch that read *"free for a real seller to claim"* was removed the same
day at David's instruction: it implied a seller could claim **that exact advert**, and
therefore that the advert already exists as a real thing. One wording, no branch, so the
claim implication cannot come back through the showcase path.

The `super_example` DB column keeps its name — this is a labelling change, not a
data-model change, which is why RG-0014 (does the ribbon render at all) is untouched by
it and stayed HOLDING. Ribbon type is 8.5px with `line-height` and a `max-width` so the
longer text wraps rather than clips on the 2-up mobile grid.

**DEMO-BANNER-1 — a page-level DEMO label on the demo maps.** New first-party
`ts_demo_banner.js` mounts a red vertical **DEMO** tab in the right-edge slot the gold
REPORT tab uses, on all 15 `adventures_*_map.html` pages. Tapping it explains, in plain
words, that the routes, adverts and prices on the page are AI-generated examples that
cannot be bought.

The two tabs are deliberately different lanes. REPORT is a tester instrument, gated on
the server flag and removed at Soft Launch when customer complaints take over. DEMO is
ungated, is for customers, and STAYS — it measures the REPORT tab at runtime and sits
below it while it exists, then self-centres in the slot the moment it is gone. No second
change is needed on soft-launch morning, and nothing about removing REPORT can take the
honesty label with it.

**Ledger.** RG-0140 (all four renderers labelled, old wording absent, pill says "not a
real listing") and RG-0141 (every demo map loads the tab; the tab never reads the tester
flag; the manifest ships it; no third-party host) are OPEN — their repo halves pass now,
their live halves cannot until the next deploy. They flip to LOCKED the run they report
READY TO LOCK. RG-0014's title was relabelled and its ref annotated; its assertion is
unchanged and not weakened.

**Proof it behaves at Soft Launch.** `scripts/demo_banner_selftest.js` runs the real script
under a DOM shim and asserts it mounts red, is labelled DEMO, sits below a present REPORT
tab, and re-centres in the slot when REPORT is removed — the soft-launch morning behaviour,
tested before it happens rather than discovered on the day.

**Also fixed in passing:** the 15 demo maps referenced `ts_report.js` at two different
cache-busters (`?v=5` on eleven, `?v=6` on four) — a page pinned to a stale build of the
fault reporter. All 15 are now on `?v=6`.

**Files:** ms.js · ts_demo_banner.js (new) · adventures_*_map.html ×15 ·
ops/autodeploy/deploy_manifest.txt · scripts/regression_ledger.py ·
scripts/rulings_check.py · RULINGS.md (RUL-040)

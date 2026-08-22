## 2026-08-22 — PROVENANCE-1: the dashboard had no inventory, so David was the inventory

**Raised by David:** *"the dashboard becomes a liability if it either shows stagnant
information or the worst case is wrong information ... it feels as if I am the
Automator and need to remember what changed?"*

He is describing an architectural hole, not a mood. A full provenance audit of
`dashboard.server.html` found **141 asserted surfaces: 65 live-fed, 8 doc-parsed,
and 68 HAND-TYPED.**

**What was actually wrong**

- **The same server was costed twice, differently.** Ops Map: `€4.51/mo` (green
  chip *and* hero tile). Ops view: `CPX32 €15.49 + Volume €6.58 = €22.07/mo`.
  `canon.yml` — named *on the page itself* as the source of truth — says
  15.49 + 5.20 + 5.99 = **€26.68**. Three numbers, five-fold apart, all
  hand-typed, because **nothing ever served canon.yml to the page.**
- **Nine chips painted a health colour with no feed at all**: `kill switches
  armed`, `nightly backup`, `routing on`, `scheduled daily`, `no-AI default`,
  `per-use AI`, plus the two cost chips and Cloudflare/Resend plan claims. Six
  of them were **green**.
- **The Server Health dot was born green in the markup** and the failure path
  never reset it — a dead `/health/resources` left a green light burning directly
  above the words "Health check failed".
- **Three of the five direction cards are Python list literals** written
  4 Jun 2026 (`dir_cl`, `dir_aa`, `dir_infra`) and never touched since. For
  eleven weeks they showed identical "priorities" while looking exactly as
  current as the two doc-fed cards beside them.

**The root cause is not that people typed values in.** It is that:

1. **Nothing enumerated them.** There was no list of what the dashboard claims,
   so the only index was David's memory. That is why he felt like the automator —
   he *was* the inventory.
2. **Provenance was invisible.** A live chip and a hand-typed chip render
   identically, so a wrong one could only be caught by contradicting something
   the reader already knew.
3. **Every prior fix was instance-scoped.** RG-0133, RG-0153 and
   INSTRUMENT-TRUTH-1/2 each named specific element ids. All 68 hand-typed
   surfaces survived them because nobody had the list.

**The inversion.** `scripts/dashboard_provenance.py` enumerates every chip on the
page and proves each is fed. A health colour with no feed is a **defect** unless
registered in `DASHBOARD_PROVENANCE.json` with a reason *and a review date* — and
an expired review date fails, so the registry can never become a hiding place.
Proven by injecting a fake green chip: caught, exit 1, clean after removal.
Wired into `deploy_marketsquare.bat`.

**Fixed this session:** all 9 unfed chips (6 demoted to the honest not-wired
style, 2 registered with Sept review dates, cost wired); cost now reads
`/dashboard/fixed-costs` → `canon.yml` from **all three** surfaces so two panels
can no longer disagree; the health dot starts grey and goes grey when the feed
dies; every direction card declares its source, with static ones dimmed and
tagged `STATIC — written 2026-06-04`.

**RG-0155** LOCKED (the class: an inventory exists and every colour is earned).
**RG-0156** OPEN — `orchestrator.html` is served live from the web root but is
**not in `deploy_manifest.txt`**; hand-uploaded, repo copy 79 days old. It also
hardcodes access code `96315` (launch gate G2, hard 29 Aug) behind a gate that
never executes, and renders any fetch failure as `"Nothing waiting on you. ✨"`.
Not executed here on purpose: shipping the stale repo copy would overwrite live
content, and rotating a live code is David's call.

**RG-0133 assertion strengthened** (not weakened): it used to grep for the literal
`CPX32 €15.49`, which could only catch one drifting number and sat green while
`€4.51/mo` contradicted it elsewhere. It now asserts the cost *feed* exists and
that no hardcoded monthly price survives anywhere in the markup. The new form
immediately caught a survivor the old one could not — the `€4.51/mo` hero tile.

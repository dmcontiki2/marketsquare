## 2026-08-29 — LISTING-AUDIT-1: listing-flow friction & AI-usage audit (RG-0205/0206/0207 opened)

David's launch-day question: is listing truly least-friction, is the AI optimally used, do we
need an in-flow help button? Audited the guided sell flow (ms.js sf*) against the live site
(live ms.js verified byte-identical to repo, index v549). Verdict: the photo-first skeleton is
sound (AI draft from main photo, skippable steps, saved drafts, score-gated publish), but three
defects were defined and opened in the regression ledger for post-freeze builds:

- **RG-0205 SF-AIDESC-1** — the flow discards vision-draft's AI-written description_draft;
  sellers publish a mechanical "Label: value" spec list.
- **RG-0206 SF-MULTIVISION-1** — sfRunVision sends 1 photo though the endpoint takes 1–12;
  secondary photos are never AI-read at draft time.
- **RG-0207 SF-COACH-ASK-1** — help-button question answered YES: coach bubbles are static,
  interactive AI is post-publish and paid, yet the EULA promises free everyday guidance.
  Fix = tappable coach avatar → free, rate-capped lane of the existing /advert-agent/coach.

Also flagged (no entry, smaller): email is requested at the very end via window.prompt —
should become an inline field earlier in the flow. No code shipped: launch-weekend deploy
freeze (28 Aug discipline). Ledger run this session: no regressions.

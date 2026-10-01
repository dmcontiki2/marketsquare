# I18N_READINESS.md — Localisation dry-run readiness plan (RUL-075)
**Status:** FROZEN build / ACTIVE preparation · **Readiness target: Fri 30 Oct 2026** · registered 30 Aug 2026

David's ruling (RUL-075): no live-app localisation work for two months, but 100% dry-run
test ready at the end of them, with really extensive sandbox testing before any rollout.
Everything below is a SIDE-ARTIFACT — nothing here touches a file the live app serves.

## What "100% dry-run ready" means — the checklist

1. **String inventory extractor** — a script that walks marketsquare.html + ms.js and
   emits every user-visible string with its location. Read-only; run repeatedly so the
   inventory tracks the app as it evolves during the freeze. Output: i18n/inventory.json
   + a count trend (a growing app means a growing extraction job — measured, not guessed).
2. **Rendered-text parity harness** — headless load of the app before/after any future
   extraction, diffing every rendered string. THE gate for Phase A: with only en.json,
   output must be IDENTICAL. Built and proven against the unmodified app first (a harness
   that has never caught a planted fault is a hope, not a gate).
3. **Pseudo-locale test** — a generated "translation" (lengthened, accented, bracketed:
   [Pȕbłïşh~~]) that catches layout breaks, clipped buttons and hardcoded strings without
   waiting for real translations. Runs in the sandbox only.
4. **Sandbox / staging environment** — a server-side clone behind the existing gate
   (own subdomain or gated path, own DB copy, own cache-buster), deployed by the same
   ONE_DEPLOY engine from a `staging` ref. This is where David's extensive testing
   happens; nothing is armed live that has not passed a full dry run here.
5. **Dictionary pipeline** — locales/en.json as source of truth; per-language files
   ES → PT → FR (measured order: +15.5% / +7.5% / +5.3%; together +28.4% at 3 years);
   Mandarin follows on the same rails for the diaspora (China itself stays horizon,
   RUL-071 — regulatory only, per David 30 Aug). Language NAMES in the switcher, not flags.
6. **Flags wiring plan** — the switcher ships dark behind /flags like the planner lane;
   arming is David's act, reversible by flag, never before item 4's full dry run passes.
7. **Planned ledger entries** — drafted OPEN entries: lang=en parity (locks at Phase A),
   sandbox-parity-with-live, switcher-dark-until-armed. No entry = not done.

## Phase map (unchanged from the accepted design)
Phase A extract strings (parity-gated) → Phase B add dictionaries (dead files) →
Phase C arm switcher (flag, reversible). A is the wide-but-shallow edit; it happens
only after the readiness date, only sandbox-first, only when David re-opens the build.

## What may be built during the freeze
Items 1–7 entirely — none are served by the live app. What may NOT happen: any edit to
marketsquare.html / ms.js strings, any locale file wired into the served bundle, any
switcher UI. RUL-075(a) freezes those until David re-opens the build.

## Triggers — readiness is measured, not remembered (added 1 Sep 2026)
- **Executable check:** `python3 scripts/i18n_readiness_check.py` — probes all 7 items
  (and defines the artifact contract for the unbuilt ones); exit 0 = dry-run ready.
  Re-runs the inventory extractor each time, so the trend stays alive.
- **Scheduled trigger 1 — mid-freeze checkpoint:** Thu 1 Oct 2026 09:00 SAST
  (task `i18n-readiness-midpoint`) — runs the check, reports gaps with a month in hand,
  progresses the next open item if the session can (side-artifacts only).
- **Scheduled trigger 2 — readiness-day verdict:** Fri 30 Oct 2026 09:00 SAST
  (task `i18n-readiness-day`) — READY / NOT-READY verdict. If READY, the one decision
  handed to David: open extensive sandbox testing. Phase A stays frozen until he
  re-opens the build after that testing passes (RUL-075 a/e).
- Build order for open items: 2 parity harness → 3 pseudo-locale → 5 en.json →
  6 flags plan → 7 ledger drafts → 4 staging (server work, sequenced deliberately).

## Lane 2 — UGC / introduction translation (RUL-086, added 1 Sep 2026)
Dictionaries translate the chrome; the INTRODUCTION is user-authored. Per RUL-086 the
design for runtime translation of listings, intro messages and dossiers lives in
i18n/UGC_TRANSLATION_DESIGN.md (store once + lang tag, translate-at-read via swappable
adapter, pay-once cache, hard monthly cap, machine-translated label with one-tap
original). **Readiness item 8** = that design present with its anchors (probed by
i18n_readiness_check.py). Lane-2 BUILD is sandbox-first alongside item 4; ARMING waits
for Phase C — users must have a language before their content can cross one.

## Checkpoint — Thu 1 Oct 2026 (mid-freeze run; PROBED by `python3 scripts/i18n_readiness_check.py`)
**4 of 8 done · 29 days to Fri 30 Oct.** Items 2 and 3 were built and proven in this run.
- **Item 2 — DONE.** `scripts/i18n_parity_harness.py` (`prove` / `check --candidate DIR [--langs en,af]` /
  `record` / `snapshot` / `compare`). Proof in `i18n/parity_proof.json`: clean pass identical within one
  walk and across two walks (29,361 strings, 45 states), three planted one-letter faults each caught
  exactly. Data fixture (gitignored, live adverts): `ledger_runs/i18n_parity_fixture.json`, rebuilt with
  `record` through the gate. The live `/i18n/translate` is never called (it can spend); the harness
  answers from `roles/app_i18n_<lang>.json`, so a dictionary edit is checkable in its own language.
- **Item 3 — DONE.** `scripts/i18n_pseudo_locale.py` → `i18n/locales/qps-pseudo.json` +
  `i18n/pseudo_locale_report.json` (coverage of the paint layer, layout breaks that appear only with
  longer text, inventory gaps, checked-dictionary coverage per language).
- **Measured context that changes item 5's shape:** since RUL-163 the live app already translates
  through a paint layer keyed by the English phrase itself (af/zu/xh/nso). Item 5's `en.json` is
  therefore the catalogue of English phrases that layer asks for (inventory + run-time phrases the
  pseudo test captures), not a key-per-string extraction of marketsquare.html/ms.js.
- **Still open:** 5 en.json → 6 flags wiring plan → 7 ledger drafts → 4 staging (server work; any spend
  or provisioning decision is David's).

## 2026-08-26 — Gemini canary arm-up run: key still absent, price row was wrong, eval set built

Scheduled arm-up run for RUL-032 (Gemini canary) on the day funds were expected for the
API key. **The canary was NOT armed — no `GEMINI_API_KEY` exists yet, so nothing could be
evaluated and nothing was switched.** RG-0121 stays OPEN and the RUL-033 reject-only
bridge stays UP: a photo that needs blurring is still rejected with "not anonymous —
replace it or leave it out". Everything below is the work that did not need the key.

**Live state, probed (not read off a doc):**

- `GET /health` → ok, v1.3.1. `GET /flags` → `mode: live`, AI lanes available:
  anthropic, openai, scaleway. **No gemini** — the lane is dark exactly as designed
  (RUL-032 keeps it out of `failover_order` and out of the /flags provider list).
- `GET /dashboard/bit` → pass 8/8.
- `/ops/selfcheck` carries `lanes_configured` but needs an API key, so key PRESENCE is
  not anonymously probeable. Absence is inferred from the code path
  (`_anon_scan_provider` requires `"gemini" in configured_lanes()`), not measured.
- GEMINI-CANARY-1 and PHOTO-REJECT-1 are both **deployed** (deploy ref `84f091c`,
  25 Aug 01:11) — the arming flip needs no further code.

**The gemini price row was wrong, and the RUL-032 costing was built on it.** The 19 Aug
row came from an OpenRouter capture at `$0.375 in / $1.50 out` with the out price flagged
in the row itself as an estimate. First-party `ai.google.dev/gemini-api/docs/pricing`,
read today: the **standard** tier — the tier `ai_provider._gemini`'s synchronous
chat/completions call actually bills at — is **$0.75 in / $3.75 out** through 31 Dec 2026,
stepping to **$1.50 / $7.50 on 1 Jan 2027**. `$0.375` is Google's *batch* input rate.
Input understated 2x, output 2.5x. Corrected in `ai_price_card.json` (card v2026-08-26.1,
`source_kind: first-party`, with the 2027 step and the batch/flex rates recorded
separately) and re-costed in `AI_PHOTO_COST_MODEL.xlsx` → "Pricing (Aug 2026) swap":

| | modelled 19 Aug | corrected 26 Aug | from 1 Jan 2027 |
|---|---|---|---|
| Gemini full switch, year-1 | $224 | **$529** | $1,058 |
| CANARY (gemini scans+refines, terra verifies), year-1 | $548 | **$845** | $1,256 |
| terra-only today (the lane that failed) | $1,729 | $1,729 | $1,729 |

**The decision does not change** — the canary is still ~51% cheaper than terra-only and
is still the zero-leak-risk step. What changes is the margin, and it narrows to ~27% at
the January price step. That is a re-cost, not a re-decision, so RUL-032 stands.

Model id `gemini-3.7-flash` verified GA/stable first-party (image + PDF input, structured
outputs, 1,048,576 in / 65,536 out) — the wired id is correct.

**New: `scripts/build_eval_set.py`** — Switch Test Plan step 0, so the eval is one command
the moment the key lands. Builds `eval_photos/` reproducibly (`--verify` re-builds to a
temp dir and diffs sha256; 22/22 byte-identical) with `TRUTH.json` as the answer key:
9 synthetic plate shapes (tiny background plate, ±skew, personalised word plate, two
plates in one frame, low light, motion blur, partial occlusion), **3 false-positive
traps** (road sign, price sticker, a car with no text at all), the 5 listing-246
originals, and 5 off-category stock photos. The traps carry as much weight as the plates:
RUL-031 is a ruling about **over**-smearing, so a set of plates alone would score the
wrong failure.

**Privacy defect found and fixed:** `eval_photos/` and `private_originals_listing246/`
were untracked but **not gitignored** — a `git add -A` would have pushed a real seller's
photos, real plates included, to the GitHub mirror. Both now ignored.

**Ledger:**

- **RG-0184 (new, LOCKED)** — no AI lane that can take traffic is priced from an
  aggregator or an estimate; first-party or it does not bill. RG-0018 already checked the
  card was *fresh* and *covering*; nothing checked a price was *first-party*, which is how
  a $548 figure got into a ruling. 7 rows checked, all pass.
- **RG-0185 (new, OPEN)** — the eval set rebuilds byte-identical and every row it scores
  has a truth label. OPEN, and correctly red on three counts: the five listing-246 rows
  are still `expect: unknown`, the 19 Aug Maroushka failure photos are absent (server-side
  uploads — the freshest evidence of the fault), and the 3 "inappropriate" samples are
  missing. 22 photos against the plan's ~30.
- RG-0121 unchanged (OPEN, canary not armed). RG-0122 green — bridge up and holding.

**Unrelated, found while probing and not fixed here:** `post_deploy_status.json` from the
24 Aug 23:13 deploy shows `migration:033_csp_verify_served.py` **failed and jammed the
chain** — later migrations were skipped. The migration restored cleanly and did not claim
success, so the site is as it was, but anything queued behind 033 has not run. RG-0178/0180
(CSP script-src not enforced at the edge) are the entries sitting on the other side of that
jam.

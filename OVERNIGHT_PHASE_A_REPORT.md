# Overnight Build Report — Tiered Grading Phase A
**Run:** night of 3→4 June 2026 (autonomous) · **Scope:** the purple "▶ The overnight build (Phase A)" section of `TIERED_GRADING_DESIGN.html`, and only that.
**Outcome:** ✅ Complete. All five scope items shipped, non-destructively, flag-gated OFF for buyers. Nothing buyer-facing changed.

---

## 1 · What was built

**a) BEA columns (additive migration).** Four nullable columns added to the idempotent `listings` migration loop in `main.py`, after `era_year`:

| Column | Type | Meaning |
|---|---|---|
| `ai_grade` | TEXT | Tier-1 grade from the vision model (descriptive vocab) |
| `ai_grade_conf` | REAL | Confidence 0–1 |
| `ai_grade_notes` | TEXT | One-line rationale (≤120 chars) |
| `grade_tier` | INTEGER | Which rung the listing is on (1 = AI-from-photos) |

The existing seller-facing **`condition` column was not modified** in the schema or the data.

**b) Vision grader helper.** `grade_card_condition(photo_urls, thumb_url, medium_url)` in `main.py`. It mirrors the existing card-vision path — `VISION_MODEL = claude-sonnet-4-6` (the model `ai-batch-cards` already uses, since "Haiku lacks vision depth for cards") and the `ANTHROPIC_API_KEY` env var — fetches up to 3 of a listing's photos, and returns strict JSON `{grade, confidence, notes}` with a conservative, indicative TCGplayer-style read. It **fails soft**: missing key, no photos, fetch failure, timeout, or bad JSON all return `grade=None` with an `error` string rather than raising.

**c) Graded the existing Collectors cards.** A one-off server script (`/root/phase_a/grade_cards.py`) graded all **26** Collectors cards (hard cap 40) and wrote results to the **new fields only**, with `grade_tier=1`. `condition` was never in the UPDATE statement.

**d) Private review page** at **`/grading-review`** — Basic-Auth gated, shows each card's photos beside its AI grade / confidence / notes and the existing `condition` for comparison. Not linked from the buyer app.

**e) Buyer-facing display stays OFF** behind `SHOW_AI_GRADE_TO_BUYERS` (default `"0"`). No buyer surface reads `ai_grade`.

---

## 2 · The review page — how to open it

**URL:** https://trustsquare.co/grading-review

**Login:** username **`david`**, password = the value of **`MS_ADMIN_PASSWORD`** (your existing admin password — viewable with `systemctl cat marketsquare` on the server, in the `Environment=` lines). No new secret was created or stored on the box.

The page sorts ungraded last and **lowest-confidence first**, so the reads most worth eyeballing are at the top. Cards where the AI grade differs from the on-file `condition`, or where confidence < 60%, carry a coloured flag.

> Note on the auth approach: the orchestrator page is gated by **nginx** Basic-Auth. To keep this change **self-contained to the BEA and fully reversible** (no nginx edit overnight), `/grading-review` enforces Basic-Auth **inside main.py** instead, reusing your admin credential. Same protection, one fewer moving part to roll back. If you'd prefer it behind the same nginx realm as `/orchestrator` (`.htpasswd_orch`), that's a small follow-up.

---

## 3 · Grading results

- **Graded:** 26 / 26 · **Errors:** 0
- **Distribution:** Lightly Played **23**, Near Mint **2**, Heavily Played **1**
- **Token cost:** ~21,684 input + ~1,388 output tokens across 26 vision calls (order of **US$1**).

**Observation for your review:** the model clustered hard on **Lightly Played at 0.45–0.55 confidence**. That is the *conservative* behaviour the prompt asked for (when in doubt, grade down and lower confidence), but it means the vocabulary spread is narrow. This is exactly the kind of thing Phase B tunes — prompt, vocabulary, and the confidence threshold — before anything goes live.

**Lowest-confidence cards to eyeball first** (all 0.45, all Revised dual lands):

| ID | Card | AI grade | Conf | Note |
|---|---|---|---|---|
| 163 | Tropical Island Dual Land (Revised) | Lightly Played | 0.45 | Surface wear/scratching; edges slightly worn |
| 165 | Savannah Dual Land (Revised) | Lightly Played | 0.45 | Surface scratch/reflection line across art |
| 166 | Scrubland Dual Land (Revised) | Lightly Played | 0.45 | Surface clean but vintage; corners/edges |
| 167 | Plateau Dual Land (Revised) | Lightly Played | 0.45 | Borders slightly worn; possible edge whitening |
| 168 | Taiga Dual Land (Revised) | Lightly Played | 0.45 | Corners slightly worn; old border |

**One notable disagreement:** card **163** (Tropical Island) has `condition = "Heavily Played"` on file but the AI read **Lightly Played** — i.e. the AI was *more lenient* than the human label here (and at low confidence). Worth a look; the review page flags it as both low-confidence and a `condition` mismatch.

Full per-card data: `/root/phase_a/grade_results.json` on the server (also has the run log at `/root/phase_a/grade_run.log`).

---

## 4 · Safety confirmations

- **`condition` untouched.** Pre- and post-run distribution identical: 19 null, 6 Near Mint, 1 Heavily Played. The UPDATE only ever wrote `ai_grade`, `ai_grade_conf`, `ai_grade_notes`, `grade_tier`.
- **Buyer-facing OFF.** `SHOW_AI_GRADE_TO_BUYERS` is unset on the server → defaults off. `ai_grade` appears nowhere in `index.html` or `ms.js`. No buyer-app files were edited.
- **No FEA drift.** `index.html`, `ms.js`, `ms.css`, `admin.html` untouched (mtimes predate this run). `fea_baseline.json` deliberately **left as-is** and **no `ms.js?v` bump** — this change is BEA-only, so the 03:30 Sensor should stay quiet without masking a real change. *(This intentionally follows the scheduled-task instruction over the design doc's prose, which had said to refresh the baseline.)*
- **BEA health.** Restarted; `/health` returns `{"status":"ok", ... "version":"1.3.1"}` — version string unchanged, as required.
- **No leakage.** 0 non-Collectors rows received an `ai_grade`.

**Reversibility — backups taken before any change (on the server):**
- `main.py` → `/var/www/marketsquare/main.py.bak.20260603_224151`
- DB → `/var/www/marketsquare/marketsquare.db.bak.20260603_224429` (consistent online snapshot via SQLite backup API)

**Local sync:** the verified server `main.py` was copied back to `C:\Users\David\Projects\MarketSquare\bea_main.py` with **sha256 parity** (`29f2ffb4…3051bb` on both).

---

## 5 · Skipped / not done (by design)

- **No git commit/push** — left for you (per CLAUDE.md and the task). `bea_main.py` and `CHANGELOG.md` changed locally and are ready to commit.
- **No `STATUS.md` / dashboard / baseline write-back** — outside Phase A scope; the task said build only the five items. (If you want the dashboard to reflect this, that's a normal session-end step you can run.)
- **Helper added but not yet wired to listing-time grading** — Phase A only backfills + reviews. Wiring the grader into the sell flow is Phase B/C.
- **Slight, intentional code parallel:** the one-off `grade_cards.py` carries its own copy of the grading logic rather than importing `main.py` (importing it triggers the heavy module-level geo-seed). It is identical to the BEA helper; if you'd rather have one source of truth, factor the grader into a tiny shared module both import.

---

## 6 · Suggested next steps (Phase B)

1. **Open `/grading-review`** and judge the AI's eye against the real cards — start at the top (lowest confidence).
2. **Tune before going live:** the heavy clustering on "Lightly Played" suggests the prompt/vocabulary/threshold need a pass. Decide a minimum confidence below which a card shows "needs verification" rather than a grade.
3. **Flip the badge on** for cards only when you're happy: set `SHOW_AI_GRADE_TO_BUYERS=1` and wire a small, clearly-labelled "AI-assessed from photos — not certified" badge in `ms.js` (with the tier shown so an AI read is never mistaken for a cert).
4. **Wire grading into the sell flow** so new card listings get a Tier-1 grade at publish (one vision call each).
5. **Then Phase C+:** Tier-2 cert capture (PSA/BGS/CGC fields + badge), and feed `grade_tier` into Trust Score and the Audit Function trail.

*Compare this report against `TIERED_GRADING_DESIGN.html` and the live `/grading-review` page — together they're the shared starting point for your Phase B feedback.*

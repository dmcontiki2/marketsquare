# Canon Addendum 1 — Founders Badge — REV 3 BRIEF (prepared 15 Jun 2026)

**Status:** decision made by David (15 Jun 2026); operational surfaces updated; the canon `.docx` itself still needs formal regeneration to **rev 3** via its generator. This brief is the spec for that regeneration. Do **not** hand-edit the `.docx` body — its whole tier table is pre-Simpler-Model and should be regenerated, not patched.

## The decision

The Founders Badge ("Ruby Spark") now mints **only on the $20 Pro subscription** during the launch window. This **supersedes rev 2** (6 Jun 2026), which minted on **$40 Business / $100 Elite**.

**Why it changed:** the *Simpler Model* (adopted 9–10 Jun 2026, i.e. *after* rev 2) retired Business and Elite to "legacy — existing users only, not offered to new sellers." Rev 2 therefore left the badge minting on tiers a new launch seller can no longer buy. Moving minting to **$20 Pro** (a current, sellable tier) closes that gap. Everything else about the badge is unchanged: launch-window only (hard close `LAUNCH_SPECIAL_DEADLINE = 2026-08-01`), ID-bound (one human, one badge), non-transferable, minting disabled at close with no override, never repeated.

## Surfaces already updated to $20 Pro (15 Jun) — canon must ratify these

- `MarketSquare/launch_redemption.py` → `QUALIFYING_TIERS = ("pro",)` + docstring.
- `CityLauncher/emailer/launch_codes.py` → minting line now "$20 Pro (Free / Starter excluded)".
- `MarketSquare/n8n/email_templates/*.html` — 14 templates (badge block → $20 Pro; bonus "12 instead of 10 Tuppence monthly on Pro").
- `CityLauncher/emailer/templates/*.html` — 14 templates (same; mirror restored byte-for-byte against MarketSquare).

## What rev 3 of the canon doc must contain

1. **Qualifying action:** "Subscribe to the **$20 Pro** tier during the launch window." (was: "$40 Business or $100 Elite").

2. **Tier table — replace the whole table** (rev 2 still shows the pre-Simpler-Model 5-tier set). Rev 3 canon table = the live `/subscription/tiers`:

   | Tier | Price/mo | Slots | Monthly Tuppence |
   |---|---|---|---|
   | Free | $0 | 2 | (free allowance) |
   | Starter | $5 | 10 | 2T |
   | Pro | $20 | 30 | 10T |
   | Agency | free + verified | 10 base (trust-graduated 10→100→500) | — |

   Legacy (existing users only, not sold to new sellers): Standard $12, Professional $20, Business $40, Elite $100.

3. **Founders bonus on Pro:** Pro's 10T → **12T** (×1.2, rounded up — same maths as rev 2: 6→8, 10→12, 20→24, 50→60). Honoured on any paid plan for life after minting; pauses/downgrades keep the badge, the normal free Tuppence applies while paused.

4. **Supersession table — add a rev 3 row:** rev 3 supersedes rev 2's **$40 Business / $100 Elite** qualifying tiers and the "24/60" bonus wording. (Unchanged from rev 2: the $2 anchor / price÷2 allocation principle, the Ruby Spark spec, the enforcement architecture, one-badge-per-human.) Note for the chain: the whitepaper-era **$15 International** tier was already retired by rev 2; rev 3 does **not** revive it.

## WhitePaper handling (do NOT edit the published disclosure)

`Codices/TrustSquare WhitePaper v2.docx` §9 is a published defensive disclosure (21 Apr 2026) and must never be silently edited. Record the change in the **next** whitepaper/codex version: the qualifying tier is now **$20 Pro**, superseding both the whitepaper's $15 International and rev 2's $40 Business / $100 Elite. The fixed-$2 principle and the enforcement architecture remain reaffirmed.

## Open flags

- **Regenerate the `.docx`** via the addendum generator (`outputs/build_addendum2.js` per the CityLauncher log) rather than hand-editing. I can do this on request.
- **Slot/name reconciliation:** rev 2 listed "$20 Professional · 25 slots"; the Simpler Model's $20 tier is "Pro · 30 slots." Rev 3 uses **Pro / 30 slots** (per the live app). Confirm 30 is correct.
- **EULA is separately stale (older than the canon doc):** `eula_clean.html` / `eula_raw.html` (and the `TrustSquare_EULA_*.docx` set) still show the April-era **$0 / $5 / $15** tiers (Free / Starter / "Premium $15"), which the 6-Jun note said "must feature nowhere." This is legal, customer-facing text and needs its own update to the Simpler Model — recommend doing it with counsel review.

*Prepared by Claude. Operational code/email changes are git-tracked and revertable; this brief governs the canon-doc regeneration, which has not been auto-applied.*

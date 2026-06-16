# Deploy & Push runbook — Pricing-canon alignment + TrustSquare rebrand (15 Jun 2026)

Use this as your checklist (or paste sections to a deploy agent). **Nothing here is auto-deployed** — every change is local and git-tracked except the `n8n/` templates (gitignored) and `Codices/` (not a git repo).

## What changed this session
- **Brand:** MarketSquare → TrustSquare across seller-facing text (server codenames `/var/www/marketsquare`, systemd, nginx, db left intact on purpose).
- **Pricing pinned to the live code, end-to-end:**
  - **Seller:** Free $0·2slots · Starter $5·10·2T · Pro $20·30·10T · Agency free+verified·10base. Legacy $12/$40/$100 = existing users only.
  - **Buyer:** Free $0 (local) · Global $5/mo (R90, national+global). The 3-tier $0/$5/$15 "sessions/day" model is retired (code is `_buyer_tier` → free|global; `WISHLIST_GLOBAL_USD = 5`).
  - **Founders Badge (Ruby Spark):** mints on **$20 Pro** (was $40/$100 Business/Elite); Pro bonus 10→12T. `QUALIFYING_TIERS = ("pro",)`.
- **Canon Addendum №1 → rev 3** (rev 2 archived as `..._rev2_SUPERSEDED_2026-06-06.docx`); audit/register/CC-002 draft reconciled; EARLY pre-provisional email variants added.

## ⚠️ Pre-flight — READ before committing MarketSquare
25 files show as **staged for deletion but are still on disk** (untracked) — e.g. `static/founders_spark.svg` (the Ruby Spark asset), `tier_resolvers.py`, `value_resolvers.py`, `test_tier_resolvers.py`, `test_ai_service_tiers.py`, `support.html`, `smoke_test.py`, `start_marketsquare.bat`, `wonders.json`. This is a pre-existing `git rm --cached`-style state, **NOT from this work**. A blind `git commit` would drop them from GitHub.
→ **Fix:** `git add -A` re-stages the on-disk copies and cancels the deletions. Do this (then `git status` to confirm they're no longer "deleted") unless you deliberately untracked them.

## Repo routing
| Target | Branch / remote | What changed | Action |
|---|---|---|---|
| **MarketSquare** | `main` · `github.com/dmcontiki2/marketsquare.git` | 15 tracked files (below) + new canon files | commit + push |
| **MarketSquare `n8n/`** | — (**gitignored**, `.gitignore:52`) | 14 badge-fixed templates + 3 `*_EARLY.html` + `_EARLY_OUTREACH_README.md` | **deploy to n8n** via `deploy_n8n_templates.bat` — not git |
| **CityLauncher** | `master` · `github.com/dmcontiki2/citylaunch.git` | `emailer/launch_codes.py` + 14 templates + CHANGELOG + PRINCIPLE_REQUIREMENTS + `orchestration/strategist_agent.py` | commit + push (review the last two) |
| **AdvertAgent** | `master` · `github.com/dmcontiki2/advertagent.git` | `PRINCIPLE_REQUIREMENTS.md` (A7); also CHANGELOG.md, `service/advert_agent.py` modified | review + commit + push |
| **Codices** | **not a git repo** | CODEX_EVOLUTION_AUDIT.md · PRINCIPLE_REQUIREMENTS.md · Solar_Council_Consolidated_Master_View.html · Solar_Council_Vision_Map.html | on disk only — sync by your usual mechanism (Obsidian/backup) |

**MarketSquare tracked files changed:** launch_redemption.py · marketsquare.html · ms.js · eula_clean.html · eula_raw.html · APP_PREVIEW.html · Solar_Council_Vision_Map.html · docs/PRINCIPLE_REQUIREMENTS.md · docs/LISTING_STATE_MACHINE.md · CHANGE_REGISTER.md · PARKED_AUCTIONS.md · PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md · Patents/Canon_Addendum_1_FoundersBadge.docx (+ untracked: rev2_SUPERSEDED + REV3_BRIEF).

## Commit & push
```bash
# --- MarketSquare ---
cd /path/to/Projects/MarketSquare
git add -A                 # re-tracks on-disk files; cancels the accidental deletions
git status                 # REVIEW — confirm founders_spark.svg / tier_resolvers.py / tests are NOT deleted
git commit -m "Pricing canon: seller Free/Starter\$5/Pro\$20/Agency + buyer Free/Global\$5; Founders Badge mints on \$20 Pro (Canon Addendum №1 rev 3); TrustSquare rebrand"
git push origin main

# --- CityLauncher ---
cd ../CityLauncher
git add -A && git status
git commit -m "Founders Badge mints on \$20 Pro (rev 3); launch_codes.py + 14 templates aligned to pinned pricing"
git push origin master

# --- AdvertAgent ---
cd ../AdvertAgent
git status                 # review CHANGELOG.md + service/advert_agent.py before adding
git add PRINCIPLE_REQUIREMENTS.md
git commit -m "A7 buyer tiers pinned to Free/Global \$5 (Simpler Model)"
git push origin master
```

## Server deploy (the live functional change)
The badge-minting change lives in `launch_redemption.py`. **The live site still mints on $40/$100 until you deploy.** Upload to `/var/www/marketsquare/`:
- `launch_redemption.py`  → then **restart the FastAPI BEA** service.
- `marketsquare.html`, `static/ms.js`, `eula_clean.html`, `eula_raw.html` (buyer table + brand + badge copy).
- Run `deploy_n8n_templates.bat` for the n8n email templates.
- **Cloudflare cache purge**, then smoke.

## Tests (restore first — they're staged-deleted but on disk)
```bash
git add test_tier_resolvers.py test_ai_service_tiers.py
python -m pytest test_tier_resolvers.py test_ai_service_tiers.py -q
```
Note: `smoke_test.py` had a pre-existing SyntaxError (~line 158) flagged in the CityLauncher log — fix or skip.

## Post-deploy verification
- `GET /subscription/tiers` → free/starter/pro/agency at $0/$5/$20/$0, slots 2/10/30/10.
- Buyer "Upgrade to Global · $5/mo" works; `_buyer_tier` returns `free|global`.
- A **Pro** subscription in the launch window mints the Founders Badge (not $40/$100).
- Live EULA §6.2 shows **Free / Global $5** (no $15 Premium, no "sessions per day").
- 200s on index/admin/dashboard; Cloudflare purged.

---
*Generated 15 Jun 2026 from this session's work. Seller pricing, buyer pricing, the badge tier, and the canon are consistent across all four repos in the working tree; this runbook makes them live.*

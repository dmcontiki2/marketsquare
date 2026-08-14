## 2026-08-14 — SUPER-AFRICA-1: Kenya super-advert stills complete (114/114)

Finished the Kenya super-advert photo ladders — the final 54 stills generated, brand-checked and
claimed into `assets/super/`. All 9 Kenya tiers (adventures experiences, adventures accommodation,
cars, property, tutors, local market, collectables, services) now hold complete photo sets, which is
the condition `post_deploy` seeds on.

Verified: 114/114 expected filenames present, no missing, no extras, no duplicate content, all valid
JPEGs. Three frames rejected and re-shot on brand grounds (a visible face; two collage compositions).

Also landed this session:
- **GRANT-KILL-1** — `claim_super.py` / `claim_photos.py` now claim from `MarketSquare/_incoming`
  inside the always-mounted Projects tree, retiring the per-session Downloads folder grant that had
  been stalling every photo run at image 1. New canon: `PREFLIGHT_GRANTS.md`.
- **DUP-CLAIM-1** — `claim_super.py` refuses any candidate whose content hash already exists in
  `assets/super`, catching the failure where a Download that doesn't fire makes Chrome re-save the
  previous image under a new "(1)" filename.

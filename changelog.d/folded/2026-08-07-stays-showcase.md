## 2026-08-07 — STAYS-SHOWCASE-1: the fourth trio built (OPEN_LOOPS D8), staged not shipped

**Photos — 15 of 15, done.** David-assisted Higgsfield run (Nano Banana Pro, 3:2, 1 image/gen,
2 credits each). Three properties x five frames, each set locking one building description so the
same property carries through every frame: `sup_email_thatch_*` (Pilanesberg — main/room/pool/
breakfast/game), `sup_email_jacaranda_*` (Hartbeespoort — main/room/deck/breakfast/dam),
`sup_email_marula_*` (Magaliesberg — main/tent/boma/deck/sunrise). All 15 audited at 1200x805,
131-258KB, inside the size band of the existing nine. PHOTO-ANON-1 honoured throughout (people
from behind or silhouetted only). Prompts + run settings recorded in `STAYS_HIGGSFIELD_PROMPTS.md`
so any future session can regenerate a frame without reverse-engineering the wording.
- Higgsfield queue wedged ~25 min on frame 2 (normal 50-60s); survived a full page reload, so it
  was genuinely server-side. Waited it out per the runbook rather than double-firing. It cleared.
- The freshness guard REFUSED one claim: floor was set to the previous file's own mtime and caught
  it on the boundary, so two candidates appeared where one was expected. Tightened to strictly-above
  and each claim now advances it. This is the guard doing exactly the job it was written for after
  the 26 Jul mis-assignment; Downloads held 267 stale hf_*.png the whole run.

**Adverts — script + migration written, NOT run.** `scripts/create_stays_showcase_adverts.py`
(153 lines) + `migrations/009_stays_showcase_adverts.py` (21 lines), both py_compile green.
Clones the ZA advacc exemplar 271 and ABORTS UNTOUCHED if 271 is not `adventures_accommodation`.
Born-clean by construction, each choice traceable to a prior fault:
- CLONE_JUNK guard nulls 40 foreign-category columns by name (vehicle/property/collector/tutor/
  rental), filtered against the live schema so a missing column cannot crash it — migration 002
  had to heal six rows for exactly this.
- `super_example=0`. Deliberately NOT following `mark_showcase_supers.py` (29 Jul), which migration
  002 reversed on 2 Aug: SUPER-PIN-1 pins super rows above every sort, so a super showcase advert
  outranks real sellers. The 29 Jul marking was the error, not the pattern.
- `price_num` set explicitly; price carries a "/ night" basis (adventures_accommodation is in
  RATE_UNIT_CATEGORIES — a bare amount is rejected 422 by `_validate_price_unit`).
- No attestation stamp, no linked wonders. Seller reuses `showcase-email@trustsquare.co` (RG-0008
  normalises adventures* to one family, so no new seller row is invented).
- `listing_lat`/`listing_lng` carry the concept map's pins, so the D8 map's B&B layer can read real
  coordinates off the DB instead of hardcoding them.
- Suburb stays a Pretoria-metro suburb with the real place in the TITLE — the established pattern
  (cf. "Hot Air Balloon Safari · Hartbeespoort" / Centurion).

**Email track — located, one safe edit made, rewrite NOT attempted.**
- FOUND: the four flipped templates are not in this repo. They live in
  `CityLauncher/emailer/templates/` — `agency`, `cars_dealer`, `tour_guide`, `travel_agency`
  are the exact four carrying `?listing=`. `adventures_accommodation_outreach.html` is NOT a dead
  filename: it is alive there, wired into the sender at `emailer.py:62`, and is a live wave-1 track.
- FOUND: its showcase section (lines 189-279) is not missing — it is THREE MOCKUP CARDS of listings
  that do not exist ("Waterberg Private Lodge", "Boutique Hotel · Cape Town", "Sossusvlei Desert
  Lodge"), hand-typed prices in a format the app itself would reject ("24000 /night"), no deep links.
  Its card photos are HOTLINKED FROM UNSPLASH — every sibling self-hosts at `/static/phone_*.jpg`
  and inlines them as CID. That reaches a third party at open time and leaks recipient IPs; RG-0025's
  spirit, though its literal scope is app pages. Template last touched 15 Jun, seven weeks behind
  its siblings. Its intro button already reads "Request Introduction · 1T" — correct, left alone.
- DONE: `flip_showcase_hrefs.py` extended with `thatch`/`jacaranda`/`marula` -> the stays template
  (9 cards now; CARD_IMG and CARD_TPL key sets asserted equal; timestamped .bak taken).
- NOT DONE, deliberately: swapping the three fake cards for real deep-linked phone cards. It is a
  visible change to an email that goes to B&B owners and wants David's eye, and the 352x728 phone
  cards still have to be built from the new photos.

Regression ledger, closing: **38 entries · 36 holding · 0 REGRESSED · 2 open · exit 0** (from the
vantage that can reach the live site; the two open are the long-standing RG-0003/RG-0004).
Cost model impact: none. Nothing deployed — no /tsl this session.

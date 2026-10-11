## 2026-10-11 — Bee Lady adverts upgraded + third advert (BEE-LADY-3)

David, 11 Oct 2026: upgrade Marietjie's adverts with new pictures, prices from David, text from her CV, and her new base.
- Pictures made with Grok Imagine 2.0 via the Higgsfield API ($0.50 total): bee_6_talk (boma talk, her face from
  David's emailed photos), bee_7_course (field course, hops + sea), bee_8_audit (farm hive audit). Real photos added:
  bee_9_apiary (Marietjie 2.jpeg), bee_10_frame (David's frame photo). All in assets/super + /static/super.
- #275 Bee Talks: R 100 per person, new text, photos bee_6/1/4.
- #274 Beekeeping course: "On demand — tailored to your group" (was R 1 200), new text, photos bee_7/10/9.
- NEW #538 Beehive Audit & Consulting for farms (Services/Technical, "Beekeeping consultant"):
  R 4 000 per audit + transport & accommodation outside the George area; on her account (marietjie.marais59@gmail.com).
- #273/#274/#275/#538 moved to Great Brak River / Mossel Bay (geo 136, area Garden Route); Pretoria POIs and legacy
  auto-linked wonders cleared (Tutors/Services/LM are outside the 12 Jun wonder allowlist).
- Credentials text now matches her CV (NBA Secretary since 2016, SABIO, DALRRD 2025, 10 yrs); the unsupported
  "national secretary" and "Gauteng government appointment" claims removed.
- Server DB backup: marketsquare.db.bak-<ts>-beelady-upgrade. Verified rendered on trustsquare.co/?listing=274/275/538.
- ZA-wide reach (David, 11 Oct: "her adverts are not area bound"): #273/#274/#275/#538 extended via listing_cities to all
  13 other active ZA cities (tester exception to the paid multi-city rule, like her tester grant).
- **LM-REACH-1** (bea_main.py lm_list_listings): the Local Market list now honours listing_cities, as the main browse
  already did -- before, an LM advert showed only in its own city. Patched in place on the server (main.py.lastgood
  saved, compile OK, restart active, /health 200); verified /local-market/listings?city=Pretoria|Durban|Cape Town -> 273.
- OPEN DECISION put to David: reach for free sellers (nationwide flag vs paid multi-city).

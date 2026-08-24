## 2026-08-24 — WAVE_SEND_PLAN.xlsx: the lists checked against RUL-053; CAT-ALIAS-1 wrong-template fix

- Live pull from the CityLauncher prospects API (3,241 listed; scraper running concurrently —
  stats reported 4,237). Workbook WAVE_SEND_PLAN.xlsx: 98 plan cells day-by-day, 653-address
  send queue with per-row template hyperlinks, 90-cell Scrape TODO, agency reserve (401),
  131 suspect emails parked (typo TLDs, image-strings, rejected rows).
- VERDICT: plan not yet covered — STAYS only in Pretoria (197 valid; 13 other cities 0-3);
  PROPERTY singles never scraped (0 anywhere); TUTORS deep (DBN 662, PMB 640; global three
  ~20 each); Services unsplit casual/technical (queue carries keyword-suggested class).
- CAT-ALIAS-1: n8n templateMap gained aliases for the scraper's real category names
  (teachers_trainers, adventures_accommodation, Services, Collector Shops...) and the
  unmapped-category fallback now DROPS instead of sending property_outreach to everyone —
  2,300+ prospects would have received the wrong template. n8n must RE-IMPORT the workflow
  JSON (runbook precondition). RG-0175 strengthened to tripwire both.

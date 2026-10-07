## 2026-10-07 — PROMOTER-TRACK-1: promoter links and complete-unit counts (RUL-212)

- New: a promoter's own link `trustsquare.co/p/<CODE>` (made from the dashboard's Comms page). It remembers the code in a cookie and opens Quick.
- A person who then publishes her FIRST advert (Quick one-tap publish or the main app) is stamped as that promoter's lister. Existing listers and the promoter himself are never stamped.
- Buzz now records the first delivered Buzz in each direction for stamped listers (survives the Buzz log trim).
- A unit is complete only when her advert is live AND Buzz was delivered both ways with one referral (not the promoter, not another of his listers, each referral used once).
- Dashboard → Comms → Promoters: make a link, copy it, pause/resume, see the funnel (listers, advert live, brought someone in, Buzz one way, complete) and each lister's state. Counts only — no money shown anywhere (RUL-212).
- Schema: three new tables (promoters, promoter_signups, promoter_buzz); nothing existing changed. Routes declared in route_policy.json. Ledger RG-0934.

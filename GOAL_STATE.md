# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it short: it is a state file, not a
diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the why.*

---

## RUN 34 — Fri 9 Oct 2026, 20:56–21:35 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; a stray `.goalrun_wtest` probe file sits in the laptop repo root).
  Built in server worktree `/root/w34` (removed at the end), shipped `claude/goal-run34` 8274749 via CLOUD-SHIP-1 (21:24Z SHIPPED,
  page `ms.js?v=1009&m=1`). Plain `/` from Cloudflare still handed out v=1008 for a few minutes — check with `/?fresh=…`.
- **Walk (Collectors / goods, a Johannesburg trading-card seller, `docs/E2E_2026-10-09.md`):** cold Home → Sell → Collectors →
  photo (read in ~20 s, score 64) → six steps → score 70 in ~3 min; stopped at Publish. No errors. **Break:** the photo read
  pre-filled Provenance & history with "…No maker, set name, year, signatures, or authentication markings are legible in the
  photo." under "buyers will read it as written" — AI-DESC-SHOWN-1's cleaner missed "legible … in the photo". **Friction:** every
  Collectors example was a coin (name "1892 ZAR Kruger 2½ Shillings", year "1892, Victorian", maker "Pretoria Mint") for a card
  seller. Both fixed and proven live (GI-0033).
- **Number: 0.** Live 141 = 132 `*@trustsquare.co` + family 9 (David Jnr 3, Marietjie 3, Maroushka 2, David 1 — new #537
  Collectors, Pretoria, dmcontiki2@, 15:52Z). **By a stranger's hand: 0.** No new user rows since 7 Oct.
- **Where people stop:** no strangers. The only bot=0 sessions on 9 Oct were **GoogleOther** (Google's fetcher, Nexus 5X UA)
  running Quick three times and hitting `q_api_fail` / `q_error` — counted as people because its name has no "bot". Now flagged
  (FUNNEL-GOOGLEOTHER-1); its 15 rows since 25 Sep re-flagged bot=1 (ids in `/root/goal34_googleother_ids_were_bot0.txt`).
- **Shipped (8274749):** GI-0033 COL-KIND-WORDS-1 + AI-DESC-CLEAN-2 + FUNNEL-GOOGLEOTHER-1, RG-0952 LOCKED. **Live proof (21:27Z,
  fresh phone, v=1009):** Trading cards → "e.g. 2003 rugby card set, 24 cards", "e.g. 2003, first series", "e.g. Panini, Topps",
  grading "e.g. PSA 9, BGS 9.5"; switched to Stamps → "e.g. 1926 Union ½d pair…", "e.g. Government Printer", her typed year kept;
  Provenance held only buyer-facing sentences. Cleaner on the walk's exact text drops the "legible in the photo" sentence.
- **Ledger:** new tree 3 !!!!, base `/opt/marketsquare-src` the same 3 — RG-0154 (counter behind; refreshed 221 → 222 in this
  commit), RG-0949/RG-0950 (trainer pictures are gitignored, absent from server checkouts; served live 200 — vantage, not a fault).
- **REVIEW NOW:** empty.
- **QA data:** none created (no save, no account).
- **Not reached:** outreach sends/opens (no record on the server: `outreach_ledger` and `prospects.db` empty).

## RUN 33b — Fri 9 Oct 2026, 00:15–00:50 UTC (Opus 5.5, David live: "fix the regression issues; GI-0020 go with a; housekeeping as suggested; let a new lister add her photo by tapping the example")

- **Shipped (f8516bd, CLOUD-SHIP-1 00:39Z):** GI-0032 QUICK-OWN-PHOTO-1 + HUB-ADD-PHOTO-1 + LANG-ONE-HOME-1, RG-0947 LOCKED.
  **Live proof (00:41Z, fresh phone, real save):** draft card shows "EXAMPLE PHOTO" + "📷 Tap to add your own photo"; a camera pick
  replaced the picture, ring 60 → 70; Save → arrival card shows her photo and "✓ Your photo is on your listing."; draft #536's
  `thumb_url` / `photo_urls` / `[photos:]` carry the R2 upload; the letter's link opened the Hub with her photo on the card. Home: one
  language button (the header globe opens the menu under the header; the floating pill stays on other screens).
- **Ledger clean:** 0 !!!! on the new tree (was 11 on origin/main). Real fixes: RG-0501 (CARWASH-1's seven phrases had only
  Afrikaans — now all 15 Quick languages), RG-0504 ("At least one advert" / "Create my advert" → listing; server sends `listing` and
  still `advert` for cached pages). Stale checks brought up to date after confirming the behaviour live: RG-0120 (PHOTO-EMPTY-1 line),
  RG-0435 (QLANGS spacing), RG-0476 (celebrate grew), RG-0817 (GENERIC-EX-1), RG-0841 (FIND-CLOSE-1 / RUL-207(b)), RG-0860
  (_svcTypeMatches), RG-0875 (TEXT-ANON-1 param). RG-0840/0871: the proofs need python-multipart — now run under
  `/var/www/marketsquare/venv/bin/python`, where they pass. RG-0194 was the relay checkout `/opt/marketsquare-src` holding 105
  Windows scripts with LF on disk (git saw them clean); re-checked-out → CRLF. **Something rewrote them after the 02:01 release —
  watch for it.** RG-0154: SESSION_COUNTER refreshed (220 → 221).
- **GI-0020:** APPROVED (a) — runs as it is; REVIEW NOW is empty.
- **QA data:** drafts #535 and #536 deleted by their own sessions; user rows `qa-goal33@` and `qa-goal33b@` deleted (before-rows in
  `/root/qa_goal33*_user_before_delete_20261009.json`; their ai_spend_log rows kept).
- **Note for walkers:** another lane's restart at 00:31Z gave one 502 to the ledger's live probe; the site answered 200 after.

## RUN 33 — Thu 8 Oct 2026, 20:56–21:40 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; probe in `_to_delete/goalrun33_write_probe`, candidate ms.js in
  `_to_delete/goalrun33_ms.js`). Built in server worktree `/root/w33` (removed at the end), shipped `claude/goal-run33` 0b8f248 via
  CLOUD-SHIP-1 (21:28Z SHIPPED, server page `ms.js?v=1000&m=1`). Cloudflare kept handing out the v=999 page for a while — check with
  `/?fresh=…`. **SSH to `trustsquare.co` times out — use `178.104.73.239`.** Port 22 dropped for ~5 min mid-run (refused, then
  timeouts) and came back by itself; the device VM cannot reach `api.hetzner.cloud`, so the self-heal beacon fails from there.
- **Walk (casual / services, Johannesburg hair braider, `docs/E2E_2026-10-08.md`):** cold Home → Sell → Work for yourself? → Quick →
  Beauty → Hair braider → Soweto, Rosebank → Fri–Sun → R150 **Per visit** (PIECE-WORK-DEFAULT-1 holds live) → Save → letter in 35 s
  → link → Hub → Publish my listing → terms; stopped at Go live. **Break:** Home said "Showing Johannesburg — from your phone's
  location" and one tap later Quick asked "Which city?" (New York first on the sandbox's US network): CITY-HANDOFF-1 passes only a
  city she picked, and since GEO-AUTO-1 nearly nobody picks. **Friction:** "Nothing listed in Johannesburg yet" above "Services 47
  listings" (tiles count AI examples since GX-TILE-COUNT-1). Both fixed and proven live (GI-0031).
- **Number: 0.** Live 140 = 132 `*@trustsquare.co` + family 8 (David Jnr 3 — new #534 Property 15:03Z — Marietjie 3, Maroushka 2).
  **By a stranger's hand: 0.** New users since run 32: this run's QA address only. Draft #533 (Services, dmcontiki2@ — David's own,
  08:30Z) left alone.
- **Where people stop:** no strangers. Human (bot=0) sessions since run 32: all family — iPhone 18_7 (David / David Jnr; four Quick
  walks to `q_draft` and one publish = #534), Maroushka's Mac (#531 publish, 7 Oct).
- **Outreach:** not re-pulled; `outreach_ledger` on the server is empty, so it is not where the sends are recorded. Last known send
  3 Oct (runs 28–32).
- **Shipped (0b8f248):** GI-0031 QUICK-AUTO-HANDOFF-1 + NUDGE-REAL-WORD-1, RG-0946 LOCKED. Also the RG-0889 check was a **false red**
  (it looked 300 chars above setsFor(); later comments pushed the sets out of view — the live braider opens on Per visit); widened.
  RG-0890's check follows the new msQuickHref. Ledger new tree 11 !!!! (RG-0120, 0435, 0476, 0501, 0504, 0817, 0840, 0841, 0860,
  0871, 0875), base 0d2cfe2 13 (the same + RG-0194, RG-0889) — none this run's.
- **Live proof (21:35Z, fresh profile, Johannesburg phone):** bar "No real listings in Johannesburg yet — the listings below are AI
  examples. Pretoria has 8 real listings."; Quick link `…&cc=ZA&city=Johannesburg`; after Hair braider Quick opens on "Where can you
  work? Sandton, Rosebank, Soweto…". No location on a US network: `cc=US`, "Which city?" (unchanged, correct).
- **Seen, not changed:** the Hub card shows a ⚙️ tile, not the example photo Quick showed her; two language controls on Home.
- **REVIEW NOW:** GI-0020 only (unchanged).
- **QA data:** draft #535 deleted by its own session (200); user row qa-goal33@ left. Nothing published.
- **Not reached:** outreach opens/clicks (no record found on the server).

## RUN 32 — Wed 7 Oct 2026, 20:56–21:35 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; write probe in `_to_delete/goalrun32_write_probe`, candidate ms.js copy in
  `_to_delete/goalrun32_ms.js`). Built in server worktree `/root/w32` (removed at the end), shipped `claude/goal-run32` 83e277a via
  CLOUD-SHIP-1 (21:22Z SHIPPED). **The page's script is `/static/ms.js?v=NNN`, not `/ms.js`** — a bare `https://trustsquare.co/ms.js`
  is a 404 JSON body, and an HTML page Cloudflare still had cached pointed at the previous v=, which made the first live check look
  like a failed deploy. Check the `src=` the page actually carries (v=988 here).
- **Walk (Local Market · Handmade & Craft, from a Durban phone, `docs/E2E_2026-10-07.md`):** cold Home → Sell → Local Market →
  Handmade & Craft → basket photo → six steps → score 70 in ~3 min; stopped at Publish. No errors. **Break:** from step 3 on, the
  flow speaks only to Food & Produce — a basket weaver was coached "A jar of honey is R80", asked for "e.g. Store below 25°C" and
  "e.g. 24 jars" (GI-0030, fixed live). **Friction:** the suburb example was always the Pretoria one (fixed); the photo read's R350
  landed in her price box unmarked because AI-PRICE-HINT-1 only marks guesses under 0.5 confidence (fixed); Home's empty-city bar
  answered an empty Durban with "Show Pretoria" only — nothing for someone who came to sell (fixed).
- **Number: 0.** Live 138 = 132 `*@trustsquare.co` + family 6 (Marietjie 3, Maroushka 2 — she listed again, #531 Property 18:14Z —
  David Jnr 1). **By a stranger's hand: 0.** New user rows since run 31: six `dmcontiki2+qa-…` addresses, all the F14 agency lane's.
- **Where people stop:** no strangers. Human (bot=0) sessions since run 31: David Jnr's iPhone (Quick to step 3, 15:27Z, left),
  Maroushka's Mac (one dwell 18:03Z, then a full Property publish 18:04–18:14Z = #531), one iPhone dwell. Drafts left open:
  #528 Property, #529 Cars, #532 Services — all `qa-codesurvive@`, another lane's.
- **Outreach:** fourth day with no letter (last 3 Oct 22:10Z). The laptop's `CityLauncher/data/prospects.db` is itself stale — its
  newest send is 26 Sep, 2,553 emailed, no event rows since 27 Sep — so the 2,614 figure in earlier runs cannot be reproduced from it.
  Not this run's lane; worth that lane's eyes. The server's demand lane keeps logging `cat=Collectors city=1 -> 0 available prospects`
  (6 Collectors prospects have a city, against Services 329 / Tutors 283 / Property 274).
- **Shipped (83e277a):** GI-0030 LM-KIND-WORDS-1 + AREA-PH-CITY-1 + AI-PRICE-MARK-1 + CITY-FIRST-SELLER-1 (RG-0937 LOCKED). Live proof
  in the GI row. Ledger new tree 11 !!!!, base `/opt/marketsquare-src` 5e57ad0 12 (the same 11 + RG-0194) — none are this run's.
- **Worth another lane's look:** RG-0889 (run 30's PIECE-WORK-DEFAULT-1) has come back — hair braider, hairdresser and nail technician
  no longer open Quick's price step on Per visit. It fails on `origin/main` too, so something in `quick.html` since 5 Oct undid it.
  RG-0504 also fails with three `advert` strings back in ms.js.
- **REVIEW NOW:** GI-0020 only (unchanged).
- **QA data:** nothing published, no account created, no listing saved; walk rows bot=2.
- **Not reached:** outreach opens/clicks (no sends to read, and the local prospects DB is stale).

## RUN 31 — Tue 6 Oct 2026, 20:56–21:35 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; candidate ms.js copy in `_to_delete/goalrun31_ms.js`). Built in
  server worktree `/root/w31` (removed at the end), shipped `claude/goal-run31` a1d6a59 via CLOUD-SHIP-1 (21:21Z SHIPPED, ms.js?v=967). Live check from a fresh
  browser: US network → nudge on Home, tap → "United States / New York"; `/?listing=499` shows no tip and no nudge, only the wristwatches photo.
- **Walk (Collectors, from abroad, `docs/E2E_2026-10-06.md`):** en-GB phone, US network. Home → Sell → Collectors → two photos →
  six steps → score 78 → e-mail; stopped at Publish. ~2½ min, no errors. **Break:** the app's photo read called our own example
  picture a pocket watch — it was the cover of four "Vintage wristwatch · 1960s automatic" / "Omega Seamaster" example adverts
  and the wristwatch card in every collectors letter (GI-0026, fixed live). **Friction:** abroad visitor treated as South African
  throughout (GI-0028, built); category tip over an advert arrival (GI-0027, built).
- **Number: 0.** Live 137 = 132 `*@trustsquare.co` + family 5 (Marietjie 3, David Jnr 1, Maroushka 1 — #526 Property, published
  6 Oct 17:25Z). **By a stranger's hand: 0.** New users since run 30: two QA addresses only.
- **Where people stop:** no strangers. Human sessions since run 30: David Jnr's iPhone (Quick, cars draft #525, 15:41Z), Maroushka's
  Mac (Property publish #526), David's Windows PC (Cars draft #527, 17:52Z).
- **Outreach:** no letter sent since 3 Oct 22:10Z (2,614 emailed total). Not this run's to restart; noted.
- **Ledger:** new tree 7 !!!! (RG-0435, 0476, 0504, 0840, 0841, 0860, 0871), base /opt/marketsquare-src 3b28b69: the same 7 + RG-0194.
  None are this run's; RG-0435/0476/0504/0841/0860 are new since run 30 — likely the CASUALS-WAVE-1 / audit lanes. Worth that lane's look.
- **REVIEW NOW:** GI-0020 only (unchanged).
- **QA data:** nothing published or saved (0 users / 0 listings for qa-goal31); walk funnel rows bot=2.
- **Not reached:** outreach opens/clicks detail (no sends to read).

## RUN 30 — Mon 5 Oct 2026, 20:56–21:40 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; probe in `_to_delete/goalrun30_write_probe`). Built in server
  worktree `/root/w30` (removed at the end), shipped `claude/goal-run30` 36437dc via CLOUD-SHIP-1 (21:25Z SHIPPED, ms.js?v=954).
  Cloudflare served the v=953 page for a few minutes after; a fresh browser got v=954 by ~21:33Z. **Don't `git checkout` in
  `/opt/marketsquare-src`** — this run detached it for a second by accident and put it back on `main` (same commit).
- **Walk (casual / services, `docs/E2E_2026-10-05.md`):** cold Home → Sell → Quick → Beauty → Hair braider → Johannesburg
  (Soweto, Rosebank) → Fri–Sun → price → Save → letter (21:05Z) → link → Seller Hub → Publish → terms; stopped at Go live.
  **Break:** the price step opened on "Per day" with the R241.84 minimum-wage floor; her R150 left Next greyed. Fixed (GI-0022).
  Also: Quick asked "Which city?" afresh after the app had a city (GI-0023). Both proven live.
- **Number: 0** (6,748 listed · 2,614 emailed · 5 registered · 0 qualifying). Live 136 = 132 `*@trustsquare.co` (incl. 53
  `showcase-email@` outreach examples, `demo_example`/`super_example` flagged, 47 of them made today for the US/UK/AU letters)
  + Marietjie 3 + David Jnr 1. **By a stranger's hand: 0.**
- **Family data moved:** Maroushka (miconradie1@, Google sign-in from the family IP) deleted **all 15 of her listings** herself,
  5 Oct 09:57–10:20Z (`DELETE /listings/<id>/seller` 200 ×15); David Jnr deleted #458, #468, #469 on 4 Oct 18:47Z. Rows are gone
  (seller delete is a hard delete). Not a fault; worth knowing that Local Market / Collectors now hold almost no real adverts.
- **Where people stop:** no strangers again. Human (bot=0) sessions since run 29: David Jnr's iPhone, David's iPhone opening the
  `email-test-svc-pta` letter link (13:35–13:42Z, 18:57Z), one Mac (09:55Z, Maroushka's session), one Linux sell-sheet tap.
- **Shipped (36437dc):** GI-0022 PIECE-WORK-DEFAULT-1 (RG-0889), GI-0023 CITY-HANDOFF-1 (RG-0890). Both fail on f9b6f5f, pass new.
- **Follow-up (David, same evening: "fix the two open actions"):** both found-not-changed items fixed and shipped —
  GI-0024 TRAIL-ONE-PIC-1 (RG-0891), GI-0025 HOME-CITY-DRAFT-1 (RG-0892). QA draft #524 (qa-goal30b@) made to prove
  GI-0025 and deleted by its own session. **Ledger id clash to watch:** another lane's SIGNIN-HOME-1 (08aa3c3) names
  RG-0889 in its commit and changelog but has no ledger entry; RG-0889 in the ledger is PIECE-WORK-DEFAULT-1.
- **REVIEW NOW:** GI-0020 only (fair-price cost; recommend (a) now, (b) when a stranger reaches the Collectors score card).
- **QA data:** draft #523 deleted by its own session (row gone); user row qa-goal30@ left (account deletion is David's).
- **Not reached:** outreach opens/clicks since run 29 (not pulled).

## RUN 29 — Sun 4 Oct 2026, 20:56–21:25 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; probe in `_to_delete/goalrun29_write_probe`). Built in server
  worktree `/root/w29` (removed at the end), shipped `claude/goal-run29` 046b996 via CLOUD-SHIP-1 (21:11Z SHIPPED, ms.js?v=935;
  backend lands as `/var/www/marketsquare/main.py`, not bea_main.py). Run 28 already ran this morning; this is the evening run.
- **Walk (Local Market with a photo, `docs/E2E_2026-10-04_run29.md`):** cold Home → Sell → Local Market → Food & Produce → jam-jars
  photo → six steps → score 70 in ~2 min; stopped at Publish. No errors. **Break:** with her story box empty, the advert's
  description would have been the photo read's paragraph, never shown to her — honey, bread loaves, a jug and flowers "as market
  styling", ending "…and pricing are not visible." — under "Homemade orange marmalade". Also the read's R80 guess (confidence
  0.28) sat in her price box unmarked. Both fixed and proven live (GI-0021).
- **Number: 0** (6,748 listed · 2,614 emailed · 5 registered · 0 qualifying). Live 104. **By a stranger's hand: 0.** Only new
  listing since run 28: #475 Property, live, David Jnr (davidconradie1234). No new user rows.
- **Where people stop:** no strangers again. Human (bot=0) sessions since 08:00Z: all David Jnr's iPhone (Quick door ×3,
  one full Quick publish 15:23–15:33Z = #475, one Quick walk to step 5 left open 15:39–17:59Z).
- **Outreach:** one letter since run 28 (ts-collectibles@t-online.de, 3 Oct 22:10Z, opened). Not pulled further.
- **Shipped (046b996):** GI-0021 AI-DESC-SHOWN-1 + AI-PRICE-HINT-1, RG-0876 LOCKED. Ledger new tree 2 !!!! (RG-0840, RG-0871 —
  pre-existing, prove_audit_b2/b3.py on the throwaway DB); base 3 (+RG-0194).
- **Found, not changed:** the cleaned AI text can still carry hedges ("subject to seller confirmation") — she now sees and edits it.
  RG-0840 / RG-0871 fail on origin/main too (audit lane's proofs) — not this run's.
- **REVIEW NOW:** GI-0020 only (fair-price cost; recommend (a) now, (b) when a stranger reaches the Collectors score card).
- **QA data:** nothing published, nothing saved; walk funnel rows bot=2.
- **Not reached:** what the Collector Shops letters did after the open.

## RUN 28 — Sun 4 Oct 2026, 07:32–08:10 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; this run's write probe is `_to_delete/goalrun28_write_probe`).
  Laptop 1 behind origin, untouched. Built in server worktree `/root/w28` (removed at the end), shipped `claude/goal-run28`
  bb5d7d5 via CLOUD-SHIP-1 (07:53Z SHIPPED, server cache-buster ms.js?v=920; Cloudflare still handed out the v=919 page for
  a few minutes after — a fresh browser got v=920). The scheduled run of 3 Oct never finished (the session's tools dropped
  after the first reads), so there is no run-28 entry for Saturday; this is run 28.
- **Walk (Collectors / goods, `docs/E2E_2026-10-04.md`):** A — cold Home → Sell → Collectors → photo → six steps → score card
  (70, "Publish now — I accept the Terms"); stopped at Publish (contract). About 2 minutes, no errors. B — the Collector
  Shops letter's own link shape (QA address): lands on "Step 1 of 6 · Photos" with no word of who or why, a Home tip over it.
  RUL-199's Collectors legal card and QUICK-CARD-1 are live as David ruled.
- **Number: 0** (6,748 listed · 2,614 emailed · 5 registered · 0 qualifying). Live 104 (#469 paused 3 Oct 06:00Z). Every live
  listing is seeded (`*@trustsquare.co`), AI-example, or family (miconradie1 15, marietjie.marais59 3, davidconradie1234 1).
  **By a stranger's hand: 0.** No listing of any kind created since 2 Oct 21Z; the 13 accounts made since 2 Oct are all
  `dmcontiki2+qa-…`.
- **Where people stop:** still no strangers arriving. Human (bot=0) sessions since run 27: David Jnr's iPhone (3 Oct 05:01–05:52,
  Quick services, to step 3) and one Windows Chrome Sell→Quick tap at 19:04Z (David's PC, the hour QUICK-CARD-1 shipped).
- **Outreach:** now one letter a night, all to **Collector Shops** (Pencafe 30 Sep, Clarke's Books 1 Oct, Fanaticus 2 Oct,
  ts-collectibles 3 Oct); 26 sent since 28 Sep, none bounced since 29 Sep. `click_register` counts 10 non-QA "human clicks"
  ever; the newest (Curro Hazeldean, 30 Sep 10:01Z) is an e-mail scanner, not a person — opened from 51.89.103.123 and clicked
  from 144.217.233.238 (both OVH data centres, Edge 122) and no `landed` row followed. Treat that tier as an upper bound.
  Note: ts-collectibles@**t-online.de** (a German mailbox) was sent as a Cape Town shop.
- **Shipped (bb5d7d5):** GI-0018 COL-DRAFT-1 (RG-0812) and GI-0019 MAGIC-HELLO-1 (RG-0813), both LOCKED after the live check.
  Full ledger on the new tree: 0 !!!! (base /opt/marketsquare-src 4e5a15b: 1, RG-0194, pre-existing). Live proof in the rows.
- **Found, not changed:** the photo read's price guess (R200) lands in Asking price unmarked; the score did not move for nine
  fields after the photo (it is the server's listing score; only photos lift it). Invited QA addresses get a 401 from the photo
  read by design (INVITE-VISION-1 passes only real invitees) — walk B's photo step cannot be proven with a QA address.
- **REVIEW NOW:** GI-0020 only — the fair-price cost breakdown David asked for (measured: $0.052 average per check, 1T = $2).
- **QA data:** nothing published, nothing saved to the server; this walk's funnel rows are bot=2.
- **Not reached:** what the Collector Shops letters did after the open (none clicked); whether CityLauncher should drop
  non-South-African mailboxes from SA city lists (outreach is not this run's to change — flagged above).

## RUN 27 — Fri 2 Oct 2026, 20:56–21:25 UTC (Opus 5.5)

- **Acting:** folder mounted and writable (`rm` not permitted; my write probe moved to `_to_delete/goalrun27_write_probe`).
  Laptop 5 behind origin, untouched. Built in server worktree `/root/w27` (removed at the end), shipped
  `claude/goal-run27` 26db01f via CLOUD-SHIP-1 (SHIPPED, ms.js?v=905). Commits from the server need
  `-c user.name="Claude (Goal run)" -c user.email=claude@trustsquare.co` — there is no global git identity there.
- **Walk (casual / services, `docs/E2E_2026-10-02.md`):** cold Home → Sell → Quick → Home cleaner, Pretoria (Mamelodi,
  Menlyn), Mon/Wed/Fri, R350/day → Save → letter in 17 s → link → Seller Hub → Publish my listing → terms step → stopped
  at Go live (contract). Path works end to end up to Go live; no errors. Breaks a person would feel: a dead orange "Email"
  button (one-tab bar); terms step told a two-minute-old seller "You have an existing account"; language pill on the
  terms step's Back button; letter said "composed". All four fixed and proven live. Note: the sign-in link is single-use
  per phone (a second open says "already used" — matches the letter). Quick picks the country from Cloudflare geo, so the
  US-egress sandbox lands on US cities; a real SA phone is not affected.
- **Number: 0** (6,748 listed · 2,612 emailed · 5 registered · 0 qualifying). Live 105 = 103 + #468, #469 (family:
  davidconradie1234@). **By a stranger's hand: 0.**
- **Where people stop:** still no strangers. Human sessions since FUNNEL-WEBDRIVER-1 (1 Oct 21:28Z): David's phone
  (03:30) and David Jnr's phone (08:42–09:05), nothing else — every other session is bot=2. The filter works; the
  funnel is empty because nobody new is arriving.
- **Found:** David Jnr's second Quick walk re-published the same Townhouse → two identical live adverts (#468, #469).
  QUICK-DUP-1 stops repeats (proven on the live DB read-only: #469's fields → finds 469; changed price → none; cannot be
  proven by a live publish without publishing).
- **Shipped (26db01f):** GI-0013 QUICK-ONE-TAB-1 (RG-0790), GI-0014 TERMS-NOTE-1 (RG-0791), GI-0015 LANG-PILL-SOB-1 +
  LETTER-WORD-1 (RG-0792), GI-0016 QUICK-DUP-1 (RG-0793). All four FAIL on origin/main 11c1f4f, pass on 26db01f; full
  ledger 14 !!!! vs 15 on origin/main, none new. Live proof: Quick key bar `display:none` with the email box shown;
  terms step note reads the new words, pill `display:none` (screenshot); letter to qa-goal27b subject "Your TrustSquare
  listing is saved — one step left"; main.py carries QUICK-DUP-1.
- **QA data:** drafts #470 and #471 deleted by their own seller sessions (200, gone from the DB). User rows for
  qa-goal27@ / qa-goal27b@ left (account deletion is David's).
- **REVIEW NOW:** GI-0017 pause #469 (new) · GI-0008 SO-6 rulings sweep · GI-0006 Collectors step-6 note · GI-0003 Quick
  card in Sell.
- **Not reached:** outreach per-wave opens/clicks (not pulled this run); Story/Selling-details scoring question from
  run 26 (not started).

## RUN 26 — Thu 1 Oct 2026, 20:56–21:40 UTC (Opus 5.5)

- **Acting:** folder mounted and writable. SSH needs `bash load_sandbox_ssh.sh` first in a fresh device VM ("Host key
  verification failed" until then). The device VM has ~1.3 GB free — a clone of the 2.2 GB repo fails, so this run
  built in a server worktree (`/root/w26`, branch `goal26` off `origin/main`) and shipped by pushing
  `claude/goal-run26` with `[ship]` (CLOUD-SHIP-1 gates, health-checked deploy). Laptop tree untouched (2 behind origin
  at start, clean apart from an untracked `SYNC_ORIGIN_GUARDS_2026-10-01.html`).
- **Walk (Local Market, `docs/E2E_2026-10-01.md`):** a fresh Chromium profile from the cloud sandbox (the built-in pane
  holds other lanes' QA storage and the safety layer refused clearing it). Home → Sell → Local Market → Food & Produce →
  six steps → score 60 in ~2 min → stopped at Publish (contract). No errors. Breaks: the "Sold" unit never reached the
  price (card would read "R85", not "R85 per box"); no "each"/"per pack" for baked goods; step 2 promised an AI title
  from a photo she had skipped. All three fixed. Seen, not fixed: Story / Selling details / Features add no points
  (score 60 before and after a full story) although the coach calls the story "your unfair advantage".
- **Number: 0** (`onboarding_number.py`): 6,748 listed · 2,611 emailed (+1 since run 25) · 5 registered · 0 qualifying.
  Live 103 = 85 AI examples + 18 family. **By a stranger's hand: 0.** New listings 1 Oct: #458 draft (David's
  davidconradie1234 address, Property) and one QA row. Nothing published by anyone outside the family.
- **Where people stop:** still unknown — **no strangers in the funnel.** Of 55 sessions stored human on 1 Oct: 35 a
  cloud check's iPhone 17_0 burst (14:39–15:01, ~12 s apart), 10 this run's own walk, 3 Pixel 8 scripted, 7 iPhone 18_7
  (one carries dmcontiki2@ — David's phone; #458 matches another). FUNNEL-QA-1 missed them because scripted walks
  without the QA key look human. Fixed (FUNNEL-WEBDRIVER-1). From 21:28Z the human count should mean people.
- **Shipped (33f3052, live 21:28:08Z, ms.js?v=885):** GI-0010 LM-UNIT-1 (RG-0652), GI-0011 LM-COACH-TRUTH-1
  (RG-0653), GI-0012 FUNNEL-WEBDRIVER-1 (RG-0654). All three FAIL on e22c12f and pass on 33f3052; full ledger on the new
  tree 14 !!!! vs 15 on origin/main (all pre-existing, server-vantage; none new). Live proof below each row.
- **REVIEW NOW (corrected 2 Oct):** GI-0008 SO-6 rulings sweep · GI-0006 Collectors step-6 note · GI-0003 Quick card
  in Sell. GI-0009 was listed here as open but OpenAI had been answering since 04:15Z on 1 Oct — re-check before inheriting.
- **Not reached:** per-wave outreach opens/clicks; whether GI-0009 (OpenAI credit) was topped up today; the scoring
  question above (next run: read sfScore / section pts before changing anything). **Data left behind:** 10 funnel rows
  of this walk (bot=0, UA SM-A156E, 20:59–21:09Z, 1 Oct) — deleting live rows is David's; readers can exclude them.
  Server worktree `/root/w26` removed at the end of the run.

## RUN 25 — Wed 30 Sep 2026, 20:56–21:35 UTC (Opus 5.5)

- **Acting:** folder mounted and writable; ssh to the server works. **The laptop checkout is 56 commits behind
  `origin/main`** (the cloud story lane ships through GitHub) and carries uncommitted nightly files
  (marketsquare.html v=504, STATUS.md, nightly logs); `DEPLOY_RESULT.txt` says FAILED 07:35. So this run built in a
  fresh clone of `origin/main` and shipped through the server relay. **These GOAL files are updated on `origin/main`,
  not in the laptop tree** — the laptop sees them when it next merges origin.
- **Walk (Collectors, `docs/E2E_2026-09-30.md`):** stranger Home → Sell → Collectors 6 steps → score → stopped at
  Publish (contract). Breaks: Home's Local Market tile had no words on it (fixed). Hesitation point: step 6 greets a
  one-coin seller with dealer registration and "SEVERE PENALTIES" (GI-0006). Buyer half not walkable: Pretoria's only
  Collectors advert is the AI demo; Local Market's only real advert is family. False red cleared: 48 h vs 96 h wording
  agrees with the Terms.
- **The cloud story lane walked F2–F14 end to end today** (publish, intro, accept, ~30 fixes). Its F10 walk found
  **the OpenAI account out of credit** — confirmed: last 200 at 19:17 UTC, 429s since 19:23; photos still pass via
  Anthropic failover; paid reports and the web fair-price check are down (GI-0009).
- **Number: 0** (`/opt/marketsquare-src/scripts/onboarding_number.py`): 6,748 listed · 2,610 emailed · 5 registered ·
  0 qualifying. Live adverts 103 = 85 AI examples + 18 family (Marietjie 3, Maroushka 15). **By a stranger's hand: 0.**
  QA adverts: 0 public (all five paused 18:46Z by another lane — GI-0002 done). Rick's draft #382 (12 Sep) still a draft.
- **Where people stop:** unknown — **the sell funnel had no people in it.** Every "human" Quick session since 1 Sep
  that reached a draft is an emulated phone in a scripted burst (Pixel 7/8, iPhone 17_0/17_5, minutes apart).
  FUNNEL-QA-1 now tags our own traffic bot=2 from tonight; read `/onboard/funnel` from 1 Oct.
- **Outreach:** 28 Sep 13 sent / 1 bounce; 29 Sep **9 sent / 1 bounce**, all organisations (service companies, tour
  operators, a collector shop). Runway 0.
- **Shipped (39572d8, live 21:20:52Z, ms.js?v=875):** GI-0005 LM-TILE-LABEL-1 (RG-0643) and GI-0007 FUNNEL-QA-1
  (RG-0644), both proven live, both ledger entries fail on the old tree.
- **REVIEW NOW:** GI-0008 SO-6 rulings sweep (RUL-138, 189/191, 191(3), 144/178, 155/156 wording, 192(a) consent) ·
  GI-0009 OpenAI credit · GI-0006 Collectors step-6 note · GI-0003 Quick card in Sell. GI-0004 overtaken by RUL-192.
- **Contract changed (GOAL_RUN_PROMPT.md):** §2 — the cloud lane owns publish-to-accept walks; the Goal walk covers a
  stranger's first minutes and ships from a fresh clone via the relay. §7 — rewritten for RUL-192 (no SMS sign-in).
- **Not reached:** Local Market accept path (only real seller is family); per-wave opens/clicks; a rand figure for the
  Anthropic failover spend. **Housekeeping:** this run's fetch left `.git/index.lock` + an old `ORIG_HEAD.lock` in the
  laptop repo; both moved (not deleted) to `.git_stale_locks/*goalrun25*`. A stray empty `.wtest` (my write probe) is
  in the laptop repo root — `rm` is not permitted from this shell.

## RUN 24 — Tue 29 Sep 2026, 20:56–21:3x UTC, first run under GOAL_RUN_PROMPT v2 (Opus 5.5)

- **Acting:** folder mounted and writable; server reachable by ssh from the device shell.
- **Walk (casual/services, `docs/E2E_2026-09-29.md`):** Quick → email link → Seller Hub draft #440 worked,
  email in under a minute. **Publish NOT walked** — the session's safety layer refused publishing a public
  advert on the live site from an unattended run. Steps after Publish were last proven 27 Sep (walk 3).
  Where she'd stop: Sell has no door that names a cleaner (Quick is a small "In a hurry?" line); her hub
  opens with an "Agent Hub — estate, car & tour agents" card above her own draft.
- **Number: 0** (`onboarding_number.py`, server): 6,748 listed · 2,601 emailed · 5 registered · 0 qualifying.
  Live adverts 108 = 85 super-examples + 18 David/family + **5 QA adverts public** (GI-0002). By a stranger's hand: **0**.
- **Outreach, 28 Sep wave (first live send in 10 days):** 13 sent, 1 bounce, 0 human clicks (scanner click +
  2 scanner Quick sessions within 60 s; 3 Google-proxy opens). 12 of 13 to schools/colleges/universities.
  `[sendable]` **9 · runway 0.** onboard_steps marks those scanner sessions bot=0 — the funnel counts machines.
- **The prize (§7):** 1,111 phone-only Gumtree South Africans advertising their own services; 0 phone-only rows
  in `prospects` (the scraper drops them). Cold SMS/WhatsApp to them is a POPIA s69 question — David's (GI-0004).
- **Shipped:** GI-0001 HUB-AGENT-FIT-1 (RG-0552 LOCKED) — 06bf885, live 30 Sep 00:14Z after `lm-walk` released its lock; proven on the live page (Services-only seller: agents' card hidden; Property / Adventures / no adverts: shown) and both Quick lines read "Cleaner, gardener, nanny, driver? Quick listing".
- **REVIEW NOW:** GI-0002 archive QA adverts · GI-0003 full-size Quick card in Sell (changes RG-0478) ·
  GI-0004 SMS account ≈ R100–135/month + legal read on the 1,111.
- **First-run check (§9):** "Daily Agent Stand-up (with Pulse)" and "trustsquare-onboarding-goal" are OFF;
  "D-U-N-S email watch" ON.
- **Not reached:** Publish and everything after it; ledger/rulings boards (ledger locked by another lane);
  deploy (waits for the lock and for the tree to go quiet, SO-5).
- **FOR RUN 25 (David asked, 30 Sep morning):** under new SO-6, sweep RULINGS.md for every ruling David approved that quietly adds a per-use/monthly cost or contradicts an earlier ruling (the RUL-167 vs RUL-122 SMS case, now corrected by RUL-192); list each in GOAL_IMPROVEMENTS REVIEW NOW with the cost, the ruling it collides with, and a recommendation. Also: BulkSMS account trustsquare_sms is OUTREACH-ONLY (RUL-192); the test texts failed NOT_SENT pending BulkSMS support.
- **Stray file:** `.goalrun_write_test` (empty, repo root) — my write probe; `rm` is not permitted from this shell.

## SUNDAY SUMMARY — written by run 28, Sunday 4 October 2026

**The number is still 0.** Nobody we wrote to has published a listing, and this week nobody new arrived to try: every
person who touched the sell flow was family, a QA address or a script. Twenty-seven days left to the 20-seller target.

**What moved.** You answered the whole cost sweep in one go (RUL-199) and it shipped the same evening; the Quick card now
opens Sell; the funnel finally separates people from scripts, so when a stranger does arrive we will see exactly where she
stops. The product path itself is in good shape: a Local Market seller (Thursday), a cleaner (Friday) and today a coin
collector each walked from a cold Home page to the Publish button in two minutes without an error.

**What today's walk found.** The letters now go to collector shops, one a night, and their link drops a shop owner onto
"Step 1 of 6 · Photos" without a word of who it is for — the welcome banner was lost in July when the sell flow was
rebuilt, so every invitee since then has landed like that. It now greets her by name. The photo reader also stopped making
her retype what it had just worked out (a coin, 1947).

**What is next.** The letters are the bottleneck, not the app: one a night to shops, and the one recent "human click" was a
mail scanner. The one decision on your desk is the fair-price check's cost — it costs us about R1 a check and earns R36;
my recommendation is to keep it as it is, and to give a new seller her first check free once strangers start arriving.

**Evening (run 29).** Still nobody new; David Jnr published a property (#475). Tonight's walk caught something no checker
would: a jam seller who added a photo and skipped the story would have published an advert describing bread, baskets and
flowers, ending with the AI's note that "pricing is not visible" — text she never saw. The AI's draft now sits in her story
box for her to read and change, its notes-to-self removed, and a weak price guess is shown as a hint instead of filled in.

## SUNDAY SUMMARY — written by run 22, Sunday 27 September 2026

**The number is 0.** Both probes agree: nobody we contacted cold has published a listing.
Thirty-four days left.

**Last night the whole campaign sent one letter.** Not twelve, not thirteen. One — to an estate
agent in Bloemfontein. That is not a fault; it is the first honest night we have had. Fixing
*which places we write to* two nights ago took away the thousands of American addresses that
could never have published anything, and what was left underneath turned out to be very small.
Most of this week was spent finding out how small, and why.

**The list is not what we thought it was, in two specific ways.**

*First, the teachers.* Last Sunday you were told the biggest thing standing between us and
sellers was a decision only you could make — 1,114 South African teachers sitting on our list,
held back by a privacy ruling. That was wrong and I am sorry it reached you in that form. Those
1,114 rows are not teachers. They are **schools** — the name on the row is "Dalibo Primary
School", the address is the school's own office mailbox. And they are held by two separate
things, not one: the privacy ruling you were being asked about, and a completely independent
rule that refuses to cold-mail an organisation rather than a person. **Lifting the privacy
ruling would release none of them.** You can take that decision off your desk; it was never
worth the weight it was given. Worse, we already knew: someone wrote that same measurement down
on 5 September and the board that should have shown it to me had been printing a blank.

*Second, we have been mailing addresses that were never real.* One of our sources, property24,
takes an estate agent's name and their agency's web address and **makes up an email address from
them** — first name, dot, surname, at the agency. It says so in its own notes. Of the twelve such
letters we have sent, **eight bounced**. The agency domains are genuine, which is why last week's
health check pronounced the whole South African list 96% clean: you cannot tell an invented
mailbox from a real one by checking the domain. Those invented addresses were sitting at the top
of the queue in Durban, Port Elizabeth, Cape Town and Johannesburg, they are what silently
switched Cape Town and Port Elizabeth off eight days ago, and they were about to be most of what
we sent for the next fortnight. They are now held. The invented-address habit itself is written
down as still to fix.

**So what is actually left?** Across every South African city we have armed: about **twenty**
addresses we can honestly write to, nearly all in Pretoria. Not thousands, not the 96 I reported
on Friday. Twenty.

**The plain conclusion, five weeks early rather than on the last day: twenty sellers by 31
October cannot come from this list.** Nothing is wrong with the letter — of the people we can
prove read one, about one in four clicked it. Nothing is now wrong with the journey — it was
repaired on 24 September. What we do not have is people to ask. Every hour spent on copy,
timing or the funnel from here is an hour spent on the wrong end of the problem.

**What is next, in one line:** the 1,091 schools are worthless to us as sellers and genuinely
valuable as *employers* — a school employs the cleaners, groundskeepers and assistants the Quick
door was built for — and the enrolment door for exactly that is being built in the other lane
this week; the measurement goes to it on Monday rather than a second cold-mail attempt at the
same 1,091 front offices.

**Nothing on this goal needs a decision from you.** The one question that was at the top of your
list last week has been withdrawn.

---

---

### Correction to the summary above, from run 23 (28 Sep) — two figures, one of them mine to own

- **"about twenty addresses we can honestly write to" was right.** Probed again on the server:
  **21** — Pretoria 20, Cape Town 1. That number has now survived two independent measurements.
- **"the 1,091 schools" was low.** Probed fresh rather than copied: **1,354** never-emailed
  `teachers_trainers` rows with no verdict against them, **every one of them MX-clean**, 1,267 of
  them school-named. The pool is a quarter larger than last night's paragraph said, and it is the
  lane the goal now depends on, so the figure matters. Full measurement in
  `EMPLOYER_LANE_SUPPLY.md`.
- **One thing the summary could not have said, because it was not known: the campaign was not
  sending at all.** Not "one letter a night" — zero. The 27 Sep wave rendered 13 letters and sent
  none of them; both remaining cities were latched. That is fixed as of tonight.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If SSH is dead, queue it host-side: `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed |
| 2026-09-13 (run 12) | **0** | 0 | 0 | 1,482 emailed at 01:00, +108 at 01:31 |
| 2026-09-18 (runs 13–14) | **0** | 0 | 0 | 2,491 emailed · **8 human clicks ever** · first full journey walked |
| 2026-09-19 (run 15) | **0** | 0 | 0 | 2,499 emailed · listing 382 still a draft |
| 2026-09-20 (run 16) | **0** | 0 | 0 | 2,499 emailed (pause held) · **466 sendable left** |
| 2026-09-23 (run 17) | **0** | 0 | 0 | 2,549 emailed · **"45 registered" was 1** |
| 2026-09-24 (run 18, 02:51) | **0** | 0 | 0 | 2,573 emailed · funnel reads 5 registered (4 e2e_test + Rick) |
| 2026-09-24 (run 19, 03:40–04:45) | **0** | 0 | 0 | raw 3, all e2e_test · **the letter to Rick has gone** · publish journey walked green |
| 2026-09-24 (run 20, 23:07–00:10) | **0** | 0 | 0 | 2,574 emailed · **the "331 human opens" were 34** · 9 clicks |
| 2026-09-26 (run 21, 04:15–05:30) | **0** | 0 | 0 | 2,587 emailed · **1,499 of 1,911 US letters had no home on the site** · ZA pool MX-cleaned |
| 2026-09-27 (run 22, 23:07–00:15) | **0** | 0 | 0 | 2,588 emailed — the 26 Sep wave sent ONE letter · true sendable ZA pool ≈ 20 · a source was inventing addresses · D8 withdrawn |
| 2026-09-28 (run 23, 23:08–01:0x) | **0** | 0 | 0 | 2,588 emailed — **the campaign was sending ZERO, both cities latched** · dashboard said 365 sendable, truth is **21** · **both latches released, gates now clear** |
| 2026-09-29 (run 24, 20:56–21:3x) | **0** | 0 | 0 | 2,601 emailed · 28 Sep wave: 13 sent, 0 human clicks · **sendable 9, runway 0** · 5 QA adverts public |
| 2026-09-30 (run 25, 20:56–21:35) | **0** | 0 | 0 | 2,610 emailed · 29 Sep wave 9 sent / 1 bounce · **the sell funnel held no people — all emulated QA phones** (FUNNEL-QA-1) · OpenAI out of credit 19:20Z |

Target: **20 by Fri 31 Oct 2026** — 33 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–23 Opus 5.

## WHAT RUN 23 DID (27–28 Sep 2026, from 23:08 UTC, Opus 5)

0. **Boards first. Pre-work:** `rulings_check` **166 rulings, 0 FAIL, 25 WARN** (the parallel lane
   has added 16 rulings since last night). Ledger, 6 shards: **526 entries · 499 holding ·
   0 REGRESSED · 22 open · 5 ready to lock · 0 UNVERIFIED.** The 5 ready-to-lock are the Ripple
   lane's own entries from 27 Sep — **left to their owner (SO-5), not promoted here.**

1. **RUN 22's HANDOVER ITEM IS DISCHARGED — RG-0507 reaches the emailer, not just the planner.**
   The 27 Sep 22:10 wave was the first under it. It visited Pretoria and Cape Town, rendered 13
   letters, and **not one was an Estate Agent and not one came from property24.** Confirmed in the
   log on the box.

2. **AND THE SAME LOG SAID THE THING NOBODY HAD ASKED: THE CAMPAIGN SENT NOTHING.** Not one letter.
   Both cities ran in DRY-RUN under stop-loss (Pretoria 25%, Cape Town 50%). `2,588 emailed` is
   unchanged from last night because **nothing was sent on either of the last two nights**, and
   nothing would have been sent on any night after. A campaign at zero and a campaign at twelve a
   night look identical in a state file that only records the total.

3. **A FALSE RED CHECKED AND CLEARED before it was inherited.** The rendered letters go to
   organisation desks (`info@christalhopebookstore.com`, `books@kalkbaybooks.co.za`), which looked
   exactly like the fault that holds the 1,091 schools. It is not: `_looks_org_name` and
   `_looks_role_address` apply **only** to `defaults.person_only_categories`, and Collector Shops /
   Tutor Institutions / Service Companies are the RUL-059 agency lane, deliberately excluded. The
   guards are working as written. Thirty minutes to clear, and a false red costs what a false green
   costs.

4. **THE SEVENTH FLATTERING NUMBER, and this one was on David's own dashboard — RG-0540
   SENDABLE-REACH-1.** `publish_sendable.py` promises "what the send chokepoint would ACTUALLY
   accept tonight" and applied armed + gates_green + disarmed_by — **but not GEO-REACH-1**, the gate
   that has decided which cities are *asked* since 26 Sep. Measured on the server, both directions:
   deployed file **365 sendable, runway 28 nights**; fixed file **21 sendable, runway 1**, with
   **344 held unreachable: Maine 344**. So 94% of the "supply" was people in a state whose sellers
   cannot say where they are on the site. FIXED: the gate is imported from `wave_cities` (one
   implementation), every dropped city is named with its count, and `reachability_state` is
   published so GEO-REACH-1's deliberate fail-open reads as NOT MEASURED instead of quietly
   restoring 365.

5. **THE RELEASE PATH FOR THE LATCHES WAS BROKEN AND WOULD HAVE FAILED SILENTLY — RG-0541
   RELEASE-STAMP-SERVER-1.** `clean_city_list.py` is host-side and stamped the wave number from the
   **laptop** DB; the gate that reads the stamp runs on the **server**. Measured on both machines:
   Pretoria host 8 / server 8, Cape Town host **13** / server **14**, Port Elizabeth host **8** /
   server **9**. **Two of the three releases would have been a no-op with a success line over
   them.** The laptop was 123 sends behind because `pull_from_server.py` had not run — and
   WAVE-SERVER-1's own note already named `clean_city_list` as one of the four tools that
   over-count without it. FIXED: the bat pulls first and fails closed; the stamp comes from
   `scripts/server_wave_no.py`, which calls the gate's **own** `wave_history()` on the box.

6. **MY OWN FIX WAS WRONG TWICE AND BOTH WERE CAUGHT BY PROBING IT INSTEAD OF TRUSTING IT.** Its
   first cut (a) tested `ssh_rows()` for `state == 'ok'` when that function returns `'read'`, so it
   refused to stamp every city and **released nothing on its first live run**; and (b) counted
   `DISTINCT date(created_at)` — **UTC** days — getting Pretoria 7 / Cape Town 12 where the gate's
   `wave_history()` says 8 / 14, because a wave is a day in the **send timezone** and a 22:10 UTC
   send belongs to the next SAST day. Wrong counter (WAVE-COUNTER-1), wrong machine (this entry),
   wrong arithmetic (that first cut). There is now exactly one place the ordinal comes from.

7. **AND THE PROXY-ASSERTION TRAP FIRED FOR THE THIRD NIGHT RUNNING, this time on my own check.**
   RG-0541's check FAILed the correct tree because the fix's own **docstring** names the SQL it had
   just removed — and the filter I copied only stripped `#` lines and lines *containing* a quote
   mark, which a docstring's body does not. Fixed properly: `_code_only()` strips triple-quoted
   blocks whole, and both new entries use it. RG-0494, RG-0508, RG-0541 — three nights, three
   entries, one trap, the third written by a session that had just read the lesson.

8. **THE LATCHES ARE RELEASED, ON MEASURED EVIDENCE, AND THE WIRE WAS FOLLOWED TO ITS FAR END.**
   The sources that latched Pretoria (`osm:shop=motorcycle` 2 of 3, `osm:shop=car`) have **zero
   unsent rows left** — exhausted, so they cannot re-latch it. Cape Town's and PE's latches were
   **100% property24**, which RG-0507 now holds. Port Elizabeth was **never latched** (2 bounces,
   floor is 3). Stamped and probed: Pretoria `released=8`, Cape Town `released=14`, both matching
   the server. Then simulated `gate_check` on the box with those stamps: **`may_send=True,
   blocks=[]` for both** — the stop-loss was the only thing stopping the campaign, so this is
   genuinely the switch and not another layer of appearance.

9. **THE EMPLOYER LANE HAND-OFF IS WRITTEN — `EMPLOYER_LANE_SUPPLY.md`, OPEN_LOOPS L27.** Probed
   fresh, not inherited: **1,354** never-emailed no-verdict `teachers_trainers` rows, **every one
   `mx_ok`**, 1,267 school-named, in **nine cities that are all armed, gates_green AND reachable** —
   Durban 596, Pietermaritzburg 535, so **84% in KwaZulu-Natal and this is an isiZulu lane first**.
   `org_enrol.py` was **not touched** (SO-5, hours old, its owner ships it). The document carries
   the measurement, the city/reachability table, and the three questions only that lane can answer.

10. **Boards, post-work: `rulings_check` 166 / 0 FAIL / 25 WARN (unchanged). Ledger: 528 entries ·
    501 holding · 0 REGRESSED · 22 open · 5 ready to lock · 0 UNVERIFIED** against pre-work
    526 · 499 · 0 · 22 · 5 · 0. Both new entries proven to **FAIL on a reverted tree**
    (`git show HEAD:`) and pass on this one.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **FIRST ACT: READ THE 28 Sep 22:10 WAVE LOG. This is the one thing only the next run can see.**
   `/var/www/citylauncher/logs/launchday_20260928_2210*.log`. Pretoria and Cape Town should now be
   **LIVE, not DRY-RUN** — the release stamp lets **ONE** wave out per city and that wave's own
   bounces govern again. Expect roughly **12 letters in Pretoria and 1 in Cape Town**. What to
   check, in order: (a) did they send, or is a gate still blocking; (b) what bounced — if Pretoria
   bounces 3 of 12 again it re-latches immediately and the source that did it must be found and
   held before any second release; (c) `[sendable]` should now read about **21 · 2/40 cities ·
   runway 1**, not 365. **Do not re-release a latch that closes again without finding the source
   first** — that is spending the domain's reputation to discover something a query answers.

1. **THE POOL IS 21 AND THE GOAL NEEDS 20. This is now arithmetic, not pessimism.** Two nights of
   sending empties it. Nothing about the letter, the timing or the funnel is the constraint — of the
   people we can prove read one, about 1 in 4 clicked. **We have run out of people to ask, on this
   list, for this lane.** Not yet STALLED under §9 only because the employer lane is untried.

2. **THE EMPLOYER LANE IS THE GOAL'S ONLY CREDIBLE PATH — and it is a hand-off, not a build.**
   `EMPLOYER_LANE_SUPPLY.md` + OPEN_LOOPS **L27**. 1,354 MX-clean school mailboxes against 21
   sellers: 64×. Next run's job is to find out whether that lane's owner has picked it up, and if
   the answer is no after a reasonable interval, **say so to David plainly** — because at that point
   the goal is blocked on something outside this lane's authority, which is a §9 BLOCKED, not a
   silence.

3. **RG-0509 is still open and is still the root cause of the invented addresses.** A scraper may
   not invent an address and hand it on as harvested. Closing it = `guess_email()` stops being a
   fallback, or a constructed address is written under its own source suffix. Re-tagging the 67
   existing rows is a write to the live prospects register — a focused session. Nothing guessed can
   be sent meanwhile (RG-0507 holds the whole source).

4. **Nobody has clicked since 24 Sep**, and all 9 human clicks predate the RG-0449 publish fix — so
   the repaired journey has **still** never been walked by a real cold prospect. The letters going
   out tonight are the first chance for that in the project's history.

5. **Residual, run 20:** 22 checks in `regression_ledger.py` read a function as a fixed byte window.
   `fn_body()` exists; the sweep is a focused session.

6. Still carried: **RG-0409** ladder values + cap 40 · **RG-0410** CONFIRM-GLIMPSE-1 · **RG-0411**
   taxi-drop area unit · **RG-0412** EULA in the launch languages · **RG-0414** DOOR-RETURN-1 ·
   **RG-0419** Quick door prices only in rands · the terms box at 39,829 px (deliberate, RUL-020).

## OPEN LOOPS

- **The 28 Sep wave is the open question of this goal.** First live sends in ten days. Unwatched
  until the next run reads the log.
- **L27 / `EMPLOYER_LANE_SUPPLY.md`** — handed to `org_enrol.py`'s owner tonight. Not yours to
  build; yours to check whether it moved.
- **RG-0509 (open):** property24 invents addresses. Whole source held meanwhile by RG-0507.
- **RG-0373 is GREEN again** — the parallel lane fixed it (trust-plan referral wording). Not ours.
- **5 entries print READY TO LOCK and were deliberately not promoted** — RG-0532, 0534, 0536, 0537,
  0539, all the Ripple lane's, all shipped 27 Sep. SO-5: the owner promotes. Flag it to them if it
  is still true in a few days, because a fix that prints READY TO LOCK and is never promoted cannot
  trip red when it rots (DW-079).
- **Run 23's CityLauncher deploy is REQUESTED, not confirmed** — it carries the stamped
  `waves_policy.json`, RG-0540's `publish_sendable.py` and RG-0541's `server_wave_no.py`. **Confirm
  it landed before trusting tonight's wave**, and confirm both repos committed (two `git_push`
  actions were queued at 00:21Z). `server_wave_no.py` was already scp'd to the box by hand and
  probed (8 / 14 / 9), so the deploy's job for it is only to make that permanent.
- **22 fixed-byte-window function reads left in `regression_ledger.py`** (RG-0465 residual).
- **RG-0419 / RG-0414** open, as above.
- `_get_json()` still does not exist (specified by run 13, unwritten). 14 `json.loads(_get(...))`
  sites remain individually unprotected against a 200 that is not JSON.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock` it cannot unlink and
  blocks Windows git. Use `git show` or the host queue. (`git show HEAD:<file>` was how both of
  tonight's entries were proven on a reverted tree.)
- Listings 386–400 range ARCHIVED, not deleted; 3 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's. Two `users` rows from run 19's walks and two probe
  addresses in `click_register` are recorded and cannot touch any onboarding figure.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.
- **Rick Wemple: CLOSED.** He is in Montana and the site never offered him a place to stand.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing on this goal is waiting on him**, and that is now the third week running. If the employer
lane does not get picked up, that changes — see "next run" item 2.

- **D5 — where does she come from at all?** The only question that matters, and the employer door is
  the first answer to it that does not need a directory we do not have.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than a strip under a "list your business" letter written for companies?
- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today. **Tonight's
  measurement sharpens this: 84% of the employer supply is in KwaZulu-Natal, so the answer is
  wanted in isiZulu first, not English.**

**~~D8 — the 1,114 teachers.~~ WITHDRAWN 27 Sep**, and it stays withdrawn. They are schools, held
by a person-only rule as well as the POPIA one; lifting the ruling would release none of them. Run
23 re-measured the pool at 1,354 rows — a bigger prize, in a different lane, with no decision
needed from David to reach it.

## WHAT RUNS 17–23 LEARNED ABOUT THEMSELVES

**A TOTAL IS NOT A RATE, AND ZERO HIDES INSIDE ONE (run 23).** `2,588 emailed` was true on
26, 27 and 28 September. It was the same number because **the campaign had stopped sending
entirely** — two cities latched, thirteen letters rendered into a dry run, none sent. Every state
file recorded the cumulative total and none recorded the nightly rate, so a dead campaign and a
slow one were the same line of text. **Record the derivative, not just the integral: what went out
LAST NIGHT is the number that tells you whether the machine is alive.**

**A VALUE WRITTEN ON ONE MACHINE AND COMPARED ON ANOTHER (run 23).** The stop-loss release stamped
the laptop's wave number; the gate that reads it runs on the server. Two of three releases would
have printed success and changed nothing. WAVE-COUNTER-1 had already fixed this stamp once, for the
wrong COUNTER; this was the right counter on the wrong MACHINE; and the first attempt at the fix
re-derived the ordinal a third way and got UTC days instead of send-timezone days. **Three ways to
compute one number is three faults. Ask the thing that will judge you what it thinks the number
is.**

**MY OWN FIX WAS WRONG TWICE AND ONLY PROBING FOUND IT (run 23).** It tested a helper for
`state == 'ok'` when that helper returns `'read'`, and released nothing on its first live run
while exiting 0. Reading my own code would never have found either fault; running it against the
real box found both in minutes. **A fix is a hypothesis until it has been fired at the real
target — and `rc=0` is not evidence that anything happened.** What proved it was probing the
policy file afterwards, not the exit code.

**THE PROXY-ASSERTION TRAP, THREE NIGHTS RUNNING, THE THIRD TIME ON A SESSION THAT HAD JUST READ
THE LESSON (run 23).** RG-0494, RG-0508, RG-0541. Each check matched its own fix's prose instead of
its code. Knowing about the trap did not prevent it; the shortcut filter I copied stripped `#`
lines and lines containing a quote mark, and a docstring's body is neither. **A lesson written down
is not a lesson installed. `_code_only()` is now the installed version** — the difference between
remembering the rule and making it impossible to break.

**FOLLOW THE WIRE TO THE FAR END BEFORE YOU CALL IT A SWITCH (run 23).** Releasing the latches
would have been worthless if any other gate still blocked those cities. That took one probe:
`gate_check` on the box with the new stamps, `may_send=True, blocks=[]`. **The cheap question
before claiming a fix will have an effect: is this the ONLY thing in the way?**

**A BLANK IS A CLAIM, AND THIS ONE COST A WEEK (run 22).** `held_by_guard` printed `{}` for
eleven of twelve cities and every reader — including run 21, including the paragraph that went
to David — read the blank as "nothing is being held". It meant "I filtered out everything I was
built to count, before counting." The two reasons it could not see were the two largest. **An
instrument that reports nothing is not reporting nothing; it is reporting that it looked
somewhere else.**

**THE ANSWER WAS ALREADY WRITTEN DOWN, IN THE FILE, IN ENGLISH (run 22).** PERSON-ONLY-1's note
has said since 5 September that the teachers pool is "a list of schools", that 1,194 of 1,235
rows are named "<X> Primary School", and that releasing it "would spend the biggest pool in the
database on the least likely converters". Run 21 then spent a session concluding the opposite
and put it at the top of David's list. **Two of the six wrong numbers in this project were not
discovered by measurement — they were rediscovered, because the measurement was already on
disk and nobody read the note attached to the thing they were about to change.**

**AUDIT WHAT YOU ARE ABOUT TO SEND, NOT ONLY WHAT YOU HAVE SENT (run 22).** Five audits have
gone backwards into the register — who opened, who clicked, who registered, which states, which
letters. The one that found the invented addresses went forwards: *what is at the top of the
queue tomorrow night?* The answer was a source that bounces two letters in three, and no
backwards-looking audit would have reached it before the letters were gone.

**A HEALTH CHECK THAT CANNOT SEE THE DISEASE WILL CERTIFY THE PATIENT (run 22).** The MX sweep
was correct, honest and useless against this fault: it verifies domains, and an invented address
has a real domain by construction. "96% clean" was true and meant nothing. **Before trusting a
clean bill, ask what the instrument is physically incapable of seeing.**

**AUDIT THE DENOMINATOR, NOT ONLY THE RATE (run 21).** Run 20 corrected the numerator — 331
"readers" were 34 — and then reasoned from "2,587 letters sent" without asking what a letter
WAS. A rate has two numbers and this project has now been wrong about both, separately.

**A PERSON IS NOT A PROSPECT UNTIL THE PRODUCT HAS A PLACE FOR THEM (run 21).** Two runs on Rick
Wemple — a personal letter, a recoup link, a vigil, an OPEN LOOP across three state files. He is
in Montana. The cheapest question about a prospect is the one nobody asked: can they even
complete the action?

**MY OWN REVERT TEST CAUGHT MY OWN PROXY ASSERTION (runs 21 and 22, two nights running).**
RG-0494's manifest leg passed a tree with the shipping line deleted, because the entry's own
comment contained the filename. RG-0508 then FAILed a correct fix because the fix's own docstring
named the thing it had removed. Same fault, both directions, one night apart. **Writing the
revert test is not the discipline; running it is.**

**An instrument re-aimed at a new question needs its EVIDENCE re-aimed with it (run 20).** The
click register was built to answer "which of our clicks were people?" It was then asked to grade
OPENS, and nobody re-asked what a machine looks like when the machine is a mailbox. The answer
was in the data in plain English — the User-Agent literally says `GoogleImageProxy`.

**Audit the number that is RISING, not the one that is stuck.** Six now: FUNNEL-DENOM-1,
ONBOARD-REAL-1, the contract's naive probe, PROXY-OPEN-1, "2,587 emailed", and "96 reachable
South Africans". Every one flattered. Flattering numbers do not get audited.

**A red is a claim, and a claim gets checked before it is inherited (run 20).** RG-0110 said both
sign-in doors had broken and carried a deploy block. The function's last line disproved it in
thirty seconds. A false RED costs the same trust as a false green.

**A thing "only a person can do" is worth re-testing before it is inherited (run 19).** A blocker
written in confident language was recopied into three runs' state without being tried once. It
dissolved in ten minutes.

**The measurement is a suspect before the app is (run 19).** The acceptance box read "0 chars"
(hidden, not empty) and the confirm row "never appeared" (the loop ran out 27,000 px short). The
app was innocent both times.

**A fix is not finished until you follow the wire to the far end (run 18).** RETURN-LINK-1 was
correct, proven, deployed — and switched on the twenty-minute sender instead of the seven-day
one two functions away.

**Ask what CREATES a number before you believe what it means (run 17).** "42 registered" survived
four runs and reached David in writing because it was plausible, rising and flattering. One query
— group the rows by the minute they were created — killed it in seconds.

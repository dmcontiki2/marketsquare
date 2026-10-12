## 2026-10-12 — The Bee Lady's adverts after her own edit: audit price, the 90-vs-100 Trust Score, her called name, the photo row (TRUST-BADGE-ONE-RULE-1, ANON-PSEUDONYM-1 / RUL-225, ANON-TITLE-TAIL-1, LM-THUMBS-1)

David, 12 Oct 2026 05:09: *"she did change ... the audit price to R7,500 but left it unchanged inside the advert as
R4,000. Please change it there as well"*; 05:13: *"i see a recurring fault, her TS has gone to 90 - it was still 100
last night and even shows 100 on the detail but show 90 in the adverts?"*; 05:37: *"Bee Lady is a pseudo name like the
Handyman. She changed the 10 years to 11 years which is correct as 11 years. Please make it live (also on bea), why
should we leave it as not live?"*; 05:40, with a screenshot of #273: *"Did Marietjie remove these photos or was it
lost in going live?"*

- **TRUST-BADGE-ONE-RULE-1 (fourth fault in the base-40 / TRUST-ONE-SET-1 / CRED-SCORE-SYNC-1 family; closes AUD-101).**
  From the server journal: the Edit screen asks `/trust-score/breakdown?category=Services-Technical`, which scored her
  under the Services set (90) and wrote 90 onto her Services adverts (#538, #539); the buyer's panel scores a seller
  who has any Local Market advert under the Local Market model on all her adverts (SUPER-CRED-2, 22 Jul) and writes
  100. The badge showed whichever screen was opened last. AUD-047 (4 Oct) had taught Edit the advert's own category,
  never the seller's rule. Cure: ONE key rule (`_seller_score_key`) and ONE badge writer (`_write_listing_badges`,
  per category and service class); the Edit screen, the buyer's panel, the profile read and the credential decision
  all go through them. Write scope per surface unchanged. Proved by running the real functions on a copy of the live
  database (`scripts/prove_trust_badge_one_rule.py`): before, panel-then-Edit left [90, 100] and 1 seller of 86 moved
  with the last screen; after, every order leaves the same badge and 0 of 6 multi-category sellers move.
  Guards: two new checks in `test_trust_one_set.py` (predeploy), the heal check in `test_trust_base40.py` re-aimed at
  the one writer (not weakened: still unconditional, value-changed guard asserted in the writer), RG-0681's assertion
  re-aimed the same way, and a ledger entry that fails the moment a second place writes `listings.trust_score`.
- **ANON-PSEUDONYM-1 (RUL-225).** When she saved, ANON-NAMES-1 took "Bee Lady" out of all five titles. David's ruling:
  a trade pseudonym is not a name. The AI read is told so, and a fixed check (`_anon_is_trade_pseudonym`) drops one it
  flags anyway. Real names still go — her brand "Misty Forest" stays out.
- **ANON-TITLE-TAIL-1.** When a real name does leave a title, the joining words and dash before it go too and the
  title keeps its capital ("... — by the" can no longer go live). Table-tested on her five titles.
- **LM-THUMBS-1.** No photo was removed or lost: all 15 were stored and served. The Local Market advert page showed one
  big photo and two arrows with no row of small pictures; it now carries the same row as every other advert page.
- **Live data (server database, a `listing_versions` snapshot before each change):** #538 text "R 4 000 per audit and
  report" → "R 7 500 ..."; titles of #273/#274/#275/#538/#539 carry "by the Bee Lady" / "via the Bee Lady" again;
  "10 years" → "11 years" in the text of #275 and #538 (she had changed #274 herself); badges on #538/#539 healed to 100.
- **Stand-off note (RUL-140):** `bea_main.py`, `ms.js` and the ledger were under the AUTO-RENEW-1 work lock, taken
  03:14Z. David was told and instructed at 05:37 SAST to make it live. Each file was checked byte-identical to HEAD
  (the build had not written to it) immediately before the edit; the edits are anchor-based; only this change's files
  were committed; the release carried the committed HEAD only. The lock itself was left untouched for its owner.
- Fact board before the change (sandbox, 12 Oct 03:5xZ, 634 of 760 entries — one shard of six exceeds the sandbox's
  command limit): 548 holding, 60 ready to lock, 22 open, 1 unverified, 3 regressions that pre-date this work
  (RG-0154, RG-0234, RG-0344).

Cost model impact: none. Schema: none.

**Shipped and proven, 12 Oct 2026 04:05Z (06:05 SAST).** Release 5be9241 through the one deploy lane: stranger test
PASS (356 routes), QA Bot gate pass, health ok, auto-rollback not triggered. On the deployed code:
`prove_trust_badge_one_rule.py` — every order of screens leaves the same badge, 0 sellers move; the real save path run
on her five adverts — the name read flags nothing and each title and text comes back unchanged. Seen in the app in
David's Chrome: #273 carries the row of 15 small pictures (tapping one changes the photo) and "— by the Bee Lady";
#538 shows the title, R7,500, Trust Score 100, "11 years" and "R 7 500 per audit and report".
Fact board after (sandbox, 637 of 764 entries): the same 3 regressions as before (RG-0154, RG-0234, RG-0344), none
new; RG-0960..0963 pass and are LOCKED. The full board and the rulings check are queued host-side.
Rulings check: RUL-225 reflected; its 2 FAILs (RUL-169 confirm.html wording, RUL-211 GEO-NET-CITY-1 marker) pre-date
this work.

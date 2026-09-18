# DAVID'S DECISIONS — 18 Sep 2026, evening (handoff to onboarding-goal run 15, 01:00 SAST 19 Sep)

> **DONE — executed by onboarding-goal RUN 15, 19 September 2026 (01:00–04:00 SAST).**
>
> - Decisions 1–8 are now **RUL-142 … RUL-149** in `RULINGS.md`, reflected in
>   `QUICK_LISTING_SPEC.md` (§1 ladder values, §6 rules, §8 WhatsApp verbatim, §9 taxi drop,
>   §10 post-confirm glimpse) and asserted by `scripts/rulings_check.py` — 126 rulings, 0 FAIL.
> - **Built and proven:** decision 5's "send my draft to myself" — the numberless WhatsApp way
>   back on the Quick hand-back screen (**WA-SELFSEND-1 / RG-0408**), guarded by the LOCKED
>   regression entry this file asked for (**WA-NONUMBER-1 / RG-0407**). Walked end to end in a
>   real browser at phone width as a stranger: q_door → 5 steps → draft → email ask → handover →
>   the WhatsApp button, link shape `https://wa.me/?text=…` with no number and no sign-in token.
> - **Open item 1 closed:** the EULA v1.16 → v1.17 landing is finished in `canon.yml` and
>   `LEGAL_VERSIONS.md`, and `rulings_check` is green. The version-pinned RUL-133 assertion that
>   caused the FAIL was corrected to assert the property, with the real check moved into the
>   ledger (**EULA-VERSION-LAND-1 / RG-0406**, proven in both directions).
> - **Open item 2 closed by probe, not by deploying over it:** the live CityLauncher dashboard is
>   md5-identical to the repo copy and carries the STATS-HUMAN-1 markers. It was stale on 18 Sep
>   and has since been refreshed by another lane. Nothing needed doing; the question of where
>   David reads the board did not need asking.
> - **Not built, and recorded as OPEN ledger entries rather than as sentences addressed to David
>   (SO-4):** the ladder values and the cap of 40 (**RG-0409**), the reachability gate and the
>   post-confirm glimpse (**RG-0410**), the taxi-drop area unit (**RG-0411**), the EULA in the
>   launch languages (**RG-0412**). Each carries why it was not done tonight.
> - **Still David's, unchanged:** D3 (what she is called), D4 (do the SA letters point at the
>   Quick door), D5 (where she comes from at all).


*These are David's rulings, given 18 Sep 2026. They are NOT yet in RULINGS.md or QUICK_LISTING_SPEC.md.
Writing them in is EXECUTION of his decisions (RUL-037), not changing a ruling. Do it first this run,
then use them to push the Easy Lane (Quick Listing, `/q/homehelp`) toward the goal number.*

## The eight decisions (verbatim substance)

1. **Trust-score ladder changes approved.** Referrals move to a rising scale (5/6/7) and must pay for
   verified clients who actually hired her, not signups. Universal cap rises from 30 to ~40. A second
   employer confirmation counts, at 6 points. Employer confirmation stays unconditional at 12 — never
   gated on the confirmer opening an account.
2. **EULA language work approved** — translation into the launch languages, with the English version
   remaining binding and said plainly.
3. **Reachability gate approved (amends RUL-136/137).** A confirmer verifies a phone or email — no
   account required. We store that contact, never publish it, never share it, never attach it to her
   listing, and say so at the point we ask. Their name is still never stored.
4. **Post-confirm glimpse.** After the tap: show her card with the score moving in front of them
   (50 → 62), then two or three other already-public workers in their area. No wall, no account.
   Free-account offer stays after the decision, per RUL-137(d).
5. **WhatsApp without holding numbers.** Use `https://wa.me/?text=<message>` — no recipient in the
   link. She picks from her own contacts. Covers the employer referral and "send my draft to myself",
   which is the no-email answer to the Montana problem. Buyer↔seller stays on Buzz. Us messaging her
   unprompted needs the Business API and money — still David's call (reserved; do not build it).
6. **Area unit is the taxi drop, not the address or the block.** Publish the route/drop and the
   suburb; a block plus her open days can identify a household. Proximity computed for the viewer
   only — "within walking distance of you" — published nowhere.
7. **Correction to an earlier misreading:** the principle is *never share private details*, not
   *never store them*. David, 18 Sep.
8. **Languages:** English, isiZulu, Sesotho, Afrikaans as the minimum four (~90% with cluster
   intelligibility); isiXhosa fifth, needed for Cape Town. 12 official languages, not 11 — SASL
   added 2023.

## Decision 5 in full — Claude's WhatsApp answer, as David approved it (carry VERBATIM into QUICK_LISTING_SPEC.md and the RULINGS row; do not paraphrase it down — David: "i dont want us to regress")

> The WhatsApp answer is better than you'd hope, because the mechanism you want already exists and
> costs nothing.
>
> `https://wa.me/?text=<message>` opens WhatsApp on her phone with a message pre-filled and no
> recipient. She picks who it goes to from her own contacts. We never learn who she chose, never see
> a number, never store one, never transmit one. The link does not contain a number because it does
> not need one.
>
> That gives you three things immediately:
>
> **Her employer referral.** She taps "Send this to someone I work for", picks them in her own
> contacts, and the one-tap confirm link travels over the channel she actually uses. This is exactly
> RUL-115(b) already — she sends her link — just expressed in WhatsApp instead of email. The
> confirmer stays unnamed and unstored, as you said.
>
> **Her way back to her own draft.** This is the Montana problem solved for a market with no email:
> a "Send this to myself on WhatsApp" button. She picks her own chat, and the link to her
> half-finished advert now lives in the app she opens fifty times a day. No API, no cost, no number,
> nothing for us to lose.
>
> **Buyer to seller — you already built it.** Buzz connects two parties without either seeing the
> other's details. That is the answer for introductions; nothing about WhatsApp changes it.
>
> The one thing that genuinely costs money is us messaging her unprompted — that needs the WhatsApp
> Business API and per-message fees, so it stays yours to decide. The two patterns above need none
> of it.

**Regression guard (build it this run):** add a LOCKED ledger entry asserting that every WhatsApp
share link the app emits is `https://wa.me/?text=...` with NO phone number in the path, and that no
code path stores, logs or transmits a recipient number from it. Scope: every Easy Lane button
(employer referral, send-to-myself) and any future WhatsApp share.

## Also open — close these in the same run (no parking)

- **Half-landed EULA v1.16 → v1.17 bump** sits uncommitted in the working tree; `canon.yml` and
  `LEGAL_VERSIONS.md` still say v1.16, so `rulings_check.py` correctly FAILs on RUL-133. Finish the
  bump consistently (or back it out if it is wrong), until rulings_check passes.
- **CityLauncher dashboard on the server is weeks stale**, so the STATS-HUMAN-1 page half never
  arrived. Refresh/redeploy it through the normal lanes (RUL-092 / RUL-095) and verify the RENDERED page.

## Order of work

1. Write decisions 1–8 into RULINGS.md (new rows, dated 18 Sep 2026, amending RUL-136/137 where
   stated) and into QUICK_LISTING_SPEC.md; rulings_check + regression-ledger entries for each.
2. Close the two open items above.
3. Build/ship what the decisions unlock in the Easy Lane, highest effect on the goal number first
   (confirm-page glimpse, wa.me share, reachability gate, ladder values, taxi-drop area unit).
4. Commit and deploy ONCE, after no other lane is writing. Verify in the rendered app.
5. Record in GOAL_STATE.md; mark this file DONE at its top with the run number.

*Housekeeping note: an empty `.git/index.lock` accidentally left by a Cowork session at 20:27 UTC
18 Sep was moved to `Projects/_to_delete/`; git is unlocked.*

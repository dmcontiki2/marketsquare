2026-08-22 (attended, David, evening): SESSION-COUNTER-1 — THE SESSION BADGE WAS NEVER A COUNTER.
David challenged the "Session 155" badge as long overtaken and noted it had been "permanently fixed"
before. Both correct. /dashboard/summary took the FIRST regex match of "Session <n>" anywhere in this
329 KB append-only file; it landed on line 1650 — the 1 Aug paragraph that itself reads "SESSION
COUNTER CORRECTED 150 -> 155". Nothing ever incremented anything, so freezing was the DEFAULT state,
and the two earlier fixes (139->141, 150->155) each corrected the number and left the mechanism, so
each lasted one session. TRUE NUMBER: 175 (anchor 155 at 1 Aug + 20 distinct session-days of
status.d/changelog.d fragments to 22 Aug; a floor — two sittings in one day count once). FIX, two
halves: (1) scripts/session_counter.py DERIVES the number from the fragments every session is already
required to leave, writes SESSION_COUNTER.json, ships via the manifest, recomputes in
deploy_marketsquare.bat before the compilers archive the fragments — the act that proves a session
happened now advances the count; (2) the badge renders "Session N · as of <date>" and greys to
UNVERIFIED off a derived counter, because a bare number lies indefinitely while a dated one confesses
when it stops moving (RG-0133's rule applied to the header). RG-0154 asserts the MECHANISM, not the
number — OPEN until deployed, then READY TO LOCK; it trips red if the prose scrape returns or the
counter drifts behind the fragments. NOT YET DEPLOYED — deploy is David's call; the live badge will
read 155 until the release goes out, and RG-0154's live half correctly fails until then.

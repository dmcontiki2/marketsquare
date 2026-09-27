# 2026-09-24 — the way back to a saved draft was two letters, and the one we pointed at died in 20 minutes

**RETURN-LANE-1 (RG-0444 assertion corrected) · RECOUP-LINK-TTL-1 (RG-0447) · RG-0429 rewritten**

Run 18 of the onboarding goal (RUL-096). The number is still **0**; both probes agree.

**What was wrong.** `goHandoff()` — the sell flow's "draft saved" step — POSTed
`/auth/request-link` and told the seller on screen "we emailed you a link so you can finish
anytime". `/auth/request-link` is the *interactive* sign-in lane: a **20-minute** token
(`_SIGNIN_CODE_MIN = 20`) with no `&draft=` on it. So the letter that toast promised expired in
twenty minutes, and inside those twenty minutes it dropped the seller on the hub's front page
instead of the advert he had just written.

The *right* letter was already being sent, and had been since SELLFLOW-RETURN-1 (18 Sep):
`POST /listings` fires `_quick_draft_return` for the self-serve lanes — seven-day token,
`&draft=<id>`, fails closed on an empty signing secret. PROBED 24 Sep 03:15Z, not read: a
`source='sellflow'` draft logged `quick-return mail for draft 398: sent`.

So the client call was a **second letter, worse than the first, arriving beside it** — and the one
the seller was told to expect. Removed. The toast stays, because a letter really is sent; its
wording now matches what is in it.

**RG-0444's assertion was a proxy and is corrected, not weakened.** It read
`"/auth/request-link" in ms.js` as proof that "the return path has a sender". It was pointing at
the wrong sender — it proved present exactly the letter that fails. It now asserts the lane that
actually carries him back (`_SELF_SERVE_LANES` carries `sellflow`, `_quick_draft_return` exists,
`goHandoff` tags `source:'sellflow'`, and the block does **not** call the 20-minute lane).

**RG-0447 RECOUP-LINK-TTL-1** makes the class explicit: a sign-in link that travels in a *letter*
is never minted from the interactive lane. The code was already right in all six minting sites;
the defect was in a written recipe. `RECOUP_RICK_LETTER.md` (23 Sep) instructed whoever sent it to
mint the publish link from `/auth/request-link` — a 20-minute button posted to a Montana outfitter
who opens his post when he opens it. It also carried no `&draft=382`. Both corrected. The entry
FAILs against the 23 Sep letter on both legs and passes against the current one.

**RG-0429 PUBLISH-WALL-1 rewritten.** As first written it claimed the wizard has *no* route past
the account wall and that the wall is the defect. Both halves were false: `HANDOVER-PUBLISH-1`
already implements RUL-145's shape, and RUL-166 (David, 23 Sep) rules that the EULA acceptance
*moves* but never goes away — an entry demanding no-account publishing would have put the board in
standing conflict with the later ruling. The entry now asserts the property that is actually
load-bearing, in three legs: the road exists, something sends the link with no population exempted,
and that link outlives the reading of the letter.

**Two false reds caught in the writing, both the same shape.** The first draft of RG-0429's
RETURN-LINK-1 leg searched the whole of `goHandoff` for `!magicLink.active`, matched the paragraph
documenting its *removal*, and convicted the fixed tree. Ten minutes later the corrected RG-0444
did it again with `/auth/request-link`. Every good fix leaves behind a comment naming what it
removed, so a function-wide substring test on a fix marker is a trap by default, not a corner case.
Both legs now read the condition line / the block forward from it. Caught by running each entry
against pre-fix, post-fix and reverted trees rather than by reading them.

**Also probed live this run:** the withdraw link in the recoup letter does exactly what the letter
promises — a throwaway draft with a real uploaded photograph went `archived / withdrawn_by_seller`
and the photograph answered **404** at its public URL afterwards (200 before). The 23 Sep
publish hole stays closed: `PUT /listings/{id}/publish` answers 401 with and without
`accepted_terms=1` for a caller with no session. A fresh Montana draft is born `country='US'`.

Cost model impact: none.

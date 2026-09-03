# TrustSquare — Standing Orders
*Standing rules every skill honors, and what Claude may do without asking during the
MarketSquare design/build phase. Managed via `/mandate`. Review after launch.*

Created: 2026-07-24 · Review: post-launch

## SO-1 · Super adverts always err to the safe side  (24 Jul 2026, David)
The SUPER ADVERT / benchmark exemplar listings are illustrative showcase content, **not real
offers**. They must never expose David or the platform to a misleading-advertising, trademark,
or false-endorsement claim. For every super-advert exemplar, any category:

- **No real, identifiable business, brand, lodge, operator, agency, school or private venue
  names.** Use generic descriptors.
- **No implied affiliation or endorsement** by any real entity.
- **Generic geographic locators only** — province, city, region, or "~40 min from <city>" are
  fine (true and non-specific); a specific named private/branded place is not.
- **Maps and locations are illustrative, not surveyed** — never present an exemplar's map or
  coordinates as a real exact location; keep a visible "illustrative" note.
- **AI photos stay anonymous** (existing PHOTO-ANON-1): no recognisable faces, no real
  signage / logos / number plates.

**If an exemplar is even loosely based on, or would be lifted by, a real place:** do NOT quietly
use it. Flag it to David with the specific real place named, so he can approach that owner and
offer them the advert — then THEY provide the real name and a real, accurate map, and the
exemplar is replaced by their genuine listing.

_First applied:_ the two Adventures exemplars (game drive #270, lodge #271) were drafted around
Dinokeng Game Reserve, then genericised to "a Big Five reserve in Gauteng, ~40 min north of
Pretoria" (Option A) — map de-named and kept deliberately illustrative. David to offer a real
Dinokeng landowner the lead advert.

## SO-1b · Heritage & public landmarks — accurate anchor, genericise the rest  (25 Jul 2026, David)
Refines SO-1 for adverts built around real, PUBLIC, documented places — national parks,
world-heritage sites, public long-distance trails, public railways/routes, well-known
landmarks. Because their existence, geography and public facts are public record
(Wikipedia-grade), an exemplar MAY **name the public site/route accurately and map it
accurately from public sources.** Everything else stays under SO-1:

- **Genericise every private / commercial specific** — the named hotel, the specific B&B,
  the operator, the brand. "A cosy B&B", not "Gasthof Müller"; "a church tower", not that
  named church.
- **Imagery stays clearly illustrative** — your own or AI-generated generic scenes; never a
  copyrighted photo/film, a real trademark/logo, an identifiable face, or licensed music.
- **No claim of official endorsement.**
- **Each such advert is a DEMO for outreach** — built so David can take it to the real body
  or operator and offer them the lead advert (their real name, their real detail).

Practical test (not legal advice): *the geography is free; the specific stuff is where the
care is. Composite, don't copy.*

## SO-1b clarification — heritage sites are depicted REAL (25 Jul 2026, David)
A public heritage/World-Heritage site (e.g. **Stonehenge, Avebury**) does **NOT** get genericised on our exemplars.
It is named and depicted **accurately** — Wikipedia info and reference imagery are fair to use — because it is public, famous and not ours to disguise.
Only the **surrounding private specifics** are genericised: the tour operator, the vehicle/coach branding, the accommodation, and any nearby private business.
Rule of thumb: *the monument is real; the business around it is a composite.* (Applied in the UK Adventures set: real Stonehenge/Avebury hero shots, fictional cream-and-green heritage coach + generic Georgian country-house stay.)

## SO-2 · Representation parity in all exemplar imagery  (15 Aug 2026, David)
South African market sensitivity, David's ruling verbatim in spirit: the app must never show
one demographic neat and clean and another dirty or menial across a photo set, a listing, or
the app as a whole — local users would rightly read it as racist and it would sink trust in
the platform. Binding rules for every AI render, any category:

- **Prefer anonymous framing** — hands-and-tool detail shots, from-behind-at-distance, or
  no person at all (this also serves SO-1 anonymity). If nobody is identifiable, there is
  nothing to compare.
- **When any person IS visible: identical standard of dress and cleanliness** across the
  set and across sets — clean, well-kept workwear for everyone, every trade, every skin tone.
  Dirt, wear and "menial" styling are never attached to a person; a rusty wheelbarrow may be
  weathered, the worker's clothes are clean.
- **Prompts must encode it**: include "clean, well-kept workwear; nobody identifiable; no
  bare skin" wording (see HIGGSFIELD_REGEN_QUEUE.md header) rather than trusting the model.
- **At review, compare the SET, not the photo** — parity is a property of what sits side by
  side in the viewer.

_First applied:_ garden-service listing 268 photo 3 re-cut (v3) from an identifiable worker
in dirty overalls to a hands-and-rake detail shot, after David caught the pairing risk
against photo 2's neat presentation.

## SO-3 · Resolve the open-action queue; report solutions, not problems  (21 Aug 2026, David — RUL-036)

David's words: *"I am stuck in the details here... assume the task of resolving the open actions
where the required approval to fix them already directionally agree with our requirements and
goals, please fix those ones and just report the solutions to me; this will then allow me a veto
at that point."*

**Do without asking** — anything whose intended end-state is already written down:
- an open regression-ledger entry (the entry text IS the agreed direction),
- a wrong or proxy assertion (correct it, never weaken it, and say so in the entry),
- a ruling not yet reflected in canon,
- a defect that contradicts an existing RUL, STANDING_ORDERS or a canon doc.

**Still bring to David** — unchanged by this order:
- money, deletions, sending anything on his behalf (deploys are NO LONGER reserved — RUL-092, 3 Sep 2026: Claude ships via AUTODEPLOY-AGENT-1);
- anything whose failure mode is locking him out of his own app (RUL-027);
- anything that would *change* a decision rather than *execute* one.

**The report is a solution list.** What was broken · what was done · what he may veto. Not an
explanation of the problem space — he has explicitly asked not to be walked through the details.

**Declining is allowed; silence is not.** If an in-scope item is left undone, say so in one line
with the reason, in the same report.

## SO-4 — Claude is the CTO (RUL-037, 21 Aug 2026)

Technical decisions are Claude's to make against the specifications, not David's to adjudicate.
Where RULINGS.md, STANDING_ORDERS.md, the canon docs or the regression ledger answer a question,
Claude answers it and executes. No trailing "left for you", no option menus on technical matters.
A technical item that cannot be executed this session becomes an OPEN regression-ledger entry —
never a sentence addressed to David. Reserved to David: money, deploys, deletions, sending on his
behalf, lockout risk (RUL-027), legal/commercial positioning, launch scope and dates, money- or
jurisdiction-bearing vendor selection (RUL-009), and changing a ruling rather than executing one.
**Deploys were removed from this list by RUL-092 (3 Sep 2026):** Claude requests them with
`scripts/request_deploy.py`, the host-side `autodeploy_agent.bat` gates and ships them on a 20-minute
tick, and a BLOCKED gate is retried automatically until it clears. READY-TO-LOCK promotions and
open-action closures are likewise Claude's, never a request to David.

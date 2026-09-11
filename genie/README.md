# The Genie — a TrustSquare sub-project

**Status: DESIGN ONLY. Nothing is wired into the app. No flag, no deploy. Not in the launch month.**
David, 7 Sep 2026: *"obviously we can't build it now in our launch month but i would like to work
towards it."* So this folder exists to hold the thinking, not to ship anything.

## What it is, in one paragraph

TrustSquare is deliberately broad, and breadth reads as complexity to a first-time visitor —
David's words: *"the variety is what we want, the complexity is a side effect; a bad one."* The
genie is the answer to that: a character you talk to in plain language, who does in one sentence
what the menus do in fifteen taps. He has two jobs.

| half | what it does | state |
|---|---|---|
| **Search** — `SEARCH_CONCEPT.html` | Front door to the narrowing funnel: a ring of the seven categories with true counts, then one question at a time. | **Ruled on** — RUL-097, 4 Sep 2026. Design of record is `../ZOOM_HMI_SPEC.md` sec 11. Deferred to a STOCK trigger, never a date. |
| **Wish** — `WISH_CONCEPT.html` | One sentence either finds a thing, or writes the whole advert and hands you a Publish button. | **Proposed**, 7 Sep 2026. Not yet ruled on. |

They are ONE design and must stay one. RUL-097(b) is explicit: the genie is the funnel's front door
and voice, never a second search engine — every narrowing decision below the first tap belongs to
the Zoom spec. A genie with its own narrowing logic means every future facet gets built twice.
That is also why both halves live in this one folder.

## THE HARNESS — supersedes the talking half (RUL-117, David, 10 Sep 2026)

David tested the conversational prototype and ruled the interaction model out: *"the chat sounds
very bad — about a 2 against Siri... it does not accept and goes into a loop from which i could not
recover... there was no way to go back or restart... we don't want any talking."*

**`HARNESS.html` is the front door now.** One tap-only engine, driven by per-category data, for all
eight categories and both directions. **5 taps to a draft advert; 4 taps to a shelf + 3 narrowing
taps to 5 items.** Back and Restart on every screen. Photo tiles at every step, a trail of
thumbnails to keep track, swipe left and right to change category. Zero speech APIs.

What survives from the talking work: the **employer link** and the **vouching gate** (RUL-115) —
David's own idea and the thing that solves the cold start. Those are design, not interaction, and
they plug into the harness at the end of the selling flow.

What does not survive: the microphone, the browser voice, the free-text box, and the
one-question-at-a-time conversation. The Search half's category ring (RUL-097) is unaffected —
the harness IS the narrowing funnel it always pointed at.

## Files

- `WISH_CONCEPT.html` — the working prototype. Press and hold the lamp; try a sentence.
  `#summon` on the URL skips straight to the genie.
- `SEARCH_CONCEPT.html` — the 4 Sep prototype, both shapes tappable, with the covering meter.
  **Two live checkers point at this path** (`scripts/regression_ledger.py` RG-0221 and
  `scripts/rulings_check.py` RUL-097). It was `MarketSquare/GENIE_SEARCH_CONCEPT.html` until
  7 Sep 2026; both checkers were updated in the same session as the move. Do not move it again
  without updating them together.
- `Genie Filter — nice.docx` — the 4 Sep write-up in house style.
- `art/` — the artwork the prototype embeds.

## The artwork

`art/scene_lamp.jpg` and `art/scene_genie.jpg` are **David's own Grok images, cropped** — placeholder
only, so the idea can be judged at the right quality. They are not what ships.

Ours gets generated on the project's existing lane: higgsfield.ai, Nano Banana Pro, David's Ultra
plan, downloads landing in `MarketSquare\_incoming` with nothing for him to click — the same lane
that made the 54 journey photos (`../JOURNEY_PHOTO_RUNBOOK.md`).

**BLOCKED 7 Sep 2026, and it is David's to clear:** Higgsfield shows *"Payment failed. We couldn't
charge your subscription. Unlimited generations are paused."* (PROBED in his Chrome, 01:45). Money
is reserved to David (RUL-037). The two prompts to run are written into `WISH_CONCEPT.html`.

## Open questions, for when this comes off the shelf

1. **His voice.** He says one line, so it is one recorded audio file from a proper voice service,
   generated once and shipped with the app — not a per-use text-to-speech bill. Vendor choice bears
   money, so it is David's (RUL-009). The browser voice in the prototype is a stand-in and always
   will be.
2. **Listening.** Speaking to him instead of typing is a real bill and a microphone permission.
   Out of scope for version one.
3. **What the AI call actually is.** One short call per wish: the sentence in, with the category
   list and the field names; a structured answer out. Roughly the size of the advert-writing call
   the app already makes, so it sits inside the existing daily AI ceiling rather than needing a new one.
4. **The search half's stock trigger still governs the ring** (RUL-097(e)): Zoom armed in the field,
   all seven categories non-zero in a typical city, ~30 days of funnel behaviour. The selling half
   has no such dependency — a person listing a bakkie does not care how many bakkies are already there.

## 2026-09-05 — Contagion model v1.6: the goal agent, the association lane, and two numbers that disagree (MODEL-GOAL-1, MODEL-ASSOC-1)

David: *"update the Cantagion model with our latest Goal orientated scheduled Fable 5.1 project,
including the stistics of us using the clubs, unions, etc. And please update the model in the Ops
Dashboard."* Both done, and the model came back with an answer worth reading twice.

### What went into the model

**The goal agent (RUL-096) is now a modelled lane, not a footnote.** Three levers — `goalW`
(week it starts, default 0 because it has been running unattended since 01:00 on 5 Sep),
`goalCap` (6 per city per night) and `goalCities` (43, measured; it was 14 that morning). The
structural point is the SHAPE, not the volume: the v3.2 ladder is a dated fortnight that stops
because the calendar says so, and the goal agent is a nightly gated draw that keeps going until
a real gate stops it. It shares the city pool with the ladder, so nothing double-counts — it
simply continues where the ladder stopped.

**The association lane — clubs, unions, federations.** Nine new parameters, three of them
`data`-tagged from live measurement rather than guessed:

| | measured |
|---|---|
| committee addresses per provincial body | **289** (AGN 366, WPA 211, read live 4 Sep) |
| survival after one-per-club | **0.542** (577 → 313 distinct clubs) |
| provincial athletics bodies that exist to read | **17**, of which 2 are read |
| teacher rows that are school switchboards, not teachers | **1,194 of 1,235 clean** |

Three lanes, each with its own conversion shape, because they are not the same pathway:
the **club letter** (an organisation reached through its committee, carrying `clubSeats`
listings once it joins), the **federation permission letter** (the only lane where we never
touch the address — the body emails its own members, which is precisely the route RUL-101(e)
left open to France and Portugal), and the **union/SACE door** (not an accelerant on a lane we
have; the only door to an individual teacher, because a school office will never list itself
as a specialist tutor).

**Two observed values pinned for the first time**, probed against 712 real sends: open **21.8%**
and hard bounce **1.54%**. Both sit inside the ranges the model already guessed, which is a
small vote of confidence in the rest of it.

### The finding, and it is the reason to open the model

**Click is deliberately NOT pinned, because the two available readings differ by a factor of
twenty.** Raw: 46 distinct people clicked of 155 who opened = 0.297, above the model's old high
end. Human-verified: the click register grades the same events and finds 56 machines, 11
uncertain and **two humans** — 2/155 = 0.013, below the model's old low end. Corporate
link-scanners fetch every URL in an email and a fetch is indistinguishable from a person unless
something grades it; the same class of error produced eleven phantom opt-outs on 1 September.

So the model now says two different things, and the gap between them is the entire risk:

| | self-published by week 8 (the week 31 Oct falls in) |
|---|---|
| at the assumed click rate | **48** — the goal lands with room |
| at the human-verified click rate | **6** — the goal misses |
| every association door open, human rate | **14** — still misses |

**Sending more does not decide it.** Capacity is not the constraint at 43 cities and 6 a night.
The number that decides the goal is the one nobody has measured: of the people who click, how
many publish. That is now `RG-0288`, held OPEN, watching the join between graded human clickers
and published rows so no session has to remember to look — it prints READY TO LOCK the day the
first real conversion happens, and the value gets written into the model as an observed
parameter.

### An honesty line the model now prints about itself

By week 8 a default run has sent **8,869** emails. Reality on 5 Sep: **712** people have ever
been emailed and the measured reachable universe is **1,441**. The gap is the persistent-scraping
assumption carrying the weight, so the diagnostic strip now says so out loud. Checked rather
than assumed: rows added over the fifteen days to 5 Sep total 2,937 ≈ 32 per armed city per week,
which supports the default — but strip the two bulk events out and the search scraper alone
contributed 908 rows ≈ 10 per city per week. Both readings are now in the lever note, and there
is a preset for the pessimistic one.

**RUL-101 landed in the model too.** A-plan wave 5 (France + Portugal) now defaults to **never**
rather than week 12. That stopped being a timing placeholder the day David ruled those two
countries out of outreach.

Eight new scenario presets, including *TODAY, as the agent is actually running* and *TODAY, but
at the HUMAN-verified click rate* — the two runs worth putting side by side.

### The Ops Dashboard

The +1 page's Horizon view pinned "Contagion Model v1.5 · updated 1 Sep" while the model moved
underneath it, and nothing said so — the same silent-mismatch class as CLUB-LANE-1 itself. Fixed,
and then asserted: **RG-0287** now checks that the dashboard's pinned version equals the model's
own AND that the club counts written on the card are what the database actually holds. A new
GOAL TRACK card carries the goal, the days remaining (arithmetic, computed live), the last probed
published count with its date, the 48-versus-6 split, and the five association-lane statistics
with honest state chips — in pool / 0 emailed, reader built / unread, written / unsent, blocked
correctly, built.

### Verified, not assumed

Both files parse and balance (588/588 and 58/58 divs). The model was rendered headless in a real
DOM: no page errors, the goal stat reads, the new lever groups and all eight presets render, and
the goal diagnostic flips from *lands* to *does not land* when the human click rate is pinned.
Twelve-seed ensemble at week 8: median 74 self-published. Ledger green, every locked fix holding.

`rulings_check.py` went red on RUL-074 and the assertion was narrowed rather than the change
reverted: it used to pin the literal `ring5W:12`, which only a newer ruling could break, and now
pins waves 2–4 plus persistent scraping exactly, and asserts wave 5 is OFF with RUL-101 named
beside it. Both halves are still assertions; the FR/PT half moved to the ruling that owns it.

Ledger: RG-0287 LOCKED, RG-0288 OPEN. The number is still **0**.

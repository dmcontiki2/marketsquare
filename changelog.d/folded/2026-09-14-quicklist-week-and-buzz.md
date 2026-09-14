## 2026-09-14 — The open-days step becomes a week, and requirement 6 gets built

### 1 — Which days are you open?

David, 14 Sep: *"It should show a full week, and allow for selection of any days where there are
openings and they are available."*

The step was `kind:'chip'`, Mon–Sat plus "Any day", single choice, auto-advancing on the first tap.
Three faults in one row: a housekeeper free on Monday, Wednesday and Friday could record exactly
one of them; Sunday did not exist at all; and "Any day" was doing duty as "more than one day",
which is not what it means.

Now `kind:'week'` — a new step kind in the harness engine, not a patch on the chip renderer:

- seven cells, Mon–Sun, each one a toggle; the weekend is drawn dashed because it is priced and
  staffed differently, and a chosen day says **open** where an unchosen one asks **free?**
- an **Every day** toggle for the worker who is simply available; it reads back onto the card as
  "Any day", so the old shorthand survives where it is actually true
- the step cannot auto-advance — the second day could never be added — so it ends with one button
  that also counts back what it is about to commit: *"Next — 4 days open"*, disabled until at
  least one day is on
- the pick keeps the day array on it (`days:[...]`) as well as the printed label, so the hand-over
  can carry structured days the moment the server has a field for them

Because one pick now costs several taps, the *"n taps to get here"* line stopped counting picks and
started counting taps. It was only ever honest by accident before.

The find side keeps its single choice — a hirer wants one day — but now offers Sunday.

### 2 — Buzz: one line, both ways, a name on it

David's four: a buzzer to the owner (late, sick, whatever); the exact same function in reverse
(an extra day, anything else); the name of whoever pressed it; and permission from both parties at
onboarding.

Built as `drawBuzz()`, reached from a card on the advert screen — the example the prospective
housekeeper sees before she refers anyone.

**Three rulings from David the same hour, after seeing the first build:**

1. **The switch lives in TrustSquare onboarding.** Each party grants the two permissions once, as
   they onboard; Quick Listing only shows them so she knows what is coming. One rulebook, one
   place, and both identities already exist there.
2. **No canned messages — a single free line.** The first build offered six one-tap reasons each
   way (running late, sick today, can you come an extra day). They are gone. One text field, one
   sentence, capped at 120 characters, send disabled until something is typed. This overrides the
   note in QUICKLIST_DESIGN_NOTES section B that argued one-tap beats typing on a cheap phone; a
   fixed menu cannot say the thing that actually happened, and half-fitting canned lines are worse
   than a short sentence in her own words.
3. **The panel is universal.** It takes two named parties and a length cap and knows nothing about
   housekeeping, so the same component can be dropped anywhere the platform needs a direct line
   between two paired people.

What it is, then: `BUZZ.parties[0]` and `[1]`, a direction toggle, one input, one button. The buzz
renders on the other party's phone with initials, full name and the time; the answer is the same
component flipped — **Buzz back** swaps the direction, clears the line and focuses it. The reply
carries the answering name the same way. Enter sends. Press send with either permission off and
nothing goes: the screen says why.

Still **no relay, no inbox, no thread**. These two already have each other's numbers; the free lane
exists *because* the worker brought the connection. The anonymous relay still belongs to stranger
introductions in the real app.

### Verified before it was called done

Rendered headless at 400×860 and tapped through, not read: the week cells are Mon–Sun; the button
is disabled on entry; four days select, one untoggles, "Every day" turns all seven on and off; the
advert card comes out reading *"Cleaning, Menlyn, Mon, Wed, Fri, R400"* with the days in the fact
chips; the Buzz refuses to fire without both permissions, then fires with the right name on the
right phone in both directions; the reply receipt names the replier; back returns to the advert.
**Zero page errors.** Eleven screenshots kept; eight of them are the visual page.

### Ledger

Nothing locked in the regression ledger — the week and the Buzz are builds in a local prototype,
not deployed surface. The three rulings above ARE decisions and are recorded as such; no open
action was left hanging.

### Correction, same session — the channel was never the open question

Claude reported that no service worker is registered and no push leaves a phone, and wrote an SMS
fallback into the Buzz copy. David: *"Did we not rule the SMS out because it has a cost associated?
I believe so."* He is right, and both claims were wrong:

- **RUL-122 (12 Sep) rules SMS out.** Web push first, email as the backup, and no channel enters
  the path unless it is free at the margin. SA SMS at R0.15–R0.30 a message breaks that outright.
  WhatsApp falls to the same rule — per-conversation cost — until David reopens it.
- **Push is not dead.** The service worker was 404ing at the root because nginx had no
  `location = /service-worker.js` block; that was found and fixed the same 12 Sep (SW-ROOT-1), and
  the rest was already there: self-hosted VAPID keypair, pywebpush, `_wlRegisterPush()` in ms.js,
  `/wishlist/vapid-public-key`, `wearable_devices`, and `_push_to_seller()`.

The bad sentence came from QUICKLIST_DESIGN_NOTES section B, which was written hours before the fix
and still said "no service worker is registered today; SMS as last resort". That line has been
corrected in place rather than left to re-infect the next session, and the harness copy now reads:
push, free and self-hosted, email if her push is off, no SMS.

**What this means for the build.** `_push_to_seller(conn, seller_email, title, body)` resolves a
user to every device they have registered and pushes to all of them; its `title` and `body` are
exactly the sender's name and the one line. So the Buzz needs no new delivery machinery at all —
only a pair record (who may buzz whom, created when the hirer joins from her link), the two
onboarding switches, and one endpoint that checks the pair and calls that function.

---

## Buzz, built for both apps (same day)

David: *"This looks good, please implement for both apps."*

### The shape

The pair is the unit of consent, and consent is not transitive. A row in `buzz_pairs` means two
people are connected — created when a hirer joins from the worker's own link — and each side carries
its OWN allow flag, because her letting him buzz her says nothing about him letting her buzz him.
Emails are stored lower-cased and ordered so a pair is exactly one row however it is asked for.
A stranger cannot appear in anyone's list: the free lane only ever opens the way the worker opens it,
which is the direction argument from QUICKLIST_DESIGN_NOTES section B, now enforced in a table.

`buzz_log` exists for two operational jobs only — rate limiting and "did it arrive, and how". It is
never read back to a user as a thread. A buzz has no history by design.

### The endpoints

| | |
|---|---|
| `POST /buzz/pair` | connect two people; grants no permission |
| `POST /buzz/allow` | one side's switch, per person, never global |
| `GET /buzz/pairs` | who you can buzz, with both switches |
| `POST /buzz` | one line, with the sender's name on it |

`POST /buzz` refuses, in order and with a stated reason every time: an empty line (400), not
connected (404), their switch is off (403), too many in an hour (429). Silence is the one outcome
that teaches nobody anything, so there is none.

Delivery adds no machinery: `_push_to_seller(conn, receiver, name, text)` — its title is the NAME
and its body is the LINE, which is requirements 2 and 3 met by the function that already existed.
Zero devices registered falls to `_send_html_email`. There is no SMS path and one must not be added
without David reopening RUL-122.

### The live app

`#screen-buzz`, reached from My Space → Buzz. One switch for the phone ("let TrustSquare buzz this
phone" — which binds the account to its buyer_token and runs the existing push registration), then
one card per connected person: name, initials, their switch, one line, one button, and a plain note
when the other side has not switched you on yet, because a buzz that cannot arrive should say so
before it is typed rather than after.

### The Quick Listing harness

The same panel, pointed at the same contract. `buzzLive()` is true only when `HANDOVER.url` and both
emails are set; then it POSTs `/buzz` and prints what the server said — "Delivered to her phone",
"No push on that account, it went to her email", or the refusal verbatim. Without them it is the
example it was this morning, and the screen says which mode it is in. One server, one rulebook.

### Verified before it was called done

- **22 endpoint checks, all green**, run against a temp SQLite database — and run against the REAL
  source text lifted verbatim out of `bea_main.py`, with only the app's dependencies stubbed, so
  nothing here tests a re-implementation. Among them: pairing grants nothing; pairing is idempotent
  either way round; consent is not transitive; a 400-character paragraph is cut to one line; newlines
  cannot make it a thread; a stranger is refused; switching off stops it again; the limit trips; a
  user with no name still buzzes with a name.
- **Both UIs rendered headless and driven.** The live screen posts the right body, shows the right
  receipt, surfaces the server's 403 verbatim, and clears the input; the harness posts the identical
  contract when wired and stays dry when not. **Zero page errors in either.**
- **One real fault found in the render pass and fixed:** `--accent-bright` is used in the app's
  inline styles but is not defined as a token anywhere in `ms.css` or the HTML, so the avatar, the
  switch and the Buzz button all rendered invisible on a white card. The new CSS uses `--accent`.
  Worth knowing beyond this feature: any other inline style reaching for that token is painting
  nothing.

### Deploy

One double-click of `deploy_marketsquare.bat`. All four changed files are already in
`ops/autodeploy/deploy_manifest.txt`, the `?v=` stamps are bumped (288 / 488), and the two tables are
created by `run_migrations()` on the restart the deploy already performs.

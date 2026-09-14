## 2026-09-14 — Quick Listing: the open week, and the Buzz

David: *"For today i would like to set the communication and scheduling, starting at the open days
page."* Both are in the harness (`genie/HARNESS.html`) and both were verified in a rendered browser,
not read off disk.

- **Open days — DONE.** A full Mon–Sun week, any number of days on, an "Every day" toggle, and a
  Next button that states the count back before she commits it. The old step was one chip row,
  Mon–Sat, single choice — a worker with three open days had to pick one and let the advert lie
  about the other two, and Sunday did not exist. The find side now offers Sunday too.
- **Buzz — DONE, and ruled.** One typed line to the other phone with the sender's name on it, the
  identical button in the other direction, and the two permission switches shown as part of the
  tool. Reached from the advert screen ("See how it works"), which is where the prospective
  housekeeper meets it before she refers anyone.

### David's three rulings, 14 Sep

1. **The switch lives in TrustSquare onboarding** — each party grants the two permissions once, as
   they onboard. Quick Listing only shows them.
2. **No canned messages.** The six-item pick list on each side is gone: a single free line, one
   sentence, and the send button stays dead until something is typed.
3. **The panel is universal.** Nothing in it knows what a housekeeper is — it takes two named
   parties and a length cap, so it can be pointed anywhere it is needed later.

`genie/HARNESS.html` is still a local prototype — it is in no deploy manifest and nothing was pushed
to the server today. The visual record is `genie/QUICK_WEEK_BUZZ.html`, tiled in the Visuals gallery.

### One correction, owned

Claude wrote earlier today that no service worker is registered and no push leaves a phone, and put
an SMS fallback in the Buzz copy. **Both were wrong.** The service-worker fault was fixed on 12 Sep
(nginx `location = /service-worker.js`, SW-ROOT-1) and push is live: self-hosted VAPID keys,
pywebpush, `_wlRegisterPush()` in ms.js, `_push_to_seller()` in bea_main.py. And RUL-122 rules SMS
OUT — web push first, email backup, nothing with a per-message cost. The stale sentence came from
QUICKLIST_DESIGN_NOTES section B, written hours before the fix; that line has now been corrected in
place so it cannot mislead another session. The Buzz copy now says push, with email as the backup.

**So the channel question is already answered and already built.** A Buzz is
`_push_to_seller(conn, other_party_email, sender_name, the_line)` — the function's title and body
map exactly onto the two things David required: the name of whoever pressed it, and the one line.
What is missing is not a channel: it is the pair record (who may buzz whom), the two onboarding
switches, and one endpoint.

The onboarding screens that carry the two switches are the next real piece of work, and they are on
the TrustSquare side.

---

## Later the same day — BUZZ IS BUILT, IN BOTH APPS

David: *"This looks good, please implement for both apps."*

**Live TrustSquare app**
- `POST /buzz/pair` connects two people (what the worker's own link does) — connecting grants no
  permission by itself.
- `POST /buzz/allow` is one side's switch: *let this person buzz me*. Per person, never global.
- `GET /buzz/pairs` lists who you can buzz and both switches as they stand.
- `POST /buzz` sends one line: it refuses an empty line (400), a stranger (404), a receiver whose
  switch is off (403) and a leaned-on doorbell (429), and every refusal says which.
- Delivery is the push lane that already exists — `_push_to_seller()`, whose title is the sender's
  NAME and whose body is the line. No devices registered → email. Never SMS (RUL-122).
- Two tables: `buzz_pairs` (the pair is the unit of consent, one row per pair, a flag per side) and
  `buzz_log` (operational only — rate limiting and did-it-arrive; never read back as a thread).
- Screen `#screen-buzz` in the app, reached from My Space → Buzz, carrying the phone switch and one
  card per person: their name, their switch, one line, one button.

**Quick Listing harness** — the same panel now POSTs the same `/buzz` contract the moment the two
accounts and `HANDOVER.url` are wired in, and says so on screen ("Live — posting to the same /buzz
the app uses"). Without them it stays the example. One server, one rulebook (RUL-125(b)).

**Verified before being called done:** 22 endpoint checks green against a temp database, exercising
the real source text lifted out of `bea_main.py` — including that consent is not transitive, that a
paragraph is cut to one line, that newlines cannot make it a thread, and that a nameless account
still buzzes with a name. Both UIs rendered headless and driven: the live screen posts the right
body, shows the right receipt, and surfaces the server's refusal verbatim; zero page errors in
either. One real fault was found and fixed in the render pass — `--accent-bright` is used in the
app's inline styles but is not a defined token anywhere, so the avatar, switch and button rendered
invisible; the new CSS uses `--accent`.

**One deploy, David's double-click:** `deploy_marketsquare.bat`. All four changed files
(`bea_main.py`, `marketsquare.html`, `ms.js`, `ms.css`) are already in the allowlist manifest, the
cache stamps are bumped, and the buzz tables are created by `run_migrations()` on the restart the
deploy performs. Nothing else is needed.

**Claude's one technical call, easily undone:** `BUZZ_MAX_PER_HOUR = 30` in `bea_main.py`. It is not
a ruling and gates nothing else — a doorbell with no limit is a doorbell somebody can lean on.

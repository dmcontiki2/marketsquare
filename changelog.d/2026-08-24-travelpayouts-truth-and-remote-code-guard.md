## 2026-08-24 — Travelpayouts: the review was NOT passed, and two live security holes found closing the door

**What David asked:** Travelpayouts came back saying "we are back up again" — read the email, integrate
their services, and do not let them breach us again.

**What the email actually says.** `support@travelpayouts.com`, Sat 22 Aug 16:53, subject *"Next steps
for your Travelpayouts partnership"*: *"We've reviewed your project and connected it to relevant brands…
you already have access to brands' programs and can start monetizing your content right away."* It
carries no snippet, no instruction and no action. It is their generic connected-brands template.

**What the partner dashboard says (PROBED, 24 Aug 21:51 server time, project Trustsquare / ID 758984).**
The 22 Aug resubmit (RUL-041) was **declined again, for the identical reason as 5 Aug**:

> *"20 programs are currently unavailable for Trustsquare… Your website is currently under development
> or not yet ready. Please complete setting up your site and re-submit your Project for review."*

- **Available: 26** — Aviasales (40%), Kiwi.com, Klook, Tiqets, WeGoTrip, KKday, Go City, Welcome
  Pickups, Kiwitaxi, GetTransfer, intui.travel, Localrent, GetRentacar, Economybookings, QEEQ,
  AutoEurope, BikesBooking, Radical Storage, AirHelp, Compensair, EKTA, Airalo, Yesim, GigSky, Saily,
  Drimsim. This is the same shelf that has been available since 2 Aug — nothing new was unlocked.
- **Still blocked: 20** — including every headliner David approved on 1 Aug: **Booking.com, Viator,
  GetYourGuide**, plus Expedia, Agoda, Trip.com, Tripadvisor Experiences, DiscoverCars, Hotels.com,
  Vrbo, Omio, 12Go, Hostelworld, Busbud, Traveloka, Ticketmaster, Vio.com, Rakuten Travel,
  VisitorsCoverage, Insubuy.
- **Drive reads "Drive is not working"** — correct, we removed the loader on 3 Aug — and the page was
  dangling *"Enable all Drive functions to unlock +25% GetYourGuide rewards through September 30.
  Available until August 24"*: an expiring incentive to reinstall the exact breach vector, aimed at the
  exact programs we are missing. The five Drive functions (Targeted Offers — *"shows them relevant
  travel offer in a background tab"*, Switch Links, Link Relevant Keywords, Insert Recommendations,
  Display Smart Previews) remain **Off** and stay off. Not taken.

**Evidence-ladder note.** The email is a REPRESENTATION and said one thing; the dashboard is a PROBE
and said another. The probe wins, and this changelog is the correction.

### The two live security holes found while closing the door

1. **INDEX-HEADERS-1 — the front page serves no security headers at all.** Measured on a cache MISS, so
   this is the origin answering: `GET /terms` returns X-Frame-Options, X-Content-Type-Options,
   Referrer-Policy, Content-Security-Policy and HSTS. `GET /?cb=…` returns **none of the five**. Cause
   is nginx's `add_header` inheritance rule — a level inherits `add_header` only if it declares none of
   its own, and `location = / {}` declares its own Cache-Control, which silently discards the entire
   inherited set. So the one document that is both the public front door and the SA Smart ID / passport
   upload flow — and the exact page the Drive loader was pasted into — has been serving naked, while
   `nginx_security_headers.conf` sat on disk saying otherwise. It survived because the file was READ and
   the page was never PROBED.
2. **CSP-SCRIPT-SRC-1 — there is no `script-src` anywhere.** The CSP is `frame-ancestors 'self'` and
   nothing else, so any script tag reaching a page executes, from any origin. A full CSP was deferred on
   16 Jul because the index carries ~163 inline `onclick` handlers; that deferral is why the 3 Aug loader
   ran to completion. `'unsafe-inline'` keeps all 163 handlers working **and still blocks every remote
   origin** — the thing that was "too hard" was never needed to close this.

### Shipped this session

- **`scripts/no_remote_code_guard.py`** (REMOTE-CODE-GUARD-1) — scans every file the deploy manifest
  actually places for remote script/iframe/stylesheet references, by static tag *and* by
  `createElement('script') + .src` (the loader's own shape), against a dated allowlist with a written
  reason per origin. Exit 1 on violation. Carries a `--self-test` that feeds it the real 3 Aug tag, the
  same shape on a new host, an unknown host, a remote iframe and a remote stylesheet, and requires all
  five to be caught — a guard that cannot fail is decoration.
  *Its first run surfaced **cdnjs.cloudflare.com**, loaded dynamically by `ms.js aiLeaflet()` and
  inventoried nowhere until now.*
- **RG-0025 rewritten from an instance to a CLASS.** It asserted the absence of two literal strings
  (`tp-em.com`, `NTU3Mzkx.js`) — which catches only the loader we already removed. A new snippet from a
  new host, exactly what a re-approved affiliate account hands you, sailed past it green. It now checks
  every non-allowlisted remote origin, live *and* across the whole manifest. The assertion was wrong,
  not weakened.
- **`migrations/031_csp_and_index_headers.py`** — sets the full CSP (script-src `'self' 'unsafe-inline'`
  + unpkg + cdnjs, no `unsafe-eval`, no wildcard, plus object-src none / base-uri / form-action) and
  adds the header include *inside* `location = /` so the index stops serving naked. Refuses rather than
  guesses if it cannot identify the files, backs up outside the globbed dir, `nginx -t` with auto-restore,
  reload with auto-restore, one-command rollback printed on apply. **Rides David's next deploy.**
- **`travelpayouts_partners.py`** (TP-LINKOUT-1) — the safe integration: server-side 302s only, hard
  outbound host allowlist, our marker appended as a query parameter, click-outs recorded by us before
  the partner hears about it, `Referrer-Policy: no-referrer` on the hop, and a plain-English disclosure
  string. **Fails closed:** all 26 programs carry `deeplink=None`, because the per-brand link formats
  have not been read yet and the module will not invent one. Dark unless `TP_LINKOUT_ENABLED` is set.
  Built precisely so that saying no to Drive stays cheap.
- **New ledger entries:** RG-0177 (the guard is real, can still fail, allowlist has not drifted),
  RG-0178 (script-src enforced — OPEN), RG-0179 (index/app header parity — OPEN), RG-0180 (connect-src
  tightening — OPEN, the honest limit recorded rather than omitted), RG-0181 (the link-out lane fails
  closed and can never grow into a script — OPEN).

**Model constraint respected throughout:** MarketSquare is an introductory service and is never merchant
of record. A link-out is compatible because the traveller pays the partner directly; commission flowing
in is income, not a variable cost (1 Aug pricing ruling).

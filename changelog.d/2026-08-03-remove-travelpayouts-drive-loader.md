## 2026-08-03 — Third-party Drive loader removed from the entire app surface (TP-DRIVE-1 REVERSED)

**David's ruling:** no third-party code may run on the app, at all. If that is a prerequisite for
Travelpayouts' products, the offer is passed.

**What was removed.** The Travelpayouts Drive loader — a remote `<script>` pulling
`https://tp-em.com/NTU3Mzkx.js?t=557391` into `<head>` — deleted from all 10 pages that carried it:
`marketsquare.html` (which ships as the live `index.html`) and the 9 `adventures_*_map.html` pages.
Each file shrank by exactly 474 bytes; all verified to still start `<!DOCTYPE html>` and end `</html>`.
Backups kept beside each file as `*.bak-tpdrive-20260803-185930`.

**Why — the evidence, not the theory.** A browser network capture of a **locked, password-gated page
load with no password entered** showed `tp-em.com`:

- fetching 4 further JS chunks (`chunk.CIR5CNTC.js`, `chunk.Dux8q1cR.js`, `chunk.DHGU-5oI.js`, `chunk.BD_XmNjn.js`)
- POSTing repeatedly to `/collect` and `/collect_batch`
- calling `/link-switch/v1/convert?location=https%3A%2F%2Ftrustsquare.co%2F&trs=557391` (HTTP 200)
- plus a `travelpayouts.com/check_auth` call

The pre-launch gate is a **client-side overlay inside the same document**, so `<head>` executed before
the password box ever rendered. The gate therefore provided **no protection whatsoever**: every hit on
the URL since 2 Aug — testers, bots, scanners, anyone who typed the domain — loaded and ran that code
and sent telemetry back. `marketsquare.html` is also the page carrying the identity-document flow, and
the site has no SRI hash and no `script-src` CSP (`nginx_security_headers.conf` sets `frame-ancestors`
only), so the script ran unpinned with full same-origin access.

**Ledger.** `RG-0025` **inverted, not deleted and not renumbered**. It previously asserted the loader
must be PRESENT on all 10 pages; it now asserts no third-party loader marker appears on any of them,
in the repo or live, and emits an INFO list of every external script origin on the index so the surface
stays visible. Any future session re-adding a remote loader trips it red.

**Revenue impact:** none today. Balance was $0 against a $400 payout floor. The 26 connected programs
work through plain affiliate **links**, which require no script. Only Drive's automated features
(link-switching, Smart Previews, and the Targeted Offers pop-unders) are given up. Travelpayouts site
verification may lapse without the loader — treated as an acceptable cost of the ruling, and to be
re-checked rather than assumed.

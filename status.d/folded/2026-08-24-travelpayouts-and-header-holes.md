### Travelpayouts — the review was NOT passed (and two live header holes found)

**The email is not an approval.** `support@travelpayouts.com`, 22 Aug 16:53, is their generic
connected-brands template. The partner dashboard, PROBED 24 Aug 21:51 (project Trustsquare, ID 758984),
says the 22 Aug resubmit was **declined again with the identical 5 Aug reason** — *"Your website is
currently under development or not yet ready."* **Available 26 / blocked 20**, and the blocked 20 still
include **Booking.com, Viator and GetYourGuide**. Nothing new was unlocked; the 26-program shelf has
been available since 2 Aug. OPEN_LOOPS **D10 stays open** — do not resubmit unchanged (RUL-041).

**Their dashboard is actively pushing the breach vector back**: *"Enable all Drive functions to unlock
+25% GetYourGuide rewards… Available until August 24"* — an expiring incentive to reinstall the loader,
aimed at the programs we are missing. Declined. All five Drive functions remain Off.

**Two live security holes, found probing while closing that door:**

1. **The index serves NO security headers** (INDEX-HEADERS-1). Origin-confirmed on a cache MISS:
   `/terms` returns all five (CSP, XFO, nosniff, Referrer-Policy, HSTS); `/?cb=…` returns none. nginx
   `add_header` inheritance — `location = / {}` sets its own Cache-Control, discarding the inherited
   set. The naked page is the front door *and* the ID-upload flow *and* the page the loader was on.
2. **No `script-src` anywhere** (CSP-SCRIPT-SRC-1). CSP is `frame-ancestors 'self'` only, so any script
   that reaches a page executes. `'unsafe-inline'` keeps the ~163 inline handlers and still blocks every
   remote origin — the deferral that made this "too hard" was never needed.

**Fixed / built:** `scripts/no_remote_code_guard.py` (class-level, self-proving); **RG-0025 rewritten
from a two-string blocklist to the class** (it would have passed a new TP snippet green);
`migrations/031_csp_and_index_headers.py` (refuses rather than guesses, `nginx -t` + auto-restore,
one-command rollback); `travelpayouts_partners.py` — the safe link-out lane, server-side 302s, hard host
allowlist, dark by flag, all 26 deeplinks `None` because it will not invent a link format.

**Ledger:** RG-0177 LOCKED; RG-0178/0179/0180/0181 OPEN. Run: 174 entries, 0 regressed.

**Needs David:** the CSP + index-header fix is an nginx change that rides **his next deploy** (RUL-037).
It is the highest-value item in the 27 Aug ship.

## 19 Aug 2026 (evening) — Marietjie's BLOCK page: diagnosis PINNED, handed to the active fix session

Server is fully open (/, /listings, /review/verify all 200 anonymously, verify says valid:true).
The block she saw is CLIENT-side, two proven causes — probes on record in this fragment:

**A. www trap (deterministic block for every www visitor).** `https://www.trustsquare.co/`
answers 200 with the app (no redirect to apex). The shell's `BEA = 'https://trustsquare.co'`
makes the verify fetch CROSS-ORIGIN from a www page, and the server returns **no
Access-Control-Allow-Origin for Origin: https://www.trustsquare.co** (probe: ACAO MISSING).
Browser blocks the response → the overlay's fail-closed `.catch(showGate)` fires → BLOCK page.
Class fix: 301 www→apex at the edge; code-level class fix: make BEA origin-relative
(`location.origin`) so no same-site page can ever be cross-origin to its own API.

**B. stale shell (intermittent).** The document is cached `public, max-age=300,
stale-while-revalidate=600` (Age header confirms caching active). Any browser/edge holding the
pre-15-Aug shell runs the old `if(!rt){showGate()}` short-circuit — gate shown WITHOUT asking
the server. Fix: `no-store` (or short max-age + purge) on the DOCUMENT while the overlay code
still ships in it. NOTE: RG-0090 was parked 19 Aug as "no subject" when the gate dropped — this
is its inverse (stale GATED shell over an OPEN site). Un-park/repoint RG-0090 when fixing.

**Ledger note for whoever fixes:** RG-0115 asserted "down for everyone" but its client-half
probe only checked apex + fresh client — extend it to (1) www origin CORS, (2) document
cache headers, or the class returns wearing a third face.

Immediate user workaround given to David: apex URL only, hard refresh.
This session is NOT editing marketsquare.html/nginx — another session holds the fix.

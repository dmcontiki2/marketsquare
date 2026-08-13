## 2026-08-13 — Real root cause from the deploy log: 007 rc 3, duplicate conf files (GATE-ENFORCE-2c)

David's SSH paste settled it: 007 never no-opped — it FAILED rc 3 on both deploys:
"multiple candidate site files, refusing to guess: sites-enabled/marketsquare,
sites-available/marketsquare". The two are duplicate REAL files (not the Debian
symlink), so realpath dedup saw two candidates. Failing FIRST in the chain, 007 also
blocked 016 from ever running. The conf itself is clean — no stale marker, no
fragments, catch-all matches the anchor at sites-enabled/marketsquare:169 — so the
earlier marker hypothesis is WITHDRAWN; a clean apply awaits.

Fixes, riding the next click: (1) 016 find_site is now ENABLED-FIRST (nginx serves
sites-enabled; available is inventory) and notes the stale duplicate after applying;
(2) 007 re-deferred in DEFERRED.txt as SUPERSEDED so it stops breaking the chain;
(3) 005 gets the same enabled-first lookup so David's future document-gate ruling
does not replay this failure. Box observation for /housekeep: sites-available copy
will be stale post-apply; symlink it someday. (Also on the box, unrelated: a second
app "snaptax" on :8090 shares this nginx.)

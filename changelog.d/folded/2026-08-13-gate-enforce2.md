## 2026-08-13 — 007 no-opped GREEN; migration 016 asserts the thing, not the label (GATE-ENFORCE-2b)

The 05:0x deploy carried the 007 activation and the chain ran PAST it (proof: migration
015 executed — /static/maint/b4_tier2.json now exists) yet the gate did not rise:
anonymous /wonders answers 200 at the ORIGIN, cache-busted, so this is not CDN staleness.
Only one rc-0 path in 007 fits: its idempotency test is `if "GATE-ENFORCE-1" in text` —
a MARKER check — and the marker evidently sits in the server conf (leftover of the 5–7 Aug
SSH-era work DW-020 planned) with no functional gate beneath it. 007 recorded itself done
and will never run again. The exact green-no-op class STATUS.md logged six times on 11 Aug.

Fix shipped: **migrations/016_review_gate_enforce2.py** — identical block and safety rails
to 007, but idempotency is FUNCTIONAL (`auth_request /_review_gate` inside the catch-all),
a stale marker is reported loudly and overridden, and pre-existing PARTIAL gate fragments
trigger a precise-inventory REFUSAL (rc 7) instead of duplicate-location nginx breakage.
Verified locally: py_compile clean, dry-run clean, repo-conf simulation = would apply
(functional absent, collisions none, anchor exactly once).

Rides David's next release click. Then: anon-401 verification → RG-0029 READY TO LOCK →
promote. If 016 refuses with rc 7, the deploy log's inventory line is the next input —
one SSH paste (ACCESS_CHEATSHEET §4) and the conf gets one manual reconciliation.

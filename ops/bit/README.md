# ops/bit — the shipped copy of the BIT self-test agent (SERVER-BIT-1, 11 Aug 2026)

Canonical source: `Projects/trustsquare-bit-agent/` (article, outside this repo).
These copies ride the ONE deploy (manifest -> live root /bit/) so the server can run
the cycle itself every 15 min via systemd timer (installed by migrations/013).
BIT_BASE=http://localhost:8000 — the origin gate (GATE-ENFORCE-1) 403s off-browser
public HTTP, and localhost is the proven lane (cf. scripts/fault_reconcile.py v2).
Mitigation stays OFF (no BIT_APPLY) — detect + post the board, nothing else.
If you change the agent, change the article first, then re-copy here.

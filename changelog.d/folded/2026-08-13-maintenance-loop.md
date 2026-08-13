## 2026-08-13 — maintenance-loop: GATE-COOKIE-1 — the B2b lanes ride the armed gate (RG-0064)

The 13:17Z maintenance run died at intake: GET /admin/faults answered 401 from nginx —
GATE-ENFORCE-2 (migration 016, ~05:4x deploy) armed auth_request on the catch-all and the
exempt list (007 unchanged) never carried the maint-key lane. Latent since 7 Aug; never bit
while 007 was a green no-op. The agent failed safe ("nothing read") — correct, but the whole
remote B2b lane was dark: intake, fault PUTs, close-send, heartbeat, fault_reconcile.

Fix — carry the credential, never widen the gate: maintenance_agent.py api() and
fault_reconcile.py call() now mint the ts_review cookie on 401/403 exactly as
regression_ledger._get does (once per run, .secrets/review_code.txt, fail-safe preserved).
Nginx untouched; widening the exempt list unattended was deliberately refused — if David
prefers an origin-side maint-lane exemption (007's machine-to-machine doctrine would cover
it), that is his call.

Evidence: 13:24Z run clean through the gate — 1 seen, 1 acted, heartbeat received_at
13:24:46Z on the live card (RG-0061 reads it). RG-0064 LOCKED: source halves + credentialed
intake + inverse guard (anonymous /admin/* must STAY 401/403 — the fix can never become a hole).

Also: BRAIN-DEPS-1's detached-run pattern died at the bash-call boundary in today's Cowork
sandbox (background processes reaped, setsid included). Working method: pre-install httpx,
then run the agent FOREGROUND with a 10-min tool timeout. Scheduled-task prompt needs
David's one-line amendment.

Queue: TS-0031 (cars pre-final, AI vehicle details) → PATH_B design backlog, third
consecutive run with the same brain verdict — sits for the designer gate. No Path-A items.

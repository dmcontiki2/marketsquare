## 2026-09-01 — Ops-dashboard 'SESSION UNDEFINED': server healthy, viewer signed out; DW-084 CLOSED on the full story

- David reported the ops dashboard reading 'Session —' / 'SESSION UNDEFINED'. PROBED: the authenticated summary is COMPLETE (session 184, all sections); anonymous callers get the deliberate heartbeat redaction (RG-0211). Cause: signed-out browser (sessionStorage JWT gone). Fix: sign in again.
- Underneath, the DW-084 landmine had FIRED at 06:00:26 UTC — unattended-upgrades restarted the service and MS_API_KEY swapped. Resolution: rotate_secrets.py doctrine — MS_API_KEY is PUBLIC IN MS.JS BY DESIGN; the swap put the server back in sync with every client. 8-var env-vs-config sweep SAME on every row; smoke ALL PASS; /payment/test ok. **DW-084 CLOSED** — no rotation, which would desync clients.
- **RG-0237 NEW (OPEN)** — DASH-SIGNEDOUT-TRUTH-1: a signed-out dashboard must SAY so (RG-0133 class); loader branch ships with tonight's deploy, promote on READY TO LOCK.
- DW-089 corrected: MS_API_KEY struck from the exposure set (public by design); the three real burns re-verified STILL LIVE — rotations remain tonight's first item.
- Concurrency note: a parallel session claimed RG-0235/0236 and committed while this pass ran (index.lock contention, self-healed via git_unlock lane); this entry took the next free id: RG-0237.

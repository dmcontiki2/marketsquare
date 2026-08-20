## 2026-08-20 — maintenance-loop

Daily B2b maintenance session ran clean. Fault queue EMPTY (0 new, 0 fix-shipped;
26 verified / 7 closed / 2 duplicate of 35). Shadow agent heartbeat posted and
readable at `/dashboard/maint`. Regression ledger green before and after; RG-0090
and RG-0120 promoted OPEN -> LOCKED. RG-0125 (migration 023 jamming the chain)
narrowed — catalog and import refuse paths both ruled out by live probe; the cause
text arrives with POSTDEPLOY-EYES-2 on the next deploy. No code fix shipped this
session because nothing in the queue asked for one.

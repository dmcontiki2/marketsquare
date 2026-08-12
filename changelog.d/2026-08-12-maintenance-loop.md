## 2026-08-12 — maintenance-loop: TS-0024 + TS-0022 verified, RG-0060 tripwire added

- Pre-run ledger green (59 entries, 56 holding, 3 open). Shadow agent run 05:33Z: 2 faults
  seen, both PATH_B — the sandbox brain has NO AI lane key (4th consecutive run; the loop's
  brain-by-hand is this session, per PRE-LAUNCH MONTH).
- **TS-0024** (AI coach unavailable, Maroushka, 7 Aug) → **verified** (LIST-024). Named
  evidence: failing action reproduced clean on live — POST /advert-agent/coach, Property,
  HTTP 200 in 10.0s, full coaching JSON (cost: 1T from David's wallet, balance 366T, one
  Haiku call). Class pinned by NEW ledger entry **RG-0060**: zero-spend probe (unregistered
  email → 401 before any model call) proves the coach front door answers whenever /flags
  names an active lane; 503 there is the tester's fault back.
- **TS-0022** (over-blurred covers, sat at `fixed` since 11 Aug) → **verified**. Named
  evidence: RG-0047 (painted-output blur ceiling) + RG-0044 (refuse-not-ruin) both green on
  today's live runs. Reporter's 9 legacy covers remain her optional re-uploads.
- **TS-0031** (Cars AI specs inaccurate) left in **Path B** — genuine design change
  (suggested-not-asserted specs UI + confidence bar), designer gate applies; awaiting
  reporter's which-fields detail. Not a refused surface, just not mechanical.
- Close-send letters for TS-0024/TS-0022 NOT sent — that press stays David's.
- Post-run ledger green: 60 entries, 57 holding, 0 regressed, 3 open (RG-0003/0004/0029).
  Escalation brief: none in 24h. No push, no deploy (NIGHTLY-SHIP-1 carries the commit).

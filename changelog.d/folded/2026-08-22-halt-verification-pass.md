## 2026-08-22 — D-7 HALT verification pass: the double-charge proven, and a placebo breaker found

Second HALT pass over the morning's consolidated launch verdict. It deliberately did NOT re-run the
three-cycle audit that completed at 07:22 — a second divergent report is the between-sessions blind
spot the machinery exists to prevent. It re-PROBED the verdict live and pushed the stress lane further.

- **Re-verification (07:25 SAST).** /health, /flags, /auth/providers, /dashboard/bit, /id-verify/status
  and /dashboard/summary all re-probed; regression_ledger.py and rulings_check.py re-run. Every live
  claim in the 07:22 report holds. The anonymous posture leak was reproduced. B4 stays NOT MEASURED
  (/admin/ai-spend/summary still 401 anonymously). Drift recorded: rulings 39 -> 40, ledger open
  defects 3 -> 8 (RG-0137..0141 landed after the report closed; RG-0140 and RG-0141 are
  customer-facing on the LIVE build and belong on the launch board).

- **B2 raised READ -> EXECUTED.** accept_intro's exact SQL sequence was replayed against a throwaway
  SQLite replica (no production data, no production box, per the HALT safety boundary): 1T -> accept
  -> 0T -> accept again -> -1T -> four accepts -> -3T, four intro_deduct rows for ONE introduction.
  The handler never tests the status/tuppence_charged flags it is about to set, and there is no floor
  at zero. Operating limit one accept, destruct limit two.

- **NEW weak link, missed by all three cycles: the automatic safe-state response is a placebo.** All
  three flags in the BIT Mitigator's SAFE_FLAGS (auth_fail_closed, tuppence_burn_enabled,
  ai_example_enabled) appear in bea_main.py only at the schema, migration, /flags exposure tuple,
  write model and read-back — never at a decision site — and neither ms.js nor marketsquare.html
  reads any of them. The mitigator flips the flag, journals it, reports the S1 mitigated, and the app
  carries on unchanged. The detection layer is real (B-NEG-AUTH is live and passing); the mitigation
  is decorative. Worst case: tuppence_burn_enabled promises "you will not be charged in the
  meantime" and stops no charging — the very lever an operator would pull during a double-charge.

- **Hardened: three OPEN ledger assertions**, each written as a class, not an instance.
  RG-0142 the money path is idempotent and a wallet can never go negative (source assertion by
  design — proving it live would mean charging a real buyer twice). RG-0143 every flag the BIT
  Mitigator may flip is actually read by the app. RG-0144 the public dashboard never publishes which
  defences are down. Ledger: 137 assertions, exit 0, every LOCKED fix holding, 11 open.

- **Verdict unchanged: HOLD.** Hardening and Hack-proofness stay RED; Robustness and Reliability are
  weaker-evidenced AMBERs than before. Across four independent passes no verdict has moved upward.
  Deliverables: FORENSIC_AUDIT_D7_VERIFICATION — nice.docx and FORENSIC_HALT_VERIFICATION_BOARD.html
  (indexed into Projects\Visuals). Reserved to David: secret rotation, the deploy carrying these
  fixes, the gate/WAF posture ruling, and the launch go/hold call.

- **Adversarial check — both new findings UPHELD and their grades RAISED.** A fresh peer given one
  instruction (break them) ran the REAL bea_main app under a FastAPI TestClient against a scratch DB:
  four PUTs to /intros/1/accept returned 200/200/200/200, balance 1 -> 0 -> -1 -> -2 -> -3, four
  intro_deduct rows for one introduction, full middleware stack running. It then wrote the mitigator's
  FULL safe state into the DB and charged again: 200 OK, a fifth deduct row. It also confirmed the
  placebo finding against the LIVE-served 1.12 MB ms.js (zero occurrences of the three flags) and
  closed the "wrong entrypoint" defence -- the manifest ships bea_main.py AS main.py.
  Sharper still: estate_agents.py ALREADY has the correct guards (409 non-pending, 402 below balance)
  with tests -- the house pattern was written, tested and never applied to the flagship buyer path;
  and create_intro takes no hold and never checks balance, so a 0T buyer goes negative on the FIRST
  accept, no retry needed.

- **Two further defects in the same class.** decline_intro writes status='declined' with no transition
  check, so a decline-after-accept leaves tuppence_charged=1 with no refund row (folded into RG-0142).
  And the shipped EULA tells a buyer 1T is "committed (held) when the Buyer makes the request" and
  "released in full if declined or expired" -- there is no hold, no release and no balance check at
  request time anywhere in the code. Fixing idempotency does not close it. New entry **RG-0145**;
  how it resolves (implement the hold, or change the wording) is David's call, not Claude's.

- **The assertions were wrong twice, and were FIXED the same session, not weakened.** The peer found
  three false-red and three false-green paths in the entries as first written. Worst false-red:
  RG-0144 read the payload through _get(), which transparently retries a 401/403 with the reviewer
  cookie -- so gating the endpoint behind auth (one of the two right answers) would have kept it red
  forever and pushed a later session to weaken it; it now checks anonymous status via _status() first
  and broadens the banned set from six literal words to patterns. Worst false-green appeared on the
  NEXT run: RG-0142's broadened token list let accept_intro's own UPDATE ... SET tuppence_charged=1
  satisfy the check for code that READS that flag. Guards now match only control flow (if/elif/assert/
  early return), never SQL handed to conn.execute. RG-0143 likewise strips comments, detects the
  /flags exposure line structurally, and treats an empty SAFE_FLAGS as a PASS (removing a flag is one
  of the two sanctioned fixes and must not read as red). Every correction is written into the entry's
  own ref. Ledger: 138 assertions, exit 0, every LOCKED fix holding, 12 open.

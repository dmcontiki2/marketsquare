# RULINGS.md — David's decision register (born 15 Aug 2026)

**Why this file exists.** The launch date (1 Sep full / 29 Aug soft-public) was expressly
reviewed and fixed across several sessions — and never reached the canonical files. A 15 Aug
sweep found "launch date STILL NEEDED from David" as the last word on disk. David's words:
"another of our challenges in having blind spots between sessions... part of my frustrations
to try and keep it all together as a human." The project already has machinery for FIXES
(regression ledger: a fix is not done until locked). It had none for RULINGS. This is it.

**THE RULE — same class as the ledger rule:**
> A ruling is not made until it is in THIS file, with its reflection points, in the SAME
> session in which David made it. `scripts/rulings_check.py` then asserts each ruling is
> actually reflected where the next session will look. No entry = the ruling does not exist
> as far as the machinery is concerned — which is exactly how the launch date got lost.

Append-only. Re-read before writing (low frequency; no compiler needed). Never renumber.
A superseded ruling is marked SUPERSEDED-BY, never deleted.

---

| ID | Date | Ruling (one line) | Reflected in |
|---|---|---|---|
| RUL-001 | 2026-08-15 | **Launch: FULL Mon 1 Sep 2026; SOFT-to-PUBLIC Fri 29 Aug 2026 (gate down). Fixed date sequence, expressly reviewed.** Hold fallback = one month, bought once | LAUNCH_BAR_2026-08-15.md; BACKLOG LAUNCH-DEADLINE-1 must re-set 2026-08-01 → 2026-09-01 |
| RUL-002 | 2026-08-14 | OpenAI = BASE usage lane; Anthropic = AUTO-FAILOVER + the DESIGN/guidance tool; Scaleway = ban/outage SAFETY NET (cost-exempt, alert-on-use). Flip gated on P1–P6 | AI_BASELINE.json v2 · AI_LANE_GUIDANCE.md |
| RUL-003 | 2026-06-12 | 60 staged prospects/city = WAVE TRIGGER, never a public-launch threshold. "60 founding sellers = launch gate" was a doc error (CC-003 purge) | BACKLOG.md must not carry launch-threshold wording — CC-003 still 0/5 after 2 months |
| RUL-004 | 2026-07-31 | No pure Chinese ENDPOINTS for any workload; Chinese-origin MODELS acceptable via Western/EU hosts | AI_VENDOR_STRATEGY_DECISION Add. 6 · EU_HARNESS_REDUNDANCY_2026-08-15.md |
| RUL-005 | 2026-07-29 | Maintenance agent: TOTAL AUTONOMY, NO VETO — human gate replaced by mechanical gates (ledger, predeploy, BIT, rollback, refuse-markers). Condition: any gate that stops asserting re-arms the veto | MAINTENANCE_AGENT.md · maintenance_agent.py refuse markers |
| RUL-006 | 2026-08-02 | ONE DEPLOY — code ships only by publishing the deploy ref; scp from bats/sessions banned (RG-0023) | ONE_DEPLOY.md · regression ledger RG-0023 |
| RUL-007 | 2026-08-01 | Tuppence feature prices are FIXED; no percentage-of-value cost may enter a feature price. Flat cappable external costs only | PRICING_CANON.md · ../CLAUDE.md |
| RUL-008 | 2026-08-01 | MarketSquare is an INTRODUCTORY service — never merchant of record for third-party goods/travel; nothing but Tuppence through the till | ../CLAUDE.md travel section |
| RUL-009 | 2026-08-14 | AI model selection is NEVER automated. Fixed baseline (model + cost envelope) + equivalent swaps only; automatic challenge, manual decision | AI_BASELINE.json · ai_baseline_check.py · ai_challenger_board.py |
| RUL-010 | 2026-08-15 | DeepSeek hosted API OUT; EU-hosted open weights eligible; HARNESS-PILOT-1 is a slip-month/post-launch item, floor work first | EU_HARNESS_REDUNDANCY_2026-08-15.md |
| RUL-011 | 2026-07-25 | A fix is not done until LOCKED in the regression ledger, same session, with scope stated | ../CLAUDE.md ledger section · regression_ledger.py |
| RUL-012 | 2026-06-17 | Edit/Write tools banned on the Projects mount (silent truncation); all file writes via bash heredoc with landing guards + timestamped .bak | ../CLAUDE.md hard rule |
| RUL-013 | 2026-08-15 | **Fault-resolution operating model, both phases.** PRE-LAUNCH (to 1 Sep): the maintenance agent does NOT surface failures or reports to David — testers are the fault source and AI resolves without him; escalations route to the FIX AGENT (Fable) under standing pre-approvals, with laptop resources open — Fable works IN A COWORK SESSION on the subscription, never via ANTHROPIC_API_KEY (SPEND-GUARD-1). **TIME-BOXED: this arrangement ENDS 1 Sep 2026 and does not renew by default.** FROM 1 SEP: Fable is OUT — design work returns to the allocated design agent or its swapped-out option (the 'design' task tier: openai gpt-5.6-sol, scaleway standby). Source becomes user complaints; maintenance agent handles most; fix agent handles 98% of the remainder; David on STANDBY for the residual ~2% for the FIRST TWO MONTHS, with Claude's support. Extends RUL-005 (total autonomy, no veto) — and inherits its condition: any gate that stops asserting re-arms the veto | MAINTENANCE_AGENT.md · STANDING_ORDERS.md · RUL-005 · RG-0080 |
| RUL-014 | 2026-08-15 | **Pre-launch gate entry is EMAIL-LINKED** — tester types an allowlisted email, gets a one-time link (30 min, single-use) that sets the same ts_review cookie; reviewer code demoted to break-glass, never removed. IP containment layers unchanged (origin lockdown, armed gate, rate limits); claim email+IP logged; tokens NOT hard-bound to claim IP — rotating tester ISPs were part of the lockout class this ends | bea_main.py GATE-EMAIL-1 · migrations/019_gate_email_link.py · marketsquare.html gate screen · regression ledger RG-0081 · ACCESS_CHEATSHEET.md |
| RUL-015 | 2026-08-15 | **Per-surface entry doctrine:** marketplace gate + personal accounts = EMAIL-LINKED; Admin and Dashboard (incl. the +1 page) deliberately KEEP password/PIN entry as the higher-security door — David: 'for the dashboard I prefer the extra code as security'. Never email-link the admin surfaces | ACCESS_CHEATSHEET.md · dashboard.server.html/admin gate (password path intact) · RUL-014 |

| RUL-016 | 2026-08-15 | Cars spec lane stays DECLARED + SELLER-ATTESTED (TS-0031 closed): VISION-inferred specs remain with the SPEC-PROVENANCE-1 attestation screen as the fix; grounding against an external vehicle-spec source and dropping the AI market note both DECLINED for now — revisit post-launch if wrong-spec reports recur | BACKLOG.md 14-Aug cars row · app_faults TS-0031 fix_note · FAULT_REGISTER.md LIST-003 note |

| RUL-017 | 2026-08-15 | Report & Fix lane (OPS-SWEEP-1): amber/red ops states are EMAILED to David as they appear, with reply commands FIX (queue for Fable's pickup run) / REVIEW (hold for a session) / REPORT. Refines RUL-013's pre-launch quiet: an FYI + opt-in lane at David's request — autonomy, gates and the no-deploy-without-the-ref doctrine unchanged | scripts/ops_sweep.py · migrations/020_ops_sweep_cron.py · orchestration_v2/cockpit.html Report & Fix card · deploy_manifest ops_sweep + cockpit lines |

| RUL-018 | 2026-08-15 | REPRESENTATION PARITY (SA sensitivity, David): never one demographic neat and another dirty/menial anywhere in the app's imagery. Prefer anonymous hands-and-tool framing; any visible person wears clean well-kept workwear, identical standard across every set. Prompts must encode it | STANDING_ORDERS.md SO-2 · HIGGSFIELD_REGEN_QUEUE.md parity rule · listing 268 photo 3 v3 |

*Seeded 15 Aug 2026 from this session plus standing canon — NOT exhaustive. Sessions append
as rulings are made; older rulings get added when they surface (that they must surface at all
is the failure this file ends).*

| RUL-019 | 2026-08-15 | **WORLDWIDE LAUNCH SCOPE — GO.** Payments verified worldwide-capable (Paystack intl enabled + Apple Pay, verified in dashboard): the launch proceeds with WORLDWIDE reach, not ZA-only; last BACKLOG launch blocker (B1) cleared same session. Launch DATES unchanged (RUL-001). Money-path go-live still requires the A10 env pastes (sk_live + webhook secret, David) | BACKLOG.md B1 row + A10 · FINANCE_CANON.md Re-verification log · GLOBAL_PAYMENT_RAILS_2026-08-15.docx · status.d 15 Aug fragments |

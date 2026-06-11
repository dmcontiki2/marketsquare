# INTRO HOLD — BEA implementation spec (CC-001 · staged 10 Jun 2026)
**Status: SPEC ONLY — Gate 2 attended build. No code changed this run.** Pattern source: the live AI hold ledger (`/tuppence/ai-commit` + `/tuppence/ai-settle`, bea_main.py ~11510, S132).

## Why spec, not diff
The intro flow touches the Tuppence ledger (Gate 2 + POLICY §12), interacts with live in-flight intros, and needs migration + smoke coverage decisions that are David's. The AI ledger gives an exact, tested pattern to mirror; an unattended diff would be guess-shipping a money path.

## Target state machine (Codex v4.8 §12)
```
POST /intros            → COMMIT  intro_hold (−1T, atomic, balance-checked; 402 if insufficient)
PUT /intros/{id}/accept → BURN    intro_hold → intro_burn (earned, final)
PUT /intros/{id}/decline→ RELEASE intro_hold → intro_hold_released + intro_release (+1T)
48-h expiry             → RELEASE (same path as decline; seller Trust-Score penalty per A3 unchanged)
```

## Edits required (all in bea_main.py unless noted)
1. **POST /intros** — after listing/buyer validation, run the commit inside one `BEGIN IMMEDIATE` transaction: balance check → insert `intro_hold` txn (−1, type `intro_hold`, idempotency key = intro id) → create intro row. Reject 402 `insufficient_tuppence` before intro creation. NOTE: today POST /intros is auth-free (buyer action); commit requires a known buyer email with balance — confirm flow for first-time buyers (top-up before request, mirroring AI gate order: known-user → balance).
2. **PUT /intros/{id}/accept** — inside the existing accept transaction: settle hold → `intro_burn` (idempotent: re-accept of a settled intro → 409). Remove/replace the current charge-on-accept debit (the accept handler's existing 1T deduction).
3. **PUT /intros/{id}/decline** — settle hold → `intro_hold_released` + compensating `intro_release` (+1), idempotent.
4. **Expiry job** — the existing 48-h ignore handling (Trust-Score penalty + unpause) gains the release settle. If no scheduled sweep exists, settle lazily on next read of an expired intro (same outcome, no new infra).
5. **GET /tuppence/balance** — already authoritative-read (invariant #6); holds reduce available balance via the txn sum — verify the txn-sum query includes the new types with correct signs (mirror ai_hold signs exactly).
6. **Migration** — in-flight pending intros at deploy time have NO hold (old model). Settle rule: accept of a pre-HOLD intro falls back to direct charge (legacy branch, flagged txn type `intro_fee_legacy`); decline needs no action. Branch keyed on `created_at < deploy_ts` or absence of a hold row (prefer: absence of hold row — self-describing).
7. **smoke_test.py** — add: commit→accept = net −1 buyer; commit→decline = net 0; double-settle → 409; insufficient balance → 402 + no intro row.
8. **FEA (ms.js)** — request path must surface 402 (insufficient T at request) → route to top-up; balance UI refresh after request (hold visible immediately). DEMO_MODE: demo intro flow stays array-served (no BEA call) — both branches verified per CLAUDE.md rule.
9. **Scale-shape invariant #2** — every settle path wrapped in explicit transactions (already the AI-ledger pattern).

## Cost model impact
None — revenue timing identical to charge-on-accept (burn at accept); declines were never revenue.

## Rollback
Feature-flag the commit branch (`INTRO_HOLD_ENABLED`, env, default OFF) so cutover is a flag flip after smoke, and rollback is the same flag.

# AI Vendor Strategy — Decision Note
**11 July 2026 · David's decision · companion to AI_PROVIDER_DEPENDENCY_POSTURE_2026-06-19.md**

## Decision (David, 11 Jul 2026)
1. **Staying with Claude.** The harness (Cowork + skills + memory + standing instructions
   + this codebase's Claude-shaped workflow) is the value, not the model-of-the-moment.
   Swapping vendors chasing benchmark leads is explicitly rejected as shortsighted.
2. **Subscription: drop to Max $100/mo when Fable 5 leaves subscriptions (13 Jul 2026).**
   Day-to-day dev work runs on the included models (Opus 4.8 tier).
3. **Fable 5 via usage credits ($10/$50 per Mtok) reserved for the most important work only.**
   Long, unsupervised, correctness-critical batches — where reviews show Fable's edge
   (SWE-Bench Pro 80.3%, fewer silent failures). Anthropic states Fable returns to
   subscriptions when capacity allows; credits are a bridge, not the end state.
4. **Add ChatGPT ($20/mo) as SECOND vendor, two roles:**
   a. Backup app-issue debugger (outage/diversity play — see posture note: this buys
      vendor diversity, NOT jurisdiction diversity; both are US).
   b. **Independent roving auditor** for MarketSquare — to be built up to scratch as an
      app agent. Rationale: Claude wrote most of this codebase; Claude auditing Claude
      has correlated blind spots. A second-vendor auditor breaks that correlation.

## Roving auditor — definition (to build when key exists)
- **Mission:** periodic independent sweep of the repo: canon-vs-code drift, cost-ceiling
  compliance (AI_FUNCTION_COST_CEILINGS), security/auth sweep, dead-code and dependency
  rot, "does STATUS.md match reality" checks.
- **Access: READ-ONLY.** It files findings; it never edits code. Findings land in an
  AUDIT_INDEPENDENT_<date>.md report next to AUDIT_PROGRESS.md.
- **Runner:** GPT-5.6 (Terra tier likely sufficient; Sol for deep passes) via the
  existing seam or a standalone script using OPENAI_API_KEY.
- **Cadence:** monthly, or after any major deploy.

## On-disk state (verified 11 Jul 2026)
- `ai_provider.py` — seam LIVE, 105 lines: ADAPTERS={anthropic, openai}, AI_ACTIVE env
  switch, fail-soft. OpenAI adapter is REAL (message translation + chat/completions +
  token logging), not vapor.
- **Stale:** OpenAI task→model map still lists gpt-4o-mini/gpt-4o (2024-era). Update to
  current model strings AND run eval_golden_set.py before any production traffic.
- `failover/ai_backends.py`, `eval_golden_set.py`, `golden_set.py` — failover path exists.

## Blocked on (David only)
- OPENAI_API_KEY (platform.openai.com, ~$10-20 credit) — the single missing piece for
  both the auditor build and a tested second adapter. ChatGPT $20 sub is separate
  (covers interactive use + Codex; contributes nothing to API).

## Explicitly rejected
- Replacing Fable-tier work with GPT-5.6 Sol for assignment batches (silent-failure risk
  on long unsupervised runs costs more in David's verification time than tokens saved).
- Vendor swap as jurisdiction hedge (posture note stands: only open-weight self-hosted
  insulates).

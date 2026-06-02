# ROADMAP — AI Independence & Token Sovereignty
**Planning deliverable · v1.0 · 2 June 2026 · author: Architect agent (planning only — nothing built/changed)**

> **What this is.** A plan to drive the just-shipped 3-task maintenance loop (Sensor 03:30 /
> Fixer 04:00 / Orchestrator 05:00) and CityLauncher's Haiko engine toward **deterministic,
> zero-token server scripts wherever judgment doesn't genuinely pay**, reserving paid LLM calls
> for the few places where a model earns its cost. Aligns with David's sovereignty principle:
> self-hosted / zero-token first, an LLM only where judgment genuinely pays.
>
> **Scope guard.** PLANNING ONLY. No code, no deploy, no git, no edits to the scheduled tasks.
> The existing two gates (Regulatory, Financial), the daily report, and the loop's behaviour
> stay exactly as they are until a phase is explicitly approved and executed in a later session.
> Sources read: `ORCHESTRATION_POLICY.md`, the three task `SKILL.md` prompts,
> `CityLauncher/orchestration/haiko_agent.py` (+ `expansion_engine.py`, `kpi_worker.py`).

---

## 0 · The thesis in one line
Most of the loop is **mechanical** (run a linter, curl an endpoint, diff a JSON, parse a
markdown doc) and is being paid for as **full Claude sessions**. Strip the mechanical work down
to plain cron scripts at **zero token**; keep an LLM **only** for: (a) writing/repairing code
the Fixer ships, (b) genuinely ambiguous triage, (c) CityLauncher scrape-strategy wording. Net
effect: from **~3 Claude sessions/day + per-stall Haiku calls** down to **a few short Sonnet
checkpoints/week + zero routine token**, with the gates and the daily report fully intact.

---

## 1 · The clean split — DETERMINISTIC (zero-token cron) vs GENUINELY-NEEDS-AN-LLM

### 1A · Move to plain server cron scripts (zero token) — the prime candidates

| Loop work | Today | Why it is deterministic | Target |
|---|---|---|---|
| **Sensor — smoke** (`smoke_test.py` 30/30 ≈ 40 curl/`node --check` assertions vs live server) | runs *inside* a Claude session | pass/fail is mechanical; no judgment | `cron` shell → writes `findings.json` |
| **Sensor — health/spend** (`/health`, `/dashboard/summary`, `/dashboard/cost`; flag spend within 20% of ceiling, health!=ok, 5xx) | Claude session | pure threshold comparisons | `cron` Python (stdlib `urllib`+`json`) |
| **Sensor — Monday static scan** (ruff F/E9/B, vulture, pylint cyclic-import, eslint 9) + delta vs `SCAN_REPORT.json` | Claude session | linters are deterministic; delta is set-diff | `cron` (Monday guard `date +%u`==1) |
| **FEA integrity** (`fea_integrity_check.py` vs `fea_baseline.json`) | already a script, invoked in-session | byte/version fingerprint compare | fold into the Sensor cron |
| **Orchestrator — state plumbing** (read `findings`/`results`, fold last Fixer result, write `queue/staged/report.json`, `scp`, append `log.md`, refresh live page) | Claude session | file IO + JSON shuffling + ordering | `cron` Python |
| **Orchestrator — gate *path* pre-catch** (POLICY §6.2: stage by **file path** if diff touches `payments.py` / EULA-Terms-Privacy / Tuppence-ledger / KYC-SA-ID) | Claude judgment | a hardcoded path/keyword allow-list — **already specified as mechanical in policy** | deterministic rule in the cron |
| **Bootstrap & queue ordering** (seed from `AUDIT_PROGRESS.md` open items, honour RUNNER PRIORITY OVERRIDE, move `approved:true` to front) | Claude session | parse + sort by sev/priority | `cron` Python |
| **Daily report assembly** (compose `report.json` from the state files into the fixed shape) | Claude session | template fill from structured inputs | `cron` Python → same JSON the live page already reads |

**CityLauncher / Haiko:**

| Work | Today | Reality | Target |
|---|---|---|---|
| **`make_decision()`** — continue / expand / pause / complete (every 15 min × city×category) | already **pure-Python thresholds** | no LLM in the hot path | keep as-is (already zero-token) |
| **Keyword expansion wording** (`haiko_expand()` → Claude **Haiku**, only on `expand_criteria`) | Haiku call (~$0.001) | a complete `CATEGORY_EXPANSIONS` table **already exists** in `expansion_engine.py` as the fallback | **default to the deterministic table; Haiku retired** (see §2) |

> **Key finding:** the Sensor's smoke/scan/health is **entirely** mechanical — it is the prime
> zero-token candidate and carries no judgment whatsoever. The Orchestrator is *mostly*
> mechanical too: only the FIX/FILE/IGNORE call on a genuinely *ambiguous* item needs a model;
> everything else (path pre-catch, ordering, report assembly, plumbing) is deterministic and is
> *already written as mechanical rules in `ORCHESTRATION_POLICY.md`*. And Haiko's decision hot
> path is **already** pure Python — only the cosmetic keyword phrasing ever calls a model.

### 1B · Genuinely needs an LLM (keep paid, but make it sparse)

These three are where judgment *actually* pays and a deterministic rule would be brittle or wrong:

1. **Fixer code edits.** Writing a correct, surgical, in-place patch to `bea_main.py` / `ms.js`
   and reasoning about whether it is safe is real generative judgment. **Keep on a model.** The
   verify-or-revert backstop (`ast.parse`/`node --check` + smoke 30/30) and the two gates already
   bound the blast radius. *This is the last thing to ever de-LLM, and likely never fully.*
2. **Ambiguous triage** — only the residue. When an item can't be confidently classified as
   FIX vs FILE vs IGNORE, or a gate classification is genuinely unclear (POLICY §6.1
   default-to-stage), a model adds value. The bulk of triage (clear FIX, clear FILE-to-design,
   re-confirm known false positive) is rule-able and moves to §1A.
3. **CityLauncher scrape *strategy*** — the non-mechanical "what's a smart *new* keyword for this
   category in this market" question. Today this is Haiku; the recommendation (§2) is to **serve
   the deterministic table by default and call a model only on table-miss**, not every expansion.

**Litmus test for any future item:** *"If I wrote the rule out in full, would it be correct
≥95% of the time and safe on the other 5%?"* Yes → deterministic cron. No → LLM, and pick the
cheapest tier in §2.

---

## 2 · Model-tiering policy (crisp — adopt as policy)

> **Default is deterministic Python. A model is the exception, justified per call.**

| Tier | Use it for | Cadence | Notes |
|---|---|---|---|
| **Deterministic Python / shell** | **the default.** All sensing, scanning, health, plumbing, ordering, report assembly, gate *path* pre-catch, Haiko decision tree, keyword table lookups | every run | zero token; runs on the Hetzner box under `cron` |
| **Opus** | one-off **design & architecture** — this roadmap, the modularization plan, a gate-policy redesign | rare, attended, human-in-the-loop | never in the daily loop |
| **Sonnet** | **sparse, checkpoint-only judgment** — the Fixer's actual code edit; the ambiguous-triage residue; a weekly review checkpoint | only when a deterministic gate has *already flagged* that judgment is required | replaces "a Claude session runs the whole job"; the session is invoked *by* the cron, not *as* the job |
| **Haiku** | — | — | **RETIRED.** Its one job (CityLauncher keyword phrasing) is served by the existing `CATEGORY_EXPANSIONS` table; a model is consulted only on a true table-miss, and that consult is Sonnet-grade judgment, not a routine Haiku tap. No standing Haiku dependency remains. |

**Operating rule to carry into every session:** *deterministic by default; escalate to Sonnet
only at a checkpoint a script couldn't decide; Opus only for attended design; Haiku not used.*

---

## 3 · Phased migration (keeps the two gates + daily report intact)

Each phase is independently shippable and reversible; **the gates, `staged.json`, the approval
flow, and `report.json`/the live page never change shape** — only *who* writes them flips from a
Claude session to a cron script. The loop we just shipped keeps running throughout.

### Phase 0 — Instrument (zero behaviour change)
Add a one-line token/cost stamp to `log.md` per run so before/after is measured, not guessed.
No logic change. *Exit:* one week of baseline numbers captured.

### Phase 1 — Sensor → cron (biggest, safest win)
Wrap the **existing** `smoke_test.py`, the health/spend curls, the FEA integrity check, and the
Monday linters in one `sensor.sh`/`sensor.py` under server `cron` at 03:30. It writes the
**same** `findings.json` to the **same** path. Retire the Sensor scheduled task only after a
week of side-by-side parity (cron `findings.json` == what the Claude Sensor would have written).
- **Risk:** low — read-only, no deploy, output schema unchanged.
- **Saves:** 1 of 3 daily Claude sessions immediately.
- *Exit:* 7 days of identical `findings.json` from cron; old Sensor task paused (not deleted).

### Phase 2 — Orchestrator plumbing → cron; judgment → Sonnet checkpoint
Split the Orchestrator in two:
- **Deterministic core (cron, 05:00):** fold last Fixer result, run the **gate path pre-catch
  (§6.2)**, seed/order the queue, honour `approved:true`, assemble `report.json`/`staged.json`
  in the exact current shape, `scp`, refresh the live page, append `log.md`. This is ~90% of the
  job and is pure file/JSON work.
- **Sonnet checkpoint (invoked by the cron *only* when needed):** hand the model **just** the
  items the deterministic pass tagged `ambiguous` (couldn't confidently FIX/FILE/IGNORE, or
  couldn't confidently clear both gates). Model returns a verdict per item; cron merges it. If
  there are zero ambiguous items that day, **no model is called at all.**
- **Gates preserved verbatim:** default-to-stage on uncertainty still holds — if the Sonnet
  checkpoint is itself unsure, the item stages. Path pre-catch runs *before* any model sees
  intent, exactly as today.
- **Risk:** medium — this is the brain; mitigated by keeping output schema identical and running
  parallel for two weeks (cron+checkpoint vs the old Orchestrator session) before cutover.
- *Exit:* 14 days parity on `queue/staged/report.json`; ambiguous-rate measured (expect most days = 0 calls).

### Phase 3 — Retire Haiku in CityLauncher
Flip `haiko_expand()` to **serve `CATEGORY_EXPANSIONS` first** (it is already the fallback path),
and only escalate to a model on a genuine table-miss. Decision hot path is untouched (already
pure Python). No standing Haiku dependency remains; `ANTHROPIC_API_KEY` becomes optional for
CityLauncher.
- **Risk:** very low — the deterministic table already exists and is already exercised as the
  fallback; this just promotes it to primary.
- *Exit:* one wave completed end-to-end with zero Haiku calls; expansion quality eyeballed OK.

### Phase 4 — Fixer stays LLM, but invoked, not standing
Leave the Fixer's code-editing on Sonnet (it's the genuine-judgment core). Optional later
optimisation: let the Phase-1 cron Sensor decide whether the queue has an actionable auto-ship
item *before* spinning a Fixer session at all — on an empty/all-staged queue, **no Fixer session
is started** (today it spins up just to no-op). Pure scheduling saving, no behaviour change.
- *Exit:* Fixer only wakes on days with actionable work.

**Throughout:** old scheduled tasks are *paused*, not deleted, until each phase has proven parity
— instant rollback is "un-pause the task, disable the cron." Nothing is irreversible.

---

## 4 · Token / cost — before vs after (order-of-magnitude)

**Before (today):**
- 3 Claude sessions/day (Sensor + Fixer + Orchestrator), every day. Sensor and Orchestrator are
  each a full session doing mostly mechanical work; Fixer is a full session doing one fix.
- + Haiko Haiku calls on every `expand_criteria` (~$0.001 each; bounded but standing).
- ⇒ ~**90 maintenance Claude sessions/month** + a trickle of Haiku.

**After (Phases 1–4):**
- **Sensor:** 0 sessions (cron, zero token).
- **Orchestrator:** 0 sessions on a clean day; **1 short Sonnet checkpoint only when ambiguous
  items exist** (expected a few days/week, small token each).
- **Fixer:** unchanged in nature (Sonnet, one fix), but only wakes on days with actionable work.
- **Haiku:** retired → ~0.

**Order-of-magnitude:** routine maintenance token drops from **3 full sessions/day** to roughly
**a handful of short Sonnet checkpoints/week + the Fixer only on workdays** — call it a **~70–90%
cut in maintenance token**, and the *standing* zero-work cost (idle Sensor/Orchestrator sessions,
Haiku trickle) goes to **zero**. Exact figures land from the Phase-0 instrumentation; this is the
shape, not a quote. **No change to the platform's user-facing AI spend or the cost ceiling** —
this is purely the maintenance/ops loop.

---

## 5 · Feasibility — a small LOCAL model on the Hetzner box (later option, not now)

**Box:** Hetzner CPX32 — **4 vCPU, 8 GB RAM, no GPU**, already running BEA (FastAPI+SQLite+Redis)
+ CityLauncher.

**Verdict: keep as a *later* option; 8 GB is tight and the box is already working.**
- **CPU-only inference** (llama.cpp / Ollama) of a small quantised model (e.g. a 3B at Q4, ~2–3 GB
  RAM) is *technically* runnable for the two low-stakes jobs that remain LLM-ish — **ambiguous-
  triage residue** and **keyword expansion** — but **not** for the Fixer's code edits (too weak;
  correctness there is load-bearing → stays Sonnet).
- **The squeeze:** 8 GB already hosts the BEA + Redis + CityLauncher. A 3B Q4 leaves little
  headroom and inference would contend with live request handling. Running it at **03:30–05:00**
  (the maintenance window, off-peak) mitigates contention but the RAM ceiling is real.
- **Sizing if pursued:** bump to a box with **≥16 GB RAM** (CPX42-class) before standing up a
  local model, or run it on a **separate small node** so it never competes with the live BEA —
  consistent with the scale-shape "no state on the box / N identical copies" invariant. A GPU is
  unnecessary for 3B-class CPU inference at this volume but would help if scope grows.
- **Why it's *later*, not now:** Phases 1–3 already take routine token to near-zero with
  **deterministic Python**, which is more sovereign (no model at all), more reliable, and free.
  A local model only earns its keep if the *ambiguous-triage* volume turns out high enough to be
  worth a standing service — measure that in Phase 2 first. If ambiguous days are rare (likely),
  a local model is **not worth the RAM**; if they're frequent, size up a node and host a small
  triage model there as a token-free judgment tier *below* Sonnet.

**Recommendation:** do **not** provision a local model in Phases 1–4. Re-evaluate after Phase 2
with real ambiguous-item counts; if it's worth it, do it on a ≥16 GB or separate node, never by
squeezing the live 8 GB box.

---

## 6 · What explicitly does NOT change
- The two approval gates (Regulatory, Financial) — verbatim, including default-to-stage and the
  §6.2 path pre-catch (which *becomes* the deterministic rule, unchanged in effect).
- `staged.json`, the "approve `<id>`" flow, and the live page contract (`report.json` shape).
- The daily report — same content, same shape; only the writer flips Claude-session → cron.
- The Fixer's surgical-only, verify-or-revert, one-item-per-run, no-git-from-sandbox discipline.
- Anything the loop already refuses to touch (design/UX, `bea_main.py` structure, legal blockers).
- Platform user-facing AI spend and the cost ceiling.

---

## 7 · Open flags (best-guess made; confirm at execution time)
- **Cron host & scheduling:** plan assumes `cron` on the existing Hetzner box at the same
  03:30/04:00/05:00 SAST slots; confirm timezone (server may be UTC — adjust the cron expr).
- **Secrets in cron:** the cron scripts need the same `ADMIN_KEY`/SSH it has today; reuse the
  existing server `.env` + the sandbox-key pattern, no new secret store.
- **Parity window length:** 7 days (Sensor) / 14 days (Orchestrator) proposed; tune to comfort.
- **Ambiguous-item rate is the pivot** for both the Sonnet-checkpoint cost and the local-model
  decision — Phase 0/2 instrumentation must capture it explicitly.

*End ROADMAP_4_AI_INDEPENDENCE.md v1.0 — planning only; nothing built, deployed, or committed.*

# TrustSquare Orchestrated Maintenance — Operating Policy
**v1.1 · 10 June 2026 · David-approved** *(v1.1 adds §6.7 — one git push/day, Orchestrator-owned; v1.0 · 2 June 2026)*

The single source of truth for the background maintenance loop. The Sensor, Fixer, and
Orchestrator scheduled tasks each read this file at the start of every run. Change behaviour
here, not in the individual task prompts.

---

## 1 · Purpose & model
Three scheduled agents replace the previous six. The goal is **set-and-forget background hygiene**:
the boring entropy (lint, dead code, latent crashes, drift) clears itself; only decisions that
genuinely matter reach David. Design, UX, and architecture are owned by David + attended sessions —
**this loop never touches them** (see §7).

```
   SENSOR ──findings──▶  ORCHESTRATOR  ──report──▶  DAVID
   (sense)                (the brain)   ◀─approve──
                          │      ▲
                        queue  results
                          ▼      │
                         FIXER (acts)
```

## 2 · Daily cadence (local / SAST)
- **03:30 — Sensor** (read-only sense)
- **04:00 — Fixer** (works exactly one item from the queue)
- **05:00 — Orchestrator** (triage + write the daily report + set the next queue)

One full loop per day. Discovery→report-of-fix latency is ~26h by design; that is fine for hygiene.

## 3 · Components
**Sensor — read-only, never edits, never deploys.** Consolidates the three old read-only jobs into
one pass: smoke test vs the live server, health + security + spend check, and (Mondays only) the
deep static scan (ruff/vulture/pylint/eslint) with a delta vs last week. Writes `findings.json`.

**Fixer — the one hands-on worker.** Takes the single top item from `queue.json`, makes a surgical
in-place fix, verifies (`ast.parse` / `node --check` + smoke 30/30), then **auto-ships or stages**
per the gates in §5. Writes `results.json`. Never structural; one item per run.

**Orchestrator — decides and reports, never edits code.** Reads `findings.json` + `results.json`,
triages every open item into FIX / FILE / IGNORE (§4), classifies each FIX against the two gates,
writes the daily brief to `report.json`, maintains `staged.json`, and sets `queue.json` for the next
Fixer run. Refreshes the live page data and emits the one daily report.

## 4 · Triage verbs
- **FIX** — an actionable code change the Fixer can make surgically and verify.
  - *auto-ship* — verified (smoke 30/30) **and** not gated → Fixer deploys it unattended.
  - *stage* — verified but hits a gate (§5) → waits for David's approval.
- **FILE** — real, but needs a human / ops / legal / product decision, or belongs to an active
  manual track (design, modularization). Logged to `AUDIT_PROGRESS.md` / `BACKLOG.md`, not actioned.
- **IGNORE** — confirmed false positive. Recorded with a reason so it is not re-raised next scan.

## 5 · The two approval gates (David-approved · 2 Jun 2026)
**Default = auto-ship every verified fix, security fixes included.** EXACTLY two categories always
**stage** for David's approval — the places where a mistake is irreversible:

### Gate 1 — Regulatory risk
Stages if the change touches any of:
- EULA / Terms / Privacy Policy / consent copy, or the EULA version, or the company reg number
- Anything tagged POPIA, FSCA, NCC, CPA, Banks Act, or "direct marketer"
- The **non-refundable / Tuppence validity / expiry** logic or wording
- KYC / SA-ID / identity-document handling, data retention, or the **seller-anonymity reveal** path

> Regulatory *completeness* (POPIA retention specifics, magic-link consent timing, etc.) is deferred
> to the attorneys' legal opinion. Until then this gate is the catch-all: when in doubt, it stages.

### Gate 2 — Financial-release risk
Stages if the change touches any of:
- `payments.py`, Paystack keys/webhooks, or any payment capture / verify / checkout endpoint
- The **Tuppence ledger** — any credit, debit, balance, top-up, or the cost-ceiling / billing logic
- Subscription / tier / slot **pricing** or plan activation
- Any refund / payout / reversal / release-of-funds path, and the `/dev/credit` grant endpoint

**Boundary example:** a fix to the Tuppence balance *display* (a UI repaint, e.g. JS-1) auto-ships;
only code that actually **credits or debits** balance hits Gate 2.

**Security-class fixes** (auth, headers, secret handling) that are neither gate **auto-ship** —
David-approved, to avoid impeding progress with extra holds. Example: adding auth to the
`ADMIN_KEY`-guarded endpoints.

## 6 · Backstops (always on, every run — independent of tier)
1. **Default-to-stage on uncertainty.** Auto-ship requires *positive confidence* the change is
   neither gate. If the Orchestrator cannot confidently classify it as non-regulatory **and**
   non-financial → it stages. Silence is not a pass.
2. **Path pre-catch.** ANY diff touching `payments.py`, the EULA/Terms/Privacy copy, the
   Tuppence-ledger code, or the KYC/SA-ID code is staged **by file path**, before intent is even
   read — the backstop against a missed keyword.
3. **Verify-or-revert.** `ast.parse` (Python) / `node --check` (JS) clean + `smoke_test.py` 30/30
   before any deploy. On any failure: revert, stage the item with the error, never deploy a red smoke.
4. **Never structural.** No restructuring `bea_main.py` — module extraction is the attended
   modularization track. A fix that would need restructuring is **FILED**, not attempted.
5. **One item per run. No git from the sandbox** (David commits from PowerShell). Deploy only via the
   standard `scp` + `systemctl restart marketsquare` + Cloudflare purge.
6. **Codex is law.** If a business-logic gap appears, FILE it; never invent product rules.
7. **One git push per day — the Orchestrator owns it (David-approved · 10 June 2026).** The loop hands David exactly ONE commit/push block per day, in the Orchestrator's daily brief. The Orchestrator runs last (05:00, after the 04:00 Fixer), so its `git add -A` sweep captures the Fixer's shipped change, any deploy/FEA drift, and the doc write-backs in a single commit. **The Fixer and Sensor NEVER surface a push** — the Fixer still does its normal doc write-back + scp, then records "N files pending → deferred to the Orchestrator sweep" and stops. *Rationale:* both agents act on the same working tree and git commits the tree (not per-agent diffs), so a second push always finds "nothing to commit." *Backstop:* if the Orchestrator misses a day, pending changes sit safely uncommitted and the next sweep catches them (`git add -A` is comprehensive by design). Attended (non-loop) sessions keep doing their own session-end sweep. Before surfacing, the Orchestrator confirms no secret is staged (`ssh_hetzner_key` / any `.env` stays gitignored).

## 7 · What this loop never touches (owned by David + attended sessions)
- Design / UX / accessibility items → **FILE** to the design track.
- `bea_main.py` structure → **FILE** to the modularization track (M1→M9 in `MODULARIZATION_PLAN.md`).
- Legal / ops launch blockers (EULA counsel, Paystack live, support mailbox, etc.) → **FILE**.

### 7.1 · Change-Control mode (big cross-cutting changes — the loop never auto-runs these)
A **large change that ripples across many artifacts** (a Codex rule, pricing/tier model, IP/whitepaper
lineage, a business-process redefinition) is governed by **`CHANGE_CONTROL_PROTOCOL.md` (CCP)**, not this
nightly loop. The CCP **reuses the three roles** — Sensor (mechanical grep of the change's *term map* across
the whole tree, zero-token), Fixer (surgical edits), Orchestrator (verify-to-zero + report) — but runs them
**ATTENDED and fully gated**: every canon/pricing/IP edit stages for David (Gates §5 + the §12 never-automated
list). The nightly loop's job is to **FILE** any drift it senses that belongs to an open CCP change
(`CHANGE_REGISTER.md`), never to action it. The CCP's "verified" bar = Sensor grep returns **zero** surviving
old tokens **and** the traceability matrix is 100% **and** smoke is green.

## 8 · Approval flow (v1)
Staged items appear on the live page and in the daily report under **"Awaiting your approval."**
To approve: tell Claude **"approve `<id>`"** in any session. The item is marked `approved:true` and
moved to the front of the queue; the next Fixer run ships it (still smoke-gated). One-click approval
from the page is a later enhancement.

## 9 · State files — server is source of truth · `/var/www/marketsquare/orchestrator/`
| File | Writer | Reader | Holds |
|---|---|---|---|
| `findings.json` | Sensor | Orchestrator | smoke result, health/spend, scan deltas |
| `results.json` | Fixer | Orchestrator | last run: shipped / staged / failed + detail |
| `queue.json` | Orchestrator | Fixer | prioritised items `{id, sev, action, verdict, gate, approved}` |
| `staged.json` | Orchestrator | live page | items awaiting David (Regulatory / Financial) |
| `report.json` | Orchestrator | live page | the daily brief |
| `log.md` | all three | — | append-only audit trail of the loop |

**Live page:** `trustsquare.co/orchestrator.html` (code-gated, same as `/support`). Reads
`/orchestrator/report.json` + the existing `/dashboard/summary` + `/dashboard/cost` (all same-origin).

## 10 · Bootstrap
On the first Orchestrator run, if `queue.json` is absent it is built from the open items in
`AUDIT_PROGRESS.md`. Until a queue exists, the Fixer no-ops cleanly. The loop is self-seeding.

---

## 11 · Model-tiering policy (RM-4 · adopted 2 Jun 2026)
**Default is deterministic Python/shell. A model is the exception, justified per call.** Imported from `ROADMAP_4_AI_INDEPENDENCE.md` §2 and adopted as binding policy for this loop and for CityLauncher.

| Tier | Use it for | Cadence |
|---|---|---|
| **Deterministic Python / shell** | the default — all sensing, scanning, health, plumbing, queue ordering, report assembly, the §6.2 gate **path** pre-catch, Haiko's decision tree, keyword-table lookups | every run · zero token · runs on the box under `cron` |
| **Opus** | one-off attended design & architecture (roadmaps, the modularization plan, a gate-policy redesign) | rare, human-in-the-loop · never in the daily loop |
| **Sonnet** | sparse, checkpoint-only judgment — the Fixer's actual code edit; the ambiguous-triage residue; a weekly review checkpoint | only when a deterministic gate has **already** flagged that judgment is required |
| **Haiku** | — | **RETIRED.** Its one job (CityLauncher keyword phrasing) is served by the existing `CATEGORY_EXPANSIONS` table; a model is consulted only on a true table-miss, and that consult is Sonnet-grade. No standing Haiku dependency. |

**Operating rule (carry into every session):** *deterministic by default; escalate to Sonnet only at a checkpoint a script couldn't decide; Opus only for attended design; Haiku not used.* **Litmus test:** "If I wrote the rule out in full, would it be correct ≥95% of the time and safe on the other 5%?" Yes → deterministic cron; No → smallest model tier above.

**Migration (phased per ROADMAP_4 §3, gates intact):** Sensor→cron first (Phase 1 — runs in **shadow** writing `findings.cron.json` until 7-day parity, then flips to `findings.json` and the Claude Sensor task is paused), then Orchestrator plumbing→cron with a Sonnet checkpoint **only** on ambiguous items (Phase 2), then retire Haiku in CityLauncher (Phase 3). The two gates, `staged.json`, the approval flow, and `report.json` / the live page never change shape — only *who writes them* flips from a Claude session to a cron script.


---

## 12 · Escalation Policy — when the loop wakes David (added 6 Jun 2026 · from AUTONOMY_LADDER.docx §4)
Autonomy is trustworthy only if its silence is informative: **no call means nothing needs you.**

| Severity | Triggers (any one) | Action | Latency |
|---|---|---|---|
| **SEV-1** | Ledger mismatch / any Tuppence balance anomaly · live payment-provider failure · security-breach indicator · data loss · site down >15 min unrecovered · contact from a regulator or lawyer | **Safe-hold the affected path, then WAKE DAVID — any hour** (channel: TBD, see AL-8) | Immediate |
| **SEV-2** | Capacity watcher amber · a shipped fix rolled back · scraper source newly blocked · day-over-day cost spike >25% · repeated auth failures | Flag in daily brief + same-day message | Same day |
| **SEV-3** | Routine fixes shipped · polish · doc drift · dependency notices | Daily brief; weekly review queue | Weekly |

**Safe-hold default.** If triage confidence is below threshold, or a change would touch any gated class, the loop holds safe and notifies — it never guess-ships. A held item is a success of this policy, not a failure of the loop.

**Never automated — at any rung, by principle:** movement of money in any direction (refunds do not exist, by canon) · credentials, secrets, access permissions · legal filings & regulatory correspondence (CIPC, Paystack live, patents) · Codex amendments / WhitePaper lineage (supersede via Addendum, never edit) · pricing, tiers, Tuppence allocations.

This section is enforced in conjunction with the two-gate policy (§6) — it does not widen any auto-ship lane; it defines the alarm wire that lets the lanes widen safely as the Autonomy Ladder climbs (BACKLOG → 🪜 track).

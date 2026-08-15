# AI LANE GUIDANCE — David's ruling, 14 August 2026

**Canon.** Supersedes the implicit "Anthropic everywhere" arrangement. Machine-readable form:
`AI_BASELINE.json` v2.0. Asserted by `scripts/ai_baseline_check.py`.

---

## The ruling, in two parts

### 1 — Lane roles

| Lane | Role | Why |
|---|---|---|
| **openai** — `gpt-5.6-luna` / `gpt-5.6-terra` | **BASE usage model** | David's selection. On the register it is both cheaper **and** higher-scoring on the tiers that carry the volume: AA **51.24** vs Haiku's **29.58**, at **77–79% less**. Luna also outscores `claude-sonnet-4-6` (47.21) at roughly a thirteenth of Sonnet's price. Golden set 8/8 on production prompts, 1 Aug 2026. |
| **anthropic** — `claude-haiku-4-5` / `claude-sonnet-4-6` | **AUTO-FAILOVER** | First lane on a T1/T2 dropout. Months live, prompts tuned, production gate. Dearer than base **by design** — continuity is worth a cost spike. 4.4–4.7× base on haiku/vision/triage, 1.35× on sonnet. |
| **scaleway** — `mistral-medium-3.5-128b` | **SAFETY NET** — last resort, cost-exempt, alert-on-use | Bans (T3) and EU jurisdiction only. ONE-MODEL STANDBY. 7.6–8.1× base, which is **fine for a last resort** — it is reached when the alternative is being down or banned, where price is not the question. But reaching it must **alert** and be **time-boxed**. |

**Failover order: `openai → anthropic → scaleway`.**

### 2 — Design tool vs usage model are different concerns

> **Anthropic is the main DESIGN tool and the guidance layer.** Development, review,
> architecture, this session, the maintenance agent's reasoning — the work of *building* the app.
>
> **OpenAI is the base USAGE model.** The runtime inside trustsquare.co — the work the app
> *does*, at volume, for users.

These must not be conflated. The tool that helps build the app is chosen for judgement quality on
open-ended problems and is used at low volume by one person. The model that runs inside the app is
chosen for cost and consistency at high volume across thousands of calls. Different jobs, different
selection criteria, and there is no reason the same vendor should win both.

---

## Two tolerances, deliberately different

Putting the **cheapest** lane at the base has a consequence worth stating plainly: **every failover
is now a cost increase by definition.** That is accepted — it is what continuity costs. But it
changes what the guard has to do.

- **AUTO-FAILOVER (anthropic)** — must stay within the **continuity tolerance, 6.0× base**. Chosen
  for continuity, not price, but the cost of continuity is bounded.
- **LAST RESORT (scaleway)** — **cost-exempt**. Gating it on price would mean choosing to be down.
  Instead: alert on use, and time-box.
- **Procurement** (changing the base lane at all) keeps the price card's own bar: **≥30% sustained
  saving at equal-or-better capability**, and it is **David's decision**, never automatic.

### Alert rules

| | When | Action |
|---|---|---|
| **AL-1** | The serving lane is not the base lane for more than 60 minutes | Alert R2 — a sustained failover is a re-pricing event |
| **AL-2** | The serving lane is the safety net at all | Alert R2 immediately and time-box — ~8× base on three tiers |
| **AL-3** | A pin (`ai_active_override`) is set | Record actor and reason — RG-0019 deliberately does not trip on a pin, so nothing else will notice |

---

## THE FLIP IS NOT DONE — six preconditions

The decision is recorded and the baseline, dashboard and checks now reflect it. **The live lane has
not moved and must not until all six are met.** Reporting otherwise would be dishonest.

| | Precondition | Owner | Status |
|---|---|---|---|
| **P1** | `OPENAI_API_KEY` provisioned in `/etc/environment` on the server | **R4 — a secret, so David** | NOT DONE |
| **P2** | Golden set re-run on the **live seam with the server key**. RG-0016 requires it; GS-OAI-V1 ran on a sandbox key | R2 | NOT DONE |
| **P3** | `openai` added to `GOLDEN_PASS` in `ai_scoreboard.py`, once P2 passes | R2 | NOT DONE |
| **P4** | Shadow period at low traffic before the standing lane moves | R2 | NOT DONE |
| **P5** | `ai_price_card.json` `active_lane` → `openai` **the same working day** as the live flip. Earlier trips RG-0019 RED; later also trips it | R2 | NOT DONE |
| **P6** | **`_MODEL_PRICE` keyed by MODEL not tier, and `_log_ai_spend` recording the SERVING lane** | R2 | NOT DONE |

### P6 is now the critical one, and it was not before

With Anthropic as base, mis-attributing a failover was a reporting nuisance. With OpenAI as base it
is a **hole in the control**: `_log_ai_spend` records the *intended* lane and `_token_cost` is keyed
on tier rather than model, so **a sustained failover to Anthropic would quadruple haiku-tier cost and
be invisible in the spend log.** The shadow period in P4 is not even measurable until P6 lands.

**Do P6 before P4.** That is a change of order from the obvious sequence, and it is the point of
running the verification before declaring anything done.

---

## Flip sequence

1. **P1** — provision the key (David)
2. **P6** — fix spend attribution *first*, so everything after it is measurable
3. **P2** — golden run on the live seam
4. **P3** — open the gate in `GOLDEN_PASS`
5. **P4** — shadow at low traffic, read the real numbers
6. Flip `launch_switches.ai_active` → `openai` via `POST /admin/flags`
7. **P5** — update the card the same day
8. Re-run `ai_baseline_check.py` and `ai_challenger_board.py` — both should come back clean

---

## Manual override is unchanged and always available

The Ops Dashboard AI Providers card keeps every manual control, and gains role labelling:

- **Make standing** — changes the standing lane (`POST /admin/flags {ai_active}`)
- **Pin 24h** — time-decaying override that outranks the standing lane, then expires
- **Unpin now** — drops the pin immediately
- **Test** — live call against a chosen lane without changing routing
- Rows are ordered **BASE → FAILOVER → SAFETY NET** and each carries its role chip, its cost
  multiple against base, and one line on why it holds that role.
- A banner states plainly whether the serving lane is the one the baseline designates — amber while
  the flip is pending, red if serving off-base, green when correct.

**Still missing, and it is the one gap the dashboard cannot close by itself:** `POST /admin/flags`
writes **no log line and no audit row**. A lane change remains undetectable after the fact. One
`_log.warning` closes the detection gap; an `admin_audit` table closes the record gap. Until then the
override is available but not accountable — which is the opposite of the ruling's intent.

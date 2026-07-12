# AI Sovereignty — Physical Layer Decision (Air-gapped Karoo standby + trusted validator)
**9 July 2026 · MarketSquare / TrustSquare · companion to `ROADMAP_4_AI_INDEPENDENCE.md` and `AI_PROVIDER_DEPENDENCY_POSTURE_2026-06-19.md`**
**Prompted by:** David — "use open-source Llama-type LLMs (and better), adopting newer ones as they are RELEASED and proven independent (not trojan horses), all residing in an off-grid air-gapped Karoo farm... always used as the trusted validator, independently and comparatively whilst using the frontier models." Recorded so the reasoning is not re-litigated.

## Decision (confirmed, not new-in-spirit)
The sovereign spine of MarketSquare's AI is **open-weight models we hold and run ourselves**, physically on an **air-gapped, off-grid cluster at the Karoo farm**. Its **primary standing role is the trusted validator**: it runs **continuously alongside** the frontier models, independently and comparatively checking their output — and it is **also** the fallback that can carry the core service the moment a gate closes. Claude mid-tier (Haiku/Sonnet/Opus) stays the everyday **generator** while available; the Karoo cluster is the everyday **referee**.

## Why it holds (and is more validated now than in June)
- No provider sits in the loop to receive a BIS-style order; weights already downloaded **cannot be un-shipped** and can move jurisdictions.
- It is symmetric-proof: it survives the **US** gate (Fable/Mythos, June), the **China** gate (Qwen/DeepSeek/GLM curbs, Reuters 7 Jul), and the emerging **EU** export-control drafts — none of which can reach a box with no network.
- Off-grid also answers the **SA grid** risk (load-shedding) that a cloud-only posture never fully escaped.

## How to read the plan
1. **Rolling adoption, not a one-time pick.** As newer/better open weights ship (Llama's successors, Mistral, or whatever leapfrogs them), each is **vetted, hashed, and rolled in behind the gap** — you ride the open-weight frontier upward instead of freezing on one model. Every downloaded copy you keep is yours permanently (pin each to a **signed hash**); the only thing you rent is the **GPU hardware**.
2. **Independence is enforced by the gap, not proven by the vetting.** You cannot *prove* weights are clean — sleeper-agent research shows triggerable hidden behaviour can survive evaluation. But a backdoored model with **no network cannot exfiltrate or phone home**, so the air-gap neutralises the trojan-horse threat by construction. Corollary: even a Chinese base (Qwen/DeepSeek/GLM) is safe to run behind the gap.
3. **Capability from the frontier, trust from the sovereign.** These are different jobs. The frontier supplies raw capability; the Karoo model supplies an **owned, un-switch-off-able reference**. A validator does not need to be the smartest model — for catching divergence, **independence (different lineage, different failure modes) is worth more than the last few points of capability**, and *always-on* beats a cold standby that quietly rots until you need it.

## Why a slight capability lag is acceptable *for a validator* (and where it isn't)
- **Fine for:** divergence detection (frontier answer drifts from the sovereign's), consistency checks, retrieval-grounded fact-checks against a corpus we hold, guardrail/policy-adherence checks, and drift/anomaly detection over time. A slightly-behind independent model does all of these well.
- **Not fine for:** refereeing a dispute that genuinely needs **frontier-level reasoning** — a weaker validator can't reliably judge that. Scope the validator to the checks above; on a genuine capability-gap disagreement, **flag-for-human or cross-check with a second frontier**, don't let the weaker model overrule.

## Bonus: the validator is also the trip-wire sensor
Running the sovereign model comparatively is exactly how you'd **automatically detect** a returned/monitored frontier model starting to behave oddly — covert throttling, injected content, quality drift. A persistent, unexplained rise in frontier-vs-sovereign **divergence** is a machine-readable early warning that feeds the same AI-Watch trip-wires (restrictions reaching Sonnet/Opus/Haiku; region throttling; gov-routed logging). The daily monitor watches the *world*; the validator watches the *models themselves*.

## Validation as BIT — two types on the sovereign referee (per `BIT_ARCHITECTURE.md`)
The validator runs the **two BIT types we already defined**, now aimed at the *model itself* rather than the app. This is a second axis on top of the existing cadence tiers (deploy-gate / continuous / daily) — not *how often* a test runs, but *what kind* it is:

- **Simple BITs — mass, cheap, run wide.** Straight comparisons and contract-shaped assertions on individual outputs: consistency, retrieval-grounded fact match, format/guardrail adherence, frontier-vs-sovereign agreement on a given answer. PASS/FAIL, high volume, cheap — these "work straight up." They map to the existing functional + negative BITs and ride the deploy-gate + fast-cycle cadence.
- **Complex KPI BITs — few, longitudinal, expensive (the real point).** A small, budgeted set of behavioural KPIs tracked over rolling windows against a frozen baseline, watching for what no single output reveals:
  - **Drift** — slow slide in quality/behaviour vs the baseline golden-set (degradation or quiet repositioning).
  - **Intention shift** — the model beginning to optimise for something other than the user's stated goal (subtle steering of recommendations/answers).
  - **Focus forcing** — attention/output pushed toward a topic, vendor, or framing; caught as a salience/distribution skew vs the independent sovereign.
  - **False flags** — spurious alarms, or real signals suppressed; caught as divergence in what gets flagged/refused vs the sovereign.
  - **Trojan programming** — latent, trigger-activated behaviour; caught by canary trigger-probes and the sudden local behavioural discontinuities the differential check surfaces.

Why the sovereign is the right **engine** for the complex tier: these signals are only visible to an **independent, different-lineage** comparator — a same-family checker cannot see its own family's intention drift. And it honours the BIT budget (§0.5 of `BIT_ARCHITECTURE.md`): the complex KPIs stay a **small, sampled, slow-cadence** set so the watcher never degrades the watched, while the cheap simple BITs carry the mass. The air-gapped Karoo model is the purest expression of the BIT principle already in the architecture — *the watcher must be a separate, minimal, independent article that outlives the watched.*

## The dimensionality of intent — why manipulation only becomes visible in 3-KPI space
*(Reconstruction of David's earlier ChatGPT/Grok discussion — the original combinations are not in this repo; reconcile if the export is found.)*

The core insight: **a complex KPI BIT is not one metric, it is an interaction of metrics, and intentional manipulation only becomes separable at the third dimension.**

- **1 KPI over time** = a measurement. Drift in it conveys meaning, but a single axis is *spoofable and noise-confusable* — any one metric can be held in-band, and innocent drift looks the same.
- **2 KPIs viewed interactively** = the correlation between them carries far more than either alone. Coincidence is still available as an explanation, but the innocent space is shrinking.
- **3 KPIs** = the **Eureka**. The joint structure across three axes forms a *signature* that random drift does not produce. Only here does deliberate steering separate cleanly from noise — and **only here is a BIT trigger actually usable** (low enough false-positive to act on) against "intentional hypnosis programming" (deliberate, below-threshold conditioning of the user over time).

**Why three, precisely.** Stealth *is* staying in-band on every single metric — so each axis must remain individually innocent for the manipulation to be worth running. Two axes lit together can still be coincidence. The **third axis is what kills the innocent explanation**: three independent measurements co-moving toward one target frame is a structure an adversary cannot fake while keeping each axis plausibly benign. (Anti-spoof corollary: an adversary can hold N-1 dimensions in-band, so you always need the Nth; 3 is the empirical threshold where structured intent becomes linearly separable from drift-noise.)

**Candidate triples (starter set — each axis measured as frontier-vs-sovereign against a frozen baseline):**

| Triple | Axes (each individually innocent) | Fires when… (the 3-way signature) | Catches |
|---|---|---|---|
| **T1 · The Steer** | salience/entity skew × assertiveness-confidence × hedging/caveat collapse | all three rise **co-directed at the same target frame** | persuasion campaign / focus forcing |
| **T2 · The Trigger** | paraphrase-consistency break × divergence localization × stance/valence flip | all three cluster in **one narrow topic region** | trojan / backdoor activation |
| **T3 · The Gaslight** | flag/refusal asymmetry × frame repetition-anchoring × call-to-action pressure | suppression + repetition + push **toward one decision** | false flags / manufactured consensus |

**Construction rule for any future triple:** each axis must be *independently explainable as benign*; the trigger fires only on the **coherent co-movement of all three toward a single target**; the **sovereign (independent lineage) supplies the baseline** each axis is measured against — a same-family model cannot furnish an uncompromised reference. This is the complex-KPI end of the two-type split above; simple mass BITs stay 1-D PASS/FAIL.

## Accepted flaws (eyes open)
| Flaw | The honest tension | Mitigation |
|---|---|---|
| **Capability/cost premium** | Self-hosted open weights trail the frontier; the *best* open weights today are **Chinese** (Qwen/DeepSeek/GLM). Llama (Meta) is neutral-ish but trails and Meta controls the licence. | The validator role tolerates the lag by design; rolling adoption closes the gap over time; air-gap makes even a Chinese base safe to run. |
| **Running two models continuously** | Validator-always-on means paying for the sovereign inference on every (or sampled) call, not just at failover. | Validate a **sampled / high-stakes subset**, not 100% of calls; size the cluster for that load; deterministic checks first, model-validation only where judgment pays (per ROADMAP_4). |
| **Air-gap freezes freshness** | No auto model updates; a frozen model can't see current data. | The **sneakernet cadence IS the release pipeline** — proven-clean models carried in on a schedule; live data via a controlled, audited retrieval channel, never a live call. |
| **Hardware layer reachable by policy** | GPU import/export controls and remote-access rules can gate getting compute to the Karoo. | On-site owned hardware sidesteps remote-access; import path is an open question (below). |
| **Single-site fragility** | One farm = fire/theft/hardware-death/power SPOF. | Spares + second node, off-site encrypted weight backups, physical security, N+1 power/cooling. |
| **Ops burden** | 24/7 GPU cluster, solar+battery, cooling, skilled maintenance far from a city. | Size for validator + fallback load; script health/failover; cold-start runbook. |

## Operating shape (three modes)
1. **Normal:** frontier **generates**, Karoo **validates** (independent, comparative) on a sampled/high-stakes subset; divergence is logged and trend-watched.
2. **Suspicion:** validator divergence spikes, or an AI-Watch trip-wire fires → raise validation coverage, alert, treat the frontier as untrusted for affected flows.
3. **Gate closed:** frontier unavailable/blocked → Karoo **promotes to primary generator** (degraded but sovereign). The failover already exists in code (`failover/ai_backends.py`, `eval_golden_set.py`); the Karoo box is where it physically lives and stays warm.

## Open questions before any spend (decide these, don't re-discuss the spine)
1. Which neutral base to **start** on — **Llama vs Mistral** vs a gap-hosted **Qwen** — and the **cadence/criteria for adopting newer released models**?
2. GPU **sourcing/import path into SA** under current export controls — new vs second-hand, via whom?
3. **What fraction of calls to validate** (all / sampled / high-stakes only) and the **divergence threshold** that trips suspicion mode.
4. **Power/cooling budget** for validator + fallback load; **sneakernet cadence** and the audited live-data channel.
5. **Second-node / off-site backup** so the resilient site is itself resilient.

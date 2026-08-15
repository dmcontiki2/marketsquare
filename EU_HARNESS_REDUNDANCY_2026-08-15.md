# EU HARNESS REDUNDANCY — evaluation record, 15 Aug 2026

**Trigger:** "The Black Whale Is Coming for Claude Code — DeepSeek Harness" (Morgans Code,
15 Aug 2026) + DeepSeek's 13 Aug release of Harness v0.1 (MIT) and V4 Pro.
**Companion canon:** AI_VENDOR_STRATEGY_DECISION_2026-07-11.md (Add. 6 models-vs-endpoints
doctrine; Add. L390+ OpenAI standing ruling), eu_hosted_ladder_2026-08-07.html,
AI_SOVEREIGNTY_PHYSICAL_LAYER_DECISION_2026-07-09.md, AI_LANE_GUIDANCE.md.

---

## What actually changed on 13 Aug

Not the models. The **harness** — the agent layer that gives a model file access, terminal,
plans, subagents, MCP tools — went open-source under MIT, model-agnostic (OpenAI-compatible
endpoints), everything-is-a-plugin. 24.7k GitHub stars in hours.

Why this matters to US specifically: **the app already has jurisdiction-diverse redundancy
(3 lanes, breaker, seam). The PROJECT does not.** The design/build/maintain toolchain — Cowork,
Claude Code, the interactive sessions that built everything in this repo — is single-vendor
Anthropic. A T3 against Anthropic today leaves the app running on OpenAI and the *build
capability* dead. The maintenance agent's spine is seam-routed (vendor-free), but the
interactive design layer has no fallback at all. Until 13 Aug there was no credible open
harness to fall back TO. Now there is one — and its very existence also disciplines pricing
across the layer, which benefits us even if we never run it.

## The China line — already drawn, still correct

Add. 6 (31 Jul) is the governing doctrine and it survives this evaluation unchanged:
**no pure Chinese endpoints for ANY workload; Chinese-origin MODELS acceptable via Western/EU
hosts.** Applied here:

- **DeepSeek hosted API: OUT.** PRC data residency, terms permit training on API data by
  default, no SOC 2 (open_weight_ladder findings). Never wired, never keyed.
- **DeepSeek/Qwen WEIGHTS on EU infrastructure: IN**, per the same doctrine. The
  eu_hosted_ladder already priced them: Scaleway Paris (Qwen 3.5-397B + Qwen 3-Coder, $0.44
  per audit unit, −97% vs all-Anthropic, no retention), DeepSeek V4 Pro EU via Frankfurt
  (€0.90, zero-training, ISO+SOC 2, DPA). "The cheapest configurations are now the sovereign
  ones."
- **The Harness CODE: Chinese-authored, MIT-licensed.** Same class as any dependency:
  pin a commit, audit before adoption, fork if adopted seriously. It runs on OUR machine;
  the privacy boundary is the ENDPOINT it is configured to call (the video is explicit on
  this). Config rule if piloted: EU endpoints only, hosted-PRC endpoints refused at config.

## The honest capability caveat

The eu_hosted_ladder's own conclusion stands: **what is unsolved is capability, not price or
sovereignty.** GLM-5.2 scored 78.7 vs Fable 5's 95.0 on SWE-bench Verified — a 16-point gap.
DeepSeek V4's claimed 92%-of-Opus figures come from DeepSeek's own harness at max reasoning
(the benchmark footnote the Cloud Codes video called out), and V4 Pro's API price rose
~11x on release day. Cost-per-useful-result, not cost-per-token, is the test — our own
PR-1 (parallel run) and the golden set are exactly the right instruments, unchanged.

## Ruling requested from David (one decision)

**Adopt as a slip-month/post-launch workstream, not a pre-launch one:**

- **HARNESS-PILOT-1** (2-3 evenings, capped $20): run DeepSeek Harness pointed EXCLUSIVELY at
  an EU endpoint (Scaleway Paris Qwen 3-Coder first; Frankfurt DeepSeek V4 EU second) against
  a copy of the repo on three closed, already-solved maintenance faults from the register.
  Score cost-per-useful-result against the same faults' actual fix history. No live access,
  no secrets in the worktree (GATE-CREDS-1 pattern), read-only clone.
- **Success bar:** 2 of 3 faults fixed to ledger-green at <25% of the recorded cost.
  If met: the harness becomes the PROJECT's DR toolchain (documented, cold, tested
  quarterly) — not the daily driver.
- **Sequencing:** AFTER the close-the-floor work (secrets, gate posture, deploy debt,
  instrument truth). A fourth toolchain added to an open-action backlog is more surface,
  not more safety.

Why not "switch the daily driver": the project's velocity currently rides on harness
maturity (Anthropic's is the mature one — the video's own verdict), and the failure mode
that matters pre-launch is open actions, not vendor concentration. The pilot buys the
OPTION cheaply; the option is what redundancy is.

**Claude's bias disclosure, per standing rule:** this evaluation was written by the product
it evaluates an alternative to. The mitigations: every capability number above is from
David's own prior research or third-party sources, the recommendation is to PILOT the
competitor, and the success bar is mechanical.

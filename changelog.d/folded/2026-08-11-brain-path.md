## 2026-08-11 — BRAIN-PATH-1: the maintenance loop could never reach its brain (a two-line bug, not an environment problem)

- **The symptom David asked about:** two maintenance runs in one day where `maintenance_agent.py`
  routed *every* fault to PATH_B with `ai_provider unavailable — defaulting to the batched
  design lane`. Read as an environment gap ("no key where the loop runs"). It was not.
- **The actual fault:** `ai_provider.py` lives at the **repo root**; `maintenance_agent.py`
  lives in **`scripts/`**. Run the documented way — `python3 scripts/maintenance_agent.py` —
  `sys.path[0]` is `scripts/`, so `import ai_provider` raised `ModuleNotFoundError` on **every
  run since the agent was written, on every machine, with or without an API key.** The agent
  computed `REPO` correctly on line 40 and then never put it on `sys.path`.
- **Why it hid:** `classify()` did exactly what RG-0049 requires — degrade, never die — and
  returned PATH_B. The loop therefore *appeared* to triage a queue nightly while actually
  reporting its own import error once per fault, and exited 0. **This is the second
  green-looking no-op found in one day** (UA-EDGE-1 / RG-0053 was the first). The fail-safe is
  not the bug. The bug is that a fail-safe with a *vague message* hides a wiring fault
  indefinitely: one string, `"ai_provider unavailable"`, covered both "the module will not
  import" and "the module is fine but has no key" — two faults with completely different fixes.
- **The fix (`scripts/maintenance_agent.py`):**
  - `REPO` goes on `sys.path` — deliberately the `__file__` root, **not** the `--repo`
    rehearsal override, which chooses which repo to *patch* and never which brain to think with.
  - Both degradation paths now name the cause: *will not import* (with the exception type) vs
    *imported fine, no lane keyed* (listing the env vars checked) vs *call failed*.
  - `.secrets/ai_keys.env` — a local key slot, read the same way the maint key already is.
    `ai_provider.envkey()` falls back to `/var/www/marketsquare/.env`, which exists **only on
    the server**, so a loop on David's machine previously had no way to be keyed at all. Real
    environment variables always win over the file; `.secrets/` is gitignored.
- **Evidence (AIK-VERIFY-1):** the failing action reproduced clean. Before, all 7 faults read
  `ai_provider unavailable`. After, the same run reads `no AI lane has a key where the loop
  runs (checked: ANTHROPIC_API_KEY, FAILOVER_API_KEY, OPENAI_API_KEY, SCALEWAY_API_KEY) — the
  brain imported fine; it has nothing to call.` Same PATH_B outcome, a completely different and
  actionable diagnosis. Dropping a test key into `.secrets/ai_keys.env` flipped
  `any_lane_configured("haiku")` from `False` to `True`; the file was then reset to a
  fully-commented template that loads nothing.
- **Ledger RG-0055 LOCKED** — source assertion (REPO on `sys.path`, `ai_provider.py` present,
  the vague wording banned) plus an **executable** half that loads the agent from `scripts/`
  the way it really runs and proves `ai_provider` imports. 55 entries, 52 holding, 0 regressed.

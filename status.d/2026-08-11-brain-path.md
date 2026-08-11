- **BRAIN-PATH-1 — the "brain unreachable" finding was a two-line bug, not an environment gap.**
  `ai_provider.py` is at the repo root, `maintenance_agent.py` is in `scripts/`, and the agent
  never put `REPO` on `sys.path` — so `import ai_provider` had failed on **every run, on every
  machine, since the agent was written**, keys or no keys. RG-0049 degradation then binned every
  fault as PATH_B and exited 0. **Second green-looking no-op found in one day** (UA-EDGE-1 was
  the first): both times a correct fail-safe with a vague message hid a plain wiring fault.
- **Fixed:** `REPO` on `sys.path` (the `__file__` root, not the `--repo` rehearsal override);
  degradation messages now distinguish *will not import* / *no key* / *call failed*; and
  `.secrets/ai_keys.env` added as the local key slot, since `ai_provider.envkey()` only falls
  back to `/var/www/marketsquare/.env`, which exists on the server alone. **RG-0055 LOCKED**,
  with an executable half that loads the agent from `scripts/` and proves the import.
- **Still keyless, and now honestly so.** The loop reports: `no AI lane has a key where the loop
  runs (checked: ANTHROPIC_API_KEY, FAILOVER_API_KEY, OPENAI_API_KEY, SCALEWAY_API_KEY) — the
  brain imported fine; it has nothing to call.` **One key in `.secrets/ai_keys.env` (gitignored,
  template already in place) turns the loop's triage on — that is David's act, and the only
  thing still outstanding.** Worth knowing before doing it: autonomous triage has never actually
  run, so its first real outing should be watched rather than left to a 2 a.m. schedule.

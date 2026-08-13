## 2026-08-13 — BRAIN-DEPS-1: keyed brain live; loop self-heals its httpx dependency

- David pasted the Anthropic key (.secrets/ai_keys.env, slot pre-uncommented; verified filled without reading it). First keyed run: brain[anthropic/haiku] classified TS-0031 = DESIGN → PATH_B by judgement — agreeing with the manual triage. Dashboard chip now KEYED green.
- Found at first call: ai_provider lazily imports httpx inside lane calls — fresh sandboxes pass the import proof but lose the brain at the first REAL call (ModuleNotFoundError, degraded per RG-0049). Fix: _ensure_brain_deps() in maintenance_agent.py — one guarded quiet pip install, fail-soft. Proven by uninstall→run→reinstalled-by-agent+clean classify.
- RG-0055 strengthened (not weakened): now also fails if the bootstrap disappears. Ledger green.
- Ops note: cold-sandbox first run can take ~3 min (httpx download) — run the agent detached and poll; a foreground bash call gets killed at the ~3-min cap.

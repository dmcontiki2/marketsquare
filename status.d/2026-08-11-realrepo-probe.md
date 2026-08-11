- **Correction to today's earlier read: the agent's three `no clean patch` results were RIGHT.**
  TS-0031 is a UX/confidence-policy change that its own row says is blocked awaiting information
  from the reporter; TS-0024 is an unanswered question with no reproducible defect. Neither is
  mechanically patchable. The queue contains no mechanical faults, so 0/2 is the correct output,
  not a failure.
- **What is still genuinely unproven, and why B4 cannot settle it:** both rehearsal tiers patch a
  two-line sandbox `app.py`. The real application is `ms.js` at 1.07 MB and `bea_main.py` at
  907 KB. CAND-FIX-1 made those files visible to the brain for the first time today — nothing has
  yet tested whether a patch written against a windowed excerpt of a million-byte file actually
  applies and gates green.
- **`scripts/maint_realrepo_probe.py` added** — clones the repo, seeds one known mechanical
  defect into a real file, runs the real agent in shadow, and reports whether the defect was
  repaired. Shadow by construction (temp clone + the kill switch stripped from the environment),
  so it can never ship. Run: `python3 scripts/maint_realrepo_probe.py [--target bea] [--keep]`.
- **This is the last open question before the timer is a reasonable idea.** Spine proven, guard
  proven in both phases, B4 Tier 2 PASS, brain reachable — but the agent has still never written
  a line of code into a file this codebase actually contains.

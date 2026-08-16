## 2026-08-16 — INFRA-TEST-VERDICT-1: the Infrastructure Test buttons answer at the row

David (attended, mid-TSL): "on the infrastructure i see nothing happening when i use those test
buttons, please add some visual indication of PASS/FAIL, and if fail then we need a small
explanation of why and what is needed to resolve it."

Root cause, not a dead button: `infraLoad(id)` did work — it re-probed `/admin/services-status?service=id`
and re-rendered the rows — but a per-service re-probe usually returns the SAME status, so the row
repainted identically and the only feedback was "Checked <time>" in a side line. The AI Providers
card (apv3Test) already answered visibly; the infra card did not.

Fix (dashboard.server.html, ships as dashboard.html):
- Each infra row now carries a verdict slot (`infra-res-<id>`) and a stable row id.
- New `window.infraVerdict`: paints ✓ PASS green / ✗ FAIL red / △ WARN amber / — NO KEY grey at
  the row the moment the re-probe answers ("testing…" while in flight).
- Any non-PASS inserts a "Why / Resolve" strip under the row: the probe's `detail` verbatim plus a
  status-specific resolution line (nokey → set the named key + restart; fail → key/provider/network
  from the server; warn → degraded-not-down guidance). The strip is removed and repainted per test.
- The `infra-out` side line now carries ✓/✗ + label + detail + time instead of a bare "Checked".

Asserted: **RG-0093** (LOCKED) — the verdict machinery must exist and the Test path must call it.

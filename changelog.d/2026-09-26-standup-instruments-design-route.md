## 2026-09-26 — Stand-up: three instrument/routing faults fixed, L8's 26-day zero explained

- **EDGE-STATUS-BLIND-1 (OPEN_LOOPS L20a).** `scripts/regression_ledger.py` told a Cloudflare
  edge refusal from an app answer in `_get()` (EDGE-BLIND-1, 18 Sep) but **not** in `_status()`,
  `_post_status()` or `_headers()` — each handed the caller Cloudflare's own 403 as though the APP
  had said it. Two-sided damage: an entry asserting `/health == 200` CONVICTS a healthy site
  (RG-0028 did exactly that on the 25 Sep board, printing "Do not deploy over this"), and an entry
  asserting a route refuses anonymous callers PASSES without the app being reached — the same hole
  QA-GATE-BLIND-1 found in the deploy gate a day earlier, one layer in. RG-0401 already rules it:
  an edge refusal is BLIND, never REGRESSED. Fixed as ONE writer, `_edge_refused()`, consulted by
  all four readers (RG-0421's pattern). **Not weakened:** only a refusal Cloudflare SIGNS counts, so
  an app 401/403 still returns its code and every negative entry keeps its teeth; origin 5xx stays
  in `_get()` alone per UPSTREAM-BLIND-1. `scripts/test_edge_status_blind1.py` is red on the pre-fix
  source and prints the false conviction and the false acquittal verbatim.
  *Correction to L20's own diagnosis:* the row blamed a missing named User-Agent. The ledger has
  carried one since line 84; probed 26 Sep, its UA gets 200 and only the bare urllib UA gets
  `error code: 1010`. The mechanism is a transient edge refusal mid-board being read as a verdict.

- **INSTRUMENT-DOOR-1.** `GET /dashboard/bit` and `GET /dashboard/maint` both carried the docstring
  *"No auth (obscure URL)"*. That stopped being true on **24 Sep**, when SEC-GATE-1 declared both
  **admin** in `route_policy.json`: the gate now answers an anonymous caller `401
  {"code":"admin_required"}` before either handler is entered. The false sentence had already cost
  vision — the 25 Sep daily watch recorded its anonymous probes going blind (DW-158), and this
  stand-up read both dashboards blind until it carried a credential. Docstrings and the MAINT-DASH-1
  header comment corrected to name the admin door and the `dashboard.server.html` fetch wrapper that
  supplies it. Handlers unchanged; the served ops dashboard was never affected (it has the wrapper).

- **DESIGN-ROUTE-1 (OPEN_LOOPS L8) — and it explains the 26-day zero four stand-ups re-probed.**
  `classify()` returned PATH_B and the loop wrote *"routed to design backlog (batched, designer
  gate)"* into its report. **Nothing wrote a dossier; nothing in `scripts/` touched
  `DESIGN_BACKLOG.md` at all.** Measured: TS-0027 and TS-0006 were both closed 11 Aug with "routed
  to the design backlog" in their fix_note, and the file holds exactly one dossier — DCB-001, which
  is neither of them. Two faults said routed; zero arrived. **So L8's premise was wrong:** the
  `design` tier was wired at the chokepoint the whole time (`/admin/maint/brain` accepts
  `task="design"`; `_MAINT_TIER_LADDER` carries it). It had no caller because no design work ever
  reached a backlog, because the routing was a string. `grep task="design"` → 0 was the symptom.
  Fixed: PATH_B now files a real dossier in the template `DESIGN_CHANGE_GUIDELINES.md` publishes,
  asking the **design tier** for the PROPOSED DIRECTION (`task="design"`, RUL-013's allocated lane —
  its first real caller), stamping the serving model, and reporting the dossier id actually written
  instead of the old sentence. **The GATE line is written EMPTY on purpose**: criterion 10 says an
  absent gate means NOT APPROVED, DO NOT BUILD, and binding the designer role is open item 2 and
  David's. The filer never scores its own dossier, declares criteria 3 and 5 unmet rather than
  claiming them, is idempotent across the loop's three daily runs, and when the brain is unreachable
  from a sandbox vantage (VANTAGE-BRAIN-1) files with the direction blank and the reason NAMED —
  never a guess. `scripts/test_design_route1.py` red on the pre-fix source, printing the measurement.

- Gates after: `rulings_check` 150 rulings, **0 FAIL**, 25 WARN, 38 NOT CHECKED (VANTAGE-BLIND-1
  reporting its blindness). BIT board from the edge vantage **8/8 PASS**. The three pre-existing
  instrument tests (hostqueue watchdog, stand-up watchdog, QA gate blind) all still exit 0.

- **BIT-STORE-FLOOR-1 — found live DURING this run's post-deploy verification, and it is the
  reason the run did not report green and stop.** At **19:36:04Z** a caller POSTed an **empty body**
  to `POST /dashboard/bit`. The handler stored `dict(payload)` unconditionally, so
  `bit_status.json` became `{"received_at": "2026-09-26T19:36:04Z"}` and nothing else — and
  `GET /dashboard/bit` served exactly that: **no state, no results, no verdict.** It could not even
  fall through to the handler's own "no BIT run recorded yet" branch, because the file existed. Two
  probes 60 s apart returned the same stub, so it was persistent, not a mid-write. **The site was
  healthy throughout:** the board had read 8/8 PASS at 19:02:29Z and an independent edge-vantage run
  returned 8/8 PASS minutes after the wipe. One empty POST replaced a real verdict with a blank, and
  the dashboard panel read neither green nor red. Verified **not** caused by this run's own deploy:
  the bea_main.py change in `d449eec` is 37 inserted lines of docstring prose and touches no handler.
  This is QA-GATE-BLIND-1's lesson (25 Sep) one store along — there the damage was not the blind run
  but `accept()` writing it over the baseline. Fixed with the same rule: a payload carrying no
  `results`, no `state` and no `total` is **NOT MEASURED** and does not overwrite; it is recorded as
  `last_blind_post` **inside** the surviving board so the blindness is visible rather than silent,
  and the caller gets 200 with `stored: false` and the reason — never an error, because a BIT runner
  that cannot post is a second failure on top of the first. **The floor never suppresses red:** an
  all-FAIL board still overwrites, asserted by name in the test. `scripts/test_bit_store_floor1.py`
  is red on the pre-fix source and reproduces the wipe verbatim.

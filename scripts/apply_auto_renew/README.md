# apply_auto_renew — how AUTO-RENEW-1 (RUL-224) was laid into the big files (12 Oct 2026)

The house rule for `bea_main.py`, `ms.js`, `dashboard.server.html` and the other large files is a Python
string-replace with a backup and a verify, never an editor write. This folder is that, kept as the audit trail.

| File | What it changes |
|---|---|
| `p1_payments.py` | `payments.py`: `plan` / `channels` on `initialize_payment`; plan + subscription calls |
| `p2_bea.py` + `bea_block.txt` | `bea_main.py`: schema, the switch, the hooks, the renewal block, the routes, the tiles |
| `p3_route_policy.py` | `route_policy.json`: the three new routes |
| `p4_ms_js.py` + `js_block.txt` | `ms.js`: the tick box, the plan-card line, Cancel renewal |
| `p5_dashboard.py` | `dashboard.server.html`: the +1 page switch and four tiles |
| `p6_ledger.py` + `ledger_block.txt` | `scripts/regression_ledger.py`: RG-0964, RG-0965, RG-0966 |
| `p7_rulings.py` | `scripts/rulings_check.py`: RUL-224 |
| `p8_docs.py` | `OPEN_LOOPS.md` L42, `AUTO_RENEW_BRIEF.md` build record, `WAYS_OF_WORKING.md` |

Every replacement asserts its anchor is found exactly once, so a patch either applies whole or stops with the
anchor it could not find. Each file gets a `.bak-autorenew-<ts>` copy first; restore = copy it back. All of them
are already applied in this repo — running `apply_all.sh` again skips every file.

The build was first laid on d51cfa4 and proven there, then re-laid on 031273f (another lane shipped into the
same files while the build was running) and proven again; the anchors held unchanged across both.

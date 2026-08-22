## 2026-08-22 — RUL-040 live: AI example adverts labelled, DEMO banner on the demo maps

Shipped through /TSL. The pre-deploy gate first returned `CM=REVIEW` — fifteen fragments
from several sessions had never been folded, so CHANGELOG's newest entry read 21 Aug while
code was shipping. Folded via the single writers (`changelog_compile.py`,
`status_compile.py`); the re-run returned `CM=ok DB=ok → ok`.

**Live verification (PROBED, not read):** index references ms.js **v516**; the served build
has 4 × `AI EXAMPLE GENERATED ADVERT`, no `SUPER ADVERT`, no claim wording, and the pill's
"not a real listing". `/static/ts_demo_banner.js` 200 (4,975 B, mounts `ts-demo-tab`);
`/static/adventures_za_map.html` loads it. `/health` ok/1.3.1, 0.32s; TLS 32 days.

**RG-0140 and RG-0141 promoted OPEN → LOCKED** on the post-deploy run, per the rule that a
fix is not done until it is locked. Ledger 0 REGRESSED / 130 holding; rulings_check 41/41.

Left deliberately: **RG-0146** (secrets register) also reported READY TO LOCK but belongs to
the concurrent secret-rotation session — that session promotes its own entry rather than
this one racing it in a file two writers were already colliding in today.

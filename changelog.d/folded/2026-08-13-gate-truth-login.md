## 2026-08-13 — GATE-TRUTH-1: a wrong reviewer code no longer reads as "Connection error" (RG-0066)

Maroushka tried to sign in to fix her photo-blur re-uploads (D11/TS-0022) and got
"Connection error. Please try again." — the same day GATE-ENFORCE-2 armed the origin
catch-all. Root cause reproduced anonymously: the gate screen falls through from
/review/login to POST /admin/login, which now answers **nginx HTML 401** at the origin;
the script's `r.json()` throws and the catch mislabels every unrecognised entry —
wrong code, stale code, rate-limit — as a network failure. Not the old BEA-down class
(BACKLOG 27 Jun): /health green, BEA v1.3.1 up throughout; it is the 5 Aug "401 that
ate David's first report" class in a new spot.

Fix (marketsquare.html gate script, +16 lines, node --check green):
- `_adminLogin` parses text-first; a gate-refused 401/403 with a non-JSON body now says
  **"Incorrect reviewer code. Please check it and try again."**; JSON answers keep their
  detail; only a real network throw says "Connection error".
- /review/login 429 now says "wait 10 minutes" (limit is 8 tries/10 min/IP); 503 says
  reviewer access is off.

Ledger: **RG-0066 OPEN** (live half: served index.html carries the GATE-TRUTH-1 marker;
repo half: source keeps the branch). EXPECTED open until the ref lands — the deploy
engine is stalled (DW-042); this ships with tonight's revival. Rollback:
marketsquare.html.bak-gatetruth-20260813.

Maroushka's unblock needs NO deploy: /review/login is live and healthy (verified —
wrong code answers clean JSON 401). She needs the current reviewer code re-sent and,
if she has been retrying, a 10-minute wait before entering it.

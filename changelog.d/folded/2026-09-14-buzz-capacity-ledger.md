## 2026-09-14 — BUZZ-CAP-1 locked in the ledger (RG-0366)

The Buzz capacity work was built and documented but carried no assertion, which by the standing
rule means it was half done — the occurrence was fixed, the class was not.

- **RG-0366 LOCKED.** Four source legs on `bea_main.py`: `BUZZ_PUSH_TIMEOUT` is defined and ≤ 2s;
  the `/buzz` push passes that timeout explicitly so it cannot silently inherit the 8s default
  again; the email fallback is queued with `background_tasks.add_task` and never awaited on the
  request path; `BUZZ_LOG_KEEP_DAYS` is defined and `_buzz_prune` is actually called from the send
  path. Source-side by design — no live probe can tell a fast push vendor from a capped one.
- **Scope is the class, not the endpoint:** any new synchronous endpoint that blocks on an outside
  vendor reopens the same hole, which is why the numbers live in named constants.
- **Board:** 353 entries · 331 holding · **0 REGRESSED** · 22 open · 0 UNVERIFIED · exit 0.
  Rulings check: 107 rulings, 0 FAIL.
- **SSH-BOOTSTRAP-1 applied:** the first board run left RG-0362 NOT EVALUATED because this vantage
  had no key to the origin; `load_sandbox_ssh.sh` fixed it in one command and the re-run evaluated
  it. A NOT EVALUATED row is not a green board — it was re-run rather than reported around.
- **Visuals:** `genie/BUZZ_CAPACITY.html` and `genie/RUL131_SELLER_TO_AGENCY.html` indexed into
  the gallery (356 visuals).

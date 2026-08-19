## 19 Aug 2026 — MIGRATE-IMPORT-1: the migration chain had been stalled since 18 Aug, silently

**The deploy log answered it in three lines:**

```
[post_deploy] migrations: running 023_relink_wonders_railexp.py
[023_relink] REFUSE: cannot import main (No module named 'main')
[post_deploy] migrations: 023 FAILED (rc=3) — NOT recorded; later migrations skipped this run.
```

`post_deploy` runs each migration as `(cd $LIVE && python3 /abs/path/NNN.py --apply)`. **Python
puts the script's own directory on `sys.path[0]` — never the CWD** — so `import main` could never
resolve, no matter what the working directory was. The file's own comment said *"CWD = live web
root per the migrations contract"*: true, and useless, because Python doesn't consult CWD for a
script invoked by path.

`post_deploy` then `break`s, which is **correct** — migrations are order-dependent and must not
run out of sequence — but it meant 023 blocked 024, 025 and 026 on every single deploy from
18 Aug onward.

**Fixed as a class, not an instance.** Both migrations that import the app (023, 024) now insert
CWD into `sys.path` before importing. Proven by running 023 under `post_deploy`'s exact
invocation: `import main` resolved where it had raised.

---

### Correction: "the deploy isn't reaching the server" was wrong

The code was deploying the whole time — the log says `DEPLOY OK · now live at 9867f059 · health
ok`. Only the **nginx-touching migrations** were stuck. This session asserted the stronger,
wrong conclusion twice, on two flawed probes:

1. `/admin/login` and `/review/claim-code` returning nginx HTML 401 was read as *old code*. It was
   actually **migration 025 never having run** — a different fault with the same symptom.
2. `/review/request-link` was probed with an `example.invalid` address. That address is **off the
   reviewer allowlist**, so the endpoint returns a bare `{"ok":true}` and returns *before* it ever
   reaches the `delivery` field the probe was looking for. The probe could never have shown new
   code, whatever was deployed.

Round 1 (GATE-NOLOCK-1) and round 2 (LINK-PREFETCH-1) have in fact been live since 03:36 UTC —
`/review/claim-code` answers with app JSON, confirmed. Round 3 (SIGNIN-CODE-1, ONETAP-1) returns
404 because it was committed after that deploy, exactly as expected.

**Ledger.** RG-0116 asserts the import contract in source for every present and future
main-importing migration, plus the chain's live effect. Also fixed RG-0081, which read a 429 from
its own probe rate as *"migration 019 has not landed"* — a false red that has now fired twice.
A 429 is the limiter answering, which proves reachability; RG-0108 already treated it that way.

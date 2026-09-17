# The rig — the REAL app, locally, for rendered proofs (17 Sep 2026, RUL-076 §7.3)

David's binding constraint for the RUL-126 batch: *"see it on the actual app first."* The rig is
the actual app — `bea_main.py` + `marketsquare.html` + `ms.js` + `ms.css` + `quick.html` +
`dashboard.server.html` — served on ONE local origin against a COPY of the live database, driven by
headless Chromium at 412×915. Every `scripts/smoke_harness/verify_*.mjs` runs against it.

## Build it (cloud container or any Linux box with Python 3.11, node 22, Playwright's Chromium)

1. `git clone --depth 1 https://github.com/dmcontiki2/marketsquare rig` and overlay the working-tree
   copies of the files above (`rig_sync.sh` copies them from the staged uploads folder).
2. Pull a DB copy from the box: `scp root@178.104.73.239:/var/www/marketsquare/marketsquare.db
   /var/www/marketsquare/marketsquare.db` (the BEA reads `database.DB_PATH`, which is that path).
   Apply the pending migrations to the COPY: `python3 migrations/040_*.py --apply`,
   `041_*.py --apply` (with `MS_API_KEY` set, from the rig folder).
3. `pip install fastapi uvicorn boto3 bcrypt python-multipart httpx pillow PyJWT`.
4. `./rig_start.sh` — starts `rig_run.py` (the app + the static files on http://127.0.0.1:8000)
   with rig-only secrets: `MS_API_KEY`, `MS_REVIEW_SECRET`, `MS_JWT_SECRET`, `MS_ADMIN_KEY`.
5. Mint cookies with the rig secrets: `rig_token.py` (review gate), `rig_user_token.py <email>`
   (a signed-in user), `rig_admin_token.py` (dashboard admin). The verify scripts read them from
   `/home/claude/rig_*_token.txt` unless `RIG_*_TOKEN_FILE` points elsewhere.
6. `node verify_zoom.mjs` … (`NODE_PATH` or a local `playwright` install; executablePath
   `/opt/pw-browsers/chromium`).

`rig_sync.sh` rewrites two constants in the RIG COPIES ONLY (`BEA_URL` / `BEA` → the local origin);
the repo files are never touched. Arm the batch on the rig with
`UPDATE launch_switches SET baseline_q4=1` or `POST /admin/flags {"baseline_q4": true}`; the app
also honours `?baseline=1` on a non-production host (`msBaselineOn()`), never on the live origin.

The rig is a COPY: fixture rows it creates (the Dlamini family agencies, rig-quick-tester drafts)
live only there. Nothing here touches the box.

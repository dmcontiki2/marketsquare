## 2026-08-20 — MIGRATE-ENV-1: the migration chain runs in the app's own interpreter and environment

The chain sat jammed at `023_relink_wonders_railexp.py` for two days (DW-051, RG-0125),
failing with `REFUSE: cannot import main`. The post-mortem found **two** faults, and
fixing either one alone still leaves the chain jammed:

1. **Environment.** `post_deploy.sh` ran migrations with a bare environment, but
   `main.py` refuses to import without `MS_API_KEY` — which the unit carries as an
   inline systemd `Environment=`, *not* in `/etc/marketsquare/secrets.env`. Sourcing
   the secrets file alone would not have been enough.
2. **Interpreter.** The runner used the system `python3`, while the service runs
   `$LIVE/venv/bin/uvicorn`. The venv has `python-multipart`; the system interpreter
   does not, so `import main` dies inside FastAPI's form-data path **even with the
   environment loaded**. This is why 19 Aug's MIGRATE-IMPORT-1 CWD guard did not clear it.

Fix (ops/autodeploy/post_deploy.sh): resolve `MS_PY` to the venv interpreter (falling
back to system python3), load the unit's inline `Environment=` plus `secrets.env`
without ever echoing the values, and warn loudly at a named step if `MS_API_KEY` is
still unset. The seeds use `$MS_PY` too.

**Class property, not an instance fix:** any script that imports the app must run in the
SAME interpreter and the SAME environment as the app it imports — every future migration
inherits this, not just 023.

Proven on the box before shipping: with venv python + service env, `023` **rc=0**
(catalog 319 wonders, 84/104 listings relinked — work stranded since 18 Aug),
`024` rc=0 (healed 0 — already clean), `027` rc=0 (0 protected listings faded).

RG-0125 is the standing assertion and stays OPEN until the next deploy records the
chain past 022.

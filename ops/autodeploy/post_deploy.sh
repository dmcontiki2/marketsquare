#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
#  post_deploy.sh — runs ON the server, called by server_deploy.sh AFTER a
#  deploy is confirmed healthy. (DEPLOY-CONSOLIDATION-1, 2 Aug 2026)
#
#  Carries the two jobs the retired scp deploy did beyond copying files:
#    1. SEED  — seed_super_global.py --apply (idempotent, self-healing; the same
#       every-deploy step the old deploy_marketsquare.bat ran).
#    2. MIGRATIONS — one-time scripts from the repo's migrations/ dir, each run
#       exactly once, recorded in $MS_LIVE/.migrations_done. The live *.db files
#       are snapshotted before the first pending migration runs.
#
#  NON-FATAL BY DESIGN: always exits 0. The deploy is already live and healthy;
#  a seed/migration problem is reported loudly in the deploy log, never hidden,
#  and never rolls the deploy back. NEVER touches .env, uploads/ or demo_sellers.json.
# ═════════════════════════════════════════════════════════════════════════════
set -u
SRC="${MS_SRC:-/opt/marketsquare-src}"
LIVE="${MS_LIVE:-/var/www/marketsquare}"
TS="$(date -u '+%Y%m%d-%H%M%S')"

say() { echo "[post_deploy] $*"; }

# ── POSTDEPLOY-EYES-1 (20 Aug 2026) ──────────────────────────────────────────
# Every step's outcome, written where ANY session can read it over plain HTTP.
# Born from a blind morning: the supers stayed hidden after a deploy and nothing
# outside the server's journal could say whether the seed ran, whether a migration
# had jammed the chain, or which one. A step nobody can observe is a step that
# fails silently -- exactly the class the regression ledger exists to end.
STATUS_JSON="$LIVE/static/post_deploy_status.json"
STEPS=""
step() {  # step <name> <ok|failed|skipped|deferred> [detail]
    local d="${3:-}"; d="${d//\"/\'}"
    STEPS="${STEPS:+$STEPS,}{\"step\":\"$1\",\"result\":\"$2\",\"detail\":\"$d\"}"
}
write_status() {
    mkdir -p "$(dirname "$STATUS_JSON")" 2>/dev/null || true
    printf '{"generated_at":"%s","ref":"%s","steps":[%s]}\n' \
        "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "${MS_DEPLOY_REF:-deploy}" "$STEPS" \
        > "$STATUS_JSON" 2>/dev/null || say "status: could not write $STATUS_JSON"
}
trap write_status EXIT

# ── MIGRATE-ENV-1 (20 Aug 2026, DW-051/RG-0125) ──────────────────────────────
# The chain sat jammed at 023 for two days with "REFUSE: cannot import main". The
# post-mortem found TWO faults, and fixing either alone still leaves it jammed:
#   1. ENV — migrations were run with a bare environment, but main.py refuses to
#      import without MS_API_KEY, which the unit carries as an inline systemd
#      Environment= (not in secrets.env, so sourcing that file is not enough).
#   2. INTERPRETER — we ran the system `python3`, while the service runs
#      $LIVE/venv/bin/uvicorn. The venv has python-multipart; system python does
#      not, so `import main` dies on FastAPI form data even WITH the env loaded.
# Class property, not an instance fix: any script that imports the app must run in
# the SAME interpreter and the SAME environment as the app it is importing. Applies
# to the seeds below and every future migration, not just 023.
MS_PY="$LIVE/venv/bin/python3"
[ -x "$MS_PY" ] || MS_PY="$(command -v python3)"
say "env: interpreter $MS_PY"
if command -v systemctl >/dev/null 2>&1; then
    # parse the unit's inline Environment= into exports; never echo the values
    _envexp="$(systemctl show marketsquare -p Environment --value 2>/dev/null \
               | tr ' ' '\n' \
               | sed -n 's/^\([A-Z_][A-Z0-9_]*\)=\(.*\)$/export \1="\2"/p')"
    [ -n "$_envexp" ] && eval "$_envexp" && say "env: service environment loaded ($(printf '%s' "$_envexp" | grep -c '^export ') vars)"
    unset _envexp
fi
[ -r /etc/marketsquare/secrets.env ] && { set -a; . /etc/marketsquare/secrets.env; set +a; say "env: secrets.env loaded"; }
if [ -z "${MS_API_KEY:-}" ]; then
    say "env: WARNING - MS_API_KEY still unset; every migration that imports the app WILL refuse"
    step env failed "MS_API_KEY unset - migrations importing the app will refuse (MIGRATE-ENV-1)"
fi


# ── 1. Idempotent super-listing seed (same contract as the old bat step 3g) ──
if [ -f "$LIVE/seed_super_global.py" ]; then
    say "seed: running seed_super_global.py --apply (idempotent)"
    if (cd "$LIVE" && "$MS_PY" seed_super_global.py --apply); then
        say "seed: ok"; step seed ok
    else
        say "seed: FAILED (rc=$?) — run it by hand: cd $LIVE && python3 seed_super_global.py --apply"; step seed failed "run by hand: cd $LIVE && python3 seed_super_global.py --apply"
    fi
else
    say "seed: seed_super_global.py not on the box (manifest ships it) — skipped"; step seed skipped "not on the box"
fi

# ── 1b. Idempotent 3-tier LADDER seed (SUPER-AFRICA-1, 12 Aug 2026) ──────────
# Safe on every deploy: skips existing titles and any (country,category,tier)
# whose sup_<cc>_<catkey>_<tier>_*.jpg photos are not yet in static/super
# (media_push.bat carries those) — so it silently no-ops until media lands.
if [ -f "$LIVE/seed_super_ladder_global.py" ]; then
    say "ladder-seed: running seed_super_ladder_global.py --apply (idempotent)"
    if (cd "$LIVE" && "$MS_PY" seed_super_ladder_global.py --apply); then
        say "ladder-seed: ok"; step ladder_seed ok
    else
        say "ladder-seed: FAILED (rc=$?) — run by hand: cd $LIVE && python3 seed_super_ladder_global.py --apply"
    fi
else
    say "ladder-seed: seed_super_ladder_global.py not on the box (manifest ships it) — skipped"
fi

# ── 2. One-time migrations ───────────────────────────────────────────────────
DONE_FILE="$LIVE/.migrations_done"
touch "$DONE_FILE" 2>/dev/null || true
shopt -s nullglob
# DEFER-1 (9 Aug 2026, DW-030): a migration David has CONSCIOUSLY deferred is listed
# in $SRC/migrations/DEFERRED.txt (in-repo, so the decision is version-controlled).
# It is skipped LOUDLY on every deploy — never marked done, never blocking the chain.
# DW-030 was five migrations dead behind one failing gate script for three days;
# the fix is that "deferred" is now a recorded state, not a silent jam.
DEFER_FILE="$SRC/migrations/DEFERRED.txt"
is_deferred() {
    [ -f "$DEFER_FILE" ] || return 1
    sed 's/#.*//' "$DEFER_FILE" | tr -d ' \t' | grep -qxF "$1"
}
pending=()
for m in "$SRC"/migrations/*.py; do
    base="$(basename "$m")"
    grep -qxF "$base" "$DONE_FILE" 2>/dev/null && continue
    if is_deferred "$base"; then
        say "migrations: ######################################################"
        say "migrations: # DEFERRED by David (migrations/DEFERRED.txt): $base"
        say "migrations: # skipped, NOT recorded — chain continues past it."
        say "migrations: ######################################################"
        continue
    fi
    pending+=("$m")
done

if [ "${#pending[@]}" -eq 0 ]; then
    say "migrations: none pending"; step migrations ok "none pending"
else
    # snapshot the live DBs once, before the first pending migration
    BK="$LIVE/.db-backups/$TS"
    mkdir -p "$BK"
    cp -a "$LIVE"/*.db "$BK"/ 2>/dev/null && say "migrations: DB snapshot → $BK" \
        || say "migrations: WARNING - no *.db snapshotted (none found?)"
    for m in "${pending[@]}"; do
        base="$(basename "$m")"
        say "migrations: running $base"
        # POSTDEPLOY-EYES-2 (20 Aug 2026): capture the migration's OWN output. EYES-1 told us
        # WHICH migration jammed but not WHY, and the why still needed SSH -- half an eye is
        # still a blind spot. tee keeps the deploy log byte-identical to before.
        MOUT="$(mktemp)"
        if (cd "$LIVE" && "$MS_PY" "$m" --apply) 2>&1 | tee "$MOUT"; [ "${PIPESTATUS[0]}" -eq 0 ]; then
            echo "$base" >> "$DONE_FILE"
            say "migrations: $base ok (recorded)"; step "migration:$base" ok "$(tail -n 1 "$MOUT" | tr -d '"' | cut -c1-200)"
        else
            say "migrations: $base FAILED (rc=$?) — NOT recorded; later migrations skipped this run."
            # POSTDEPLOY-EYES-3 (26 Aug 2026): the window was tail -n 3 | cut -c1-300, and it
            # DESTROYED the only diagnostic that mattered. 033_csp_verify_served.py failed four
            # deploys running; each time the line naming the value it measured was line -4 of its
            # output, one line outside the window, so every report said "something else is
            # emitting the header" and no report ever said WHAT was served. That is EYES-2's own
            # blind spot -- capturing a migration's output is worth nothing if the capture is
            # narrower than the evidence. Widened to 12 lines / 1200 chars, and backslashes are
            # stripped alongside quotes so a Windows path in an error can never break the JSON.
            step "migration:$base" failed "CHAIN JAMMED HERE (later migrations skipped) :: $(tail -n 12 "$MOUT" | tr '\n' ' ' | tr -d '"\\' | cut -c1-1200)"
            say "migrations: restore if needed: cp $BK/<file>.db $LIVE/  then systemctl restart marketsquare"
            break
        fi
        rm -f "$MOUT" 2>/dev/null || true
    done
fi
exit 0

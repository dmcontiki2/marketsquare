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

# ── 1. Idempotent super-listing seed (same contract as the old bat step 3g) ──
if [ -f "$LIVE/seed_super_global.py" ]; then
    say "seed: running seed_super_global.py --apply (idempotent)"
    if (cd "$LIVE" && python3 seed_super_global.py --apply); then
        say "seed: ok"
    else
        say "seed: FAILED (rc=$?) — run it by hand: cd $LIVE && python3 seed_super_global.py --apply"
    fi
else
    say "seed: seed_super_global.py not on the box (manifest ships it) — skipped"
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
    say "migrations: none pending"
else
    # snapshot the live DBs once, before the first pending migration
    BK="$LIVE/.db-backups/$TS"
    mkdir -p "$BK"
    cp -a "$LIVE"/*.db "$BK"/ 2>/dev/null && say "migrations: DB snapshot → $BK" \
        || say "migrations: WARNING - no *.db snapshotted (none found?)"
    for m in "${pending[@]}"; do
        base="$(basename "$m")"
        say "migrations: running $base"
        if (cd "$LIVE" && python3 "$m" --apply); then
            echo "$base" >> "$DONE_FILE"
            say "migrations: $base ok (recorded)"
        else
            say "migrations: $base FAILED (rc=$?) — NOT recorded; later migrations skipped this run."
            say "migrations: restore if needed: cp $BK/<file>.db $LIVE/  then systemctl restart marketsquare"
            break
        fi
    done
fi
exit 0

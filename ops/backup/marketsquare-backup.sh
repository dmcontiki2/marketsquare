#!/usr/bin/env bash
# MarketSquare nightly backup — SQLite-safe + Redis + media + configs,
# encrypted & deduplicated with restic, to TWO independent repos:
#   tier-1: local 100GB drive (fast restore)
#   tier-2: Hetzner Storage Box over SFTP (survives loss of the server)
#
# Deploy: /usr/local/sbin/marketsquare-backup.sh   (chmod 750, root-owned)
# Config: /etc/marketsquare-backup.env             (chmod 600)
# Run by: marketsquare-backup.timer (nightly)
set -Eeuo pipefail

ENV_FILE="${1:-/etc/marketsquare-backup.env}"
[ -r "$ENV_FILE" ] || { echo "FATAL: cannot read $ENV_FILE"; exit 2; }
# shellcheck disable=SC1090
source "$ENV_FILE"
export RESTIC_PASSWORD

TS="$(date -u +%Y%m%dT%H%M%SZ)"
log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
ping_hc(){ [ -n "${HEALTHCHECK_URL:-}" ] && curl -fsS -m 10 --retry 3 "${HEALTHCHECK_URL}${1:-}" >/dev/null 2>&1 || true; }
fail(){ log "FAILED: $*"; ping_hc "/fail"; exit 1; }
trap 'fail "unexpected error on line $LINENO"' ERR

ping_hc "/start"
log "=== MarketSquare backup $TS ==="

# 0) clean staging
rm -rf "$STAGE_DIR"; mkdir -p "$STAGE_DIR"

# 1) SQLite — ONLINE backup (never copy a live DB file directly)
if [ -n "${SQLITE_DB:-}" ] && [ -f "$SQLITE_DB" ]; then
  log "SQLite online backup: $SQLITE_DB"
  sqlite3 "$SQLITE_DB" ".backup '$STAGE_DIR/marketsquare.db'"
  # integrity check the COPY (not the live db)
  ok=$(sqlite3 "$STAGE_DIR/marketsquare.db" "PRAGMA integrity_check;")
  [ "$ok" = "ok" ] || fail "SQLite integrity_check on backup copy returned: $ok"
  log "SQLite copy integrity: ok"
else
  log "WARN: SQLITE_DB not found ($SQLITE_DB) — skipping DB"
fi

# 2) Redis — trigger a fresh snapshot, then stage dump.rdb
if command -v redis-cli >/dev/null && [ -n "${REDIS_RDB:-}" ]; then
  log "Redis BGSAVE"
  last="$(redis-cli LASTSAVE 2>/dev/null || echo 0)"
  redis-cli BGSAVE >/dev/null 2>&1 || log "WARN: BGSAVE call failed"
  for _ in $(seq 1 30); do
    now="$(redis-cli LASTSAVE 2>/dev/null || echo 0)"
    [ "$now" != "$last" ] && break; sleep 1
  done
  [ -f "$REDIS_RDB" ] && cp -a "$REDIS_RDB" "$STAGE_DIR/redis-dump.rdb" || log "WARN: $REDIS_RDB missing"
fi

# 3) manifest (what/when/versions) for restore sanity
{
  echo "backup_utc=$TS"
  echo "host=$(hostname)"
  echo "app_dir=$APP_DIR"
  command -v python3 >/dev/null && echo "python=$(python3 -V 2>&1)"
  echo "git_head=$(git -C "$APP_DIR" rev-parse HEAD 2>/dev/null || echo n/a)"
} > "$STAGE_DIR/MANIFEST.txt"

# 4) assemble restic source list (stage + live dirs; restic dedups so this is cheap)
SOURCES=( "$STAGE_DIR" "$APP_DIR" )
[ -n "${MEDIA_DIR:-}" ] && [ -d "$MEDIA_DIR" ] && SOURCES+=( "$MEDIA_DIR" )
[ -n "${N8N_DIR:-}" ]   && [ -d "$N8N_DIR" ]   && SOURCES+=( "$N8N_DIR" )
# shellcheck disable=SC2206
[ -n "${EXTRA_PATHS:-}" ] && SOURCES+=( $EXTRA_PATHS )

# exclude noise (re-creatable / huge / secret-bearing handled separately)
EXCLUDES=( --exclude '*/__pycache__/*' --exclude '*/.venv/*' --exclude '*/node_modules/*'
           --exclude '*.pyc' --exclude '*/.git/*' )

backup_to_repo(){
  local repo="$1" label="$2"
  [ -n "$repo" ] || { log "skip $label (no repo set)"; return 0; }
  export RESTIC_REPOSITORY="$repo"
  # init once (idempotent: ignore "already initialized")
  restic snapshots >/dev/null 2>&1 || { log "init $label repo"; restic init; }
  log "backup -> $label"
  restic backup --tag nightly --host "$(hostname)" "${EXCLUDES[@]}" "${SOURCES[@]}"
  log "retention -> $label (d:$KEEP_DAILY w:$KEEP_WEEKLY m:$KEEP_MONTHLY)"
  restic forget --prune --keep-daily "$KEEP_DAILY" --keep-weekly "$KEEP_WEEKLY" --keep-monthly "$KEEP_MONTHLY"
  # cheap structural check every run; full --read-data is done by restore-test.sh
  restic check
  unset RESTIC_REPOSITORY
}

backup_to_repo "${LOCAL_RESTIC_REPO:-}"      "tier-1 local 100GB drive"
backup_to_repo "${STORAGEBOX_RESTIC_REPO:-}" "tier-2 Hetzner Storage Box"

# 5) tidy staging (don't leave a plaintext DB copy lying around)
rm -rf "$STAGE_DIR"

log "=== backup OK ==="
ping_hc ""   # success ping

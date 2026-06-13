#!/usr/bin/env bash
# Restore drill — proves the backups are actually recoverable.
# A backup you have never restored is a backup you do not have.
# Run monthly (manually or via a second timer). Restores the latest snapshot from a repo
# into a temp dir, verifies the SQLite copy, and reports — it does NOT touch live data.
set -Eeuo pipefail
ENV_FILE="${1:-/etc/marketsquare-backup.env}"
REPO_CHOICE="${2:-local}"   # "local" or "box"
source "$ENV_FILE"; export RESTIC_PASSWORD

case "$REPO_CHOICE" in
  local) export RESTIC_REPOSITORY="$LOCAL_RESTIC_REPO" ;;
  box)   export RESTIC_REPOSITORY="$STORAGEBOX_RESTIC_REPO" ;;
  *) echo "usage: restore-test.sh <env> <local|box>"; exit 2 ;;
esac

OUT="$(mktemp -d)"
echo "Repo: $RESTIC_REPOSITORY"
echo "Restoring latest snapshot to $OUT ..."
restic restore latest --target "$OUT"

DB="$(find "$OUT" -name marketsquare.db | head -1)"
if [ -n "$DB" ]; then
  ok=$(sqlite3 "$DB" "PRAGMA integrity_check;")
  rows=$(sqlite3 "$DB" "SELECT count(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo '?')
  echo "Restored DB: $DB"
  echo "  integrity_check: $ok"
  echo "  tables: $rows"
  [ "$ok" = "ok" ] || { echo "RESTORE TEST FAILED"; exit 1; }
else
  echo "WARN: no marketsquare.db found in restore"
fi
echo "Restore test OK. Inspect $OUT then: rm -rf $OUT"

#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
#  server_deploy.sh — MarketSquare / TrustSquare server-side git-pull deploy
#
#  Runs ON the Hetzner box. Pulls the latest source from the GitHub mirror,
#  places files into the live web root, restarts the app, reloads nginx, purges
#  the CDN, health-checks the result and AUTO-ROLLS-BACK if the app fails to
#  come up healthy. It is the server half of Phase 3 "automated deploy": it
#  removes the need for a human to run deploy_marketsquare.bat.
#
#  It is driven two ways (both call THIS script — one engine, one rollback story):
#    • the systemd timer (marketsquare-deploy.timer) — polls every ~2 min and
#      deploys only when the tracked ref has advanced (idempotent no-op otherwise)
#    • the optional POST /admin/deploy HTTPS hook — runs it now, with --force
#
#  SAFETY / IDEMPOTENCE
#    • Placement is an ALLOWLIST copy from deploy_manifest.txt. It NEVER deletes.
#      The live SQLite DB, .env, uploads and demo_sellers.json are never touched.
#    • A single flock means two deploys can never overlap.
#    • Unchanged ref → exits 0 without touching anything.
#    • Every changed run snapshots the files it is about to overwrite, so a bad
#      deploy is restored automatically (and can be restored by hand — see README).
#    • No secret lives in this file or in the repo. Optional tokens are read from
#      the environment / the systemd unit only.
#
#  Exit codes:  0 = success or nothing-to-do · 2 = deploy failed & rolled back
#               3 = deploy failed & rollback ALSO failed (needs a human) · 1 = usage/setup
#
#  Config (all optional — sensible defaults; override in the systemd unit):
#    MS_SRC          source clone dir            (default /opt/marketsquare-src)
#    MS_LIVE         live web root               (default /var/www/marketsquare)
#    MS_REMOTE_URL   mirror URL                  (default https://github.com/dmcontiki2/marketsquare.git)
#    MS_DEPLOY_REF   branch to track            (default "deploy"; set "main" for full GitOps)
#    MS_SERVICES     services to restart         (default "marketsquare")
#    MS_HEALTH_URL   health endpoint             (default http://localhost:8000/health)
#    MS_HEALTH_OK    grep pattern for healthy    (default '"status":"ok"')
#    MS_PURGE_URL    CDN purge endpoint          (default http://localhost:8000/admin/purge-cache)
#    MS_ADMIN_KEY    optional X-Admin-Key for purge (default unset → no header)
#    MS_LOG          deploy log file             (default /var/log/marketsquare-deploy.log)
#    MS_LOCK         lock file                   (default /run/marketsquare-deploy.lock)
#    MS_KEEP_BACKUPS how many rollback snapshots (default 10)
# ═════════════════════════════════════════════════════════════════════════════
set -uo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
MS_SRC="${MS_SRC:-/opt/marketsquare-src}"
MS_LIVE="${MS_LIVE:-/var/www/marketsquare}"
MS_REMOTE_URL="${MS_REMOTE_URL:-https://github.com/dmcontiki2/marketsquare.git}"
MS_DEPLOY_REF="${MS_DEPLOY_REF:-deploy}"
MS_SERVICES="${MS_SERVICES:-marketsquare}"
MS_HEALTH_URL="${MS_HEALTH_URL:-http://localhost:8000/health}"
MS_HEALTH_OK="${MS_HEALTH_OK:-\"status\":\"ok\"}"
MS_PURGE_URL="${MS_PURGE_URL:-http://localhost:8000/admin/purge-cache}"
MS_ADMIN_KEY="${MS_ADMIN_KEY:-}"
MS_LOG="${MS_LOG:-/var/log/marketsquare-deploy.log}"
MS_LOCK="${MS_LOCK:-/run/marketsquare-deploy.lock}"
MS_KEEP_BACKUPS="${MS_KEEP_BACKUPS:-10}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="${MS_MANIFEST:-$SCRIPT_DIR/deploy_manifest.txt}"

main() {   # entire run parses before execution — safe against self-update mid-run (2 Aug 2026)
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

# ── Logging ──────────────────────────────────────────────────────────────────
_ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log()  { local m; m="[$(_ts)] $*"; echo "$m"; { echo "$m" >>"$MS_LOG"; } 2>/dev/null || true; }
warn() { log "WARN: $*"; }
die()  { log "ERROR: $*"; exit "${2:-1}"; }

# ── Single-flight lock (so two deploys never overlap) ────────────────────────
exec 9>"$MS_LOCK" 2>/dev/null || die "cannot open lock $MS_LOCK"
if ! flock -n 9; then
    log "another deploy is already running (lock held) — skipping this tick."
    exit 0
fi

# ── Preconditions ────────────────────────────────────────────────────────────
command -v git  >/dev/null 2>&1 || die "git not found on PATH"
[ -d "$MS_LIVE" ] || die "live root $MS_LIVE does not exist"
[ -f "$MANIFEST" ] || die "manifest $MANIFEST not found"

# ── Ensure the source clone exists (self-healing) ────────────────────────────
if [ ! -d "$MS_SRC/.git" ]; then
    log "source clone missing — cloning $MS_REMOTE_URL → $MS_SRC (one-time)"
    mkdir -p "$(dirname "$MS_SRC")"
    git clone --quiet "$MS_REMOTE_URL" "$MS_SRC" || die "initial clone failed"
fi

# ── Fetch and resolve the target ─────────────────────────────────────────────
if ! git -C "$MS_SRC" fetch --quiet --prune origin 2>>"$MS_LOG"; then
    warn "git fetch failed (network?) — leaving live site untouched."
    exit 0
fi

# Does the tracked ref exist on the mirror yet?
if ! git -C "$MS_SRC" rev-parse --verify --quiet "origin/${MS_DEPLOY_REF}^{commit}" >/dev/null; then
    log "deploy ref 'origin/${MS_DEPLOY_REF}' does not exist yet — nothing to deploy."
    log "  → arm the first deploy by publishing it, e.g.:  git push origin main:${MS_DEPLOY_REF}"
    exit 0
fi

TARGET_SHA="$(git -C "$MS_SRC" rev-parse "origin/${MS_DEPLOY_REF}")"
STATE_FILE="$MS_SRC/.last_deployed_sha"
LAST_SHA="$(cat "$STATE_FILE" 2>/dev/null || echo '')"

if [ "$FORCE" -eq 0 ] && [ "$TARGET_SHA" = "$LAST_SHA" ]; then
    # Idempotent no-op — this is the common case on the 2-minute timer.
    exit 0
fi

SHORT="$(echo "$TARGET_SHA" | cut -c1-8)"
PREV_DISP="${LAST_SHA:0:8}"; [ -z "$PREV_DISP" ] && PREV_DISP="none"
log "─────────────────────────────────────────────────────────────────────────"
log "DEPLOY start · ref=${MS_DEPLOY_REF} · target=${SHORT} · previous=${PREV_DISP} · force=${FORCE}"

# ── Check out the exact target commit ────────────────────────────────────────
if ! git -C "$MS_SRC" reset --hard "$TARGET_SHA" >>"$MS_LOG" 2>&1; then
    die "git reset --hard $SHORT failed — live site NOT changed." 2
fi
git -C "$MS_SRC" clean -fd -e '.last_deployed_sha' >>"$MS_LOG" 2>&1 || true

# ── Snapshot current live files (rollback point) BEFORE we overwrite anything ─
TS="$(date -u '+%Y%m%d-%H%M%S')"
BACKUP_DIR="$MS_LIVE/.deploy-backups/$TS"
mkdir -p "$BACKUP_DIR"
echo "prev_sha=$LAST_SHA" > "$BACKUP_DIR/DEPLOY_INFO"
echo "target_sha=$TARGET_SHA" >> "$BACKUP_DIR/DEPLOY_INFO"

# Parse the manifest into src|dest pairs.
declare -a SRCS=() DESTS=()
while IFS= read -r line; do
    line="${line%%#*}"                        # strip trailing comments
    [ -z "${line// /}" ] && continue          # skip blank
    src="$(echo "${line%%|*}" | xargs)"       # trim
    dest="$(echo "${line##*|}" | xargs)"
    [ -z "$src" ] || [ -z "$dest" ] && continue
    SRCS+=("$src"); DESTS+=("$dest")
done < "$MANIFEST"

# Snapshot the live copy of each dest that currently exists.
for dest in "${DESTS[@]}"; do
    if [ -f "$MS_LIVE/$dest" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$dest")"
        cp -a "$MS_LIVE/$dest" "$BACKUP_DIR/$dest"
    fi
done
log "snapshot of current live files saved → $BACKUP_DIR"

# ── Place the new files (allowlist copy — never deletes) ─────────────────────
placed=0; skipped=0
for i in "${!SRCS[@]}"; do
    src="${SRCS[$i]}"; dest="${DESTS[$i]}"
    if [ -f "$MS_SRC/$src" ]; then
        mkdir -p "$MS_LIVE/$(dirname "$dest")"
        # write to a temp then mv = atomic replace, no half-written file served
        tmp="$MS_LIVE/$dest.deploy-tmp.$$"
        if cp -a "$MS_SRC/$src" "$tmp" && mv -f "$tmp" "$MS_LIVE/$dest"; then
            placed=$((placed+1))
        else
            rm -f "$tmp" 2>/dev/null || true
            warn "failed to place $src → $dest"
        fi
    else
        skipped=$((skipped+1))
    fi
done
log "placed $placed file(s); skipped $skipped missing source(s)."

# ── Bump the cache-buster ?v=N on the served index.html (monotonic) ──────────
# Browsers cache each ?v= URL as immutable, so a deploy only reaches users when
# the number changes. We read the number ALREADY LIVE and increment it, so it is
# always monotonic regardless of what value was committed in the HTML.
INDEX="$MS_LIVE/index.html"
if [ -f "$INDEX" ]; then
    # capture the previous live values from the snapshot (pre-overwrite)
    prev_index="$BACKUP_DIR/index.html"
    for asset in ms.js ms.css; do
        cur="$(grep -oE "${asset//./\\.}\?v=[0-9]+" "$INDEX" 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)"
        prevv=0
        [ -f "$prev_index" ] && prevv="$(grep -oE "${asset//./\\.}\?v=[0-9]+" "$prev_index" 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)"
        base=$(( cur > prevv ? cur : prevv ))
        next=$(( base + 1 ))
        sed -i -E "s/${asset//./\\.}\?v=[0-9]+/${asset//./\\.}?v=${next}/g" "$INDEX" 2>/dev/null \
            && log "cache-buster: ${asset}?v=${next}" \
            || warn "cache-buster bump failed for ${asset}"
    done
fi

# ── Restart services ─────────────────────────────────────────────────────────
# Redis is a standalone cache/rate-limit service and is intentionally NOT bounced
# on a code deploy (that would drop the session/rate-limit cache for no reason).
# The BEA's background jobs run as in-process threads, so restarting the app IS
# restarting the worker.
restart_ok=1
for svc in $MS_SERVICES; do
    if systemctl restart "$svc" >>"$MS_LOG" 2>&1; then
        log "restarted service: $svc"
    else
        warn "restart FAILED for service: $svc"
        restart_ok=0
    fi
done

# ── Reload nginx (cheap; config rarely changes on a code deploy) ─────────────
if command -v nginx >/dev/null 2>&1; then
    nginx -s reload >>"$MS_LOG" 2>&1 && log "nginx reloaded" || warn "nginx reload failed (non-fatal)"
fi

# ── Health check (retry — the app takes a few seconds to bind) ───────────────
healthy=0
for _ in $(seq 1 12); do
    body="$(curl -s -m 8 "$MS_HEALTH_URL" 2>/dev/null || true)"
    if echo "$body" | grep -q "$MS_HEALTH_OK"; then healthy=1; break; fi
    sleep 2
done

# ── Verdict / rollback ───────────────────────────────────────────────────────
if [ "$healthy" -eq 1 ] && [ "$restart_ok" -eq 1 ]; then
    echo "$TARGET_SHA" > "$STATE_FILE"
    # purge CDN (best-effort, non-fatal) now that the app is confirmed healthy
    if [ -n "$MS_ADMIN_KEY" ]; then
        curl -sf -m 20 -X POST -H "X-Admin-Key: $MS_ADMIN_KEY" "$MS_PURGE_URL" >/dev/null 2>&1 \
            && log "CDN purge requested" || warn "CDN purge failed (non-fatal)"
    else
        curl -sf -m 20 -X POST "$MS_PURGE_URL" >/dev/null 2>&1 \
            && log "CDN purge requested" || warn "CDN purge failed (non-fatal)"
    fi
    # prune old rollback snapshots
    if [ -d "$MS_LIVE/.deploy-backups" ]; then
        ls -1dt "$MS_LIVE"/.deploy-backups/*/ 2>/dev/null | tail -n +"$((MS_KEEP_BACKUPS+1))" \
            | xargs -r rm -rf 2>/dev/null || true
    fi
    # ── Post-deploy hook (2 Aug 2026, DEPLOY-CONSOLIDATION-1) ────────────────
    # Runs the repo's ops/autodeploy/post_deploy.sh (seed + one-time migrations)
    # AFTER the app is confirmed healthy. Non-fatal by design: the deploy is
    # already live; a hook problem is logged loudly, never rolls anything back.
    HOOK="$MS_SRC/ops/autodeploy/post_deploy.sh"
    if [ -f "$HOOK" ]; then
        log "post-deploy hook: running (seed + migrations)"
        if MS_SRC="$MS_SRC" MS_LIVE="$MS_LIVE" bash "$HOOK" >>"$MS_LOG" 2>&1; then
            log "post-deploy hook: ok"
        else
            warn "post-deploy hook reported a problem (deploy stays live) — read this log above."
        fi
    fi
    log "DEPLOY OK · now live at ${SHORT} · health ok"
    log "─────────────────────────────────────────────────────────────────────────"
    exit 0
fi

# ---- failure: roll back to the snapshot + previous commit -------------------
warn "deploy UNHEALTHY (health=$healthy restart_ok=$restart_ok) — rolling back to snapshot $TS"
rb_ok=1
for dest in "${DESTS[@]}"; do
    if [ -f "$BACKUP_DIR/$dest" ]; then
        mkdir -p "$MS_LIVE/$(dirname "$dest")"
        cp -a "$BACKUP_DIR/$dest" "$MS_LIVE/$dest" 2>>"$MS_LOG" || rb_ok=0
    fi
done
# put the source clone back to the previously-deployed commit (if we knew it)
if [ -n "$LAST_SHA" ]; then
    git -C "$MS_SRC" reset --hard "$LAST_SHA" >>"$MS_LOG" 2>&1 || rb_ok=0
fi
for svc in $MS_SERVICES; do
    systemctl restart "$svc" >>"$MS_LOG" 2>&1 || rb_ok=0
done
# confirm the rollback is healthy
rb_healthy=0
for _ in $(seq 1 12); do
    if curl -s -m 8 "$MS_HEALTH_URL" 2>/dev/null | grep -q "$MS_HEALTH_OK"; then rb_healthy=1; break; fi
    sleep 2
done

if [ "$rb_ok" -eq 1 ] && [ "$rb_healthy" -eq 1 ]; then
    log "ROLLBACK OK · restored previous release · health ok · target ${SHORT} was NOT applied"
    log "  (fix the bad commit, then re-publish the deploy ref to try again)"
    log "─────────────────────────────────────────────────────────────────────────"
    exit 2
fi

log "ROLLBACK FAILED — the site may be down. Human action needed."
log "  restore by hand:  cp -a $BACKUP_DIR/<file> $MS_LIVE/<file>  then  systemctl restart $MS_SERVICES"
log "─────────────────────────────────────────────────────────────────────────"
exit 3
}

main "$@"

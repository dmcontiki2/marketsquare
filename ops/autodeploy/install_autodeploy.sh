#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════════════
#  install_autodeploy.sh — ONE-TIME activation of the MarketSquare auto-deploy.
#
#  Run this ONCE on the Hetzner box (as root). It is idempotent — running it
#  again is safe and simply re-syncs the units. It:
#    1. clones the mirror to /opt/marketsquare-src  (source of truth for deploys)
#    2. installs the systemd service + timer
#    3. enables + starts the 2-minute poll timer
#    4. prints how to arm the first deploy and where the logs are
#
#  It deploys NOTHING by itself — the live site is only touched once the tracked
#  deploy ref (default: the 'deploy' branch) is published on the mirror.
#
#  This is the SINGLE manual step for David. After this, deploys are hands-free.
# ═════════════════════════════════════════════════════════════════════════════
set -euo pipefail

MS_SRC="${MS_SRC:-/opt/marketsquare-src}"
MS_REMOTE_URL="${MS_REMOTE_URL:-https://github.com/dmcontiki2/marketsquare.git}"
MS_DEPLOY_REF="${MS_DEPLOY_REF:-deploy}"
UNIT_DIR="/etc/systemd/system"

say() { echo "  $*"; }
hr()  { echo "────────────────────────────────────────────────────────────────────────"; }

hr
echo "  MarketSquare auto-deploy — installer"
hr

if [ "$(id -u)" -ne 0 ]; then
    echo "  ERROR: run as root (sudo). Needs to write $UNIT_DIR and clone to /opt." >&2
    exit 1
fi
command -v git >/dev/null 2>&1        || { echo "  ERROR: git not installed." >&2; exit 1; }
command -v systemctl >/dev/null 2>&1  || { echo "  ERROR: systemd not present." >&2; exit 1; }

# ── 1. Source clone ──────────────────────────────────────────────────────────
if [ -d "$MS_SRC/.git" ]; then
    say "[1/4] source clone already present at $MS_SRC — fetching latest"
    git -C "$MS_SRC" remote set-url origin "$MS_REMOTE_URL" 2>/dev/null || true
    git -C "$MS_SRC" fetch --quiet --prune origin || say "      (fetch failed — check network; continuing)"
else
    say "[1/4] cloning $MS_REMOTE_URL → $MS_SRC"
    mkdir -p "$(dirname "$MS_SRC")"
    git clone --quiet "$MS_REMOTE_URL" "$MS_SRC"
fi

SELF_DIR="$MS_SRC/ops/autodeploy"
if [ ! -f "$SELF_DIR/server_deploy.sh" ]; then
    echo "  ERROR: $SELF_DIR/server_deploy.sh not found in the clone." >&2
    echo "         The auto-deploy files must be committed to the mirror first." >&2
    exit 1
fi
chmod +x "$SELF_DIR/server_deploy.sh"

# ── 2. Install systemd units ─────────────────────────────────────────────────
say "[2/4] installing systemd units into $UNIT_DIR"
install -m 0644 "$SELF_DIR/marketsquare-deploy.service" "$UNIT_DIR/marketsquare-deploy.service"
install -m 0644 "$SELF_DIR/marketsquare-deploy.timer"   "$UNIT_DIR/marketsquare-deploy.timer"
systemctl daemon-reload

# ── 3. Enable + start the timer ──────────────────────────────────────────────
say "[3/4] enabling the 2-minute poll timer"
systemctl enable --now marketsquare-deploy.timer

# ── 4. Report ────────────────────────────────────────────────────────────────
say "[4/4] done. Status:"
echo
systemctl --no-pager status marketsquare-deploy.timer | sed 's/^/      /' || true
echo
hr
echo "  INSTALLED. The server now checks the mirror every 2 minutes."
echo
if git -C "$MS_SRC" rev-parse --verify --quiet "origin/${MS_DEPLOY_REF}^{commit}" >/dev/null; then
    echo "  The tracked deploy ref 'origin/${MS_DEPLOY_REF}' already exists — the next"
    echo "  tick will bring the live site to it (with health-check + auto-rollback)."
else
    echo "  ARM THE FIRST DEPLOY: publish the deploy ref once, from David's PC:"
    echo "      git push origin main:${MS_DEPLOY_REF}"
    echo "  (or run release.bat). After that, every future 'go live' is one push."
fi
echo
echo "  Logs:   tail -f /var/log/marketsquare-deploy.log"
echo "  Timer:  systemctl list-timers marketsquare-deploy.timer"
echo "  Off:    systemctl disable --now marketsquare-deploy.timer"
hr

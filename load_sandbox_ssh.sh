#!/bin/bash
# load_sandbox_ssh.sh
# Called by Claude at the start of every session to load the Hetzner SSH key
# into the sandbox's ~/.ssh folder.
#
# The key file (ssh_hetzner_key) lives in the MarketSquare project folder and
# is gitignored — it never gets committed to GitHub.

# Resolve path relative to this script's location — works regardless of session name
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY_SOURCE="$SCRIPT_DIR/ssh_hetzner_key"
KEY_DEST="$HOME/.ssh/id_ed25519"

if [ ! -f "$KEY_SOURCE" ]; then
    echo "ERROR: ssh_hetzner_key not found in project folder."
    echo "Run setup_sandbox_ssh.ps1 once from PowerShell to fix this."
    exit 1
fi

mkdir -p "$HOME/.ssh"
cp "$KEY_SOURCE" "$KEY_DEST"
chmod 600 "$KEY_DEST"

# --- Hetzner host + connection setup (so scheduled/unattended runs don't trip) ---
HOST="178.104.73.239"

# 1. Seed the server's host key so SSH won't fail with "Host key verification failed".
#    Idempotent: only add if not already present (avoids duplicate known_hosts lines).
touch "$HOME/.ssh/known_hosts"
if ! ssh-keygen -F "$HOST" >/dev/null 2>&1; then
    ssh-keyscan -H "$HOST" >> "$HOME/.ssh/known_hosts" 2>/dev/null
fi

# 2. Enable connection multiplexing so multi-call scripts (smoke_test.py opens
#    ~12 SSH connections) reuse one socket and finish within the shell timeout.
#    Idempotent: only append the Host block if it isn't already there.
mkdir -p "$HOME/.ssh/cm"
if ! grep -q "^Host $HOST\$" "$HOME/.ssh/config" 2>/dev/null; then
    cat >> "$HOME/.ssh/config" <<CFG_EOF
Host $HOST
    User root
    ControlMaster auto
    ControlPath ~/.ssh/cm/%r@%h:%p
    ControlPersist 300
    ServerAliveInterval 15
    StrictHostKeyChecking accept-new
CFG_EOF
    chmod 600 "$HOME/.ssh/config"
fi

echo "SSH key loaded into sandbox — Hetzner server accessible (host key seeded, multiplexing on)."

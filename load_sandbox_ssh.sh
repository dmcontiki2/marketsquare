#!/bin/bash
# load_sandbox_ssh.sh
# Called by Claude at the start of every session to load the Hetzner SSH key
# into the sandbox's ~/.ssh folder.
#
# The key file (ssh_hetzner_key) lives in the MarketSquare project folder and
# is gitignored — it never gets committed to GitHub.

KEY_SOURCE="/sessions/quirky-brave-galileo/mnt/MarketSquare/ssh_hetzner_key"
KEY_DEST="$HOME/.ssh/id_ed25519"

if [ ! -f "$KEY_SOURCE" ]; then
    echo "ERROR: ssh_hetzner_key not found in project folder."
    echo "Run setup_sandbox_ssh.ps1 once from PowerShell to fix this."
    exit 1
fi

mkdir -p "$HOME/.ssh"
cp "$KEY_SOURCE" "$KEY_DEST"
chmod 600 "$KEY_DEST"
echo "✅ SSH key loaded into sandbox — Hetzner server accessible."

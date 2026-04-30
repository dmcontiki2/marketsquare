# setup_sandbox_ssh.ps1
# Run this ONCE from PowerShell to copy your SSH key into the MarketSquare
# project folder so the Claude sandbox can use it in every future session.
#
# Usage:
#   cd C:\Users\David\Projects\MarketSquare
#   .\setup_sandbox_ssh.ps1

$sourceKey = "$env:USERPROFILE\.ssh\id_ed25519"
$destKey   = "$PSScriptRoot\ssh_hetzner_key"

if (-not (Test-Path $sourceKey)) {
    Write-Error "SSH key not found at $sourceKey - check your .ssh folder"
    exit 1
}

Copy-Item $sourceKey $destKey -Force
Write-Host "OK: Key copied to $destKey"
Write-Host "    Claude can now SSH to the Hetzner server directly from the sandbox."
Write-Host ""
Write-Host "NOTE: ssh_hetzner_key is in .gitignore - it will NOT be committed to GitHub."

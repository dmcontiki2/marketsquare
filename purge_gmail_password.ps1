$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\gmail_install_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== PURGE run $(Get-Date -Format s) =====")
& scp -q "scripts\purge_gmail_password.py" "${srv}:/tmp/purge_gmail_password.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/purge_gmail_password.py; rm -f /tmp/purge_gmail_password.py" 2>&1 | ForEach-Object { Say $_ }
Say ""; Say "  Done - Claude reads the log directly."
Read-Host "  Press Enter to close"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\inbound_fix_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== place inbound secrets $(Get-Date -Format s) =====")
& scp -q "scripts\place_inbound_secrets.py" "${srv}:/tmp/place_inbound_secrets.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/place_inbound_secrets.py; rm -f /tmp/place_inbound_secrets.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

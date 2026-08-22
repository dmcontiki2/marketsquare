$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\demand_fix_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== fix demand.conf $(Get-Date -Format s) =====")
& scp -q "scripts\fix_demand_from.py" "${srv}:/tmp/fix_demand_from.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/fix_demand_from.py; rm -f /tmp/fix_demand_from.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\lanes_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== lane check $(Get-Date -Format s) =====")
& scp -q "scripts\check_all_lanes.py" "${srv}:/tmp/check_all_lanes.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/check_all_lanes.py; rm -f /tmp/check_all_lanes.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

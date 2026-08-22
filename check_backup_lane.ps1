$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\lanes_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== backup lane check $(Get-Date -Format s) =====")
& scp -q "scripts\check_backup_lane.sh" "${srv}:/tmp/check_backup_lane.sh" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "bash /tmp/check_backup_lane.sh; rm -f /tmp/check_backup_lane.sh" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

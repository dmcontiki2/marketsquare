$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\inbound_fix_log2.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== verify inbound auth $(Get-Date -Format s) =====")
& scp -q "scripts\verify_inbound_auth.py" "${srv}:/tmp/verify_inbound_auth.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/verify_inbound_auth.py; rm -f /tmp/verify_inbound_auth.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

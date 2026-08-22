$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\cf_token_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== verify CF token $(Get-Date -Format s) =====")
& scp -q "scripts\verify_cf_token.py" "${srv}:/tmp/verify_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/verify_cf_token.py; rm -f /tmp/verify_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\cf_token_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== RESTORE CF token $(Get-Date -Format s) =====")
& scp -q "scripts\restore_cf_token.py" "${srv}:/tmp/restore_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/restore_cf_token.py; rm -f /tmp/restore_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

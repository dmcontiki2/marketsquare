$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\cf_token_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== trace CF_CACHE_TOKEN $(Get-Date -Format s) =====")
& scp -q "scripts\diag_env_var.py" "${srv}:/tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/diag_env_var.py CF_CACHE_TOKEN; rm -f /tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

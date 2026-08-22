$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\catalog_keys_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== catalogue key presence $(Get-Date -Format s) =====")
& scp -q "scripts\diag_env_var.py" "${srv}:/tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
Say "--- NUMISTA_API_KEY ---"
& ssh $srv "python3 /tmp/diag_env_var.py NUMISTA_API_KEY" 2>&1 | ForEach-Object { Say $_ }
Say "--- JUSTTCG_API_KEY ---"
& ssh $srv "python3 /tmp/diag_env_var.py JUSTTCG_API_KEY; rm -f /tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

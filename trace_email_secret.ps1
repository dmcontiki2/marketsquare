$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\inbound_fix_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== trace EMAIL_INBOUND_SECRET $(Get-Date -Format s) =====")
& scp -q "scripts\diag_env_var.py" "${srv}:/tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/diag_env_var.py EMAIL_INBOUND_SECRET; echo '--- secrets.env keys (names only) ---'; grep -o '^[A-Z_]*=' /etc/marketsquare/secrets.env 2>/dev/null | tr -d '='; echo '--- demand.conf line 5 context ---'; sed -n '1,8p' /etc/systemd/system/marketsquare.service.d/demand.conf | sed 's/=.*@/=<redacted>@/'; rm -f /tmp/diag_env_var.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

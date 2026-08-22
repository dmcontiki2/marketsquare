$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\anthropic_install_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== identify burnt key $(Get-Date -Format s) =====")
& scp -q "scripts\find_old_anthropic_key.sh" "${srv}:/tmp/find_old_anthropic_key.sh" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "bash /tmp/find_old_anthropic_key.sh; rm -f /tmp/find_old_anthropic_key.sh" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

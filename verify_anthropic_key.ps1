$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\anthropic_install_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== post-deletion verify $(Get-Date -Format s) =====")
& scp -q "scripts\verify_anthropic_key.py" "${srv}:/tmp/verify_anthropic_key.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/verify_anthropic_key.py; rm -f /tmp/verify_anthropic_key.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

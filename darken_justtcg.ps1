$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\catalog_keys_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== darken JustTCG $(Get-Date -Format s) =====")
& scp -q "scripts\darken_justtcg.py" "${srv}:/tmp/darken_justtcg.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/darken_justtcg.py; rm -f /tmp/darken_justtcg.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Read-Host "  Press Enter to close"

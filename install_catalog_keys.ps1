$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\catalog_keys_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== run $(Get-Date -Format s) =====")
Write-Host ""
Write-Host "  Paste the NEW keys. Press Enter alone to SKIP either one."
Write-Host "  Neither is stored on this PC or shown to Claude."
Write-Host ""
$n = (Read-Host "  NUMISTA key (Enter to skip)") -replace '\s',''
$j = (Read-Host "  JUSTTCG key (Enter to skip)") -replace '\s',''
if ($n -eq '') { $n = '-' } else { Say ("  numista key: {0} chars" -f $n.Length) }
if ($j -eq '') { $j = '-' } else { Say ("  justtcg key: {0} chars" -f $j.Length) }
if ($n -eq '-' -and $j -eq '-') { Say "  nothing entered - nothing sent."; Read-Host "  Press Enter to close"; exit 1 }
Say "  [OK] shipping."
& scp -q "scripts\install_catalog_keys.py" "${srv}:/tmp/install_catalog_keys.py" 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Say "  [X] could not reach the server"; Read-Host "  Press Enter to close"; exit 1 }
& ssh $srv "python3 /tmp/install_catalog_keys.py '$n' '$j'; rm -f /tmp/install_catalog_keys.py" 2>&1 | ForEach-Object { Say $_ }
Say ""; Say "  Done - Claude reads .secrets\catalog_keys_log.txt directly."
Read-Host "  Press Enter to close"

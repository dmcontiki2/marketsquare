# diag_gmail.ps1 - read-only Gmail check. APPENDS to a log Claude can read.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\gmail_diag_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""
Say ("===== run $(Get-Date -Format s) =====")
& scp -q "scripts\diag_gmail.py" "${srv}:/tmp/diag_gmail.py" 2>&1 | ForEach-Object { Say $_ }
& ssh $srv "python3 /tmp/diag_gmail.py; rm -f /tmp/diag_gmail.py" 2>&1 | ForEach-Object { Say $_ }
Say ""
Say "  Done - Claude reads .secrets\gmail_diag_log.txt directly, nothing to paste."
Read-Host "  Press Enter to close"

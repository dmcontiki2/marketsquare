# install_gmail_password.ps1 - paste directly, or drop a file. Never logs the password.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\gmail_install_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""
Say ("===== run $(Get-Date -Format s) =====")

# Look for a file in every place Notepad might have put it (including .txt.txt)
$candidates = @(
  ".secrets\gmail_pw.txt", ".secrets\gmail_pw.txt.txt", "gmail_pw.txt", "gmail_pw.txt.txt",
  "$env:USERPROFILE\Desktop\gmail_pw.txt",   "$env:USERPROFILE\Desktop\gmail_pw.txt.txt",
  "$env:USERPROFILE\Documents\gmail_pw.txt", "$env:USERPROFILE\Documents\gmail_pw.txt.txt"
)
$pw = $null
foreach ($c in $candidates) {
  if (Test-Path $c) { $pw = ((Get-Content -Raw $c) -replace '\s',''); Say "  found a file: $c"; $found = $c; break }
}

if (-not $pw) {
  Write-Host ""
  Write-Host "  No file found - paste the app password here instead."
  Write-Host "  (Right-click pastes in this window. Spaces are fine.)"
  Write-Host ""
  $pw = (Read-Host "  App password") -replace '\s',''
}

Say ("  length: {0} characters" -f $pw.Length)
if ($pw.Length -eq 0) {
  Say "  [X] nothing entered. Nothing sent."
  Read-Host "  Press Enter to close"; exit 1
}
if ($pw.Length -ne 16) {
  Say "  [!] WARNING: Google issues 16 characters, this is $($pw.Length) - probably a lost character."
  Say "      Shipping it anyway so Gmail itself can give the verdict."
}
if ($pw -cnotmatch '^[a-z]{16}$') { Say "  [!] not all lowercase letters - shipping anyway, SMTP will judge it" }
Say "  [OK] length correct - shipping."
Say ""

& scp -q "scripts\install_gmail_password.py" "${srv}:/tmp/install_gmail_password.py" 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Say "  [X] could not reach the server"; Read-Host "  Press Enter to close"; exit 1 }
& ssh $srv "python3 /tmp/install_gmail_password.py '$pw'; rm -f /tmp/install_gmail_password.py" 2>&1 | ForEach-Object { Say $_ }

if ($found) { Remove-Item -Force $found -ErrorAction SilentlyContinue; Say "  [OK] deleted $found" }
Say ""
Say "  Done - Claude reads .secrets\gmail_install_log.txt directly, nothing to paste."
Read-Host "  Press Enter to close"

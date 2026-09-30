@echo off
REM ============================================================================
REM  add_sms_key.bat -- SMS-DAILY-CAP-1 / PHONE-KEY-1 (David, 30 Sep 2026)
REM  Puts the BulkSMS API token on the server so Quick can send phone sign-in codes.
REM  You type the Token ID and Token Secret here; the secret is never echoed, never
REM  on a command line, never in git, never in chat. It travels to the server over
REM  ssh's stdin and is appended to /etc/marketsquare/secrets.env ONLY if no SMS_TOKEN
REM  is there yet (run it twice and the second run changes nothing).
REM  Also writes SMS_DAILY_CAP=40: at most 40 SMS a day across the whole server.
REM  Then restarts the app and prints sms_ready (expect True).
REM ============================================================================
setlocal EnableExtensions
echo(
echo   BulkSMS: Settings - API Tokens - Create Token. Keep that page open.
echo   Paste the Token ID, Enter; then the Token Secret, Enter. The secret is not shown.
echo(
powershell -NoProfile -ExecutionPolicy Bypass -Command "$id = (Read-Host '  Token ID').Trim(); $s = Read-Host -AsSecureString '  Token Secret'; $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try { $sec = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b).Trim() } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) }; if ($id.Length -eq 0 -or $sec.Length -eq 0) { Write-Host '  ABORTED - empty input, nothing sent.'; exit 1 }; if ($id -notmatch '^[A-Za-z0-9_-]+$') { Write-Host '  ABORTED - the Token ID has unexpected characters.'; exit 1 }; $p = [char]10 + 'SMS_PROVIDER=bulksms' + [char]10 + 'SMS_TOKEN=' + $id + ':' + $sec + [char]10 + 'SMS_DAILY_CAP=40'; $sec = $null; $p | ssh root@178.104.73.239 'grep -q ^SMS_TOKEN= /etc/marketsquare/secrets.env && echo ALREADY-PRESENT-nothing-changed || (cat >> /etc/marketsquare/secrets.env && echo ADDED && systemctl restart marketsquare && sleep 5)'; $p = $null; [GC]::Collect(); if ($LASTEXITCODE -ne 0) { exit 1 }"
if errorlevel 1 (
  echo(
  echo   Something failed - see the lines above. Nothing else was changed.
  echo(
  pause
  exit /b 1
)
echo(
echo   Checking the live site (expect sms_ready True):
powershell -NoProfile -Command "try { $d = Invoke-RestMethod https://trustsquare.co/quick/me; Write-Host ('  sms_ready = ' + $d.sms_ready) } catch { Write-Host '  could not reach trustsquare.co' }"
echo(
echo   Done. Tell Claude: SMS key is in.
echo(
pause
endlocal

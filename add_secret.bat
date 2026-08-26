@echo off
REM ============================================================================
REM  add_secret.bat -- David pastes a secret into .secrets\<name>.txt WITHOUT it
REM  ever appearing on screen, in a screenshot, in a chat, or in a scrollback.
REM
REM  WHY THIS EXISTS (SECRET-ONSCREEN-1, 26 Aug 2026)
REM  7 Aug 2026 fixed one direction: rotate_secrets.py PRINTS NO VALUES, because a
REM  diagnostic dumped the production set into a transcript. That rule held.
REM  26 Aug 2026 the OTHER direction failed: Claude asked David to open Notepad to
REM  paste a Hetzner token, Notepad restored its previous tab -- .secrets\
REM  rotated_secrets.txt, the post-rotation set in plaintext -- and Claude's
REM  screenshot captured five live self-issued credentials.
REM
REM  The lesson is not "be careful with Notepad". It is: SECRET ENTRY MUST NEVER
REM  REQUIRE A GUI, because a GUI requires Claude to look at the screen, and
REM  looking at the screen is the exposure. This is the no-GUI path.
REM
REM  USAGE:  add_secret.bat hetzner_token
REM          (then paste at the prompt and press Enter -- nothing echoes)
REM
REM  Prints ONLY: the file path, the byte count, and a short sha256 fingerprint,
REM  so Claude can verify the secret landed and matches later WITHOUT ever
REM  learning the value. Never prints the secret. Never takes an argument
REM  containing the secret (that would put it in your command history).
REM ============================================================================
setlocal
if "%~1"=="" (
  echo(
  echo   Usage: add_secret.bat ^<name^>
  echo   Example: add_secret.bat hetzner_token   -^> .secrets\hetzner_token.txt
  echo(
  exit /b 1
)

set "NAME=%~1"
set "PROJECT=%~dp0"
set "TARGET=%PROJECT%.secrets\%NAME%.txt"

if not exist "%PROJECT%.secrets" mkdir "%PROJECT%.secrets"

if exist "%TARGET%" (
  echo(
  echo   NOTE: %NAME%.txt already exists. A timestamped .bak is kept before overwriting.
)

echo(
echo   Paste the value for [%NAME%] and press Enter.
echo   Nothing will be echoed. Nothing will be printed back.
echo(

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$t='%TARGET%';" ^
  "if (Test-Path -LiteralPath $t) { Copy-Item -LiteralPath $t -Destination ($t + '.bak-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) -Force };" ^
  "$s = Read-Host -AsSecureString '  value';" ^
  "$b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s);" ^
  "try { $v = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) };" ^
  "$v = $v.Trim();" ^
  "if ($v.Length -eq 0) { Write-Host '  ABORTED - empty input, file unchanged.'; exit 1 };" ^
  "[IO.File]::WriteAllText($t, $v, (New-Object Text.UTF8Encoding $false));" ^
  "$h = (Get-FileHash -LiteralPath $t -Algorithm SHA256).Hash.Substring(0,8).ToLower();" ^
  "Write-Host '';" ^
  "Write-Host ('  WROTE : ' + $t);" ^
  "Write-Host ('  BYTES : ' + $v.Length);" ^
  "Write-Host ('  FPRINT: sha256:' + $h + '  (safe to quote to Claude)');" ^
  "Write-Host '';" ^
  "$v = $null; [GC]::Collect()"

if errorlevel 1 (
  echo   Nothing was written.
  exit /b 1
)

echo   Done. .secrets\ is gitignored ^(.gitignore:141^) so this never reaches git.
echo(
endlocal

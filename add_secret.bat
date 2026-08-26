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
REM  BAT-CRLF-1 / BAT-FLICKER-1 (26 Aug 2026) -- WHY THIS FILE WAS REWRITTEN.
REM  The first version flickered on and off when David ran it and did nothing.
REM  THREE faults, each alone enough to make it vanish unreadably:
REM    1. LF line endings (the repo's .gitattributes forced eol=lf on everything).
REM       cmd.exe expects CRLF; a caret continuation followed by a bare LF does
REM       NOT continue the line, so the 15-caret PowerShell block was mangled.
REM    2. Caret continuations at all -- fragile for exactly that reason. The
REM       PowerShell call is now ONE line and cannot be broken by line endings.
REM    3. No PAUSE on any exit path, and an instant exit when double-clicked with
REM       no argument. Every failure closed the window before it could be read.
REM  A script David runs BY HAND must never close without saying why.
REM
REM  USAGE:  add_secret.bat hetzner_token        (or just double-click it)
REM          then paste at the prompt and press Enter -- nothing echoes
REM
REM  Prints ONLY: the file path, the byte count, and a short sha256 fingerprint,
REM  so Claude can verify the secret landed and matches later WITHOUT ever
REM  learning the value. Never prints the secret. Never takes an argument
REM  containing the secret (that would put it in your command history).
REM ============================================================================
setlocal EnableExtensions

set "PROJECT=%~dp0"
set "NAME=%~1"

REM Double-clicked from Explorer? ASK, never exit silently.
if "%NAME%"=="" (
  echo(
  echo   Which secret? ^(name only, no value^)
  echo   e.g.  hetzner_token   cf_waf_token   tp_token
  echo(
  set /p "NAME=  name: "
)
if "%NAME%"=="" (
  echo(
  echo   No name given -- nothing was written.
  echo(
  pause
  exit /b 1
)

REM Name validation lives in the PowerShell call below, NOT here. A `echo %NAME%|`
REM pipe would put a variable on the command line, and ledger RG-0189 rightly refuses
REM any echoed variable in this file -- the guard cannot tell a harmless name from a
REM secret, so the rule is absolute and the echo goes rather than the assertion.

set "TARGET=%PROJECT%.secrets\%NAME%.txt"
if not exist "%PROJECT%.secrets" mkdir "%PROJECT%.secrets"

if exist "%TARGET%" (
  echo(
  echo   NOTE: %NAME%.txt already exists. A timestamped .bak is kept, but ONLY
  echo         once you have actually entered a value ^(an abort leaves it alone^).
)

echo(
echo   Paste the value for [%NAME%] and press Enter.
echo   Nothing will be echoed. Nothing will be printed back.
echo(

REM ONE line, no caret continuations -- see BAT-FLICKER-1 above. The backup is
REM taken AFTER a non-empty value is confirmed, so an aborted run no longer
REM leaves another .bak credential copy lying under .secrets\ (RG-0189's drift).
powershell -NoProfile -ExecutionPolicy Bypass -Command "$n='%NAME%'; if ($n -notmatch '^[A-Za-z0-9_-]+$') { Write-Host '  Invalid name - letters, digits, underscore and hyphen only.'; exit 1 }; $t='%TARGET%'; $s = Read-Host -AsSecureString '  value'; $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try { $v = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) }; $v = $v.Trim(); if ($v.Length -eq 0) { Write-Host '  ABORTED - empty input, file unchanged.'; exit 1 }; if (Test-Path -LiteralPath $t) { Copy-Item -LiteralPath $t -Destination ($t + '.bak-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) -Force }; [IO.File]::WriteAllText($t, $v, (New-Object Text.UTF8Encoding $false)); $h = (Get-FileHash -LiteralPath $t -Algorithm SHA256).Hash.Substring(0,8).ToLower(); Write-Host ''; Write-Host ('  WROTE : ' + $t); Write-Host ('  BYTES : ' + $v.Length); Write-Host ('  FPRINT: sha256:' + $h + '  (safe to quote to Claude)'); Write-Host ''; $v = $null; [GC]::Collect()"

if errorlevel 1 (
  echo(
  echo   Nothing was written.
  echo(
  pause
  exit /b 1
)

echo   Done. .secrets\ is gitignored ^(.gitignore:141^) so this never reaches git.
echo(
pause
endlocal

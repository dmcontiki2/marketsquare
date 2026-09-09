@echo off
setlocal
:: sandbox_repair.bat - SANDBOX-REPAIR-1 stage 1 = DIAGNOSE (9 Sep 2026)
:: The Cowork Linux command sandbox on David's PC fails every command with
::   "sandbox-helper: no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared"
:: (the Windows drive share into the Linux VM was never attached). PROVEN 9 Sep:
::   - WSL is NOT installed on this PC; the sandbox is the app's own Hyper-V (HCS) VM.
::   - A full Claude app restart (21:11) does NOT cure it - the VM outlives the app.
::   - Cause class: Windows update KB5124008 (claude-code #92984). Only removing the KB
::     restores the shares - that is David's decision, never queued.
:: This stage only records the facts (read-only). Both the queue's 4000-char tail AND a full
:: copy in host_queue\done\sandbox_diag_<stamp>.txt, because the tail cuts the head off.
:: Runs HOST-SIDE via the host queue (RUL-095). Touches nothing in the repo, DBs or server.
set STAMP=%DATE:~-4%%DATE:~-7,2%%DATE:~-10,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set STAMP=%STAMP: =0%
set OUT=%~dp0host_queue\done\sandbox_diag_%STAMP%.txt
echo === SANDBOX-REPAIR-1 stage 1 (diagnose)  %DATE% %TIME%
echo user=%USERNAME%   full copy: %OUT%
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sandbox_repair_diag.ps1" > "%OUT%" 2>&1
type "%OUT%"
echo.
echo === STAGE 1 done at %TIME%. Read the full copy above; act on the CAUSE it shows (CLAUDE.md, SANDBOX-REPAIR-1).
exit /b 0

# ledger_rows.ps1 - SANDBOX-REPAIR-1 (10 Sep 2026).
# Prints the rows of a regression-ledger board that need a human eye, WITH the whole of each
# row's detail. Born from a near-miss the same night: ledger_host.bat used
#   findstr /C:"           REGRESSION:"
# which matches line by line, so a multi-line FAIL detail printed only its FIRST line. The
# 05:54 board's RG-0194 row showed a caret WARNING and silently dropped the line under it --
# "FAIL remove_kb5124008.bat has LF-only line endings", the one script whose whole job is to
# get the sandbox back. An instrument that truncates its own evidence hides exactly the fault
# it was built to surface. Reads a board file, prints nothing else, changes nothing.
param([Parameter(Mandatory = $true)][string]$Board)
if (-not (Test-Path $Board)) { Write-Output "board file not found: $Board"; exit 0 }
$emit = $false
foreach ($l in Get-Content -LiteralPath $Board) {
    if ($l -match '^\[\s*(!!!!|LOCK|\?\?\?\?)\s*\]') { $emit = $true; Write-Output $l; continue }
    if ($l -match '^\[') { $emit = $false; continue }          # a row that is merely ok
    if (-not $emit) { continue }
    if ($l -match '^\s+(fixed \d|scope:)') { continue }        # the entry's own prose header
    if ($l.Trim() -eq '') { continue }
    Write-Output $l
}

# kb_fix.ps1 - remove KB5124008, and RECORD EVERYTHING.
#
# Third attempt. The two batch versions failed silently: one hid the error with
# /quiet, the other crashed before writing anything and the window vanished.
# PowerShell is used here because Start-Transcript captures the whole session to
# a file no matter what happens - including a crash. Nothing can disappear.
#
# Read-only until step 3; step 3 is the only thing that changes the PC.

$ErrorActionPreference = 'Continue'
$report = Join-Path $PSScriptRoot 'host_queue\done\kb_removal_report.txt'
New-Item -ItemType Directory -Force -Path (Split-Path $report) | Out-Null
Start-Transcript -Path $report -Force | Out-Null

function Say($t) { Write-Host "`n=== $t ===" }

Say "WHEN"
Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
"Windows: " + (Get-CimInstance Win32_OperatingSystem).Caption
"Build:   " + (Get-CimInstance Win32_OperatingSystem).Version + " / " +
    (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').UBR
"Admin:   " + ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Say "1 of 4 - is KB5124008 installed?"
$hf = Get-HotFix -Id KB5124008 -ErrorAction SilentlyContinue
if ($hf) { $hf | Format-List HotFixID, InstalledOn, Description | Out-String }
else     { "NOT listed as installed." }

Say "2 of 4 - what packages match, and can they be removed?"
$pkgs = @(Get-WindowsPackage -Online -ErrorAction SilentlyContinue |
          Where-Object { $_.PackageName -match 'RollupFix|LanguageFeatures-Basic' -or
                         $_.PackageName -match '26200' })
if (-not $pkgs) { "No candidate packages found." }
foreach ($p in $pkgs) {
    $d = Get-WindowsPackage -Online -PackageName $p.PackageName -ErrorAction SilentlyContinue
    "{0}`n    state={1}  removable={2}  installed={3}" -f `
        $p.PackageName, $p.PackageState, $d.Removable, $d.InstallTime
}

Say "3 of 4 - attempt removal"
if (-not $hf) {
    "Nothing to remove - it is not installed."
} else {
    "--- try A: wusa (often refuses on Windows 11 cumulative updates) ---"
    $w = Start-Process wusa.exe -ArgumentList '/uninstall','/kb:5124008','/norestart' `
         -Wait -PassThru
    "wusa exit code = $($w.ExitCode)   (0=accepted  87=wrong tool  2359303=not permitted)"

    if ($w.ExitCode -ne 0) {
        "--- try B: DISM (the supported route) ---"
        $target = $pkgs | Where-Object { $_.PackageName -match 'RollupFix' } |
                  Sort-Object PackageName -Descending | Select-Object -First 1
        if (-not $target) {
            "No RollupFix package found to remove."
        } else {
            "Removing: $($target.PackageName)"
            try {
                Remove-WindowsPackage -Online -PackageName $target.PackageName `
                    -NoRestart -ErrorAction Stop | Out-Null
                "DISM reported success."
            } catch {
                "DISM FAILED: $($_.Exception.Message)"
            }
        }
    }
}

Say "4 of 4 - will a restart actually achieve anything?"
$pending = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
if ($pending) { ">> YES - a change is staged. RESTART NOW." }
else          { ">> NO - nothing is staged. A restart will change nothing. Do NOT restart." }

Say "FALLBACK - system restore points available"
$rp = Get-ComputerRestorePoint -ErrorAction SilentlyContinue
if ($rp) { $rp | Select-Object SequenceNumber, Description, CreationTime | Format-Table | Out-String }
else     { "None found (System Protection may be off)." }

Say "DONE"
"Report saved to: $report"
Stop-Transcript | Out-Null

Write-Host "`nThis window stays open. Press Enter when you have finished reading."
Read-Host

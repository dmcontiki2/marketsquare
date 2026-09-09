# sandbox_repair_diag.ps1 - SANDBOX-REPAIR-1 diagnostics (9 Sep 2026)
# Prints what the Cowork sandbox VM is made of, so the repair can target the VM rather than the
# app. Read-only: it changes nothing. Called by sandbox_repair.bat and by
# sandbox_repair_restart_app.bat (before the restart).
# PROVEN 9 Sep 21:11: the VM is a Host Compute Service (Hyper-V) VM - vmcompute.exe / vmwp.exe /
# vmmem - and it SURVIVED a full Claude app restart, still broken. WSL is off on this PC.
$me = (Get-Process -Id $PID).SessionId
$cl = @(Get-Process claude -ErrorAction SilentlyContinue)
$clSess = if ($cl.Count -gt 0) { $cl[0].SessionId } else { 'none' }
Write-Output ("my session={0}  claude processes={1}  claude session={2}" -f $me, $cl.Count, $clSess)
if ($cl.Count -gt 0) { Write-Output ("claude path: " + $cl[0].Path) }
Write-Output "--- Windows build + the September 2026 updates (KB5124008 breaks Cowork Plan9 shares: claude-code #92984) ---"
try {
    $cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    Write-Output ("windows {0} build {1}.{2} ({3})" -f $cv.DisplayVersion, $cv.CurrentBuild, $cv.UBR, $cv.ProductName)
} catch { Write-Output ("build query failed: " + $_.Exception.Message) }
try {
    Get-HotFix -ErrorAction Stop | Sort-Object InstalledOn -Descending | Select-Object -First 6 | ForEach-Object {
        $d = if ($_.InstalledOn) { $_.InstalledOn.ToString('yyyy-MM-dd') } else { '?' }
        '   {0,-12} {1,-18} installed={2}' -f $_.HotFixID, $_.Description, $d
    }
    $kb = Get-HotFix -Id KB5124008 -ErrorAction SilentlyContinue
    Write-Output ("KB5124008 installed: " + $(if ($kb) { 'YES (' + $kb.InstalledOn.ToString('yyyy-MM-dd') + ')' } else { 'no' }))
} catch { Write-Output ("hotfix query failed: " + $_.Exception.Message) }
foreach ($f in @("$env:SystemRoot\System32\vmcompute.exe", "$env:SystemRoot\System32\vmwp.exe", "$env:SystemRoot\System32\drivers\p9rdr.sys", "$env:SystemRoot\System32\p9np.dll")) {
    if (Test-Path $f) { $v = (Get-Item $f).VersionInfo; Write-Output ('   {0,-16} {1}' -f (Split-Path $f -Leaf), $v.FileVersion) }
}
Write-Output "--- Cowork VM logs: last lines about Plan9 shares ---"
$logs = @("$env:LOCALAPPDATA\Claude\Logs\cowork_vm_node.log", "C:\ProgramData\Claude\Logs\cowork-service.log")
$logs += @(Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'Claude_*' } | ForEach-Object { Join-Path $_.FullName 'LocalCache\Local\Claude\Logs\cowork_vm_node.log' })
$logs += @(Get-ChildItem "C:\ProgramData\Claude\Logs\coworkd" -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
foreach ($lg in $logs) {
    if (-not (Test-Path $lg)) { continue }
    Write-Output ("log: " + $lg + "  (" + (Get-Item $lg).LastWriteTime.ToString('yyyy-MM-dd HH:mm') + ")")
    Select-String -Path $lg -Pattern 'Plan9|plan9|HcsModifyComputeSystem|VM started|shares' -ErrorAction SilentlyContinue | Select-Object -Last 6 | ForEach-Object {
        $l = $_.Line -replace '\s+', ' '
        if ($l.Length -gt 220) { $l = $l.Substring(0, 220) + '...' }
        Write-Output ('   ' + $_.LineNumber + '  ' + $l)
    }
}
Write-Output "--- elevation ---"
$wi = [Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = (New-Object Security.Principal.WindowsPrincipal $wi).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Output ("user={0}  admin token={1}" -f $wi.Name, $isAdmin)
Write-Output "--- VM processes (Host Compute Service) with start time ---"
Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(vmcompute|vmwp|vmmem|vmmemWSL|vmmemCmZygote)' } | ForEach-Object {
    $t = if ($_.CreationDate) { $_.CreationDate.ToString('yyyy-MM-dd HH:mm:ss') } else { '?' }
    '{0,6}  {1,-14} started={2}' -f $_.ProcessId, $_.Name, $t
}
Write-Output "--- hcsdiag list (Host Compute Service systems) ---"
try {
    $out = & "$env:SystemRoot\System32\hcsdiag.exe" list 2>&1
    $out | ForEach-Object { [string]$_ } | Select-Object -First 20
} catch { Write-Output ("hcsdiag failed: " + $_.Exception.Message) }
Write-Output "--- claude.exe processes by type ---"
Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | ForEach-Object {
    $c = [string]$_.CommandLine
    $t = if ($c -match '--type=(\S+)') { $Matches[1] } else { 'main' }
    $u = if ($c -match '--utility-sub-type=(\S+)') { $Matches[1] } else { '' }
    '{0,6}  parent={1,-6} type={2} {3}' -f $_.ProcessId, $_.ParentProcessId, $t, $u
}
Write-Output "--- Hyper-V / hypervisor platform state ---"
try {
    $f = Get-CimInstance -ClassName Win32_OptionalFeature -Filter "Name='Microsoft-Hyper-V' OR Name='HypervisorPlatform' OR Name='VirtualMachinePlatform' OR Name='Microsoft-Windows-Subsystem-Linux'" -ErrorAction Stop
    $f | ForEach-Object { '{0,-40} state={1}' -f $_.Name, $(if ($_.InstallState -eq 1) { 'ENABLED' } else { 'off' }) }
} catch { Write-Output "optional-feature query failed: $($_.Exception.Message)" }
Write-Output "--- Claude app data: folders that look like the sandbox (depth 3) ---"
$pkg = Join-Path $env:LOCALAPPDATA 'Packages'
$roots = @(Get-ChildItem $pkg -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'Claude_*' } | ForEach-Object { $_.FullName })
$roots += @((Join-Path $env:APPDATA 'Claude'), (Join-Path $env:LOCALAPPDATA 'Claude'), (Join-Path $env:LOCALAPPDATA 'AnthropicClaude'))
foreach ($r in $roots) {
    if (-not (Test-Path $r)) { continue }
    Write-Output ("root: " + $r)
    Get-ChildItem $r -Directory -Recurse -Depth 3 -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'vm|sandbox|linux|cowork|virt|rootfs|hcs' } | Select-Object -First 15 | ForEach-Object { '   ' + $_.FullName.Substring($r.Length) }
}
Write-Output "--- recent *.log lines mentioning the drive share (last 24h, first 12 hits, 200 chars each; transcripts excluded) ---"
$hits = 0
foreach ($r in $roots) {
    if (-not (Test-Path $r)) { continue }
    Get-ChildItem $r -Recurse -Depth 4 -File -Include *.log -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) -and $_.Length -lt 20MB } |
        ForEach-Object {
            $f = $_
            Select-String -Path $f.FullName -Pattern 'Plan9|plan9|9p share|virtiofs|sandbox-helper|drive share' -ErrorAction SilentlyContinue |
                Select-Object -Last 4 | ForEach-Object {
                    if ($hits -lt 12) {
                        $l = $_.Line -replace '\s+', ' '
                        if ($l.Length -gt 200) { $l = $l.Substring(0, 200) + '...' }
                        Write-Output ('   ' + $f.Name + ':' + $_.LineNumber + '  ' + $l)
                        $hits++
                    }
                }
        }
}
if ($hits -eq 0) { Write-Output "   (no matching log lines found)" }

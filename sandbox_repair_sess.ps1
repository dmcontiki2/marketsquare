# sandbox_repair_sess.ps1 - SANDBOX-REPAIR-1 (9 Sep 2026). Prints ONE line: "<my session id> <claude session id|none>"
# so sandbox_repair_restart_app.bat can refuse to restart the app onto a desktop nobody sees.
$me = (Get-Process -Id $PID).SessionId
$cl = @(Get-Process claude -ErrorAction SilentlyContinue)
$clSess = if ($cl.Count -gt 0) { $cl[0].SessionId } else { 'none' }
Write-Output ("{0} {1}" -f $me, $clSess)

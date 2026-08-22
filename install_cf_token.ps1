$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\cf_token_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== run $(Get-Date -Format s) =====")
Write-Host ""
Write-Host "  Paste the NEW Cloudflare cache-purge token (right-click pastes)."
Write-Host "  Never stored on this PC, never shown to Claude."
Write-Host ""
$t = (Read-Host "  CF token") -replace '\s',''
Say ("  length: {0} characters" -f $t.Length)
# Character profile - tells us WHAT was pasted without revealing it.
$lower = ($t.ToCharArray() | Where-Object { $_ -cmatch '[a-z]' }).Count
$upper = ($t.ToCharArray() | Where-Object { $_ -cmatch '[A-Z]' }).Count
$digit = ($t.ToCharArray() | Where-Object { $_ -match '[0-9]' }).Count
$other = ($t.ToCharArray() | Where-Object { $_ -notmatch '[a-zA-Z0-9]' })
$otherSet = ($other | Sort-Object -Unique) -join ''
Say ("  profile: {0} lowercase, {1} uppercase, {2} digits, {3} other [{4}]" -f $lower, $upper, $digit, $other.Count, $otherSet)
# NOTE 22 Aug 2026: do NOT assert a token length. Cloudflare issues 53-character
# tokens on this account; an earlier "40 characters" claim was wrong and sent David
# back three times to re-copy a value that was correct every time. The only verdict
# that counts is the real purge call the server-side script makes.
if ($t.Length -eq 32) { Say "  [!] 32 characters - that is Account-ID shaped, not a token. Check before continuing." }
if ($t.Length -lt 20) { Say "  [X] too short to be a Cloudflare token - nothing sent."; Read-Host "  Press Enter to close"; exit 1 }
Say "  [OK] shipping."
& scp -q "scripts\install_cf_token.py" "${srv}:/tmp/install_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Say "  [X] could not reach the server"; Read-Host "  Press Enter to close"; exit 1 }
& ssh $srv "python3 /tmp/install_cf_token.py '$t'; rm -f /tmp/install_cf_token.py" 2>&1 | ForEach-Object { Say $_ }
Say ""; Say "  Done - Claude reads .secrets\cf_token_log.txt directly."
Read-Host "  Press Enter to close"

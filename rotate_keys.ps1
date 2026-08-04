# rotate_keys.ps1 — one command, three keys, automatic rollback.
#
# Written 5 Aug 2026 after Claude's own diagnostic command printed the server's whole
# environment into a chat transcript. Rotating by hand is eleven fiddly steps where a
# wrong sed breaks the unit file and takes the site down; this does the mechanical part
# once, verifies the site is healthy, and puts everything back if it is not.
#
#   .\rotate_keys.ps1
#
# It rotates ONLY the three server-side keys — MS_ADMIN_KEY, MS_DEPLOY_KEY, MS_MAINT_KEY.
# It deliberately does NOT touch:
#   FOUNDERS_ID_SALT     rotating invalidates every founder ID already minted
#   LAUNCH_CODE_SECRET   shared with CityLauncher; both ends must change together
#   MS_API_KEY           already public in ms.js by design
#   MS_ADMIN_PASSWORD    your call, and only matters if it is reused elsewhere
# Vendor keys (Resend, Cloudflare, Travelpayouts, Numista, JustTCG) need their own
# dashboards and cannot be scripted.
#
# Nothing is printed except status lines. The new values never appear on screen.

$ErrorActionPreference = "Stop"
$server = "root@178.104.73.239"
$stamp  = Get-Date -Format "yyyyMMdd-HHmmss"

function Say($m) { Write-Host "  $m" }
Write-Host "`n  KEY ROTATION  $stamp" -ForegroundColor Cyan
Write-Host "  ---------------------------------------------"

# ── 1. new values, generated locally, never displayed ───────────────────────
$admin = python -c "import secrets; print('msq_admin_' + secrets.token_hex(20))"
$deploy = python -c "import secrets; print('msq_deploy_' + secrets.token_hex(20))"
if (Test-Path .secrets\ms_maint_key.txt) {
    $maint = (Get-Content .secrets\ms_maint_key.txt -Raw).Trim()
    Say "maintenance key: reusing the one already generated ($($maint.Length) chars)"
} else {
    $maint = python -c "import secrets; print('ms_maint_' + secrets.token_urlsafe(32))"
    Say "maintenance key: generated"
}
if (-not $admin -or -not $deploy -or -not $maint) { throw "key generation failed - nothing was changed" }
Say "new admin + deploy keys generated"

# ── 2. build the remote script LOCALLY, then send it ────────────────────────
#     (project rule: never pass a script inline over ssh - write it, copy it, run it)
$sh = @"
#!/bin/bash
set -u
UNIT=`$(systemctl show -p FragmentPath --value marketsquare)
[ -f "`$UNIT" ] || { echo "ROTATE_FAILED unit file not found"; exit 1; }
BAK="`$UNIT.bak-rotate-$stamp"
cp "`$UNIT" "`$BAK"

# drop any existing line for the three keys, in either quoting style
sed -i '/^Environment=.*MS_ADMIN_KEY=/d;  /^Environment=.*MS_DEPLOY_KEY=/d;  /^Environment=.*MS_MAINT_KEY=/d' "`$UNIT"
# and add them back, once each, immediately under [Service]
sed -i '/^\[Service\]/a Environment=MS_ADMIN_KEY=$admin\nEnvironment=MS_DEPLOY_KEY=$deploy\nEnvironment=MS_MAINT_KEY=$maint' "`$UNIT"

systemctl daemon-reload
systemctl restart marketsquare
sleep 5

HEALTH=`$(curl -sf --max-time 8 http://localhost:8000/health || echo FAIL)
SEEN=`$(tr '\0' '\n' < /proc/`$(systemctl show -p MainPID --value marketsquare)/environ | grep -c '^MS_MAINT_KEY=' || true)

if echo "`$HEALTH" | grep -q '"status":"ok"' && [ "`$SEEN" = "1" ]; then
  echo "ROTATE_OK backup=`$BAK"
else
  cp "`$BAK" "`$UNIT"
  systemctl daemon-reload
  systemctl restart marketsquare
  sleep 4
  echo "ROTATE_FAILED rolled back health=`$HEALTH maint_seen=`$SEEN"
fi
"@
$tmp = "$env:TEMP\rotate_$stamp.sh"
$sh -replace "`r`n", "`n" | Out-File -Encoding ascii -NoNewline $tmp
Say "rotation script built"

# ── 3. run it on the server ─────────────────────────────────────────────────
scp -q $tmp "${server}:/tmp/rotate.sh" | Out-Null
$result = ssh $server "bash /tmp/rotate.sh; rm -f /tmp/rotate.sh"
Remove-Item $tmp -Force
Say "server says: $result"

# ── 4. only write the new values locally once the server is proven healthy ──
if ($result -match "ROTATE_OK") {
    if (Test-Path .secrets\deploy_keys.txt) {
        Copy-Item .secrets\deploy_keys.txt ".secrets\deploy_keys.txt.bak-$stamp"
    }
    "MS_ADMIN_KEY=$admin`nMS_DEPLOY_KEY=$deploy" | Out-File -Encoding ascii .secrets\deploy_keys.txt
    $maint | Out-File -Encoding ascii -NoNewline .secrets\ms_maint_key.txt
    Say "local .secrets updated (old copy kept as .bak-$stamp)"

    $k = $maint
    $probe = curl.exe -s -o NUL -w "%{http_code}" -H "X-Maint-Key: $k" "https://trustsquare.co/admin/faults?limit=1"
    Say "live check: /admin/faults with the new maintenance key -> HTTP $probe"
    Write-Host "`n  DONE. Site healthy, keys rotated, maintenance lane " -NoNewline -ForegroundColor Green
    if ($probe -eq "200") { Write-Host "OPEN." -ForegroundColor Green } else { Write-Host "still closed (HTTP $probe) - tell Claude." -ForegroundColor Yellow }
} else {
    Write-Host "`n  NOTHING CHANGED. The server rolled itself back and is running the old keys." -ForegroundColor Yellow
    Write-Host "  Your local .secrets files were not touched. Paste the line above to Claude." -ForegroundColor Yellow
}
Write-Host ""

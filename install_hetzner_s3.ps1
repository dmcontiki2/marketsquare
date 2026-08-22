$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$log = Join-Path $root ".secrets\hetzner_s3_log.txt"
$srv = "root@178.104.73.239"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
Say ""; Say ("===== run $(Get-Date -Format s) =====")
Write-Host ""
Write-Host "  Paste the new CLOUDFLARE R2 credentials."
Write-Host "  (The variables are NAMED HETZNER_S3_* for historical reasons, but the"
Write-Host "   endpoint is r2.cloudflarestorage.com - R2 is what they authenticate to.)"
Write-Host "  Neither value is stored on this PC or shown to Claude."
Write-Host ""
$ak = (Read-Host "  ACCESS KEY") -replace '\s',''
$sk = (Read-Host "  SECRET KEY") -replace '\s',''
Say ("  access key: {0} chars | secret key: {1} chars" -f $ak.Length, $sk.Length)
if ($ak.Length -lt 8 -or $sk.Length -lt 8) { Say "  [X] one of those is too short - nothing sent."; Read-Host "  Press Enter to close"; exit 1 }
if ($ak.Length -eq 20) {
  Say "  [X] a 20-character access key is a HETZNER credential. This lane talks to"
  Say "      Cloudflare R2, which issues 32-character Access Key IDs. Nothing sent -"
  Say "      get the pair from Cloudflare: R2 > Manage R2 API Tokens > Object Read & Write."
  Read-Host "  Press Enter to close"; exit 1
}
if ($ak.Length -ne 32) { Say "  [!] R2 access keys are normally 32 characters, this is $($ak.Length) - shipping anyway, the S3 call will judge it" }
Say "  [OK] shipping."
& scp -q "scripts\install_hetzner_s3.py" "${srv}:/tmp/install_hetzner_s3.py" 2>&1 | ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Say "  [X] could not reach the server"; Read-Host "  Press Enter to close"; exit 1 }
& ssh $srv "python3 /tmp/install_hetzner_s3.py '$ak' '$sk'; rm -f /tmp/install_hetzner_s3.py" 2>&1 | ForEach-Object { Say $_ }
Say ""; Say "  Done - Claude reads .secrets\hetzner_s3_log.txt directly."
Read-Host "  Press Enter to close"

param(
  [Parameter(Mandatory=$true)][string]$LocalDir,
  [Parameter(Mandatory=$true)][string]$Filter,
  [Parameter(Mandatory=$true)][string]$RemoteDir,
  [Parameter(Mandatory=$true)][string]$Server
)
# ============================================================
#  sync_assets.ps1  (22 Jul 2026, ASSET-SYNC)
#  Replaces bulk "scp *.jpg / *.mp4 every deploy" with a hash
#  sync: one ssh call reads remote md5sums, only NEW or CHANGED
#  files upload. Unchanged deploys skip ~570MB of re-upload.
#  Exit 0 = in sync (incl. nothing to do). Exit 1 = failure.
# ============================================================
$ErrorActionPreference = 'Continue'

$files = @(Get-ChildItem -LiteralPath $LocalDir -Filter $Filter -File -ErrorAction SilentlyContinue)
$label = Split-Path $LocalDir -Leaf
if ($files.Count -eq 0) {
  Write-Host ("   [SYNC] {0}: no local files match {1} - nothing to do." -f $label, $Filter)
  exit 0
}

# One ssh round-trip: ensure the dir exists AND read remote hashes.
$remoteOut = ssh -n -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 $Server "mkdir -p $RemoteDir && md5sum $RemoteDir/* 2>/dev/null; true"
if ($LASTEXITCODE -ne 0) {
  Write-Host ("   [FAIL] SYNC {0}: cannot reach server to read remote hashes." -f $label)
  exit 1
}

$remote = @{}
foreach ($line in @($remoteOut)) {
  if ($line -match '^([0-9a-fA-F]{32})\s+(.+)$') {
    $name = [System.IO.Path]::GetFileName($Matches[2].Trim())
    $remote[$name] = $Matches[1].ToLower()
  }
}

$toSend = @()
foreach ($f in $files) {
  $h = (Get-FileHash -Algorithm MD5 -LiteralPath $f.FullName).Hash.ToLower()
  if ($remote[$f.Name] -ne $h) { $toSend += $f }
}

if ($toSend.Count -eq 0) {
  Write-Host ("   [OK] SYNC {0}: all {1} files already current - upload skipped." -f $label, $files.Count)
  exit 0
}

Write-Host ("   [SYNC] {0}: {1} of {2} files new/changed - uploading only those..." -f $label, $toSend.Count, $files.Count)
foreach ($f in $toSend) { Write-Host ("       up: " + $f.Name) }
$paths = @($toSend | ForEach-Object { $_.FullName })
scp -q $paths ("{0}:{1}/" -f $Server, $RemoteDir)
if ($LASTEXITCODE -ne 0) {
  Write-Host ("   [FAIL] SYNC {0}: scp upload failed. Check SSH connection." -f $label)
  exit 1
}
Write-Host ("   [OK] SYNC {0}: {1} file(s) uploaded." -f $label, $toSend.Count)
exit 0

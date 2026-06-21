<#
  MarketSquare laptop backup -> Hetzner Object Storage bucket (restic, S3). Weekly, automatic.
  Secrets are loaded from OUTSIDE the repo: %USERPROFILE%\.marketsquare-backup\laptop.env.ps1
  Run by Task Scheduler (weekly). Dedup + prune keep storage bounded.
#>
$ErrorActionPreference = 'Stop'

# --- secrets (repo URL + S3 keys + restic password), kept out of git ---
$cfg = "$env:USERPROFILE\.marketsquare-backup\laptop.env.ps1"
if (-not (Test-Path $cfg)) { Write-Error "Missing config: $cfg"; exit 2 }
. $cfg

# --- locate restic (known winget path first; search as fallback if it updates) ---
$restic = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\restic.restic_Microsoft.Winget.Source_8wekyb3d8bbwe\restic_0.19.0_windows_amd64.exe"
if (-not (Test-Path $restic)) {
  $restic = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages","C:\Program Files\WinGet" -Recurse -Filter "restic*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $restic) { Write-Error "restic.exe not found"; exit 3 }

$Source = 'C:\Users\David\Projects'
$LogDir = "$env:USERPROFILE\.marketsquare-backup\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir ("backup-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

try {
  "[start] $(Get-Date) using $restic" | Tee-Object $Log -Append
  & $restic backup $Source `
      --exclude "**/node_modules" --exclude "**/__pycache__" --exclude "**/.venv" `
      --exclude "**/_ARCHIVE/installers/**" *>> $Log
  if ($LASTEXITCODE -ne 0) { throw "restic backup failed ($LASTEXITCODE)" }

  "[prune] keep 8 weekly / 12 monthly" | Tee-Object $Log -Append
  & $restic forget --prune --keep-weekly 8 --keep-monthly 12 *>> $Log
  if ($LASTEXITCODE -ne 0) { throw "restic forget failed ($LASTEXITCODE)" }

  "[ok] $(Get-Date)" | Tee-Object $Log -Append
}
catch {
  "[FAILED] $_" | Tee-Object $Log -Append
  try { [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');
        [System.Windows.Forms.MessageBox]::Show("MarketSquare weekly backup FAILED. See $Log","Backup failed") } catch {}
  exit 1
}
finally {
  $env:RESTIC_PASSWORD=$null; $env:AWS_SECRET_ACCESS_KEY=$null
}

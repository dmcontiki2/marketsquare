<#
  MarketSquare laptop backup — backs up C:\Users\David\Projects nightly to the SAME
  Hetzner Storage Box used by the server, but a SEPARATE encrypted repo (/restic-laptop),
  so the box holds: server data, AND your laptop working files (code, videos, docs).

  restic = encrypted, deduplicated, incremental. Your Projects folder (~2.2 GB) backs up
  small after the first run because restic only stores what changed.

  Deploy: keep this script under C:\Users\David\Projects\MarketSquare\ops\backup\windows\
  Config: C:\Users\David\.marketsquare-backup\laptop.env.ps1 (NOT in git)
  Schedule: Task Scheduler (see SETUP_WINDOWS.md)
#>

$ErrorActionPreference = 'Stop'

# ---- load config (paths + secrets kept OUTSIDE the repo) ----
$cfg = "$env:USERPROFILE\.marketsquare-backup\laptop.env.ps1"
if (-not (Test-Path $cfg)) { Write-Error "Missing config: $cfg  (copy laptop.env.example.ps1 there and fill it in)"; exit 2 }
. $cfg   # defines $StorageBoxRepo, $ResticPassword, $SshUser/$SshHost handled via ~/.ssh/config

$env:RESTIC_REPOSITORY = $StorageBoxRepo          # e.g. sftp:u123456@u123456.your-storagebox.de:/restic-laptop
$env:RESTIC_PASSWORD   = $ResticPassword

$Source   = 'C:\Users\David\Projects'
$LogDir   = "$env:USERPROFILE\.marketsquare-backup\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir ("backup-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

function Log($m){ $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m; $line | Tee-Object -FilePath $Log -Append }

try {
  Log "=== Laptop backup start ==="
  Log "Source: $Source  ->  $StorageBoxRepo"

  # init repo once (ignore 'already initialized')
  & restic snapshots *> $null
  if ($LASTEXITCODE -ne 0) { Log "Initializing repo"; & restic init }

  # exclude regenerable / noise; keep .git (small, also your local history safety net)
  $excludes = @(
    '--exclude', '**/node_modules',
    '--exclude', '**/__pycache__',
    '--exclude', '**/.venv',
    '--exclude', '**/*.pyc',
    '--exclude', '**/.DS_Store',
    '--exclude', '**/Thumbs.db'
  )

  Log "Backing up..."
  & restic backup --tag laptop-nightly $excludes "$Source"
  if ($LASTEXITCODE -ne 0) { throw "restic backup failed ($LASTEXITCODE)" }

  Log "Applying retention (7 daily / 4 weekly / 6 monthly)"
  & restic forget --prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6
  if ($LASTEXITCODE -ne 0) { throw "restic forget failed ($LASTEXITCODE)" }

  Log "Structural check"
  & restic check
  if ($LASTEXITCODE -ne 0) { throw "restic check failed ($LASTEXITCODE)" }

  Log "=== Laptop backup OK ==="
}
catch {
  Log "FAILED: $_"
  # Optional desktop toast so a failed backup doesn't pass silently:
  try { [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');
        [System.Windows.Forms.MessageBox]::Show("MarketSquare laptop backup FAILED. See $Log","Backup failed") } catch {}
  exit 1
}
finally {
  $env:RESTIC_PASSWORD = $null
}

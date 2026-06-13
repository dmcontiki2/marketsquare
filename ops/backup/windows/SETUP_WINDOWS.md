# Laptop backup — Windows setup (C:\Users\David\Projects → Storage Box)

Backs up your whole Projects folder nightly to the **same Hetzner Storage Box** as the server, in a **separate encrypted repo** (`/restic-laptop`). Result: the Storage Box holds both your live server data *and* your laptop working files (code, the videos, scripts, docs) — independent of your laptop, GitHub, or the CPX22.

> Why this matters: GitHub holds your *code*, but not the big media (videos) or uncommitted work. This catches everything in the Projects folder, encrypted, off-machine.

## One-time setup

### 1. Install the tools (PowerShell, as admin)
```powershell
winget install restic.restic
winget install Microsoft.OpenSSH.Client   # usually already present on Win10/11
restic version
ssh -V
```

### 2. SSH key so the laptop can reach the Storage Box (port 23)
```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519 -N '""'
# upload the PUBLIC key to the Storage Box:
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -p 23 u123456@u123456.your-storagebox.de install-ssh-key
```
Create `C:\Users\David\.ssh\config` (so restic's sftp uses port 23 + the key):
```
Host u123456.your-storagebox.de
    Port 23
    User u123456
    IdentityFile C:\Users\David\.ssh\id_ed25519
```
Test: `ssh u123456@u123456.your-storagebox.de "echo box-ok"` → should print `box-ok`.

### 3. Config file (outside the repo)
```powershell
mkdir $env:USERPROFILE\.marketsquare-backup
copy ops\backup\windows\laptop.env.example.ps1 $env:USERPROFILE\.marketsquare-backup\laptop.env.ps1
notepad $env:USERPROFILE\.marketsquare-backup\laptop.env.ps1   # set repo URL + password
```
Generate a password: `[Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))` — and store it offline.

### 4. First run
```powershell
powershell -ExecutionPolicy Bypass -File ops\backup\windows\backup-projects.ps1
restic -r sftp:u123456@u123456.your-storagebox.de:/restic-laptop snapshots   # confirm a snapshot exists
```

### 5. Schedule nightly (Task Scheduler)
Run once, as admin:
```powershell
$action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\David\Projects\MarketSquare\ops\backup\windows\backup-projects.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 1:30AM
$set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -RunOnlyIfNetworkAvailable
Register-ScheduledTask -TaskName 'MarketSquare Laptop Backup' -Action $action -Trigger $trigger `
  -Settings $set -RunLevel Highest -Description 'Nightly Projects backup to Hetzner Storage Box'
```
`-StartWhenAvailable` means if the laptop was off at 01:30 it runs at next opportunity. Check it: `Get-ScheduledTask -TaskName 'MarketSquare Laptop Backup'`.

## Restore
```powershell
$env:RESTIC_REPOSITORY='sftp:u123456@u123456.your-storagebox.de:/restic-laptop'
$env:RESTIC_PASSWORD='...'
restic snapshots
restic restore latest --target C:\Restore           # everything
restic restore latest --target C:\Restore --include 'C:\Users\David\Projects\MarketSquare\ms.js'   # one file
```

## Monthly drill
Restore `latest` to a throwaway folder, open a couple of files (a video, ms.js), confirm they're intact, delete the folder. A backup you've never restored isn't yet a backup.

## How the two backups relate
- **Server** (`ops/backup/marketsquare-backup.*`): live app + SQLite + Redis + media → 100GB drive + Storage Box `/restic-marketsquare`.
- **Laptop** (this): Projects folder → Storage Box `/restic-laptop`.
- Same Storage Box, two repos. One ~€3.80/mo box covers both with room to spare.

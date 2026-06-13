# Laptop backup config — copy to:  %USERPROFILE%\.marketsquare-backup\laptop.env.ps1
# Keep this OUT of git (it holds the encryption password). The folder above is outside the repo.

# Same Storage Box as the server, but a SEPARATE repo path so laptop & server don't mix:
$StorageBoxRepo = 'sftp:u123456@u123456.your-storagebox.de:/restic-laptop'

# Encryption password for this repo. You may reuse the server's restic password or use a new one.
# Store it offline too (password manager) — without it the backup cannot be restored.
$ResticPassword = 'CHANGE-ME-long-random-string'

# MarketSquare nightly backup — setup runbook

Two independent copies every night, encrypted, with one-command restore:
- **Tier 1** — the extra **100GB drive** on your CPX22 (fast local restore).
- **Tier 2** — a separate **Hetzner Storage Box** (survives loss of the whole server/account).

Tool: **restic** — encrypted, deduplicated, incremental. Your data (SQLite + Redis + media + configs) is ~1–2 GB, so each nightly run after the first is tiny and fast, and months of history stay within a few GB.

> Why not the 100GB drive alone? It lives on the same server. If the VM dies, the account is suspended, or the region has an incident, you lose the live data **and** that backup together. The Storage Box is the independence that makes this a real 3-2-1 setup (3 copies, 2 media, 1 off-site).

---

## One-time setup

### 1. Mount the 100GB drive (if not already)
```bash
lsblk                                   # find the device, e.g. /dev/sdb
sudo mkfs.ext4 /dev/sdb                 # ONLY if it's blank/new
sudo mkdir -p /mnt/backup100
echo '/dev/sdb /mnt/backup100 ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
sudo mount -a && df -h /mnt/backup100
```

### 2. Order a Hetzner Storage Box
Hetzner Robot/Cloud console → Storage Box → **BX11** (1 TB, ~€3.80/mo is ample). Then in its web UI enable **"SSH support"** and note the host/user (e.g. `u123456.your-storagebox.de`, user `u123456`).

Give the server passwordless SSH to the box:
```bash
ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""      # if you don't already have a key
# add the PUBLIC key to the Storage Box (paste into its web UI, or):
cat /root/.ssh/id_ed25519.pub | ssh -p 23 u123456@u123456.your-storagebox.de install-ssh-key
ssh -p 23 u123456@u123456.your-storagebox.de "echo box-ok"   # should print box-ok
```
> Storage Box SSH/SFTP uses **port 23**. The restic SFTP URL handles this if you add a tiny `~/.ssh/config` entry:
> ```
> Host u123456.your-storagebox.de
>     Port 23
>     User u123456
>     IdentityFile /root/.ssh/id_ed25519
> ```

### 3. Install restic + sqlite
```bash
sudo apt-get update && sudo apt-get install -y restic sqlite3
restic version
```

### 4. Configure
```bash
sudo cp ops/backup/backup.env.example /etc/marketsquare-backup.env
sudoedit /etc/marketsquare-backup.env        # fill REAL paths, Storage Box URL, and a password
sudo chmod 600 /etc/marketsquare-backup.env
openssl rand -base64 32                       # generate RESTIC_PASSWORD; paste it in
```
**Write the restic password somewhere offline too (password manager / paper).** Lose it and the backups are unrecoverable — that is the point of encryption.

Set `SQLITE_DB` to the real database path. Find it if unsure:
```bash
find /var/www/marketsquare -maxdepth 3 -name '*.db' -o -name '*.sqlite*' 2>/dev/null
```

### 5. Install the script + timer
```bash
sudo install -m 750 ops/backup/marketsquare-backup.sh /usr/local/sbin/marketsquare-backup.sh
sudo cp ops/backup/marketsquare-backup.service /etc/systemd/system/
sudo cp ops/backup/marketsquare-backup.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now marketsquare-backup.timer
```

### 6. First run + verify
```bash
sudo systemctl start marketsquare-backup.service      # run once now
journalctl -u marketsquare-backup.service -n 60 --no-pager
sudo systemctl list-timers marketsquare-backup.timer  # confirm next run scheduled
```

---

## Restore (when you need it)
```bash
source /etc/marketsquare-backup.env; export RESTIC_PASSWORD
export RESTIC_REPOSITORY="$LOCAL_RESTIC_REPO"     # or "$STORAGEBOX_RESTIC_REPO"
restic snapshots                                  # list backups
restic restore latest --target /tmp/restore       # full restore
# or pull a single file:
restic restore latest --target /tmp/restore --include /var/www/marketsquare/marketsquare.db
```

## Monthly drill (do not skip)
```bash
sudo ops/backup/restore-test.sh /etc/marketsquare-backup.env box   # test the OFF-SERVER copy
```
This restores the latest Storage Box snapshot to a temp dir and runs a SQLite integrity check. A backup you have never restored is not yet a backup.

---

## What's covered / not
**Covered:** SQLite DB (online-safe copy + integrity-checked), Redis snapshot, the app dir (html/js/css/python), uploaded media, nginx + systemd unit, optional n8n data.
**Deliberately not in here:** secrets like the restic password and Paystack live keys — keep those in your password manager. The script never logs them.
**Not a substitute for git:** your *source code* history still belongs on GitHub; this protects the *running system's data*. The two are complementary.

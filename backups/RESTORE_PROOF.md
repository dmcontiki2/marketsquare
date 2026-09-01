# Backup RESTORE PROOF log (append-only)

Each entry: a dated proof that a specific archive was EXTRACTED and the restored DB passed PRAGMA integrity_check. Written by the session that ran the test; asserted every ledger run by RG-0234.

## 2026-09-01 — archive 2026-09-01_0653.zip
- restored from archive to temp, PRAGMA integrity_check: ok
- rows: users=70, listings=113
- source: live DB snapshot via sqlite3 -readonly .backup on the box, md5-matched after scp

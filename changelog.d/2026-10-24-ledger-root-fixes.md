## 2026-10-24 — Seven ledger reds fixed at the root (BACKUP-DAILY-1, DEPLOY-SYNC-1, SHIP-AND-SEE-1, RETIRE-AWARE-1, LEG-DEPS-1)

- RG-0234 backups 12 days stale -> BACKUP-DAILY-1: the 20-min host queue tick takes a backup once the newest archive is 20 h old (scripts/host_queue_worker.py daily_backup; backup_db_sandbox.py now Windows-safe). Backup 2026-10-24_1211 taken and restore-proven (users 234). RG-1102.
- RG-0344 email view stale (twice today) + RG-0154 session counter behind -> DEPLOY-SYNC-1: request_deploy.py rebuilds the Ops Email Templates view (adding any new letter's manifest row) and recomputes the session counter before every deploy, committing only those outputs. RG-1103.
- RG-0418 new sports_club letter missing from the CityLauncher deploy -> EMAIL-SHIP-ALL-1: deploy_citylauncher.bat ships every *.v2.html by glob, never a hand list. RG-1104.
- RG-0254 'No module named dotenv' read as a regression -> LEG-DEPS-1: in-process legs use _leg_broke() (missing third-party = NOT EVALUATED, missing own module = FAIL); maint_deps installs python-dotenv. RG-1104.
- RG-0248 resend_human_clicks.py 'gone' -> RETIRE-AWARE-1: it was retired on purpose in the 22 Oct CityLauncher review; the entry now recognises a deliberate retirement (_retired/) and still fails if a file is simply gone.

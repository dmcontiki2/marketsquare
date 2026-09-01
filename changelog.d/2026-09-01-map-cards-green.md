## 2026-09-01 — MAP-CARDS-1: the coverage board's last blues retired (attended map-fix pass)

David's ask: "fix the map coverage cards you can." Three non-green cards fixed, one deferred.

- **DW-088 CLOSED** — FEA baseline refreshed on-box after deploy_drift read clean 19/19; re-probe status ok, alerts [], stale notes gone. Structural fix (deploy engine refreshes its own baseline post-drift-clean) stays on tonight's CTO list.
- **RG-0233 NEW (LOCKED)** — DEPLOY-ENGINE-ASSERT-1: placement asserted every run — report parses, ref=deploy, no non-ok step, and origin/deploy may never sit >45 min ahead of the report (published-but-unplaced detection). Proven red-capable before green was believed.
- **RG-0234 NEW (LOCKED)** — BACKUP-RESTORE-ASSERT-1: the ledger itself EXTRACTS the newest backups/*.zip and integrity-checks the restored DB every run, plus freshness (<=8d) and dated RESTORE_PROOF (<=35d). The lane was found 27 days stale; refreshed with a live snapshot (sqlite3 -readonly .backup, md5-matched), archived 2026-09-01_0653.zip, restore-proven (ok, users=70, listings=113), proof logged in Backups/RESTORE_PROOF.md.
- Coverage map: **57 green · 0 blue · 1 amber · 0 red · 10 grey** — ZERO BLUE for the first time. Remaining amber: RG-0075 (admin-gate script x5 copies — refactor + deploy, tonight's discussion).
- Ledger after: 227 entries · 208 holding · 0 REGRESSED · exit 0. Mirror push from sandbox failed (no GitHub credential — host lanes carry it); mirror 1 commit behind until the next host push.

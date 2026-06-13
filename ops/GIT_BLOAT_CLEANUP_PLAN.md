# Git repository slim-down plan

## Diagnosis (measured 2026-06-13)
`.git` is ~1.1 GB. Breakdown of largest content in history:

| What | In history |
|------|-----------|
| `Kronberg/` apartment media (extension-less images) | ~593 MB |
| `.MOV` videos (mostly under `Kronberg/`) | ~293 MB |
| `.HEIC` photos | ~74 MB |
| `.html` (churn across many `marketsquare.html` versions) | ~112 MB |
| `.md`, `.js`, `.py`, `.jpg` | ~150 MB combined |

**Conclusion:** ~960 MB — the overwhelming majority — is the **Kronberg apartment media** (the breach/evidence files). That material is legal documentation, not application source. It does not belong in the app's version control; it belongs in the backup (Storage Box / Object Storage). The code/text churn is secondary and not worth a risky rewrite on its own.

---

## Do this FIRST (safe, non-destructive): commit today's pending work
This captures the work without rewriting anything. It deliberately keeps large video binaries OUT of git (they go to backup/Object Storage instead).

```bash
cd /path/to/MarketSquare

# 1) stop new big binaries entering git (append the additions — see ops/gitignore-additions.txt)
cat ops/gitignore-additions.txt >> .gitignore

# 2) stage code/text + the new ops/ backup system + heritage scripts (NOT the .mp4s)
git add .gitignore ops/ \
        BACKLOG.md CHANGELOG.md STATUS.md \
        marketsquare.html ms.css ms.js \
        Records/COST_SWEEP_2026-06-13.md \
        feature-videos/*.md feature-videos/02-heritage/*.md feature-videos/02-heritage/**/*.md

git status        # review — confirm no .mp4 / .MOV / large media staged
git commit -m "Backup system (restic 2-tier) + heritage video scripts + S138 checkpoint"
git push origin main
```
The finished video MP4s are protected by the nightly backup (and, once set up, Object Storage) — not by GitHub, on purpose.

---

## Then (optional, higher-effort): purge the heavy media from history
This **rewrites history** — every commit SHA changes — so it needs care and coordination. Only do it when you have a quiet window and can update every clone.

### Guardrails before you start
- This repo deploys via **scp**, not `git pull`, so the live server is unaffected by a history rewrite. Good.
- Coordinate with your multi-agent workflow: after the rewrite, **every working copy must be re-cloned** (old clones have the old history and will fight a force-push).
- **Make a full mirror backup of the repo first** (below). If anything goes wrong, you restore the mirror.

### Steps
```bash
# 0) install the tool
pipx install git-filter-repo   # or: pip install --user git-filter-repo

# 1) SAFETY: full mirror backup of the repo as-is
git clone --mirror https://github.com/dmcontiki2/marketsquare.git ms-mirror-backup.git
tar czf ms-mirror-backup-$(date +%F).tar.gz ms-mirror-backup.git   # keep this somewhere safe

# 2) work on a fresh mirror
git clone --mirror https://github.com/dmcontiki2/marketsquare.git ms-clean.git
cd ms-clean.git

# 3) drop the heavy material from ALL history
git filter-repo --force \
  --path Kronberg/ --invert-paths \
  --path-glob '*.MOV' --invert-paths \
  --path-glob '*.HEIC' --invert-paths \
  --path-glob '*.mp4'  --invert-paths

# 4) check the new size
du -sh .            # expect a few hundred MB -> tens of MB

# 5) push the rewritten history (force)
git remote add origin https://github.com/dmcontiki2/marketsquare.git
git push --force --mirror origin
```

### After the rewrite
- On your laptop and every agent machine: **delete the old clone and re-clone fresh.** Do not `git pull` an old clone.
- Confirm the Kronberg media is safely in the backup (Storage Box) BEFORE relying on the slimmed repo — once purged from history, git is no longer its home.
- GitHub keeps old objects server-side for a while; they age out, or contact support to expedite if you want the storage reclaimed immediately.

> If a full history rewrite feels too heavy, the lighter alternative is **git-lfs**: migrate the big types to LFS going forward and stop new bloat, accepting that existing history stays large. The filter-repo route is the only way to actually shrink the existing 1.1 GB.

---

## Keep it from recurring
The `.gitignore` additions (see `ops/gitignore-additions.txt`) block videos, raw camera media (`.MOV`, `.HEIC`), and the `feature-videos` MP4s from re-entering the repo. Big media → backup + Object Storage. Source/text → git.

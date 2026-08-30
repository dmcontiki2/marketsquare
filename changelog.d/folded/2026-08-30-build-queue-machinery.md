## 2026-08-30 — BUILD-QUEUE-1: the to-be-built board, derived not remembered

David asked how the piled-up design additions don't get forgotten. Answer made visible:
scripts/build_queue.py derives BUILD_QUEUE.md + build_queue.html (color-coded board,
Visuals-indexed) from the regression ledger's OPEN entries — single source, no parallel
list, regenerated on demand; a built item turns READY TO LOCK green and leaves on
promotion. Probed live: 18 OPEN entries = the real queue. Same run caught and fixed two
things before Monday's launch: a stranded .git/HEAD.lock (RG-0015/0197 red — healed via
git_unlock.py rename) and sandbox fastapi/httpx missing (RG-0181/0182 NOT EVALUATED —
installed; ledger now exits 0, "every locked fix is holding"). Weekly forcing function:
scheduled task build-queue-pickup (Wed 08:00) regenerates the board and names the next
build (first up post-launch: RG-0216 FIDE-CLAIM-1, then RG-0205/6/7 per RUL-065).

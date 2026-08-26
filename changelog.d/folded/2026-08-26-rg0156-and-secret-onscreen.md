## 2026-08-26 — RG-0156 orchestrator LOCKED · SECRET-ONSCREEN-1 closed as a class (RG-0189) · RG-0188 false-green caught

Attended follow-on to the morning's third-party sweep. Four items, all executed.

**RG-0156 — orchestrator.html, all four defects, now LOCKED.**
(a) Added to `ops/autodeploy/deploy_manifest.txt` (nginx maps `/orchestrator` -> `try_files
/orchestrator.html`, so it places at the web root). It had been served live while absent from the
manifest — outside the one deploy engine, fossilising, which is the class the manifest exists to
prevent. (b) **The access code was removed, not rotated.** PROBED first: `DOMContentLoaded`
revealed `#app` unconditionally, so `96315` enforced nothing, while anonymous GET of
`/orchestrator`, `/orchestrator/report.json` and `/orchestrator/approve` all answer **401 at
nginx** — the real gate. Rotating a code that gates nothing is ceremony; deleting the pretence is
the fix, and it needed no RUL-027 call because no live access changed. (c) The all-clear defect:
`jget()` returned `null` for both "fetch failed" and "server said no", so a 404, a 500, expired
auth or a corrupt report all rendered as five cheerful empties. It now returns `{ok,data,why}`;
`fill()` renders a distinct **FEED UNAVAILABLE** or **FIELD MISSING** banner; the health badge
gained a grey **not measured** state (RG-0133 class — an unreachable probe may not wear amber).
(d) `~05:00 SAST` corrected to 06:30 (merged 11 Jun). The *"Nothing waiting on you. ✨"* copy went
too — the sparkle was itself a verdict, and an empty list is not a verdict.

**Four PRESENCE assertions added to RG-0156 in the same run.** Its original four checks were all
*absence* tests, which a page rendering nothing at all would equally pass. The honest-failure
machinery is now asserted positively, so a later edit cannot restore the all-clear behaviour while
still satisfying the absence tests.

**RG-0189 (SECRET-ONSCREEN-1) — written and LOCKED.** The class behind this morning's exposure.
The 7 Aug rule (`rotate_secrets.py` prints no values) held and was never violated; the failure came
from the unguarded direction — `ROTATE_SECRETS.bat` left a permanent combined dump at
`.secrets\rotated_secrets.txt`, which an unrelated Notepad request restored as a previous tab into
a screenshot. Two lessons encoded: a secret at REST in a GUI-openable file is an exposure waiting
for an accident, and *"be careful with the editor"* is not a fix — secret **entry must not require
a GUI at all**, because a GUI requires someone to look at the screen and looking at the screen IS
the exposure. The assertion is shape-based, not name-based (renaming the dump cannot evade it):
no file under `.secrets/` may hold 2+ credentials at rest, `add_secret.bat` must exist and must
read via `-AsSecureString`, and `split_rotated_secrets.py` must exist to consume the transit dump.

**Built:** `add_secret.bat` (no-GUI entry; prints only a length and an 8-char fingerprint) and
`scripts/split_rotated_secrets.py` (fans the dump into the per-purpose files, refuses to shred
while `MS_ADMIN_PASSWORD` is the only copy — a script must not destroy the last copy of a human
credential). **`ROTATE_SECRETS.bat` rewritten**: 4 steps became 6, the dump is transit-only, and
credential `.bak` files older than 7 days are pruned.

**RG-0188 caught a false green — its own author's fault.** Creating an empty
`.secrets/hetzner_token.txt` as a paste target for David satisfied `os.path.exists()` and flipped
the entry to READY TO LOCK, while `hetzner_fw_selfheal.py` would still have exited *"NO TOKEN,
nothing changed"* in a real lockout. Presence was never the property — **runnability** is. The
assertion now distinguishes missing / empty / implausible, and notes that a present-but-empty
secret file is *more* dangerous than a missing one, because it paints the board green over an
unarmed remedy. Entry correctly back to OPEN.

**RG-0160 needed no build at all — corrected finding.** The two dossier PDFs already exist at
`assets/studywork/` (built 23 Aug, 2.0 MB + 1.7 MB), `media_push.bat` line 40 already carries the
`*.pdf` filter for that folder, and the teaser already links both (lines 135, 199). The code half
shipped on 23 Aug; the media half never ran. One `media_push.bat` run closes it — not a build.
The morning register's "still to BUILD" line was wrong and is corrected.

**Ledger after: 182 entries · 159 holding · 2 REGRESSED · 19 open · 0 ready to lock.** The two reds
are RG-0125 (migration chain jammed — its fix is the unshipped `b77cd2b`) and RG-0154 (session
badge), both of which clear on the Wed 27 Aug ship. Rulings 56/0 FAIL. EULA in sync.

## 2026-08-13 — Why three release presses did nothing: release.bat commits NOTHING (BAT-NAMING-1)

Three of this morning's five presses produced no commit, no push of pending work, and
a green-looking "RELEASE PUBLISHED" banner. Root cause is naming, and the error was
Claude's: project shorthand says "David's release.bat click", but release.bat is the
push-only lane — its own header says "commit manually before running this". The
auto-commit lane is deploy_marketsquare.bat (git_unlock → autobump → fold fragments →
gates/lock → COMMIT → push main → push deploy). The presses "succeeded" at pushing an
unchanged HEAD while the session's files sat modified on disk. Standing correction:
say and use deploy_marketsquare.bat; treat release.bat as advanced/manual. Queued
improvement (attended, CRLF-safe): a dirty-tree warning in release.bat, or retire it.

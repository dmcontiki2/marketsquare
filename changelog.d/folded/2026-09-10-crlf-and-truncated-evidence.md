## 2026-09-10 — The KB-removal script was itself LF-only, and the board that found it was hiding the line

Two faults, both in the machinery rather than the product, both found in the 05:54 host-side board.

**`remove_kb5124008.bat` had LF-only line endings (RG-0194).** The script written this morning to
remove the Windows update that killed the sandbox — the one thing standing between David and a
working shell — carried the exact defect RG-0194 exists to catch. It has no caret continuations, so
it would probably have run; "probably" is the whole reason that guard is a class rule and not a
per-file one. Converted to CRLF, contents untouched (verified: still elevates via
`Start-Process -Verb RunAs`, still `/norestart`, still `pause`, still prints the Settings fallback),
and the bytes re-read from disk afterwards rather than assumed.

**The wrapper was truncating its own evidence.** `ledger_host.bat` summarised the board with
`findstr /C:"           REGRESSION:"`, which matches line by line — so a multi-line fail printed only
its FIRST line. On this board that first line was a caret *warning* about ROTATE_SECRETS.bat, and the
line underneath it — `FAIL remove_kb5124008.bat has LF-only line endings` — was dropped. The queue
tail therefore reported a red whose visible text described something harmless. An instrument that
truncates its own evidence hides the fault it was built to surface; that is the same family as the
two corrected yesterday, and it nearly worked. Replaced by `ledger_rows.ps1`, which prints each
flagged row with its whole detail, proven against the 05:54 board before shipping.

**Also fixed:** the three host wrappers built their output file names by slicing `%DATE%`, which on
this machine is MM/DD/YYYY — so files written on 10 Sep were named `20261009`. They now ask
PowerShell for `yyyyMMdd-HHmmss`.

**Board after yesterday's corrections:** 336 entries · 312 holding · 22 open, with RG-0154, RG-0155
and RG-0349 all back to green and the session counter current at 194 on disk. The only outstanding
live item is two sittings of deploy debt (badge serves 192), which clears on the next ship — voiced
as INFO again, not as "do not deploy", now that OS-SYSTEM-QUOTES-1 is fixed.

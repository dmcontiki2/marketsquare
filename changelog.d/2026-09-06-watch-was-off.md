## 2026-09-06 — the daily watch was switched off, with no record (DW-104)

Found while answering David's question about which queue item was easiest to do next — not by any
instrument, because the instrument that would have noticed is the one that was off.

**The scheduler reports `trustsquare-daily-watch` enabled = false**, last run 5 Sep 04:33Z. The
register's newest pass is 5 Sep, so it ran yesterday and was disabled some time after. Nothing in
RULINGS.md, OPEN_LOOPS.md, the changelog or the status files records a decision to stop it.

That is the single consolidated monitor: it runs every check daily, maintains the watch register,
closes items on their own re-passing evidence, and reports the real issues. While it is off, nothing
sweeps, nothing closes, and a new fault waits for a human to notice.

**It also made something we told David false.** Earlier in the same session he was told *"your morning
watch runs the full board on its own schedule"* — offered as reassurance when a full board run would not
finish in the sandbox. That was RECALLED, not probed, and it was wrong. This is the
READ-wearing-a-PROBE's-colour fault the evidence ladder exists to prevent, made about the very
instrument that enforces the evidence ladder.

**Re-enabled the same session**, and reported to David in the same message so he can reverse it if the
silence was deliberate. Restoring a monitor to its documented schedule is CTO lane (RUL-037): no money,
no deletion, no sending, no lockout risk, and one click to undo.

**Residual, stated because it is the real gap.** Nothing asserts that the scheduled tasks which matter
are *enabled*. The register is maintained BY the watch, so a watch that is off cannot file its own
absence — the same circularity as an alarm riding the transport it monitors (DW-097, yesterday). A
liveness check for the schedule itself belongs in the ledger. It is not written yet.

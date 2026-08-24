### The terminal-behind-Claude complaint, and the half of the CSP fix that lied

**WINDOW-ZORDER-1 — cause found, not David's machine.** The `/start` skill launches the deploy itself,
and the desktop tooling launches apps in background mode by design ("the user's focus is preserved"),
so the console opens behind. When *he* double-clicks it, Windows grants foreground and it lands in
front as always. Windows refuses to let a background process steal foreground, so instead of fighting
that: `notify_attention.ps1/.bat` beeps, renames the window, and **flashes the taskbar button until it
is looked at** (FLASHW_TIMERNOFG). Wired at all five waiting pauses — the three ABORT pauses matter
most. `start_session.bat` reordered so Claude launches LAST, after the summary he was never seeing.
**RG-0183 LOCKED** as a class. Unproven on the machine (no PowerShell in the sandbox) — double-clicking
`notify_attention.bat` self-tests it.

**The 22:47 deploy landed.** Fares lane deployed and correctly dark (**RG-0182 LOCKED**). The naked
index is **fixed** — / now serves all five security headers where it served none (**RG-0179 LOCKED**).

**But `script-src` did not take, and migration 031 reported `ok` anyway.** My error, and the exact class
this repo keeps relearning: it declared success from the file WRITE, never probing the served response;
it also never searched `sites-enabled/`. **`migrations/033`** rewrites every CSP under `/etc/nginx`
including the vhost, then reads the header off a real response and **restores everything if it cannot
prove it**. RG-0178 stays open and honest until then.

**Needs David:** one more deploy carries 033 (the real CSP fix) and the corrected 032 (which fills the
fare cache immediately instead of waiting for 06:20). Flip `data_flights` after that deploy and the
fares appear; flipping before it just shows nothing, harmlessly.

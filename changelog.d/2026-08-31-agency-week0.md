## 2026-08-31 — RUL-079: agency outreach opens at WEEK 0, and the three guards that had to ship with it

David, the same day he activated the Resend $20/50k tier: *"i agree Claude, please do it."*

**The ruling.** `agGateW` moves from week 8 to **week 0** in the contagion model, and the National
key-accounts lane is ARMED (`waves_policy.json`: `armed` + `gates_green` true, batch 30). The
reasoning is part of the ruling: the model's own best lever set is *roll wk4 + agencies wk0*,
reaching **130 sellers by wk52 against the pinned median of 99**, and its Ideas tab states the
mechanism — one agency at 14 agents outruns 300 cold emails at 0.5%, and agencies are the only hub
already instrumented.

**What this is not: a volume increase.** The Resend flip that prompted the conversation changes no
lever in the model — there is no email-quota lever — and RAMP-1 (RG-0213) still governs batch
growth, unweakened. What changed is the earliest week David's per-wave word may be given. The send
itself is still his act (`--arm`).

**Pre-flight PROBED before arming:** 27 ZA prospects (Estate Agents 7 / Car Dealers 6 / Travel
Agencies 4 / Tour Operators 10), 0 bad MX, all four categories exact-keyed to their own template
(no RG-0218 fuzzy-match risk), jurisdiction ZA covered by RUL-063. Real hubs — Pam Golding, Seeff,
RE/MAX, Rawson, Chas Everitt, Motus, Halfway, NMI, and nine tour operators.

**Three guards shipped with it, all CTO calls under RUL-037. None were optional.**

**PRIV-OFFICER-1 (RG-0226).** The National note had said since 27 July: *"POPIA-officer addresses
(Motus, Bidvest McCarthy, Group 1) are FLAGGED in notes — prefer their contact forms for first
touch."* A note is not a control, and it was also wrong. A shape probe found **five** on that list
(Pam Golding's `compliance@` and Seeff's `informationofficer@` had never been flagged) and **seven**
across the whole pool — including `complaints.ir@justice.gov.za` sitting on a **SUPERSPAR
Botshabelo** row, i.e. the Department of Justice complaints desk about to be sent marketing for a
supermarket. That is not a bounce, that is the sending domain. The rule now lives at the send
chokepoint beside JUNK-GUARD-1, matched by **shape** so a re-scrape cannot reintroduce what a list
edit removed. The addresses are **held — never suppressed, never marked opted-out**, because nobody
opted out; writing a fake opt-out into the POPIA register to solve an engineering problem would be
its own offence. Reach them by contact form. Boundary asserted both ways: `info@`, `sales@`,
`support@`, `enquiries@`, `reservations@` must keep sending.

**SUPPRESS-GATE-1 (RG-0227).** Probed on the eve of the wave: `no such table: suppression`.
emailer.py's SUPPRESS-1 chokepoint reads a local opt-out register that `pull_from_server.py`
creates — and the pull had never run on this machine. **The chokepoint had been enforcing against
nothing, silently, for the whole first outreach fortnight.** No real send now proceeds without it.
Deliberately asymmetric to its sibling RG-0225: stale bounce evidence only *holds* the batch,
because volume is a business risk; an absent opt-out register *blocks*, because honouring an
opt-out is a legal obligation with no safe smaller version. Dry-runs stay unrestricted.

**PLAN-TRUTH-1 (in RG-0226).** `sendable_by_category` now counts only what the chokepoint would
accept, so National reads its true **22 of 27** with `held by guards: privacy_desk×5` printed
beside it. Previously the plan promised addresses the sender would silently refuse.

**State now:** the lane is armed and one gate from firing. `sync_to_server.bat` clears it — the
same command that arms the opt-out register, writes the RAMP-EVIDENCE-1 witness, and lets Pretoria
earn its 12 → 24.

**Also fixed, unrelated and self-inflicted:** a sandbox SQLite write against `prospects.db` failed
with `disk I/O error` mid-transaction and left a hot journal that made the database unreadable —
including read-only opens. Recovered from the pre-write backup (integrity ok, 1519 rows, 110 events,
nothing lost) and the mount rule written into `Projects/CLAUDE.md`: **the sandbox reads SQLite on
this mount and never writes it.** The better fix was the one that needed no mutation anyway.

Files: `docs/TrustSquare_Contagion_Model_v0.2.html` · `RULINGS.md` · `scripts/rulings_check.py` ·
`scripts/regression_ledger.py` · `../CityLauncher/emailer/emailer.py` ·
`../CityLauncher/emailer/wave_runner.py` · `../CityLauncher/emailer/waves_policy.json` ·
`../Projects/CLAUDE.md`.

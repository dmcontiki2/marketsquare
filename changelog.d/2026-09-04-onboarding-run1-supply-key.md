## 2026-09-04 — Onboarding run 1 (close): supply is the wall, and the key to it was never cut

**RG-0263 OPEN — SUPPLY-KEY-1.** `fill_wave_gaps.py`, allowlisted under RUL-096(d)
precisely so an unattended run can refill an empty city pool, failed rc=1 with HTTP 401.
Not a bug: `LAUNCH_API_KEY` has never been set in the server environment, and
LAUNCH-API-FAILCLOSED-1 (RG-0176, 26 Aug) makes an unset key mean CLOSED TO EVERYONE —
server.py says so in its own comment. That gate was the right call; the 26 Aug probe
found 200 prospect records with names, emails and phone numbers served anonymously. The
unpaid half is that nobody then provisioned the key, so our own tooling sits outside our
own door. Entered as OPEN rather than done, deliberately: provisioning a secret and
restarting production unattended at 13:15 is the lockout-risk class reserved under
RUL-027, and RUL-037 says an item that cannot be executed this session goes into the
ledger, not into a sentence to David. Two legs when it promotes — the door still refuses
strangers AND the key opens it for us. Either alone is a wrong fix. Until then, supply
comes from the scraper lane, not the API lane.

**Stop-loss released on three cities.** `clean_stoploss_cities.bat` MX-verified and
cleaned the pools, stamping the dirty wave number per STOP-LOSS-RELEASE-1. Polokwane is
now GREEN; Pretoria and New York are blocked only by min-gap and clear on 5 Sep. That
turns three dead lanes back on for tomorrow's scheduled wave.

**Where the goal actually stands.** The listing floor is repaired and locked, the
outreach link opens for a stranger, and the number is an honest 0. What is missing is
people: 542 of the 546 we emailed received the broken link and none has been re-mailed,
so only 30 human beings have ever been shown a working funnel — and of 64 recorded
clicks the register scores just 2 as real. The goal needs 20 publishers from a
population that has, so far, effectively been 30. The one reserved decision with David
is whether to re-mail the 441 still-mailable broken-link recipients.

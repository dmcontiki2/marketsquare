## PROXY-OPEN-1 / FN-WINDOW-1 — the open rate was measuring Google, and a red was measuring nothing (24–25 Sep 2026)

Onboarding run 20. Both are measurement faults, found by checking a number and a red before
inheriting either.

- **PROXY-OPEN-1 (RG-0464).** The click register graded **331 recipients as `human_open`** — a
  12.9% read rate on 2,574 letters. PROBED on the live register: **297 of them had no open event
  that was anything but a mailbox-provider prefetch.** 229 events carry `GoogleImageProxy` in the
  User-Agent, 18 `YahooMailProxy`, 17 `MSOffice 16`, and 301 the bare token `Mozilla/5.0`, which is
  Apple Mail Privacy Protection. 326 of the open events came from Google IP ranges.
  `MACHINE_UA`/`MACHINE_IP_PREFIXES` were written on 3 Sep for *clicks* — corporate scanners — and
  no image proxy is in either list, so a proxy fetch scored on `clicked Nh after send` alone, worth
  −1, and −1 is "human". 328 of the 331 gradings rested on that single reason.
  **Fixed without deleting the signal:** a proxy fetch proves the letter reached a live mailbox and
  proves nothing about whether a person looked. New `proxy_open` tier, `n_proxy_opens` column
  (+ migration for the live table), `opened_proxy` in the funnel totals, and it can never rejoin a
  human count. Re-scored on a copy of the live DB before shipping: human_open 331 → 34, uncertain
  84 → 16, proxy_open 365, machine 203 unchanged, **human_click 9 unchanged** — an image proxy
  fetches pixels, not links. Strictly tightening.
  *The honest funnel:* 2,574 letters · 34 demonstrable readers · 365 delivered-but-unmeasurable ·
  9 clicks · 0 published. Nine clicks from thirty-four visible readers is ~26%: the letter works on
  the people who read it, and the shortfall is reach.
- **FN-WINDOW-1 (RG-0465).** RG-0110 printed *"auth_verify no longer routes through
  `_establish_user_session`"* and carried a deploy block. That call is auth_verify's **last line**.
  The check read `split("def auth_verify(")[1][:1400]` — the first 1400 bytes of the rest of the
  file — and SIGNIN-ONCE-1, shipped the same morning, added ~1,050 characters and pushed the call to
  offset 2056. `auth_verify_code` sat at 1372, **28 characters** from the same false red. New
  `fn_body()` bounds the read by the next top-level def. Board: 4 regressed → 3.
  *Named, not claimed closed:* 22 other checks in that file still read a fixed byte window.

Cost model impact: none.

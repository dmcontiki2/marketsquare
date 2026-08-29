## 2026-08-28 — D1 closed: the domain lifeline is fully recorded, and the toggle was already on

**DOMAIN-LIFELINE-1 CLOSED · RG-0137 OPEN → LOCKED** · first item served off the new DAVID_QUEUE

David opened Cloudflare looking for auto-renew and landed on the **zone** overview — auto-renew
lives at **account** level under Domains → Registrations. Since he was logged in, the read was
driven directly rather than handed back as directions.

**Result: `trustsquare.co` — status Active, auto-renew ON, expires Dec 31 2026, one domain in the
account.** Nothing needed changing. Combined with the 27 Aug WHOIS work (registrar **Cloudflare,
Inc.**, registry expiry **2026-12-30**, registrar lock ON), the domain lifeline is now completely
recorded and **RG-0137 is LOCKED**.

Worth stating plainly: this item sat in the David-only column for **six days across five sweeps**
as an action he had to take — and it turned out to be a read of a setting that was already
correct. That is the third item this week to follow that exact pattern, after the Google consent
screen and the registrar itself. The DAVID_QUEUE built yesterday exists because of it.

### One discrepancy, recorded rather than reconciled away

WHOIS gives registry expiry **2026-12-30T23:59:59Z**; the dashboard displays **Dec 31, 2026**. Same
instant, two timezones — not two dates. The register keeps the WHOIS value because the registry is
the authority and the dashboard is a rendering of it. Noted so a future session does not "fix" one
to match the other and quietly lose the reason.

### An assertion that punished provenance — fixed

`DOMAIN-AUTORENEW-PROVENANCE-1`: RG-0137's auto-renew check demanded the field equal a bare `on`,
and went **red** on `ON (read in the Cloudflare Registrations dashboard 2026-08-28; status Active)`.
It was penalising the session for recording *where and when* the fact came from. An assertion that
punishes provenance teaches the next session to strip provenance — the opposite of what this ledger
is for. It now matches the leading token **and requires a date**, the same shape RG-0139 already
used: an undated status assertion silently ages into a lie.

Ledger: 191 entries · **179 holding** · 0 REGRESSED · 13 open · 0 UNVERIFIED · exit 0.

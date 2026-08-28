## 2026-08-27 — Two "David-only" items were never David's: the consent screen and the domain registrar

**DOMAIN-WHOIS-1 / CONSENT-READ-1** · follow-on to the same day's third-party sweep · 2 days to soft-public

David asked how many of the sweep's open actions could be closed for him. Four of the seven turned
out not to need him at all. The interesting part is not the answers — it is that both had been
sitting in the David-only column for **six days across five sweeps**, and neither was ever a David
job.

### The domain: a "settled negative" that was never tested properly

`RG-0137` had been open since 22 Aug. Four consecutive sweeps tried RDAP, failed, and escalated the
failure into canon — the 26 Aug register read **"these four fields will never be filled by
machinery"**, an instruction to every future session to stop trying.

Every one of those sweeps was **guessing RDAP hostnames** — `rdap.org`, `rdap.nic.co`,
`rdap.identitydigital.services`, `rdap.net`, `rdap.markmonitor.com` — and reading five 404s as
proof the data did not exist. **None asked the authority which server to use.** The method that
works takes about a second:

```
whois.iana.org:43    <- "co"              => refer: whois.registry.co
whois.registry.co:43 <- "trustsquare.co"  => the full registration record
```

`.co` is operated by **CentralNic**, which no amount of guessing was going to reach.

**Result — PROBED, not read off a file:** registrar **Cloudflare, Inc.** (IANA ID 1910), created
2025-12-30, **expiry 2026-12-30 — 125 days out**, `clientTransferProhibited` (registrar lock ON),
nameservers KOA/AINSLEY.NS.CLOUDFLARE.COM, DNSSEC unsigned. Registrar and DNS are the same party,
which is why the 22 Aug note that Cloudflare nameservers "narrow but do not prove" the registrar
was right to hedge — and is now settled. The silent-death risk is four months away, not days.

**The class lesson, written into RG-0137 rather than left in a changelog: a negative result proves
a negative only if the method was right. Five wrong doors is not a locked building.** This is the
same shape as the 21 Aug Google-OAuth error the whole sweep exists to prevent — a confident
recorded "no" that one probe overturned — and it is worse, because this one had been promoted from
an observation into a standing instruction not to look again.

`DOMAIN_AUTORENEW` genuinely cannot be probed: WHOIS does not publish it, it is a registrar-account
setting. That one field, and only that one, is David's. RG-0137 now holds **one** failing
assertion instead of four.

### The consent screen: nobody had opened the page

`RG-0139` — **PROMOTED OPEN → LOCKED.** Publishing status **"In production"** (not Testing), user
type External, and the Verification centre states in its own words: *"Verification is not required
since your app is not requesting any sensitive or restricted scopes."* Data access confirms it —
zero sensitive, zero restricted. **Strangers can sign in on Friday.** Five sweeps listed this as a
David-only console errand; it was one navigation.

Two residuals recorded, neither blocking: the Audience page displays an **OAuth user cap of
"0 users / 100 user cap"** (the unverified-app cap, which the console has just said does not apply
— worth one re-read in week one, since the symptom if it ever did bite is sign-ins refusing at
exactly 100 users), and **branding is not being shown to users**, so the consent screen displays
the bare domain rather than the TrustSquare name and logo.

### CityLauncher launch deadline — half done, and the other half is bigger than the register said

`LAUNCH_SPECIAL_DEADLINE=2026-09-01` written to `CityLauncher/.env`. But reading
`emailer/launch_codes.py` first changed the finding: `enabled()` requires **all three** of
`LAUNCH_SPECIAL_ENABLED`, `LAUNCH_CODE_SECRET` and the deadline, and that `.env` carries **none of
the other two** — so the launch-special block is currently **stripped from every outbound
CityLauncher email**, not merely mis-dated. The register's "set the deadline on both sides" was
necessary but not sufficient. The other two are deliberately left off: switching on a
customer-facing discount lane is launch scope, and `LAUNCH_CODE_SECRET` is an HMAC key whose
rotation invalidates unissued codes.

### Board

`regression_ledger.py` exit **0** — 191 entries · **178 holding** (was 177) · 0 REGRESSED · 13 open
(was 14) · 0 READY TO LOCK · 0 UNVERIFIED. `rulings_check.py` 59 rulings, 0 FAIL, 0 WARN.

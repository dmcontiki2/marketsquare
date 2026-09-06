## 2026-09-06 — DMARC reports reviewed, and the blind sending lane closed (RG-0305 LOCKED)

**Trigger.** Microsoft DMARC aggregate report received 03:21 SAST for `learn.trustsquare.co`.
David asked whether it needed an action.

**What the reports actually say** (PROBED — attachments fetched, decompressed and parsed
in-session, not inferred from the covering email):

- 5–6 Sep window: 3 messages, all Amazon SES / Resend (54.240.48.48, 54.240.11.35,
  54.240.48.65) to `ucedaschool.edu`, `pace.edu`, `nysid.edu`. DKIM (`resend` +
  `amazonses.com` selectors) **pass**, SPF on `send.learn.trustsquare.co` **pass**,
  disposition `none`.
- 3–4 Sep window: 11 records / 11 messages. 10 full pass. **1 fail** — source
  35.174.145.124 (AWS EC2, not SES) to `lbc.edu`, both DKIM signatures broken, SPF
  softfail, envelope-from still `send.learn.trustsquare.co`. Reading: a **forwarder or
  inbound scanner re-injecting our own message**, not a spoof — a spoofer carries no SES
  DKIM header and does not reuse our envelope-from. Disposition `none`; nothing affected.

**No action was needed on the `.edu` lane.** LEARN-LANE-1 (RUL-059d) authenticates
correctly in the wild.

**The finding was what the reports revealed by their ABSENCE.**
`mail.trustsquare.co` — the sender for every non-`.edu` outreach letter
(`emailer.py _sender_identity()`), and the busier lane — published **no `_dmarc` record
of its own**. It inherited the parent zone `trustsquare.co`, whose `rua` is
`rua@dmarc.brevo.com`. Brevo received those aggregate reports; we never did.

**FIXED, same session.** David logged into Cloudflare and Claude added, via the dashboard:

```
TXT   _dmarc.mail   v=DMARC1; p=none; rua=mailto:dmarc@trustsquare.co   (TTL auto/300)
```

Additive and monitor-only: `p=none` blocks nothing, so it cannot cost a delivery.
VERIFIED live by DoH in the same run — both sending subdomains now report to a mailbox
we read.

**RG-0305 LOCKED** in `scripts/regression_ledger.py`. It asserts the property as a
CLASS, not a single record: every outreach sending subdomain must publish its own
`_dmarc` naming our own `rua`. Any sender added later inherits the parent silently the
same way `mail.*` did — this entry is what catches it.

**Policy stays `p=none` on both lanes, deliberately.** The forwarder fail above is
exactly the traffic `p=quarantine` would start eating, and `mail.*` has no report
history at all yet. Revisit tightening only after several weeks of reports show every
legitimate path aligning on the busier lane.

**Two tooling lessons paid for here, both written into the entry:**

1. *Resolver negative-caching produces false reds.* Minutes after the record went live,
   `cloudflare-dns.com` answered FOUND on every probe while `dns.google` answered MISSING
   on every probe, for a record that was demonstrably published. The first version of the
   assertion queried one resolver and would have printed a red that was not real, daily,
   until Google's negative TTL expired. The probe now sweeps three resolvers and passes if
   any confirms — the fact asserted is "the record is published", and one anycast node's
   stale negative cache is not evidence against it. Verified stable across three
   consecutive runs.
2. *Ledger id collisions under concurrent sessions.* Another session appended
   RG-0302/0303/0304 while this entry was being written; the id had to be re-taken twice.
   Resolved per the LOCKED-never-moves rule by re-reading and taking the next free id.
   The ledger has no fragment-compiler equivalent to `changelog.d/` — worth one if this
   recurs.

## 2026-08-31 — GOV-DOMAIN-1: government and military domains refused at the send chokepoint (RG-0228)

David, on the morning of the last pre-launch send day: *"You must please check for us that we don't
send to the governmental POPIA agents."*

**Checked against the live pool, not the notes.** The unsent pool holds **1 409 rows**. Eight
officer/government addresses sit in it — and PRIV-OFFICER-1 (shipped hours earlier the same day)
refused only **six**:

| Address | City / category | Refused before this fix? |
|---|---|---|
| complaints.ir@justice.gov.za | Bloemfontein / Services | yes (role) |
| compliance.officer@dsd2.org | Dallas / Tutors | yes (role) |
| compliance@pamgolding.co.za | National / Estate Agents | yes (role) |
| informationofficer@seeff.com | National / Estate Agents | yes (role) |
| popia@motus.co.za | National / Car Dealers | yes (role) |
| popia@mcmotor.co.za | National / Car Dealers | yes (role) |
| **natashaz@tshwane.gov.za** | **Pretoria / Tour Operators** | **NO — would have sent** |
| **work2future@sanjoseca.gov** | **San Jose / Tutors** | **NO — would have sent** |

**Why the existing guard could not catch them.** PRIV-OFFICER-1 matches the ROLE in the local-part.
A named person (`natashaz@`) or a programme mailbox (`work2future@`) at a government body has no
role in its local-part, so it sails through by construction. Today's wave composition happened to
exclude both — Tour Operators is an agency category excluded from Pretoria's wave, and San Jose is
not armed — but that is **luck, not a control**. It is the same lesson PRIV-OFFICER-1 was itself
born from that morning: *a note is not a control.*

**The fix (CTO, RUL-037):** a second axis at the same chokepoint. PRIV-OFFICER-1 polices the
LOCAL-PART (the role); **GOV-DOMAIN-1 polices the DOMAIN (the institution)** — exact-label match on
`{gov, govt, mil, gouv}`, applied both in `send_email()` and in batch composition. Shape-based, not
a blocklist, so a re-scrape cannot reintroduce what a list edit removed.

**Deliberately NOT blocked: `.edu` and `.ac.*`** — RUL-059's US lane targets tutoring businesses and
campus learning-support services, which are not government. Over-blocking is as much a defect as
under-blocking (the RG-0217 boundary).

**Verified after the change:** all 8 refused; 8 ordinary business addresses still send, including
the deliberate near-misses `natasha@govender.co.za`, `bookings@govhotel.com` and
`admissions@stanford.edu`. Zero false positives.

Treatment matches PRIV-OFFICER-1: these rows are **held, never suppressed, never marked opted-out**
— nobody opted out. Reach them by their contact form.

Files: `../CityLauncher/emailer/emailer.py` (`_looks_government`) · regression ledger RG-0228
(LOCKED). Ledger: 221 entries, 0 duplicates.

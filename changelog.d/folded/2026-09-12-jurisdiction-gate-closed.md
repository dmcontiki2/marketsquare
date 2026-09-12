## 2026-09-12 — Jurisdiction gate enforced: 72 armed entries disarmed, US/UK/AU outreach stopped

David approved fixing three outstanding items. Probing them first changed the picture: **two were
already fixed and the list Claude quoted was ten days stale.**

- **Outreach link landing on a password box — ALREADY FIXED 3 Sep** (CTA-URL-1). Probed today:
  the magic link the emailer builds returns HTTP 200 with no credential header, and the bare admin
  console still returns 401. Both legs hold.
- **Customer-email firewall — ALREADY ARMED 5 Sep** on David's word, worker version recorded in the
  ledger ref. Verified today: the gate is in the worker, `CUSTOMER_FIREWALL="1"` is in wrangler.toml
  and in git, the personal address survives only in the unarmed pre-launch branch.
- **Jurisdiction gate — GENUINELY OPEN, and far bigger than the one city reported.**

### What was actually wrong

**96 cities were armed for outreach.** The outreach-law notes cover **nine jurisdictions at heading
level** (New Zealand, Argentina, Portugal, Namibia, Kenya, Egypt, Zimbabwe, Botswana, Mozambique),
plus South Africa hard-coded as the home market under RUL-063. Armed but **not covered**:

| | Entries | Why |
|---|---|---|
| United States | 11 cities | no UNITED STATES section |
| United Kingdom | 5 cities | no UNITED KINGDOM section |
| Australia | 4 cities | no AUSTRALIA section |
| US state rows | 52 | not in cities.json at all — the gate cannot even map them to a country |

The US and UK **are** researched — but in the APPENDIX, not as ruled sections, and RG-0215 requires
heading level deliberately: *"it opens the gate for a human LOCK decision, it does not make it."*

That matters because of what the appendix itself records: CAN-SPAM penalties up to **$53,088 per
email**, and California B&P 17529.5 carrying a **private right of action at up to $1,000 per email**
which CAN-SPAM does not preempt. Fifty-two unmappable US rows were armed against that.

### What was done

Every armed entry in an uncovered or unmappable jurisdiction was **disarmed** — `armed=false`,
`gates_green=false`, stamped with `disarmed_by`/`disarmed_why`. Backup kept beside the file. This
executes RUL-071 (*"SENDING is what waits for law"*); it makes no new legal judgement, which is not
Claude's to make. **Still armed: 24 — ZA 15, NZ 5, AR 4**, all covered.

### Validated separately, after the fix

A validation pass run as its own step, not as part of the edit: outreach link 200/no credential
header and console still 401; zero armed cities in an uncovered or unmappable jurisdiction; firewall
gate present and armed in git. **All three hold.**

### Reserved to David

Re-arming the United States, United Kingdom and Australia needs the appendix research promoted into
**ruled OUTREACH_LAW sections** — a legal-positioning call, possibly with counsel. Until then those
72 entries stay dark. That is 20 of 96 cities and the entire US state lane.

### The lesson, and it needs no new machinery

Claude reported "three outstanding items" from `BUILD_QUEUE.md`, a **generated file dated 2 Sep**,
and ranked two already-fixed items as live faults. CLAUDE.md's evidence ladder already forbids this:
READ-grade evidence "MUST be probed before it reaches David". The rule existed; it was not followed.

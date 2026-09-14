## 2026-09-14 — The baseline changes once: four rulings taken, the batch written, production cleaned

David, reading the open-actions list: *"all of them please, we want the baseline to change once only
for a longer period than to have short changes?"* Every open design item is in, and they ship as ONE
baseline change. **RUL-126.**

### The list was checked against the code, not against the build queue

`BUILD_QUEUE.md` is generated 2 Sep and had gone stale. Probed instead: `SF-AIDESC-1`,
`SF-MULTIVISION-1` and `SF-COACH-ASK-1` are all present in `ms.js` (built 4 Sep), and
`INTRO-REMIND-1` is in `bea_main.py`. So **RG-0205/0206/0207 and RG-0208 are done** and were
struck off the list before it was shown to him. Confirmed unbuilt by the same method: no `ZOOM`
string in `ms.js`, no `SQUIRE` anywhere, `/credentials/mine` absent from both app files, no
`/quick` route.

### Four decisions taken, none of them parked

- **RUL-127 — DCB-001 approved.** The GATE line in `DESIGN_BACKLOG.md` has been empty since
  11 Aug; it now carries his name and date. Batch-upload any order, tap one as cover, AI orders
  the rest, drag to adjust.
- **RUL-128 — one $5 tier.** Global buyer reach folds into Starter: Free · Starter $5 (10 slots +
  reach) · Pro $20. He took the consequence with it — a pure buyer now buys a seller plan to get
  reach. The Agency Pro seat (RUL-048) was NOT folded; he chose the two-product fold.
- **RUL-129 — the trust ladder gains private-seller credentials.** Property and Local Market stop
  being silent. Every new entry must be a dated, sourced fact, checkable by somebody outside
  TrustSquare, added once and counting on every listing after.
- **Listings 383 and 384 deleted.** The two hand-over proof drafts are gone from production, by
  the seller-authenticated route so no API key crossed the wire. Re-probed: both `GET /listings/{id}`
  return **404**.

### The batch itself

`BASELINE_BATCH_2026Q4.md` is the plan of record — nine build items ordered by dependency (Zoom
first, Squire after it by ruling, the Quick app after the service worker), what each must prove in
the RENDERED app, and the arming sequence that stays David's.

**Two live faults are explicitly NOT in the batch** and are repaired on their own, because RUL-126
governs design and not repair: the false offline banner, and the missing service worker that keeps
both web push (RUL-122) and the install offer (RUL-123) from ever firing.

### Reserved, and stated rather than buried

The travel funnel endpoint (the Expedition Dossier as the introduction) is a commercial shape and
is his; it blocks arming the travel lane, not building Zoom. The designer-role binding (D14) is his.
The Agency $5 seat is his.

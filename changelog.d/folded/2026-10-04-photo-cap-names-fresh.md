## 2026-10-04 — QUICK-FRESH-1, PHOTO-CAP-2, ANON-NAMES-1 (RG-0872..0874)

- **QUICK-FRESH-1** (David: *"i dont see the 'near you' option in the live Quick app yet"*): it was live; his Quick had
  been open since before the deploy and Start again only redrew the door. Start again (and returning to an idle Quick at
  the door) now loads the newest version when the server has one. Shipped e4fdd84.
- **PHOTO-CAP-2** (Dave jnr via David: *"up our number of photos per property to 20"*): PHOTO-CAP-1 (15 Jul, David-approved
  after costing) already allows **24** for property, cars and places to stay (12 elsewhere) in the Sell flow; the Edit
  screen -- where every Quick listing gets its photos -- had its own hard-coded 10. One rule now: `msPhotoCap()`, read by
  both. No server change (the server never capped the count). Cost model impact: none beyond PHOTO-CAP-1's budget
  (Rev C plans 16.8 photos per listing); measured anon-scan cost $0.0038 per scan call (ai_spend_log, 45 days).
- **ANON-NAMES-1** (David: the complex name *"iQ Rondebosch"* stayed in his title and description while the photo pass
  removed the complex IDs): the text scrub had regexes only, and a name has no shape a regex can see. Every private
  publish and edit now asks the AI for the NAMES in the title, body and every photo caption -- complexes, estates,
  buildings, residences, developments, businesses, people -- and replaces them; the typed area is checked the same way.
  Suburbs, towns and public landmarks (malls, schools, highways) stay. Fail-open and logged; ~$0.0002 per changed text.
  Cost model impact: one small fast-tier read per publish/edit of changed text, inside the C1 ceilings.

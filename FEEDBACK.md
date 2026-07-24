# MarketSquare — Feedback Register

*The voice of the customer, filed. Verbatim stays verbatim; paraphrase launders the pain out of feedback.*
*Classes: fix-now (blocks a core journey or touches money/trust) · next (real friction, workaround exists) · later (honest parking) · out-of-scope (conflicts with the Codex — cite the rule).*

| id | date | source | verbatim | theme | class | status | link |
|---|---|---|---|---|---|---|---|
| F-001 | 2026-07-23 | Maroushka Conradie (email, rental-listing test) | "I don't think the rental listing should show options like levies or rates and taxes, as these costs are NEVER for the tenant's account. It should rather list options like: 1. Electricity and 2. Water (which most tenants are liable to pay for). 3. Who is responsible for garden upkeep and maintenance. 4. What the deposit is. 5. Any other fees for the tenant's account." | rental-cost-fields | fix-now | FIXED (built, awaiting /ship) | RENTAL-COSTS-1 · CHANGELOG 23 Jul (night) |
| F-002 | 2026-07-23 | Maroushka Conradie | "Step 6 should also rather include info relevant to lessors: Why would an agent be better to work with? Because they will make sure that you are compliant with all the relevant property legislation, they properly vet applicants to ensure they are suitable prospective lessees, and they handle all the administrative work regarding the rental relating to payments and maintenance." | step6-lessor-info | fix-now | FIXED (built, awaiting /ship) | RENTAL-COSTS-1 (SF_LEGAL_NOTES.property_rental) |
| F-003 | 2026-07-23 | Maroushka Conradie | "I would have preferred that the quality improvement button telling me how to improve my score be clickable, taking me directly to the place where I can make the necessary changes instead of making me go back manually (which I don't want to do because I don't like complicated processes and fear I might mess up the listing if I change things)." | score-tips-clickable | next | FIXED (built, awaiting /ship) | SCORE-JUMP-1 |
| F-004 | 2026-07-23 | Maroushka Conradie | "I saw that the number of bedrooms, bathrooms and garages did not display any information." | published-fields-empty | fix-now | FIXED (built, awaiting /ship) | BEDS-PUBLISH-1 (frontend + backend) |
| F-005 | 2026-07-23 | Maroushka Conradie | "The map function did not work or take me to a map to see the area." | detail-map-broken | fix-now | FIXED (built, awaiting /ship) | MAP-FIX-1 |
| F-006 | 2026-07-23 | Maroushka Conradie | "The closest hospitals listed is not right, it should list St. Mary's. The closest schools should include Waterkloof Preparatory, Anton van Wouw, Affies, Boys High and St. Mary's DSG. Shopping should include Brooklyn Mall" | poi-accuracy | fix-now | FIXED (built, awaiting /ship — existing listings need nearby_pois cleared to refetch) | POI-QUALITY-1 |
| F-007 | 2026-07-23 | Maroushka Conradie | "The property guide also caters to buyers, not lessees, it should reflect average rental prices in the area, even if just by doing a simple 0.85% of the selling price calculation, which is the industry average." | rental-price-guide | fix-now | FIXED (built, awaiting /ship) | RENTAL-GUIDE-1 |
| F-008 | 2026-07-23 | Maroushka Conradie | "There is no use for an investor yield calculator on a rental property, this will just clutter the listing and confuse people looking for rentals." | yield-on-rentals | fix-now | FIXED (built, awaiting /ship) | RENTAL-GUIDE-1 (frontend hide) |
| F-009 | 2026-07-23 | David Jnr (super-advert screenshots, via David) | "the super advert example shows the older format… Claude can you please update the super advert of the better format?" | super-advert-old-format | fix-now | LIVE ✅ — server migration applied 24 Jul, verified on trustsquare.co (/listings/265) | SUPER-FORMAT-1 · CHANGELOG 23 Jul (late) |
| F-010 | 2026-07-23 | David Jnr (super-advert screenshots, via David) | "There are repetition of information… inside the table blocks and his About This Listing… This way it looks unproffessional" | cars-about-repeats-specs | fix-now | Existing Figo LIVE ✅ (migration applied 24 Jul) · new-listing prevention (CARS-DESC-DEDUPE-1, ms.js) awaiting code deploy | CARS-DESC-DEDUPE-1 · CHANGELOG 23 Jul (late) |
| P-001 | 2026-07-23 | Maroushka Conradie | "The listing process was easy and I loved seeing my quality score climb with the info I added." | praise-quality-score | — (praise) | noted | — |
| P-002 | 2026-07-23 | Maroushka Conradie | "I love the 'Introduce me to an agent' function!!!" | praise-agent-intro | — (praise) | noted | AGENT-SVC-1 |

## Notes
- 2026-07-23: F-001…F-008 all from one voice (Maroushka, founding seller, rental vertical). fix-now
  classification: F-001/2/4/5/6/7/8 sit on the sell/browse core journeys and touch listing trust.
  All eight fixed in one pass same day (see CHANGELOG 23 Jul night). Related earlier round:
  FEEDBACK_DAVIDJNR_SUPERADVERTS_2026-07-21.docx (David Jnr, Session 147) — predates this register.
- 2026-07-23 (late): F-009/F-010 from David Jnr's super-advert screenshots. Root cause of the About-vs-table repetition was sfComposeDescription folding structured Cars fields into the description; fixed in ms.js for new listings (CARS-DESC-DEDUPE-1) and cleaned on existing rows by scripts/fix_super_advert_format.py, which also backfills the Hilux super advert to the new spec-panel format.
- The retired quick-list wizard (SB_FIELDS in ms.js) still carries a levies field for To Let;
  left as-is since the guided sell flow (sf) is the live path — flag if it ever resurfaces.

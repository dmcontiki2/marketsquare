# Collections AI Validation — App vs Fable Comparison
**Date:** 19 Jul 2026 · **Items:** 6 jewelry pieces (13 photos) · **Status:** Fable evaluation COMPLETE · App run PENDING photo files (see §2)

---

## 1. What the app's collections AI validation actually is (from bea_main.py, verified on disk today)

Three separate AI checks touch a Collectors listing:

| Check | Where it fires | Model (today) | What it does |
|---|---|---|---|
| **Photo anon/safety gate** (`_seller_photo_anon_gate`) | Every photo upload | vision → **Haiku 4.5** | PII/branding scan (clean/redact/reject), inappropriate-content flag, subject read, WRONG-TYPE-1 `fits_category` — a primary photo of the wrong kind of item is BLOCKED |
| **AI5 batch listings** (`/listings/batch-cards`, 2T) | Seller invokes | vision → **Haiku 4.5** | Per photo: title, 40–80-word description, SA price suggestion, condition (mint→poor), category=Collectors |
| **Tier-1 condition grader** (`grade_card_condition`) | Batch job on published listings | vision → **Haiku 4.5** | Conservative TCGplayer-vocab grade (Near Mint→Damaged) + confidence; written to ai_grade columns only, buyer display off |

All three route through the ai_provider seam, `task="vision"` → `claude-haiku-4-5-20251001` (Haiku-first, 3 Jul 2026).

**Structural finding before any run:** the whole stack is *card-centric*. The AI5 prompt says "expert trading card and collectables appraiser"; the Tier-1 grader grades in TCGplayer card vocabulary; `_CATEGORY_EXPECTS["collectors"]` lists "coin, banknote, trading card, stamp, artwork, antique, watch, toy, book, vinyl, memorabilia or similar" — **jewellery is not named anywhere** (it passes only via "or similar"). Expect the app to handle these six items, but in card-flavoured language, with condition vocab designed for cards, not jewellery. That is itself a validation-test result.

## 2. App validation run — NOT DONE YET (blocked on photo files)

The photos were pasted into chat; no image files exist on disk, and chat pixels cannot be re-serialised into files. The live run needs the originals.

**Ready to fire:** `run_collections_validation.py` (this folder) sends every photo in `validation_test_photos/` to the LIVE `/listings/batch-cards` endpoint — same prompt, same Haiku 4.5, same sanitisation the app applies. Cost 2T flat (balance today: 369T on dmcontiki2@gmail.com). Results save as JSON beside the photos and this report's §4 gets filled in.

Not externally testable even with files: the anon gate (`/listings/photo` needs the server API key) and the Tier-1 grader (fires only on published listings). Their prompts and expected behaviour are covered in §5.

## 3. Fable evaluation (done now, from the same 13 photos)

> I am not a certified appraiser; metal and stone identifications below are visual reads and need XRF/acid testing and a loupe to confirm. Values are second-hand SA market estimates, not offers.

### Item A — Fine curb-link chain necklace, gold tone
Fine-gauge curb (gourmette) chain, spring-ring clasp, approx. 45–55 cm. **No hallmark visible** in the photo; slight tonal difference near one end link raises plating-wear suspicion. Condition good — no kinks, breaks or clasp damage visible. **Identity risk:** solid 9ct vs rolled-gold/plated is undeterminable from photos. If solid 9ct (~2–3 g): roughly R1,800–R3,500 metal value at 2026 prices (estimate — weigh and test). If plated: R50–R150. **Action: acid/XRF test before listing any gold claim.**

### Item B — Freshwater cultured pearl strand, gold-tone clasp
Potato-shaped freshwater cultured pearls with visible growth rings, ~7–9 mm, cream-white, good lustre. Decorative filigree box/fish-hook clasp, gold-tone (almost certainly plated base metal — typical for these strands). Appears unknotted or minimally knotted between pearls (re-string risk if it snaps). Condition good; a few pearls with surface blemishes. Commodity item: **R150–R400 resale; R400–R900 retail-equivalent** in SA. No certification expected or needed at this value.

### Item C — Pentagon pendant/charm, engraved knot motif
Small bevelled pentagon pendant, engraved interlaced five-petal star/knot, soldered jump-ring loop, plain back. The deep saturated yellow is a **high-carat look (18–22k colour) — or brass/gilt; the two are indistinguishable in photos**. No hallmark visible anywhere. This is the highest-variance item on the table: at ~1.5–2 g, 22k would be roughly R2,500–R4,500 in metal; gilt brass is under R50. **Do not list with a gold claim untested.**

### Item D — Silver marcasite ring, red-orange stone (with "Honey" stamp)
Vintage openwork ring: marcasite-set double-quatrefoil/butterfly gallery over a barrel-form red-orange stone — **carnelian or honey amber**. The shank stamp reads "Honey": plausibly the stone designation (honey amber), a maker's mark, **or simply a personal engraving** — it is NOT a fineness mark, and no 925/STERLING is visible. Mid-20th-century style. Condition: fair — dirty, white residue near the bezel (possible old glue repair), oxidation in crevices; marcasites look substantially complete. **R250–R700** after a clean; test silver fineness.

### Item E — 9K garnet-set ring, stamped "JAYFOR 9K"
Legible maker + fineness stamp: JAYFOR 9K. Tall crown, six split claws holding a dark red round/oval faceted stone — **garnet most likely** (dark tone argues against synthetic ruby, but verify). Shank clean, light wear, claws intact and gripping. Estimated 2.5–3.5 g gross. The stamp materially de-risks this one. **R1,200–R2,800 resale** depending on stone verdict and ring size demand.

### Item F — 9ct citrine pendant, leaf mount
"9ct" stamp visible on the frame. Large round mixed-cut pale champagne-yellow stone ~16–18 mm, four claws, textured leaf/branch shoulders, generous split bail. **Citrine or lemon quartz most likely; pale synthetic spinel/glass possible** — a loupe check of wear on facet junctions would tell. Very good condition; best piece of the six visually. **R1,800–R4,000 if citrine in a solid 9ct mount**; the mount alone carries meaningful metal value.

### Cross-item observations
- Three of six items (A, C, D) carry **no readable fineness mark** — the decisive value question for each is a metal test, which no photo-only AI (the app's or mine) can resolve.
- None of the photos contain PII, faces, plates or branding — the app's anon gate should return **clean** on all 13.
- All six fit "collectible… or similar", so `fits_category` should pass, but the subject-hint list (`_SUBJECT_HINTS["collectors"]`) contains no jewellery tokens beyond "watch"/"medal" — worth adding "jewellery, ring, necklace, pendant, brooch, chain" to both `_SUBJECT_HINTS` and `_CATEGORY_EXPECTS`.
- Trust-score: no authentication certificates exist for these items; for values this size that's fine (SANA/cert path only pays above ~R5k).

## 4. App validation results — LIVE RUN 19 Jul 2026 (2T, 369T→367T, Haiku 4.5)

Raw drafts: `Jewelry/APP_VALIDATION_RESULT_2026-07-19.json`. One primary photo per item (8044, 8042, 8040, 8037, 8035, 8034).

| Item | App title | Cond | App price | Key delta vs Fable |
|---|---|---|---|---|
| 1 Chain | "Gold-Plated Curb Chain Necklace, 9K Gold, Vintage" | excellent | R450–R650 | Self-contradictory; asserted 9K — no mark exists |
| 2 Pearls | "Freshwater Pearl Necklace with Gold Spacer Bead Earrings" | excellent | R280–R450 | Hallucinated an included earring |
| 3 Pentagon | "Gold Ornate Star Pendant, Floral Relief Design" | good | R180–R320 | Correctly hedged "gold-tone"; priced as costume |
| 4 Marcasite | "Vintage Silver Marcasite Ring, Garnet Stone, Red" | excellent | R520–R820 | Fabricated "Hallmarked 9K gold band"; condition inflated |
| 5 Garnet 9K | "9K Gold Hand-Set Garnet Ring, Vintage Estate Jewel" | excellent | R680–R1050 | Read hallmark correctly; "cabochon" wrong; ~40% under |
| 6 Citrine 9ct | "9K Gold Citrine Pendant, Leaf Filigree Mounting" | excellent | R750–R1200 | Good draft; "9K" vs actual "9ct"; bottom-of-range |

**Error pattern:** two fabricated fineness claims (1, 4), one hallucinated inclusion (2), 5/6 graded "excellent" (incl. the visibly dirty marcasite ring), prices compressed to a safe middle.

## 5. Comparison — what can already be said

| Dimension | App validation (Haiku 4.5, card-centric prompts) | Fable evaluation |
|---|---|---|
| Purpose | Produce sellable listing drafts fast, 2T, ≤10 photos | Appraisal-style scrutiny of identity, marks, risk |
| Condition vocab | mint→poor (cards); Tier-1 grades in TCGplayer terms | Jewellery-appropriate condition language |
| Hallmark handling | Not asked for in the prompt at all | Read JAYFOR 9K, 9ct, "Honey"; flagged the three unmarked pieces |
| Metal/stone risk | Will likely state "gold chain" from appearance | Explicitly refuses to confirm metal from photos; test instructions |
| Price basis | "SA collectables market values" from model prior | Ranged estimates conditional on test outcomes |
| Cost/latency | 2T, one call, seconds | Not a product path — this depth doesn't fit a 2T flow |

**Provisional verdict:** the app's checks are safety/anonymity gates plus a *listing generator* — they validate that photos are safe, on-category and sellable, not that the jewellery is what it appears to be. If collections is to carry jewellery credibly at launch, the two cheap upgrades are (1) jewellery tokens in the two category lists, (2) one line in the AI5 prompt: *"For jewellery: transcribe any visible hallmarks/stamps verbatim and never assert metal fineness without a visible mark."* LIVE-RUN CONFIRMED: the generator crosses from describing to inventing on jewellery — the prompt fix ("transcribe hallmarks verbatim; never assert fineness without a visible mark; say 'untested' when unmarked") is now evidence-backed, not theoretical.

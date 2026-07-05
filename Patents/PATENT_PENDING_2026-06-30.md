# PATENT PENDING — TrustSquare Provisional (OFFICIAL)
Lodged at CIPC Intellectual Property Online (iponline.cipc.co.za), 30 June 2026.

## Official details
- **Application No:** **2026/06760**
- **Filing / priority date:** **30 June 2026**
- **Status:** Processed
- **Type:** Provisional — Section 30(1), Patents Act 57 of 1978
- **Applicant & inventor:** David Maurice Conradie (natural person; self-filed, no attorney)
- **Filed document:** `patent-loop/TrustSquare_Provisional_FILING_with_Annex_2026-06-30.pdf` (spec + whitepaper annex, 14 pp, A4)
- **Official fee:** R60, paid by EFT (reference AFGGPO)
- **Title:** A COMMITMENT-GATED ANONYMOUS-INTRODUCTION MARKETPLACE PLATFORM WITH A HOLD-SETTLED DUAL-USE VALUE UNIT METERING BOTH HUMAN INTRODUCTIONS AND EXTERNAL MACHINE-INFERENCE SERVICES

## What this secures
- **Priority date 30 June 2026** for the invention as disclosed (spec + annexed whitepaper).
- "Patent pending" status.
- **Novelty gate CLEARED** → the whitepaper may now be published as a defensive prior-art disclosure.

## Deadlines / future patent actions
- **Complete specification due within 12 months → by ~30 June 2027** (the provisional lapses if missed). This is where claims are finalised and the 7 counsel items (CPA s63 wording, §101/COMVIK framing, professional novelty search vs US 8,095,377, applicant/assignment chain, C3/Pingsby, Banks Act/SARB, POPIA s71) are addressed — with a patent attorney.
- Optional **PCT / foreign filings** within the same 12-month convention window.

## Do next (launch sequence)
1. Download & store the official **filing receipt / acknowledgement** from IP Online.
2. **Publish the whitepaper** (defensive prior-art disclosure) — now unblocked.
3. **TRUSTSQUARE trademark** (word mark; classes 35/36/42) on the same IP Online portal (+ optional TUPPENCE word mark, + logo device mark).
4. **Paystack** register + integrate → test in app → plan launch cadence → launch.

## Post-filing addendum (2 Jul 2026) — claims truncation found in the filed PDF
Pre-publication review found the claims section of the UPLOADED document
(`TrustSquare_Provisional_FILING_with_Annex_2026-06-30.pdf`, sha256 03bc5aa3…) ends mid-word
inside dependent claim C4 ("…server-side recompute pat"). NOT in the filed document: rest of C4,
C5, C6, C8, C9, C10–C13, and the Abstract. Truncation already present in the 29-Jun frozen
FILING.docx (same write-truncation fault class as the whitepaper Claim-7 row; uncaught).
Full claim text survives in `patent-loop/working/patent.md`.
- Mitigation: a s30(1) provisional requires no claims; priority rests on the description, and the
  annexed whitepaper v3.11 discloses all truncated claim subject matter (§3.2, §3.4, §3.5, §3.8, §3.9, §4).
- ACTION (attorney, complete spec ≤ ~30 Jun 2027): restore full C4–C13 + Abstract from working/patent.md;
  confirm no corrective filing needed now. Details: `Patents/TrustSquare_WhitePaper_PrePublication_Accuracy_Review_2026-07-02.docx`.

## Publication set (2 Jul 2026) — supersedes PUBLIC_2026-06-30 for publication
- `patent-loop/TrustSquare_WhitePaper_PUBLIC_v3.12_2026-07-02.docx` / `.pdf` (12 pp) — A-fixes applied:
  §9 claim-basis reworded; §4 table completed (Claims 8, 9, C10–C13 rows); §3.2 internal counsel/launch-blocker
  wording removed; schema/tier/claims tables inline; Version History completed; illustrative Figures 1–6 embedded
  (match the spec's figure list; no new technical matter beyond the filed description).
  sha256 docx 3e72be52… · pdf 3d028a26… · text-of-record: `patent-loop/archive/whitepaper.v3.12-public-20260702.md`
- `Patents/TrustSquare_Claim_Visuals_PUBLIC_v4.html` — public-safe visuals (verdict panel, WEAK/AT-RISK tags,
  prior-art commentary removed; filing status + app number added; legacy tier names replaced).
  Claim Visuals v3 remains INTERNAL (counsel briefing aid) — do not publish v3.
- Claim-5 accuracy pass (2 Jul, David's check): whitepaper Claim 5 row + Claim Visuals v4 panel + §3.8 aligned to the
  PRODUCTION reach model per bea_main.py GET /listings + PRICING_CANON §2/§2a: buyer reach local (free) vs national+global
  (paid); seller multi-city on paid tiers; travel-planning categories (adventures/experiences, tours, accommodation,
  heritage) deliberately borderless. NOTE for counsel: this publishes the borderless-exemption behaviour (implemented
  28 Jun, pre-priority-date but NOT described in the filed annex) — if the carve-out mechanism should be claimable in the
  complete spec, weigh this disclosure; the published wording is functional only (no Branch-C mechanism detail).

## Publication runbook (2 Jul 2026) — how to post the whitepaper safely
Email is NOT publication — private sends create no citable, dateable prior art. The 5-Wave launch
emails (docs/TrustSquare_LaunchEmails_5Wave.docx) are founding-seller marketing; they should LINK to
the published whitepaper afterwards, not carry it.
1. David: final read of `patent-loop/TrustSquare_WhitePaper_PUBLIC_v3.12_2026-07-02.pdf` (sha256 3e9a7904…).
2. David: run `publish_whitepaper.bat` (staged; scp's whitepaper.html + PDF + visuals v4 to trustsquare.co).
3. Same day, capture independent date evidence:
   - Wayback: web.archive.org/save on /static/whitepaper.html and /static/trustsquare_whitepaper_v3.12.pdf
   - Zenodo (free DOI): upload the same PDF, note app 2026/06760 in the description.
4. Optional (counsel call): Research Disclosure / IP.com paid defensive-publication for guaranteed
   examiner-searched indexing.
5. Publish v4 visuals ONLY — Claim Visuals v3 stays internal.
### Publication evidence — CAPTURED 2 Jul 2026
- PUBLISHED on trustsquare.co: 2 July 2026 (~05:58 SAST / 03:58 UTC), served from /static/:
  - https://trustsquare.co/static/whitepaper.html
  - https://trustsquare.co/static/trustsquare_whitepaper_v3.12.pdf
  - https://trustsquare.co/static/trustsquare_claim_visuals_v4.html
- Integrity: server-side sha256 of the PDF verified in the publish run output = 3e9a7904bf84ed16687eb0e683e8c76887b8d2e1084415dec2fa2efe8658d1ec
  (identical to the reviewed local file; same hash printed on the public landing page).
- Wayback Machine (independent third-party timestamps, 2 Jul 2026 UTC):
  - landing 03:59:15 — https://web.archive.org/web/20260702035915/https://trustsquare.co/static/whitepaper.html
  - PDF 04:00:34 — https://web.archive.org/web/20260702040034/https://trustsquare.co/static/trustsquare_whitepaper_v3.12.pdf
  - visuals 04:00:56 — https://web.archive.org/web/20260702040056/https://trustsquare.co/static/trustsquare_claim_visuals_v4.html
- Zenodo DOI: SKIPPED by decision (David, 2 Jul 2026) — Wayback + hash chain deemed sufficient. Revisit with counsel at complete-spec stage if examiner-searchable indexing (Zenodo / Research Disclosure) is wanted.
- Housekeeping: first upload also left non-served copies in the webroot (/var/www/marketsquare/whitepaper.html, …pdf, …v4.html);
  harmless, remove at leisure via ssh. Publish scripts now target /static/.

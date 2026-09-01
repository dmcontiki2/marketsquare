## 2026-09-01 — Contagion model v1.5 + launch page carries the reply lane

**Model → v1.5 / Email Wave Plan v3.2** (`docs/TrustSquare_Contagion_Model_v0.2.html`):

- **New lever group "Credential lanes (RUL-072)": `fideW` + `fideUp`.** FIDE-TRAINERS-1 already
  harvested 4,237 unique titled trainers (NI 1,680 · FI 1,126 · DI 1,023 · FT 408; IND 934, ~7x the
  next federation; RUS 93; RSA 23). **Modelled honestly as a CONVERSION lane, not a supply lane** —
  the registry holds credentials and identities but **no emails**, so it never enters the wave
  machine and `fideW` adds zero prospects. It lifts the organic and referral paths only (a tutor
  arriving under their own steam claims a FIDE ID and wears a verified credential tier). Wiring an
  emailless registry into outbound would have been a straightforward lie about where growth comes
  from. `fideUp` defaults to a modest 1.35 and its note says plainly that it is an UNMEASURED
  assumption until the claim flow ships.
- **Measured reality replacing estimates in two lever notes.** `scrapeWk`: the pool is **3,784
  prospects, all with an email**, up from 1,519 on 30 Aug (ZA 2,827 · US 406 · UK 199 · FR 163 ·
  AU 114 · PT 39). `varsityW`: the US pool already holds **147 `us_university_tutors`** plus Tutors
  72 and Tutor Institutions 38 — so RUL-059's lane is *fuelled and held*, not empty and held.
  Leaving it at 157 is a SEND decision, not a scraping one.

**Launch page** (`CityLauncher/citylauncher_launch.html`) — new card **"0 · Before you run a wave —
where the replies go"**, placed above the wave runner because it is a precondition on pressing those
buttons:

- The four reply classes with their colours, matching the dashboard card exactly (machine/grey ·
  FAQ/green · opt-out/red · commercial/gold — "the only tile that wants you").
- Current true state: deployed 16:09:46Z, machine-silence live, `OUTREACH_AUTO_SEND` unset and
  verified unset in the live process env, everything else drafting and queuing.
- **A hard amber gate on non-ZA waves.** The FAQ class answers from hardcoded South African facts,
  so a US/UK/AU prospect asking which cities we cover would get a confident answer about
  Johannesburg. Wave 2 (US+GB), Wave 3 (AU/NZ) and later rings must not fire until the canon block
  is market-aware or FAQ falls back to commercial for non-ZA senders. Tracked as RG-0236.

Verified: every `<script>` block in both files parses (`node --check`); the launch page parses as
HTML; model levers wired into the existing `L.`/`DEFAULTS` pattern with single-match anchors.
Backups kept beside both files.

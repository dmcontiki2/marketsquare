## 2026-08-21 — AIPROV-VERIFY-1: the AI Providers dot stops lying about liveness

David asked why the OpenAI row was solid green when he had never tested it. He was right to ask.

- **The bug:** the dot and the `ACTIVE` badge were painted from `p.id===active` and `p.available`.
  The server computes `available` as `bool(ai_provider.envkey("OPENAI_API_KEY"))` — key **presence**,
  not a network call. `/flags` publishes no liveness field at all. So a revoked, over-quota or
  simply wrong key rendered as a healthy green lane — on the lane serving live traffic.
- **The fix (client-side, no extra API spend):** an unproven lane now shows **amber ·
  UNVERIFIED** with "key present & lane selected — but no live call verified. Press Test."
  A failed test shows **red · TEST FAILED** with the reason. Only a successful
  `/admin/ai-test` round trip earns green, stamped with the time, and it decays after 24h.
  Result cached in `localStorage.ms_apv3_verify`. A dot-key legend sits under the rows.
- **Also fixed:** the Test 401 line read `Admin session expired — reload + PIN` inside the
  provider card, which reads like the provider dropped. It now says plainly that the
  **dashboard's own login** expired, the test never ran, and it is not a provider fault.
- Ledger: **RG-0130** LOCKED, scope all three lanes.
**Two more lies on the same card, same class, both fixed (RUL-037 — CTO call, not David's):**

- **The banner.** `_apv3PendingFlip` was a hardcoded `true` nobody remembered to clear, so for a
  week the page said the flip was "pending: server key, live-seam golden run, spend attribution"
  when the key was present, the flip had been live since 14 Aug 20:05 UTC and P6 spend attribution
  landed 15 Aug. Constant deleted; the banner derives from live `/flags` and from the funnel's own
  reconciled gate. It now says the flip is DONE and names the one thing genuinely outstanding.
- **The funnel strip.** It showed `openai (golden-set-passed)` on all four tiers.
  `ai_price_card.json` claimed `gate: golden-set-passed` from GS-OAI-V1 — which ran on a **sandbox**
  key with raw vendor calls — while `ai_scoreboard.GOLDEN_PASS` excluded openai *by design* pending
  the server-key run (RG-0016). Two files, one fact, and the dashboard rendered the flattering one.
  **GOLDEN-AUTHORITY-1:** `price_truth.py` now reconciles every gate label against `GOLDEN_PASS` in
  both the report and the `--snapshot`, and raises rather than defaulting open if the scoreboard
  can't be read. Snapshot regenerated: openai reads `pending-golden-set` on all four tiers.
- Ledger: **RG-0131** LOCKED (single authority). **RG-0132 OPEN** — the base lane serving 100% of
  live traffic has no production golden run on record; `scripts/golden_seam_v2.py` needs one run on
  the Hetzner box with the production key, then openai joins GOLDEN_PASS (P3). Tracked as an OPEN
  ledger entry rather than a sentence to David, per RUL-037.

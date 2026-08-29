## 2026-08-28 — CONTAGION-GEO-1 (Pacific added · market barriers modelled · Canada and Mauritius were never excluded)

David asked why we do not spread into Canada, Mauritius, the Pacific islands and China, and noted the
reasons could be different. They are, in four distinct ways. All four verified against primary sources
— statute text, regulator sites, national censuses and company filings — not commentary.

### Canada and Mauritius were never excluded

Both have always been in the city data and both light up on their own, by corridor and shared language,
without ever receiving a wave: Toronto wk 38, Montreal wk 36, Vancouver wk 45, Port Louis wk 42 (seed 7).
They carry `pr = 0`, which is why they are invisible in the wave board, not absent from the world.

- **Canada** — no legal barrier. PIPEDA attaches on a real-and-substantial-connection test with no
  registration step; Bill C-27 / CPPA died on prorogation Jan 2025 and was not re-tabled. Québec Law 25
  s.17 wants a documented PIA before PI leaves the province. **The real trap is CASL**, not privacy —
  consent for commercial electronic messages, per-violation penalties, and it bites a listings app that
  emails buyers. Verdict: right to ignore commercially, wrong to blame law or payments.
- **Mauritius** — the strongest of the four, and the belief keeping us out may be false. DPA 2017 s.14
  registration is mandatory, but **s.3(5) confines the Act to a controller established in Mauritius, or
  one using equipment in Mauritius**. On the plain text a South African controller on German servers is
  out of scope. NOT settled — "uses equipment" is lifted from the old EU Directive, where cookies and
  scripts on a device once counted, and there is no Mauritian case law or DPO guidance. 1.24m people,
  73.3% online, corridor 2.0 from ZA. Paystack is not live there, so ZAR card charging.

### The Pacific was our gap, and it is now filled

Fiji, Samoa, Tonga, Vanuatu, PNG, Solomon Islands, New Caledonia and French Polynesia were absent from
`CITIES` entirely — 121 of 177 mapped countries had no city at all. Eleven Pacific cities added from the
national statistics offices: Port Moresby 757k (PNG NSO 2024), Greater Suva 268k (FBoS 2017), Lae 203k,
Grand Nouméa 174k (ISEE 2025), Greater Honiara 170k (SINSO 2019), Papeete urban zone 124k (ISPF 2022),
Lautoka 72k, Port Vila 49k (VNSO 2020), Apia 36k (SBS 2021), Greater Nuku'alofa 34k. Coordinates from
OpenStreetMap/Nominatim. Traps recorded in the code so nobody re-derives them wrongly: **PNG's national
population is genuinely disputed** (2024 census 10.19m against a 2021 modelled 11.78m NSO still
publishes alongside it); **New Caledonia is shrinking** (Nouméa 94,285 → 85,976, net migration ≈ −18,000
after the May 2024 unrest, and SPC's projection runs ~11% above the actual census — use the census);
**Papeete is only the third-largest commune** in French Polynesia, behind Faaa.

Filling the hole does not make the case. The bloc is ~12.9m of whom **10.2m is PNG at 18.8% internet** —
the worst combination in the set. Strip PNG and it is 2.75m across eight scattered groups with no card
culture (Fiji runs on M-PAiSA and MyCash, which Paystack cannot touch). The two that would work are
New Caledonia and French Polynesia — 544k, French, inside CNIL, and **not in SEPA**, though their cards
are French-bank Visa/MC and clear normally.

### Two markets are now modelled as walls, with the reason stored

New `MARKET_BARRIER` table. A barriered country carries **no addressable market at all** (`N = 0`,
`GP = 0`), paints dark red on the map with its own legend entry, and raises a diagnostic.

- **Vanuatu — an outright legal blocker.** Data Protection and Privacy Act No. 13 of 2024, in force
  2 Jan 2025: s.2(1)(e) extraterritorial reach over offering services to people in Vanuatu whether or not
  payment is required; **s.15(1) — data generated or collected in Vanuatu must not be used elsewhere
  without prior Ministerial authorisation**, and no adequacy regulations exist. Our servers are in
  Germany. Port Vila now never lights up.
- **China — three independent blockers, any one fatal.** (1) PIPL Art. 3(2)(1) reaches us
  extraterritorially and **Art. 53 requires an in-China representative regardless of user count** — the
  2024 Cross-Border Data Flow Provisions exempt us from the transfer mechanism under 100,000 users but
  not from Art. 53. (2) **No payment rail a South African entity can reach**: Paystack has no
  Alipay/WeChat/UnionPay channel anywhere; Stripe lists SA as "Extended network" pointing back at
  Paystack; every cross-border PSP holding the China connection needs a merchant entity in a jurisdiction
  it supports, and none supports SA. UnionPay has 10.2bn cards; Visa holds no clearing licence.
  (3) **The category is held** — Alibaba's own 20-F calls Xianyu China's largest C2C marketplace by GMV
  and has published no absolute number since Q2 2021.

**Correcting a common assumption, recorded so it does not resurface:** the **ICP filing is not the China
blocker**. It attaches to operating from inside China; we do not need one and could not obtain one — a
filing goes through a mainland host against a mainland business licence, and foreign equity in a VAS
licence is capped at 50% outside the Oct 2024 pilot zones (13 firms approved by Feb 2025, all large
multinationals).

### Also

New `barriers` lever (default ON). Turning it off asks the counterfactual — but it barely moves anything,
because China was never in `CITIES` to begin with, so the counterfactual only frees Vanuatu. **Sizing
China would mean adding its cities, which is a decision to take deliberately, not a data fix to slip in.**
City count 171 → 181.

**Deliverable:** `Market Entry — Canada, Mauritius, Pacific, China — nice.docx`.

**Verified:** `node --check` clean; headless page harness green; Port Vila confirmed never active while
every other new Pacific city lights up (Suva wk 43, Port Moresby wk 39, Honiara wk 51, Apia wk 55,
Nuku'alofa wk 62, Nouméa wk 49, Papeete wk 52); backup `*.bak-prev09-*`.

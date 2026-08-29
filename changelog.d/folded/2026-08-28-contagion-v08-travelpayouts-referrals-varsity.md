## 2026-08-28 — CONTAGION-V08-1 (Travelpayouts · a real referral loop · the RUL-059 university lane)

Continues the contagion-model work folded from 27 Aug. Model file unchanged in name:
`docs/TrustSquare_Contagion_Model_v0.2.html`, now labelled v0.8 internally.

### Travelpayouts (TP-LINKOUT-1, partner 758984)

Modelled as commission on planner click-outs: flights at 1.1–1.3% (Data API live), tours at ~8%
(DECLINED 24 Aug, gated behind `tpToursW`, default 157 = still declined). Implementation constraints
carried into the code comments so a later session cannot regress them: server-side link-out, host
allowlist, fails closed, dark by flag, RG-0181 asserts the invariant, and **no third-party script runs
on any app page** — RG-0025 was INVERTED after the 3–4 Aug breach and asserts the absence. Flight
basket priced from our OWN 1 Aug dry run in native ZAR (JNB-CPT R2,267 · JNB-DUR R1,348 ·
JNB-WDH R5,080 · JNB-LHR R11,417, mean ≈ R5,000 ≈ $270).

**The finding is not the one expected.** David's premise that the planner runs are where the gross of
the business sits is **correct** — but the money in a planner run is the Tuppence for the plan, not the
affiliate commission on top of it. Per run, at mid parameters:

| Line | Per planner run | Share of the plan fee |
|---|---|---|
| Tuppence for the plan itself (free/2T mix) | **$1.40** | 100% |
| Travelpayouts, flights only | $0.01 | 0.6% |
| Travelpayouts, tours at the mid mix | $0.01 | 0.8% |
| Travelpayouts, every parameter at its high end | $0.24 | 17.3% |

For tour commission to **match** the plan fee at mid click-out and booking rates, the average tour
basket would have to be about **$6,481** — a multi-day guided tour or a package, not a $70 activity.
At scale (week 104, tours approved) Travelpayouts runs at ~$33k/mo against $5.6M/mo total: **1% of
revenue.**

What it genuinely is: **the only revenue line in the model that needs no payment rail, pays no
processing fee and creates no merchant-of-record exposure** — the F4 introduction doctrine working in
our favour. It earns worldwide from day one regardless of `liveKeysW`, and it is pure margin. A good
garnish, not the meal. Two levers decide whether it becomes material and both are ours: `tpTourMix`
(what the planners surface — tours pay 6.7× flights) and the tour basket size (packages and
expeditions, not activities). The $400 minimum payout is surfaced in the diagnostic, because early
commission accrues without landing in the bank.

### Referrals — asked for, and they were genuinely absent

What existed was a `referral` **lever** that multiplied ambient word of mouth. A referral **programme**
is a different thing: instrumented, incentivised, attributable. New parameters `refRate`, `refTake`,
`refKeep` (referred users churn less — applied as a divisor on churn for the referred share of the
base) and `refCostT` (granted Tuppence per successful referral, real money at $2/T, now flowing into
the net line). A new `REF` compartment tracks the referred population so the retention advantage decays
correctly. Worth at week 104, 24 seeds: **28,646 referred sellers**, revenue $5.52M → $5.68M; with the
incentive at maximum, 31,650 referred and $6.19M.

**The honest headline is that it cannot be switched on.** `refW` defaults to 157 = never, because there
is no `referred_by`, no invite code and no `inviter_id` anywhere in the schema, and
`users.referral_count` says *"not yet tracked. Always missing."* The diagnostic now says so whenever the
programme is off: Airbnb's own engineering blog puts its referral programme at about 25% of new bookings
in some markets, and ours is one column and one hidden input away from existing. Same missing instrument
that sits at #1 on the Telemetry tab.

### RUL-059 US university-tutor lane

Encoded literally from the ruling, including the parts that constrain it:

- **(a) UK is OUT** — named academic addresses are personal data under UK GDPR and PECR's
  corporate-subscriber allowance is not clean for named individuals. The lane is US-only.
- **(c) NO SEND by default** — `varsityW` defaults to 157, with the ruling's reasoning in the lever note.
- **(d) Separate sending subdomain, modelled literally** — the lane carries its OWN `varsityDecay`, so a
  bad campaign into .edu cannot touch the deliverability the South African core depends on. That is the
  whole point of the ruling and it is now a mechanism, not a comment.
- **(e) Eleven US cities, no new geography** — `VARSITY_CITIES` names them, and they matched the model's
  own US cities carrying a prospect pool **exactly**: New York, Los Angeles, Chicago, Houston, Phoenix,
  Philadelphia, San Antonio, San Diego, Dallas, San Jose, Austin. Denver and the rest carry zero. A good
  independent cross-check on both the ruling and the model's city data.
- **Its own list.** The first cut wrongly drew from the CityLauncher city pool — wrong twice, because
  that pool is private individuals and the main ladder has already emptied it. RUL-059 commissions
  `scraper/sources/us_university_tutors.py`, so the lane now has its own pool sized by the campaign the
  ruling authorises. That correction took the lane from 1 signup to 27.
- **Capacity, not headcount** — new `varSeats` (1/3/8): a test-prep centre or campus learning-support
  service brings several tutors on one account, which is why a small list can still matter.

Effect on the whole at week 104 (24 seeds): median sellers **276,761 without** the lane, **267,016 with**
it — within noise, and **not a growth lever**. That is the ruling being right rather than the lane being
useless. RUL-059's own rationale is depth first: the binding constraint is liquidity, and the lane's
value is Tutors inventory depth in eleven cities where the scrape found 59 / 18 / 3 / 12 prospects — not
seller count.

### Verification

`node --check` clean on the full inline script; headless DOM harness runs the real page end to end
(both simulations, both ensembles, the toggle both ways, the money strip, all four panel tabs); the
eleven-city cross-check above; backups `TrustSquare_Contagion_Model_v0.2.html.bak-prev08-*`.

Standing caveat unchanged: levels remain in the runaway regime and are not forecasts. Read the per-run
arithmetic and the relative effects, never the totals.

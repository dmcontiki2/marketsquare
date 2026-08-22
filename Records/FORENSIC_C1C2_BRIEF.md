

===== FORENSIC_AUDIT_CYCLE1 — nice.docx =====
MarketSquare — Launch-Readiness Forensic Audit
Cycle 1 · Claude's forensic + HALT stress pass · trustsquare.co
D-7 gate review · Saturday 22 August 2026 · Soft launch Fri 29 Aug · Full launch Mon 1 Sep 2026 (RUL-001)
Evidence ladder in force: PROBED > EXECUTED > READ > RECALLED. Only PROBED live measurements are reported as fact. A dimension with no live instrument is scored NOT MEASURED, never assumed green.
Scoreboard: 2 RED · 6 AMBER · 2 GREEN. The app's own auth surface is genuinely hard (no injection, no enumeration, no exhaustion, fails closed) — the RED is the burnt credentials that sit in front of it, not the code behind it.
▍ The ten-dimension scorecard
Change since the 15 Aug launch bar: IL-01 (GET /tuppence/balance?email=) is now authenticated — probed 401 today, was OPEN on 15 Aug. That launch-blocker is cleared. The secrets blocker is not.
▍ Method — probe first, then read, then over-stress
Cycle 1 ran the live probe sweep before touching a single doc: GET /health, /flags, /auth/providers, /dashboard/bit, /id-verify/status, plus /listings, /demo-listings, /dashboard/summary and a battery of hostile requests; then scripts/regression_ledger.py, rulings_check.py and predeploy_check.py from the repo. Only after that did it cross-read the canon (FINANCE_CANON, PRICING_CANON, canon.yml, LAUNCH_BAR, OPEN_LOOPS, THIRD_PARTY_LAUNCH_REGISTER). Where a doc and a probe disagreed, the probe won.
▍ The HALT stress lane — operating and destruct limits
HALT over-stresses each dimension past its rated spec to precipitate the latent weak link, then records where it degrades (operating limit) and where it breaks (destruct limit). A weak link found here is a win — caught in the lab, not on launch day.
Security — actively attacked, not merely inspected
Every probed attack vector held. This is the strongest dimension of the app itself:
SQL injection: /listings?category=' OR 1=1-- matched 0 rows — the string was treated as a literal value (parameterized). Not injectable.
Resource exhaustion: /listings?limit=99999999 still returned the capped 66 rows. The server bounds its own result set.
Auth fail-closed: POST /intros with a well-formed body → 401 'Please sign in'; POST to a forged credit endpoint → 404; Paystack-webhook forge (no signature) → 404. Admin/ops routes → 401.
Enumeration: /tuppence/balance?email= returns 401 for real and fake emails alike — no existence oracle. IL-01 is now authenticated (was the open launch-blocker on 15 Aug).
Oversized input: a 2 MB junk body to POST /app/fault → 422 rejected.
Server & scalability — operating limit, honestly NOT MEASURED at launch scale
A bounded synthetic load ramp was attempted, but Cloudflare bot-management returned 403 to the non-browser client at the edge (confirmed: default Python UA → 403, browser UA → 200). The load never reached the origin, so it measured the edge, not the box. Per the evidence ladder this is scored NOT MEASURED — I will not bypass the edge protection to stress the production box 7 days before launch (HALT safety boundary). What IS known: today's load is trivial (2.88 MB SQLite, 104 listings, ~120 ms reads even through the edge). The operating and destruct limits at launch concurrency remain unknown by design of a box that has never seen launch traffic.
Economic model — stressed to find where it breaks
The unit-economics model (1T = $2 fixed; Free/Starter $5/Pro $20 sellers; Global $5 buyers; fixed opex ≈ €28 server + ~$135/mo accountant + capped AI COGS) was stressed with 2× churn (10%), a 40% intro-demand drop, a 15% ZAR depreciation, and a vendor reprice (infra→$40, AI ceiling→$60, 5% MoR fee) ALL AT ONCE:
Base case: profitable at 60 / 600 / 6000 sellers (net ≈ $388 / $5,373 / $55,396 per month).
Combined stress: STILL profitable at all three scales; break-even falls at ~25–30 sellers.
Even a Free-heavy conversion collapse (5% Pro, 10% Starter, 1 intro/seller) stays marginally positive at 60 sellers under full stress.
Robustness — dependency failure
AI-lane failover is proven in the decision layer (RG-0128, 13/13 via the failover harness that stubs only the vendor sockets) and three lanes are live right now, so a vendor outage has somewhere to move. Killing live Paystack, Resend or Travelpayouts was out of bounds (can't safely kill production dependencies), so their single-fail and double-fail behaviour is READ from the fail-closed flags and supplier-fallback doctrine, not PROBED. Scored AMBER for that gap.
▍ The blocker — confirmed, not cleared
The plan named one going-in blocker and required Cycle 1 to confirm or clear it. It is CONFIRMED still open (grade: READ — the live server env cannot be probed from here, so the disk record stands as the honest worst case):
OPEN_LOOPS B1 / DW-057 (20 Aug) + DW-029 (7 Aug): the full production secret set was printed into a transcript a SECOND time and remains unrotated. Partial rotations happened earlier (MS_JWT_SECRET on 4 Aug; a maint key on 17 Aug) but not the DW-057 set.
RUL-034 / WAF-OPEN-1: the Cloudflare edge allowlist rule is deliberately disabled for the rest of pre-launch.
Probed reality: the origin gate is also effectively down — the app shell (417 KB), live /listings and /dashboard/summary all return 200 with no cookie. So the '29 Aug exposure event' the launch bar warned about is the LIVE condition today, 7 days early.
▍ HALT weak links precipitated — and what was hardened
Discipline note: the git-lock regression is the only weak link that was mine to fix reversibly and unattended — it is fixed and its LOCKED assertion already holds. The rest are either reserved to David or cannot be safely tested against production; adding new load-bearing ledger entries in an unattended run would be the wrong kind of change, so they are documented here as ready-to-lock rather than forced in.
▍ Cycle 3 sizing (no spend yet)
scripts/peer_pack_ai.py built the 119 KB code extract. A --dry-run of peer_review.py (gpt-5.6-terra) on the extract + FINANCE_CANON + PRICING_CANON sized one security lens at ~34,700 input tokens, cost ceiling ≈ $0.26. Six passes (security, cost, performance, privacy, maintainability, plus a full HALT-focus pass) put the total ceiling at roughly $1.00–1.60, with likely actual spend ~$0.30–0.60 on Terra. OPENAI_API_KEY is present. No paid call has been made — that is David's reserved approval.
▍ Reserved to David
The launch GO / HOLD ruling. Two REDs at D-7 = HOLD posture by the 15 Aug rule; the ruling itself is David's.
Rotating the exposed production secrets (RUL-027 lockout risk + RUL-037 credentials) — the one action that clears both REDs.
Approving the small OpenAI spend for Cycle 3 (~$1.00–1.60 ceiling).
Ruling the pre-launch gate posture and any launch scope/date change.
Cycle 1 authored under the Evidence Ladder, 22 Aug 2026. Next: Cycle 2 (doctoral peer analysis, fresh Fable sub-agent) then Cycle 3 (OpenAI peer review, on David's go).
★ Headline verdict  Two dimensions land RED — Hardening and Hack-proofness — and both trace to ONE root cause: production secrets exposed twice (DW-029, DW-057) and still unrotated, while the pre-launch gate and Cloudflare WAF allowlist are BOTH effectively down (probed: the app shell, live /listings and /dashboard/summary all answer 200 to an anonymous client). By the 15 Aug rule, any RED at the D-7 review = HOLD declared that day. The launch go/hold ruling is reserved to David. The good news buried in the RED: this is a single, well-understood, David-clearable blocker — not a systemic defect. Rotate the exposed secret set and rule the gate posture, and both REDs clear. The other eight dimensions are AMBER or GREEN.
# | Dimension | Verdict | Evidence | Blocker? | Single most important finding
1 | Business viability | AMBER | PROBED+READ | No | 59 sellers / 104 listings / 115 lifetime intros live — the two-sided market functions. Demand at PUBLIC scale is unproven.
2 | Financial growth | AMBER | EXECUTED+READ | No | Ramp is credible and profitable 60→6000, but the growth story rests on intros/seller/mo + paid-conversion — both unmeasured.
3 | Profitability / unit economics | GREEN | EXECUTED | No | Break-even ~25–30 sellers even under combined HALT stress. Cost never breaks it; only revenue realization does.
4 | Server capability | AMBER | PROBED (today) / NOT MEASURED (launch) | No | Healthy today (p50 ~120ms, SQLite 2.9MB). Launch-scale load NEVER measured; edge blocks synthetic load.
5 | Robustness | AMBER | PROBED+EXECUTED+READ | No | 3 AI lanes live + failover proven in the decision layer (13/13). Paystack/Resend/relay single-fail behaviour NOT live-tested.
6 | Reliability | GREEN | PROBED | No | BIT 8/8 fresh, auth fails closed, no demo bleed, ledger 126/129 holding. Gap: no independent external uptime monitor.
7 | Maintainability | AMBER | PROBED+READ | No | bea_main.py is a 1.0 MB single file with 12 files uncommitted on disk. Strong change machinery offsets it, but 2am-diagnosis risk is real.
8 | Scalability | AMBER | READ+PROBED | No (at 60) | SQLite today (fine at 60). Postgres move (RUL-024) NOT executed; ~79 SQLite-coupled call sites remain. First wall at 600–6000.
9 | Hardening | RED | PROBED+READ | BLOCKER | The 29 Aug gate-down exposure is LIVE NOW, 7 days early: gate down both halves + WAF allowlist down + secrets unrotated.
10 | Hack-proofness | RED | PROBED+READ | BLOCKER | App auth is hard, but exposed unrotated secrets mean one stolen credential bypasses all of it. Blast radius = total.
✓ Probe facts (grade: PROBED)  /health ok, v1.3.1, DB 2.88 MB, integrity ok · /dashboard/bit 8/8 PASS (fresh, 04:33Z) · /auth/providers google=true apple=false · 3 AI lanes live (anthropic/openai/scaleway all available) · regression ledger 129 entries, 126 holding, 0 regressed (after healing one tooling regression this session), 3 open · rulings_check 39/39 reflected · predeploy verdict ok.
⚠️ Security destruct limit (the one that matters)  The destruct limit for security is NOT in the code — it is the credential layer in front of it. Production secrets (MS_API_KEY, PAYSTACK_WEBHOOK_SECRET, RESEND_API_KEY, CF_CACHE_TOKEN, MS_DEPLOY_TOKEN, FOUNDERS_ID_SALT, TRAVELPAYOUTS_TOKEN, NUMISTA/JUSTTCG) were printed into a transcript TWICE and remain unrotated per STATUS.md + OPEN_LOOPS B1. A valid stolen MS_API_KEY walks straight past every check above. This is the RED.
★ Economic weak link  The economics do not break on cost — the fixed base is tiny and the introduction fee is ~100% margin. The single variable that breaks the growth story is REVENUE REALIZATION: intros per active seller per month × paid-tier conversion. Both are assumptions today. At 59 sellers the platform has 115 LIFETIME introductions — the monthly rate and the paid-conversion rate are not yet measured. That is why Profitability scores GREEN (structure is sound) but Financial growth scores AMBER (the demand inputs are unproven).
→ What clears it (David's reserved action)  Run ROTATE_SECRETS.bat, then hand-edit the systemd unit for MS_API_KEY / MS_DEPLOY_TOKEN / FOUNDERS_ID_SALT; Claude then drives the vendor-side rotation (Resend → Cloudflare → Numista/JustTCG/Travelpayouts). This is reserved to David under RUL-027 (lockout risk) and RUL-037 (spend/credentials). Once rotated and the gate posture ruled, Hardening and Hack-proofness both clear — the underlying app auth already passes every probed attack.
Weak link | Where it surfaced | Status this session
Stranded git locks (.git/index.lock + HEAD.lock >60 min) | Regression ledger RG-0015 tripped RED at the start of the run | FIXED — healed via scripts/git_unlock.py (rename to stale_locks/); ledger re-run clean, 0 regressed. Already LOCKED as RG-0015.
Gate-down exposure live 7 days early | Probe: app shell + /listings + /dashboard/summary all 200 anonymous | Reserved to David (gate posture + secret rotation). Recommended LOCKED assertion: key data endpoints require auth OR gate state is explicit (extends RG-0094).
Unrotated exposed secrets | STATUS.md + OPEN_LOOPS B1 | Reserved to David (RUL-027/037). The blocker.
No launch-scale load instrument | HALT load ramp blocked at the Cloudflare edge | Fast-follow: a browser-UA, rate-bounded load probe should be built and run in a window David approves, or against a staging copy.
openai base lane has no production golden run | Ledger RG-0132 OPEN; openai serves 100% of live traffic | Fast-follow: run scripts/golden_seam_v2.py on the server with the production key, then add openai to GOLDEN_PASS.
ℹ️ Note on the verdict  Nothing in this audit says the product is unsound — the economics are robust, the app auth is hard, the instruments are honest. It says the security FLOOR (G2 on the launch bar) is not yet laid: burnt credentials in front of a gate that is already down. That floor is one focused piece of work, reserved to David, and the tooling for it is ready.


===== FORENSIC_AUDIT_CYCLE2_PEER — nice.docx =====
MarketSquare — Launch-Readiness Forensic Audit
Cycle 2 · Doctoral Peer Review (adversarial) · Fresh reviewer, no stake in Cycle 1 · trustsquare.co
D-7 gate review · Saturday 22 August 2026 · Soft launch Fri 29 Aug · Full launch Mon 1 Sep 2026 (RUL-001)
Mandate: not to re-grade the app, but to try to BREAK the audit — catch the correlated blind spot of Claude grading Claude. Evidence ladder in force: PROBED > EXECUTED > READ > RECALLED. Every green re-checked against a live probe this session; a green sourced from a doc is downgraded on sight.
▍ Re-verification of Cycle 1's load-bearing claims (all PROBED this session)
▍ Dimension-by-dimension: UPHELD or OVERTURNED
▍ Corrected scorecard (Cycle 2 revised verdicts)
Two GREENs overturned to AMBER; two REDs upheld (one strengthened); six AMBERs upheld. Net board: 2 RED · 8 AMBER · 0 GREEN.
▍ What Cycle 1 got wrong or under-weighted
1. Missed an active information-disclosure leak. — GET /dashboard/summary, anonymous and cookieless, publishes the WAF-down state, the origin-gate-only-guard state, and the exact server sizing. Cycle 1 saw the 200 and stopped; it never read the body. This is a discrete information-disclosure finding that hands an attacker a map, on top of the gate being down.
2. Profitability GREEN is assumption-fragile. — 'Break-even ~25-30 sellers even under combined HALT stress' is true only because the combined stress hit COSTS (churn, FX, vendor reprice) while leaving the demand side near-intact (2 intros/seller/mo). That intro rate is ~4x the observed 0.49 (115 lifetime intros / 59 sellers over ~4 months). Stress the demand side to the observed rate and break-even is 49-103 sellers, above the 60-seller launch target, with net@60 negative under freemium-realistic conversion. GREEN was not warranted.
3. The 'edge blocks load' basis is falsified. — Cycle 1 justified NOT MEASURED with 'default Python UA -> 403 at the edge.' My probe: default curl, python-requests, and browser UAs ALL return 200. The edge is not blocking non-browser clients. The verdict (NOT MEASURED) is right; the reason is wrong. The honest reason is the safety choice not to load-test production pre-launch — which should be stated as such, not dressed as a technical impossibility.
4. Reliability GREEN despite naming the gap that voids it. — Cycle 1 explicitly named 'no independent external uptime monitor' as a gap, then scored Reliability GREEN. Reliability is a property over time; an 8/8 snapshot (with some sub-checks sourced from disk, not the live box) cannot establish it. Snapshot-green is not reliability-green.
5. Churn modelled as a haircut, not base erosion; RG-0132 under-weighted. — At 20%/mo churn you need ~12 gross seller adds/month just to HOLD 59; at 6/mo the base collapses to ~30 within a year. Cycle 1 treated churn as a static revenue haircut and missed the base-erosion dynamic entirely. Separately, RG-0132 (the openai base lane serves 100% of live AI traffic with NO production golden run on record) was filed as a footnote fast-follow; 'the only lane every user hits has never had its output validated in prod' deserved more weight.
▍ Independent economic model (recomputed from PRICING_CANON, not from Cycle 1)
Inputs: 1T = $2 fixed; buyer pays 1T per introduction ($2, net of ~2.9% Paystack). Seller tiers Free $0 / Starter $5 / Pro $20. Fixed opex from FINANCE_CANON: accountant R2,000 + R500 software (~$139), Hetzner CPX32 (~$30), AI COGS capped. Base opex ~$194/mo; stress opex ~$255/mo (FX + AI ceiling). Break-even = opex / revenue-per-seller.
Reality anchor: 115 lifetime introductions / 59 sellers = 1.95 intros per seller LIFETIME, i.e. ~0.49 per seller per MONTH over ~4 months live. Cycle 1 assumed 2.0 per seller per month — about 4.1x the only observed data point.
Churn dynamics (Cycle 1 omitted): starting at 59 sellers, 20%/mo churn needs ~12 gross adds/month just to stand still. At +6/mo the base falls to ~30 within a year; at +12/mo it holds ~60; at +18/mo it grows to ~88. Churn is a base-erosion risk, not merely a revenue haircut — the growth story lives or dies on acquisition out-running 20% monthly churn.
▍ Coverage gaps — what Cycle 1 did not look at
Anonymous information disclosure via /dashboard/summary (infra sizing + WAF/gate-down state) — probed, confirmed, NEW.
Rate-limit / lockout posture — I probed it (429 after 7 fails); Cycle 1 never did. It HOLDS (a positive, adds to app-auth hardness).
POPIA/PII exposure of the anonymously-readable endpoints — I probed /listings (0 emails, 0 phones, no street_address, no demo bleed) and /dashboard/summary (operational text, no customer PII). PII exposure is low; the disclosure risk is operational, not personal-data.
Legal-doc reachability (G7) — /terms and /privacy return 200 (EULA is served at /terms, byte-identical to eula_clean.html; there is simply no /eula alias — a non-issue). Note privacy.html carries a 'pending attorney review' provenance flag (LEGAL-COUNTRY-1) — a known follow-up, not a blocker.
Churn base-erosion dynamics and the ~4x intro-rate gap — quantified above.
BIT provenance — some BIT sub-checks are disk/source-sourced, not live-probed; the '8/8 fresh PROBED' framing is mixed-grade.
RG-0132: base lane (100% of live AI traffic) has no production golden run — a launch-relevant quality unknown, not a footnote.
Backup/restore not actually exercised in either cycle — the /backup machinery exists (READ) but a restore was not proven this session; remains an untested-recovery unknown.
▍ Bottom line
The audit holds where it matters most and improves where it was soft. Cycle 1's central finding — two REDs, a single well-understood root blocker (unrotated exposed secrets while the gate and WAF are down), and a HOLD posture at D-7 — survives adversarial re-probing intact and is reinforced: the /dashboard/summary disclosure makes the hardening picture worse, not better. Where Cycle 1 was too generous — the two GREENs — the corrected board is 2 RED · 8 AMBER · 0 GREEN. Profitability is contingent on unmeasured demand (real break-even ~49-103 sellers, not ~25-30), and Reliability cannot be GREEN without a time-series and an external monitor. None of this is a GO signal; two of the corrections push further toward HOLD. The HOLD-vs-GO picture does not change: it is HOLD until the secret set is rotated and the gate/WAF posture is ruled, and it now rests on firmer evidence than Cycle 1 provided.
Cycle 2 authored under the Evidence Ladder by a fresh adversarial reviewer, 22 Aug 2026. All greens re-probed live; two overturned. The launch GO/HOLD ruling, secret rotation (RUL-027/037), and the Cycle 3 OpenAI spend remain reserved to David.
★ Peer verdict, one line  The audit's CENTRAL conclusion HOLDS and is reinforced: two REDs, HOLD posture at D-7 is correct, and the root blocker (unrotated exposed secrets + gate/WAF down) is real and WORSE than Cycle 1 stated. But Cycle 1 was too generous on BOTH its GREENs — Profitability and Reliability each fall to AMBER under probe. Corrected board: 2 RED · 8 AMBER · 0 GREEN (was 2 RED · 6 AMBER · 2 GREEN). Nothing found moves the needle toward GO; two findings move it further toward HOLD.
Claim under test | Cycle 1 said | Cycle 2 probe result
Site open anonymously? | Gate down, all data endpoints 200 | UPHELD — /, /listings, /demo-listings, /dashboard/summary, /dashboard/bit, /auth/providers, /id-verify/status, /flags ALL 200 with no cookie (PROBED)
IL-01 (tuppence balance) authenticated? | 401, launch-blocker cleared | UPHELD — 401 for real-format AND fake email alike; no existence oracle (PROBED)
Regression ledger 0-regressed? | 129 entries, 126 holding, 0 regressed, 3 open | UPHELD — re-ran live: 129 · 126 holding · 0 REGRESSED · 3 open · 0 ready-to-lock (EXECUTED)
Rulings reflected? | 39/39 | UPHELD — 39 rulings checked, 0 FAIL, 0 WARN (EXECUTED)
Edge blocks synthetic load? | default Python UA -> 403, so load NOT MEASURED | OVERTURNED — default curl, python-requests AND browser UA ALL return 200 now. The edge is NOT blocking non-browser clients. Cycle 1's stated basis is falsified (PROBED)
⚠️ New finding Cycle 1 missed — anonymous information disclosure  GET /dashboard/summary, cookieless, returns 200 AND leaks operational intelligence to any anonymous reader: the exact strings "Hetzner CPX32 (8GB RAM) + 100GB volume", "WAF allowlist DISABLED", and "origin gate GATE-ENFORCE-1 the only guard". Cycle 1 noted the 200 but never read the body. This is not merely gate-down — the app is PUBLISHING which defences are down and its infra sizing (a DoS planning aid). It materially strengthens the Hardening RED.
Dimension | Cycle 1 | Ruling | Cycle 2 | Evidence & reasoning
1 · Business viability | AMBER | UPHELD | AMBER | PROBED — 59 sellers / 104 listings / 115 lifetime intros live; two-sided market functions. Public-scale demand unproven. Fair call.
2 · Financial growth | AMBER | UPHELD (leans pessimistic) | AMBER | EXECUTED+READ — ramp rests on intros/seller and paid-conversion, both unmeasured. My model (below) shows it is more fragile than Cycle 1 implied, but AMBER is the right band.
3 · Profitability / unit economics | GREEN | OVERTURNED | AMBER | The per-transaction margin is genuinely ~100% (structural, GREEN-worthy). But the headline 'break-even ~25-30 sellers' holds ONLY at 2 intros/seller/mo = 4x the observed lifetime rate. Recomputed at the observed ~0.5 intro/seller/mo the break-even is 49-103 sellers and net@60 goes NEGATIVE. A GREEN that needs 4x the only real data point is not PROBED-green. Downgrade.
4 · Server capability | AMBER (NOT MEASURED) | VERDICT UPHELD, REASON OVERTURNED | AMBER | Still correctly NOT MEASURED at launch scale. But the STATED reason ('edge blocks synthetic load') is falsified — all client UAs get 200 now, so a bounded ramp WOULD reach the origin. The honest reason is the HALT safety choice not to load-test production 7 days out, not an edge block.
5 · Robustness | AMBER | UPHELD | AMBER | PROBED+EXECUTED+READ — AI failover proven in the decision layer (RG-0128 13/13); Paystack/Resend/relay single-fail behaviour READ not live-tested. Fair.
6 · Reliability | GREEN | OVERTURNED | AMBER | BIT 8/8 and ledger 126/129 are real, but (a) NO external uptime monitor exists — Cycle 1 named this gap then scored GREEN anyway; (b) some BIT sub-checks are disk-sourced (B-FEA-SHELL reads 'size=... (disk)', example endpoints 'src advertagent'), i.e. EXECUTED against source, not PROBED against the live box; (c) reliability is a time-series property a single snapshot cannot establish. Snapshot-green is not reliability-green.
7 · Maintainability | AMBER | UPHELD | AMBER | PROBED+READ — bea_main.py ~1.0 MB single file; RG-0075 CONFIRMED OPEN (admin-gate script duplicated across 5 files). Strong change machinery offsets but does not erase 2am-diagnosis risk.
8 · Scalability | AMBER | UPHELD | AMBER | READ+PROBED — SQLite fine at 60; Postgres move (RUL-024) NOT executed. First wall at 600-6000. Fair.
9 · Hardening | RED | UPHELD & STRENGTHENED | RED | PROBED — gate down both halves, WAF allowlist down, secrets unrotated. PLUS the new /dashboard/summary disclosure actively advertises the WAF-down state and infra to attackers. If anything Cycle 1 under-stated this. Blocker.
10 · Hack-proofness | RED | UPHELD | RED | PROBED — app auth is genuinely hard: I ADD a live check Cycle 1 never ran — /admin/login rate-limits (7x 401 then 429, failure-only budget per RG-0134). No injection, no enumeration, fails closed. But burnt unrotated secrets mean one stolen credential bypasses all of it. Blast radius total. Blocker.
#  Dimension | Cycle 1 | Cycle 2 | Blocker?
1 Business viability | AMBER | AMBER | No
2 Financial growth | AMBER | AMBER | No
3 Profitability / unit economics | GREEN | AMBER (overturned) | No
4 Server capability | AMBER | AMBER (reason corrected) | No
5 Robustness | AMBER | AMBER | No
6 Reliability | GREEN | AMBER (overturned) | No
7 Maintainability | AMBER | AMBER | No
8 Scalability | AMBER | AMBER | No (at 60)
9 Hardening | RED | RED (strengthened) | BLOCKER
10 Hack-proofness | RED | RED | BLOCKER
✓ Where Cycle 1 was RIGHT (upheld under adversarial probe)  IL-01 clearing is real (401 real+fake). The site really is open anonymously (all endpoints 200). The ledger really is 0-regressed (3 open). The app's own auth is genuinely hard — and I ADD a live positive Cycle 1 never probed: the admin door rate-limits (429 after 7 failures, failure-only budget). No PII in /listings (0 emails, 0 phones, street_address unpopulated) and no demo bleed (is_demo=0 in live). Both REDs are correctly called. The core HOLD conclusion is sound.
Scenario (conv Pro/Starter · intros/seller/mo) | $/seller/mo | Net @60 | Net @600 | Break-even (sellers)
C1 base — 15%/25% · 2.0 (reproduce) | $8.13 | +$294 | +$4,686 | ~24
C1 'collapse' floor — 5%/10% · 1.0 | $3.44 | -$48 | +$1,810 | ~74
C2 realistic demand — 15%/25% · 0.5 + 20% churn opex | $5.22 | +$58 | +$2,878 | ~49
C2 pessimistic — 5%/10% · 0.5 (freemium+observed) | $2.47 | -$107 | +$1,228 | ~103
C2 harsh floor — 3%/7% · 0.3 | $1.53 | -$163 | +$665 | ~166
★ Break-even — the honest number  Cycle 1's ~25-30 sellers reproduces ONLY at its optimistic demand inputs. Calibrated to the observed intro rate (~0.5/seller/mo), the real break-even is ~49 sellers if paid-conversion stays optimistic, and ~103 sellers under freemium-realistic conversion (5% Pro / 10% Starter). At the 60-seller launch target the platform is roughly break-even-to-slightly-negative on defensible pessimistic inputs. The economics do not COLLAPSE — fixed opex is tiny and the intro is ~100% margin — but 'comfortably profitable at launch' is not established. It is contingent on demand that has not been measured.
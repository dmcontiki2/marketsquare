## 2026-08-21 — ID-NPR-1: paid Home Affairs ID verification, offered but never forced (RUL-039)

David, on the stay-deposit scam — fake listing, stolen photos, credentials sent to the
prospect, deposit paid, property gone or never theirs: *"we still build the capability in
with the ID upload to buy the verification at 1 Tuppence, but it is then less forced and
also at the same time better visibility... We also need to only ever do this verification
one time, against a database of ID numbers?"*

**What the audit found first, because it shapes everything else.** The AI document check was
setting `users.id_verified_at` at confidence ≥0.60 with the code's own comment reading *"no
human review path"* — and that flag was what a buyer saw as "verified". It only ever proved
the uploaded document was legible and internally consistent with what was typed. It cannot
tell a competent fake from a real ID, nor whether the ID belongs to the person holding it.
Separately, accommodation credentials (TGCSA +22, municipal licence +6, health & safety +5,
fire +4, award +3) auto-earn on **any** file upload because no `adv_acc` signal is in
`_LEGAL_SIGNALS` — five arbitrary JPEGs reach 40 base + 40 category = 80 = "Trusted". That
second hole is NOT fixed here and is recorded as still open.

**Three states, and only the paid one may say "verified":** `submitted` (format valid) /
`ai_checked` (document check — keeps its existing job as the introduction gate, untouched) /
`npr_verified` (checked against the DHA National Population Register, `users.
id_npr_verified_at`, the green tick). The paid tier is a deliberately separate column: had it
reused `id_verified_at` it would have become a second barrier to introductions, which is the
opposite of the ruling.

**Never a blocker.** A seller who declines keeps their listing and their introductions. A
buyer proceeding with an unverified seller is told so plainly and the acknowledgement is
recorded — informed consent, not gatekeeping. For stays the warning names the actual risk:
never pay a deposit for a place you have not seen, and TrustSquare holds no deposits and
cannot recover money sent to a seller.

**One check ever — with the trap that must not be optimised away.** Dedupe is by salted ID
hash in the new `id_verification_ledger`, so an answered hash is never re-queried or
re-billed. But the same hash under a **second** account is a duplicate identity claim: it is
flagged for review, granted nothing, and charged nothing. A reused ID number is a fraud
signal, not a saving.

**Cost shape and supplier doctrine.** Flat per-check (DHA R10 real-time / R1 off-peak batch;
aggregator retail ~R27–30) against 1T = $2 fixed — the only external cost shape the 1 Aug
pricing ruling permits. `id_verify_provider.py` is a swappable adapter, unconfigured by
default, and fails **closed**: no provider, no tick, and critically **no charge**. Every
early return in the endpoint is free; a seller is billed only when a supplier query is
actually consumed.

**Honest limit, written into the EULA rather than glossed:** an NPR pass proves the identity
number exists and the recorded names match. It does **not** prove the presenter is the
holder. Closing that needs DHA photo retrieval plus a live selfie — a future tier. Copy may
never claim more.

EULA **v1.14 → v1.15** adds §3.5A covering all of the above plus POPIA opt-in consent given
at request time (not by accepting the EULA) and an explicit deposit clause. Written to
`eula_clean.html` — the one writer — and propagated via `scripts/eula_sync.py` (`--check`
green across all three copies). **Also corrected in passing: `canon.yml`'s eula pointer had
drifted to v1.13 while `LEGAL_VERSIONS.md` read v1.14**; `check_canon_pointers.py` should
have caught that and did not.

Guards: `test_id_npr.py`, 10 assertions — the duplicate-ID trap, the intro gate staying free
of the NPR column, the notice never being able to raise, and the provider never billing when
unconfigured. Regression ledger **RG-0136**.

**Scope honesty:** backend only. The green tick and the buyer warning are backend-ready but
the front-end render is not built, and no provider is configured — so today this capability
is dark and correct, not live. A seller cannot yet buy a check.

Cost model impact: none yet — no provider configured, so no external spend is possible. When
armed, each check is a flat supplier fee recovered by a 1T charge, with no percentage
component and no exposure if a check fails.

# Introduction Mechanism — Comparative Brief

*5 August 2026 · how TrustSquare introduces a buyer and a seller · for David's decision*

## The tension worth naming first

Two of your principles pull in opposite directions here, and the whole decision is about
where they meet.

The first is the reliability principle from electronics: **fewer parts, less to go wrong.**
Fewer lines of code is fewer failure modes, less to maintain, less to break at 2 a.m. By
that rule alone, the current design — just hand each party the other's email — wins,
because it is the least machinery.

The second is the one you stated plainly: **security and anonymity are worth paying for.**
When TrustSquare divulges nothing about either party, the two meet on neutral ground we
control, and — your words — that keeps our side legally clean.

The right answer is not to obey one principle and ignore the other. It is to find the
option where the *smallest* addition of parts buys the *largest* gain in anonymity and
legal cleanliness. That is the lens this brief applies.

## The three ways to introduce two strangers

**A · Direct email exchange (what the code does today).** On an accepted intro the app
hands each party the other's real email address (today, via the accept-intro webhook).
Simplest possible design.

**B · Relay through masked aliases (the marketplace standard).** On an accepted intro,
TrustSquare mints a throwaway alias for each side — e.g. `intro-7f3a@trustsquare.co` —
that forwards to their real inbox. Each party writes to the alias; TrustSquare passes it
through. Neither ever sees the other's real address. Kill the alias and the channel dies.

**C · On-platform messaging (no email at all).** The two parties talk in a thread inside
TrustSquare. No address is ever exchanged unless they choose to hand it over themselves.

## Side by side

| | A · Direct email | B · Relay alias | C · On-platform |
|---|---|---|---|
| Moving parts / failure surface | Fewest | Moderate (reuses existing infra) | Most (new inbox UI + notifications) |
| What leaves TrustSquare | Both real emails | Nothing — only an alias | Nothing |
| Anonymity to the parties | None | Full until they choose to reveal | Full |
| Neutral ground / legal posture | We are the discloser of PII | We disclose nothing; we relay | We disclose nothing |
| Revocable if abused | No — address is out for good | Yes — kill the alias | Yes — close the thread |
| New subscription | No | **No** (Cloudflare Routing + existing sender) | No |
| Build effort | Already built | A few focused sessions | Largest build |
| User experience | Familiar email | Familiar email | New habit; users often leave anyway |

## Reading it through the reliability lens

Your fewer-parts instinct does real work here — it just doesn't point where it first seems
to. It argues *against* option C, not for option A. C is the most machinery for the least
marginal gain over B: it adds an inbox, notifications and a messaging UI to achieve the
same "nothing leaves TrustSquare" result the relay already gives you — and users frequently
abandon on-platform chat to swap emails anyway, so you carry the parts and still lose the
anonymity at the last step.

Between A and B, the parts B adds are contained and — crucially — mostly parts you already
own. The inbound side is your existing Cloudflare Email Routing and Worker (the same path
that already feeds your fault intake). The outbound side is your existing authenticated
sender. The only genuinely new pieces are a small alias-to-real mapping table in the
database you already run, and the forwarding logic. So B is not "a whole new subsystem" —
it is a modest extension of wiring that is already live and already proven.

## The legal point you put your finger on

This is the part that makes B more than a nicety. Under a direct exchange, TrustSquare is
the party that *discloses* one person's personal information to another — we are in the
data-handover business, and every disclosure is ours to justify and defend. Under a relay,
we disclose nothing: we operate a channel and pass messages across it, and the real
addresses never leave our control. The two parties meet on ground we own and can revoke.

That is a materially better posture under POPIA's data-minimisation principle — we hold and
move the least personal information necessary, and we never make an irreversible disclosure
on a customer's behalf. It also matches the doctrine you stated: *nothing of the customer's
leaves TrustSquare except a consented, revocable email channel — never the address itself.*
(This is the engineering and privacy logic, not formal legal advice — worth a line past
counsel before launch, but the direction is sound.)

## Recommendation

**Option B — the relay.** It is where your two principles meet: the smallest addition of
parts that reuses infrastructure you already run, in exchange for full anonymity, a
revocable channel, and a clean "we disclosed nothing" legal posture. Option C is the
purist's answer but spends the most parts for the least extra value and fights the way
people actually behave. Option A is the status quo we are deliberately moving off, because
"we handed over their address" is precisely the exposure you want gone.

Scope note if you pick B: a one-way reveal (buyer reaches seller through an alias) is the
smaller build; a full two-way relay with clean reply handling — stripping quoted history,
mapping each side's reply alias, killing an alias on abuse — is the fuller build. I would
start one-way and grow it, so the first version is the fewest parts that still divulges
nothing.

## Decision asked

**B or C?** (A is the status quo we are leaving.) On your word I write the implementation
plan for the chosen option, fold it into the Option-A account-binding work as one "who sees
what, who pays" pass, and put it through the same Peer review the AI services just had.

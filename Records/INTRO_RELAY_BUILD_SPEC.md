# Introduction Relay — Build Spec v1

*5 August 2026 · David selected Option B (masked-alias relay) from the Introduction
Mechanism Brief. This is the implementation plan, house-pattern like AI_AUTO_FAILOVER_P2.
Not yet built — it has one Cloudflare-console prerequisite and goes through the Peer review
first, same as the AI-services work.*

## 0. Doctrine (David's ruling, 5 Aug 2026)

> Nothing of the customer's leaves TrustSquare except a consented, revocable email channel —
> never the address itself. The two parties meet on neutral ground we control. We disclose
> nothing; we relay.

Every decision below serves that line. It is worth enshrining in CLAUDE.md as a standing
design rule so every future feature is measured against it.

## 1. Scope — one-way first, grow to two-way

**Phase 1 (v1, the fewest parts that still divulges nothing):** a buyer who has an accepted
intro can email the seller through a masked alias; the seller receives it and can reply
through their own masked alias. Neither ever sees the other's real address. This is already
a full two-way conversation from the users' point of view — "one-way" refers only to who
opens it (the buyer, off an accepted intro), not to message direction.

**Deferred to v2 (only if wanted):** attachments passthrough, per-message abuse scoring,
and on-platform message mirroring. Named so v1 stays small.

## 2. Architecture — reuses what is already live

| Leg | Reused component (already in the stack) |
|---|---|
| Receive alias mail | Cloudflare Email Routing → Email Worker (the same path that feeds `/email/inbound`) |
| Hand mail to the app | New `POST /intro/relay` endpoint, mirroring `/email/inbound` (X-Inbound-Secret auth) |
| Send the forward | Resend (`api.resend.com`) — the existing `_smtp_send_reply` sending lane |
| Store the mapping | A new table in the SQLite DB you already run |

No new subscription. The only genuinely new code is one table, one inbound endpoint, one
forward helper, and a small change to the intro-accept flow.

## 3. Data model — `intro_relay_aliases`

```sql
CREATE TABLE IF NOT EXISTS intro_relay_aliases (
  alias       TEXT PRIMARY KEY,         -- e.g. intro-7f3a9c@relay.trustsquare.co
  intro_id    INTEGER NOT NULL,
  party       TEXT NOT NULL,            -- 'buyer' | 'seller' — whose real inbox this alias hides
  real_email  TEXT NOT NULL,            -- the hidden real address (never sent to the counterparty)
  counter_alias TEXT NOT NULL,          -- the OTHER party's alias (the From on the forward)
  active      INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  expires_at  TEXT NOT NULL             -- channel auto-closes; default e.g. 30 days
);
CREATE INDEX IF NOT EXISTS idx_relay_intro ON intro_relay_aliases(intro_id);
```

Two rows per accepted intro — one alias per party. `real_email` is the only place the real
address lives, and it is never placed in an outbound message body, header, or webhook.

## 4. Flow

**On intro accept (replaces today's leak):** today `accept_intro` fires the n8n webhook
carrying BOTH raw emails. v1 instead mints the two aliases, stores the mapping, and emails
each party a "you're introduced — reply to this message to talk, your address stays private"
note *from their counterpart's alias*. The n8n webhook, if kept, carries alias identifiers
only — never the raw counterpart address.

**Inbound (a party writes to an alias):** Cloudflare Routing catches `intro-*@relay.
trustsquare.co` → Worker POSTs `{to_alias, from_addr, subject, body}` to `/intro/relay`
with `X-Relay-Secret`. The endpoint:
1. Looks up `to_alias` → must be `active` and unexpired, else drop with an honest bounce.
2. Confirms `from_addr` matches the real_email of the *counter* alias (only the two enrolled
   parties can use the channel; a stranger who guesses an alias is rejected).
3. Sanitises subject/body (strip CR/LF header-injection, cap size).
4. Forwards via Resend to the counterpart's `real_email`, with `From =` the sender's own
   alias and `Reply-To =` the same, so the reply loops back through the curtain.

**Outbound helper:** a thin `_relay_forward(to_real, from_alias, subject, body)` modelled on
`_smtp_send_reply` — same Resend lane, same domain auth.

## 5. Alias lifecycle & abuse control

- **Format:** `intro-<random>@relay.trustsquare.co` — random, unguessable, no PII in the string.
- **Expiry:** `expires_at` closes the channel automatically (default 30 days; tunable).
- **Kill switch:** set `active=0` on either alias and the channel dies instantly — the thing a
  raw-email exchange can never do.
- **Enrolled-parties-only:** the `from_addr` check means only the two real inboxes can drive
  the channel; a leaked alias alone is inert.

## 6. Integration with the F1 account-binding work (one pass)

Fold this into the Option-A "who sees what, who pays" change so we touch the intro flow once:
account identity comes from the authenticated session (F1), and the counterpart's address is
replaced by an alias (this spec). Same review, same deploy, one coherent story: *identity is
proven, not asserted; and the only thing that crosses is a revocable alias.*

## 7. Security review points (for the Peer)

- No outbound fetch anywhere in this path — nothing SSRF-shaped is introduced.
- Real addresses never appear in a body, a header, a log line, or a webhook payload.
- Header-injection guard on relayed subject/body (strip CR/LF).
- Size cap on relayed content; attachments dropped in v1 (named limit, not silent).
- The `from_addr` enrolment check prevents alias-guessing abuse.

## 8. Regression-ledger tripwires (added on build)

- **RG-00xx:** `accept_intro` never emits a raw counterpart email to the other party or to a
  webhook — only alias identifiers. (Asserts the leak we are closing cannot return.)
- **RG-00xx:** `/intro/relay` rejects an inactive/expired alias and a non-enrolled `from_addr`.
- **RG-00xx:** the relay forward's `From`/`Reply-To` is an alias, never a `real_email`.

## 9. David's console prerequisites (before the code can work end-to-end)

1. **Cloudflare Email Routing:** add a route for `intro-*@relay.trustsquare.co` (or a catch-all
   on a `relay.` subdomain) to the Email Worker — same mechanism already routing your support
   mail. DNS: the MX + verification records Cloudflare generates.
2. **Env:** `RELAY_INBOUND_SECRET` on the server (mirrors `EMAIL_INBOUND_SECRET`); the Worker
   carries it. `RELAY_DOMAIN=relay.trustsquare.co`.
3. Confirm Resend is authorised to send `From: *@relay.trustsquare.co` (SPF/DKIM on the
   subdomain) so forwards don't land in spam.

These are console/DNS clicks, not code — the one part I can't do from a session.

## 10. Build phases (each ships through the normal gates)

- **P1 — table + endpoint + forward helper + accept-flow change + tripwires** (~1 session,
  code side). Behind a `launch_switches.intro_relay` flag, fail-closed, so it's dark until
  the Cloudflare side is live.
- **P2 — Peer review** (the same GPT-5.6 pass the AI services had), then enable the flag and
  run a live two-party drill (send through an alias both directions, confirm neither real
  address ever appears).
- **P3 (optional, later) — attachments, abuse scoring.**

## 11. Decision / next step

The plan is ready. Two ways to start, your call: I build P1 now behind the dark flag (so the
code is in and reviewed while you set up the Cloudflare route at your convenience), or I hold
until you've done the console prerequisites so the first build lands on working rails. Either
way it folds into the F1 account-binding pass and goes through the Peer before it carries a
single real introduction.

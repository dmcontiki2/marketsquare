# DAVID QUEUE — one action at a time

**What this is.** The serialized list of things only David can do, ordered, with exactly what to
click and what "done" looks like. **One item is served at a time** so it can be handled between
other work without holding the whole list in his head.

**Why it is a file and not a chat message** (the standing problem this exists to solve): a queue
that lives in a transcript dies at the session break, and the next session re-derives it wrongly.
This file is read by `scripts/david_queue.py`, which **re-verifies every item against evidence**
and prints the single next open one. An item does not close because someone remembered it closed.

**Run it:** `python3 scripts/david_queue.py`  ·  add `--all` to see the whole board.

**Verification grades** (deliberately honest — see the CLAUDE.md evidence ladder):
- `LEDGER:<id>` — auto-closes when that regression-ledger entry stops failing. Strongest.
- `FIELD:<name>` — auto-closes when that field in `THIRD_PARTY_LAUNCH_REGISTER.md` is filled.
- `DAVID` — **no instrument can see this.** Closes only when David says so, and the date he said
  it is recorded here. Never reported as PROBED.

**Rules.** Never renumber. Never delete a closed item. An item that turns out to be Claude's after
all is CLOSED here with a note saying so — that has already happened twice (the Google consent
screen and the domain registrar both sat in this column for six days and neither was David's).

---

## D1 · Domain auto-renew — the last field on the domain lifeline
STATE: DONE 2026-08-28 (auto-renew ON, status Active, expires Dec 31 2026 — read in the dashboard; nothing needed changing)
TIME: 1 minute
VERIFY: FIELD:DOMAIN_AUTORENEW
WHY_DAVID: Cloudflare account login. WHOIS does not publish the auto-renew flag — it is a setting
inside the registrar account, so no probe we own can read it.
STEPS:
  1. Cloudflare Dashboard → **Domain Registration** → **Manage Domains** → trustsquare.co
  2. Look for **Auto-renew**.
  3. If it is OFF, turn it ON while you are there.
  4. Reply: `D1 auto-renew on` (or `off`).
CONTEXT: Everything else about the domain is now settled and safe — registrar **Cloudflare, Inc.**,
expiry **2026-12-30 (125 days out)**, registrar lock ON. This one field closes **RG-0137**, the
"one dependency that can end the business silently", completely.

## D2 · Paystack 2FA
STATE: DONE 2026-08-28 (David confirmed: two-factor authentication enabled on the live money rail)
TIME: 3 minutes
VERIFY: DAVID
WHY_DAVID: Account security — needs your phone/authenticator.
STEPS:
  1. Paystack dashboard → Settings → Security → enable two-factor authentication.
  2. Store the recovery codes somewhere that is not the same device.
  3. Reply: `D2 done`.
CONTEXT: Your reminder for this was set for today. Paystack is the live money rail — it is the one
account where a compromise costs real money rather than time.

## D3 · Resend RED-alert key — the outage alarm is dead
STATE: DONE 2026-08-28 (watch copy re-installed from the live systemd drop-in; PROBED `GET https://api.resend.com/domains` = HTTP 200, 74 B, 0640 root:msdeploy)
TIME: 5 minutes
VERIFY: DAVID
WHY_DAVID: Root on the Hetzner box + a live credential. This session has no SSH key, and pasting a
live key through chat is how one got burnt on 21 Aug.
STEPS:
  1. SSH to the box.
  2. Put the CURRENT Resend API key into `/etc/marketsquare/resend.watch.conf`
     (keep it `0640 root:msdeploy`).
  3. Reply: `D3 done`.
CONTEXT: **Dead since the 22–23 Aug rotation — day 3, re-probed from the box at 04:39 UTC on 28 Aug: `GET https://api.resend.com/domains` returns HTTP 400.**
Nothing has been able to wake you about an outage in that time, and it was only discovered because
a real RED fired on 26 Aug and did not arrive. The conf file is untouched — 74 B, `-rw-r----- root:msdeploy`, mtime still `Aug 5 06:26`. **Soft-public is TOMORROW. Do this before D4** so the watcher gets the fresh
key, not the burnt one.

## D4 · Deploy the external uptime watcher
STATE: DONE 2026-08-28 (Worker trustsquare-uptime live, cron */5, PROBED ok:true kv:true 11:31:54 UTC; RG-0138 promoted OPEN -> LOCKED. Alert half unproven until the 06:00 UTC heartbeat lands 29 Aug)
TIME: 10 minutes
VERIFY: LEDGER:RG-0138
WHY_DAVID: `wrangler` needs an interactive Cloudflare login on your machine, and step 2 prompts for
a secret. Neither can be driven from here.
STEPS: Full runbook at `ops/cloudflare/UPTIME_MONITOR.md`. Three commands:
  1. `wrangler kv namespace create UPTIME_STATE`  → copy the printed id into `uptime_wrangler.toml`
  2. `wrangler secret put RESEND_API_KEY --config ops/cloudflare/uptime_wrangler.toml`
  3. `wrangler deploy --config ops/cloudflare/uptime_wrangler.toml`
  Then write `ops/cloudflare/UPTIME_DEPLOYED.md` with `DEPLOYED_ON:` and `LAST_HEARTBEAT:` —
  RG-0138 reads those two lines and closes itself.
CONTEXT: Built 22 Aug, undeployed for five days. Every other instrument watching the site runs
**on the box it is watching** or **on your desktop** — so a dead server or a closed laptop is a
blind day by construction, and that already happened on 6 Aug. This is the only thing that would
notice an outage over the launch weekend. No new vendor, no cost.

## D5 · Gemini key (budget-capped)
STATE: OPEN
TIME: 5 minutes
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: Buy the key with a budget cap set, paste it to the server env, reply `D5 done`.
CONTEXT: Funds were expected ~25 Aug. Until it lands, photo anonymisation runs **reject-only**
(RUL-033) — sellers' photos get rejected rather than anonymised. Not a launch blocker; it is a
quality-of-experience cost that grows with every seller who uploads.

## D6 · Resend $20/mo 50k tier
STATE: OPEN
TIME: 2 minutes
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: Flip the plan at launch, reply `D6 done`.
CONTEXT: Pre-approved (B7) — this is execution of a decision already made, not a new one. Free tier
carries sign-in email today; it will not carry public launch volume.

## D7 · Launch special — on or off for launch?
STATE: OPEN
TIME: a decision, not a task
VERIFY: DAVID
WHY_DAVID: Launch scope, and `LAUNCH_CODE_SECRET` is an HMAC key.
STEPS: Tell me **on** or **off**. If on, I generate the secret, set `LAUNCH_SPECIAL_ENABLED`, and
the block starts rendering into outbound email.
CONTEXT: I set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on CityLauncher today, but reading the code
first changed the picture: `launch_codes.enabled()` needs **all three** of `LAUNCH_SPECIAL_ENABLED`,
`LAUNCH_CODE_SECRET` and the deadline, and that `.env` had **none** of the other two. So the launch
special is currently **stripped from every outbound CityLauncher email** — not mis-dated, absent.
The MarketSquare server-env half of the deadline also still needs your root access.

## D8 · Anthropic subscription — renew or drop
STATE: OPEN
TIME: a decision
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: Decide before 1 Sep, reply `D8 renew` or `D8 drop`.
CONTEXT: RUL-013 time-boxed Fable's arrangement to **1 Sep and said it does not renew by default**.
The successor is already decided and wired — `ai_provider.py` routes the `design` tier to
`gpt-5.6-sol` with Scaleway standby. Nothing breaks if you drop it; this is purely whether you want
the subscription lane past launch.

## D9 · One live Paystack buy (smallest pack, close the tab mid-flow)
STATE: OPEN
TIME: 5 minutes
VERIFY: DAVID
WHY_DAVID: Real money on the live rail.
STEPS: Buy the smallest Tuppence pack, **close the tab before the callback returns**, then check
the credit landed. Reply `D9 done` with what you saw.
CONTEXT: Closes the detached-credit end-to-end — the case where a buyer's browser dies between
Paystack taking the money and us crediting it. That path has never been exercised with real money.

## D10 · One real Didit ID check
STATE: OPEN
TIME: 5 minutes
VERIFY: DAVID
WHY_DAVID: Real money (possibly $1.10).
STEPS: Run one real Home Affairs check on a real ID, reply `D10 done` with whether it billed.
CONTEXT: The lane is ARMED and its SAFETY properties are asserted and passing (a partial match
never passes, a provider failure never charges, the tick never gates an introduction). What is
unknown is **billing shape**: whether the 500 free monthly verifications cover Database Validation
or it bills $1.10 from call one. One check settles it.

## D11 · Travelpayouts tours — resubmit?
STATE: OPEN
TIME: a decision
VERIFY: DAVID
WHY_DAVID: Commercial timing.
STEPS: Say when, and I prepare the submission.
CONTEXT: Declined twice — most recently 24 Aug, *"website under development or not yet ready"*.
26 programs available / 20 blocked, including Booking.com, Viator and GetYourGuide. RUL-041 says
never resubmit unchanged; **Friday's soft launch is the first materially changed face** we have had.

## D12 · Delete two superseded Cloudflare tokens
STATE: OPEN
TIME: 2 minutes
VERIFY: DAVID
WHY_DAVID: Deletions are reserved to you (RUL-037).
STEPS: Cloudflare → API Tokens → delete `MarketSquare Media` and `Trustsquare Cache Purge`.
Reply `D12 done`.
CONTEXT: Rotation residue from 22 Aug. Not blocking anything — but a live token nobody uses is a
credential nobody is watching.

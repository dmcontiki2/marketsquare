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
STATE: OPEN — KEY SHIPPED 2026-08-28; BILLING DEFERRED to next week (David, 28 Aug: Google
places a ~$50 card verification hold — released ~a week, never charged — and his region routes
through PREPAID credits; launch-weekend cash goes to Resend instead. Prepaid, when bought, IS
the hard cap — better than any setting).
**TRIPWIRE — DO NOT run eval_photo_anon.py or set PHOTO_SCAN_CANARY while the key is unbilled:**
free-tier traffic is LOGGED by Google, and the eval set carries a real seller's actual plates
(real_246_*). Billing/credits attach FIRST, then eval, then arming. The key sits dark and
harmless on the server meanwhile; RUL-033 reject-only is the designed bridge. Remaining, the '-capped' half: billing attach + the $10/mo spend cap in AI Studio. Then reply `D5 done`. Optional accelerator: paste the key into `.secrets\ai_keys.env` as GEMINI_API_KEY=... so Claude can run the eval locally (it gets registered as an out-of-band copy so rotations refresh it)
TIME: 5 minutes
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: 1. aistudio.google.com → API keys → create the key in a NEW project (never the old
     Places project). Attach billing there — **$0 upfront, pay-per-use**; that card attach is the
     whole "funds" moment.
  2. Burn-proofing: click **Create a spend cap** on the same API-keys page and set **$10/month**
     — AI Studio's native HARD stop (seen live 28 Aug; supersedes the older quota workaround).
     The Places lesson, solved at the vendor.
  3. Double-click `add_gemini_key.bat` (built 28 Aug, gitignored) — pastes once, ships to server
     env, restarts, health-checks. Key only; PHOTO_SCAN_CANARY arming stays RUL-032's own step.
  4. Reply `D5 key shipped`.
CONTEXT: Funds were expected ~25 Aug. Until it lands, photo anonymisation runs **reject-only**
(RUL-033) — sellers' photos get rejected rather than anonymised. Not a launch blocker; it is a
quality-of-experience cost that grows with every seller who uploads.
COSTED 28 Aug (docs, READ-grade): Nano Banana-class image ops ≈ $0.039/image at ≤1024px; scans
are cheaper still. Founding volumes (~300 photos/mo) ≈ **$2–5/month**. Free tier REJECTED on
purpose: Google logs free-tier traffic for product improvement — seller photos into Google's
logs is the opposite of what the anonymity lane exists for; paid keys are not logged.

## D6 · Resend $20/mo 50k tier
STATE: DONE 2026-08-31 (RUL-079's own text records it: David activated the Resend $20/50k tier on 31 Aug — the same day he approved the agency-outreach ruling. Grade: READ (dated ruling); the billing tier is not probeable from the sandbox without the key, so no independent probe exists. This row sat OPEN two days after the act — corrected by the 1 Sep final third-party sweep, probe-beats-file class.)
TIME: 2 minutes
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: **Flip to Pro on Mon 31 Aug** (clean month, no pro-rata) — before the Tue 1 Sep morning
sends. Reply `D6 done`. A scheduled reminder fires Mon 08:00.
CONTEXT: Pre-approved (B7) — this is execution of a decision already made, not a new one. Free tier
carries sign-in email today; it will not carry public launch volume.
**RUL-061 (28 Aug): David deferred the flip to 1 Sep** — pro-rata for 3 days buys nothing while
warm-up waves run 60/day under the free 100/day cap (60 wave + ~3 service + heartbeat fits).
THE CLIFF: Tue 1 Sep sends up to 420; on free tier the day fails 320 short AND wave mail can
starve the RED-alert lane (same account). Flip Monday = clean full month, no pro-rata. If
Monday passes unflipped, the 1 Sep morning session must treat sending as BLOCKED, not degraded.

## D7 · Launch special — on or off for launch?
STATE: DONE 2026-08-28 (RUL-060 — David chose ON over the 'off' recommendation and ran enable_launch_special.bat: server armed + health ok [EXECUTED, his transcript], CityLauncher half verified 1/1 [PROBED on disk]; render path proven both ways, block live from the next send batch; hard close 2026-09-01)
TIME: a decision, not a task
VERIFY: DAVID
WHY_DAVID: Launch scope, and `LAUNCH_CODE_SECRET` is an HMAC key.
STEPS: Reply `D7 on` or `D7 off`. If **on**: double-click `enable_launch_special.bat`
(built 28 Aug — generates the HMAC secret ON the server, arms both halves incl. FOUNDERS_ID_SALT,
restarts, health-checks, then arms the CityLauncher issuing side; secret never displayed).
If **off**: nothing to do — the block stays stripped, and D16 keeps the occasion for later.
CONTEXT: I set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on CityLauncher today, but reading the code
first changed the picture: `launch_codes.enabled()` needs **all three** of `LAUNCH_SPECIAL_ENABLED`,
`LAUNCH_CODE_SECRET` and the deadline, and that `.env` had **none** of the other two. So the launch
special is currently **stripped from every outbound CityLauncher email** — not mis-dated, absent.
The MarketSquare server-env half of the deadline also still needs your root access.
**READ 28 Aug (code, both repos): this switch and RUL-047 are the SAME lever.** The server
redemption side (`launch_redemption.py`) is the parked founders machinery — its gate needs
LAUNCH_REDEMPTION_ENABLED + secret + FOUNDERS_ID_SALT + deadline, and every redemption MINTS a
founders badge ("one badge per human, forever"; "the special is NEVER repeated"). Saying **on**
therefore SPENDS the once-only occurrence RUL-047 reserved for a moment when a customer base
exists — and with the 2026-09-01 hard close ("never extended") the window would be the
soft-public weekend only, in front of ~zero audience. **CTO recommendation: `D7 off` for this
launch; D16 already tracks naming the real occasion.** Decision stays yours — launch scope.

## D8 · Anthropic subscription — renew or drop
STATE: DONE 2026-08-28 (David: 'works as we have it wired' = DROP, executing RUL-013's no-renew default. Wiring PROBED on source this session: TASK_MODEL design → openai gpt-5.6-sol, scaleway mistral-medium-3.5-128b standby — current 5.6-era rows, the H1 staleness concern does not apply. Residue: if the subscription auto-renews in the account, the cancel click before the billing date is David's)
TIME: a decision
VERIFY: DAVID
WHY_DAVID: Spend.
STEPS: Decide before 1 Sep, reply `D8 renew` or `D8 drop`.
CONTEXT: RUL-013 time-boxed Fable's arrangement to **1 Sep and said it does not renew by default**.
The successor is already decided and wired — `ai_provider.py` routes the `design` tier to
`gpt-5.6-sol` with Scaleway standby. Nothing breaks if you drop it; this is purely whether you want
the subscription lane past launch.

## D9 · One live Paystack buy (smallest pack, close the tab mid-flow)
STATE: DONE 2026-08-29 (David: TWO live real Tuppence buys completed through Paystack. He reported this for the SECOND time — the first report was never recorded, so the queue re-served a closed item. Recorded now per the DAVID-grade rule: closes on his word, date written. NOTE, stated not hidden: the close-the-tab-mid-flow detached-credit variant is not confirmed as part of those two buys — if neither buy abandoned the tab, that specific path stays unexercised with real money; ordinary follow-up, not a launch gate.)
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
READ 28 Aug (didit.me pricing + product pages): Database Validation is listed with its own
"500 free / month" tier, "from $0.05", with premium government registries at $0.20+/check —
SA Home Affairs is almost certainly a premium source, so EXPECT the check to bill (the $1.10
class) despite the free-tier headline. The one real check stays decisive; docs are READ-grade.

## D11 · Travelpayouts tours — resubmit? — ALREADY DONE, nothing to decide
STATE: DONE 2026-09-06 — SUPERSEDED, the decision was taken and acted on 2 Sep
TIME: 0 minutes
VERIFY: DAVID
WHY_NOT_DAVID: This asked "say when and I prepare the submission". It was written against the
24 Aug decline. The THIRD resubmission has since gone in — 2 Sep 2026 — and the scheduled task
`travelpayouts-review-check-sep7` fires 7 Sep 09:00 to probe the outcome and record it. There is
no decision left to make; the answer arrives tomorrow.
NOTE 2026-09-06: found stale while answering David's "which is easy to fix next?" — the same
shape as D15. An item that asks for a decision already taken is worse than no item: it spends
his attention twice on the same thing.
CONTEXT: Declined 5 Aug and again 24 Aug (*"website under development or not yet ready"*).
RUL-041 bars resubmitting unchanged; soft launch was the material change that justified the
third attempt. 26 programs available / 20 blocked, including Booking.com, Viator, GetYourGuide.

## D12 · Delete ONE superseded Cloudflare token — DONE
STATE: DONE 2026-09-06 — deleted by David, and the deletion was VERIFIED not assumed
TIME: 0 — finished
VERIFY: DAVID
EVIDENCE 2026-09-06, after the deletion rather than before it:
  - the user token `trustsquare-cache` (Zone.Cache Rules, last used 22 Aug) is gone;
  - CDN purge still WORKS — a real single-URL purge against zone trustsquare.co returned
    success on the live account token, run on the server so the token never left the box;
  - site healthy, root 200.
  Nothing was leaning on the deleted token, which is what the pre-work predicted and what
  the risk in the original steps was about.
CONTEXT: Rotation residue from 22 Aug. The item said "two" — the other was already gone when
the dashboard was read on 28 Aug. The original instructions asked David to compare two token
ids by eye before deleting, because deleting the live purge token would have killed CDN purge
silently. That comparison was settled by probe on 6 Sep (the live token is an ACCOUNT token;
this was a USER token — different kinds, cannot be the same), so the job reduced to one click.

## D13 · Publish the deploy ref — closes the red card
STATE: DONE 2026-08-30 (David's 07:48 release — verified live: anon /dashboard/summary returns the bare heartbeat; RG-0198/RG-0211 LOCKED and passing)
TIME: 1 minute
VERIFY: LEDGER:RG-0211
WHY_DAVID: The sandbox holds no GitHub push credential (correct, DW-057 class) — publishing the
deploy ref needs your stored git credentials.
STEPS:
  1. Double-click `deploy_marketsquare.bat` (or any `git push` of HEAD to `deploy`).
  2. Done. The server engine places by manifest, health-checks, auto-rolls-back on failure;
     the first post-deploy ledger run flips RG-0198/RG-0211 to READY TO LOCK and the watch
     closes DW-078 with the live evidence.
CONTEXT: Carries the whole 30 Aug batch: the summary-endpoint heartbeat fix (the RED card),
/static sample rows, the Defence Coverage button + colour filter, and the gated map + watch
register (`/orchestrator/defence_map.html`, `/orchestrator/watch_register.md`) so the board is
phone-reachable per RUL-070.

## D14 · MS_API_KEY → sandbox .secrets — turns the failover blue GREEN
STATE: DONE 2026-08-30 — **turned out Claude's after all** (the queue's own celebrated pattern): the session key is authorized for root@, so the key was read from the RUNNING process env (RG-0147 point-of-use — the on-disk copies are all stale, see DW-084) directly into .secrets/ops_api_key.txt, never through David or chat. RG-0128 now reads 4 live lanes authenticated. David's forgotten sudo password was never needed.
TIME: 3 minutes
VERIFY: LEDGER:RG-0128
WHY_DAVID: The key is root-sealed on the box (`/etc/marketsquare/secrets.env`, 0600) — reading it
is a credential grant, reserved to you (RUL-027 class).
STEPS:
  1. PowerShell: `ssh msdeploy@178.104.73.239` then
     `sudo grep -r "MS_API_KEY" /etc/marketsquare/ /etc/systemd/system/marketsquare* 2>/dev/null`
     (sudo asks your root password).
  2. Copy ONLY the value after `MS_API_KEY=` into
     `C:\Users\David\Projects\MarketSquare\.secrets\ops_api_key.txt` — one line, no prefix.
     The folder is gitignored. **Never paste the key into chat** (the DW-029 burn class).
  3. Reply `D14 done` — the next session teaches RG-0128's live half to read the key and the
     failover card goes green by assertion.
CONTEXT: 30 Aug probe proved production HAS two non-Anthropic lanes (OpenAI + Gemini env keys
live); this grant lets the ledger SEE the lane count every run instead of trusting a dated note.
OPTIONAL SIBLING, same trip: a push-scoped GitHub PAT for the sandbox (fixes D13's class
permanently — sessions could then ship end-to-end when you say "close it for me").

## D15 · Push-scoped GitHub PAT for the sandbox — NO LONGER NEEDED
STATE: DONE 2026-09-06 — SUPERSEDED, the capability exists without the credential
TIME: 0 minutes — nothing for you to do
VERIFY: LEDGER:RG-0300
WHY_NOT_DAVID: This asked you to mint a fine-grained GitHub token so the sandbox could
publish. It was the right ask when written on 30 Aug. It was overtaken three days later
by the deploy relay (AUTODEPLOY-AGENT-1, 3 Sep): the sandbox pushes over SSH to the
server's checkout, and the SERVER pushes to GitHub with the credential it already holds.
No token in the sandbox, and your PC is not in the loop.
EVIDENCE 2026-09-06, probed not argued:
  - two commits sitting unpushed went `b099067..4a79b3c  claude-relay -> main` straight
    from the sandbox, with no token file present (`.secrets/github_push_token.txt` does
    not exist and never did);
  - six deploys rode the same lane earlier the same day;
  - the server authenticates to GitHub as a writer (`git ls-remote` over its own key).
WHY IT WAS NOT MINTED ANYWAY, since David offered: a second write credential to the code
repo, living in a file, expiring every 90 days, is a standing chore and a standing risk —
and 5 Sep was spent removing exactly that class of thing (a hand-typed heartbeat date, a
hand-remembered firewall flag, five hand-maintained copies of one script). The only window
a PAT would cover is SSH being down while David's PC is awake, and the host queue's
`git_push` already covers that window — while the SSH lockout class itself became
self-healing that morning (RG-0274). Redundancy that overlaps an existing path is not free.
CLOSES WHEN: it already has — RG-0300 asserts the publish lane is live on every ledger run,
so "Claude cannot ship" can never be re-derived from memory the way this item was.
IF YOU EVER WANT IT ANYWAY: the original steps are in git history; it would be a third,
independent path, not a fix for a missing one.


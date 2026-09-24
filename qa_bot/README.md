# QA Bot — the independent security auditor (QA-BOT-1, 24 Sep 2026)

David: *"the tester should not be a human tester. I am a one man owner, i need you to create an
independent QA Bot to perform the audit."*

## Who decides what

| Role | Who | Where it lives |
|---|---|---|
| Judge: what every route **should** require | OpenAI (a different vendor from the Author) | `/var/lib/trustsquare-qabot/policy.json` on the server only, never in git |
| Attacker: tries every protected route | this bot | `qa_bot/qa_bot.py`, runs on the server |
| Fixer | Claude (the Author) | the app code; it never writes the policy |
| Reader | David | an email only when something is red |

The Author can **appeal** a ruling (`qa_bot.py appeal "METHOD /path" "reason"`); OpenAI re-reads
the code with the objection and rules again. Every appeal and the earlier ruling stay on record.
On 24 Sep 2026 the Author appealed five rulings and OpenAI upheld all five
(`appeals_20260924.json`).

## What it tries

- **stranger**: no sign-in, no keys.
- **publickey**: only the `X-Api-Key` that ships inside the public `ms.js`.
- **intruder**: a real signed-in QA account aimed at a second QA account's archived advert
  and account.

It attacks through the front door (`https://trustsquare.co` pinned to the box, so nginx counts
and Cloudflare's limits do not). Every persona aims at real objects that belong to the QA
victim account. Every row in every table keyed by the victim's email is snapshotted first.
Anything a probe gets through is detected as a change and put back exactly. Any advert a probe
manages to create is taken down at once.

## Verdicts

PASS (refused) · FAIL (work done, data shown, object changed or created: evidence, not
guesses) · CRASH (a 5xx for a caller it should simply refuse) · UNPROVEN (the bot could not
get a well-formed request past validation, or had only a made-up target).

## When it runs

- **Every deploy**: `server_deploy.sh` runs `qa_bot.py gate` after the health check. If a
  route that was closed, or a brand-new route, is now open, the release is rolled back like an
  unhealthy one. That commit is not retried until a new commit (or `--force`) arrives.
- **Every night at 02:30 SAST**: `trustsquare-qabot.timer` (installed by migration 050) runs
  `qa_bot.py nightly`. That is the full attack plus OpenAI's review of the last 24 hours of
  code changes, including any change that weakens tests, this bot or the deploy gate. It
  emails the ops address only when something is red.

The gate **fails closed**: a bot that cannot run (crash, timeout) also refuses the release, and the
refused commit is not retried until a new commit arrives. The bot's own OpenAI spend has a **hard
daily cap** (`QA_DAILY_USD`, default $3). Past the cap, new routes stay unruled and are attacked as
protected. Both came from OpenAI's first nightly review, which reviewed the bot itself.

#!/usr/bin/env python3
"""AUTHZ-PROBE-1 — SUPERSEDED 24 Sep 2026 by the QA Bot (QA-BOT-1).

This was a stop-gap live authorization probe (built earlier the same day when David asked
"why did the watch not catch the app vulnerabilities?"). It found a real hole on its first
run: POST /admin/purge-cache answered anonymous callers (fixed as ADMIN-LOCALGUARD-1).

It is now FOLDED INTO the independent QA Bot, which does everything this did and more, so
there is ONE probe, not two:

  - qa_bot/qa_bot.py enumerates EVERY route from the live OpenAPI spec (no hand-kept case
    list to drift), attacks each as three personas -- stranger, public-key, and a real
    signed-in INTRUDER aimed at a second QA account's own objects (which catches the
    "public key gets past the gate" class this probe could only guess at with bogus targets).
  - OpenAI rules what every route SHOULD require (server policy, a different vendor from the
    author); the bot is the judge, Claude only fixes.
  - It runs ON the box (resolves trustsquare.co -> 127.0.0.1), so it is behind Cloudflare and
    never hits the bot-block that forced this probe to spoof a browser User-Agent.
  - It GATES every deploy and runs nightly; a release that opens a closed route is rolled back.

Run the real thing on the server instead:
    python3 qa_bot/qa_bot.py probe      # attack using the current rulings (no new AI spend)
    python3 qa_bot/qa_bot.py show       # what every route is ruled to require
See qa_bot/README.md. A security fix is done when the BOT says the route is closed.
"""
import sys

def main():
    sys.stderr.write(__doc__ + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())

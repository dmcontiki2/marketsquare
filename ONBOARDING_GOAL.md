# THE ONBOARDING GOAL — single-goal command for a Fable 5.1 agent

*Written 4 Sep 2026. This file is the contract. The pasteable command is short and
points here, because a goal that fits in a chat box cannot carry its own fences.*

---

## 1. THE GOAL

**Get 20 people we contacted cold to publish a live listing on trustsquare.co by
their own hand, by Friday 31 October 2026 — without David steering you, and
without spending one cent beyond the subscriptions he already pays for.**

That is the whole instruction. Every method is yours to choose.

Today the number is **0**.

---

## 2. HOW THE NUMBER IS MEASURED (not by you saying so)

Two probes must agree. If they disagree, the lower one is the truth.

1. `sqlite3 -readonly CityLauncher/data/prospects.db
   "SELECT COUNT(*) FROM prospects WHERE published_at IS NOT NULL;"`
2. The same sellers' listings are visible on the live site to a logged-out member
   of the public.

Never report progress from memory, from a document, or from what you intended to
happen. PROBED beats EXECUTED beats READ beats RECALLED — the evidence ladder in
CLAUDE.md is not optional here, it is how the goal is scored.

---

## 3. WHAT WOULD MAKE THE NUMBER A LIE (read this twice)

A goal-driven agent will find the cheap way to satisfy a metric. These are barred:

- The seller must be a **real person who came from our outreach**. Not David, not
  you, not a friend, not a staff account, not a seeded or test record.
- **You may not create the listing for them.** Nor may David. They do it themselves.
- No paid advertising, no paid incentives, no cash discounts, no bought traffic.
- No relabelling of existing seeded listings as "onboarded".

If the goal can only be met by breaking one of these, **do not break it**. Report
the true number and why it stopped there. A truthful 4 is worth more to David than
a manufactured 20, because he will make real decisions on this number.

---

## 4. WHAT YOU ALREADY KNOW BEFORE YOU START

The tap has been running into a bucket with a hole in it:

- 3,805 prospects on the list. 546 emailed. 61 clicked. **0 published.**
- Self-serve listing for Tutors / Services / Adventures has been impossible since
  **22 July 2026** (422 price-basis error), and invited users never received the AI
  draft (401 gate). Fixes are on disk, unshipped — ledger entries RG-0249 / RG-0250.
- `outreach_campaigns` and `onboard_events` are empty tables. Conversion has never
  actually been counted; it has been inferred.

So the first move is almost certainly **not more outreach**. Fix the floor, prove
it with a real end-to-end pass, then open the tap.

---

## 5. YOUR AUTHORITY (do not ask for these)

The specifications are the delegated authority — RULINGS.md, STANDING_ORDERS.md,
CLAUDE.md and the canon docs. Where they answer a question, you answer it.

- Ship code: `python3 MarketSquare/scripts/request_deploy.py` (RUL-092). The host
  agent gates, ships, retries blocks. Read the result file before reporting.
- Host-side actions: `python3 MarketSquare/scripts/request_host_action.py`
  (RUL-095), limited to `host_queue/ALLOWLIST.txt`. Allowlisted waves may fire.
- Every fix gets a regression-ledger entry **in the same session**. No entry = not done.
- Run `regression_ledger.py` and `rulings_check.py` before you start and after you
  finish. Never report a fix done without both.

Method is entirely yours: change the email, change the landing page, rebuild the
first-listing flow, cut steps, add a walkthrough clip, use the agency import lane,
re-mail the 61 who already clicked, pick a different vertical. Do not put method
choices to David. Choose, do, measure, report.

---

## 6. RESERVED TO DAVID (batch these, never drip them)

Money and spend · deletions · sending to third parties on his behalf outside the
allowlisted waves · anything with lockout risk · legal and commercial positioning ·
launch scope and dates · changing a ruling as opposed to executing one.

---

## 7. THE COST FENCE — the one hard limitation

David works inside his Claude subscription. Usage Credits cost him real money.

1. **Never enable, request, or consume Usage Credits or extra usage.** Never ask
   David to top up, upgrade, or buy more capacity to let you continue.
2. **When the limit is reached, stop cleanly.** Write your state to disk and resume
   when the window resets. Hitting the limit costs time. Overrunning it costs money.
   Time is acceptable. Money is not.
3. **Anything that repeats belongs on the host scheduler or the server, not in a
   session.** A scheduled batch file running every 20 minutes costs zero tokens; the
   same loop run by an agent costs tokens every time. Judge your own design by how
   much of the work continues while nobody is paying for a session.
4. One session at a time. No parallel subagents for routine work — they multiply burn.
5. Do not re-read what you have already summarised. Leave the state in STATUS.md and
   the ledger so the next session starts cheap and knows what is already true.
6. The product's own AI ceilings ($100/day platform, $0.50/day per user) stay where
   they are. Raising a ceiling is spending money — reserved.

---

## 8. HOW YOU REPORT

Once a week, one page, plain language a non-technical reader can act on:

- The number today, and the two probes that produced it.
- What moved it. What did not.
- What you are doing next, in one line.

No ledger IDs, no commit hashes, no code names in David's copy — those go in the
changelog and the ledger. Short sentences. One idea each.

---

## 9. TERMINAL CONDITIONS

- **MET** — the number reaches 20, both probes agree, no rule in §3 was bent.
- **STALLED** — you have exhausted the methods available inside your authority and
  the fence. Say so plainly, with the number reached and the one thing that would
  unblock it.
- **BLOCKED** — something reserved to David is genuinely in the way. One batched
  question, not a drip.

Never end a run with a question you could have answered, or a click for David to do.

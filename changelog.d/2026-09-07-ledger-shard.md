## 2026-09-07 — LEDGER-SHARD-1: the self-check board runs to a verdict again, in pieces

**David's question:** "can we now determine why the timing per full self check has changed, and what is?"

**Measured, not estimated.** Every entry timed individually (311 at the time of measuring):

| | |
|---|---|
| total check time | **250.7 s** (4.2 min) |
| median entry | **0.023 s** |
| entries under 0.5 s | **250 of 311** |
| entries over 5 s | 8 |
| slowest 7 entries | **155 s — 62% of the whole run** |

The seven: **RG-0025 52 s** (downloads the live index plus ten adventures map pages — ~20 MB
over the wire), **RG-0258 24 s** and **RG-0012 12 s** (live fetches), **RG-0259 22 s**,
**RG-0276 20 s**, **RG-0308 10 s** (each spawns a subprocess on the FUSE mount), **RG-0028 16 s**
(a connection that must time out to prove the origin refuses direct traffic).

**Why it changed.** The board grew from 13 entries (26 Jul) to 311 (7 Sep) — but that is *not*
the cause, and it matters that it isn't. 250 entries cost under half a second each; adding
cheap checks is free. Four of the seven heavy entries were added **4–6 Sep** (RG-0258/0259 on
the 4th, RG-0276 on the 5th, RG-0308 on the 6th), together ~76 s. That is when the run crossed
the ~180 s ceiling on a Cowork command and became unfinishable from this kind of session.

**CLASS:** run cost tracks the *heavy* checks, never the entry count. A check that downloads a
live page or spawns a process costs 10–50 s of every future run, forever.

**Fix — `--shard=k/n` and `--combine=n`.** Entries are split round-robin (`i % n`) so the heavy
ones spread across slices instead of stacking. Three shards measured **83 s / 57 s / 75 s** —
each comfortably inside the ceiling. `--combine` prints the verdict and carries the exit code.

Two properties, because a sharded board that lies is worse than no board:

* **One judging path.** `_judge()` was split out of `run()` and is used by both, so a shard and
  a full run cannot reach different verdicts.
* **Refuse, never warn.** `--combine` exits non-zero on a missing shard, a stale set, or a shard
  measured against a different ledger size. Proven both ways this session: a 311-entry shard set
  was refused the moment the ledger reached 312, and `--combine=4` refused with no shards run.

**First complete run in this session, through shards: 312 entries · 290 holding · 0 REGRESSED ·
0 UNVERIFIED · 22 open.** Locked as **RG-0319**.

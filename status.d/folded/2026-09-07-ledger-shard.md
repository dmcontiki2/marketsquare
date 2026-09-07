- **LEDGER-SHARD-1 (RG-0319).** The self-check board is runnable again from a capped session:
  `--shard=1/3 .. 3/3` then `--combine=3` (83s/57s/75s). `--combine` refuses a missing, stale or
  wrong-sized set rather than assembling a board nobody measured. Board is GREEN: 312 entries,
  0 regressed, 0 unverified, 22 open.
- **Measured cost of the board:** 250.7s total, median entry 0.023s, but 7 entries carry 62% of
  it (live page downloads + subprocess launches). Cost tracks heavy checks, not entry count.

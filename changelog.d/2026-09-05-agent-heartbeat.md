## 2026-09-05 — the agent was never broken; the instrument was (AGENT-HEARTBEAT-1)

David, seeing the report: *"The laptop did not go to sleep, it was still up and running when
i came online just now?"* He is right, and the earlier run was wrong twice over.

**What actually happened.** Three requests were queued at 01:33 SAST. The agent ran all three
at 01:51 — its very next 20-minute tick, 18 minutes later — and every one returned rc=0. The
agent was healthy the whole time.

**Why the ledger said otherwise.** `autodeploy_agent.bat` only calls the queue worker when a
`.req` already exists (`if exist "%HQ%\*.req"`). An idle agent therefore writes **nothing** to
`autodeploy_agent_log.txt`. Log silence is the normal state of a healthy agent with an empty
queue. RG-0257's live leg read the age of that log and called anything over 40 minutes a
REGRESSION — so queueing a request into any quiet stretch fired red instantly, blaming the
agent for silence that *preceded* the request.

**Why the report was worse than the ledger.** The ledger produced a false alarm; the run then
explained it away with "the PC was almost certainly asleep" — a guess, dressed as a finding,
in a message to David. Nothing probed it. RG-0133's rule says no instrument may default to a
healthy colour; the same rule holds in the other direction, and a guess offered as a cause is
the ladder's bottom rung (RECALLED) reported as its top one.

**Fix, both halves:**
- `autodeploy_agent.bat` now stamps `host_queue/agent_heartbeat.txt` on **every** tick, before
  any work and whether or not there is any. Aliveness is measured, not inferred from work the
  agent happened to have. Gitignored; one line, overwritten.
- RG-0257's live leg reads that heartbeat for aliveness, and judges lateness from how long a
  **request** has waited (a tick plus one tick of grace) — never from log silence. Its scope
  text carries the correction so the next reader is not misled by the old description.

CLASS: any check that infers a system's health from a side-effect it only produces when busy.
The cure is to make the thing observable, not to widen the threshold.

**Also confirmed this morning, probed:** the queued stop-loss clean ran and released all four
latched cities (Cape Town, Durban, Port Elizabeth, Pietermaritzburg). 12 of 14 lanes now pass
their gates; New York clears its one-day gap at tonight's run. **About 62 genuine individuals
go out at 00:10 on 6 Sep** — up from 5 real sends yesterday morning.

The number is unchanged: **0**.

## 2026-09-06 — SHIP-LANE-PROVEN-1: the publish credential was never needed (D15 closed, RG-0300)

David: *"lets fix this — one access token so I can publish code without routing everything through
your PC."*

**Fixed by not creating it.** The queue item was written 30 Aug and was right then. It was overtaken
three days later by the deploy relay (AUTODEPLOY-AGENT-1, 3 Sep): the sandbox pushes over SSH to the
server's own checkout, and **the server** pushes to GitHub with the credential it already holds. No
token in the sandbox, and David's PC is not in the loop.

**Proved rather than argued.** Two commits sitting unpushed went `b099067..4a79b3c  claude-relay ->
main` straight from the sandbox, with no token file present — `.secrets/github_push_token.txt` does not
exist and never did. Six deploys rode the same lane the day before. The server authenticates to GitHub
as a writer over its own key.

**Why it was not minted anyway, since it was offered.** A second write credential to the code repo,
living in a file, expiring every 90 days, is a standing chore and a standing risk — and 5 Sep was spent
removing exactly that class of thing: a hand-typed heartbeat date, a hand-remembered firewall flag, five
hand-maintained copies of one script. The only window a token would cover is SSH being down while
David's PC is awake, and the host queue's `git_push` already covers that window — while the SSH lockout
class itself became self-healing on 5 Sep (RG-0274). Redundancy that overlaps an existing path is not
free.

**Why this is a ledger entry and not just a closed queue item.** A capability nobody asserts is one the
next session asks for again — which is exactly what happened here. **RG-0300** now checks on every run
that the publish lane is live, so "Claude cannot ship" can never be re-derived from memory.

**Two faults found and fixed on the way.**

1. **My own probe could hang the entire board.** RG-0300's first cut called `load_sandbox_ssh.sh` with
   output captured. That loader starts an ssh ControlMaster in the background; the master inherits the
   captured pipes, and `subprocess.run` waits on the pipes forever — the timeout kills the child, not
   the pipe. The board sat at two lines for fifteen minutes. Rewritten to run ssh directly with stdin
   closed and stderr discarded: **4.2 seconds**. A probe that can stall the instrument is worse than one
   that reports UNVERIFIED.
2. **The queue checker had an unsatisfiable rule.** RG-0199 failed any item marked DONE that carried a
   machine-checkable verification — but not marking it left it counted as still open. Four items had
   been sitting in that contradiction. It now checks whether the named ledger entry exists and is
   LOCKED; if that entry ever rots, *it* goes red, which is where the failure belongs. Two of the four
   cleared immediately; the remaining two are claiming done against entries that are still open, which
   is the rule working correctly.

**David's queue is now four items**, all genuinely his: two that spend money, one commercial timing
call, and two Cloudflare tokens to delete.

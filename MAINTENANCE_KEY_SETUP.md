# Giving the Maintenance lane its own key (MS_MAINT_KEY)

**The problem, stated plainly.** A session can read your own fault reports with the public
app key, but it cannot see screenshots, set fault codes, mark duplicates, or send retest
letters. Those sit behind `/admin/faults`, which wants an admin credential.

**Why not just use `MS_ADMIN_KEY`.** That key opens the launch switches, the deploy channel,
the lifecycle sweep and the ledger. Handing it to a session to read a complaint queue is
the same mistake as SEC-1 on 23 July, where a leaked key had to be demoted after the fact.
Cheaper to scope it up front than to contain it later.

**What is now in the code.** `MS_MAINT_KEY` — a separate secret that opens exactly four
endpoints and nothing else:

| Endpoint | What it allows |
|---|---|
| `GET /admin/faults` | read the queue, including screenshots and detail |
| `PUT /admin/faults/{id}` | set fault code, bin, severity, status, mark duplicates |
| `GET /admin/faults/{id}/close-draft` | read the closure letter before it goes |
| `POST /admin/faults/{id}/close-send` | send it — the send closes the fault (NO-RETEST-1) |

A tripwire (`test_maintenance_key_opens_faults_and_nothing_else`) fails the pre-deploy check
if that list ever grows. The comparison is constant-time. The closure letter can only ever
mail the address already on the fault row, so this key cannot be aimed at an arbitrary
recipient. Your dashboard is unaffected — the ordinary admin paths still work.

**Blast radius if it leaks:** someone can read the fault queue and re-send a retest letter
to a reporter. They cannot flip a flag, deploy, touch the ledger, or move money.

---

## Setting it up — one block, nothing to substitute

**Lesson paid for on 5 Aug 2026:** the first version of this runbook used `PASTE_IT_HERE`
as a placeholder in three separate commands. David ran them verbatim — as anyone would —
and the literal string `PASTE_IT_HERE` went into the server `.env` and the secrets file,
while the real key was echoed to his terminal (and from there into a chat transcript,
burning it). **A runbook that requires hand-substitution of a secret is a defective
runbook.** This version substitutes nothing and prints nothing.

Copy the whole block into PowerShell:

```powershell
cd C:\Users\David\Projects\MarketSquare
$k = python -c "import secrets; print('ms_maint_' + secrets.token_urlsafe(32))"
$k | Out-File -Encoding ascii -NoNewline .secrets\ms_maint_key.txt
ssh root@178.104.73.239 "sed -i '/^MS_MAINT_KEY=/d' /var/www/marketsquare/.env; echo 'MS_MAINT_KEY=$k' >> /var/www/marketsquare/.env; systemctl restart marketsquare"
.\deploy_marketsquare.bat
```

What each line does, in case you ever need to do it by hand:

1. `$k = python -c ...` — generates the secret into a variable. **Assignment does not print**,
   so it never reaches the screen or your scrollback.
2. `Out-File` — writes it to `.secrets\ms_maint_key.txt` (gitignored), which is where a
   session reads it from.
3. The `ssh` line — `sed -i` **deletes any existing `MS_MAINT_KEY=` line first** (so a
   re-run replaces rather than duplicates), appends the real value, and restarts the BEA.
   PowerShell expands `$k` inside the double quotes before ssh ever sees it.
4. The deploy — ships the code that reads the key, and restarts once more.

## Verifying it

```powershell
$k = Get-Content .secrets\ms_maint_key.txt -Raw
curl.exe -s -H "X-Maint-Key: $k" "https://trustsquare.co/admin/faults?limit=3"
```

That returns the fault queue as JSON. **GATE NOTE (5 Aug 2026, found live):** since the edge gate (RG-0027/GATE-ENFORCE-1) went up, this curl — and ANY off-browser HTTP call — gets 403 at the edge BEFORE the key is examined. That is the gate working, not key drift. Maintenance tooling now runs ON the server against localhost over SSH (see RECONCILE_FAULTS.bat v2 for the pattern). If it returns `Admin credentials required`, the key
on the server and the key in the file have drifted — re-run the block above, which resets
both from one source.

## If a key is ever exposed

Re-run the block. It replaces the server value and the local file in one go, and the old
key stops working the moment the service restarts. There is no revocation list to maintain
because there is only ever one live value.

## What this does and does not unlock

- **Does:** a session with the device bridge can now triage, code, dedupe and close the
  loop end to end, including sending you the retest letter to approve.
- **Does not:** unattended overnight running. The key lives on your disk, so a session can
  only reach it while your desktop is online. True unattended operation is the B2 re-bind —
  a worker resident on the Hetzner box, reading the key from the server's own environment,
  with nothing travelling anywhere. That is the right end state; this is the right next step.

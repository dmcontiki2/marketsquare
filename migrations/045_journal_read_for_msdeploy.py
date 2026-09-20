#!/usr/bin/env python3
"""045_journal_read_for_msdeploy.py -- JOURNAL-READ-1 (20 Sep 2026).

Make the deploy account able to READ the application journal, permanently and
across a server rebuild.

Why: DW-111 sat OPEN in the daily-watch register for NINE DAYS -- nine separate
sessions each re-probed the same wall and wrote "still not verifiable from
here". `msdeploy` was in neither `adm` nor `systemd-journal`, so
`journalctl -u marketsquare` returned "-- No entries --" and
/var/www/marketsquare/*.log does not exist. Every session could therefore say
only "absence from a blind instrument is not a clean bill", which is honest and
useless. The question it was blocking -- which caller produced a Resend 422
every five minutes -- was answered in about four minutes once the journal could
actually be read: `_infra_resend()` POSTs an EMPTY BODY to Resend on purpose
(INFRA-RESEND-1, 22 Jul 2026) and treats 422 as "auth passed, nothing sent", and
the +1 dashboard polls /admin/services-status every five minutes. There was no
failing mail lane. Nine days of a register row for a probe working correctly.

Why the WHOLE journal and not a narrower grant: a sudoers rule like
`journalctl -u marketsquare *` looks tighter but is not -- the wildcard lets any
further `-u <unit>` be appended, so it grants the same breadth while pretending
otherwise, and a false fence is worse than an honest one. `msdeploy` already
owns and can read /var/www/marketsquare/.env (mode 0640, msdeploy:msdeploy), so
it already holds the application's own secrets; journal read adds no new
exposure of those. It is READ-ONLY and grants no write, no restart beyond the
three systemctl verbs msdeploy already has, and no root.

Idempotent and safe to re-run: usermod -aG is additive, and the script checks
first. Takes effect on the next LOGIN -- an existing multiplexed SSH session
keeps the old group set, which is why the verification below opens a fresh one.
"""
import grp
import pwd
import subprocess
import sys

USER = "msdeploy"
GROUP = "systemd-journal"


def in_group() -> bool:
    try:
        return USER in grp.getgrnam(GROUP).gr_mem
    except KeyError:
        return False


def main() -> int:
    try:
        pwd.getpwnam(USER)
    except KeyError:
        print("045: no %s account here -- nothing to do" % USER)
        return 0
    try:
        grp.getgrnam(GROUP)
    except KeyError:
        print("045: group %s does not exist on this host -- nothing to do" % GROUP)
        return 0

    if in_group():
        print("045: %s is already in %s -- nothing to do" % (USER, GROUP))
        return 0

    try:
        subprocess.run(["usermod", "-aG", GROUP, USER], check=True,
                       capture_output=True, text=True)
    except FileNotFoundError:
        print("045: usermod not found -- skipping (not a systemd host?)")
        return 0
    except subprocess.CalledProcessError as exc:
        # Never fail a deploy over an observability grant.
        print("045: could not add %s to %s (%s) -- deploy continues; "
              "DW-111's blindness returns until this is applied"
              % (USER, GROUP, (exc.stderr or "").strip()[:120]))
        return 0

    if in_group():
        print("045: %s added to %s -- journalctl -u marketsquare readable "
              "from the next login (JOURNAL-READ-1)" % (USER, GROUP))
    else:
        print("045: usermod reported success but %s is still not in %s" % (USER, GROUP))
    return 0


if __name__ == "__main__":
    sys.exit(main())

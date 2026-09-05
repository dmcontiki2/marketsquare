"""
request_host_action.py - Claude's side of HOST-QUEUE-1 (RUL-095). Writes a permission-backed
request that autodeploy_agent.bat executes on David's PC within ~20 minutes.

  python3 scripts/request_host_action.py git_push CityLauncher \
      --permission "David, 3 Sep 2026: 'build mechanisms to deploy and commit after I have given permission'" \
      --reason "publish exchange/ so Dave can pull it"

  python3 scripts/request_host_action.py run_bat "CityLauncher\\exchange_sync.bat" --permission "..." --reason "..."

Refuses to write a request without --permission. The action/arg must be on host_queue/ALLOWLIST.txt
(checked here too, so a typo is caught now, not 20 minutes later). Result appears in
host_queue/done/<name>.result - read it before reporting the action as done (evidence ladder).
"""
import argparse, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
QDIR = HERE / 'host_queue'
ALLOW = QDIR / 'ALLOWLIST.txt'

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('action'); ap.add_argument('arg')
    ap.add_argument('--permission', required=True, help="David's words + date that authorise this class of action")
    ap.add_argument('--reason', default='')
    a = ap.parse_args()
    allow = set()
    for l in ALLOW.read_text(encoding='utf-8').splitlines():
        l = l.strip()
        if l and not l.startswith('#'):
            p = l.split(None, 1)
            if len(p) == 2: allow.add((p[0].lower(), p[1].strip().lower()))
    if (a.action.lower(), a.arg.lower()) not in allow:
        print(f'REFUSED: ({a.action}, {a.arg}) is not on {ALLOW.name}. Add it there first (that is a visible change).')
        return 1
    if len(a.permission.strip()) < 15:
        print('REFUSED: --permission must quote David and a date.'); return 1
    QDIR.mkdir(exist_ok=True)
    import re
    # REQ-COLLIDE-1 (5 Sep 2026): the name used only the FILENAME of the argument, so
    # MarketSquare\commit.bat and CityLauncher\commit.bat both became "..._run_bat_commit"
    # -- and two requests queued in the same second silently OVERWROTE each other. That is
    # exactly what happened: a permission-backed MarketSquare commit vanished with no error
    # and no result file, and only the CityLauncher one survived. A queue that loses a
    # request without saying so is worse than one that refuses it. The slug now carries the
    # whole path, the timestamp carries milliseconds, and an existing name is never reused.
    slug = re.sub(r'[^A-Za-z0-9]+', '-', a.arg.replace('\\', '/').rsplit('.', 1)[0]).strip('-').lower()
    base = f'{datetime.now(timezone.utc):%Y%m%d-%H%M%S-%f}'[:-3] + f'_{a.action}_{slug}'
    name, n = base + '.req', 0
    while (QDIR / name).exists():                 # never clobber, whatever the clock says
        n += 1
        name = f'{base}-{n}.req'
    (QDIR / name).write_text(
        f'action={a.action}\narg={a.arg}\nrequested_at={datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}\n'
        f'permission={a.permission}\nreason={a.reason}\n', encoding='utf-8')
    print(f'queued {name} -> runs on the next agent tick (<=20 min); result in host_queue/done/')
    return 0

if __name__ == '__main__':
    sys.exit(main())

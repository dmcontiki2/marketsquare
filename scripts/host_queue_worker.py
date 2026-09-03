"""
host_queue_worker.py - HOST-QUEUE-1 (RUL-095, 3 Sep 2026). Runs ON DAVID'S PC, called by
autodeploy_agent.bat every 20 min. Executes permission-backed requests that Claude's sandbox
cannot perform itself (git push with David's credentials, bats that write the local DB, ...).

  MarketSquare\host_queue\*.req     one request per file, written by scripts/request_host_action.py
  MarketSquare\host_queue\ALLOWLIST.txt   the ONLY actions that may run (action + argument)
  MarketSquare\host_queue\done\<name>.result   verdict + output tail, request moved beside it

A request MUST carry a `permission=` line quoting David's words and date. No permission line,
or an action/argument not on the allowlist = REFUSED (result written, nothing run). This is the
guardrail: the click became a permission, the permission is on record, the machine does the click.
Long jobs are fine: the agent tick just waits. One request at a time, oldest first, so two
DB-writing bats can never overlap.
"""
import subprocess, sys, shutil
from datetime import datetime
from pathlib import Path

HERE   = Path(__file__).resolve().parent.parent          # MarketSquare
ROOT   = HERE.parent                                     # Projects
QDIR   = HERE / 'host_queue'
DONE   = QDIR / 'done'
ALLOW  = QDIR / 'ALLOWLIST.txt'
LOG    = HERE / 'autodeploy_agent_log.txt'

def log(msg: str):
    line = f'{datetime.now():%Y-%m-%d %H:%M:%S}  [host_queue] {msg}'
    print(line)
    with LOG.open('a', encoding='utf-8') as f: f.write(line + '\n')

def allowlist() -> set[tuple[str, str]]:
    out = set()
    for l in ALLOW.read_text(encoding='utf-8').splitlines():
        l = l.strip()
        if not l or l.startswith('#'): continue
        parts = l.split(None, 1)
        if len(parts) == 2: out.add((parts[0].lower(), parts[1].strip().lower()))
    return out

def parse(req: Path) -> dict:
    d = {}
    for l in req.read_text(encoding='utf-8').splitlines():
        if '=' in l:
            k, v = l.split('=', 1); d[k.strip().lower()] = v.strip()
    return d

def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=str(cwd), stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       errors='replace', timeout=6 * 3600)
    return p.returncode, (p.stdout or '') + (p.stderr or '')

def execute(action: str, arg: str) -> tuple[int, str]:
    if action == 'git_push':
        repo = ROOT / arg
        subprocess.run([str(HERE / 'git_unlock.bat')], cwd=str(repo), stdin=subprocess.DEVNULL,
                       capture_output=True)
        return run(['git', 'push', 'origin', 'HEAD:main'], repo)
    if action == 'run_bat':
        bat = ROOT / arg
        return run(['cmd', '/c', 'call', str(bat)], bat.parent)
    if action == 'run_py':
        py = ROOT / arg
        # project root = first path segment (CityLauncher\...), so `python -m`/imports resolve
        proj = ROOT / Path(arg).parts[0]
        return run(['python', str(py)], proj)
    return 2, f'unknown action {action}'

def main() -> int:
    DONE.mkdir(parents=True, exist_ok=True)
    reqs = sorted(QDIR.glob('*.req'), key=lambda p: p.stat().st_mtime)
    if not reqs: return 0
    allow = allowlist()
    for req in reqs:
        d = parse(req)
        action, arg = d.get('action', '').lower(), d.get('arg', '')
        perm = d.get('permission', '').strip()
        verdict, rc, out = 'REFUSED', 1, ''
        if not perm:
            out = 'no permission= line - a request must quote David\'s words and date'
        elif (action, arg.lower()) not in allow:
            out = f'({action}, {arg}) is not on ALLOWLIST.txt'
        else:
            log(f'RUN {req.name}: {action} {arg}  [{perm}]')
            try:
                rc, out = execute(action, arg)
                verdict = 'DONE' if rc == 0 else 'FAILED'
            except Exception as ex:
                rc, out, verdict = 1, repr(ex), 'FAILED'
        tail = out[-4000:]
        res = DONE / (req.stem + '.result')
        res.write_text(f'{verdict} rc={rc} at {datetime.now():%Y-%m-%d %H:%M:%S}\n'
                       f'action={action}\narg={arg}\npermission={perm}\nreason={d.get("reason","")}\n'
                       f'--- output tail ---\n{tail}\n', encoding='utf-8')
        shutil.move(str(req), str(DONE / req.name))
        log(f'{verdict} {req.name} rc={rc}')
    return 0

if __name__ == '__main__':
    sys.exit(main())

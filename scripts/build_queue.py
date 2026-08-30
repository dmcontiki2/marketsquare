#!/usr/bin/env python3
"""
build_queue.py - BUILD-QUEUE-1 (30 Aug 2026)

The to-be-built board, DERIVED from the regression ledger's OPEN entries.
One source of truth: this script never stores its own list -- it parses a
ledger run (live, or --from a saved run) and renders two views:
  BUILD_QUEUE.md    (repo, generated, dated -- DO NOT HAND-EDIT)
  build_queue.html  (visual board for David; index into Projects/Visuals)
An OPEN entry that starts passing prints READY TO LOCK in the ledger itself;
here it turns green. Born of David's question: "How do we not forget these
very important to-be-done design additions?" -- answer: the machinery already
cannot forget them; this makes the queue VISIBLE in one glance.
"""
import argparse, re, subprocess, sys, html
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

def get_run(from_file):
    if from_file:
        return Path(from_file).read_text(encoding='utf-8', errors='replace')
    r = subprocess.run([sys.executable, str(HERE / 'regression_ledger.py')],
                       capture_output=True, text=True)
    return r.stdout + r.stderr

def parse(run):
    entries, cur = [], None
    for line in run.splitlines():
        m = re.match(r'\[ open \] (RG-\d+)\s+(.*)', line)
        if m:
            cur = {'id': m.group(1), 'title': m.group(2).strip(), 'detail': '', 'ready': False}
            entries.append(cur); continue
        if cur is not None:
            s = line.strip()
            if s.startswith('open:') or s.startswith('info:'):
                cur['detail'] = s.split(':', 1)[1].strip()
                if 'READY TO LOCK' in line.upper() or s.startswith('info:'):
                    cur['ready'] = 'READY TO LOCK' in line.upper() or s.startswith('info:')
            elif line.startswith('[') :
                cur = None
    return entries

def render(entries, run):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    verdict = 'LEDGER RED - fix regressions before building features' if 'HAVE COME BACK' in run else 'ledger otherwise green'
    md = [f'# BUILD QUEUE - generated {now} - DO NOT HAND-EDIT',
          f'*Derived from regression_ledger.py OPEN entries ({len(entries)} waiting). '
          f'The ledger is the single source; edit nothing here - build the item, the ledger '
          f'prints READY TO LOCK, a session promotes it, and the row vanishes. {verdict}.*', '']
    for e in entries:
        flag = 'READY TO LOCK' if e['ready'] else 'waiting'
        md.append(f"- **{e['id']}** [{flag}] {e['title']}")
        if e['detail']:
            md.append(f"    - {e['detail'][:220]}")
    (REPO / 'BUILD_QUEUE.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    cards = ''
    for e in entries:
        cls = 'ready' if e['ready'] else 'wait'
        cards += (f'<div class="card {cls}"><div class="rid">{e["id"]}'
                  f'<span class="st">{"READY TO LOCK" if e["ready"] else "waiting"}</span></div>'
                  f'<div class="t">{html.escape(e["title"])}</div>'
                  f'<div class="d">{html.escape(e["detail"][:260])}</div></div>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Build Queue - TrustSquare</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{font-family:Segoe UI,system-ui,sans-serif;background:#f4f6fa;margin:0;color:#16233b}}
header{{background:#0f2a52;color:#fff;padding:16px 24px}}h1{{margin:0;font-size:19px}}
header p{{margin:4px 0 0;font-size:12px;opacity:.85}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px;padding:18px 24px}}
.card{{background:#fff;border-left:5px solid #d97706;border-radius:6px;padding:12px 14px;box-shadow:0 1px 4px rgba(15,42,82,.08)}}
.card.ready{{border-left-color:#15803d}}
.rid{{font-weight:700;color:#0f2a52;font-size:13px}}.st{{float:right;font-size:10px;font-weight:600;
padding:2px 8px;border-radius:9px;background:#fef3c7;color:#92400e}}
.ready .st{{background:#dcfce7;color:#166534}}
.t{{font-size:13px;margin:6px 0 4px;line-height:1.35}}.d{{font-size:11px;color:#5a6a85;line-height:1.35}}
</style></head><body><header><h1>Build Queue - the machinery's memory</h1>
<p>Generated {now} from regression_ledger.py OPEN entries - {len(entries)} item(s) - {verdict}.
Amber = waiting to be built. Green = built and READY TO LOCK. This page is DERIVED: the ledger is the only truth.</p>
</header><div class="grid">{cards}</div></body></html>"""
    (REPO / 'build_queue.html').write_text(page, encoding='utf-8')
    print(f'[build_queue] {len(entries)} OPEN entries -> BUILD_QUEUE.md + build_queue.html ({verdict})')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='from_file', default=None, help='saved ledger run (else runs live)')
    a = ap.parse_args()
    run = get_run(a.from_file)
    render(parse(run), run)

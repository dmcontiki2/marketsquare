#!/bin/bash
# Run before every deploy to catch JS syntax errors in HTML script blocks
# Usage: bash check_js_syntax.sh [file]
FILE=${1:-marketsquare.html}
python3 - << PYEOF
import subprocess, tempfile, re, os, sys

path = '$FILE' if '$FILE'.startswith('/') else f'/sessions/laughing-wonderful-albattani/mnt/MarketSquare/$FILE'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
errors = []
for i, s in enumerate(scripts):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tf:
        tf.write(s)
        name = tf.name
    r = subprocess.run(['node', '--check', name], capture_output=True, text=True)
    if r.returncode != 0:
        errors.append((i, r.stderr.strip()))
    os.unlink(name)

if errors:
    print(f'FAIL — {len(errors)} syntax error(s) in {path}:')
    for i, e in errors:
        print(f'  Block {i}: {e[:300]}')
    sys.exit(1)
else:
    print(f'OK — all {len(scripts)} script blocks in {path} pass syntax check')
PYEOF

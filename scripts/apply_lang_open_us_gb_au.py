#!/usr/bin/env python3
"""apply_lang_open_us_gb_au.py -- LANG-OPEN-1 (RUL-204, David 5 Oct 2026).

David, 5 Oct 2026: "lets make the languages active - it is worth the small risk of people giving us
more grammar complaints, and then we can use it to improve". AMENDS RUL-165(b) for the US, the UK
and Australia: their approved languages go from 'prepared' to 'offered'.

PROBED first: 'prepared' had never meant 'translated' -- Quick carried words for the five ZA
languages only. So this script also lands Claude's drafts (RUL-160: Claude drafts, readers and the
Language reviewer correct after launch) for the ten languages, from
roles/quick_i18n_new_langs_2026-10-05.json (826 strings each: 786 words, 6 phrases, 34 patterns,
keyed by position w### / p## / r## in roles/quick_i18n.json as it stood on 5 Oct 2026).

Steps (idempotent; asserts every anchor):
  1. roles/quick_i18n.json  -- append es zh tl vi cy pl ro pa ar yue as columns
  2. roles/lang_countries.json -- US / GB / AU: prepared -> offered (NA, BW, MZ, KE, DE untouched)
  3. quick.html -- the language table names every language Quick can speak; Arabic reads right-to-left
  then run scripts/sync_quick_roles.py (QI18N) and scripts/apply_lang_country.py (per-country table +
  HARNESS copy).
"""
import io, json, os, re, shutil, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE)
TS = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
NEW = ['es', 'zh', 'tl', 'vi', 'cy', 'pl', 'ro', 'pa', 'ar', 'yue']
def bak(p): shutil.copy2(p, p + '.bak-langopen-' + TS)
def save_json(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as fh: json.dump(d, fh, ensure_ascii=False, indent=1)
    json.load(io.open(p, encoding='utf-8'))   # proves it landed whole

# 1. quick_i18n.json
QP = os.path.join(MS, 'roles', 'quick_i18n.json')
q = json.load(io.open(QP, encoding='utf-8'))
if 'es' not in q['langs']:
    T = json.load(io.open(os.path.join(MS, 'roles', 'quick_i18n_new_langs_2026-10-05.json'), encoding='utf-8'))
    keys = list(q['w'].keys())
    assert len(keys) == 786 and len(q['p']) == 6 and len(q['r']) == 34, 'quick_i18n.json changed shape since the drafts'
    nl = len(q['langs'])
    for i, k in enumerate(keys):
        assert len(q['w'][k]) == nl
        q['w'][k] = q['w'][k] + [T[l]['w%03d' % i] for l in NEW]
    for i, row in enumerate(q['p']):
        q['p'][i] = row + [T[l]['p%02d' % i] for l in NEW]
    for i, row in enumerate(q['r']):
        q['r'][i] = row + [T[l]['r%02d' % i] for l in NEW]
    q['langs'] = q['langs'] + NEW
    q['_about'] += (" 5 Oct 2026 (RUL-204, David: 'lets make the languages active - it is worth the small risk of people "
                    "giving us more grammar complaints, and then we can use it to improve'): Claude's drafts for the US, UK and "
                    "Australian languages added -- es zh tl vi cy pl ro pa ar yue -- to be corrected from readers' flags (RUL-160).")
    bak(QP); save_json(QP, q); print('quick_i18n.json: +%d languages' % len(NEW))
else:
    print('quick_i18n.json: already carries the new languages')

# 2. lang_countries.json -- done as a text edit on the three country lines so the file keeps its shape
LP = os.path.join(MS, 'roles', 'lang_countries.json')
s = io.open(LP, encoding='utf-8').read(); o = s
for cc in ('US', 'GB', 'AU'):
    m = re.search(r'^  "%s": \{.*\},?$' % cc, s, re.M); assert m, cc
    line = m.group(0); s = s.replace(line, line.replace('"prepared"]', '"offered"]'))
if 'RUL-204' not in s:
    s = s.replace('English stays on everywhere."', 'English stays on everywhere. RUL-204 (David, 5 Oct 2026): the US, the UK and Australia go live in their languages now; the other countries stay prepared."', 1)
if s != o:
    bak(LP); io.open(LP, 'w', encoding='utf-8', newline='').write(s)
d = json.load(io.open(LP, encoding='utf-8'))
for cc in ('US', 'GB', 'AU'):
    assert all(st == 'offered' for c, st in d['countries'][cc]['langs']), cc
for cc in ('NA', 'BW', 'MZ', 'KE', 'DE'):
    assert any(st == 'prepared' for c, st in d['countries'][cc]['langs']), cc
print('lang_countries.json: US/GB/AU offered')

# 3. quick.html
Q = os.path.join(MS, 'quick.html'); src = io.open(Q, encoding='utf-8').read(); orig = src
names = d['names']
a = "  QLANGS=[['en','English'],['zu','isiZulu'],['xh','isiXhosa'],['af','Afrikaans'],['nso','Sepedi']];\n"
if a in src:
    full = [['en', 'English'], ['zu', 'isiZulu'], ['xh', 'isiXhosa'], ['af', 'Afrikaans'], ['nso', 'Sepedi']] + [[l, names[l]] for l in NEW]
    src = src.replace(a, "  /* LANG-OPEN-1 (RUL-204, 5 Oct 2026): every language Quick can speak; LANG-COUNTRY-1 narrows it to her country */\n"
                         "  QLANGS=" + json.dumps(full, ensure_ascii=False).replace('"', "'") + ";\n")
else:
    assert "LANG-OPEN-1 (RUL-204" in src, 'QLANGS anchor'
g = "  document.documentElement.lang=QLANG;\n  SVC_SPEAKS_MAIN=['English','isiZulu','isiXhosa','Afrikaans','Sepedi'];"
rtl = ("  document.documentElement.lang=QLANG;\n"
       "  /* LANG-OPEN-1: Arabic reads right-to-left inside every line, while the screen layout stays as it is */\n"
       "  try{ var _rs=document.createElement('style'); _rs.textContent='html[lang=ar] #app *{unicode-bidi:plaintext}'; document.head.appendChild(_rs); }catch(_){}\n"
       "  SVC_SPEAKS_MAIN=['English','isiZulu','isiXhosa','Afrikaans','Sepedi'];")
if "html[lang=ar] #app *{unicode-bidi:plaintext}" not in src:
    assert src.count(g) == 1, 'rtl anchor'; src = src.replace(g, rtl)
if src != orig:
    bak(Q); io.open(Q, 'w', encoding='utf-8', newline='').write(src)
print('quick.html: language table + Arabic direction')

for cmd in (['python3', os.path.join(HERE, 'sync_quick_roles.py')], ['python3', os.path.join(HERE, 'apply_lang_country.py')]):
    r = subprocess.run(cmd, cwd=MS, capture_output=True, text=True); print(r.stdout.strip()[-300:] or r.stderr.strip()[-300:])
    assert r.returncode == 0, cmd

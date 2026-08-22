#!/usr/bin/env python3
"""cleanup_catalog_keys.py - strip stale (quoted) definitions and verify properly.
PRINTS NO SECRET VALUES."""
import glob, hashlib, json, os, re, shutil, subprocess, time, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
KEYS = ("NUMISTA_API_KEY", "JUSTTCG_API_KEY")
DROPDIR = "/etc/systemd/system/marketsquare.service.d"
CANON = os.path.join(DROPDIR, "zz-catalog-keys.conf")
STAMP = time.strftime("%Y%m%d-%H%M%S")

print("  === strip stale definitions (quote-aware this time) ===")
targets = []
frag = out("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): targets.append(frag)
targets += sorted(glob.glob(os.path.join(DROPDIR, "*.conf")))
for t in list(targets):
    for m in re.finditer(r'(?m)^\s*EnvironmentFile\s*=\s*-?(\S+)', open(t, errors="replace").read()):
        if os.path.isfile(m.group(1)) and m.group(1) not in targets: targets.append(m.group(1))

n = 0
for t in targets:
    if os.path.abspath(t) == os.path.abspath(CANON): continue
    src = open(t, errors="replace").read()
    hits = []
    for k in KEYS:
        m = re.search(r'(?m)^\s*(?:Environment=)?"?%s=([^"\n]*)"?\s*$' % k, src)
        if m: hits.append((k, m.group(1).strip()))
    if not hits: continue
    shutil.copy2(t, "%s.bak-%s" % (t, STAMP))
    for k, v in hits:
        src = re.sub(r'(?m)^\s*(?:Environment=)?"?%s=.*\n?' % k, "", src)
        print("    [OK] removed %s from %-24s (held %s - now off disk)" % (k, os.path.basename(t), fp(v)))
        n += 1
    open(t, "w").write(src)
print("    %d stale definition(s) removed" % n)

if n:
    sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v

print("\n  === verify (full response read, then parsed - the last bug was mine) ===")
def call(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.read().decode("utf8", "replace")

k = env.get("NUMISTA_API_KEY", "")
print("  [--] NUMISTA_API_KEY fingerprint %s" % fp(k))
try:
    st, body = call("https://api.numista.com/api/v3/types?q=krugerrand&lang=en",
                    {"Numista-API-Key": k, "User-Agent": "TrustSquare/1.0"})
    try:
        d = json.loads(body)
        cnt = d.get("count", len(d.get("types", [])))
        print("  [OK] NUMISTA AUTH PASSED - HTTP %s, %s catalogue match(es)" % (st, cnt))
    except Exception:
        print("  [OK] NUMISTA AUTH PASSED - HTTP %s (body not JSON-parseable, but auth succeeded)" % st)
except urllib.error.HTTPError as e:
    print("  [X]  NUMISTA REJECTED: HTTP %s" % e.code)
except Exception as e:
    print("  [?]  numista: %s" % str(e)[:120])

k = env.get("JUSTTCG_API_KEY", "")
print("  [--] JUSTTCG_API_KEY fingerprint %s" % fp(k))
try:
    st, body = call("https://api.justtcg.com/v1/cards?q=charizard",
                    {"x-api-key": k, "User-Agent": "TrustSquare/1.0"})
    try:
        meta = (json.loads(body) or {}).get("meta", {})
        print("  [OK] JUSTTCG AUTH PASSED - HTTP %s, %s call(s) remaining this period"
              % (st, meta.get("api_calls_remaining", "?")))
    except Exception:
        print("  [OK] JUSTTCG AUTH PASSED - HTTP %s" % st)
except urllib.error.HTTPError as e:
    print("  [X]  JUSTTCG REJECTED: HTTP %s" % e.code)
except Exception as e:
    print("  [?]  justtcg: %s" % str(e)[:120])

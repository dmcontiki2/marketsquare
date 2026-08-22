#!/usr/bin/env python3
"""install_catalog_keys.py NUMISTA JUSTTCG - rotate the collectibles catalogue keys.
Pass "-" to skip either. PRINTS NO SECRET VALUES."""
import glob, hashlib, json, os, re, shutil, subprocess, sys, time, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

num, jtc = sys.argv[1].strip(), sys.argv[2].strip()
wanted = {}
if num != "-": wanted["NUMISTA_API_KEY"] = num
if jtc != "-": wanted["JUSTTCG_API_KEY"] = jtc
if not wanted:
    print("  nothing to do"); raise SystemExit(0)

DROPDIR = "/etc/systemd/system/marketsquare.service.d"
CANON = os.path.join(DROPDIR, "zz-catalog-keys.conf")   # sorts LAST: wins on precedence
STAMP = time.strftime("%Y%m%d-%H%M%S")

def senv():
    pid = out("systemctl show -p MainPID --value marketsquare"); d = {}
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if "=" in e:
                k, v = e.split("=", 1); d[k] = v
    except Exception: pass
    return d

before = senv()
print("  === before ===")
for k in wanted:
    print("  [--] live %-18s %s" % (k, fp(before.get(k, ""))))

# canonical file, last in sort order
lines = ["[Service]"]
for k in ("NUMISTA_API_KEY", "JUSTTCG_API_KEY"):
    v = wanted.get(k, before.get(k, ""))
    if v: lines.append("Environment=%s=%s" % (k, v))
u = os.umask(0o077)
open(CANON, "w").write("\n".join(lines) + "\n")
os.umask(u); os.chmod(CANON, 0o600)
print("\n  === install ===")
print("  [OK] wrote %s (0600, sorts last so nothing can override it)" % os.path.basename(CANON))

# strip every OTHER definition - the precedence lesson, applied up front
targets = []
frag = out("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): targets.append(frag)
targets += sorted(glob.glob(os.path.join(DROPDIR, "*.conf")))
for t in list(targets):
    for m in re.finditer(r'(?m)^\s*EnvironmentFile\s*=\s*-?(\S+)', open(t, errors="replace").read()):
        if os.path.isfile(m.group(1)) and m.group(1) not in targets: targets.append(m.group(1))
for t in targets:
    if os.path.abspath(t) == os.path.abspath(CANON): continue
    src = open(t, errors="replace").read()
    hit = [k for k in wanted if re.search(r'(?m)^\s*(?:Environment=)?%s=' % k, src)]
    if not hit: continue
    shutil.copy2(t, "%s.bak-%s" % (t, STAMP))
    for k in hit:
        src = re.sub(r'(?m)^\s*(?:Environment=)?%s=.*\n?' % k, "", src)
    open(t, "w").write(src)
    print("  [OK] removed %s from %s" % (", ".join(hit), os.path.basename(t)))

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

print("\n  === verify by exercising each key's OWN scope ===")
env = senv()
def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()[:400].decode("utf8", "replace")

if "NUMISTA_API_KEY" in wanted:
    k = env.get("NUMISTA_API_KEY", "")
    print("  [%s] NUMISTA_API_KEY live fingerprint %s" % ("OK" if k == num else "X ", fp(k)))
    try:
        st, body = get("https://api.numista.com/api/v3/types?q=krugerrand&lang=en",
                       {"Numista-API-Key": k, "User-Agent": "TrustSquare/1.0"})
        n = len(json.loads(body).get("types", [])) if body.strip().startswith("{") else "?"
        print("  [OK] NUMISTA AUTH PASSED - HTTP %s, catalogue answered" % st)
    except urllib.error.HTTPError as e:
        print("  [X]  NUMISTA REJECTED: HTTP %s" % e.code)
    except Exception as e:
        print("  [?]  numista: %s" % str(e)[:110])

if "JUSTTCG_API_KEY" in wanted:
    k = env.get("JUSTTCG_API_KEY", "")
    print("  [%s] JUSTTCG_API_KEY live fingerprint %s" % ("OK" if k == jtc else "X ", fp(k)))
    try:
        st, body = get("https://api.justtcg.com/v1/cards?q=charizard",
                       {"x-api-key": k, "User-Agent": "TrustSquare/1.0"})
        print("  [OK] JUSTTCG AUTH PASSED - HTTP %s, card search answered" % st)
    except urllib.error.HTTPError as e:
        print("  [X]  JUSTTCG REJECTED: HTTP %s" % e.code)
    except Exception as e:
        print("  [?]  justtcg: %s" % str(e)[:110])

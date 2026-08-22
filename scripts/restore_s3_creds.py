#!/usr/bin/env python3
"""restore_s3_creds.py - put the previous (working) R2 credentials back. NO VALUES PRINTED."""
import glob, hashlib, os, re, subprocess, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
KEYS = ("HETZNER_S3_ACCESS_KEY", "HETZNER_S3_SECRET_KEY")
DROPIN = "/etc/systemd/system/marketsquare.service.d/hetzner_s3.conf"

found = {}
for b in sorted(glob.glob("/etc/environment.bak-*"), key=os.path.getmtime, reverse=True):
    txt = open(b, errors="replace").read()
    got = {k: m.group(1).strip() for k in KEYS
           for m in [re.search(r'(?m)^\s*%s=(.*)$' % k, txt)] if m}
    if len(got) == 2:
        found = got
        print("  [OK] recovered the previous pair from %s" % os.path.basename(b))
        break
if not found:
    print("  [X]  no backup carries both keys - cannot restore automatically"); raise SystemExit(1)

print("  [--] restoring fingerprints %s / %s" % (fp(found[KEYS[0]]), fp(found[KEYS[1]])))
old = os.umask(0o077)
with open(DROPIN, "w") as f:
    f.write("[Service]\n" + "".join("Environment=%s=%s\n" % (k, found[k]) for k in KEYS))
os.umask(old); os.chmod(DROPIN, 0o600)
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
try:
    import boto3
    from botocore.client import Config
    c = boto3.client("s3", endpoint_url=env.get("HETZNER_S3_ENDPOINT"),
                     aws_access_key_id=env.get(KEYS[0]), aws_secret_access_key=env.get(KEYS[1]),
                     config=Config(signature_version="s3v4"))
    r = c.list_objects_v2(Bucket=env.get("HETZNER_S3_BUCKET"), MaxKeys=5)
    print("  [OK] PHOTO STORAGE WORKING AGAIN - listed the bucket, %s object(s) reported"
          % r.get("KeyCount", "?"))
    print("  [--] endpoint in use: %s" % env.get("HETZNER_S3_ENDPOINT"))
except Exception as e:
    print("  [X]  still failing: %s" % str(e)[:160])

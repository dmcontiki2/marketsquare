#!/usr/bin/env python3
"""install_hetzner_s3.py - rotate the Object Storage credentials. argv: access_key secret_key
PRINTS NO SECRET VALUES."""
import hashlib, os, re, shutil, subprocess, sys, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

ak, sk = sys.argv[1].strip(), sys.argv[2].strip()
DROPIN = "/etc/systemd/system/marketsquare.service.d/hetzner_s3.conf"
ENVFILE = "/etc/environment"
APPENV = "/var/www/marketsquare/.env"
STAMP = time.strftime("%Y%m%d-%H%M%S")
KEYS = ("HETZNER_S3_ACCESS_KEY", "HETZNER_S3_SECRET_KEY")

def env_of_service():
    pid = out("systemctl show -p MainPID --value marketsquare")
    d = {}
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if "=" in e:
                k, v = e.split("=", 1); d[k] = v
    except Exception: pass
    return d

before = env_of_service()
print("  === before ===")
for k in KEYS:
    print("  [--] live %-24s %s" % (k, fp(before.get(k, ""))))
print("  [--] endpoint : %s" % (before.get("HETZNER_S3_ENDPOINT") or "NOT SET"))
print("  [--] bucket   : %s" % (before.get("HETZNER_S3_BUCKET") or "NOT SET"))

print("\n  === install ===")
old = os.umask(0o077)
with open(DROPIN, "w") as f:
    f.write("[Service]\nEnvironment=%s=%s\nEnvironment=%s=%s\n" % (KEYS[0], ak, KEYS[1], sk))
os.umask(old); os.chmod(DROPIN, 0o600)
print("  [OK] wrote %s (0600)" % DROPIN)

for f in (ENVFILE, APPENV):
    if not os.path.isfile(f): continue
    src = open(f, errors="replace").read()
    if not any(re.search(r'(?m)^\s*%s=' % k, src) for k in KEYS): continue
    shutil.copy2(f, "%s.bak-%s" % (f, STAMP))
    if f == ENVFILE:
        for k in KEYS:
            src = re.sub(r'(?m)^\s*%s=.*\n?' % k, "", src)
        open(f, "w").write(src); os.chmod(f, 0o600)
        print("  [OK] removed both keys from %s (box-wide file)" % f)
    else:
        for k, v in zip(KEYS, (ak, sk)):
            src = re.sub(r'(?m)^(\s*%s=).*$' % k, lambda m: m.group(1) + v, src)
        open(f, "w").write(src)
        print("  [OK] updated both keys in %s" % f)

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

print("\n  === verify at the point of USE (RG-0147) ===")
after = env_of_service()
ok = after.get(KEYS[0]) == ak and after.get(KEYS[1]) == sk
print("  [%s] live process now holds the new pair (%s / %s)"
      % ("OK" if ok else "X ", fp(after.get(KEYS[0], "")), fp(after.get(KEYS[1], ""))))
try:
    import boto3
    from botocore.client import Config
    c = boto3.client("s3", endpoint_url=after.get("HETZNER_S3_ENDPOINT"),
                     aws_access_key_id=after.get(KEYS[0]),
                     aws_secret_access_key=after.get(KEYS[1]),
                     config=Config(signature_version="s3v4"))
    r = c.list_objects_v2(Bucket=after.get("HETZNER_S3_BUCKET"), MaxKeys=5)
    print("  [OK] AUTH PASSED - listed the bucket (%d object(s) sampled, %s total reported)"
          % (len(r.get("Contents", [])), r.get("KeyCount", "?")))
except Exception as e:
    print("  [X]  S3 call FAILED: %s" % str(e)[:160])

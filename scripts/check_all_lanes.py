#!/usr/bin/env python3
"""check_all_lanes.py - which lanes still authenticate? NO SECRET VALUES."""
import hashlib, json, subprocess, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v

print("  === R2 photo storage (HETZNER_S3_* -> Cloudflare R2) ===")
print("  [--] key pair: %s / %s" % (fp(env.get("HETZNER_S3_ACCESS_KEY","")), fp(env.get("HETZNER_S3_SECRET_KEY",""))))
try:
    import boto3
    from botocore.client import Config
    c = boto3.client("s3", endpoint_url=env.get("HETZNER_S3_ENDPOINT"),
                     aws_access_key_id=env.get("HETZNER_S3_ACCESS_KEY"),
                     aws_secret_access_key=env.get("HETZNER_S3_SECRET_KEY"),
                     config=Config(signature_version="s3v4"))
    r = c.list_objects_v2(Bucket=env.get("HETZNER_S3_BUCKET"), MaxKeys=3)
    print("  [OK] PHOTO STORAGE WORKING (%s object(s) reported)" % r.get("KeyCount","?"))
except Exception as e:
    print("  [X]  PHOTO STORAGE BROKEN: %s" % str(e)[:150])

print("\n  === Cloudflare cache purge (CF_CACHE_TOKEN) ===")
tok = env.get("CF_CACHE_TOKEN","")
print("  [--] token: %s" % fp(tok))
try:
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/user/tokens/verify",
                                 headers={"Authorization": "Bearer " + tok})
    print("  [OK] CACHE TOKEN VALID - status '%s'"
          % json.loads(urllib.request.urlopen(req, timeout=20).read().decode())["result"]["status"])
except urllib.error.HTTPError as e:
    print("  [X]  CACHE TOKEN REJECTED: HTTP %s" % e.code)
except Exception as e:
    print("  [?]  %s" % str(e)[:120])

print("\n  === app health ===")
print("  [--] service: %s" % out("systemctl is-active marketsquare"))
print("  [--] /health: %s" % out("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health"))

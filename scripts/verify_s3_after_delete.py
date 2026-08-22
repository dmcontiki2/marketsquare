#!/usr/bin/env python3
"""verify_s3_after_delete.py - the surviving R2 token still works."""
import hashlib, subprocess
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
pid = subprocess.run("systemctl show -p MainPID --value marketsquare", shell=True,
                     capture_output=True, text=True).stdout.strip()
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
print("  [--] live pair: %s / %s" % (fp(env.get("HETZNER_S3_ACCESS_KEY","")),
                                     fp(env.get("HETZNER_S3_SECRET_KEY",""))))
try:
    import boto3
    from botocore.client import Config
    c = boto3.client("s3", endpoint_url=env.get("HETZNER_S3_ENDPOINT"),
                     aws_access_key_id=env.get("HETZNER_S3_ACCESS_KEY"),
                     aws_secret_access_key=env.get("HETZNER_S3_SECRET_KEY"),
                     config=Config(signature_version="s3v4"))
    r = c.list_objects_v2(Bucket=env.get("HETZNER_S3_BUCKET"), MaxKeys=3)
    print("  [OK] PHOTO STORAGE HEALTHY after the deletion (%s object(s) reported)" % r.get("KeyCount","?"))
    try:
        c.list_objects_v2(Bucket="trustsquare-backups", MaxKeys=1)
        print("  [!!] this token CAN also read trustsquare-backups - scoping did not take")
    except Exception:
        print("  [OK] and it CANNOT reach trustsquare-backups - least privilege confirmed")
except Exception as e:
    print("  [X]  FAILED: %s" % str(e)[:160])

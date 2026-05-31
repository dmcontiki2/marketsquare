# storage.py — Hetzner Object Storage (S3-compatible)
# Handles photo upload: receives bytes, uploads to bucket, returns public URL.
#
# Setup required (one-time):
#   1. Create a bucket in Hetzner console (e.g. "marketsquare-media")
#   2. Generate S3 credentials in Hetzner Object Storage settings
#   3. Set environment variables on the server:
#      MS_STORAGE_KEY_ID     — Hetzner access key ID
#      MS_STORAGE_SECRET     — Hetzner secret access key
#      MS_STORAGE_BUCKET     — bucket name (e.g. marketsquare-media)
#      MS_STORAGE_REGION     — e.g. nbg1 (Nuremberg)
#
# Until Hetzner Object Storage is configured, photos are saved to local
# /var/www/marketsquare/media/ and served via nginx. Switch to S3 by
# setting the environment variables above.

import os
import boto3
from botocore.client import Config
import uuid

STORAGE_KEY_ID = os.environ.get("MS_STORAGE_KEY_ID")
STORAGE_SECRET  = os.environ.get("MS_STORAGE_SECRET")
STORAGE_BUCKET  = os.environ.get("MS_STORAGE_BUCKET", "marketsquare-media")
STORAGE_REGION  = os.environ.get("MS_STORAGE_REGION", "nbg1")
STORAGE_ENDPOINT = f"https://{STORAGE_REGION}.your-objectstorage.com"

# Local fallback path (used when S3 credentials not set)
LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"
LOCAL_MEDIA_URL = "https://trustsquare.co/media"

def _s3_available():
    return bool(STORAGE_KEY_ID and STORAGE_SECRET)

def _get_s3():
    return boto3.client(
        "s3",
        endpoint_url=STORAGE_ENDPOINT,
        aws_access_key_id=STORAGE_KEY_ID,
        aws_secret_access_key=STORAGE_SECRET,
        config=Config(signature_version="s3v4"),
        region_name=STORAGE_REGION,
    )

def upload_photo(image_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """
    Upload photo bytes to storage. Returns public URL.
    Falls back to local disk if S3 not configured.
    """
    if _s3_available():
        s3 = _get_s3()
        s3.put_object(
            Bucket=STORAGE_BUCKET,
            Key=f"listings/{filename}",
            Body=image_bytes,
            ContentType=content_type,
            ACL="public-read",
        )
        return f"{STORAGE_ENDPOINT}/{STORAGE_BUCKET}/listings/{filename}"
    else:
        # Local fallback
        os.makedirs(LOCAL_MEDIA_DIR, exist_ok=True)
        path = os.path.join(LOCAL_MEDIA_DIR, filename)
        with open(path, "wb") as f:
            f.write(image_bytes)
        return f"{LOCAL_MEDIA_URL}/{filename}"

def generate_filename(prefix: str = "img", ext: str = "jpg") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"

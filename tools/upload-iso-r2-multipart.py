#!/usr/bin/env python3
"""Resumable multipart upload of the OU Linux ISO to Cloudflare R2.

Usage: PYTHONPATH=<boto-libs> python3 tools/upload-iso-r2-multipart.py [env-file]
Credentials are read from the env file and never printed.
"""
import hashlib
import os
import sys

import boto3
from boto3.s3.transfer import TransferConfig

EXPECT_SHA = "a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779"
KEY = "OU-OS-Akar-Alpha-v36.iso"


def load_env(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main():
    env_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.config/ou-r2.env")
    env = load_env(env_path)
    for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"):
        if not env.get(k):
            raise SystemExit(f"Missing {k} in {env_path}")
    iso = os.environ.get("ISO_PATH", "/home/desktop/OU OS/OU-OS-Akar-Alpha-v36.iso.bak")
    if not os.path.isfile(iso):
        raise SystemExit(f"Cannot read ISO: {iso}")

    print("Verifying local checksum...", flush=True)
    digest = hashlib.sha256()
    with open(iso, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != EXPECT_SHA:
        raise SystemExit(f"Checksum mismatch: {actual}")
    print(f"Checksum OK: {actual}", flush=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    cfg = TransferConfig(
        multipart_threshold=32 * 1024 * 1024,
        multipart_chunksize=16 * 1024 * 1024,
        max_concurrency=12,
        use_threads=True,
    )
    print("Uploading with 12 parallel multipart workers...", flush=True)
    s3.upload_file(
        iso, env["R2_BUCKET"], KEY,
        Config=cfg,
        ExtraArgs={"ContentType": "application/octet-stream"},
    )
    head = s3.head_object(Bucket=env["R2_BUCKET"], Key=KEY)
    size = head["ContentLength"]
    print(f"Upload complete. Remote size: {size}", flush=True)
    if size != 3037724672:
        raise SystemExit("Remote size mismatch")
    url = f"https://{env['R2_BUCKET']}.{env['R2_ACCOUNT_ID']}.r2.dev/{KEY}"
    print(f"ISO_URL={url}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Resumable multipart ISO upload to R2. Reuses completed parts after failures.

Usage: PYTHONPATH=<boto-libs> python3 tools/upload-iso-r2-resumable.py [env-file]
"""
import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.config import Config

EXPECT_SHA = "a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779"
EXPECT_SIZE = 3037724672
KEY = "OU-OS-Akar-Alpha-v36.iso"
PART_SIZE = 5 * 1024 * 1024
WORKERS = 32


def load_env(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
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
    bucket = env["R2_BUCKET"]
    if not os.path.isfile(iso):
        raise SystemExit(f"Cannot read ISO: {iso}")
    if os.path.getsize(iso) != EXPECT_SIZE:
        raise SystemExit("Local ISO size mismatch")

    print("Verifying checksum...", flush=True)
    digest = hashlib.sha256()
    with open(iso, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != EXPECT_SHA:
        raise SystemExit("Checksum mismatch")
    print("Checksum OK", flush=True)

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(
            read_timeout=180,
            connect_timeout=30,
            retries={"max_attempts": 8, "mode": "adaptive"},
        ),
    )

    uploads = s3.list_multipart_uploads(Bucket=bucket, Prefix=KEY).get("Uploads", [])
    if uploads:
        upload_id = uploads[0]["UploadId"]
        print(f"Reusing multipart upload {upload_id[:12]}...", flush=True)
    else:
        upload_id = s3.create_multipart_upload(
            Bucket=bucket, Key=KEY, ContentType="application/octet-stream"
        )["UploadId"]
        print(f"Created multipart upload {upload_id[:12]}...", flush=True)

    done = {}
    marker = None
    while True:
        kwargs = {"Bucket": bucket, "Key": KEY, "UploadId": upload_id}
        if marker:
            kwargs["PartNumberMarker"] = marker
        resp = s3.list_parts(**kwargs)
        for p in resp.get("Parts", []):
            done[p["PartNumber"]] = p["ETag"]
        if not resp.get("IsTruncated"):
            break
        marker = resp.get("NextPartNumberMarker")

    total_parts = (EXPECT_SIZE + PART_SIZE - 1) // PART_SIZE
    missing = [n for n in range(1, total_parts + 1) if n not in done]
    print(f"Parts total={total_parts} done={len(done)} missing={len(missing)}", flush=True)

    def upload_part(n):
        offset = (n - 1) * PART_SIZE
        size = min(PART_SIZE, EXPECT_SIZE - offset)
        for attempt in range(1, 6):
            try:
                with open(iso, "rb") as fh:
                    fh.seek(offset)
                    body = fh.read(size)
                r = s3.upload_part(
                    Bucket=bucket, Key=KEY, UploadId=upload_id,
                    PartNumber=n, Body=body,
                )
                return n, r["ETag"]
            except Exception as exc:
                print(f"part {n} attempt {attempt} failed: {type(exc).__name__}", flush=True)
                time.sleep(2 * attempt)
        raise RuntimeError(f"part {n} failed after 5 attempts")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(upload_part, n): n for n in missing}
        completed = 0
        for fut in as_completed(futures):
            n, etag = fut.result()
            done[n] = etag
            completed += 1
            if completed % 10 == 0:
                print(f"uploaded {completed}/{len(missing)} new parts", flush=True)

    parts = [{"PartNumber": n, "ETag": done[n]} for n in sorted(done)]
    s3.complete_multipart_upload(
        Bucket=bucket, Key=KEY, UploadId=upload_id,
        MultipartUpload={"Parts": parts},
    )
    head = s3.head_object(Bucket=bucket, Key=KEY)
    size = head["ContentLength"]
    print(f"Complete. Remote size: {size}", flush=True)
    if size != EXPECT_SIZE:
        raise SystemExit("Remote size mismatch")
    print(f"ISO_URL=https://pub-2ec95528c38340d6a3d88f97aa7449aa.r2.dev/{KEY}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
# Upload the OU Linux ISO to Cloudflare R2 with the S3-compatible API.
# Usage:  ./tools/upload-iso-r2.sh [path-to-env-file]
#
# The env file must contain (never paste these into chat):
#   R2_ACCOUNT_ID=...
#   R2_ACCESS_KEY_ID=...
#   R2_SECRET_ACCESS_KEY=...
#   R2_BUCKET=ou-linux-iso
# Optional: R2_PUBLIC_BASE=https://iso.yourdomain.com  (custom domain for the bucket)
#
# Create the keys in Cloudflare: R2 > Manage R2 API tokens > Create API token
# with Object Read & Write, scoped to the bucket. Store the env file with
# chmod 600 and keep it out of Git.

set -euo pipefail

ENV_FILE="${1:-$HOME/.config/ou-r2.env}"
ISO="${ISO_PATH:-/home/desktop/OU OS/OU-OS-Akar-Alpha-v36.iso}"
OBJECT="${R2_OBJECT:-OU-OS-Akar-Alpha-v36.iso}"
EXPECT_SHA="${EXPECT_SHA:-a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779}"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "Cannot read credential file: $ENV_FILE" >&2
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

for key in R2_ACCOUNT_ID R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY R2_BUCKET; do
  if [[ -z "${!key:-}" ]]; then
    echo "Missing $key in $ENV_FILE" >&2
    exit 1
  fi
done

if [[ ! -r "$ISO" ]]; then
  echo "Cannot read ISO: $ISO" >&2
  exit 1
fi

echo "Verifying local ISO checksum..."
ACTUAL_SHA="$(sha256sum "$ISO" | awk '{print $1}')"
if [[ "$ACTUAL_SHA" != "$EXPECT_SHA" ]]; then
  echo "Checksum mismatch: $ACTUAL_SHA" >&2
  exit 1
fi
echo "Checksum OK: $ACTUAL_SHA"

ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${R2_BUCKET}/${OBJECT}"
echo "Uploading $(stat -c %s "$ISO") bytes to R2 (this takes several minutes)..."

curl --fail --silent --show-error --retry 2 \
  --aws-sigv4 "aws:amz:auto:s3" \
  --user "${R2_ACCESS_KEY_ID}:${R2_SECRET_ACCESS_KEY}" \
  -X PUT \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$ISO" \
  "$ENDPOINT"

echo "Upload complete. Verifying with a signed range request..."
curl --silent --show-error --fail \
  --aws-sigv4 "aws:amz:auto:s3" \
  --user "${R2_ACCESS_KEY_ID}:${R2_SECRET_ACCESS_KEY}" \
  --range 0-0 -D - -o /dev/null "$ENDPOINT" \
  | grep -iE '^(HTTP/|content-length:|content-range:|etag:)' || true

if [[ -n "${R2_PUBLIC_BASE:-}" ]]; then
  URL="${R2_PUBLIC_BASE%/}/${OBJECT}"
else
  URL="https://${R2_BUCKET}.${R2_ACCOUNT_ID}.r2.dev/${OBJECT}"
fi
echo
echo "ISO_URL=$URL"
echo "Add this to mirrors in site/site.config.js, then push to main:"
echo "  { name: \"Cloudflare R2\", url: \"$URL\", note: \"Direct ISO download\" }"

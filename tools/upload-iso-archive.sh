#!/usr/bin/env bash
# Upload the OU Linux ISO to Internet Archive (free, no credit card).
# Usage:  ./tools/upload-iso-archive.sh [path-to-env-file]
#
# Env file (chmod 600, never commit, never paste in chat):
#   IA_ACCESS_KEY_ID=...
#   IA_SECRET_ACCESS_KEY=...
#   IA_IDENTIFIER=ou-linux-akar-akar-alpha-v36
#
# Keys: https://archive.org/account/s3.php  (free account first)

set -euo pipefail

ENV_FILE="${1:-$HOME/.config/ou-archive.env}"
ISO="${ISO_PATH:-/home/desktop/OU OS/OU-OS-Akar-Alpha-v36.iso}"
REMOTE_NAME="${REMOTE_NAME:-OU-OS-Akar-Alpha-v36.iso}"
EXPECT_SHA="${EXPECT_SHA:-a3d34fec32ca70133a5c45a4b643609118365a268f9a932464554066650cc779}"
IA_LIBS="${IA_LIBS:-$HOME/.local/share/ou-linux-ia-libs}"

if [[ ! -r "$ENV_FILE" ]]; then
  echo "Cannot read credential file: $ENV_FILE" >&2
  exit 1
fi
set -a
source "$ENV_FILE"
set +a

for key in IA_ACCESS_KEY_ID IA_SECRET_ACCESS_KEY IA_IDENTIFIER; do
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

if ! PYTHONPATH="$IA_LIBS" python3 -c 'import internetarchive' 2>/dev/null; then
  echo "Installing the Internet Archive CLI into $IA_LIBS ..."
  python3 -m pip install -q --target "$IA_LIBS" internetarchive
fi

echo "Uploading to archive.org item '$IA_IDENTIFIER' (this takes a while)..."
PYTHONPATH="$IA_LIBS" python3 -m internetarchive.cli.ia upload \
  "$IA_IDENTIFIER" "$ISO" \
  --remote-name="$REMOTE_NAME" \
  --metadata="mediatype:data" \
  --metadata="collection:open_source_software" \
  --metadata="title:OU Linux (Orang Utan) - Akar Alpha v36 ISO" \
  --metadata="description:Debian 13 based OU Linux Akar Alpha v36 live ISO. SHA-256: $ACTUAL_SHA" \
  --no-derive --verify --checksum --retries=5

URL="https://archive.org/download/${IA_IDENTIFIER}/${REMOTE_NAME}"
echo
echo "ISO_URL=$URL"
echo "Add this to mirrors in site/site.config.js, then push to main:"
echo "  { name: \"Internet Archive\", url: \"$URL\", note: \"Direct ISO download\" }"

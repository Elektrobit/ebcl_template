#!/bin/bash
set -euo pipefail
echo "=============================="
echo " 🛠️ patch the initrd"
echo "=============================="

if [ $# -ne 3 ]; then
    echo "Usage: $0 <initrd.img> <new-init> <output-initrd.img>"
    exit 1
fi

INITRD_IN="$1"
NEW_INIT="$2"
INITRD_OUT="$3"

INITRD_IN="$(readlink -f "$INITRD_IN")"
NEW_INIT="$(readlink -f "$NEW_INIT")"
INITRD_OUT="$(readlink -f "$INITRD_OUT")"

WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

echo "📦 Unpacking $INITRD_IN into $WORKDIR..."
pushd "$WORKDIR" > /dev/null
cpio -idmv < "$INITRD_IN"

echo "📝 Replacing /init with $NEW_INIT..."
cp "$NEW_INIT" init
chmod +x init

#echo "📦 Repacking into $INITRD_OUT..."
find . | cpio -o -H newc > "$INITRD_OUT"

popd > /dev/null
echo "✅ Done. New initrd written to $INITRD_OUT"

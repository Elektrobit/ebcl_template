#!/bin/sh
set -e
echo "=============================="
echo "🛠️ set up wrapped key partition"
echo "=============================="

# create 1MB image file
sudo dd if=/dev/zero of=build/wrapped_key.img bs=1M count=1 status=progress

# format ext4 filesystem
sudo mkfs.ext4 -F build/wrapped_key.img

echo "✅ wrapped_key.img created"
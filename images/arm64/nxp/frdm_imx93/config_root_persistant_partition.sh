#!/bin/sh
set -e
echo "set up persistent partition"
pwd
# ensure build dir exists
mkdir -p build

# create 256MB image file
sudo dd if=/dev/zero of=build/data.img bs=1M count=256 status=progress

# format ext4 filesystem
sudo mkfs.ext4 -F build/data.img

# mount, create dirs and seed if you like
mkdir -p /tmp/_data_mnt
sudo mount -o loop build/data.img /tmp/_data_mnt

# create overlay dirs and any persistent folders
sudo mkdir -p /tmp/_data_mnt/overlay/upper
sudo mkdir -p /tmp/_data_mnt/overlay/work
sudo mkdir -p /tmp/_data_mnt/var/log          # example: persistent logs
sudo mkdir -p /tmp/_data_mnt/var/lib/dpkg /tmp/_data_mnt/var/lib/apt/lists /tmp/_data_mnt/var/cache/apt/archives

# set ownership / perms as needed (root:root)
sudo chown -R root:root /tmp/_data_mnt
sudo chmod 0755 /tmp/_data_mnt

sudo umount /tmp/_data_mnt
rmdir /tmp/_data_mnt

echo "✅ data.img created"
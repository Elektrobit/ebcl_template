#!/bin/bash

set -e

IMAGE=$1
DEVICE=$(losetup -f)

[ -z "${IMAGE}" ] && echo "Usage $0 /path/to/image" && exit 1

echo "Selected device is ${DEVICE}"

sudo losetup ${DEVICE} -P ${IMAGE}


ROOTFS=$(mktemp -d /tmp/config_grub.XXXXXX)
mkdir -p ${ROOTFS}

echo "Mount OS partition"
sudo mount ${DEVICE}p2 ${ROOTFS}

echo "Mount EFI partition"
sudo mkdir -p ${ROOTFS}/efi
sudo mount ${DEVICE}p1 ${ROOTFS}/efi

echo "Mount filesystems"
for i in dev dev/pts proc sys tmp
do
    sudo mount -o bind /${i} ${ROOTFS}/${i}
done

echo "Entering chroot to configure Grub"
cat << EOF | sudo chroot ${ROOTFS}
  set -e

  # setup grub on the efi partition
  export DEBIAN_FRONTEND=noninteractive
  grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB --removable
  update-grub

EOF

echo "Unmount filesystems"
for i in dev/pts dev proc sys tmp efi
do
    sudo umount ${ROOTFS}/${i}
done

sudo umount ${ROOTFS}
rmdir ${ROOTFS}

sudo losetup -d ${DEVICE}

echo "Done"


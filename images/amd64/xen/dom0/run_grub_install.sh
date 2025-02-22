#!/bin/bash

IMAGE="build/image.raw"
DEVICE=$(losetup -f)

echo "Selected device is ${DEVICE}"

sudo losetup ${DEVICE} -P ${IMAGE}

ROOTFS=$(mktemp -d /tmp/edit_domu.XXXXXX)

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

sudo cp -f /etc/resolv.conf ${ROOTFS}/etc/resolv.conf
sudo cp -f /etc/gai.conf ${ROOTFS}/etc/gai.conf
sudo cp -f /proc/mounts ${ROOTFS}/etc/mtab

echo "Entering chroot..."

cat << EOF | sudo chroot ${ROOTFS}
    set -e

    export DEBIAN_FRONTEND="noninteractive"
    export TZ="Etc/UTC"

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

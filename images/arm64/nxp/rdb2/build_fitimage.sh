#!/bin/sh

set -e

#=======================================
# Rename kernel
#---------------------------------------
echo "Rename kernel..."
if [ ! -f /boot/vmlinuz ]; then
    mv /boot/vmlinuz-* /boot/Image
fi
mv /boot/vmlinuz /boot/Image
mv /boot/initrd.img /boot/initrd

#=======================================
# Get NXP S32G device tree
#---------------------------------------
cp /lib/firmware/*/device-tree/freescale/s32g274a-rdb2.dtb \
    /boot/fsl-s32g274a-rdb2.dtb

#=======================================
# Get NXP S32G ATF (secure boot image)
#---------------------------------------
cp /usr/lib/arm-trusted-firmware-s32/s32g274ardb2/fip.s32 \
    /boot/fip.s32

#=======================================
# Create fit image
#---------------------------------------
cd /boot

ls -lah bootargs-overlay.dts

dtc -I dts -O dtb -o bootargs-overlay.dtbo bootargs-overlay.dts
ls -lah bootargs-overlay.dtbo

fdtoverlay -i fsl-s32g274a-rdb2.dtb -o target.dtb bootargs-overlay.dtbo
ls -lah bootargs-overlay.dtbo

ls -lah bootargs.its

mkimage -f bootargs.its fitimage
ls -lah fitimage

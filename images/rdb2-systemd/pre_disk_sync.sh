#!/bin/dash
  
set -ex

#==================================
# Allow suid tools with sudo again
#----------------------------------
chmod u+s /usr/bin/sudo

#=======================================
# Rename kernel
#---------------------------------------
mv /boot/initrd.img-* /boot/initrd
mv /boot/vmlinuz-* boot/Image

#=======================================
# Cleanup unused
#---------------------------------------
rm /boot/System.map-*
rm /boot/config-*

#=======================================
# Create stub resolv.conf link
#---------------------------------------
# kiwi cleanup has dropped stale resolv.conf
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

#=======================================
# Get NXP S32G device tree
#---------------------------------------
cp /lib/firmware/*/device-tree/freescale/s32g274a-rdb2.dtb \
    /boot/fsl-s32g274a-rdb2.dtb

#=======================================
# Get NXP S32G ATF (secure boot image)
#---------------------------------------
cp /usr/lib/arm-trusted-firmware-s32g/s32g274ardb2/fip.s32 \
    /boot/fip.s32

#=======================================
# Create fit image
#---------------------------------------
(
    cd /boot
    dtc -I dts -O dtb -o bootargs-overlay.dtbo bootargs-overlay.dts
    fdtoverlay -i fsl-s32g274a-rdb2.dtb -o target.dtb bootargs-overlay.dtbo
    mkimage -f bootargs.its fitImage
)
rm -f /boot/initrd
rm -f /boot/Image
rm -f /boot/System.map*
rm -f /boot/fsl-s32g274a-rdb2.dtb
rm -f /boot/target.dtb

#=======================================
# Delete symlinks from /boot
#---------------------------------------
# symlinks not supported on fat and uboot is configured to do
# fatboot which is the reason why the boot filesystem is set
# to fat32
for file in /boot/*;do
    if [ -L ${file} ];then
        rm -f ${file}
    fi
done

chown -R root:root /boot

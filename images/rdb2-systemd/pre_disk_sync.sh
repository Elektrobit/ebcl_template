#!/bin/dash
  
set -ex

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

#=======================================
# Rename kernel
#---------------------------------------
mv /boot/initrd.img* /boot/initrd
mv /boot/vmlinuz-* boot/Image

#=======================================
# Cleanup unused
#---------------------------------------
rm /boot/System.map-*
rm /boot/config-*

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
# Create default hosts file
#---------------------------------------
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

#=======================================
# Create stub resolv.conf link
#---------------------------------------
# kiwi cleanup has dropped stale resolv.conf
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

#=======================================
# Relink /var/lib/dhcp to /run (rw)
#---------------------------------------
(cd /var/lib && rm -rf dhcp && ln -s /run dhcp)

#=======================================
# Update license data
#---------------------------------------
for p in $(dpkg --list | grep ^ii | cut -f3 -d" ");do
    grep -m 1 "ii  $p" /licenses || true
done > /licenses.new
mv /licenses.new /licenses

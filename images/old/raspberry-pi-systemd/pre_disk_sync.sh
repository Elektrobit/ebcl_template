#!/bin/dash

set -ex

#==================================
# Allow suid tools with sudo again
#----------------------------------
chmod u+s /usr/bin/sudo

#=======================================
# Create /etc/hosts
#---------------------------------------
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

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

#=======================================
# Set localtime of image
#---------------------------------------
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

#=======================================
# Create stub resolv.conf link
#---------------------------------------
# kiwi cleanup has dropped stale resolv.conf
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# copy Raspberry Pi boot data to "EFI" part...
#==========================================
# copy firmware
#------------------------------------------
cp -a /usr/lib/linux-firmware-raspi/* /boot/efi

#==========================================
# copy device tree's
#------------------------------------------
cp -a /usr/lib/firmware/*-raspi/device-tree/overlays /boot/efi/
cp -a /usr/lib/firmware/*-raspi/device-tree/broadcom/* /boot/efi/

#==========================================
# copy initrd and kernel
#------------------------------------------
cp /boot/vmlinuz-*-raspi /boot/efi/vmlinuz

#==========================================
# copy u-boot
#------------------------------------------
cp /usr/lib/u-boot/rpi_3/u-boot.bin /boot/efi/uboot_rpi_3.bin
cp /usr/lib/u-boot/rpi_4/u-boot.bin /boot/efi/uboot_rpi_4.bin
cp /usr/lib/u-boot/rpi_arm64/u-boot.bin /boot/efi/uboot_rpi_arm64.bin

#==========================================
# create u-boot loader config
#------------------------------------------
echo "console=serial0,115200 dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rd.kiwi.debug rootfstype=ext4 rootwait fixrtc" > /boot/efi/cmdline.txt

mkimage -A arm64 -O linux -T script -C none -d /boot/efi/boot.cmd \
    /boot/efi/boot.scr

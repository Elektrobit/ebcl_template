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
# Enable reboot and poweroff commands
# Now will call crinit
# Delete data associated with these
# commands to avoid confusion
#---------------------------------------

ln -sf /sbin/crinit-shutdown/reboot /sbin/reboot
ln -sf /sbin/crinit-shutdown/poweroff /sbin/poweroff

rm -f \
    /sbin/telinit \
    /sbin/shutdown \
    /sbin/halt \
    /sbin/runlevel \
    /usr/share/man/man1/init.1 \
    /usr/share/man/man8/telinit.8 \
    /usr/share/man/man8/runlevel.8 \
    /usr/share/man/man8/shutdown.8 \
    /usr/share/man/man8/poweroff.8 \
    /usr/share/man/man8/reboot.8 \
    /usr/share/man/man8/halt.8

#=======================================
# Kiwi dropes /etc/resolv.conf on
# cleanup -> relink
#---------------------------------------
ln -sf /var/run/resolv.conf.netifd /etc/resolv.conf

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
    ls
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

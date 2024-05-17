#!/bin/bash

#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

#======================================
# Create license information
#--------------------------------------
/usr/local/bin/dpkg-licenses/dpkg-licenses > /licenses

#==================================
# Turn grub-mkconfig into a noop
#----------------------------------
# We provide our own static version of the grub config
cp /bin/true /usr/sbin/grub-mkconfig

#==================================
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox

#=======================================
# Enable dhcp network service
#---------------------------------------
ln -sf /etc/crinit/crinit.net.d/dhcp.crinit \
    /etc/crinit/crinit.d/network.crinit

#======================================
# Install firmware
#--------------------------------------
dpkg -i /var/tmp/firmware/linux-firmware-raspi_6-0ubuntu3_arm64.deb
dpkg -i /var/tmp/firmware/linux-firmware-raspi2_6-0ubuntu3_arm64.deb

#=======================================
# Setup system timezone
#---------------------------------------
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/${kiwi_timezone} /etc/localtime

#======================================
# Create license information
#--------------------------------------
/usr/local/bin/dpkg-licenses/dpkg-licenses > /licenses

#======================================
# Set hostname
#--------------------------------------
echo "raspberrypi4crinit" > /etc/hostname

# Work around HDMI connector bug and network issues
# No HDMI hotplug available
# Prevent too many page allocations (bsc#1012449)
cat > /etc/modprobe.d/50-rpi3.conf <<-EOF
    options drm_kms_helper poll=0
    options smsc95xx turbo_mode=N
EOF

# Avoid running out of DMA pages for smsc95xx (bsc#1012449)
cat > /usr/lib/sysctl.d/50-rpi3.conf <<-EOF
    vm.min_free_kbytes = 2048
EOF

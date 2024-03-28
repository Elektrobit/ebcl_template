#!/bin/bash

#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

#======================================
# Setup default target, multi-user
#--------------------------------------
baseSetRunlevel 3

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

#==================================
# Mask/Disable services
#----------------------------------
for service in \
    apt-daily.service \
    apt-daily.timer \
    apt-daily-upgrade.service \
    apt-daily-upgrade.timer \
    grub-common.service \
    grub-initrd-fallback.service
do
    systemctl mask "${service}"
done

#======================================
# Activate services
#--------------------------------------
baseInsertService systemd-networkd
baseInsertService systemd-resolved
baseInsertService systemd-timesyncd

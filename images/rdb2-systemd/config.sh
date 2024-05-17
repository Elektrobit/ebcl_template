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
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox

#==================================
# Delete initrd from kernel
#----------------------------------
# The kernel package provides some arbitrary initrd
rm -f /boot/initrd*

#==================================
# Create init symlink
#----------------------------------
pushd /usr/sbin
ln -s ../lib/systemd/systemd init
popd

#==================================
# Mask/Disable services
#----------------------------------
for service in \
    apt-daily.service \
    apt-daily.timer \
    apt-daily-upgrade.service \
    apt-daily-upgrade.timer \
    dracut-shutdown.service
do
    systemctl mask "${service}"
done

#======================================
# Activate services
#--------------------------------------
baseInsertService ssh
baseInsertService systemd-networkd
baseInsertService systemd-resolved
baseInsertService systemd-timesyncd

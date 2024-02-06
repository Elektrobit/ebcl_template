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
# This data gets updated in images.sh when the
# strip down of the system in terms of packages
# has been completed. At this time only a subset
# of the information produced now will be relevant
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
# Delete data not needed or wanted
#----------------------------------
rm -rf /var/backups
rm -rf /usr/share/man
rm -rf /usr/share/doc/*
rm -rf /usr/lib/x86_64-linux-gnu/gconv

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

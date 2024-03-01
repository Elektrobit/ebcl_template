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

#==================================
# Create RW partition mountpoint
#----------------------------------
mkdir /containers
#==================================
# Turn grub-mkconfig into a noop
#----------------------------------
cp /bin/true /usr/sbin/grub-mkconfig
#==================================
# Allow suid tools with busybox
#----------------------------------
chmod oug+s /usr/bin/busybox

#==================================
# Delete initrd from kernel
#----------------------------------
# The kernel package provides some arbitrary initrd
rm -f /boot/initrd*
rm -f /boot/vmlinuz.old

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
# Add systemd unit
#----------------------------------
ln -sf /usr/share/systemd/tmp.mount /etc/systemd/system/tmp.mount

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
baseInsertService ssh
baseInsertService systemd-networkd
baseInsertService systemd-resolved

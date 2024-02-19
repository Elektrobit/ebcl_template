#!/bin/bash
#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

#==================================
# Turn grub-mkconfig into a noop
#----------------------------------
cp /bin/true /usr/sbin/grub-mkconfig
#==================================
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox

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

ln -sf /etc/systemd/system/data.mount /etc/systemd/system/multi-user.target.wants/data.mount
ln -sf /lib/systemd/system/systemd-networkd.service /etc/systemd/system/multi-user.target.wants/systemd-networkd.service

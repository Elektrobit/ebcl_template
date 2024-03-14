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
rm -rf /etc/systemd
rm -rf /usr/lib/systemd
rm -rf /var/lib/systemd
rm -rf /usr/bin/systemd-hwdb
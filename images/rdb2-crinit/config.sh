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
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox

#==================================
# Delete initrd from kernel
#----------------------------------
# The kernel package provides some arbitrary initrd
rm -f /boot/initrd*


#=======================================
# Enable dhcp network service
#---------------------------------------
ln -sf /etc/crinit/crinit.net.d/dhcp.crinit \
    /etc/crinit/crinit.d/network.crinit

#=======================================
# Setup system timezone
#---------------------------------------
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/${kiwi_timezone} /etc/localtime

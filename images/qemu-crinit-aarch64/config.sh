#!/bin/bash
#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

#======================================
# Create license information
#--------------------------------------
# This data gets updated in images.sh when the
# strip down of the system in terms of packages
# has been completed. At this time only a subset
# of the information produced now will be relevant
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

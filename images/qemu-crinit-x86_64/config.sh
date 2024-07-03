#!/bin/bash

#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

#==================================
# Turn grub-mkconfig into a noop
#----------------------------------
# We provide our own static version of the grub config
cp /bin/true /usr/sbin/grub-mkconfig

#==================================
# Allow suid tools with busybox
#----------------------------------
chmod u+s /usr/bin/busybox

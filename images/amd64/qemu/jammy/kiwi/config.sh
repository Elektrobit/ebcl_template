#!/bin/bash

#======================================
# Functions...
#--------------------------------------
test -f /.kconfig && . /.kconfig

set -ex

echo "Running config.sh..."

echo "Creating symlink to systemd..."
ln -sf /usr/lib/systemd/systemd /sbin/init

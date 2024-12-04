#!/bin/sh

# Ensure init is executable
chmod +x ./sbin/init

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Enable DNS
rm -f ./etc/resolv.conf || true
ln -sf /var/run/resolv.conf.netifd ./etc/resolv.conf

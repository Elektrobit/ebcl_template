#!/bin/sh

chmod +x ./sbin/*

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Create a hostname file
echo "sbc" > ./etc/hostname

# Link DHCP network config
cd ./etc/crinit/crinit.d
ln -s ../crinit.net.d/dhcp.crinit

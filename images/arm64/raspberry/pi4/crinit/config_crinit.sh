#!/bin/sh

# Link crinit as init
chmod +x /sbin/init

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Create a hostname file
echo "ebcl-rdb2-network" > ./etc/hostname

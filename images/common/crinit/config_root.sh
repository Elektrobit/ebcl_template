#!/bin/sh

# Ensure scripts are executable
chmod +x ./sbin/*

# Link crinit as init
rm -f /sbin/init
ln -s /usr/bin/crinit /sbin/init

# Set localtime of image
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

# Ensure netifd is used for DNS
ln -sf /var/run/resolv.conf.netifd /etc/resolv.conf

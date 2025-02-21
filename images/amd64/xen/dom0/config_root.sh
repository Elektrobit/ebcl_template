#!/bin/sh

# Link systemd as init
rm -f ./sbin/init
ln -sf /usr/lib/systemd/systemd ./sbin/init

# Link resolv.conf from systemd-resolved
rm -f ./etc/resolv.conf
ln -sf /run/systemd/resolve/stub-resolv.conf ./etc/resolv.conf

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

# Start ebcl VM
systemctl enable start-ebcl-1.service

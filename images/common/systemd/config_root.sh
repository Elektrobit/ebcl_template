#!/bin/sh

# Link systemd as init
ln -s /usr/lib/systemd/systemd /sbin/init

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

# Ensure netifd is used for DNS
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

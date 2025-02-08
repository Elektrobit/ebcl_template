#!/bin/sh

# Link systemd as init
rm -rf ./sbin/init
ln -s /usr/lib/systemd/systemd ./sbin/init

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd
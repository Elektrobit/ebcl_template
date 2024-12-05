#!/bin/sh

# Link systemd as init
ln -sf /usr/lib/systemd/systemd ./sbin/init

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd
systemctl enable weston

systemctl disable systemd-networkd-wait-online
systemctl disable snapd.seeded
systemctl disable codemeter
systemctl disable snapd
systemctl disable ModemManager
systemctl disable packagekit
systemctl disable bluetooth
systemctl disable wpa_supplicant.service
systemctl disable networkd-dispatcher.service
systemctl disable systemd-random-seed

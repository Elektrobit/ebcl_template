#!/bin/sh

# Link systemd as init
rm -f ./sbin/init
ln -sf /usr/lib/systemd/systemd ./sbin/init

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd
systemctl enable symlink-resolvconf

# Setup locale
RUN export LC_ALL=en_US.UTF-8 && \
    export LANG=en_US.UTF-8 && \
    locale-gen en_US.UTF-8

ls -lah /dev/*

# Install AMD stuff
apt update
cd /amd
chmod +x install_debs.sh

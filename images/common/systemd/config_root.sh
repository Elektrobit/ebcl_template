#!/bin/sh

# Link systemd as init
rm -f /sbin/init
ln -s /usr/lib/systemd/systemd /sbin/init

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

# Disable binfmt - doesn't work on QEMU
systemctl disable proc-sys-fs-binfmt_misc.automount
systemctl disable proc-sys-fs-binfmt_misc.mount
systemctl disable systemd-binfmt.service
systemctl mask proc-sys-fs-binfmt_misc.automount
systemctl mask proc-sys-fs-binfmt_misc.mount
systemctl mask systemd-binfmt.service

# Ensure netifd is used for DNS
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

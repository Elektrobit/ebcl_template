#!/bin/sh

# Link systemd as init
ln -s /usr/lib/systemd/systemd /sbin/init

# Create a hostname file
echo "sbc_systemd" > ./etc/hostname

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Fix access rights of /etc
chmod 755 /etc
chmod -R 755 /etc/systemd
chmod 600 /etc/ssh/ssh_host_ecdsa_key

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

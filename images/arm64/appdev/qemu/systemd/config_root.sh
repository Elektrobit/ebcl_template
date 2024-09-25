#!/bin/sh

# Link systemd as init
ln -s /usr/lib/systemd/systemd /sbin/init

# Create a hostname file
echo "appdev" > ./etc/hostname

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

#!/bin/sh

# Ensure Init is executable
chmod +x /usr/sbin/init

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost ebclai64
::1             localhost ebclai64 ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Enable DNS
rm -f ./etc/resolv.conf || true
ln -sf /var/run/resolv.conf.netifd ./etc/resolv.conf

# Create a fake machine-id
echo "04711" > ./etc/machine-id

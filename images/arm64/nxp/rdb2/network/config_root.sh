#!/bin/sh

# Ensure init is executable
chmod +x ./sbin/*

# Ensure modprobe.sh is executable
chmod +x ./usr/sbin/load_modules.sh
chmod +x ./usr/sbin/ntp_time.sh

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Create a hostname file
echo "ebcl-rdb2-network" > ./etc/hostname

# Create /etc/hosts
cat > ./etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Enable DNS
rm -f ./etc/resolv.conf || true
ln -sf /var/run/resolv.conf.netifd ./etc/resolv.conf

#!/bin/sh

chmod +x ./sbin/*

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Create a hostname file
echo "sbc" > ./etc/hostname

# Link DHCP network config
cd ./etc/crinit/crinit.d
ln -s ../crinit.net.d/static.crinit

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

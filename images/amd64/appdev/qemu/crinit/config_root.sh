#!/bin/sh

# Ensure init is executable
chmod +x ./sbin/*

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# allow name resolution (needed for apt update)
touch /etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

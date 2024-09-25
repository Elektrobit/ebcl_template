#!/bin/sh

# Ensure init ie executable
chmod +x ./sbin/*

# Create a fake machine-id
echo "04711" > ./etc/machine-id

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

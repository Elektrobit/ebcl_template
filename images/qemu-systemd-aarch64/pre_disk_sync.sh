#!/bin/dash

set -ex

#==================================
# Allow suid tools with sudo again
#----------------------------------
chmod u+s /usr/bin/sudo

#=======================================
# Create /etc/hosts
#---------------------------------------
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

#=======================================
# Create stub resolv.conf link
#---------------------------------------
# kiwi cleanup has dropped stale resolv.conf
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

#=======================================
# Update license data
#---------------------------------------
for p in $(dpkg --list | grep ^ii | cut -f3 -d" ");do
    grep -m 1 "ii  $p" /licenses || true
done > /licenses.new
mv /licenses.new /licenses

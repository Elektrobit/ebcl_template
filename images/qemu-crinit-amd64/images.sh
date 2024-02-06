#!/bin/dash

set -ex

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
# Update license data
#---------------------------------------
for p in $(dpkg --list | grep ^ii | cut -f3 -d" ");do
    grep -m 1 "ii  $p" /licenses || true
done > /licenses.new
mv /licenses.new /licenses

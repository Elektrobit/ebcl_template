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
# Relink /var/lib/dhcp to /run (rw)
#---------------------------------------
(cd /var/lib && rm -rf dhcp && ln -s /run dhcp)

#=======================================
# Update license data
#---------------------------------------
for p in $(dpkg --list | grep ^ii | cut -f3 -d" ");do
    grep -m 1 "ii  $p" /licenses || true
done > /licenses.new
mv /licenses.new /licenses

#=======================================
# Set localtime of image
#---------------------------------------
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

#=======================================
# Enable reboot and poweroff commands
# Now will call crinit
# Delete data associated with these
# commands to avoid confusion
#---------------------------------------

ln -sf /sbin/crinit-shutdown/reboot /sbin/reboot
ln -sf /sbin/crinit-shutdown/poweroff /sbin/poweroff

rm -f \
    /sbin/telinit \
    /sbin/shutdown \
    /sbin/halt \
    /sbin/runlevel \
    /usr/share/man/man1/init.1 \
    /usr/share/man/man8/telinit.8 \
    /usr/share/man/man8/runlevel.8 \
    /usr/share/man/man8/shutdown.8 \
    /usr/share/man/man8/poweroff.8 \
    /usr/share/man/man8/reboot.8 \
    /usr/share/man/man8/halt.8

#=======================================
# Kiwi dropes /etc/resolv.conf on
# cleanup -> relink
#---------------------------------------
ln -sf /var/run/resolv.conf.netifd /etc/resolv.conf

#=======================================
# Enable dhcp network service
#---------------------------------------
ln -sf /etc/crinit/crinit.net.d/dhcp.crinit \
    /etc/crinit/crinit.d/network.crinit

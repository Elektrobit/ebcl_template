#!/bin/dash

set -ex

#=======================================
# Move coreutils to busybox
#---------------------------------------
# remove coreutils and others for which a busybox
# replacement exists
dpkg \
    --remove --force-remove-reinstreq \
    --force-remove-essential --force-depends \
coreutils tar

for file in $(busybox --list);do
    if [ "${file}" = "busybox" ] || \
       [ "${file}" = "init" ] || \
       [ "${file}" = "reboot" ] || \
       [ "${file}" = "poweroff" ]
    then
        # unwanted from busybox
        continue
    fi
    busybox rm -f /bin/$file
    busybox ln /usr/bin/busybox /bin/$file || true
done

#==================================
# Allow suid tools with sudo again
#----------------------------------
chmod u+s /usr/bin/sudo

#=======================================
# Create /etc/hosts
#---------------------------------------
cat >/etc/hosts <<- EOF
127.0.0.1       localhost vmtimetracker
::1             localhost vmtimetracker ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

#=======================================
# Relink /var/lib/dhcp to /run (rw)
#---------------------------------------
(cd /var/lib && rm -rf dhcp && ln -s /run dhcp)

#=======================================
# Relink /var/lib/cni to /run (rw)
#---------------------------------------
(cd /var/lib && rm -rf cni && ln -s /run cni)


# Podman rootless operation requires
# the directories below as writeable
# there is no working config that
# is able to change those directories
# so a relinking is needed here
#=======================================
# Relink /home/ebcl/.config to /data/ebcl (rw)
#---------------------------------------
mkdir /data/ebcl
(cd /home/ebcl && rm -rf .config && ln -s /data/ebcl .config)

#=======================================
# Relink /home/ebcl/.cache to /data/ebcl/.cache (rw)
#---------------------------------------
(cd /home/ebcl && rm -rf .cache && ln -s /data/ebcl .cache)

#=======================================
# Relink /home/ebcl/.local to /data/ebcl/.local (rw)
#---------------------------------------
mkdir /home/ebcl/.local
mkdir /data/ebcl/.local
(cd /home/ebcl/.local && rm -rf share && ln -s /data/ebcl/.local share)

#=======================================
# create so that that tmpfs can be 
# mounted here later
#---------------------------------------
mkdir -p /var/cache

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
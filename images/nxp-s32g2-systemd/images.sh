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

#=======================================
# Create /etc/hosts
#---------------------------------------
cat >/etc/hosts <<- EOF
127.0.0.1       localhost vm-registry
::1             localhost vm-registry ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Kiwi dropped resolv.conf on cleanup
ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf

#================================================
# Add link to enable additional systemd service
#------------------------------------------------
ln -sf /etc/systemd/system/mosquitto-container.service \
    /etc/systemd/system/multi-user.target.wants/mosquitto-container.service


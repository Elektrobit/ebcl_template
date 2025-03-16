#!/bin/sh

# Link systemd as init
ln -sf /usr/lib/systemd/systemd /sbin/init

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# allow name resolution (needed for apt update)
ln -s /usr/lib/systemd/resolv.conf /etc/resolv.conf

#configure eth0
cat >/etc/systemd/network/20-wired.network <<- EOF
[Match]
Name=eth0

[Link]
RequiredForOnline=routable

[Network]
DHCP=yes
EOF

#configure wlan0
cat >/lib/systemd/network/51-wireless.network <<- EOF
[Match]
Name=wlan0

[Network]
DHCP=ipv4
EOF

#if you want to encrypt the password do "wpa_passphrase "SSID" "PASS" >> /etc/wpa_supplicant/wpa_supplicant-wlan0.conf" on target and reboot or:
#systemctl restart systemd-networkd.service
#systemctl restart wpa_supplicant@wlan0.service

cat >/etc/wpa_supplicant/wpa_supplicant-wlan0.conf <<- EOF
ctrl_interface=/var/run/wpa_supplicant
eapol_version=1
ap_scan=1
fast_reauth=1

network={
        ssid="SSID_OF_NETWORK"
        #psk="PASSWORD_OF_NETWORK"
        psk=2debb6d6c0b8299fca81af914ac463883720bbd9b7624cfe678566b8208aa28e
}
EOF



# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd
systemctl enable wpa_supplicant@wlan0.service

echo "/dev/mmcblk1p2  /  ext4  noatime,errors=remount-ro  0  1" > /etc/fstab
#echo "/dev/mmcblk1p1  /boot/firmware vfat user,uid=1000,gid=1000,defaults 0 2" >> /etc/fstab
#echo "debugfs  /sys/kernel/debug  debugfs  mode=755,uid=root,gid=gpio,defaults  0  0" >> /etc/fstab

#create eb user
useradd -m -d /home/eb -s /bin/bash "eb"
echo "eb:elektrobit" | chpasswd

#prevent root login on console (TTY)
echo "-:root:ALL" >> /etc/security/access.conf
echo "auth required pam_access.so" >> /etc/pam.d/login

#add info that the image is for security demonstaration
echo "EB corbos Linux – built on Ubuntu" >> /etc/issue
echo "Secured by security requirements meeting the industry regulations" >> /etc/issue


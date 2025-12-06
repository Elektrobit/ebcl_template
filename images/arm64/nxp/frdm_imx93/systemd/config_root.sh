#!/bin/sh
echo "configure rootfs"

#cp /usr/lib/aarch64-linux-gnu/ld-linux-aarch64.so.1 /lib/ld-linux-aarch64.so.1

# Link systemd as init
if [ ! -e "./sbin/init"  ]; then
    ln -s /usr/lib/systemd/systemd ./sbin/init
else 
    echo "sbin/init already exists."
    ls -lah ./sbin/init
fi

# Create /etc/hosts
cat >/etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# allow name resolution (needed for apt update)
ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf

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
#cat >/lib/systemd/network/51-wireless.network <<- EOF
#[Match]
#Name=wlan0
#
#[Network]
#DHCP=ipv4
#EOF

#if you want to encrypt the password do "wpa_passphrase "SSID" "PASS" >> /etc/wpa_supplicant/wpa_supplicant-wlan0.conf" on target and reboot or:
#systemctl restart systemd-networkd.service
#systemctl restart wpa_supplicant@wlan0.service

#cat >/etc/wpa_supplicant/wpa_supplicant-wlan0.conf <<- EOF
#ctrl_interface=/var/run/wpa_supplicant
#eapol_version=1
#ap_scan=1
#fast_reauth=1
#
#network={
#        ssid="SSID_OF_NETWORK"
#        #psk="PASSWORD_OF_NETWORK"
#        psk=2debb6d6c0b8299fca81af914ac463883720bbd9b7624cfe678566b8208aa28e
#}
#EOF

# Activate services
systemctl enable systemd-networkd
systemctl enable systemd-resolved
systemctl enable systemd-timesyncd

systemctl daemon-reload
systemctl enable --now tee-supplicant.service
systemctl status tee-supplicant.service

#systemctl enable wpa_supplicant@wlan0.service
systemctl enable tee-supplicant.service
systemctl restart tee-supplicant.service

#create eb user
#useradd -m -d /home/eb -s /bin/bash "eb"
#echo "eb:elektrobit" | chpasswd

#prevent root login on console (TTY)
#echo "-:root:ALL" >> /etc/security/access.conf
#echo "auth required pam_access.so" >> /etc/pam.d/login

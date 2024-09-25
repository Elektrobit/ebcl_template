#!/bin/sh

# Create a hostname file
echo "ebcl-pi4" > ./etc/hostname

# Create /etc/hosts
cat > ./etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
EOF

# Copy Raspi device trees
cp ./usr/lib/firmware/5.15.0-1060-raspi/device-tree/broadcom/bcm2711*.dtb ./boot/
# Copy device tree overlays
cp -R ./usr/lib/firmware/5.15.0-1060-raspi/device-tree/overlays ./boot/
# Copy raspi firmware
cp ./usr/lib/linux-firmware-raspi/* ./boot/

# Copy kernel as the expected name
cp ./boot/vmlinuz-* ./boot/kernel8.img || true
# Copy initrd as the expected name
cp ./boot/initrd.img-* ./boot/initramfs8 || true

# Delete the symlinks
rm ./boot/vmlinuz || true
rm ./boot/initrd.img || true

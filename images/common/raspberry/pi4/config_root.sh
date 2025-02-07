#!/bin/sh

ls -lah ./usr/lib/firmware/*
# Copy Raspi device trees
cp ./usr/lib/firmware/*-raspi/device-tree/broadcom/bcm2711*.dtb ./boot/
# Copy device tree overlays
cp -R ./usr/lib/firmware/*-raspi/device-tree/overlays ./boot/
# Copy raspi firmware
cp ./usr/lib/linux-firmware-raspi/* ./boot/

# Copy kernel as the expected name
cp ./boot/vmlinuz-* ./boot/kernel8.img || true
# Copy initrd as the expected name
cp ./boot/initrd.img-* ./boot/initramfs8 || true

# Delete the symlinks
rm ./boot/vmlinuz || true
rm ./boot/initrd.img || true

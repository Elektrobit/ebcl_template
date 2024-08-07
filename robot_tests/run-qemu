#!/bin/bash

if [ $# -lt 3 ]; then
    echo "Usage: $0 <image> <format> <arch>"
    exit 1
fi

image_file="$1"

if [ -e "$image_file" ]; then

    if [[ "$3" == *"aarch64"* ]]; then
        echo "Running aarch64 image..."
        qemu-system-aarch64 \
            -machine virt \
            -cpu cortex-a72 \
            -m 256 \
            -nographic \
            -netdev user,id=eth0,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3 \
            -device virtio-net-pci,netdev=eth0 \
            -kernel vmlinuz \
            -initrd initrd.img \
            -append "root=/dev/vda1 rw console=ttyAMA0,115200n8" \
            -drive file=$image_file,format=$2,if=virtio
    else
        echo "Running x86_64 image..."
        qemu-system-x86_64 \
            -m 256 \
            -display none \
            -serial stdio \
            -netdev user,id=eth0,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3 \
            -device virtio-net-pci,netdev=eth0 \
            -kernel vmlinuz \
            -initrd initrd.img \
            -append "root=/dev/vda1 rw console=ttyS0,115200n8" \
            -drive file=$image_file,format=$2,if=virtio
    fi

else
    echo "File '$image_file' does not exist."
    exit 1
fi
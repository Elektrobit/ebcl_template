#!/bin/sh

qemu-system-aarch64 \
        -machine virt \
        -cpu cortex-a72 \
        -m 4G \
        -nographic \
        -netdev user,id=mynet0,hostfwd=tcp::2222-:22 \
        -device virtio-net-pci,netdev=mynet0 \
        -drive file=${1},if=virtio  \
        -bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd

#!/bin/sh

qemu-system-x86_64 \
        -m 4G \
        -nographic \
        -netdev user,id=mynet0,hostfwd=tcp::2222-:22 \
        -device virtio-net-pci,netdev=mynet0 \
        -drive file=${1},if=virtio

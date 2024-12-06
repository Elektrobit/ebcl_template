#!/bin/bash

qemu-system-aarch64 \
    -machine virt -cpu cortex-a72 -machine type=virt -nographic -m 4G \
    -netdev user,id=mynet0,ipv6-net=fd00::eb/64,ipv6-host=fd00::eb:1,ipv6-dns=fd00::eb:3 \
    -device virtio-net-pci,netdev=mynet0 \
    -kernel vmlinuz \
    -append "console=ttyAMA0 rw" \
    -initrd initrd.img \
    -drive format=raw,file=image.raw,if=virtio

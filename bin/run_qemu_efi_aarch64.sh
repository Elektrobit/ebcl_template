#!/bin/bash

qemu-system-aarch64 \
	-machine virt \
	-cpu cortex-a72 \
	-m 4096 \
	-nographic \
	-netdev user,id=mynet0,hostfwd=tcp::2222-:22,hostfwd=tcp::1234-:1234 \
	-device virtio-net-pci,netdev=mynet0 \
	-drive file=${1},if=virtio  \
	-bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd

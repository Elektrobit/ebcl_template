# Makefile for runnung QEMU amd64 images

#-------------------
# Run the QEMU image
#-------------------

.PHONY: qemu
qemu: $(disc_image)
	@echo "Running $(disc_image) in QEMU aarch64 using EFI loader..."	
	qemu-system-aarch64 \
        -machine virt \
        -cpu cortex-a72 \
        -m 4096 \
        -nographic \
        -netdev user,id=mynet0$(qemu_net_append) \
        -device virtio-net-pci,netdev=mynet0 \
        -drive format=raw,file=$(disc_image),if=virtio
		-bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd

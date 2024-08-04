# Makefile for runnung QEMU amd64 images

#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel commandline
ifeq ($(kernel_cmdline),)
kernel_cmdline = "console=ttyS0"
endif

ifeq ($(kernel_cmdline_append),)
kernel_cmdline_append = ""
endif

ifeq ($(qemu_net_append),)
qemu_net_append = ",hostfwd=tcp::2222-:22"
endif

.PHONY: qemu
qemu: $(kernel) $(initrd_img) $(disc_image)
	@echo "Running $(disc_image) in QEMU x86_64..."
	qemu-system-x86_64 \
		-nographic -m 4G \
		-netdev user,id=mynet0$(qemu_net_append) \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel $(kernel) \
		-append "$(kernel_cmdline) $(kernel_cmdline_append)" \
		-initrd $(initrd_img) \
		-drive format=raw,file=$(disc_image),if=virtio

.PHONY: qemu_efi
qemu_efi: $(disc_image)
	@echo "Running $(disc_image) in QEMU x86_64 using EFI loader..."
	qemu-system-x86_64 \
        -m 4096 \
        -nographic \
        -netdev user,id=mynet0$(qemu_net_append) \
        -device virtio-net-pci,netdev=mynet0 \
        -drive format=raw,file=$(disc_image),if=virtio

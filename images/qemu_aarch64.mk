# Makefile for runnung QEMU amd64 images

#-------------------
# Run the QEMU image
#-------------------

# QEMU kernel commandline
kernel_cmdline ?= console=ttyAMA0
kernel_cmdline_append ?= 
qemu_net_append ?= 

.PHONY: qemu
qemu: $(kernel) $(initrd_img) $(disc_image)
	@echo "Running $(disc_image) in QEMU aarch64..."
	qemu-system-aarch64 \
		-machine virt -cpu cortex-a72 -machine type=virt -nographic -m 4G \
		-netdev user,id=mynet0$(qemu_net_append) \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel $(kernel) \
		-append "$(kernel_cmdline) $(kernel_cmdline_append)" \
		-initrd $(initrd_img) \
		-drive format=raw,file=$(disc_image),if=virtio

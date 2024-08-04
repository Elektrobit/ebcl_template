# Makefile for Jammy QEMU amd64 image using grub efi bootloader

# Arch for sysroot extraction
arch = x86_64

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = image.yaml
# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = ../root.yaml
# Specificaiton of the initrd.img
initrd_spec = ../initrd.yaml
# Specificaiton of the boot partition
boot_spec = boot.yaml
# Specificaiton of the efi partition
efi_spec = efi.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh

# Configuration for the grub bootloader
grub = grub.cfg

# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_x86_64.mk

#--------------------
# Generated artefacts
#--------------------

# Boot partition tarball
boot = build/boot.tar
# EFI partition tarball
efi = build/efi.tar

#-------------------
# Run the QEMU image
#-------------------
.PHONY: qemu
qemu: $(kernel) $(initrd_img) $(disc_image)
	@echo "Running $(disc_image) in QEMU..."
	qemu-system-x86_64 \
		-nographic -m 4G \
		-netdev user,id=mynet0 \
		-device virtio-net-pci,netdev=mynet0 \
		-kernel $(kernel) \
		-append "console=ttyS0" \
		-initrd $(initrd_img) \
		-drive format=raw,file=$(disc_image),if=virtio


#--------------------------
# Image build configuration
#--------------------------

$(disc_image): $(root_tarball) $(boot) $(efi) $(partition_layout)
	@echo "Build image..."
	mkdir -p build
	embdgen -o ./$(disc_image) $(partition_layout)

$(boot): $(boot_spec)
	@echo "Generate boot partition content..."
	mkdir -p build
	boot_generator $(boot_spec) ./build

$(efi): $(efi_spec)
	@echo "Generate boot partition content..."
	mkdir -p build
	boot_generator $(boot_spec) ./build

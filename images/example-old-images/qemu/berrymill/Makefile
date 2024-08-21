# Makefile for old Berrymill images

# Arch for sysroot extraction
arch = x86_64

#---------------------
# Select bash as shell
#---------------------

SHELL := /bin/bash

#--------------
# Result folder
#--------------

result_folder ?= ./build

#---------------------
# Image specifications
#---------------------

# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml

# Specification of the sysroot
sysroot_spec = sysroot.yaml

#--------------------
# Generated artifacts
#--------------------

# QEMU EFI images require only a qcow-image

# Disc image
disc_image = $(result_folder)/root.qcow2

# Sysroot tarball
sysroot_tarball = $(result_folder)/root_sysroot.tar.xz

#--------------------------------
# Default make targets for images
#--------------------------------



#--------------------------
# Image build configuration
#--------------------------

# Build the qcow2 image
$(disc_image): $(root_filesystem_spec)
	@echo "Build image..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --no-config $(root_filesystem_spec) $(result_folder) 2>&1 | tee $(result_folder)/image.log

# Build the sysroot tarball
$(sysroot_tarball): $(sysroot_spec)
	@echo "Build image..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --sysroot --no-config $(sysroot_spec) $(result_folder) 2>&1 | tee $(result_folder)/sysroot.log

#-------------------
# Run the QEMU image
#-------------------

.PHONY: qemu
qemu: $(disc_image)
	@echo "Running $(disc_image) in QEMU x86_64 using EFI loader..."
	qemu-system-x86_64 \
        -m 4096 \
        -nographic \
        -netdev user,id=mynet0$(qemu_net_append) \
        -device virtio-net-pci,netdev=mynet0 \
        -drive file=$(disc_image),if=virtio

#--------------------------------
# Default make targets for images
#--------------------------------

# default action
.PHONY: default
default: qemu

# build of the disc image
.PHONY: image
image: $(disc_image)

# build of the sysroot tarball
.PHONY: sysroot
sysroot: $(sysroot_tarball)

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf build

# install the sysroot tarball
.PHONY: sysroot_install
sysroot_install: $(sysroot_tarball)
	rm -rf /workspace/sysroot_$(arch)/*
	cp $(sysroot_tarball) /workspace/sysroot_$(arch)/
	cd /workspace/sysroot_$(arch)/ && tar xf $(sysroot_tarball)

# Makefile for old Berrymill images

# QEMU EFI images require only a qcow-image

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

# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = root.yaml

#--------------------
# Generated artefacts
#--------------------

# Disc image
disc_image = $(result_folder)/root.img

#--------------------------------
# Default make targets for images
#--------------------------------

# default action
.PHONY: default
default: qemu

# build of the disc image
.PHONY: image
image: $(disc_image)

# clean - delete the generated artefacts
.PHONY: clean
clean:
	rm -rf build

#--------------------------
# Image build configuration
#--------------------------

$(disc_image): $(root_filesystem_spec)
	@echo "Build image..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --no-config $(root_filesystem_spec) $(result_folder) 2>&1 | tee $(disc_image).log

#-------------------
# Run the QEMU image
#-------------------

.PHONY: qemu
qemu: $(disc_image)
	@echo "Running $(disc_image) in QEMU x86_64 using EFI loader..."
	qemu-system-aarch64 \
        -machine virt \
        -cpu cortex-a72 \
        -m 4096 \
        -nographic \
        -netdev user,id=mynet0 \
        -device virtio-net-pci,netdev=mynet0 \
        -drive format=raw,file=$(disc_image),if=virtio
		-bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd

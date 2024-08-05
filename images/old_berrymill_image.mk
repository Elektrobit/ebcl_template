# Makefile for old Berrymill images

# QEMU EFI images require only a qcow-image

#---------------------
# Select bash as shell
#---------------------

SHELL := /bin/bash

#--------------------
# Generated artefacts
#--------------------

# Disc image
ifeq ($(disc_image),)
disc_image = build/image.qcow2
endif

# Sysroot tarball
ifeq ($(sysroot_tarball),)
sysroot_tarball = build/sysroot.tar.xz
endif

#--------------------------------
# Default make targets for images
#--------------------------------

# default action
.PHONY: default
default: qemu

# build of the disc image
.PHONY: image
image: $(disc_image)

# build the sysroot tarball
.PHONY: sysroot
sysroot: $(sysroot_tarball)

# install the sysroot tarball
.PHONY: sysroot_install
sysroot_install: $(sysroot_tarball)
	rm -rf /workspace/sysroot_$(arch)/*
	cp build/$(sysroot_tarball) /workspace/sysroot_$(arch)/
	cd /workspace/sysroot_$(arch)/ && tar xf $(sysroot_tarball)

# clean - delete the generated artefacts
.PHONY: clean
clean:
	rm -rf build

#--------------------------
# Image build configuration
#--------------------------

$(disc_image): $(root_filesystem_spec)
	@echo "Build image..."
	mkdir -p build
	set -o pipefail && TODO

$(sysroot_tarball): $(root_filesystem_spec)
	@echo "Build sysroot.tar..."
	mkdir -p build
	set -o pipefail && TODO

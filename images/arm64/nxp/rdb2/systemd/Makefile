# Makefile for NXP RDB2

# Arch for sysroot extraction
arch = aarch64

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = image.yaml
# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = root.yaml
# Specificaiton of the initrd.img
initrd_spec = initrd.yaml
# Specificaiton of the kernel
boot_spec = boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = config_root.sh

# Makefile for QEMU amd64 images

# QEMU images require three artefacts:
# - root filesystem image (image.raw)
# - Linux kernel binary (vmlinuz)
# - Initrd image (initrd.img)

# The initrd image is needed because the Canonical kernel has no
# built-in support for virtio block devices.

# default action
.PHONY: default
default: image

#---------------------
# Select bash as shell
#---------------------

SHELL := /bin/bash

#--------------------
# Generated artefacts
#--------------------

# Disc image
ifeq ($(disc_image),)
disc_image = build/image.raw
endif

# Base root tarball
ifeq ($(base_tarball),)
base_tarball = build/ebcl_rdb2.tar
endif

# Configured root tarball
ifeq ($(root_tarball),)
root_tarball = build/ebcl_rdb2.config.tar
endif

# Generated initrd.img
ifeq ($(initrd_img),)
initrd_img = build/initrd.img
endif

# Generated boot tarball
ifeq ($(boot_tarball),)
boot_tarball = build/boot.tar
endif

# Sysroot tarball
ifeq ($(sysroot_tarball),)
sysroot_tarball = build/ebcl_rdb2_sysroot.tar
endif

#--------------------------------
# Default make targets for images
#--------------------------------

# build of the disc image
.PHONY: image
image: $(disc_image)

# build of the root tarball(s)
.PHONY: root
root: $(base_tarball)

# build of the initrd.img(s)
.PHONY: initrd
initrd: $(initrd_img)

# build of the kernel(s)
.PHONY: boot
boot: $(boot_tarball)

# config the root tarball
.PHONY: config
config: $(root_tarball)

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

#-------------------------------------------
# Open a shell for manual root configuration
#-------------------------------------------
.PHONY: edit_root
edit_root:
	@echo "Extacting root tarball..."
	mkdir -p build/root
	cd build && fakeroot -s fakedit -- tar xf ubuntu.config.tar -C ./root
	@echo "Open edit shell..."
	cd build/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	cd build && rm -f ubuntu.config.old.tar
	cd build && mv ubuntu.config.tar ubuntu.config.old.tar
	cd build/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../ubuntu.config.tar .

#--------------------------
# Image build configuration
#--------------------------

$(disc_image): $(root_tarball) $(partition_layout)
	@echo "Build image..."
	mkdir -p build
	set -o pipefail && embdgen -o ./$(disc_image) $(partition_layout) 2>&1 | tee $(disc_image).log

$(base_tarball): $(root_filesystem_spec)
	@echo "Build root.tar..."
	mkdir -p build
	set -o pipefail && root_generator --no-config $(root_filesystem_spec) ./build 2>&1 | tee $(base_tarball).log

$(root_tarball): $(base_tarball) $(config_root)
	@echo "Configuring ${base_tarball} as ${root_tarball}..."
	mkdir -p build
	set -o pipefail && root_configurator $(root_filesystem_spec) $(base_tarball) $(root_tarball) 2>&1 | tee $(root_tarball).log

$(boot_tarball): $(boot_spec)
	@echo "Build the boot tarball..."
	mkdir -p build
	echo "Not implemented!"; exit 1
	set -o pipefail && boot_generator $(boot_spec) ./build 2>&1 | tee $(boot_tarball).log

$(initrd_img): $(initrd_spec)
	@echo "Build initrd.img..."
	mkdir -p build
	echo "Not implemented!"; exit 1
	set -o pipefail && initrd_generator $(initrd_spec) ./build 2>&1 | tee $(initrd_img).log

$(sysroot_tarball): $(root_filesystem_spec)
	@echo "Build sysroot.tar..."
	mkdir -p build
	set -o pipefail && root_generator --sysroot --no-config $(root_filesystem_spec) ./build 2>&1 | tee $(sysroot_tarball).log

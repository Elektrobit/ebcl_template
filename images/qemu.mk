# Makefile for QEMU images

# QEMU images require three artifacts:
# - root filesystem image (image.raw)
# - Linux kernel binary (vmlinuz)
# - Initrd image (initrd.img)
#
# The initrd image is needed because the Canonical kernel has no
# built-in support for virtio block devices.

# default action
.PHONY: default
default: qemu

#--------------
# Result folder
#--------------

result_folder ?= ./build

#---------------------
# Select bash as shell
#---------------------

SHELL := /bin/bash

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout ?= image.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec ?= root.yaml
# Specification of the initrd.img
initrd_spec ?= initrd.yaml
# Specification of the kernel
boot_spec ?= boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root ?= config_root.sh

#--------------------
# Generated artifacts
#--------------------

# Disc image
disc_image ?= $(result_folder)/image.raw

# Base root tarball
base_tarball ?= $(result_folder)/root.tar

# Configured root tarball
root_tarball ?= $(result_folder)/root.config.tar

# Generated initrd.img
initrd_img ?= $(result_folder)/initrd.img

# Kernel image
kernel ?= $(result_folder)/vmlinuz

# Sysroot tarball
sysroot_tarball ?= $(result_folder)/root_sysroot.tar

#--------------------------
# Image build configuration
#--------------------------

# Build flow:
#
# boot_spec -[boot gen]-> kernel -----------------------------------------------------------------\
#                                                                                                  \
# initrd_spec -[initrd gen]-> initrd_img -----------------------------------------------------------\
#                                                                                                    \
# root_filesystem_spec -[root gen]-> base_tarball -[root conf]-> root_tarball -[embdgen]-> disc_image -> QEMU
#                                                /                           /
# config_root ----------------------------------/                           /
#                                                                          /
# partition_layout -------------------------------------------------------/


# Embdgen is used to build the disc image.
# root_tarball: the contents of the root filesystem
# partition_layout: the partition layout of the SD card image
$(disc_image): $(root_tarball) $(partition_layout)
	@echo "Build image..."
	mkdir -p $(result_folder)
	set -o pipefail && embdgen -o ./$(disc_image) $(partition_layout) 2>&1 | tee $(disc_image).log

# The root generator is used to build the base root filesystem tarball.
# root_filesystem_spec: specification of the root filesystem packages.
#
# This fist step only installs the specified packages. User configuration
# is done as a second step, because the build of this tarball is quite 
# time consuming and configuration is fast. This is an optimization for 
# the image development process.
$(base_tarball): $(root_filesystem_spec)
	@echo "Build root.tar..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --no-config $(root_filesystem_spec) $(result_folder) 2>&1 | tee $(base_tarball).log

# The root configurator is used to run the user configuration scripts
# as a separate step in the build process.
# base_tarball: tarball which is configured
# config_root: the used configuration script
$(root_tarball): $(base_tarball) $(config_root)
	@echo "Configuring ${base_tarball} as ${root_tarball}..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(root_filesystem_spec) $(base_tarball) $(root_tarball) 2>&1 | tee $(root_tarball).log

# The boot generator is used to extract the kernel image for a Debian package.
# boot_spec: specification where and how to extract the kernel
$(kernel): $(boot_spec)
	@echo "Get kernel binary..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(kernel).log
	mv ./$(kernel)-* ./$(kernel) || true

# The initrd image is build using the initrd generator.
# initrd_spec: specification of the initrd image.
$(initrd_img): $(initrd_spec)
	@echo "Build initrd.img..."
	mkdir -p $(result_folder)
	set -o pipefail && initrd_generator $(initrd_spec) $(result_folder) 2>&1 | tee $(initrd_img).log

# The root generator is used to build a sysroot variant of the root filesystem.
# root_filesystem_spec: specification of the root filesystem
#
# --no-config means that the configuration step is skipped
$(sysroot_tarball): $(root_filesystem_spec)
	@echo "Build sysroot.tar..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --sysroot --no-config $(root_filesystem_spec) $(result_folder) 2>&1 | tee $(sysroot_tarball).log

#--------------------------------
# Default make targets for images
#--------------------------------

# build of the disc image
.PHONY: image
image: $(disc_image)

# build of the root tarball
.PHONY: root
root: $(base_tarball)

# build of the initrd.img
.PHONY: initrd
initrd: $(initrd_img)

# build of the kernel image
.PHONY: boot
boot: $(kernel)

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
	tar xf $(sysroot_tarball) -C /workspace/sysroot_$(arch)/ || true

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf $(result_folder)

#-------------------------------------------
# Open a shell for manual root configuration
#-------------------------------------------
.PHONY: edit_base
edit_base:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s $(result_folder)/fakedit -- tar xf $(base_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(base_tarball).old
	mv $(base_tarball) $(base_tarball).old
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../../$(base_tarball) .
	rm -rf $(result_folder)/root

.PHONY: edit_root
edit_root:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s $(result_folder)/fakedit -- tar xf $(root_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(root_tarball).old
	mv $(root_tarball) $(root_tarball).old
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../../$(root_tarball) .
	rm -rf $(result_folder)/root

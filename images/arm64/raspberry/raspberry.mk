# Makefile for NXP RDB2

# The NXP S32G2 expects to find the bootloader written as fip image
# at the begining of the storage, spitted into two parts. In the middle
# a slot for the U-Boot configuration is specified.
# After the bootloader area, a MBR partition is expected.
# The kernel and device tree needs to be packed as a fitimage and stored
# on the first partition, which has to be fat32.
# The root partition for Linux can come as partition 2.
# This image layout is specified in the image.yaml and picked up by embdgen.
#
# To generate the image, embdgen requires three artifacts:-
# - the bootloader as fip.s32 image
# - the kernel fitimage
# - and the contents of the root partition.
#
# This makefile makes use of a separate root tarball, specified as 
# ../boot_root.yaml, to setup the environment for building the fitimage.
# The boot generator and the script ../build_fitimage.sh is used to 
# finally generate the fitimage artefact.

# Arch for sysroot extraction
arch ?= aarch64

# default action
.PHONY: default
default: image

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

#-------------------------
# Additional configuration
#-------------------------

#--------------------
# Generated artifacts
#--------------------

# The ifeqs allow overwriting the values
# if the makefile is used as include.

# Disc image
disc_image ?= $(result_folder)/image.raw

# Base root tarball
base_tarball ?= $(result_folder)/ebcl_pi4.tar

# Configured root tarball
root_tarball ?= $(result_folder)/ebcl_pi4.config.tar

# Sysroot tarball
sysroot_tarball ?= $(result_folder)/ebcl_pi4_sysroot.tar

#--------------------------
# Image build configuration
#--------------------------

# Embdgen is used to build the SD card image.
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

# The root generator is used to build a sysroot variant of the root filesystem.
# root_filesystem_spec: specification of the root filesystem
#
# --no-config means that the configuration step is skipped
$(sysroot_tarball): $(root_filesystem_spec)
	@echo "Build sysroot.tar..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --sysroot --no-config $(root_filesystem_spec) $(result_folder) 2>&1 | tee $(sysroot_tarball).log

#--------------------------------------
# Open a shell for manual configuration
#--------------------------------------

# Helper targets to manually inspect and adapt the different tarballs.

.PHONY: edit_base
edit_base:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s $(result_folder)/fakeedit -- tar xf $(base_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i $(result_folder)/fakeedit -s $(result_folder)/fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(base_tarball).old
	mv $(base_tarball) $(base_tarball).old
	cd $(result_folder)/root && fakeroot -i $(result_folder)/fakeedit -s $(result_folder)/fakeedit -- tar cf ../../$(base_tarball) .
	rm -rf $(result_folder)/root

.PHONY: edit_root
edit_root:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s $(result_folder)/fakedit -- tar xf $(root_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i $(result_folder)/fakedit -s $(result_folder)/fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(root_tarball).old
	mv $(root_tarball) $(root_tarball).old
	cd $(result_folder)/root && fakeroot -i $(result_folder)/fakedit -s $(result_folder)/fakedit -- tar cf ../../$(root_tarball) .
	rm -rf $(result_folder)/root

#--------------------------------
# Default make targets for images
#--------------------------------

# build of the disc image
.PHONY: image
image: $(disc_image)

# build of the root tarball(s)
.PHONY: root
root: $(base_tarball)

# config the root tarball
.PHONY: config
config: $(root_tarball)

# Build the initrd
.PHONY: initrd
initrd:
	@echo "Fake target to be interface compliant"
	@echo "Image was written to"

# Build the initrd
.PHONY: boot
boot:
	@echo "Fake target to be interface compliant"
	@echo "Results were written to"

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

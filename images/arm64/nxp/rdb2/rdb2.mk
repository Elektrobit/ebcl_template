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
# Specification of the initrd.img
initrd_spec ?= initrd.yaml
# Specification of the fitimage
boot_spec ?= boot.yaml
# Specification of the root environment for fitimage building
boot_root_spec ?= boot_root.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec ?= root.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root ?= config_root.sh

# Build script for the fitimage
build_fitimage ?= build_fitimage.sh
# Layout of the fitimage
fitimage_config ?= bootargs.its
# NXP bootloader config
bootloader_config ?= bootargs-overlay.dts

#--------------------
# Generated artifacts
#--------------------

# The ifeqs allow overwriting the values
# if the makefile is used as include.

# Disc image
disc_image ?= $(result_folder)/image.raw

# Base root tarball
base_tarball ?= $(result_folder)/ebcl_rdb2.tar

# Configured root tarball
root_tarball ?= $(result_folder)/ebcl_rdb2.config.tar

# Boot root tarball
boot_root ?= $(result_folder)/boot_root.tar

# Disc image
fitimage ?= $(result_folder)/fitimage

# Generated initrd.img
initrd_img ?= $(result_folder)/initrd.img

# Sysroot tarball
sysroot_tarball ?= $(result_folder)/ebcl_rdb2_sysroot.tar

#--------------------------
# Image build configuration
#--------------------------

# Build flow:
#
# root_filesystem_spec -[root gen]-> base_tarball -\
#                                                   \
# config_root ----------------------------------------[root conf]-> root_tarball -\
#                                                                                  \
# boot_root_spec -[root gen]-> boot_root -------\                                   \
#                                                \                                   \
# boot_spec --------------------------------------[boot gen]-> fitimage (and fip.s32) -[embdgen]-> disc_image
#                                                /                                   /
# fitimage_config ------------------------------/                                   /
#                                              /                                   /
# bootloader_config --------------------------/                                   /
#                                            /                                   /
# build_fitimage ---------------------------/                                   /
#                                          /                                   /
# initrd_spec -[initrd gen]-> initrd_img -/                                   /
#                                                                            /
# partition_layout ---------------------------------------------------------/

# Embdgen is used to build the SD card image.
# fitimage: the fitimage containing the kernel, the device tree and the initrd.img
# root_tarball: the contents of the root filesystem
# partition_layout: the partition layout of the SD card image
#
# The bootloader fip.s32 is not explicitly metioned, since it is build in one step
# with the fitimage.
$(disc_image): $(fitimage) $(root_tarball) $(partition_layout)
	@echo "Build image..."
	mkdir -p $(result_folder)
	set -o pipefail && embdgen -o ./$(disc_image) $(partition_layout) 2>&1 | tee $(disc_image).log


# The boot generator is used to run the fitimage build in a chroot environment.
# boot_spec: spec of the fitimage build enviroment
# boot_root: tarball of the fitimage build environment
# build_fitimage: build script for the fitimage
# fitimage_config: fitimage layout configuration
# fitimage_config: bootloader configuration
# initrd_img: the initrd.img which is embedded in the fitimage
# initrd_spec: the initrd.img specification
$(fitimage): $(boot_spec) $(boot_root) $(build_fitimage) $(fitimage_config) $(fitimage_config) $(initrd_img)
	@echo "Build $(fitimage)..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(fitimage).log

# The root generator is used to build a chroot enviroment which contains all tools for building the fitimage.
# boot_root_spec: specification of the fitimage build environment
#
# A separate image build is used for the fitimage build environment, to not bloat the
# root filesystem with this stuff.
$(boot_root): $(boot_root_spec)
	@echo "Build $(boot_root) from $(boot_root_spec)..."
	mkdir -p $(result_folder)
	set -o pipefail && root_generator --no-config $(boot_root_spec) $(result_folder) 2>&1 | tee $(boot_root).log

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

#--------------------------------------
# Open a shell for manual configuration
#--------------------------------------

# Helper targets to manually inspect and adapt the different tarballs.

.PHONY: edit_base
edit_base:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s  $(result_folder)/fakeedit -- tar xf $(base_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i ../fakeedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(base_tarball).old
	mv $(base_tarball) $(base_tarball).old
	cd $(result_folder)/root && fakeroot -i ../fakeedit -s ../fakeedit -- tar cf ../../$(base_tarball) .
	rm -rf $(result_folder)/root

.PHONY: edit_root
edit_root:
	@echo "Extacting base root tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s  $(result_folder)/fakedit -- tar xf $(root_tarball) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(root_tarball).old
	mv $(root_tarball) $(root_tarball).old
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../../$(root_tarball) .
	rm -rf $(result_folder)/root

.PHONY: edit_boot_root
edit_boot_root:
	@echo "Extacting boot base tarball..."
	mkdir -p $(result_folder)/root
	fakeroot -s  $(result_folder)/fakedit -- tar xf $(boot_root) -C $(result_folder)/root
	@echo "Open edit shell..."
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakeedit
	@echo "Re-packing root tarball..."
	rm -f $(boot_root).old
	mv $(boot_root) $(boot_root).old
	cd $(result_folder)/root && fakeroot -i ../fakedit -s ../fakedit -- tar cf ../../$(boot_root) .
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

# build of the initrd.img(s)
.PHONY: initrd
initrd: $(initrd_img)

# build of the kernel(s)
.PHONY: boot
boot: $(fitimage)

# build of the kernel(s)
.PHONY: boot_root
boot_root: $(boot_root)

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

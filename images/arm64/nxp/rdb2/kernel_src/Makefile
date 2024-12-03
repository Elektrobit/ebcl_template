# Makefile for NXP RDB2 with kernel build form source

#--------------
# Output folder
#--------------

# Folder for generated artifacts
result_folder ?= ./build

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the fitimage
boot_spec = boot.yaml
# Specification of the root environment for fitimage building
boot_root_spec = ../boot_root.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml

# Specification how to get the kernel config
kernel_config = kernel_config.yaml
# Kernel source package name
kernel_package = linux-buildinfo-5.15.0-1034-s32-eb-optimized

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = config_root.sh

# Build script for the fitimage
build_fitimage = ../build_fitimage.sh
# Layout of the fitimage
fitimage_config = ../bootargs.its
# NXP bootloader config
bootloader_config = ../bootargs-overlay.dts

include ../rdb2.mk

#--------------------
# Generated artifacts
#--------------------

# Kernel image
kernel = $(result_folder)/vmlinuz
# Kernel modules
modules = $(result_folder)/lib
# Kernel config
kconfig = $(result_folder)/config
# Kernel source
source = kernel
# Path of the kernel sources
kernel_dir = $(source)/linux-s32-eb-optimized-5.15.0
# Kernel make arguments
kernel_make_args = ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-

#--------------------------
# Image build configuration
#--------------------------

# Build flow of the kernel binary:
# --------------------------------
#
# [make $modules]-> $result_folder/lib (not use, could be picked up by initrd gen
#
# kernel_package -[make $source]-> /kernel -\
#                                            \
# kernel_config -[boot gen]-> kconfig --------- [make $kernel]-> kernel
#
#
# Adapte build flow of the base makefile:
# ---------------------------------------
#
# root_filesystem_spec -[root gen]-> base_tarball -\
#                                                   \
# config_root ----------------------------------------[root conf]-> root_tarball -\
#                                                                                  \
# boot_root_spec -[root gen]-> boot_root -------\                                   \
#                                                \                                   \
# (adapted) boot_spec ----------------------------[boot gen]-> fitimage (and fip.s32) -[embdgen]-> disc_image
#                                                /                                   /
# fitimage_config ------------------------------/                                   /
#                                              /                                   /
# bootloader_config --------------------------/                                   /
#                                            /                                   /
# build_fitimage ---------------------------/                                   /
#                                          /                                   /
# initrd_spec -[initrd gen]-> initrd_img -/                                   /
#                                        /                                   /
# (kernel build flow) kernel -----------/                                   /
#                                                                          /
# partition_layout -------------------------------------------------------/

# Download the kernel source form the apt repo
# and install the build dependencies.
$(source):
	@echo "Get kernel sources..."
	mkdir -p $(source)
	cd $(source) && apt -y source $(kernel_package)
	sudo apt -y build-dep $(kernel_package)
	cd $(kernel_dir) && chmod +x scripts/*.sh

# Get the kernel config form the configured kernel binary package.
$(kconfig): $(kernel_config) $(source)
	@echo "Get kernel config..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(kernel_config) $(result_folder) 2>&1 | tee $(kconfig).log
	@echo "Deleting old $(kconfig)..."
	rm -f $(kconfig) || true
	@echo "Renaming $(result_folder)/config-* as $(kconfig)..."
	mv $(result_folder)/config-* $(kconfig) || true
	@echo "Copying $(kconfig) to $(kernel_dir)..."
	cp $(kconfig) $(kernel_dir)/.config
	@echo "Set all not defined values of the kernel config to defaults..."
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) olddefconfig
	@echo "Copying modified config as olddefconfig..."
	cp $(kernel_dir)/.config $(result_folder)/olddefconfig

# Build the kernel binary
$(kernel): $(kconfig) $(source)
	@echo "Compile kernel..."
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) -j 16 Image
	@echo "Get kernel binary..."
	cp $(kernel_dir)/arch/arm64/boot/Image $(kernel)
	@echo "Results were written to $(kernel)"

# Adpate build spec for the fitimage
# Additional dependency to the kernel binary
# Please not that another boot_spec is used, see ./boot.yaml.
$(fitimage): $(boot_spec) $(boot_root) $(build_fitimage) $(fitimage_config) $(fitimage_config) $(initrd_img) $(kernel)
	@echo "Build $(fitimage)..."
	mkdir -p $(result_folder)
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(fitimage).log

# Make the modules and install them in the results folder
$(modules): $(kernel)
	@echo "Get virtio driver..."
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) modules -j 16
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	mkdir -p $(result_folder)
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) $(kernel_make_args) modules_install

#--------------------
# Helper make targets
#--------------------

# Configure the kernel binary
.PHONY: config_kernel
config_kernel:
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) menuconfig

# Rebuild the kernel binary
.PHONY: rebuild_kernel
rebuild_kernel:
	mkdir -p $(result_folder)
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) -j 16 Image
	@echo "Delete the old kernel binary..."
	rm -f $(kernel)
	@echo "Get the new kernel binary..."
	cp $(kernel_dir)/arch/arm64/boot/Image $(kernel)

# Rebuild the kernel modules
.PHONY: rebuild_modules 
rebuild_modules: kernel
	mkdir -p $(result_folder)
	cd $(kernel_dir) && $(MAKE) $(kernel_make_args) modules -j 16
	cd $(kernel_dir) && chmod +x debian/scripts/sign-module
	@echo "Delete the old kernel modules..."
	rm -rf $(modules)
	@echo "Install the new kernel modules..."
	cd $(kernel_dir) && INSTALL_MOD_PATH=../../$(result_folder) $(MAKE) $(kernel_make_args) modules_install

# clean - delete the generated artifacts
.PHONY: clean
clean:
	rm -rf $(result_folder)

.PHONY: clean_kernel
clean_kernel:
	rm -rf $(source)

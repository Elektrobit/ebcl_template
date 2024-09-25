# Makefile for NXP RDB2 systemd variant

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the initrd.img
initrd_spec = initrd.yaml
# Specification of the fitimage
boot_spec = boot.yaml
# Specification of the root environment for fitimage building
boot_root_spec = ../boot_root.yaml
# Specification of the root filesystem content and configuration
root_filesystem_spec = root.yaml

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

# base_tarball: tarball which is configured
# config_root: the used configuration script
# fitimage: indirect dependency to the step extracting the kernel modules
$(root_tarball): $(base_tarball) $(config_root) $(fitimage)
	@echo "Configuring ${base_tarball} as ${root_tarball}..."
	mkdir -p $(result_folder)
	set -o pipefail && root_configurator $(root_filesystem_spec) $(base_tarball) $(root_tarball) 2>&1 | tee $(root_tarball).log

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
	rm -rf $(result_folder)/modules
	set -o pipefail && boot_generator $(boot_spec) $(result_folder) 2>&1 | tee $(fitimage).log

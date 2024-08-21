# Makefile for ammy QEMU amd64 image using elbe

# Arch for sysroot extraction
arch = aarch64

#---------------------
# Image specifications
#---------------------

# Specification of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specification of the initrd.img
initrd_spec = ../initrd.yaml
# Specification of the fitimage
boot_spec = ../boot.yaml
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

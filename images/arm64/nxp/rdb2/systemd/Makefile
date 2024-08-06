# Makefile for NXP RDB2 systemd variant

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specificaiton of the initrd.img
initrd_spec = ../initrd.yaml
# Specificaiton of the fitimage
boot_spec = ../boot.yaml
# Specificaiton of the root environment for fitimage building
boot_root_spec = ../boot_root.yaml
# Specificaiton of the root filesystem content and configuration
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

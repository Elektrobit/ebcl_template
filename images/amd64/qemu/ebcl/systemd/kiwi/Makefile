# Makefile for ammy QEMU amd64 image using kiwi

# Arch for sysroot extraction
arch = x86_64

#---------------------
# Image specifications
#---------------------

# Specificaiton of the partition layout of the image.raw
partition_layout = ../image.yaml
# Specificaiton of the root filesystem content and configuration
root_filesystem_spec = root.yaml
# Specificaiton of the initrd.img
initrd_spec = ../initrd.yaml
# Specificaiton of the kernel
boot_spec = ../boot.yaml

#-------------------------
# Additional configuration
#-------------------------

# Config script for root filesystem
config_root = ../config_root.sh

#--------------------
# Generated artefacts
#--------------------

# Base root tarball
base_tarball = build/ubuntu.tar.xz


# for building
include ../../../../qemu.mk

# for running QEMU
include ../../../../qemu_x86_64.mk

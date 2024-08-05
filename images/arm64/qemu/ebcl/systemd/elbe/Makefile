# Makefile for ammy QEMU amd64 image using elbe

# Arch for sysroot extraction
arch = aarch64

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
base_tarball = build/ebcl.tar

# Configured root tarball
root_tarball = build/ebcl.config.tar

# Sysroot tarball
sysroot_tarball = build/ebcl_sysroot.tar

# for building
include ../../../../../qemu.mk

# for running QEMU
include ../../../../../qemu_aarch64.mk
